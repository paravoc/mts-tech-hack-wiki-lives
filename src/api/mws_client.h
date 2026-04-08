#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include "src/api/retry_policy.h"
#include "src/utils/errors.h"

namespace wikilive::api {

struct MwsRecord {
    std::string recordId;
    std::unordered_map<std::string, std::string> fields;
    std::string payload;
};

struct MwsFieldValue {
    std::string recordId;
    std::string fieldName;
    std::string value;
};

struct MwsClientOptions {
    int requestTimeoutMs = 10000;
    int retryAttempts = 3;
    int retryBaseDelayMs = 1000;
};

class MwsClient {
public:
    MwsClient(std::string token, std::string tableId, std::string viewId, MwsClientOptions options = {});

    void setFallbackRecords(std::vector<MwsRecord> records);

    [[nodiscard]] utils::Expected<std::vector<MwsRecord>> getRecords(const std::vector<std::string>& recordIds = {});
    [[nodiscard]] utils::Expected<MwsRecord> getRecordById(const std::string& recordId);
    [[nodiscard]] utils::Expected<MwsFieldValue> getFieldValue(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName);
    [[nodiscard]] utils::Expected<std::string> createRecord(const std::string& payload);
    [[nodiscard]] utils::Expected<std::string> updateRecord(const std::string& recordId, const std::string& payload);
    [[nodiscard]] utils::VoidExpected deleteRecord(const std::string& recordId);

private:
    [[nodiscard]] utils::Expected<std::vector<MwsRecord>> getRecordsOnce(const std::vector<std::string>& recordIds) const;
    [[nodiscard]] utils::Expected<MwsFieldValue> getFieldValueOnce(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) const;
    [[nodiscard]] utils::Expected<std::string> createRecordOnce(const std::string& payload) const;
    [[nodiscard]] utils::Expected<std::string> updateRecordOnce(const std::string& recordId, const std::string& payload) const;
    [[nodiscard]] utils::VoidExpected deleteRecordOnce(const std::string& recordId) const;
    [[nodiscard]] bool hasConfiguration() const;
    [[nodiscard]] utils::Error missingConfigurationError() const;

    std::string token_;
    std::string tableId_;
    std::string viewId_;
    MwsClientOptions options_{};
    RetryPolicy retryPolicy_{};
    std::vector<MwsRecord> fallbackRecords_;
    std::vector<MwsRecord> lastGoodRecords_;
};

}  // namespace wikilive::api
