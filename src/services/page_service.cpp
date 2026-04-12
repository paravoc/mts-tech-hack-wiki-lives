#include "src/services/page_service.h"

#include <algorithm>
#include <charconv>
#include <string_view>

#include "src/utils/time_utils.h"

namespace wikilive::services {

PageService::PageService(storage::PageStorage& storage) : storage_(storage) {
    const auto pages = storage_.listPages();
    if (!pages) {
        return;
    }

    std::size_t maxPageNumber = 0;
    for (const auto& page : pages.value()) {
        constexpr std::string_view prefix = "page-";
        if (page.pageId.rfind(prefix, 0) != 0) {
            continue;
        }

        const auto numberView = std::string_view(page.pageId).substr(prefix.size());
        std::size_t parsedNumber = 0;
        const auto result = std::from_chars(
            numberView.data(),
            numberView.data() + numberView.size(),
            parsedNumber);
        if (result.ec == std::errc{} && result.ptr == numberView.data() + numberView.size()) {
            maxPageNumber = std::max(maxPageNumber, parsedNumber);
        }
    }

    pageCounter_ = std::max<std::size_t>(pageCounter_, maxPageNumber + 1);
}

utils::Expected<std::vector<models::Page>> PageService::listPages() const {
    auto pages = storage_.listPages();
    if (!pages) {
        return std::unexpected(pages.error());
    }

    auto value = pages.value();
    std::sort(value.begin(), value.end(), [](const models::Page& left, const models::Page& right) {
        if (left.updatedAt == right.updatedAt) {
            return left.pageId < right.pageId;
        }
        return left.updatedAt > right.updatedAt;
    });

    return value;
}

utils::Expected<models::Page> PageService::getPage(const std::string& pageId) const {
    return storage_.getPage(pageId);
}

utils::Expected<models::Page> PageService::createPage(const PageDraft& draft) {
    const auto validDraft = validateDraft(draft);
    if (!validDraft) {
        return std::unexpected(validDraft.error());
    }

    const auto timestamp = utils::formatIso(utils::now());
    models::Page page{
        .pageId = nextPageId(),
        .title = validDraft->title,
        .description = validDraft->description,
        .content = validDraft->content,
        .createdAt = timestamp,
        .updatedAt = timestamp,
        .ownerId = validDraft->ownerId.empty() ? "viewer" : validDraft->ownerId,
        .ownerName = validDraft->ownerName.empty() ? "Гость" : validDraft->ownerName,
    };

    const auto saveResult = storage_.savePage(page);
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return page;
}

utils::Expected<models::Page> PageService::updatePage(const std::string& pageId, const PageDraft& draft) {
    const auto validDraft = validateDraft(draft);
    if (!validDraft) {
        return std::unexpected(validDraft.error());
    }

    auto existingPage = storage_.getPage(pageId);
    if (!existingPage) {
        return std::unexpected(existingPage.error());
    }

    auto page = existingPage.value();
    page.title = validDraft->title;
    page.description = validDraft->description;
    page.content = validDraft->content;
    page.updatedAt = utils::formatIso(utils::now());
    if (!validDraft->ownerId.empty()) {
        page.ownerId = validDraft->ownerId;
    }
    if (!validDraft->ownerName.empty()) {
        page.ownerName = validDraft->ownerName;
    }

    const auto saveResult = storage_.savePage(page);
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return page;
}

utils::VoidExpected PageService::deletePage(const std::string& pageId) {
    return storage_.deletePage(pageId);
}

utils::Expected<PageDraft> PageService::validateDraft(const PageDraft& draft) const {
    if (draft.title.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "title must not be empty",
            400,
            false));
    }

    return draft;
}

std::string PageService::nextPageId() {
    return "page-" + std::to_string(pageCounter_++);
}

}  // namespace wikilive::services
