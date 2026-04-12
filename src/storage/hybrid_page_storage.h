#pragma once

#include <memory>
#include <unordered_map>

#include "src/storage/page_storage.h"

namespace wikilive::storage {

class HybridPageStorage final : public PageStorage {
public:
    HybridPageStorage(std::unique_ptr<PageStorage> localStorage, std::unique_ptr<PageStorage> remoteStorage);

    [[nodiscard]] utils::Expected<std::vector<models::Page>> listPages() const override;
    [[nodiscard]] utils::Expected<models::Page> getPage(const std::string& pageId) const override;
    [[nodiscard]] utils::VoidExpected savePage(const models::Page& page) override;
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId) override;

private:
    [[nodiscard]] std::vector<models::Page> mergePages(
        const std::vector<models::Page>& localPages,
        const std::vector<models::Page>& remotePages) const;

    std::unique_ptr<PageStorage> localStorage_;
    std::unique_ptr<PageStorage> remoteStorage_;
};

}  // namespace wikilive::storage
