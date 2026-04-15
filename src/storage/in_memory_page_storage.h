#pragma once

#include <mutex>
#include <unordered_map>

#include "src/storage/page_storage.h"

namespace wikilive::storage {

class InMemoryPageStorage final : public PageStorage {
public:
    [[nodiscard]] utils::Expected<std::vector<models::Page>> listPages() const override;
    [[nodiscard]] utils::Expected<models::Page> getPage(const std::string& pageId) const override;
    [[nodiscard]] utils::VoidExpected savePage(const models::Page& page) override;
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId) override;

private:
    mutable std::mutex mutex_{};
    std::unordered_map<std::string, models::Page> pages_{};
};

}  // namespace wikilive::storage
