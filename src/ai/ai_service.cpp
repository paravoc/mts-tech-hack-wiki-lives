#include "src/ai/ai_service.h"

namespace wikilive::ai {

AiService::AiService(std::unique_ptr<AiProvider> provider)
    : provider_(std::move(provider)) {
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

utils::Expected<AiAnalysisResult> AiService::analyzeText(const AiAnalyzeRequest& request) const {
    if (provider_ == nullptr) {
        return std::unexpected(unavailableError());
    }

    return provider_->analyzeText(request);
}

utils::Expected<AiSuggestInsertResult> AiService::suggestInsert(const AiSuggestInsertRequest& request) const {
    if (provider_ == nullptr) {
        return std::unexpected(unavailableError());
    }

    return provider_->suggestInsert(request);
}

utils::Expected<AiGeneratedPage> AiService::generatePage(const AiGeneratePageRequest& request) const {
    if (provider_ == nullptr) {
        return std::unexpected(unavailableError());
    }

    return provider_->generatePage(request);
}

utils::Error AiService::unavailableError() const {
    return utils::makeError(
        utils::ErrorCode::InvalidConfig,
        "AI provider is not configured. Set ENABLE_AI=true and configure AI_PROVIDER in .env.",
        503,
        false);
}

}  // namespace wikilive::ai
