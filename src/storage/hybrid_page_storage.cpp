#include "src/storage/hybrid_page_storage.h"

#include <utility>

#include "src/utils/logger.h"

namespace wikilive::storage {

HybridPageStorage::HybridPageStorage(std::unique_ptr<PageStorage> localStorage, std::unique_ptr<PageStorage> remoteStorage)
    : localStorage_(std::move(localStorage)),
      remoteStorage_(std::move(remoteStorage)) {
}

utils::Expected<std::vector<models::Page>> HybridPageStorage::listPages() const {
    const auto localPages = localStorage_->listPages();
    const auto remotePages = remoteStorage_ ? remoteStorage_->listPages() : utils::Expected<std::vector<models::Page>>{std::vector<models::Page>{}};

    if (localPages && remotePages) {
        return mergePages(localPages.value(), remotePages.value());
    }

    if (localPages) {
        if (!remotePages) {
            utils::Logger::instance().warn("Remote WikiPages storage is unavailable, using local pages");
        }
        return localPages.value();
    }

    if (remotePages) {
        return remotePages.value();
    }

    return wikilive::utils::makeUnexpected(localPages.error());
}

utils::Expected<models::Page> HybridPageStorage::getPage(const std::string& pageId) const {
    const auto localPage = localStorage_->getPage(pageId);
    if (localPage) {
        return localPage.value();
    }

    if (remoteStorage_) {
        const auto remotePage = remoteStorage_->getPage(pageId);
        if (remotePage) {
            return remotePage.value();
        }
        return wikilive::utils::makeUnexpected(remotePage.error());
    }

    return wikilive::utils::makeUnexpected(localPage.error());
}

utils::VoidExpected HybridPageStorage::savePage(const models::Page& page) {
    const auto localResult = localStorage_->savePage(page);
    if (!localResult) {
        return wikilive::utils::makeUnexpected(localResult.error());
    }

    if (remoteStorage_) {
        const auto remoteResult = remoteStorage_->savePage(page);
        if (!remoteResult) {
            utils::Logger::instance().warn("Remote WikiPages save failed, local copy was kept: " + remoteResult.error().message);
        }
    }

    return {};
}

utils::VoidExpected HybridPageStorage::deletePage(const std::string& pageId) {
    const auto localResult = localStorage_->deletePage(pageId);
    if (!localResult && localResult.error().code != utils::ErrorCode::PageNotFound) {
        return wikilive::utils::makeUnexpected(localResult.error());
    }

    if (remoteStorage_) {
        const auto remoteResult = remoteStorage_->deletePage(pageId);
        if (!remoteResult && remoteResult.error().code != utils::ErrorCode::PageNotFound) {
            utils::Logger::instance().warn("Remote WikiPages delete failed, local delete was kept: " + remoteResult.error().message);
        }
    }

    if (!localResult && remoteStorage_) {
        return {};
    }

    return {};
}

std::vector<models::Page> HybridPageStorage::mergePages(
    const std::vector<models::Page>& localPages,
    const std::vector<models::Page>& remotePages) const {
    std::unordered_map<std::string, models::Page> merged;

    for (const auto& page : remotePages) {
        merged.insert_or_assign(page.pageId, page);
    }

    for (const auto& page : localPages) {
        merged.insert_or_assign(page.pageId, page);
    }

    std::vector<models::Page> result;
    result.reserve(merged.size());
    for (auto& [pageId, page] : merged) {
        (void)pageId;
        result.push_back(std::move(page));
    }
    return result;
}

}  // namespace wikilive::storage
