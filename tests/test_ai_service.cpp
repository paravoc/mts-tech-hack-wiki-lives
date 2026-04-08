#include "src/ai/ai_field_verifier.h"
#include "src/ai/ai_context_builder.h"
#include "src/ai/ai_provider.h"
#include "src/ai/ai_provider_factory.h"
#include "src/ai/ai_service.h"
#include "src/ai/ai_suggestion_validator.h"
#include "src/core/app_config.h"
#include "src/utils/errors.h"
#include "tests/test_common.h"

#include <utility>
#include <vector>

namespace {

class FakeAiProvider final : public wikilive::ai::AiProvider {
public:
    const wikilive::ai::AiProviderMetadata& metadata() const override {
        return metadata_;
    }

    wikilive::utils::Expected<wikilive::ai::AiSuggestInsertResult> suggestInsert(
        const wikilive::ai::AiSuggestInsertRequest& request) const override {
        lastRequest = request;
        return nextResult;
    }

    mutable wikilive::ai::AiSuggestInsertRequest lastRequest;
    wikilive::ai::AiSuggestInsertResult nextResult;

private:
    wikilive::ai::AiProviderMetadata metadata_{
        .provider = "fake",
        .model = "fake-model",
        .baseUrl = "http://fake",
        .enabled = true,
    };
};

class FakeAiFieldVerifier final : public wikilive::ai::AiFieldVerifier {
public:
    wikilive::utils::Expected<bool> exists(
        const std::string& tableId,
        const std::string& recordId,
        const std::string& fieldName) const override {
        seenQueries.push_back(tableId + ":" + recordId + ":" + fieldName);

        const auto key = tableId + ":" + recordId + ":" + fieldName;
        if (errorKey == key) {
            return std::unexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::MwsRateLimit,
                "temporary verification failure",
                429,
                true));
        }

        for (const auto& denied : deniedKeys) {
            if (denied == key) {
                return false;
            }
        }

        return true;
    }

    mutable std::vector<std::string> seenQueries;
    std::vector<std::string> deniedKeys;
    std::string errorKey;
};

class FakeAiContextBuilder final : public wikilive::ai::AiContextBuilder {
public:
    wikilive::utils::Expected<std::string> buildSuggestInsertContext() const override {
        ++buildCalls;
        return nextContext;
    }

    mutable int buildCalls = 0;
    std::string nextContext = R"({"tables":[{"tableId":"dst-demo"}]})";
};

void returnsUnavailableWhenProviderIsMissing() {
    wikilive::ai::AiService service(nullptr);

    wikilive::tests::expect(!service.isAvailable(), "AI service should be unavailable without provider");

    const auto result = service.suggestInsert({
        .userPrompt = "insert project status",
        .pageContent = "",
        .contextJson = "{}",
    });

    wikilive::tests::expect(!result.has_value(), "AI request should fail when provider is missing");
    wikilive::tests::expectEqual(
        result.error().code,
        wikilive::utils::ErrorCode::InvalidConfig,
        "missing AI provider should be reported as invalid config");
}

void normalizesAndDeduplicatesCandidates() {
    auto provider = std::make_unique<FakeAiProvider>();
    provider->nextResult.candidates = {
        {
            .tableId = "  dst-demo  ",
            .recordId = " rec-demo ",
            .fieldName = " Status ",
            .insert = "bad-insert",
            .reason = "",
            .confidence = 1.4,
        },
        {
            .tableId = "dst-demo",
            .recordId = "rec-demo",
            .fieldName = "Status",
            .insert = "{{dst-demo:rec-demo:Status}}",
            .reason = "duplicate candidate",
            .confidence = 0.2,
        },
        {
            .tableId = "dst-demo",
            .recordId = "rec-owner",
            .fieldName = "Owner",
            .insert = "",
            .reason = "Owner field is relevant",
            .confidence = 0.7,
        },
        {
            .tableId = "dst-demo",
            .recordId = "",
            .fieldName = "Broken",
            .insert = "",
            .reason = "Should be dropped",
            .confidence = 0.5,
        },
    };

    wikilive::ai::AiService service(std::move(provider));
    const auto result = service.suggestInsert({
        .userPrompt = "insert project status",
        .pageContent = "",
        .contextJson = "{}",
    });

    wikilive::tests::expect(result.has_value(), "AI service should normalize provider output");
    wikilive::tests::expectEqual(result->candidates.size(), static_cast<std::size_t>(2), "duplicates and invalid candidates should be removed");
    wikilive::tests::expectEqual(result->candidates[0].insert, std::string("{{dst-demo:rec-demo:Status}}"), "insert should be canonical");
    wikilive::tests::expectEqual(result->candidates[0].reason, std::string("Suggested by AI"), "missing reason should be filled");
    wikilive::tests::expectEqual(result->candidates[0].confidence, 1.0, "confidence should be clamped");
    wikilive::tests::expectEqual(result->candidates[1].insert, std::string("{{dst-demo:rec-owner:Owner}}"), "secondary candidate should also be canonical");
}

void filtersCandidatesUsingVerifier() {
    auto provider = std::make_unique<FakeAiProvider>();
    provider->nextResult.candidates = {
        {
            .tableId = "dst-demo",
            .recordId = "rec-status",
            .fieldName = "Status",
            .insert = "",
            .reason = "status",
            .confidence = 0.9,
        },
        {
            .tableId = "dst-demo",
            .recordId = "rec-obsolete",
            .fieldName = "Deprecated",
            .insert = "",
            .reason = "deprecated",
            .confidence = 0.8,
        },
    };

    auto verifier = std::make_unique<FakeAiFieldVerifier>();
    verifier->deniedKeys = {"dst-demo:rec-obsolete:Deprecated"};
    auto* verifierRaw = verifier.get();

    auto validator = std::make_unique<wikilive::ai::AiSuggestionValidator>(std::move(verifier));
    wikilive::ai::AiService service(std::move(provider), std::move(validator));

    const auto result = service.suggestInsert({
        .userPrompt = "insert status",
        .pageContent = "",
        .contextJson = "{}",
    });

    wikilive::tests::expect(result.has_value(), "AI validation should succeed when verifier responds");
    wikilive::tests::expectEqual(result->candidates.size(), static_cast<std::size_t>(1), "denied candidate should be filtered out");
    wikilive::tests::expectEqual(
        result->candidates[0].insert,
        std::string("{{dst-demo:rec-status:Status}}"),
        "verified candidate should stay in canonical form");
    wikilive::tests::expectEqual(
        verifierRaw->seenQueries.size(),
        static_cast<std::size_t>(2),
        "verifier should inspect both candidates");
}

void buildsContextWhenRequestDoesNotProvideIt() {
    auto provider = std::make_unique<FakeAiProvider>();
    provider->nextResult.candidates = {
        {
            .tableId = "dst-demo",
            .recordId = "rec-status",
            .fieldName = "Status",
            .insert = "",
            .reason = "status",
            .confidence = 0.9,
        },
    };
    auto* providerRaw = provider.get();

    auto contextBuilder = std::make_unique<FakeAiContextBuilder>();
    auto* contextBuilderRaw = contextBuilder.get();
    wikilive::ai::AiService service(
        std::move(provider),
        std::make_unique<wikilive::ai::AiSuggestionValidator>(),
        std::move(contextBuilder));

    const auto result = service.suggestInsert({
        .userPrompt = "insert status",
        .pageContent = "",
        .contextJson = "",
    });

    wikilive::tests::expect(result.has_value(), "AI request should succeed with built context");
    wikilive::tests::expectEqual(contextBuilderRaw->buildCalls, 1, "context builder should be used when request context is empty");
    wikilive::tests::expectEqual(
        providerRaw->lastRequest.userPrompt,
        std::string("insert status"),
        "provider should still receive original user prompt");
    wikilive::tests::expect(
        providerRaw->lastRequest.contextJson.find("\"tableId\":\"dst-demo\"") != std::string::npos,
        "provider should receive generated context");
}

void propagatesVerifierInfrastructureErrors() {
    auto provider = std::make_unique<FakeAiProvider>();
    provider->nextResult.candidates = {
        {
            .tableId = "dst-demo",
            .recordId = "rec-status",
            .fieldName = "Status",
            .insert = "",
            .reason = "status",
            .confidence = 0.9,
        },
    };

    auto verifier = std::make_unique<FakeAiFieldVerifier>();
    verifier->errorKey = "dst-demo:rec-status:Status";
    auto validator = std::make_unique<wikilive::ai::AiSuggestionValidator>(std::move(verifier));
    wikilive::ai::AiService service(std::move(provider), std::move(validator));

    const auto result = service.suggestInsert({
        .userPrompt = "insert status",
        .pageContent = "",
        .contextJson = "{}",
    });

    wikilive::tests::expect(!result.has_value(), "transient verifier errors should fail the AI request");
    wikilive::tests::expectEqual(result.error().code, wikilive::utils::ErrorCode::MwsRateLimit, "verifier error should propagate");
}

void createsOpenRouterProviderFromConfig() {
    wikilive::core::AppConfig config;
    config.enableAi = true;
    config.aiProvider = "openrouter";
    config.aiBaseUrl = "https://openrouter.ai/api/v1";
    config.aiApiKey = "test-key";
    config.aiModel = "meta-llama/llama-3.3-70b-instruct";
    config.aiMaxTokens = 300;
    config.aiTemperature = 0.1;

    wikilive::ai::AiService service(wikilive::ai::createAiProvider(config));
    wikilive::tests::expect(service.isAvailable(), "AI service should be available with OpenRouter config");

    const auto metadata = service.metadata();
    wikilive::tests::expectEqual(metadata.provider, std::string("openrouter"), "provider should match config");
    wikilive::tests::expectEqual(metadata.model, config.aiModel, "model should match config");
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
        {"normalizes and deduplicates candidates", normalizesAndDeduplicatesCandidates},
        {"filters candidates using verifier", filtersCandidatesUsingVerifier},
        {"builds context when request does not provide it", buildsContextWhenRequestDoesNotProvideIt},
        {"propagates verifier infrastructure errors", propagatesVerifierInfrastructureErrors},
        {"creates openrouter provider from config", createsOpenRouterProviderFromConfig},
        {"creates ollama provider from config", createsOllamaProviderFromConfig},
    });
}
