#include "src/api/mws_client.h"

#include <windows.h>
#include <winhttp.h>

#include <cctype>
#include <string_view>
#include <utility>

#include "src/utils/string_utils.h"

namespace {

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

wikilive::utils::Expected<std::string> executeGetRequest(
    const std::wstring& pathWithQuery,
    const std::string& token,
    const int timeoutMs) {
    using wikilive::utils::ErrorCode;

    WinHttpHandle session(WinHttpOpen(L"WikiLive/1.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_NO_PROXY_NAME,
                                      WINHTTP_NO_PROXY_BYPASS, 0));
    if (!session) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "WinHTTP session initialization failed",
            502,
            true));
    }

    WinHttpSetTimeouts(session.get(), timeoutMs, timeoutMs, timeoutMs, timeoutMs);

    WinHttpHandle connection(WinHttpConnect(session.get(), L"tables.mws.ru", INTERNET_DEFAULT_HTTPS_PORT, 0));
    if (!connection) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "WinHTTP connection to tables.mws.ru failed",
            502,
            true));
    }

    WinHttpHandle request(WinHttpOpenRequest(connection.get(), L"GET", pathWithQuery.c_str(), nullptr, WINHTTP_NO_REFERER,
                                             WINHTTP_DEFAULT_ACCEPT_TYPES, WINHTTP_FLAG_SECURE));
    if (!request) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "WinHTTP request initialization failed",
            502,
            true));
    }

    const auto header = toWide("Authorization: Bearer " + token + "\r\nAccept: application/json\r\n");
    if (!WinHttpSendRequest(request.get(), header.c_str(), static_cast<DWORD>(header.size()),
                            WINHTTP_NO_REQUEST_DATA, 0, 0, 0)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "Sending request to MWS failed",
            502,
            true));
    }

    if (!WinHttpReceiveResponse(request.get(), nullptr)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "Receiving response from MWS failed",
            502,
            true));
    }

    DWORD statusCode = 0;
    DWORD statusCodeSize = sizeof(statusCode);
    if (!WinHttpQueryHeaders(request.get(), WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER, WINHTTP_HEADER_NAME_BY_INDEX,
                             &statusCode, &statusCodeSize, WINHTTP_NO_HEADER_INDEX)) {
        return std::unexpected(wikilive::utils::makeError(
            ErrorCode::MwsApiError,
            "Could not read MWS HTTP status code",
            502,
            true));
    }

    std::string body;
    for (;;) {
        DWORD availableSize = 0;
        if (!WinHttpQueryDataAvailable(request.get(), &availableSize)) {
            return std::unexpected(wikilive::utils::makeError(
                ErrorCode::MwsApiError,
                "Could not query MWS response size",
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
                "Could not read MWS response body",
                502,
                true));
        }

        buffer.resize(bytesRead);
        body += buffer;
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

    return body;
}

std::string extractJsonStringField(std::string_view source, const std::string& fieldName) {
    std::size_t keyPosition = 0;
    if (!fieldName.empty()) {
        const std::string key = "\"" + fieldName + "\"";
        keyPosition = source.find(key);
        if (keyPosition == std::string_view::npos) {
            return {};
        }
    }

    std::size_t openingQuote = std::string_view::npos;
    if (fieldName.empty()) {
        openingQuote = source.find('"');
    } else {
        const auto colonPosition = source.find(':', keyPosition);
        if (colonPosition == std::string_view::npos) {
            return {};
        }
        openingQuote = source.find('"', colonPosition + 1);
    }

    if (openingQuote == std::string_view::npos) {
        return {};
    }

    std::string result;
    bool escape = false;
    for (std::size_t index = openingQuote + 1; index < source.size(); ++index) {
        const char current = source[index];
        if (escape) {
            result.push_back(current);
            escape = false;
            continue;
        }

        if (current == '\\') {
            escape = true;
            continue;
        }

        if (current == '"') {
            return wikilive::utils::unescapeJson(result);
        }

        result.push_back(current);
    }

    return {};
}

std::string extractJsonPrimitiveField(std::string_view source, const std::string& fieldName) {
    const std::string key = "\"" + fieldName + "\"";
    const auto keyPosition = source.find(key);
    if (keyPosition == std::string_view::npos) {
        return {};
    }

    const auto colonPosition = source.find(':', keyPosition + key.size());
    if (colonPosition == std::string_view::npos) {
        return {};
    }

    std::size_t valueStart = colonPosition + 1;
    while (valueStart < source.size() && std::isspace(static_cast<unsigned char>(source[valueStart]))) {
        ++valueStart;
    }

    if (valueStart >= source.size()) {
        return {};
    }

    if (source[valueStart] == '"') {
        return extractJsonStringField(source.substr(valueStart), "");
    }

    std::size_t valueEnd = valueStart;
    while (valueEnd < source.size() && source[valueEnd] != ',' && source[valueEnd] != '}' && source[valueEnd] != ']') {
        ++valueEnd;
    }

    return wikilive::utils::trim(std::string(source.substr(valueStart, valueEnd - valueStart)));
}

std::string findRecordObject(const std::string& json, const std::string& recordId) {
    const std::string recordMarker = "\"recordId\":\"" + wikilive::utils::escapeJson(recordId) + "\"";
    const auto recordPosition = json.find(recordMarker);
    if (recordPosition == std::string::npos) {
        return {};
    }

    const auto objectStart = json.rfind('{', recordPosition);
    if (objectStart == std::string::npos) {
        return {};
    }

    int depth = 0;
    bool inString = false;
    bool escape = false;
    for (std::size_t index = objectStart; index < json.size(); ++index) {
        const char current = json[index];

        if (inString) {
            if (escape) {
                escape = false;
                continue;
            }
            if (current == '\\') {
                escape = true;
                continue;
            }
            if (current == '"') {
                inString = false;
            }
            continue;
        }

        if (current == '"') {
            inString = true;
            continue;
        }

        if (current == '{') {
            ++depth;
        } else if (current == '}') {
            --depth;
            if (depth == 0) {
                return json.substr(objectStart, index - objectStart + 1);
            }
        }
    }

    return {};
}

std::string findFieldsObject(const std::string& recordObject) {
    const auto fieldsPosition = recordObject.find("\"fields\"");
    if (fieldsPosition == std::string::npos) {
        return {};
    }

    const auto openingBrace = recordObject.find('{', fieldsPosition);
    if (openingBrace == std::string::npos) {
        return {};
    }

    int depth = 0;
    bool inString = false;
    bool escape = false;
    for (std::size_t index = openingBrace; index < recordObject.size(); ++index) {
        const char current = recordObject[index];

        if (inString) {
            if (escape) {
                escape = false;
                continue;
            }
            if (current == '\\') {
                escape = true;
                continue;
            }
            if (current == '"') {
                inString = false;
            }
            continue;
        }

        if (current == '"') {
            inString = true;
            continue;
        }

        if (current == '{') {
            ++depth;
        } else if (current == '}') {
            --depth;
            if (depth == 0) {
                return recordObject.substr(openingBrace, index - openingBrace + 1);
            }
        }
    }

    return {};
}

wikilive::utils::Expected<std::string> extractFieldValueFromResponse(
    const std::string& json,
    const std::string& recordId,
    const std::string& fieldName) {
    const auto recordObject = findRecordObject(json, recordId);
    if (recordObject.empty()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::PageNotFound,
            "MWS record was not found: " + recordId,
            404,
            false));
    }

    const auto fieldsObject = findFieldsObject(recordObject);
    if (fieldsObject.empty()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::MwsApiError,
            "MWS response does not contain a fields object for record " + recordId,
            502,
            false));
    }

    const auto stringValue = extractJsonStringField(fieldsObject, fieldName);
    if (!stringValue.empty()) {
        return stringValue;
    }

    const auto primitiveValue = extractJsonPrimitiveField(fieldsObject, fieldName);
    if (!primitiveValue.empty()) {
        return primitiveValue;
    }

    return std::unexpected(wikilive::utils::makeError(
        wikilive::utils::ErrorCode::MwsApiError,
        "Field was not found in MWS record: " + fieldName,
        404,
        false));
}

}  // namespace

namespace wikilive::api {

MwsClient::MwsClient(std::string token, std::string tableId, std::string viewId, MwsClientOptions options)
    : token_(std::move(token)),
      tableId_(std::move(tableId)),
      viewId_(std::move(viewId)),
      options_(options) {
}

void MwsClient::setFallbackRecords(std::vector<MwsRecord> records) {
    fallbackRecords_ = std::move(records);
    if (!fallbackRecords_.empty()) {
        lastGoodRecords_ = fallbackRecords_;
    }
}

utils::Expected<std::vector<MwsRecord>> MwsClient::getRecords() {
    auto result = retryPolicy_.run(
        [this]() {
            return getRecordsOnce();
        },
        options_.retryAttempts,
        options_.retryBaseDelayMs);

    if (result) {
        lastGoodRecords_ = result.value();
        return result;
    }

    if (!lastGoodRecords_.empty()) {
        return lastGoodRecords_;
    }

    if (!fallbackRecords_.empty()) {
        return fallbackRecords_;
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

utils::Expected<MwsFieldValue> MwsClient::getFieldValueOnce(
    const std::string& tableId,
    const std::string& recordId,
    const std::string& fieldName) const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    if (recordId.empty() || fieldName.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "recordId and fieldName must not be empty",
            400,
            false));
    }

    const auto resolvedTableId = tableId.empty() ? tableId_ : tableId;
    const auto path = "/fusion/v1/datasheets/" + urlEncode(resolvedTableId) +
                      "/records?viewId=" + urlEncode(viewId_) +
                      "&fieldKey=name&recordIds=" + urlEncode(recordId);

    const auto response = executeGetRequest(toWide(path), token_, options_.requestTimeoutMs);
    if (!response) {
        return std::unexpected(response.error());
    }

    const auto fieldValue = extractFieldValueFromResponse(response.value(), recordId, fieldName);
    if (!fieldValue) {
        return std::unexpected(fieldValue.error());
    }

    return MwsFieldValue{
        .recordId = recordId,
        .fieldName = fieldName,
        .value = fieldValue.value(),
    };
}

utils::Expected<std::vector<MwsRecord>> MwsClient::getRecordsOnce() const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    const auto path = "/fusion/v1/datasheets/" + urlEncode(tableId_) +
                      "/records?viewId=" + urlEncode(viewId_) +
                      "&fieldKey=name";
    const auto response = executeGetRequest(toWide(path), token_, options_.requestTimeoutMs);
    if (!response) {
        return std::unexpected(response.error());
    }

    return std::vector<MwsRecord>{
        MwsRecord{
            .recordId = "live-response",
            .payload = response.value(),
        },
    };
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

    return std::unexpected(utils::makeError(
        utils::ErrorCode::NotImplemented,
        "Live MWS POST transport is not wired yet.",
        501,
        false));
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

    return std::unexpected(utils::makeError(
        utils::ErrorCode::NotImplemented,
        "Live MWS PATCH transport is not wired yet.",
        501,
        false));
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

    return std::unexpected(utils::makeError(
        utils::ErrorCode::NotImplemented,
        "Live MWS DELETE transport is not wired yet.",
        501,
        false));
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
