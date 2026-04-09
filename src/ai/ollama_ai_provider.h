#pragma once

#include <string>

#include "src/ai/ai_provider.h"
#include "src/api/retry_policy.h"

namespace wikilive::ai {

struct OllamaAiProviderOptions {
    int requestTimeoutMs = 30000;
    int retryAttempts = 2;
    int retryBaseDelayMs = 1000;
    int maxTokens = 500;
    double temperature = 0.2;
};

class OllamaAiProvider : public AiProvider {
public:
    OllamaAiProvider(std::string baseUrl, std::string model, OllamaAiProviderOptions options = {});

    [[nodiscard]] const AiProviderMetadata& metadata() const override;
    [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const override;

private:
    [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsertOnce(const AiSuggestInsertRequest& request) const;

    AiProviderMetadata metadata_{};
    OllamaAiProviderOptions options_{};
    api::RetryPolicy retryPolicy_{};
};

}  // namespace wikilive::ai
