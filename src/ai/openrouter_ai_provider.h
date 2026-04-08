#pragma once

#include <string>

#include "src/ai/ai_provider.h"

namespace wikilive::ai {

class OpenRouterAiProvider : public AiProvider {
public:
    OpenRouterAiProvider(std::string baseUrl, std::string apiKey, std::string model);

    [[nodiscard]] const AiProviderMetadata& metadata() const override;
    [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const override;

private:
    [[nodiscard]] utils::Error notImplementedError(const std::string& operation) const;

    AiProviderMetadata metadata_{};
    std::string apiKey_;
};

}  // namespace wikilive::ai
