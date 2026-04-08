#include "src/ai/ollama_ai_provider.h"

namespace wikilive::ai {

OllamaAiProvider::OllamaAiProvider(std::string baseUrl, std::string model) {
    metadata_.provider = "ollama";
    metadata_.model = std::move(model);
    metadata_.baseUrl = baseUrl.empty() ? "http://127.0.0.1:11434" : std::move(baseUrl);
    metadata_.enabled = true;
}

const AiProviderMetadata& OllamaAiProvider::metadata() const {
    return metadata_;
}

utils::Expected<AiAnalysisResult> OllamaAiProvider::analyzeText(const AiAnalyzeRequest& /*request*/) const {
    return std::unexpected(notImplementedError("analyzeText"));
}

utils::Expected<AiSuggestInsertResult> OllamaAiProvider::suggestInsert(const AiSuggestInsertRequest& /*request*/) const {
    return std::unexpected(notImplementedError("suggestInsert"));
}

utils::Expected<AiGeneratedPage> OllamaAiProvider::generatePage(const AiGeneratePageRequest& /*request*/) const {
    return std::unexpected(notImplementedError("generatePage"));
}

utils::Error OllamaAiProvider::notImplementedError(const std::string& operation) const {
    return utils::makeError(
        utils::ErrorCode::NotImplemented,
        "AI provider ollama is configured, but " + operation + " is not implemented yet.",
        501,
        false);
}

}  // namespace wikilive::ai
