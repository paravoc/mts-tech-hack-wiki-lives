#include "src/server/router.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "tests/test_common.h"

namespace {

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

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"returns health payload", returnsHealthPayload},
        {"handles page crud flow", handlesPageCrudFlow},
        {"renders content from json payload", rendersContentFromJsonPayload},
        {"rejects malformed payload", rejectsMalformedPayload},
    });
}
