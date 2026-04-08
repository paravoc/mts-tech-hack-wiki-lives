#include "src/ai/ai_provider_factory.h"

#include "src/ai/ollama_ai_provider.h"
#include "src/ai/openrouter_ai_provider.h"
#include "src/core/app_config.h"
#include "src/utils/logger.h"

namespace wikilive::ai {

std::unique_ptr<AiProvider> createAiProvider(const core::AppConfig& config) {
    if (!config.enableAi) {
        return nullptr;
    }

    if (config.aiProvider == "openrouter") {
        return std::make_unique<OpenRouterAiProvider>(
            config.aiBaseUrl,
            config.aiApiKey,
            config.aiModel);
    }

    if (config.aiProvider == "ollama") {
        return std::make_unique<OllamaAiProvider>(
            config.aiBaseUrl,
            config.aiModel);
    }

    utils::Logger::instance().warn(
        "Unknown AI provider '" + config.aiProvider + "', AI module will stay disabled");
    return nullptr;
}

}  // namespace wikilive::ai
