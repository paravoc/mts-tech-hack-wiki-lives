#include "src/storage/local_file_page_storage.h"

#include <filesystem>
#include <fstream>
#include <utility>

#include <nlohmann/json.hpp>

namespace wikilive::storage {

namespace {

nlohmann::json pageToJson(const models::Page& page) {
    return {
        {"pageId", page.pageId},
        {"title", page.title},
        {"description", page.description},
        {"content", page.content},
        {"createdAt", page.createdAt},
        {"updatedAt", page.updatedAt},
        {"ownerId", page.ownerId},
        {"ownerName", page.ownerName},
    };
}

models::Page pageFromJson(const nlohmann::json& value) {
    return {
        .pageId = value.value("pageId", std::string{}),
        .title = value.value("title", std::string{}),
        .description = value.value("description", std::string{}),
        .content = value.value("content", std::string{}),
        .createdAt = value.value("createdAt", std::string{}),
        .updatedAt = value.value("updatedAt", std::string{}),
        .ownerId = value.value("ownerId", std::string{}),
        .ownerName = value.value("ownerName", std::string{}),
        .renderedHtml = {},
    };
}

}  // namespace

LocalFilePageStorage::LocalFilePageStorage(std::string storagePath)
    : storagePath_(std::move(storagePath)) {
}

utils::Expected<std::vector<models::Page>> LocalFilePageStorage::listPages() const {
    std::scoped_lock lock(mutex_);
    const auto pages = loadPagesUnlocked();
    if (!pages) {
        return std::unexpected(pages.error());
    }

    std::vector<models::Page> result;
    result.reserve(pages->size());
    for (const auto& [pageId, page] : pages.value()) {
        (void)pageId;
        result.push_back(page);
    }
    return result;
}

utils::Expected<models::Page> LocalFilePageStorage::getPage(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);
    const auto pages = loadPagesUnlocked();
    if (!pages) {
        return std::unexpected(pages.error());
    }

    const auto it = pages->find(pageId);
    if (it == pages->end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return it->second;
}

utils::VoidExpected LocalFilePageStorage::savePage(const models::Page& page) {
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

    std::scoped_lock lock(mutex_);
    auto pages = loadPagesUnlocked();
    if (!pages) {
        return std::unexpected(pages.error());
    }

    pages->insert_or_assign(page.pageId, page);
    return persistPagesUnlocked(pages.value());
}

utils::VoidExpected LocalFilePageStorage::deletePage(const std::string& pageId) {
    std::scoped_lock lock(mutex_);
    auto pages = loadPagesUnlocked();
    if (!pages) {
        return std::unexpected(pages.error());
    }

    if (pages->erase(pageId) == 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return persistPagesUnlocked(pages.value());
}

utils::Expected<LocalFilePageStorage::PageMap> LocalFilePageStorage::loadPagesUnlocked() const {
    if (storagePath_.empty()) {
        return PageMap{};
    }

    if (!std::filesystem::exists(storagePath_)) {
        return PageMap{};
    }

    std::ifstream stream(storagePath_, std::ios::binary);
    if (!stream.is_open()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            "Failed to open page storage: " + storagePath_,
            500,
            true));
    }

    nlohmann::json payload;
    try {
        stream >> payload;
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Failed to parse page storage: ") + exception.what(),
            500,
            true));
    }

    PageMap pages;
    for (const auto& item : payload.value("pages", nlohmann::json::array())) {
        const auto page = pageFromJson(item);
        if (!page.pageId.empty()) {
            pages.insert_or_assign(page.pageId, page);
        }
    }

    return pages;
}

utils::VoidExpected LocalFilePageStorage::persistPagesUnlocked(const PageMap& pages) const {
    if (storagePath_.empty()) {
        return {};
    }

    try {
        const auto path = std::filesystem::path(storagePath_);
        if (path.has_parent_path()) {
            std::filesystem::create_directories(path.parent_path());
        }

        nlohmann::json payload;
        payload["pages"] = nlohmann::json::array();
        for (const auto& [pageId, page] : pages) {
            (void)pageId;
            payload["pages"].push_back(pageToJson(page));
        }

        std::ofstream stream(storagePath_, std::ios::binary | std::ios::trunc);
        if (!stream.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to write page storage: " + storagePath_,
                500,
                true));
        }

        stream << payload.dump(2);
        return {};
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Failed to persist page storage: ") + exception.what(),
            500,
            true));
    }
}

}  // namespace wikilive::storage
