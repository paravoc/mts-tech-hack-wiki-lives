#include "src/ai/ai_provider_factory.h"
#include "src/ai/ai_service.h"
#include "src/core/app_config.h"
#include "src/utils/errors.h"
#include "tests/test_common.h"

namespace {

void returnsUnavailableWhenProviderIsMissing() {
    wikilive::ai::AiService service(nullptr);

    wikilive::tests::expect(!service.isAvailable(), "AI service should be unavailable without provider");

    const auto result = service.suggestInsert({
        .userPrompt = "вставь статус проекта",
        .pageContent = "",
        .contextJson = "{}",
    });

    wikilive::tests::expect(!result.has_value(), "AI request should fail when provider is missing");
    wikilive::tests::expectEqual(
        result.error().code,
        wikilive::utils::ErrorCode::InvalidConfig,
        "missing AI provider should be reported as invalid config");
}

void createsOpenRouterProviderFromConfig() {
    wikilive::core::AppConfig config;
    config.enableAi = true;
    config.aiProvider = "openrouter";
    config.aiBaseUrl = "https://openrouter.ai/api/v1";
    config.aiApiKey = "test-key";
    config.aiModel = "meta-llama/llama-3.3-70b-instruct";

    wikilive::ai::AiService service(wikilive::ai::createAiProvider(config));
    wikilive::tests::expect(service.isAvailable(), "AI service should be available with OpenRouter config");

    const auto metadata = service.metadata();
    wikilive::tests::expectEqual(metadata.provider, std::string("openrouter"), "provider should match config");
    wikilive::tests::expectEqual(metadata.model, config.aiModel, "model should match config");

    const auto result = service.generatePage({
        .prompt = "собери страницу статуса",
        .contextJson = "{}",
    });

    wikilive::tests::expect(!result.has_value(), "stubbed provider should report not implemented");
    wikilive::tests::expectEqual(
        result.error().code,
        wikilive::utils::ErrorCode::NotImplemented,
        "stubbed provider should keep extension point explicit");
}

void createsOllamaProviderFromConfig() {
    wikilive::core::AppConfig config;
    config.enableAi = true;
    config.aiProvider = "ollama";
    config.aiBaseUrl = "http://127.0.0.1:11434";
    config.aiModel = "qwen2.5:7b";

    wikilive::ai::AiService service(wikilive::ai::createAiProvider(config));
    wikilive::tests::expect(service.isAvailable(), "AI service should be available with Ollama config");

    const auto metadata = service.metadata();
    wikilive::tests::expectEqual(metadata.provider, std::string("ollama"), "provider should match config");
    wikilive::tests::expectEqual(metadata.baseUrl, config.aiBaseUrl, "baseUrl should match config");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"returns unavailable when provider is missing", returnsUnavailableWhenProviderIsMissing},
        {"creates openrouter provider from config", createsOpenRouterProviderFromConfig},
        {"creates ollama provider from config", createsOllamaProviderFromConfig},
    });
}
