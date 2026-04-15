#include "src/api/mws_client.h"

#include <curl/curl.h>

#include <nlohmann/json.hpp>

#include <memory>
#include <algorithm>
#include <cctype>
#include <sstream>
#include <string_view>
#include <utility>

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

    std::string urlEncode(const std::string& value) {
        constexpr char kHex[] = "0123456789ABCDEF";
        std::string encoded;
        encoded.reserve(value.size() * 3);

        for (const unsigned char ch : value) {
            if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' ||
                ch == '.' || ch == '~') {
                encoded.push_back(static_cast<char>(ch));
                continue;
            }

            encoded.push_back('%');
            encoded.push_back(kHex[(ch >> 4) & 0x0F]);
            encoded.push_back(kHex[ch & 0x0F]);
        }

        return encoded;
    }

    std::string makeAbsoluteTablesUrl(const std::string& value) {
        if (value.empty()) {
            return {};
        }

        if (value.rfind("http://", 0) == 0 || value.rfind("https://", 0) == 0) {
            return value;
        }

        if (value.front() == '/') {
            return "https://tables.mws.ru" + value;
        }

        return "https://tables.mws.ru/" + value;
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

    wikilive::utils::Expected<HttpResponse> performHttpRequest(
        const std::string& method,
        const std::string& url,
        const std::vector<std::string>& headers,
        const int timeoutMs,
        const std::string* body = nullptr) {
        using wikilive::utils::ErrorCode;

        (void)curlGlobalInitInstance();

        CURL* rawHandle = curl_easy_init();
        if (rawHandle == nullptr) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                "libcurl initialization failed",
                502,
                true));
        }

        std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> handle(rawHandle, &curl_easy_cleanup);

        std::string responseBody;
        char errorBuffer[CURL_ERROR_SIZE] = {};
        curl_easy_setopt(handle.get(), CURLOPT_ERRORBUFFER, errorBuffer);
        curl_easy_setopt(handle.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(handle.get(), CURLOPT_CUSTOMREQUEST, method.c_str());
        curl_easy_setopt(handle.get(), CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(handle.get(), CURLOPT_CONNECTTIMEOUT_MS, static_cast<long>(timeoutMs));
        curl_easy_setopt(handle.get(), CURLOPT_TIMEOUT_MS, static_cast<long>(timeoutMs));
        curl_easy_setopt(handle.get(), CURLOPT_WRITEFUNCTION, appendResponseBytes);
        curl_easy_setopt(handle.get(), CURLOPT_WRITEDATA, &responseBody);
        curl_easy_setopt(handle.get(), CURLOPT_USERAGENT, "WikiLive/1.0");

        if (body != nullptr) {
            curl_easy_setopt(handle.get(), CURLOPT_POSTFIELDS, body->data());
            curl_easy_setopt(handle.get(), CURLOPT_POSTFIELDSIZE_LARGE, static_cast<curl_off_t>(body->size()));
        }

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
                ErrorCode::MwsApiError,
                curlErrorMessage("Request to MWS", performCode, errorBuffer),
                502,
                true));
        }

        long statusCode = 0;
        curl_easy_getinfo(handle.get(), CURLINFO_RESPONSE_CODE, &statusCode);
        return HttpResponse{ .statusCode = statusCode, .body = std::move(responseBody) };
    }

    wikilive::utils::Expected<std::string> executeRequest(
        const std::string& method,
        const std::string& pathWithQuery,
        const std::string& token,
        const int timeoutMs,
        const std::string& body = {},
        const std::string& contentType = "application/json") {
        using wikilive::utils::ErrorCode;

        std::vector<std::string> headers{
            "Authorization: Bearer " + token,
            "Accept: application/json",
        };
        if (!body.empty()) {
            headers.push_back("Content-Type: " + contentType);
        }

        const auto response = performHttpRequest(
            method,
            makeAbsoluteTablesUrl(pathWithQuery),
            headers,
            timeoutMs,
            body.empty() ? nullptr : &body);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto statusCode = response->statusCode;
        if (statusCode == 429) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::MwsRateLimit,
                "MWS rate limit exceeded",
                429,
                true));
        }

        if (statusCode == 401 || statusCode == 403) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                "MWS rejected the request. Check the token and table permissions.",
                static_cast<int>(statusCode),
                false));
        }

        if (statusCode >= 500) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                "MWS temporary server error: HTTP " + std::to_string(statusCode),
                static_cast<int>(statusCode),
                true));
        }

        if (statusCode >= 400) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                "MWS request failed: HTTP " + std::to_string(statusCode),
                static_cast<int>(statusCode),
                false));
        }

        return response->body;
    }

    std::string guessMimeTypeFromPath(const std::string& value) {
        std::string lower = value;
        std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char ch) {
            return static_cast<char>(std::tolower(ch));
            });

        if (lower.find(".png") != std::string::npos) return "image/png";
        if (lower.find(".jpg") != std::string::npos || lower.find(".jpeg") != std::string::npos) return "image/jpeg";
        if (lower.find(".webp") != std::string::npos) return "image/webp";
        if (lower.find(".gif") != std::string::npos) return "image/gif";
        if (lower.find(".svg") != std::string::npos) return "image/svg+xml";
        if (lower.find(".pdf") != std::string::npos) return "application/pdf";
        return "application/octet-stream";
    }



    std::string sanitizeFilename(const std::string& value) {
        std::string result;
        for (const unsigned char ch : value) {
            if (std::isalnum(ch) || ch == '.' || ch == '_' || ch == '-') {
                result.push_back(static_cast<char>(ch));
            }
        }
        return result.empty() ? std::string("upload.bin") : result;
    }


    std::string buildMultipartBody(
        const std::string& boundary,
        const std::string& filename,
        const std::string& mimeType,
        const std::vector<unsigned char>& bytes) {
        const auto safeFilename = sanitizeFilename(filename);
        const auto safeMimeType = mimeType.empty() ? std::string("application/octet-stream") : mimeType;

        std::string body;
        body.reserve(bytes.size() + 512);

        body += "--" + boundary + "\r\n";
        body += "Content-Disposition: form-data; name=\"file\"; filename=\"" + safeFilename + "\"\r\n";
        body += "Content-Type: " + safeMimeType + "\r\n\r\n";
        body.append(reinterpret_cast<const char*>(bytes.data()), bytes.size());
        body += "\r\n--" + boundary + "--\r\n";

        return body;
    }



    wikilive::utils::Expected<json> parseResponseJson(const std::string& responseBody) {
        try {
            auto parsed = json::parse(responseBody);
            if (parsed.contains("success") && parsed["success"].is_boolean() && !parsed["success"].get<bool>()) {
                const auto code = parsed.contains("code") ? parsed["code"].get<int>() : 502;
                const auto message = parsed.contains("message") && parsed["message"].is_string()
                    ? parsed["message"].get<std::string>()
                    : std::string("MWS responded with an unsuccessful payload");
                return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                    wikilive::utils::ErrorCode::MwsApiError,
                    message,
                    code,
                    code >= 500 || code == 429));
            }
            return parsed;
        }
        catch (const std::exception& exception) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::MwsApiError,
                std::string("Failed to parse MWS JSON response: ") + exception.what(),
                502,
                false));
        }
    }

    std::string jsonValueToString(const json& value) {
        if (value.is_null()) {
            return {};
        }
        if (value.is_string()) {
            return value.get<std::string>();
        }
        if (value.is_boolean()) {
            return value.get<bool>() ? "true" : "false";
        }
        if (value.is_number_integer()) {
            return std::to_string(value.get<long long>());
        }
        if (value.is_number_unsigned()) {
            return std::to_string(value.get<unsigned long long>());
        }
        if (value.is_number_float()) {
            std::ostringstream stream;
            stream << value.get<double>();
            return stream.str();
        }
        if (value.is_array()) {
            std::string result;
            bool first = true;
            for (const auto& item : value) {
                const auto renderedItem = jsonValueToString(item);
                if (renderedItem.empty()) {
                    continue;
                }
                if (!first) {
                    result += ", ";
                }
                first = false;
                result += renderedItem;
            }
            return first ? value.dump() : result;
        }
        if (value.is_object()) {
            if (value.contains("name") && value["name"].is_string()) {
                return value["name"].get<std::string>();
            }
            if (value.contains("url") && value["url"].is_string()) {
                return makeAbsoluteTablesUrl(value["url"].get<std::string>());
            }
            return value.dump();
        }
        return value.dump();
    }

    void applyFieldMetadata(const json& value, wikilive::api::MwsFieldValue& fieldValue) {
        if (value.is_array()) {
            for (const auto& item : value) {
                applyFieldMetadata(item, fieldValue);
                if (!fieldValue.resourceUrl.empty()) {
                    return;
                }
            }
            return;
        }

        if (!value.is_object()) {
            return;
        }

        if (value.contains("url") && value["url"].is_string()) {
            fieldValue.resourceUrl = makeAbsoluteTablesUrl(value["url"].get<std::string>());
        }

        if (value.contains("mimeType") && value["mimeType"].is_string()) {
            fieldValue.mimeType = value["mimeType"].get<std::string>();
            fieldValue.isImage = fieldValue.mimeType.rfind("image/", 0) == 0;
        }

        if (fieldValue.value.empty() && value.contains("name") && value["name"].is_string()) {
            fieldValue.value = value["name"].get<std::string>();
        }
    }


    wikilive::utils::Expected<std::vector<wikilive::api::MwsRecord>> parseRecords(const std::string& responseBody) {
        const auto parsed = parseResponseJson(responseBody);
        if (!parsed) {
            return wikilive::utils::makeUnexpected(parsed.error());
        }

        if (!parsed->contains("data") || !(*parsed)["data"].is_object()) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::MwsApiError,
                "MWS response does not contain a data object",
                502,
                false));
        }

        const auto& data = (*parsed)["data"];
        if (!data.contains("records") || !data["records"].is_array()) {
            return std::vector<wikilive::api::MwsRecord>{};
        }

        std::vector<wikilive::api::MwsRecord> records;
        for (const auto& item : data["records"]) {
            if (!item.is_object()) {
                continue;
            }

            wikilive::api::MwsRecord record;
            if (item.contains("recordId") && item["recordId"].is_string()) {
                record.recordId = item["recordId"].get<std::string>();
            }
            record.payload = item.dump();

            if (item.contains("fields") && item["fields"].is_object()) {
                for (const auto& [key, value] : item["fields"].items()) {
                    record.fields[key] = jsonValueToString(value);
                    record.rawFieldsJson[key] = value.dump();
                }
            }

            records.push_back(std::move(record));
        }

        return records;
    }

    wikilive::utils::Expected<std::vector<wikilive::api::MwsFieldMeta>> parseFields(const std::string& responseBody) {
        const auto parsed = parseResponseJson(responseBody);
        if (!parsed) {
            return wikilive::utils::makeUnexpected(parsed.error());
        }

        if (!parsed->contains("data") || !(*parsed)["data"].is_object()) {
            return wikilive::utils::makeUnexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::MwsApiError,
                "MWS fields response does not contain a data object",
                502,
                false));
        }

        const auto& data = (*parsed)["data"];
        if (!data.contains("fields") || !data["fields"].is_array()) {
            return std::vector<wikilive::api::MwsFieldMeta>{};
        }

        std::vector<wikilive::api::MwsFieldMeta> fields;
        for (const auto& item : data["fields"]) {
            if (!item.is_object()) {
                continue;
            }

            wikilive::api::MwsFieldMeta meta;
            if (item.contains("id") && item["id"].is_string()) {
                meta.id = item["id"].get<std::string>();
            }
            if (item.contains("name") && item["name"].is_string()) {
                meta.name = item["name"].get<std::string>();
            }
            if (item.contains("type") && item["type"].is_string()) {
                meta.type = item["type"].get<std::string>();
            }
            if (item.contains("property") && item["property"].is_object()) {
                meta.property = item["property"];
                if (meta.property.contains("options") && meta.property["options"].is_array()) {
                    for (const auto& option : meta.property["options"]) {
                        if (!option.is_object()) {
                            continue;
                        }
                        wikilive::api::MwsFieldOption parsedOption;
                        if (option.contains("name") && option["name"].is_string()) {
                            parsedOption.name = option["name"].get<std::string>();
                        }
                        if (option.contains("color") && option["color"].is_string()) {
                            parsedOption.color = option["color"].get<std::string>();
                        }
                        if (!parsedOption.name.empty()) {
                            meta.options.push_back(std::move(parsedOption));
                        }
                    }
                }
            }

            fields.push_back(std::move(meta));
        }

        return fields;
    }

    std::string appendViewParameter(const std::string& query, const std::string& viewId) {
        if (viewId.empty()) {
            return query;
        }

        if (query.empty()) {
            return "viewId=" + urlEncode(viewId);
        }

        return query + "&viewId=" + urlEncode(viewId);
    }

    std::string buildRecordIdsQuery(const std::vector<std::string>& recordIds) {
        std::string query;
        for (const auto& recordId : recordIds) {
            if (!query.empty()) {
                query += "&";
            }
            query += "recordIds=" + urlEncode(recordId);
        }
        return query;
    }

    wikilive::utils::Expected<std::vector<wikilive::api::MwsRecord>> requestRecordsForTable(
        const std::string& token,
        const std::string& tableId,
        const std::string& viewId,
        const std::vector<std::string>& recordIds,
        const int timeoutMs) {
        auto query = std::string("fieldKey=name");
        if (!viewId.empty()) {
            query = appendViewParameter(query, viewId);
        }

        const auto recordIdsQuery = buildRecordIdsQuery(recordIds);
        if (!recordIdsQuery.empty()) {
            query += "&" + recordIdsQuery;
        }

        const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId) + "/records?" + query;
        const auto response = executeRequest("GET", path, token, timeoutMs);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        return parseRecords(response.value());
    }

    const wikilive::api::MwsRecord* findRecordById(
        const std::vector<wikilive::api::MwsRecord>& records,
        const std::string& recordId) {
        for (const auto& record : records) {
            if (record.recordId == recordId) {
                return &record;
            }
        }

        return nullptr;
    }

}  // namespace

namespace wikilive::api {

    MwsClient::MwsClient(std::string token, std::string tableId, std::string viewId, MwsClientOptions options)
        : token_(std::move(token)),
        tableId_(std::move(tableId)),
        viewId_(std::move(viewId)),
        options_(options) {
    }

    const std::string& MwsClient::tableId() const {
        return tableId_;
    }

    const std::string& MwsClient::viewId() const {
        return viewId_;
    }

    utils::Expected<std::vector<MwsRecord>> MwsClient::getRecords(const std::vector<std::string>& recordIds) {
        return getRecordsForTable(tableId_, viewId_, recordIds);
    }

    utils::Expected<std::vector<MwsRecord>> MwsClient::getRecordsForTable(
        const std::string& tableId,
        const std::string& viewId,
        const std::vector<std::string>& recordIds) {
        const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
        const auto resolvedViewId = viewId.empty() ? viewId_ : viewId;
        const bool usesConfiguredTable = resolvedTableId == tableId_ && resolvedViewId == viewId_;

        auto result = retryPolicy_.run(
            [this, &resolvedTableId, &resolvedViewId, &recordIds]() {
                return getRecordsOnce(resolvedTableId, resolvedViewId, recordIds);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);

        if (result) {
            if (recordIds.empty() && usesConfiguredTable) {
                lastGoodRecords_ = result.value();
            }
            return result;
        }

        if (recordIds.empty() && usesConfiguredTable) {
            if (!lastGoodRecords_.empty()) {
                return lastGoodRecords_;
            }
        }

        return result;
    }

    utils::Expected<MwsFieldValue> MwsClient::getFieldValue(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) {
        return retryPolicy_.run(
            [this, &tableId, &recordId, &fieldName]() {
                return getFieldValueOnce(tableId, recordId, fieldName);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::vector<MwsFieldMeta>> MwsClient::getFieldsForTable(
        const std::string& tableId,
        const std::string& viewId) {
        const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
        const auto resolvedViewId = viewId.empty() ? viewId_ : viewId;

        return retryPolicy_.run(
            [this, &resolvedTableId, &resolvedViewId]() -> utils::Expected<std::vector<MwsFieldMeta>> {
                if (token_.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidConfig,
                        "MWS client is missing MWS_TOKEN in .env.",
                        500,
                        false));
                }

                if (resolvedTableId.empty()) {
                    return wikilive::utils::makeUnexpected(missingConfigurationError());
                }

                auto query = std::string{};
                if (!resolvedViewId.empty()) {
                    query = appendViewParameter(query, resolvedViewId);
                }

                const auto path = query.empty()
                    ? "/fusion/v1/datasheets/" + urlEncode(resolvedTableId) + "/fields"
                    : "/fusion/v1/datasheets/" + urlEncode(resolvedTableId) + "/fields?" + query;

                const auto response = executeRequest("GET", path, token_, options_.requestTimeoutMs);
                if (!response) {
                    return wikilive::utils::makeUnexpected(response.error());
                }

                return parseFields(response.value());
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }


    utils::Expected<MwsUploadedAttachment> MwsClient::uploadAttachmentForField(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldId,
        const std::string& filename,
        const std::string& mimeType,
        const std::vector<unsigned char>& bytes) {
        return retryPolicy_.run(
            [this, &tableId, &recordId, &fieldId, &filename, &mimeType, &bytes]() -> utils::Expected<MwsUploadedAttachment> {
                if (token_.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidConfig,
                        "MWS client is missing MWS_TOKEN in .env.",
                        500,
                        false));
                }

                if (tableId.empty() || recordId.empty() || fieldId.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "tableId, recordId and fieldId must not be empty for MWS attachment upload",
                        400,
                        false));
                }

                if (bytes.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Attachment content must not be empty",
                        400,
                        false));
                }

                const std::string boundary = "----WikiLiveMwsBoundary7MA4YWxkTrZu0gW";
                const std::string body = buildMultipartBody(boundary, filename, mimeType, bytes);

                const auto path =
                    "/fusion/v1/datasheets/" + urlEncode(tableId) +
                    "/attachments?recordId=" + urlEncode(recordId) +
                    "&fieldId=" + urlEncode(fieldId);

                const auto response = executeRequest(
                    "POST",
                    path,
                    token_,
                    options_.requestTimeoutMs,
                    body,
                    "multipart/form-data; boundary=" + boundary);

                if (!response) {
                    return wikilive::utils::makeUnexpected(response.error());
                }

                const auto parsed = parseResponseJson(response.value());
                if (!parsed) {
                    return wikilive::utils::makeUnexpected(parsed.error());
                }

                if (!parsed->contains("data") || !(*parsed)["data"].is_object()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::MwsApiError,
                        "MWS attachment upload response does not contain data object",
                        502,
                        false));
                }

                const auto& data = (*parsed)["data"];
                MwsUploadedAttachment result;
                result.token = data.value("token", std::string{});
                result.name = data.value("name", filename);
                result.mimeType = data.value("mimeType", mimeType);
                result.bucket = data.value("bucket", std::string{});
                result.size = data.contains("size") && data["size"].is_number_unsigned()
                    ? static_cast<std::size_t>(data["size"].get<unsigned long long>())
                    : static_cast<std::size_t>(bytes.size());

                const auto rawUrl = data.value("url", std::string{});
                result.url = makeAbsoluteTablesUrl(rawUrl);
                result.isImage = result.mimeType.rfind("image/", 0) == 0;

                if (result.token.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::MwsApiError,
                        "MWS attachment upload did not return token",
                        502,
                        false));
                }

                return result;
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::string> MwsClient::createRecord(const std::string& payload) {
        return retryPolicy_.run(
            [this, &payload]() {
                return createRecordOnce(payload);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::string> MwsClient::updateRecord(const std::string& recordId, const std::string& payload) {
        return retryPolicy_.run(
            [this, &recordId, &payload]() {
                return updateRecordOnce(recordId, payload);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::string> MwsClient::downloadAttachmentByPath(
        const std::string& relativePath,
        std::string& outMimeType) {
        return retryPolicy_.run(
            [this, &relativePath, &outMimeType]() -> utils::Expected<std::string> {
                if (token_.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidConfig,
                        "MWS client is missing MWS_TOKEN in .env.",
                        500,
                        false));
                }

                if (relativePath.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "relativePath must not be empty",
                        400,
                        false));
                }

                const std::string path =
                    relativePath.front() == '/'
                    ? relativePath
                    : "/" + relativePath;

                const auto response = executeRequest(
                    "GET",
                    path,
                    token_,
                    options_.requestTimeoutMs,
                    {},
                    "application/octet-stream");

                if (!response) {
                    return wikilive::utils::makeUnexpected(response.error());
                }

                outMimeType = guessMimeTypeFromPath(path);
                return response.value();
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::string> MwsClient::downloadAttachment(
        const std::string& tableId,
        const std::string& token,
        std::string& outMimeType) {
        return retryPolicy_.run(
            [this, &tableId, &token, &outMimeType]() -> utils::Expected<std::string> {
                if (token_.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidConfig,
                        "MWS client is missing MWS_TOKEN in .env.",
                        500,
                        false));
                }

                if (tableId.empty() || token.empty()) {
                    return wikilive::utils::makeUnexpected(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "tableId and token must not be empty",
                        400,
                        false));
                }

                const auto path =
                    "/fusion/v1/datasheets/" + urlEncode(tableId) +
                    "/attachments?token=" + urlEncode(token);

                const auto response = executeRequest(
                    "GET",
                    path,
                    token_,
                    options_.requestTimeoutMs,
                    {},
                    "application/octet-stream"
                );

                if (!response) {
                    return wikilive::utils::makeUnexpected(response.error());
                }

                outMimeType = "application/octet-stream";
                return response.value();
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::string> MwsClient::updateRecordForTable(
        const std::string& tableId,
        const std::string& viewId,
        const std::string& recordId,
        const std::string& payload) {
        const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
        const auto resolvedViewId = viewId.empty() ? viewId_ : viewId;

        return retryPolicy_.run(
            [this, &resolvedTableId, &resolvedViewId, &recordId, &payload]() {
                return updateRecordOnceForTable(resolvedTableId, resolvedViewId, recordId, payload);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::VoidExpected MwsClient::deleteRecord(const std::string& recordId) {
        return retryPolicy_.run(
            [this, &recordId]() {
                return deleteRecordOnce(recordId);
            },
            options_.retryAttempts,
            options_.retryBaseDelayMs);
    }

    utils::Expected<std::vector<MwsRecord>> MwsClient::getRecordsOnce(
        const std::string& tableId,
        const std::string& viewId,
        const std::vector<std::string>& recordIds) const {
        if (token_.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is missing MWS_TOKEN in .env.",
                500,
                false));
        }

        if (tableId.empty()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        return requestRecordsForTable(token_, tableId, viewId, recordIds, options_.requestTimeoutMs);
    }

    utils::Expected<MwsFieldValue> MwsClient::getFieldValueOnce(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) const {
        if (token_.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is missing MWS_TOKEN in .env.",
                500,
                false));
        }

        if (recordId.empty() || fieldName.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "recordId and fieldName must not be empty",
                400,
                false));
        }

        const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
        if (resolvedTableId.empty()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        const bool useConfiguredView = resolvedTableId == tableId_ && !viewId_.empty();
        const auto resolveFromRecords =
            [&recordId, &fieldName](const std::vector<MwsRecord>& records) -> utils::Expected<MwsFieldValue> {
            const auto* record = findRecordById(records, recordId);
            if (record == nullptr) {
                return wikilive::utils::makeUnexpected(utils::makeError(
                    utils::ErrorCode::PageNotFound,
                    "MWS record was not found: " + recordId,
                    404,
                    false));
            }

            const auto fieldIt = record->fields.find(fieldName);
            if (fieldIt == record->fields.end()) {
                return wikilive::utils::makeUnexpected(utils::makeError(
                    utils::ErrorCode::MwsApiError,
                    "Field was not found in MWS record: " + fieldName,
                    404,
                    false));
            }

            MwsFieldValue result{
                .recordId = record->recordId,
                .fieldName = fieldName,
                .value = fieldIt->second,
            };

            if (const auto rawFieldIt = record->rawFieldsJson.find(fieldName); rawFieldIt != record->rawFieldsJson.end()) {
                try {
                    applyFieldMetadata(json::parse(rawFieldIt->second), result);
                }
                catch (...) {
                }
            }

            return result;
            };

        auto tryResolve =
            [this, &resolvedTableId, &resolveFromRecords](const std::string& queryViewId,
                const std::vector<std::string>& recordIds) -> utils::Expected<MwsFieldValue> {
                    const auto records = requestRecordsForTable(
                        token_,
                        resolvedTableId,
                        queryViewId,
                        recordIds,
                        options_.requestTimeoutMs);
                    if (!records) {
                        return wikilive::utils::makeUnexpected(records.error());
                    }

                    return resolveFromRecords(records.value());
            };

        std::vector<utils::Expected<MwsFieldValue>> attempts;
        attempts.reserve(4);

        const auto primaryViewId = useConfiguredView ? viewId_ : std::string{};
        attempts.push_back(tryResolve(primaryViewId, { recordId }));

        if (!attempts.back()) {
            attempts.push_back(tryResolve(primaryViewId, {}));
        }

        if (useConfiguredView) {
            if (!attempts.back()) {
                attempts.push_back(tryResolve({}, { recordId }));
            }
            if (!attempts.back()) {
                attempts.push_back(tryResolve({}, {}));
            }
        }

        utils::Error lastError = utils::makeError(
            utils::ErrorCode::PageNotFound,
            "MWS record was not found: " + recordId,
            404,
            false);

        for (auto& attempt : attempts) {
            if (attempt) {
                return attempt.value();
            }

            lastError = attempt.error();
            if (lastError.code == utils::ErrorCode::MwsRateLimit ||
                (lastError.code == utils::ErrorCode::MwsApiError && lastError.httpStatus >= 500)) {
                return wikilive::utils::makeUnexpected(lastError);
            }
        }

        return wikilive::utils::makeUnexpected(lastError);
    }

    utils::Expected<std::string> MwsClient::createRecordOnce(const std::string& payload) const {
        if (!hasConfiguration()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        if (payload.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Create payload must not be empty",
                400,
                false));
        }

        const auto query = appendViewParameter("fieldKey=name", viewId_);
        const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) + "/records?" + query;
        const auto response = executeRequest("POST", path, token_, options_.requestTimeoutMs, payload);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto records = parseRecords(response.value());
        if (!records) {
            return wikilive::utils::makeUnexpected(records.error());
        }

        if (records->empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::MwsApiError,
                "MWS create response does not contain created records",
                502,
                false));
        }

        return records->front().recordId;
    }

    utils::Expected<std::string> MwsClient::updateRecordOnce(const std::string& recordId, const std::string& payload) const {
        if (!hasConfiguration()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        return updateRecordOnceForTable(tableId_, viewId_, recordId, payload);
    }

    utils::Expected<std::string> MwsClient::updateRecordOnceForTable(
        const std::string& tableId,
        const std::string& viewId,
        const std::string& recordId,
        const std::string& payload) const {
        if (token_.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is missing MWS_TOKEN in .env.",
                500,
                false));
        }

        if (tableId.empty()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        if (recordId.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "recordId must not be empty",
                400,
                false));
        }

        if (payload.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Update payload must not be empty",
                400,
                false));
        }

        const auto query = appendViewParameter("fieldKey=name", viewId);
        const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId) + "/records?" + query;
        const auto response = executeRequest("PATCH", path, token_, options_.requestTimeoutMs, payload);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto records = parseRecords(response.value());
        if (!records) {
            return wikilive::utils::makeUnexpected(records.error());
        }

        if (records->empty()) {
            return recordId;
        }

        return records->front().recordId.empty() ? recordId : records->front().recordId;
    }

    utils::VoidExpected MwsClient::deleteRecordOnce(const std::string& recordId) const {
        if (!hasConfiguration()) {
            return wikilive::utils::makeUnexpected(missingConfigurationError());
        }

        if (recordId.empty()) {
            return wikilive::utils::makeUnexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "recordId must not be empty",
                400,
                false));
        }

        const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) + "/records?recordIds=" + urlEncode(recordId);
        const auto response = executeRequest("DELETE", path, token_, options_.requestTimeoutMs);
        if (!response) {
            return wikilive::utils::makeUnexpected(response.error());
        }

        const auto parsed = parseResponseJson(response.value());
        if (!parsed) {
            return wikilive::utils::makeUnexpected(parsed.error());
        }

        return {};
    }

    bool MwsClient::hasConfiguration() const {
        return !token_.empty() && !tableId_.empty() && !viewId_.empty();
    }

    utils::Error MwsClient::missingConfigurationError() const {
        return utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "MWS client is missing configuration. Set MWS_TOKEN, MWS_TABLE_ID and MWS_VIEW_ID in .env.",
            500,
            false);
    }

}  // namespace wikilive::api
