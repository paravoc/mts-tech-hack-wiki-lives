#pragma once

#include <memory>

#include "src/ai/ai_context_builder.h"
#include "src/ai/ai_provider.h"
#include "src/ai/ai_suggestion_validator.h"

namespace wikilive::ai {

class AiService {
public:
    explicit AiService(
        std::unique_ptr<AiProvider> provider,
        std::unique_ptr<AiSuggestionValidator> suggestionValidator = std::make_unique<AiSuggestionValidator>(),
        std::unique_ptr<AiContextBuilder> contextBuilder = nullptr);

    [[nodiscard]] bool isAvailable() const;
    [[nodiscard]] AiProviderMetadata metadata() const;
    [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const;

private:
    [[nodiscard]] utils::Error unavailableError() const;

    std::unique_ptr<AiProvider> provider_;
    std::unique_ptr<AiSuggestionValidator> suggestionValidator_;
    std::unique_ptr<AiContextBuilder> contextBuilder_;
};

}  // namespace wikilive::ai
