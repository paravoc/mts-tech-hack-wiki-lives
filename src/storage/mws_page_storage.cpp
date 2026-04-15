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
        return wikilive::utils::makeUnexpected(records.error());
    }

    std::vector<models::Page> pages;
    pages.reserve(records->size());
    for (const auto& record : records.value()) {
        const auto page = toPage(record);
        if (!page) {
            return wikilive::utils::makeUnexpected(page.error());
        }
        pages.push_back(page.value());
    }

    return pages;
}

utils::Expected<models::Page> MwsPageStorage::getPage(const std::string& pageId) const {
    const auto record = findRecordByPageId(pageId);
    if (!record) {
        return wikilive::utils::makeUnexpected(record.error());
    }

    return toPage(record.value());
}

utils::VoidExpected MwsPageStorage::savePage(const models::Page& page) {
    if (page.pageId.empty()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "pageId must not be empty",
            400,
            false));
    }

    if (page.title.empty()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "title must not be empty",
            400,
            false));
    }

    const auto existingRecord = findRecordByPageId(page.pageId);
    if (existingRecord) {
        const auto updateResult = client_.updateRecord(existingRecord->recordId, buildUpdatePayload(existingRecord->recordId, page));
        if (!updateResult) {
            return wikilive::utils::makeUnexpected(updateResult.error());
        }
        return {};
    }

    if (existingRecord.error().code != utils::ErrorCode::PageNotFound) {
        return wikilive::utils::makeUnexpected(existingRecord.error());
    }

    const auto createResult = client_.createRecord(buildCreatePayload(page));
    if (!createResult) {
        return wikilive::utils::makeUnexpected(createResult.error());
    }

    return {};
}

utils::VoidExpected MwsPageStorage::deletePage(const std::string& pageId) {
    const auto record = findRecordByPageId(pageId);
    if (!record) {
        return wikilive::utils::makeUnexpected(record.error());
    }

    return client_.deleteRecord(record->recordId);
}

utils::Expected<api::MwsRecord> MwsPageStorage::findRecordByPageId(const std::string& pageId) const {
    if (pageId.empty()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "pageId must not be empty",
            400,
            false));
    }

    const auto records = client_.getRecords();
    if (!records) {
        return wikilive::utils::makeUnexpected(records.error());
    }

    for (const auto& record : records.value()) {
        const auto fieldIt = record.fields.find("pageId");
        if (fieldIt != record.fields.end() && fieldIt->second == pageId) {
            return record;
        }
    }

    return wikilive::utils::makeUnexpected(utils::makeError(
        utils::ErrorCode::PageNotFound,
        "Page not found: " + pageId,
        404,
        false));
}

utils::Expected<models::Page> MwsPageStorage::toPage(const api::MwsRecord& record) const {
    const auto pageId = getFieldOrEmpty(record, "pageId");
    const auto title = getFieldOrEmpty(record, "title");
    if (pageId.empty() || title.empty()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::MwsApiError,
            "WikiPages record is missing required fields pageId or title",
            502,
            false));
    }

    const auto createdAt = getFieldOrEmpty(record, "createdAt");
    const auto updatedAt = getFieldOrEmpty(record, "updatedAt");

    return models::Page{
        .pageId = pageId,
        .projectId = getFieldOrEmpty(record, "projectId"),
        .title = title,
        .description = getFieldOrEmpty(record, "description"),
        .content = getFieldOrEmpty(record, "content"),
        .createdAt = createdAt,
        .updatedAt = updatedAt.empty() ? createdAt : updatedAt,
        .ownerId = getFieldOrEmpty(record, "ownerId"),
        .ownerName = getFieldOrEmpty(record, "ownerName"),
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
                       {"description", page.description},
                       {"content", page.content},
                       {"createdAt", page.createdAt},
                       {"updatedAt", page.updatedAt},
                       {"projectId", page.projectId},
                      {"ownerId", page.ownerId},
                      {"ownerName", page.ownerName},
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
                       {"description", page.description},
                       {"content", page.content},
                       {"createdAt", page.createdAt},
                       {"updatedAt", page.updatedAt},
                       {"projectId", page.projectId},
                      {"ownerId", page.ownerId},
                      {"ownerName", page.ownerName},
                  }},
             },
         })},
        {"fieldKey", "name"},
    };

    return payload.dump();
}

}  // namespace wikilive::storage
