#include "src/storage/page_storage.h"

namespace wikilive::storage {

utils::Expected<std::vector<Page>> PageStorage::listPages() const {
    std::vector<Page> pages;
    pages.reserve(pages_.size());

    for (const auto& [pageId, page] : pages_) {
        (void)pageId;
        pages.push_back(page);
    }

    return pages;
}

utils::Expected<Page> PageStorage::getPage(const std::string& pageId) const {
    const auto it = pages_.find(pageId);
    if (it == pages_.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return it->second;
}

utils::VoidExpected PageStorage::savePage(const Page& page) {
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

    pages_[page.pageId] = page;
    return {};
}

utils::VoidExpected PageStorage::deletePage(const std::string& pageId) {
    if (pages_.erase(pageId) == 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Page not found: " + pageId,
            404,
            false));
    }

    return {};
}

}  // namespace wikilive::storage
