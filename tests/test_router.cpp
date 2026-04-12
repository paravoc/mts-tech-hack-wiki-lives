#include <filesystem>

#include "src/ai/ai_context_builder.h"
#include "src/ai/ai_provider.h"
#include "src/ai/ai_service.h"
#include "src/server/router.h"
#include "src/services/collaboration_service.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "src/storage/local_collaboration_storage.h"
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

    const auto createResponse = router.createPage(R"({"title":"Wiki page","description":"Short summary","content":"Status: {{projects:rec123:status}}","ownerId":"ivan","ownerName":"Иван Иванов"})");
    wikilive::tests::expectEqual(createResponse.statusCode, 201, "create should return 201");
    wikilive::tests::expect(createResponse.body.find("\"pageId\":\"page-1\"") != std::string::npos, "created page should be returned");
    wikilive::tests::expect(createResponse.body.find("\"ownerId\":\"ivan\"") != std::string::npos, "created page owner should be returned");
    wikilive::tests::expect(createResponse.body.find("\"description\":\"Short summary\"") != std::string::npos, "created page description should be returned");

    const auto listResponse = router.listPages();
    wikilive::tests::expectEqual(listResponse.statusCode, 200, "list should return 200");
    wikilive::tests::expect(listResponse.body.find("\"items\"") != std::string::npos, "list should contain items");

    const auto getResponse = router.getPage("page-1");
    wikilive::tests::expectEqual(getResponse.statusCode, 200, "get should return 200");
    wikilive::tests::expect(getResponse.body.find("wikilive-insert") != std::string::npos, "get should include rendered html");

    const auto updateResponse = router.updatePage("page-1", R"({"title":"Updated","description":"Updated summary","content":"Updated body","ownerId":"sergei","ownerName":"Сергей Иванов"})");
    wikilive::tests::expectEqual(updateResponse.statusCode, 200, "update should return 200");
    wikilive::tests::expect(updateResponse.body.find("\"title\":\"Updated\"") != std::string::npos, "updated title should be returned");
    wikilive::tests::expect(updateResponse.body.find("\"ownerId\":\"sergei\"") != std::string::npos, "updated page owner should be returned");
    wikilive::tests::expect(updateResponse.body.find("\"description\":\"Updated summary\"") != std::string::npos, "updated page description should be returned");

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
    wikilive::server::Router router(pageService, renderService);

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

void handlesVersionsAndCommentsFlow() {
    const auto tempPath = std::filesystem::current_path() / "test-router-collaboration.json";
    std::filesystem::remove(tempPath);

    wikilive::storage::InMemoryPageStorage storage;
    wikilive::storage::LocalCollaborationStorage collaborationStorage(tempPath.string());
    wikilive::services::PageService pageService(storage);
    wikilive::services::CollaborationService collaborationService(pageService, collaborationStorage);
    wikilive::services::RenderService renderService;
    wikilive::server::Router router(pageService, renderService, static_cast<wikilive::ai::AiService*>(nullptr), &collaborationService, nullptr);

    const auto createResponse = router.createPage(R"({"title":"Wiki page","content":"Draft"})");
    wikilive::tests::expectEqual(createResponse.statusCode, 201, "create should return 201");

    const auto listVersionsResponse = router.listVersions("page-1");
    wikilive::tests::expectEqual(listVersionsResponse.statusCode, 200, "versions should return 200");
    wikilive::tests::expect(
        listVersionsResponse.body.find("\"label\":\"Created page\"") != std::string::npos,
        "created page snapshot should exist");

    const auto manualVersionResponse = router.createVersion("page-1", R"({"label":"Checkpoint"})");
    wikilive::tests::expectEqual(manualVersionResponse.statusCode, 201, "manual version should return 201");

    const auto updateResponse = router.updatePage("page-1", R"({"title":"Wiki page","content":"Draft v2"})");
    wikilive::tests::expectEqual(updateResponse.statusCode, 200, "update should return 200");

    const auto commentResponse = router.createComment(
        "page-1",
        R"({"author":"sergei","body":"Needs review","selectionLabel":"Paragraph 1","targetId":"block-1","targetType":"paragraph","targetPreview":"Paragraph 1"})");
    wikilive::tests::expectEqual(commentResponse.statusCode, 201, "comment should return 201");
    wikilive::tests::expect(commentResponse.body.find("\"selectionLabel\":\"Paragraph 1\"") != std::string::npos, "selection label should be persisted");
    wikilive::tests::expect(commentResponse.body.find("\"targetId\":\"block-1\"") != std::string::npos, "target id should be persisted");

    const auto duplicateTargetResponse = router.createComment(
        "page-1",
        R"({"author":"anton","body":"Duplicate target should not create another thread","selectionLabel":"Paragraph 1","targetId":"block-1","targetType":"paragraph","targetPreview":"Paragraph 1"})");
    wikilive::tests::expectEqual(duplicateTargetResponse.statusCode, 201, "duplicate target should still return a thread payload");

    const auto commentsResponse = router.listComments("page-1");
    wikilive::tests::expectEqual(commentsResponse.statusCode, 200, "comments should return 200");
    wikilive::tests::expect(commentsResponse.body.find("\"Needs review\"") != std::string::npos, "comment list should contain body");
    wikilive::tests::expect(
        commentsResponse.body.find("Duplicate target should not create another thread") == std::string::npos,
        "duplicate target should not create a second active thread");

    const auto threadIdStart = commentsResponse.body.find("\"threadId\":\"");
    wikilive::tests::expect(threadIdStart != std::string::npos, "threadId should be present");
    const auto threadValueStart = threadIdStart + std::string("\"threadId\":\"").size();
    const auto threadValueEnd = commentsResponse.body.find('"', threadValueStart);
    const auto threadId = commentsResponse.body.substr(threadValueStart, threadValueEnd - threadValueStart);

    const auto rootMessageIdStart = commentsResponse.body.find("\"messageId\":\"");
    wikilive::tests::expect(rootMessageIdStart != std::string::npos, "root messageId should be present");
    const auto rootMessageValueStart = rootMessageIdStart + std::string("\"messageId\":\"").size();
    const auto rootMessageValueEnd = commentsResponse.body.find('"', rootMessageValueStart);
    const auto rootMessageId = commentsResponse.body.substr(rootMessageValueStart, rootMessageValueEnd - rootMessageValueStart);

    const auto replyResponse = router.replyToComment("page-1", threadId, R"({"author":"ivan","body":"Working on it"})");
    wikilive::tests::expectEqual(replyResponse.statusCode, 200, "reply should return 200");
    wikilive::tests::expect(replyResponse.body.find("\"Working on it\"") != std::string::npos, "reply body should be stored");

    const auto messageIdStart = replyResponse.body.rfind("\"messageId\":\"");
    wikilive::tests::expect(messageIdStart != std::string::npos, "messageId should be present");
    const auto messageValueStart = messageIdStart + std::string("\"messageId\":\"").size();
    const auto messageValueEnd = replyResponse.body.find('"', messageValueStart);
    const auto messageId = replyResponse.body.substr(messageValueStart, messageValueEnd - messageValueStart);

    const auto editResponse = router.updateCommentMessage("page-1", threadId, messageId, R"({"author":"ivan","body":"Updated reply"})");
    wikilive::tests::expectEqual(editResponse.statusCode, 200, "edit should return 200");
    wikilive::tests::expect(editResponse.body.find("\"Updated reply\"") != std::string::npos, "edited reply should be stored");

    const auto forbiddenEditResponse =
        router.updateCommentMessage("page-1", threadId, messageId, R"({"author":"anna","body":"Nope"})");
    wikilive::tests::expectEqual(forbiddenEditResponse.statusCode, 403, "foreign author edit should be rejected");

    const auto likeResponse = router.toggleCommentLike("page-1", threadId, std::string("{\"author\":\"tester\",\"messageId\":\"") + rootMessageId + "\"}");
    wikilive::tests::expectEqual(likeResponse.statusCode, 200, "like should return 200");
    wikilive::tests::expect(likeResponse.body.find("\"likeCount\":1") != std::string::npos, "like count should increase");

    const auto unlikeResponse = router.toggleCommentLike("page-1", threadId, std::string("{\"author\":\"tester\",\"messageId\":\"") + rootMessageId + "\"}");
    wikilive::tests::expectEqual(unlikeResponse.statusCode, 200, "second like should toggle off");
    wikilive::tests::expect(unlikeResponse.body.find("\"likeCount\":0") != std::string::npos, "like count should drop back to zero");

    const auto resolveResponse = router.resolveComment("page-1", threadId, R"({"author":"ivan","resolved":true})");
    wikilive::tests::expectEqual(resolveResponse.statusCode, 200, "resolve should return 200");
    wikilive::tests::expect(resolveResponse.body.find("\"resolved\":true") != std::string::npos, "thread should be resolved");
    wikilive::tests::expect(resolveResponse.body.find("\"resolvedBy\":\"ivan\"") != std::string::npos, "resolved author should be stored");

    const auto historyResponse = router.listCommentHistory("page-1");
    wikilive::tests::expectEqual(historyResponse.statusCode, 200, "history should return 200");
    wikilive::tests::expect(historyResponse.body.find("\"threadId\":\"") != std::string::npos, "history should contain resolved thread");

    const auto forbiddenDeleteMessageResponse =
        router.deleteCommentMessage("page-1", threadId, messageId, R"({"author":"anna"})");
    wikilive::tests::expectEqual(forbiddenDeleteMessageResponse.statusCode, 403, "foreign author delete should be rejected");

    const auto deleteMessageResponse = router.deleteCommentMessage("page-1", threadId, messageId, R"({"author":"ivan"})");
    wikilive::tests::expectEqual(deleteMessageResponse.statusCode, 200, "delete message should return 200");

    const auto deleteThreadResponse = router.deleteCommentThread("page-1", threadId, R"({"author":"anton"})");
    wikilive::tests::expectEqual(deleteThreadResponse.statusCode, 200, "delete thread should return 200");

    const auto commentsAfterDelete = router.listComments("page-1");
    wikilive::tests::expectEqual(commentsAfterDelete.statusCode, 200, "comments after delete should return 200");
    wikilive::tests::expect(commentsAfterDelete.body.find("\"threadId\":\"") == std::string::npos, "deleted thread should disappear from active list");

    const auto versionsAfterUpdate = router.listVersions("page-1");
    wikilive::tests::expect(versionsAfterUpdate.body.find("\"Saved changes\"") != std::string::npos, "update snapshot should exist");

    std::filesystem::remove(tempPath);
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
        {"handles versions and comments flow", handlesVersionsAndCommentsFlow},
    });
}
