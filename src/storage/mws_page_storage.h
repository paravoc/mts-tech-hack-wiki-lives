#pragma once

#include "src/api/mws_client.h"
#include "src/storage/page_storage.h"

namespace wikilive::storage {

class MwsPageStorage final : public PageStorage {
public:
    explicit MwsPageStorage(api::MwsClient& client);

    [[nodiscard]] utils::Expected<std::vector<models::Page>> listPages() const override;
    [[nodiscard]] utils::Expected<models::Page> getPage(const std::string& pageId) const override;
    [[nodiscard]] utils::VoidExpected savePage(const models::Page& page) override;
    [[nodiscard]] utils::VoidExpected deletePage(const std::string& pageId) override;

private:
    [[nodiscard]] utils::Expected<api::MwsRecord> findRecordByPageId(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::Page> toPage(const api::MwsRecord& record) const;
    [[nodiscard]] std::string buildCreatePayload(const models::Page& page) const;
    [[nodiscard]] std::string buildUpdatePayload(const std::string& recordId, const models::Page& page) const;

    api::MwsClient& client_;
};

}  // namespace wikilive::storage
