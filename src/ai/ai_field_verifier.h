#pragma once

#include <string>

#include "src/utils/errors.h"

namespace wikilive::api {
class MwsClient;
}

namespace wikilive::ai {

class AiFieldVerifier {
public:
    virtual ~AiFieldVerifier() = default;

    [[nodiscard]] virtual utils::Expected<bool> exists(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) const = 0;
};

class MwsAiFieldVerifier final : public AiFieldVerifier {
public:
    explicit MwsAiFieldVerifier(api::MwsClient& mwsClient);

    [[nodiscard]] utils::Expected<bool> exists(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) const override;

private:
    api::MwsClient& mwsClient_;
};

}  // namespace wikilive::ai
