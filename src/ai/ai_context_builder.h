#pragma once

#include <cstddef>
#include <string>

#include "src/utils/errors.h"

namespace wikilive::api {
class MwsClient;
}

namespace wikilive::ai {

class AiContextBuilder {
public:
    virtual ~AiContextBuilder() = default;

    [[nodiscard]] virtual utils::Expected<std::string> buildSuggestInsertContext() const = 0;
};

class MwsAiContextBuilder final : public AiContextBuilder {
public:
    MwsAiContextBuilder(
        api::MwsClient& mwsClient,
        std::string tableId,
        std::size_t maxRecords = 10,
        std::size_t maxFields = 20);

    [[nodiscard]] utils::Expected<std::string> buildSuggestInsertContext() const override;

private:
    api::MwsClient& mwsClient_;
    std::string tableId_;
    std::size_t maxRecords_ = 10;
    std::size_t maxFields_ = 20;
};

}  // namespace wikilive::ai
