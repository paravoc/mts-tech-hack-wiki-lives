#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include "src/utils/errors.h"

namespace wikilive::storage {

struct Page {
    std::string pageId;
    std::string title;
    std::string content;
};

class PageStorage {
public:
    [[nodiscard]] utils::Expected<std::vector<Page>> listPages() const;
    [[nodiscard]] utils::Expected<Page> getPage(const std::string& pageId) const;
    [[nodiscard]] utils::VoidExpected savePage(const Page& page);
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId);

private:
    std::unordered_map<std::string, Page> pages_;
};

}  // namespace wikilive::storage
