#include "src/ai/ai_context_builder.h"

#include <algorithm>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>

#include "src/api/mws_client.h"

namespace wikilive::ai {

MwsAiContextBuilder::MwsAiContextBuilder(
    api::MwsClient& mwsClient,
    std::string tableId,
    const std::size_t maxRecords,
    const std::size_t maxFields)
    : mwsClient_(mwsClient),
      tableId_(std::move(tableId)),
      maxRecords_(maxRecords),
      maxFields_(maxFields) {
}

utils::Expected<std::string> MwsAiContextBuilder::buildSuggestInsertContext() const {
    const auto records = mwsClient_.getRecords();
    if (!records) {
        return std::unexpected(records.error());
    }

    nlohmann::json tableJson = {
        {"tableId", tableId_},
        {"fields", nlohmann::json::array()},
        {"records", nlohmann::json::array()},
    };

    std::vector<std::string> fieldNames;
    fieldNames.reserve(maxFields_);

    const auto recordCount = std::min(records->size(), maxRecords_);
    for (std::size_t index = 0; index < recordCount; ++index) {
        const auto& record = (*records)[index];
        nlohmann::json recordJson = {
            {"recordId", record.recordId},
            {"fields", nlohmann::json::object()},
        };

        for (const auto& [fieldName, value] : record.fields) {
            recordJson["fields"][fieldName] = value;

            if (fieldNames.size() >= maxFields_) {
                continue;
            }

            if (std::find(fieldNames.begin(), fieldNames.end(), fieldName) == fieldNames.end()) {
                fieldNames.push_back(fieldName);
            }
        }

        tableJson["records"].push_back(std::move(recordJson));
    }

    for (const auto& fieldName : fieldNames) {
        tableJson["fields"].push_back(fieldName);
    }

    nlohmann::json context = {
        {"tables", nlohmann::json::array({std::move(tableJson)})},
    };
    return context.dump();
}

}  // namespace wikilive::ai
