#pragma once

#include <string>
#include <vector>

#include "src/models/page.h"
#include "src/utils/errors.h"

namespace wikilive::storage {

class PageStorage {
public:
    virtual ~PageStorage() = default;

    [[nodiscard]] virtual utils::Expected<std::vector<models::Page>> listPages() const = 0;
    [[nodiscard]] virtual utils::Expected<models::Page> getPage(const std::string& pageId) const = 0;
    [[nodiscard]] virtual utils::VoidExpected savePage(const models::Page& page) = 0;
    [[nodiscard]] virtual utils::VoidExpected deletePage(const std::string& pageId) = 0;
};

}  // namespace wikilive::storage
