#include "src/services/page_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "src/utils/errors.h"
#include "src/utils/time_utils.h"
#include "tests/test_common.h"

namespace {

void createsReadsUpdatesAndDeletesPage() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService service(storage);

    const auto created = service.createPage({
        .projectId = "project-1",
        .title = "Project status",
        .content = "Initial content",
    });

    wikilive::tests::expect(created.has_value(), "page should be created");
    wikilive::tests::expectEqual(created->pageId, std::string("page-1"), "page id should start from page-1");

    const auto loaded = service.getPage(created->pageId);
    wikilive::tests::expect(loaded.has_value(), "created page should be readable");
    wikilive::tests::expectEqual(loaded->title, std::string("Project status"), "page title should match");

    wikilive::utils::sleepMs(1100);
    const auto updated = service.updatePage(created->pageId, {
        .projectId = "project-1",
        .title = "Updated status",
        .content = "Updated content",
    });

    wikilive::tests::expect(updated.has_value(), "page should be updated");
    wikilive::tests::expectEqual(updated->title, std::string("Updated status"), "updated title should match");
    wikilive::tests::expectEqual(updated->content, std::string("Updated content"), "updated content should match");
    wikilive::tests::expect(updated->updatedAt >= created->updatedAt, "updated timestamp should not go backwards");

    const auto deleted = service.deletePage(created->pageId);
    wikilive::tests::expect(deleted.has_value(), "page should be deleted");

    const auto missing = service.getPage(created->pageId);
    wikilive::tests::expect(!missing.has_value(), "deleted page should not be readable");
    wikilive::tests::expectEqual(missing.error().code, wikilive::utils::ErrorCode::PageNotFound, "deleted page should return not found");
}

void rejectsInvalidDraft() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService service(storage);

    const auto created = service.createPage({
        .projectId = "project-1",
        .title = "",
        .content = "Body",
    });

    wikilive::tests::expect(!created.has_value(), "empty title should be rejected");
    wikilive::tests::expectEqual(created.error().code, wikilive::utils::ErrorCode::InvalidRequest, "empty title should be invalid");
}

void sortsPagesByMostRecentlyUpdated() {
    wikilive::storage::InMemoryPageStorage storage;
    wikilive::services::PageService service(storage);

    const auto first = service.createPage({
        .projectId = "project-1",
        .title = "First",
        .content = "A",
    });
    wikilive::tests::expect(first.has_value(), "first page should be created");

    wikilive::utils::sleepMs(1100);

    const auto second = service.createPage({
        .projectId = "project-1",
        .title = "Second",
        .content = "B",
    });
    wikilive::tests::expect(second.has_value(), "second page should be created");

    wikilive::utils::sleepMs(1100);

    const auto updatedFirst = service.updatePage(first->pageId, {
        .projectId = "project-1",
        .title = "First updated",
        .content = "A2",
    });
    wikilive::tests::expect(updatedFirst.has_value(), "first page should be updated");

    const auto pages = service.listPages();
    wikilive::tests::expect(pages.has_value(), "page list should be readable");
    wikilive::tests::expectEqual(pages->size(), static_cast<std::size_t>(2), "there should be two pages");
    wikilive::tests::expectEqual(pages->front().pageId, first->pageId, "most recently updated page should be first");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"creates reads updates and deletes page", createsReadsUpdatesAndDeletesPage},
        {"rejects invalid draft", rejectsInvalidDraft},
        {"sorts pages by most recently updated", sortsPagesByMostRecentlyUpdated},
    });
}
