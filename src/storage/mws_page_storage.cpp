#include "src/storage/mws_page_storage.h"

#include <nlohmann/json.hpp>

namespace {

using json = nlohmann::json;

std::string getFieldOrEmpty(const wikilive::api::MwsRecord& record, const std::string& fieldName) {
    const auto it = record.fields.find(fieldName);
    return it == record.fields.end() ? std::string{} : it->second;
}

}  // namespace

namespace wikilive::storage {

MwsPageStorage::MwsPageStorage(api::MwsClient& client)
    : client_(client) {
}

utils::Expected<std::vector<models::Page>> MwsPageStorage::listPages() const {
    const auto records = client_.getRecords();
    if (!records) {
        return std::unexpected(records.error());
    }

    std::vector<models::Page> pages;
    pages.reserve(records->size());
    for (const auto& record : records.value()) {
        const auto page = toPage(record);
        if (!page) {
            return std::unexpected(page.error());
        }
        pages.push_back(page.value());
    }

    return pages;
}

utils::Expected<models::Page> MwsPageStorage::getPage(const std::string& pageId) const {
    const auto record = findRecordByPageId(pageId);
    if (!record) {
        return std::unexpected(record.error());
    }

    return toPage(record.value());
}

utils::VoidExpected MwsPageStorage::savePage(const models::Page& page) {
    if (page.pageId.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "pageId must not be empty",
            400,
            false));
    }

    if (page.title.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "title must not be empty",
            400,
            false));
    }

    const auto existingRecord = findRecordByPageId(page.pageId);
    if (existingRecord) {
        const auto updateResult = client_.updateRecord(existingRecord->recordId, buildUpdatePayload(existingRecord->recordId, page));
        if (!updateResult) {
            return std::unexpected(updateResult.error());
        }
        return {};
    }

    if (existingRecord.error().code != utils::ErrorCode::PageNotFound) {
        return std::unexpected(existingRecord.error());
    }

    const auto createResult = client_.createRecord(buildCreatePayload(page));
    if (!createResult) {
        return std::unexpected(createResult.error());
    }

    return {};
}

utils::VoidExpected MwsPageStorage::deletePage(const std::string& pageId) {
    const auto record = findRecordByPageId(pageId);
    if (!record) {
        return std::unexpected(record.error());
    }

    return client_.deleteRecord(record->recordId);
}

utils::Expected<api::MwsRecord> MwsPageStorage::findRecordByPageId(const std::string& pageId) const {
    if (pageId.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "pageId must not be empty",
            400,
            false));
    }

    const auto records = client_.getRecords();
    if (!records) {
        return std::unexpected(records.error());
    }

    for (const auto& record : records.value()) {
        const auto fieldIt = record.fields.find("pageId");
        if (fieldIt != record.fields.end() && fieldIt->second == pageId) {
            return record;
        }
    }

    return std::unexpected(utils::makeError(
        utils::ErrorCode::PageNotFound,
        "Page not found: " + pageId,
        404,
        false));
}

utils::Expected<models::Page> MwsPageStorage::toPage(const api::MwsRecord& record) const {
    const auto pageId = getFieldOrEmpty(record, "pageId");
    const auto title = getFieldOrEmpty(record, "title");
    if (pageId.empty() || title.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::MwsApiError,
            "WikiPages record is missing required fields pageId or title",
            502,
            false));
    }

    const auto createdAt = getFieldOrEmpty(record, "createdAt");
    const auto updatedAt = getFieldOrEmpty(record, "updatedAt");

    return models::Page{
        .pageId = pageId,
        .title = title,
        .content = getFieldOrEmpty(record, "content"),
        .createdAt = createdAt,
        .updatedAt = updatedAt.empty() ? createdAt : updatedAt,
    };
}

std::string MwsPageStorage::buildCreatePayload(const models::Page& page) const {
    json payload = {
        {"records",
         json::array({
             {
                 {"fields",
                  {
                      {"pageId", page.pageId},
                      {"title", page.title},
                      {"content", page.content},
                      {"createdAt", page.createdAt},
                      {"updatedAt", page.updatedAt},
                  }},
             },
         })},
        {"fieldKey", "name"},
    };

    return payload.dump();
}

std::string MwsPageStorage::buildUpdatePayload(const std::string& recordId, const models::Page& page) const {
    json payload = {
        {"records",
         json::array({
             {
                 {"recordId", recordId},
                 {"fields",
                  {
                      {"pageId", page.pageId},
                      {"title", page.title},
                      {"content", page.content},
                      {"createdAt", page.createdAt},
                      {"updatedAt", page.updatedAt},
                  }},
             },
         })},
        {"fieldKey", "name"},
    };

    return payload.dump();
}

}  // namespace wikilive::storage
