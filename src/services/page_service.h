#pragma once

#include <cstddef>
#include <string>
#include <vector>

#include "src/models/page.h"
#include "src/storage/page_storage.h"
#include "src/utils/errors.h"

namespace wikilive::services {

struct PageDraft {
    std::string title;
    std::string description;
    std::string content;
    std::string ownerId;
    std::string ownerName;
};

class PageService {
public:
    explicit PageService(storage::PageStorage& storage);

    [[nodiscard]] utils::Expected<std::vector<models::Page>> listPages() const;
    [[nodiscard]] utils::Expected<models::Page> getPage(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::Page> createPage(const PageDraft& draft);
    [[nodiscard]] utils::Expected<models::Page> updatePage(const std::string& pageId, const PageDraft& draft);
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId);

private:
    [[nodiscard]] utils::Expected<PageDraft> validateDraft(const PageDraft& draft) const;
    [[nodiscard]] std::string nextPageId();

    storage::PageStorage& storage_;
    std::size_t pageCounter_ = 1;
};

}  // namespace wikilive::services
