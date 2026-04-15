#include "src/ai/ai_service.h"

namespace wikilive::ai {

AiService::AiService(
    std::unique_ptr<AiProvider> provider,
    std::unique_ptr<AiSuggestionValidator> suggestionValidator,
    std::unique_ptr<AiContextBuilder> contextBuilder)
    : provider_(std::move(provider)),
      suggestionValidator_(std::move(suggestionValidator)),
      contextBuilder_(std::move(contextBuilder)) {
    if (suggestionValidator_ == nullptr) {
        suggestionValidator_ = std::make_unique<AiSuggestionValidator>();
    }
}

bool AiService::isAvailable() const {
    return provider_ != nullptr;
}

AiProviderMetadata AiService::metadata() const {
    if (provider_ == nullptr) {
        return AiProviderMetadata{};
    }

    return provider_->metadata();
}

utils::Expected<AiSuggestInsertResult> AiService::suggestInsert(const AiSuggestInsertRequest& request) const {
    if (provider_ == nullptr) {
        return wikilive::utils::makeUnexpected(unavailableError());
    }

    AiSuggestInsertRequest preparedRequest = request;
    if (preparedRequest.contextJson.empty() && contextBuilder_ != nullptr) {
        const auto builtContext = contextBuilder_->buildSuggestInsertContext();
        if (!builtContext) {
            return wikilive::utils::makeUnexpected(builtContext.error());
        }
        preparedRequest.contextJson = builtContext.value();
    }

    const auto providerResult = provider_->suggestInsert(preparedRequest);
    if (!providerResult) {
        return wikilive::utils::makeUnexpected(providerResult.error());
    }

    if (suggestionValidator_ == nullptr) {
        return providerResult;
    }

    return suggestionValidator_->validate(providerResult.value());
}

utils::Error AiService::unavailableError() const {
    return utils::makeError(
        utils::ErrorCode::InvalidConfig,
        "AI provider is not configured. Set ENABLE_AI=true and configure AI_PROVIDER in .env.",
        503,
        false);
}

}  // namespace wikilive::ai
