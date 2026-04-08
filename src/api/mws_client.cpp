#include "src/api/mws_client.h"

#include <utility>

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

utils::Expected<std::vector<MwsRecord>> MwsClient::getRecordsOnce() const {
    if (!hasConfiguration()) {
        return std::unexpected(missingConfigurationError());
    }

    return std::unexpected(utils::makeError(
        utils::ErrorCode::NotImplemented,
        "Live MWS GET transport is not wired yet. Add libcurl request code in MwsClient::getRecordsOnce.",
        501,
        false));
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
        "Live MWS POST transport is not wired yet. Add libcurl request code in MwsClient::createRecordOnce.",
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
        "Live MWS PATCH transport is not wired yet. Add libcurl request code in MwsClient::updateRecordOnce.",
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
        "Live MWS DELETE transport is not wired yet. Add libcurl request code in MwsClient::deleteRecordOnce.",
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
