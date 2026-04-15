#include "src/storage/in_memory_page_storage.h"

#include <utility>

namespace wikilive::storage {

utils::Expected<std::vector<models::Page>> InMemoryPageStorage::listPages() const {
    std::scoped_lock lock(mutex_);

    std::vector<models::Page> pages;
    pages.reserve(pages_.size());
    for (const auto& [pageId, page] : pages_) {
        (void)pageId;
        pages.push_back(page);
    }

    return pages;
}

utils::Expected<models::Page> InMemoryPageStorage::getPage(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);

    const auto it = pages_.find(pageId);
    if (it == pages_.end()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return it->second;
}

utils::VoidExpected InMemoryPageStorage::savePage(const models::Page& page) {
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

    std::scoped_lock lock(mutex_);
    pages_[page.pageId] = page;
    return {};
}

utils::VoidExpected InMemoryPageStorage::deletePage(const std::string& pageId) {
    std::scoped_lock lock(mutex_);

    if (pages_.erase(pageId) == 0) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return {};
}

}  // namespace wikilive::storage
