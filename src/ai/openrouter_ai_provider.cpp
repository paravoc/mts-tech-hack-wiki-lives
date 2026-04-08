#include "src/ai/openrouter_ai_provider.h"

namespace wikilive::ai {

OpenRouterAiProvider::OpenRouterAiProvider(std::string baseUrl, std::string apiKey, std::string model)
    : apiKey_(std::move(apiKey)) {
    metadata_.provider = "openrouter";
    metadata_.model = std::move(model);
    metadata_.baseUrl = baseUrl.empty() ? "https://openrouter.ai/api/v1" : std::move(baseUrl);
    metadata_.enabled = true;
}

const AiProviderMetadata& OpenRouterAiProvider::metadata() const {
    return metadata_;
}

utils::Expected<AiSuggestInsertResult> OpenRouterAiProvider::suggestInsert(const AiSuggestInsertRequest& /*request*/) const {
    return std::unexpected(notImplementedError("suggestInsert"));
}

utils::Error OpenRouterAiProvider::notImplementedError(const std::string& operation) const {
    return utils::makeError(
        utils::ErrorCode::NotImplemented,
        "AI provider openrouter is configured, but " + operation + " is not implemented yet.",
        501,
        false);
}

}  // namespace wikilive::ai
