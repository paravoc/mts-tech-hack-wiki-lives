#include "src/ai/openrouter_ai_provider.h"

#include <curl/curl.h>

#include <nlohmann/json.hpp>

#include <memory>
#include <sstream>
#include <string_view>
#include <utility>

#include "src/ai/openrouter_prompt_builder.h"

namespace {

    using json = nlohmann::json;

    class CurlGlobalInit {
    public:
        CurlGlobalInit() {
            curl_global_init(CURL_GLOBAL_DEFAULT);
        }

        ~CurlGlobalInit() {
            curl_global_cleanup();
        }

        CurlGlobalInit(const CurlGlobalInit&) = delete;
        CurlGlobalInit& operator=(const CurlGlobalInit&) = delete;
    };

    CurlGlobalInit& curlGlobalInitInstance() {
        static CurlGlobalInit instance;
        return instance;
    }

    struct ParsedUrl {
        std::string baseUrl;
    };

    struct HttpResponse {
        long statusCode = 0;
        std::string body;
    };

    size_t appendResponseBytes(char* ptr, size_t size, size_t nmemb, void* userdata) {
        const std::size_t totalSize = size * nmemb;
        auto* output = static_cast<std::string*>(userdata);
        output->append(ptr, totalSize);
        return totalSize;
    }

    std::string trimTrailingSlash(std::string value) {
        while (!value.empty() && value.back() == '/') {
            value.pop_back();
        }
        return value;
    }

    wikilive::utils::Expected<ParsedUrl> parseBaseUrl(const std::string& baseUrl) {
        const auto normalized = trimTrailingSlash(baseUrl);
        if (normalized.empty() || (normalized.rfind("http://", 0) != 0 && normalized.rfind("https://", 0) != 0)) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::InvalidConfig,
                "AI_BASE_URL must start with http:// or https://",
                500,
                false));
        }

        return ParsedUrl{ .baseUrl = normalized };
    }

    std::string joinPath(const std::string& baseUrl, const std::string& suffix) {
        if (suffix.empty()) {
            return baseUrl;
        }

        if (suffix.front() == '/') {
            return baseUrl + suffix;
        }

        return baseUrl + "/" + suffix;
    }

    std::string curlErrorMessage(const std::string& operation, const CURLcode code, const char* buffer) {
        std::string message = operation + " failed";
        if (buffer != nullptr && buffer[0] != '\0') {
            message += ": ";
            message += buffer;
        }
        else {
            message += ": ";
            message += curl_easy_strerror(code);
        }
        return message;
    }

    wikilive::utils::Expected<HttpResponse> performJsonPost(
        const std::string& url,
        const std::vector<std::string>& headers,
        const int timeoutMs,
        const std::string& body) {
        using wikilive::utils::ErrorCode;

        (void)curlGlobalInitInstance();

        CURL* rawHandle = curl_easy_init();
        if (rawHandle == nullptr) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                "libcurl initialization failed",
                502,
                true));
        }

        std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> handle(rawHandle, &curl_easy_cleanup);

        std::string responseBody;
        char errorBuffer[CURL_ERROR_SIZE] = {};
        curl_easy_setopt(handle.get(), CURLOPT_ERRORBUFFER, errorBuffer);
        curl_easy_setopt(handle.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(handle.get(), CURLOPT_POST, 1L);
        curl_easy_setopt(handle.get(), CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(handle.get(), CURLOPT_CONNECTTIMEOUT_MS, static_cast<long>(timeoutMs));
        curl_easy_setopt(handle.get(), CURLOPT_TIMEOUT_MS, static_cast<long>(timeoutMs));
        curl_easy_setopt(handle.get(), CURLOPT_WRITEFUNCTION, appendResponseBytes);
        curl_easy_setopt(handle.get(), CURLOPT_WRITEDATA, &responseBody);
        curl_easy_setopt(handle.get(), CURLOPT_USERAGENT, "WikiLive/1.0");
        curl_easy_setopt(handle.get(), CURLOPT_POSTFIELDS, body.data());
        curl_easy_setopt(handle.get(), CURLOPT_POSTFIELDSIZE_LARGE, static_cast<curl_off_t>(body.size()));

        curl_slist* rawHeaderList = nullptr;
        for (const auto& header : headers) {
            rawHeaderList = curl_slist_append(rawHeaderList, header.c_str());
        }
        std::unique_ptr<curl_slist, decltype(&curl_slist_free_all)> headerList(rawHeaderList, &curl_slist_free_all);
        if (headerList) {
            curl_easy_setopt(handle.get(), CURLOPT_HTTPHEADER, headerList.get());
        }

        const CURLcode performCode = curl_easy_perform(handle.get());
        if (performCode != CURLE_OK) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                curlErrorMessage("Request to AI provider", performCode, errorBuffer),
                502,
                true));
        }

        long statusCode = 0;
        curl_easy_getinfo(handle.get(), CURLINFO_RESPONSE_CODE, &statusCode);
        return HttpResponse{ .statusCode = statusCode, .body = std::move(responseBody) };
    }

    wikilive::utils::Expected<std::string> executeJsonRequest(
        const ParsedUrl& baseUrl,
        const std::string& endpointPath,
        const std::string& apiKey,
        const int timeoutMs,
        const std::string& body) {
        using wikilive::utils::ErrorCode;

        const auto response = performJsonPost(
            joinPath(baseUrl.baseUrl, endpointPath),
            {
                "Authorization: Bearer " + apiKey,
                "Content-Type: application/json",
                "Accept: application/json",
                "HTTP-Referer: https://wikilive.local",
                "X-Title: WikiLive",
            },
            timeoutMs,
            body);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto statusCode = response->statusCode;
        if (statusCode == 429) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiRateLimit,
                "OpenRouter rate limit exceeded",
                429,
                true));
        }

        if (statusCode == 401 || statusCode == 403) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                "AI provider rejected the request. Check AI_API_KEY.",
                static_cast<int>(statusCode),
                false));
        }

        if (statusCode >= 500) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                "AI provider temporary server error: HTTP " + std::to_string(statusCode),
                static_cast<int>(statusCode),
                true));
        }

        if (statusCode >= 400) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                "AI provider request failed: HTTP " + std::to_string(statusCode),
                static_cast<int>(statusCode),
                false));
        }

        return response->body;
    }

    wikilive::utils::Expected<json> parseJson(const std::string& responseBody) {
        try {
            return json::parse(responseBody);
        }
        catch (const std::exception& exception) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::AiApiError,
                std::string("Failed to parse AI provider JSON response: ") + exception.what(),
                502,
                false));
        }
    }

    wikilive::utils::Expected<std::string> extractAssistantContent(const json& response) {
        if (!response.contains("choices") || !response["choices"].is_array() || response["choices"].empty()) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::AiApiError,
                "AI response does not contain choices",
                502,
                false));
        }

        const auto& message = response["choices"][0]["message"];
        if (message.is_object() && message.contains("content")) {
            const auto& content = message["content"];
            if (content.is_string()) {
                return content.get<std::string>();
            }

            if (content.is_array()) {
                std::string text;
                for (const auto& item : content) {
                    if (item.is_object() && item.contains("text") && item["text"].is_string()) {
                        text += item["text"].get<std::string>();
                    }
                }

                if (!text.empty()) {
                    return text;
                }
            }
        }

        return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            "AI response does not contain assistant content",
            502,
            false));
    }

    wikilive::utils::Expected<wikilive::ai::AiSuggestInsertResult> parseSuggestInsertPayload(const std::string& payload) {
        const auto parsed = parseJson(payload);
        if (!parsed) {
            return wikilive::utils::makeUnexpected(parsed.error());
        }

        if (!parsed->contains("candidates") || !(*parsed)["candidates"].is_array()) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::AiApiError,
                "AI suggestInsert payload must contain candidates array",
                502,
                false));
        }

        wikilive::ai::AiSuggestInsertResult result;
        for (const auto& candidateJson : (*parsed)["candidates"]) {
            if (!candidateJson.is_object()) {
                continue;
            }

            wikilive::ai::AiInsertCandidate candidate;
            candidate.tableId = candidateJson.value("tableId", "");
            candidate.recordId = candidateJson.value("recordId", "");
            candidate.fieldName = candidateJson.value("fieldName", "");
            candidate.insert = candidateJson.value("insert", "");
            candidate.reason = candidateJson.value("reason", "");
            candidate.confidence = candidateJson.value("confidence", 0.0);

            if (candidate.tableId.empty() || candidate.recordId.empty() || candidate.fieldName.empty() || candidate.insert.empty()) {
                continue;
            }

            result.candidates.push_back(std::move(candidate));
        }

        return result;
    }

}  // namespace

namespace wikilive::ai {

    OpenRouterAiProvider::OpenRouterAiProvider(
        std::string baseUrl,
        std::string apiKey,
        std::string model,
        OpenRouterAiProviderOptions options)
        : apiKey_(std::move(apiKey)),
        options_(options) {
        metadata_.provider = "openrouter";
        metadata_.model = std::move(model);
        metadata_.baseUrl = baseUrl.empty() ? "https://openrouter.ai/api/v1" : std::move(baseUrl);
        metadata_.enabled = true;
    }

    const AiProviderMetadata& OpenRouterAiProvider::metadata() const {
        return metadata_;
    }

    utils::Expected<AiSuggestInsertResult> OpenRouterAiProvider::suggestInsert(const AiSuggestInsertRequest& request) const {
        return retryPolicy_.run(
            [this, &request]() {
                return suggestInsertOnce(request);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<AiSuggestInsertResult> OpenRouterAiProvider::suggestInsertOnce(const AiSuggestInsertRequest& request) const {
        if (apiKey_.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "OpenRouter provider is missing AI_API_KEY",
                500,
                false));
        }

        if (metadata_.model.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "OpenRouter provider is missing AI_MODEL",
                500,
                false));
        }

        const auto parsedBaseUrl = parseBaseUrl(metadata_.baseUrl);
        if (!parsedBaseUrl) {
            return wikilive::utils::makeUnexpected(parsedBaseUrl.error());
        }

        const json requestBody = {
            {"model", metadata_.model},
            {"messages", json::array({
                {
                    {"role", "system"},
                    {"content", buildSuggestInsertSystemPrompt()},
                },
                {
                    {"role", "user"},
                    {"content", buildSuggestInsertUserPrompt(request)},
                },
            })},
            {"temperature", options_.temperature},
            {"max_tokens", options_.maxTokens},
            {"response_format", {
                {"type", "json_schema"},
                {"json_schema", {
                    {"name", "wikilive_suggest_insert"},
                    {"strict", true},
                    {"schema", buildSuggestInsertJsonSchema()},
                }},
            }},
        };

        const auto response = executeJsonRequest(
            parsedBaseUrl.value(),
            "/chat/completions",
            apiKey_,
            options_.requestTimeoutMs,
            requestBody.dump());
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto parsedResponse = parseJson(response.value());
        if (!parsedResponse) {
            return wikilive::utils::makeUnexpected(parsedResponse.error());
        }

        if (parsedResponse->contains("error") && (*parsedResponse)["error"].is_object()) {
            const auto message = (*parsedResponse)["error"].value("message", std::string("OpenRouter returned an error"));
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::AiApiError,
                message,
                502,
                false));
        }

        const auto content = extractAssistantContent(parsedResponse.value());
        if (!content) {
            return wikilive::utils::makeUnexpected(content.error());
        }

        return parseSuggestInsertPayload(content.value());
    }

}  // namespace wikilive::ai
