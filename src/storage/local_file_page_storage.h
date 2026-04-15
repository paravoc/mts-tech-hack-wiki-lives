#pragma once

#include <mutex>
#include <string>
#include <unordered_map>

#include "src/storage/page_storage.h"

namespace wikilive::storage {

class LocalFilePageStorage final : public PageStorage {
public:
    explicit LocalFilePageStorage(std::string storagePath);

    [[nodiscard]] utils::Expected<std::vector<models::Page>> listPages() const override;
    [[nodiscard]] utils::Expected<models::Page> getPage(const std::string& pageId) const override;
    [[nodiscard]] utils::VoidExpected savePage(const models::Page& page) override;
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId) override;

private:
    using PageMap = std::unordered_map<std::string, models::Page>;

    [[nodiscard]] utils::Expected<PageMap> loadPagesUnlocked() const;
    [[nodiscard]] utils::VoidExpected persistPagesUnlocked(const PageMap& pages) const;

    std::string storagePath_;
    mutable std::mutex mutex_{};
};

}  // namespace wikilive::storage
