#include "src/api/mws_client.h"

#include <windows.h>
#include <winhttp.h>

#include <nlohmann/json.hpp>

#include <sstream>
#include <string_view>
#include <utility>

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

wikilive::utils::Expected<std::string> executeRequest(
    const std::string& method,
    const std::wstring& pathWithQuery,
    const std::string& token,
    const int timeoutMs,
    const std::string& body = {},
    const std::string& contentType = "application/json") {
    using wikilive::utils::ErrorCode;

    WinHttpHandle session(WinHttpOpen(L"WikiLive/1.0", WINHTTP_ACCESS_TYPE_NO_PROXY, WINHTTP_NO_PROXY_NAME,
                                      WINHTTP_NO_PROXY_BYPASS, 0));
    if (!session) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
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

    WinHttpHandle connection(WinHttpConnect(session.get(), L"tables.mws.ru", INTERNET_DEFAULT_HTTPS_PORT, 0));
    if (!connection) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            lastWinHttpErrorMessage("WinHTTP connection to tables.mws.ru"),
            502,
            true));
    }

    const auto wideMethod = toWide(method);
    WinHttpHandle request(WinHttpOpenRequest(connection.get(), wideMethod.c_str(), pathWithQuery.c_str(), nullptr, WINHTTP_NO_REFERER,
                                             WINHTTP_DEFAULT_ACCEPT_TYPES, WINHTTP_FLAG_SECURE));
    if (!request) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            lastWinHttpErrorMessage("WinHTTP request initialization"),
            502,
            true));
    }

    // Compatibility fallback for environments where the local Windows certificate
    // store or inspection proxy breaks the TLS handshake to MWS during development.
    DWORD securityFlags =
        SECURITY_FLAG_IGNORE_UNKNOWN_CA |
        SECURITY_FLAG_IGNORE_CERT_CN_INVALID |
        SECURITY_FLAG_IGNORE_CERT_DATE_INVALID |
        SECURITY_FLAG_IGNORE_CERT_WRONG_USAGE;
    WinHttpSetOption(request.get(), WINHTTP_OPTION_SECURITY_FLAGS, &securityFlags, sizeof(securityFlags));

    std::string headers = "Authorization: Bearer " + token + "\r\nAccept: application/json\r\n";
    if (!body.empty()) {
        headers += "Content-Type: " + contentType + "\r\n";
    }
    const auto wideHeaders = toWide(headers);

    const LPVOID requestBody = body.empty() ? WINHTTP_NO_REQUEST_DATA : const_cast<char*>(body.data());
    const DWORD requestBodySize = static_cast<DWORD>(body.size());

    if (!WinHttpSendRequest(request.get(), wideHeaders.c_str(), static_cast<DWORD>(wideHeaders.size()), requestBody, requestBodySize,
                            requestBodySize, 0)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            lastWinHttpErrorMessage("Sending request to MWS"),
            502,
            true));
    }

    if (!WinHttpReceiveResponse(request.get(), nullptr)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            lastWinHttpErrorMessage("Receiving response from MWS"),
            502,
            true));
    }

    DWORD statusCode = 0;
    DWORD statusCodeSize = sizeof(statusCode);
    if (!WinHttpQueryHeaders(request.get(), WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER, WINHTTP_HEADER_NAME_BY_INDEX,
                             &statusCode, &statusCodeSize, WINHTTP_NO_HEADER_INDEX)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            lastWinHttpErrorMessage("Reading MWS HTTP status code"),
            502,
            true));
    }

    std::string responseBody;
    for (;;) {
        DWORD availableSize = 0;
        if (!WinHttpQueryDataAvailable(request.get(), &availableSize)) {
            return std::unexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                lastWinHttpErrorMessage("Querying MWS response size"),
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
                ErrorCode::MwsApiError,
                lastWinHttpErrorMessage("Reading MWS response body"),
                502,
                true));
        }

        buffer.resize(bytesRead);
        responseBody += buffer;
    }

    if (statusCode == 429) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsRateLimit,
            "MWS rate limit exceeded",
            429,
            true));
    }

    if (statusCode == 401 || statusCode == 403) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "MWS rejected the request. Check the token and table permissions.",
            static_cast<int>(statusCode),
            false));
    }

    if (statusCode >= 500) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "MWS temporary server error: HTTP " + std::to_string(statusCode),
            static_cast<int>(statusCode),
            true));
    }

    if (statusCode >= 400) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "MWS request failed: HTTP " + std::to_string(statusCode),
            static_cast<int>(statusCode),
            false));
    }

    return responseBody;
}

wikilive::utils::Expected<json> parseResponseJson(const std::string& responseBody) {
    try {
        auto parsed = json::parse(responseBody);
        if (parsed.contains("success") && parsed["success"].is_boolean() && !parsed["success"].get<bool>()) {
            const auto code = parsed.contains("code") ? parsed["code"].get<int>() : 502;
            const auto message = parsed.contains("message") && parsed["message"].is_string()
                                     ? parsed["message"].get<std::string>()
                                     : std::string("MWS responded with an unsuccessful payload");
            return std::unexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::MwsApiError,
                message,
                code,
                code >= 500 || code == 429));
        }
        return parsed;
    } catch (const std::exception& exception) {
        return std::unexpected(wikilive::utils::makeError(
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
            return value["url"].get<std::string>();
        }
        return value.dump();
    }
    return value.dump();
}

wikilive::utils::Expected<std::vector<wikilive::api::MwsRecord>> parseRecords(const std::string& responseBody) {
    const auto parsed = parseResponseJson(responseBody);
    if (!parsed) {
        return std::unexpected(parsed.error());
    }

    if (!parsed->contains("data") || !(*parsed)["data"].is_object()) {
        return std::unexpected(wikilive::utils::makeError(
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
            }
        }

        records.push_back(std::move(record));
    }

    return records;
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
    const auto response = executeRequest("GET", toWide(path), token, timeoutMs);
    if (!response) {
        return std::unexpected(response.error());
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
    auto result = retryPolicy_.run(
        [this, &recordIds]() {
            return getRecordsOnce(recordIds);
        },
        options_.retryAttempts,
        options_.retryBaseDelayMs);

    if (result) {
        if (recordIds.empty()) {
            lastGoodRecords_ = result.value();
        }
        return result;
    }

    if (recordIds.empty()) {
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

utils::VoidExpected MwsClient::deleteRecord(const std::string& recordId) {
    return retryPolicy_.run(
        [this, &recordId]() {
            return deleteRecordOnce(recordId);
        },
        options_.retryAttempts,
        options_.retryBaseDelayMs);
}

utils::Expected<std::vector<MwsRecord>> MwsClient::getRecordsOnce(const std::vector<std::string>& recordIds) const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    return requestRecordsForTable(token_, tableId_, viewId_, recordIds, options_.requestTimeoutMs);
}

utils::Expected<MwsFieldValue> MwsClient::getFieldValueOnce(
    const std::string& tableId,
    const std::string& recordId,
    const std::string& fieldName) const {
    if (token_.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "MWS client is missing MWS_TOKEN in .env.",
            500,
            false));
    }

    if (recordId.empty() || fieldName.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "recordId and fieldName must not be empty",
            400,
            false));
    }

    const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
    if (resolvedTableId.empty()) {
        return std::unexpected(missingConfigurationError());
    }

    const bool useConfiguredView = resolvedTableId == tableId_ && !viewId_.empty();
    const auto resolveFromRecords =
        [&recordId, &fieldName](const std::vector<MwsRecord>& records) -> utils::Expected<MwsFieldValue> {
        const auto* record = findRecordById(records, recordId);
        if (record == nullptr) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::PageNotFound,
                "MWS record was not found: " + recordId,
                404,
                false));
        }

        const auto fieldIt = record->fields.find(fieldName);
        if (fieldIt == record->fields.end()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::MwsApiError,
                "Field was not found in MWS record: " + fieldName,
                404,
                false));
        }

        return MwsFieldValue{
            .recordId = record->recordId,
            .fieldName = fieldName,
            .value = fieldIt->second,
        };
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
            return std::unexpected(records.error());
        }

        return resolveFromRecords(records.value());
    };

    std::vector<utils::Expected<MwsFieldValue>> attempts;
    attempts.reserve(4);

    const auto primaryViewId = useConfiguredView ? viewId_ : std::string{};
    attempts.push_back(tryResolve(primaryViewId, {recordId}));

    if (!attempts.back()) {
        attempts.push_back(tryResolve(primaryViewId, {}));
    }

    if (useConfiguredView) {
        if (!attempts.back()) {
            attempts.push_back(tryResolve({}, {recordId}));
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
            return std::unexpected(lastError);
        }
    }

    return std::unexpected(lastError);
}

utils::Expected<std::string> MwsClient::createRecordOnce(const std::string& payload) const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    if (payload.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Create payload must not be empty",
            400,
            false));
    }

    const auto query = appendViewParameter("fieldKey=name", viewId_);
    const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) + "/records?" + query;
    const auto response = executeRequest("POST", toWide(path), token_, options_.requestTimeoutMs, payload);
    if (!response) {
        return std::unexpected(response.error());
    }

    const auto records = parseRecords(response.value());
    if (!records) {
        return std::unexpected(records.error());
    }

    if (records->empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::MwsApiError,
            "MWS create response does not contain created records",
            502,
            false));
    }

    return records->front().recordId;
}

utils::Expected<std::string> MwsClient::updateRecordOnce(const std::string& recordId, const std::string& payload) const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    if (recordId.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "recordId must not be empty",
            400,
            false));
    }

    if (payload.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Update payload must not be empty",
            400,
            false));
    }

    const auto query = appendViewParameter("fieldKey=name", viewId_);
    const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) + "/records?" + query;
    const auto response = executeRequest("PATCH", toWide(path), token_, options_.requestTimeoutMs, payload);
    if (!response) {
        return std::unexpected(response.error());
    }

    const auto records = parseRecords(response.value());
    if (!records) {
        return std::unexpected(records.error());
    }

    if (records->empty()) {
        return recordId;
    }

    return records->front().recordId.empty() ? recordId : records->front().recordId;
}

utils::VoidExpected MwsClient::deleteRecordOnce(const std::string& recordId) const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    if (recordId.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "recordId must not be empty",
            400,
            false));
    }

    const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) + "/records?recordIds=" + urlEncode(recordId);
    const auto response = executeRequest("DELETE", toWide(path), token_, options_.requestTimeoutMs);
    if (!response) {
        return std::unexpected(response.error());
    }

    const auto parsed = parseResponseJson(response.value());
    if (!parsed) {
        return std::unexpected(parsed.error());
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
