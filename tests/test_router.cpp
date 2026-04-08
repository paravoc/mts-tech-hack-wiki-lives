#include "src/ai/ai_provider.h"
#include "src/ai/ai_service.h"
#include "src/ai/ai_context_builder.h"
#include "src/server/router.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "tests/test_common.h"

namespace {

class FakeAiProvider final : public wikilive::ai::AiProvider {
public:
    const wikilive::ai::AiProviderMetadata& metadata() const override {
        return metadata_;
    }

    wikilive::utils::Expected<wikilive::ai::AiSuggestInsertResult> suggestInsert(
        const wikilive::ai::AiSuggestInsertRequest& request) const override {
        lastRequest = request;
        return wikilive::ai::AiSuggestInsertResult{
            .candidates = {
                {
                    .tableId = " dst1 ",
                    .recordId = " rec1 ",
                    .fieldName = " Status ",
                    .insert = "broken",
                    .reason = "",
                    .confidence = 0.91,
                },
            },
        };
    }

    mutable wikilive::ai::AiSuggestInsertRequest lastRequest;

private:
    wikilive::ai::AiProviderMetadata metadata_{
        .provider = "fake",
        .model = "fake-model",
        .baseUrl = "http://fake",
        .enabled = true,
    };
};

class FakeAiContextBuilder final : public wikilive::ai::AiContextBuilder {
public:
    wikilive::utils::Expected<std::string> buildSuggestInsertContext() const override {
        ++buildCalls;
        return R"({"tables":[{"tableId":"dst-built"}]})";
    }

    mutable int buildCalls = 0;
};

void returnsHealthPayload() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService);

    const auto response = router.handleHealth();
    wikilive::tests::expectEqual(response.statusCode, 200, "health should return 200");
    wikilive::tests::expect(response.body.find("\"status\":\"ok\"") != std::string::npos, "health body should contain ok status");
}

void handlesPageCrudFlow() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService);

    const auto createResponse = router.createPage(R"({"title":"Wiki page","content":"Status: {{projects:rec123:status}}"})");
    wikilive::tests::expectEqual(createResponse.statusCode, 201, "create should return 201");
    wikilive::tests::expect(createResponse.body.find("\"pageId\":\"page-1\"") != std::string::npos, "created page should be returned");

    const auto listResponse = router.listPages();
    wikilive::tests::expectEqual(listResponse.statusCode, 200, "list should return 200");
    wikilive::tests::expect(listResponse.body.find("\"items\"") != std::string::npos, "list should contain items");

    const auto getResponse = router.getPage("page-1");
    wikilive::tests::expectEqual(getResponse.statusCode, 200, "get should return 200");
    wikilive::tests::expect(getResponse.body.find("wikilive-insert") != std::string::npos, "get should include rendered html");

    const auto updateResponse = router.updatePage("page-1", R"({"title":"Updated","content":"Updated body"})");
    wikilive::tests::expectEqual(updateResponse.statusCode, 200, "update should return 200");
    wikilive::tests::expect(updateResponse.body.find("\"title\":\"Updated\"") != std::string::npos, "updated title should be returned");

    const auto deleteResponse = router.deletePage("page-1");
    wikilive::tests::expectEqual(deleteResponse.statusCode, 200, "delete should return 200");

    const auto missingResponse = router.getPage("page-1");
    wikilive::tests::expectEqual(missingResponse.statusCode, 404, "deleted page should return 404");
}

void rendersContentFromJsonPayload() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService);

    const auto renderResponse = router.renderContent(R"({"content":"Status: {{projects:rec123:status}}"})");
    wikilive::tests::expectEqual(renderResponse.statusCode, 200, "render should return 200");
    wikilive::tests::expect(renderResponse.body.find("wikilive-insert") != std::string::npos, "render should include insert span");
}

void rejectsMalformedPayload() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService);

    const auto response = router.createPage(R"({"title":"Only title"})");
    wikilive::tests::expectEqual(response.statusCode, 400, "missing content should return 400");
    wikilive::tests::expect(response.body.find("\"InvalidRequest\"") != std::string::npos, "error body should describe invalid request");
}

void rejectsAiRequestWhenServiceIsMissing() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService, nullptr, nullptr);

    const auto response = router.suggestInsert(R"({"userPrompt":"insert project status"})");
    wikilive::tests::expectEqual(response.statusCode, 503, "missing AI service should return 503");
    wikilive::tests::expect(response.body.find("\"InvalidConfig\"") != std::string::npos, "missing AI should be reported");
}

void handlesAiSuggestInsertFlow() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    auto provider = std::make_unique<FakeAiProvider>();
    auto* providerRaw = provider.get();
    wikilive::ai::AiService aiService(std::move(provider));
    wikilive::server::Router router(pageService, renderService, &aiService, nullptr);

    const auto response = router.suggestInsert(
        R"({"userPrompt":"insert project status","pageContent":"Current report","context":{"tables":[{"tableId":"dst1"}]}})");
    wikilive::tests::expectEqual(response.statusCode, 200, "AI suggestInsert should return 200");
    wikilive::tests::expect(response.body.find("{{dst1:rec1:Status}}") != std::string::npos, "AI response should include insert");
    wikilive::tests::expect(response.body.find("Suggested by AI") != std::string::npos, "AI response should include normalized reason");
    wikilive::tests::expectEqual(providerRaw->lastRequest.userPrompt, std::string("insert project status"), "prompt should be passed through");
    wikilive::tests::expect(providerRaw->lastRequest.contextJson.find("\"tableId\":\"dst1\"") != std::string::npos, "context object should be serialized");
}

void buildsAiContextWhenPayloadDoesNotIncludeIt() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService pageService(storage);
    wikilive::services::RenderService renderService;
    auto provider = std::make_unique<FakeAiProvider>();
    auto* providerRaw = provider.get();
    auto contextBuilder = std::make_unique<FakeAiContextBuilder>();
    auto* contextBuilderRaw = contextBuilder.get();
    wikilive::ai::AiService aiService(
        std::move(provider),
        std::make_unique<wikilive::ai::AiSuggestionValidator>(),
        std::move(contextBuilder));
    wikilive::server::Router router(pageService, renderService, &aiService, nullptr);

    const auto response = router.suggestInsert(R"({"userPrompt":"insert project status"})");
    wikilive::tests::expectEqual(response.statusCode, 200, "AI suggestInsert should build context when it is omitted");
    wikilive::tests::expectEqual(contextBuilderRaw->buildCalls, 1, "router path should trigger context builder");
    wikilive::tests::expect(
        providerRaw->lastRequest.contextJson.find("\"tableId\":\"dst-built\"") != std::string::npos,
        "provider should receive generated context");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"returns health payload", returnsHealthPayload},
        {"handles page crud flow", handlesPageCrudFlow},
        {"renders content from json payload", rendersContentFromJsonPayload},
        {"rejects malformed payload", rejectsMalformedPayload},
        {"rejects AI request when service is missing", rejectsAiRequestWhenServiceIsMissing},
        {"handles AI suggest insert flow", handlesAiSuggestInsertFlow},
        {"builds AI context when payload does not include it", buildsAiContextWhenPayloadDoesNotIncludeIt},
    });
}
