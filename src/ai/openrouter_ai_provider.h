#pragma once

#include <string>

#include "src/ai/ai_provider.h"
#include "src/api/retry_policy.h"

namespace wikilive::ai {

    struct OpenRouterAiProviderOptions {
        int requestTimeoutMs = 10000;
        int retryAttempts = 3;
        int retryBaseDelayMs = 1000;
        int maxTokens = 500;
        double temperature = 0.2;
    };

    class OpenRouterAiProvider : public AiProvider {
    public:
        OpenRouterAiProvider(std::string baseUrl, std::string apiKey, std::string model, OpenRouterAiProviderOptions options = {});

        [[nodiscard]] const AiProviderMetadata& metadata() const override;
        [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const override;

    private:
        [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsertOnce(const AiSuggestInsertRequest& request) const;

        AiProviderMetadata metadata_{};
        std::string apiKey_;
        OpenRouterAiProviderOptions options_{};
        api::RetryPolicy retryPolicy_{};
    };

}  // namespace wikilive::ai
