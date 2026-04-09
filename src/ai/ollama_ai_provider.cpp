#include "src/ai/ollama_ai_provider.h"

#include <windows.h>
#include <winhttp.h>

#include <nlohmann/json.hpp>

#include <string_view>
#include <utility>

#include "src/ai/openrouter_prompt_builder.h"

namespace {

using json = nlohmann::json;

class WinHttpHandle {
public:
    explicit WinHttpHandle(HINTERNET handle = nullptr)
        : handle_(handle) {
    }

    ~WinHttpHandle() {
        if (handle_ != nullptr) {
            WinHttpCloseHandle(handle_);
        }
    }

    WinHttpHandle(const WinHttpHandle&) = delete;
    WinHttpHandle& operator=(const WinHttpHandle&) = delete;

    WinHttpHandle(WinHttpHandle&& other) noexcept
        : handle_(std::exchange(other.handle_, nullptr)) {
    }

    WinHttpHandle& operator=(WinHttpHandle&& other) noexcept {
        if (this != &other) {
            if (handle_ != nullptr) {
                WinHttpCloseHandle(handle_);
            }
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

    [[nodiscard]] HINTERNET get() const {
        return handle_;
    }

    [[nodiscard]] explicit operator bool() const {
        return handle_ != nullptr;
    }

private:
    HINTERNET handle_ = nullptr;
};

std::wstring toWide(const std::string& value) {
    if (value.empty()) {
        return {};
    }

    const int size = MultiByteToWideChar(CP_UTF8, 0, value.c_str(), static_cast<int>(value.size()), nullptr, 0);
    if (size <= 0) {
        return {};
    }

    std::wstring wide(size, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, value.c_str(), static_cast<int>(value.size()), wide.data(), size);
    return wide;
}

std::string lastWinHttpErrorMessage(const std::string& operation) {
    const DWORD errorCode = GetLastError();
    LPSTR buffer = nullptr;
    const DWORD size = FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        errorCode,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        reinterpret_cast<LPSTR>(&buffer),
        0,
        nullptr);

    std::string message = operation + " failed";
    if (size != 0 && buffer != nullptr) {
        message += ": ";
        message.append(buffer, size);
        while (!message.empty() && (message.back() == '\r' || message.back() == '\n' || message.back() == ' ')) {
            message.pop_back();
        }
    }

    if (buffer != nullptr) {
        LocalFree(buffer);
    }

    message += " (WinHTTP code " + std::to_string(errorCode) + ")";
    return message;
}

struct ParsedUrl {
    bool secure = false;
    INTERNET_PORT port = INTERNET_DEFAULT_HTTP_PORT;
    std::wstring host;
    std::wstring basePath;
};

wikilive::utils::Expected<ParsedUrl> parseBaseUrl(const std::string& baseUrl) {
    URL_COMPONENTS components{};
    components.dwStructSize = sizeof(components);

    std::wstring wideUrl = toWide(baseUrl);
    std::wstring hostBuffer(256, L'\0');
    std::wstring pathBuffer(1024, L'\0');

    components.lpszHostName = hostBuffer.data();
    components.dwHostNameLength = static_cast<DWORD>(hostBuffer.size());
    components.lpszUrlPath = pathBuffer.data();
    components.dwUrlPathLength = static_cast<DWORD>(pathBuffer.size());

    if (!WinHttpCrackUrl(wideUrl.c_str(), static_cast<DWORD>(wideUrl.size()), 0, &components)) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::InvalidConfig,
            lastWinHttpErrorMessage("Parsing AI_BASE_URL"),
            500,
            false));
    }

    ParsedUrl parsed;
    parsed.secure = components.nScheme == INTERNET_SCHEME_HTTPS;
    parsed.port = components.nPort;
    parsed.host.assign(components.lpszHostName, components.dwHostNameLength);
    parsed.basePath.assign(components.lpszUrlPath, components.dwUrlPathLength);
    return parsed;
}

std::wstring joinPath(const std::wstring& basePath, const std::wstring& suffix) {
    if (basePath.empty()) {
        return suffix;
    }

    if (basePath.back() == L'/' && !suffix.empty() && suffix.front() == L'/') {
        return basePath.substr(0, basePath.size() - 1) + suffix;
    }

    if (basePath.back() != L'/' && !suffix.empty() && suffix.front() != L'/') {
        return basePath + L"/" + suffix;
    }

    return basePath + suffix;
}

wikilive::utils::Expected<std::string> executeJsonRequest(
    const ParsedUrl& baseUrl,
    const std::wstring& endpointPath,
    const int timeoutMs,
    const std::string& body) {
    using wikilive::utils::ErrorCode;

    WinHttpHandle session(WinHttpOpen(
        L"WikiLive/1.0",
        WINHTTP_ACCESS_TYPE_NO_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        0));
    if (!session) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("WinHTTP session initialization"),
            502,
            true));
    }

    WinHttpSetTimeouts(session.get(), timeoutMs, timeoutMs, timeoutMs, timeoutMs);

    DWORD secureProtocols = WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_2;
#ifdef WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_3
    secureProtocols |= WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_3;
#endif
    WinHttpSetOption(session.get(), WINHTTP_OPTION_SECURE_PROTOCOLS, &secureProtocols, sizeof(secureProtocols));

    WinHttpHandle connection(WinHttpConnect(session.get(), baseUrl.host.c_str(), baseUrl.port, 0));
    if (!connection) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("WinHTTP connection to Ollama"),
            502,
            true));
    }

    const auto fullPath = joinPath(baseUrl.basePath, endpointPath);
    const DWORD requestFlags = baseUrl.secure ? WINHTTP_FLAG_SECURE : 0;
    WinHttpHandle request(WinHttpOpenRequest(
        connection.get(),
        L"POST",
        fullPath.c_str(),
        nullptr,
        WINHTTP_NO_REFERER,
        WINHTTP_DEFAULT_ACCEPT_TYPES,
        requestFlags));
    if (!request) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("WinHTTP Ollama request initialization"),
            502,
            true));
    }

    const auto wideHeaders = toWide("Content-Type: application/json\r\nAccept: application/json\r\n");
    const LPVOID requestBody = body.empty() ? WINHTTP_NO_REQUEST_DATA : const_cast<char*>(body.data());
    const DWORD requestBodySize = static_cast<DWORD>(body.size());

    if (!WinHttpSendRequest(
            request.get(),
            wideHeaders.c_str(),
            static_cast<DWORD>(wideHeaders.size()),
            requestBody,
            requestBodySize,
            requestBodySize,
            0)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("Sending request to Ollama"),
            502,
            true));
    }

    if (!WinHttpReceiveResponse(request.get(), nullptr)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("Receiving response from Ollama"),
            502,
            true));
    }

    DWORD statusCode = 0;
    DWORD statusCodeSize = sizeof(statusCode);
    if (!WinHttpQueryHeaders(
            request.get(),
            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
            WINHTTP_HEADER_NAME_BY_INDEX,
            &statusCode,
            &statusCodeSize,
            WINHTTP_NO_HEADER_INDEX)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            lastWinHttpErrorMessage("Reading Ollama HTTP status code"),
            502,
            true));
    }

    std::string responseBody;
    for (;;) {
        DWORD availableSize = 0;
        if (!WinHttpQueryDataAvailable(request.get(), &availableSize)) {
            return std::unexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                lastWinHttpErrorMessage("Querying Ollama response size"),
                502,
                true));
        }

        if (availableSize == 0) {
            break;
        }

        std::string buffer(availableSize, '\0');
        DWORD bytesRead = 0;
        if (!WinHttpReadData(request.get(), buffer.data(), availableSize, &bytesRead)) {
            return std::unexpected(wikilive::utils::makeError(
                ErrorCode::AiApiError,
                lastWinHttpErrorMessage("Reading Ollama response body"),
                502,
                true));
        }

        buffer.resize(bytesRead);
        responseBody += buffer;
    }

    if (statusCode == 429) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiRateLimit,
            "Ollama rate limit exceeded",
            429,
            true));
    }

    if (statusCode >= 500) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            "Ollama temporary server error: HTTP " + std::to_string(statusCode),
            static_cast<int>(statusCode),
            true));
    }

    if (statusCode >= 400) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::AiApiError,
            "Ollama request failed: HTTP " + std::to_string(statusCode),
            static_cast<int>(statusCode),
            false));
    }

    return responseBody;
}

wikilive::utils::Expected<json> parseJson(const std::string& responseBody) {
    try {
        return json::parse(responseBody);
    } catch (const std::exception& exception) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            std::string("Failed to parse Ollama JSON response: ") + exception.what(),
            502,
            false));
    }
}

wikilive::utils::Expected<std::string> extractAssistantContent(const json& response) {
    if (response.contains("error") && response["error"].is_string()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            response["error"].get<std::string>(),
            502,
            false));
    }

    if (!response.contains("message") || !response["message"].is_object()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            "Ollama response does not contain message object",
            502,
            false));
    }

    const auto& message = response["message"];
    if (!message.contains("content") || !message["content"].is_string()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            "Ollama response does not contain assistant content",
            502,
            false));
    }

    return message["content"].get<std::string>();
}

wikilive::utils::Expected<wikilive::ai::AiSuggestInsertResult> parseSuggestInsertPayload(const std::string& payload) {
    const auto parsed = parseJson(payload);
    if (!parsed) {
        return std::unexpected(parsed.error());
    }

    if (!parsed->contains("candidates") || !(*parsed)["candidates"].is_array()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::AiApiError,
            "Ollama suggestInsert payload must contain candidates array",
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

        if (candidate.tableId.empty() || candidate.recordId.empty() || candidate.fieldName.empty()) {
            continue;
        }

        result.candidates.push_back(std::move(candidate));
    }

    return result;
}

}  // namespace

namespace wikilive::ai {

OllamaAiProvider::OllamaAiProvider(std::string baseUrl, std::string model, OllamaAiProviderOptions options)
    : options_(options) {
    metadata_.provider = "ollama";
    metadata_.model = std::move(model);
    metadata_.baseUrl = baseUrl.empty() ? "http://127.0.0.1:11434/api" : std::move(baseUrl);
    metadata_.enabled = true;
}

const AiProviderMetadata& OllamaAiProvider::metadata() const {
    return metadata_;
}

utils::Expected<AiSuggestInsertResult> OllamaAiProvider::suggestInsert(const AiSuggestInsertRequest& request) const {
    return retryPolicy_.run(
        [this, &request]() {
            return suggestInsertOnce(request);
        },
        options_.retryAttempts,
        options_.retryBaseDelayMs);
}

utils::Expected<AiSuggestInsertResult> OllamaAiProvider::suggestInsertOnce(const AiSuggestInsertRequest& request) const {
    if (metadata_.model.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "Ollama provider is missing AI_MODEL",
            500,
            false));
    }

    const auto parsedBaseUrl = parseBaseUrl(metadata_.baseUrl);
    if (!parsedBaseUrl) {
        return std::unexpected(parsedBaseUrl.error());
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
        {"stream", false},
        {"format", buildSuggestInsertJsonSchema()},
        {"options", {
            {"temperature", options_.temperature},
            {"num_predict", options_.maxTokens},
        }},
    };

    const auto response = executeJsonRequest(
        parsedBaseUrl.value(),
        L"/chat",
        options_.requestTimeoutMs,
        requestBody.dump());
    if (!response) {
        return std::unexpected(response.error());
    }

    const auto parsedResponse = parseJson(response.value());
    if (!parsedResponse) {
        return std::unexpected(parsedResponse.error());
    }

    const auto content = extractAssistantContent(parsedResponse.value());
    if (!content) {
        return std::unexpected(content.error());
    }

    return parseSuggestInsertPayload(content.value());
}

}  // namespace wikilive::ai
