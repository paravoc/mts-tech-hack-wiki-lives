#include "src/services/collaboration_service.h"

#include <algorithm>
#include <chrono>

#include "src/utils/time_utils.h"

namespace wikilive::services {

CollaborationService::CollaborationService(PageService& pageService, storage::LocalCollaborationStorage& storage)
    : pageService_(pageService),
      storage_(storage) {
}

utils::Expected<std::vector<models::PageVersion>> CollaborationService::listVersions(const std::string& pageId) const {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    return storage_.listVersions(pageId);
}

utils::Expected<models::PageVersion> CollaborationService::captureVersion(
    const models::Page& page,
    const std::string& label,
    const std::string& author) {
    const auto versions = storage_.listVersions(page.pageId);
    if (!versions) {
        return std::unexpected(versions.error());
    }

    if (!versions->empty()) {
        const auto& latest = versions->front();
        if (latest.title == page.title && latest.content == page.content) {
            return latest;
        }
    }

    models::PageVersion version{
        .versionId = nextId("ver"),
        .pageId = page.pageId,
        .title = page.title,
        .content = page.content,
        .createdAt = utils::formatIso(utils::now()),
        .label = label,
        .author = author.empty() ? "system" : author,
    };

    const auto appendResult = storage_.appendVersion(version);
    if (!appendResult) {
        return std::unexpected(appendResult.error());
    }

    return version;
}

utils::Expected<models::PageVersion> CollaborationService::createManualVersion(
    const std::string& pageId,
    const std::string& label,
    const std::string& author) {
    const auto page = pageService_.getPage(pageId);
    if (!page) {
        return std::unexpected(page.error());
    }

    return captureVersion(page.value(), label.empty() ? "Manual snapshot" : label, author);
}

utils::Expected<models::Page> CollaborationService::restoreVersion(
    const std::string& pageId,
    const std::string& versionId,
    const std::string& author) {
    const auto currentPage = pageService_.getPage(pageId);
    if (!currentPage) {
        return std::unexpected(currentPage.error());
    }

    const auto version = storage_.getVersion(pageId, versionId);
    if (!version) {
        return std::unexpected(version.error());
    }

    const auto preRestoreSnapshot = captureVersion(currentPage.value(), "Auto snapshot before restore", author);
    if (!preRestoreSnapshot) {
        return std::unexpected(preRestoreSnapshot.error());
    }

    const auto restored = pageService_.updatePage(
        pageId,
        PageDraft{
            .title = version->title,
            .content = version->content,
        });
    if (!restored) {
        return std::unexpected(restored.error());
    }

    const auto postRestoreSnapshot = captureVersion(restored.value(), "Restored from version", author);
    if (!postRestoreSnapshot) {
        return std::unexpected(postRestoreSnapshot.error());
    }

    return restored.value();
}

utils::Expected<std::vector<models::CommentThread>> CollaborationService::listThreads(const std::string& pageId) const {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    return storage_.listThreads(pageId);
}

utils::Expected<models::CommentThread> CollaborationService::createThread(
    const std::string& pageId,
    const CommentThreadDraft& draft) {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    const auto validDraft = validateThreadDraft(draft);
    if (!validDraft) {
        return std::unexpected(validDraft.error());
    }

    const auto timestamp = utils::formatIso(utils::now());
    models::CommentThread thread{
        .threadId = nextId("thread"),
        .pageId = pageId,
        .selectionLabel = validDraft->selectionLabel,
        .createdAt = timestamp,
        .updatedAt = timestamp,
        .resolved = false,
        .likedBy = {},
        .messages = {
            models::CommentMessage{
                .messageId = nextId("msg"),
                .author = validDraft->author,
                .body = validDraft->body,
                .createdAt = timestamp,
            },
        },
    };

    const auto saveResult = storage_.saveThread(thread);
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread;
}

utils::Expected<models::CommentThread> CollaborationService::addReply(
    const std::string& pageId,
    const std::string& threadId,
    const CommentReplyDraft& draft) {
    const auto validDraft = validateReplyDraft(draft);
    if (!validDraft) {
        return std::unexpected(validDraft.error());
    }

    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto timestamp = utils::formatIso(utils::now());
    thread->messages.push_back(models::CommentMessage{
        .messageId = nextId("msg"),
        .author = validDraft->author,
        .body = validDraft->body,
        .createdAt = timestamp,
    });
    thread->updatedAt = timestamp;

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::setResolved(
    const std::string& pageId,
    const std::string& threadId,
    const bool resolved) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    thread->resolved = resolved;
    thread->updatedAt = utils::formatIso(utils::now());

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::toggleLike(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto user = actor.empty() ? std::string("viewer") : actor;
    const auto likeIt = std::find(thread->likedBy.begin(), thread->likedBy.end(), user);
    if (likeIt == thread->likedBy.end()) {
        thread->likedBy.push_back(user);
    } else {
        thread->likedBy.erase(likeIt);
    }
    thread->updatedAt = utils::formatIso(utils::now());

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::VoidExpected CollaborationService::deletePageData(const std::string& pageId) {
    return storage_.deletePageData(pageId);
}

utils::Expected<void> CollaborationService::ensurePageExists(const std::string& pageId) const {
    const auto page = pageService_.getPage(pageId);
    if (!page) {
        return std::unexpected(page.error());
    }

    return {};
}

utils::Expected<CommentThreadDraft> CollaborationService::validateThreadDraft(const CommentThreadDraft& draft) const {
    if (draft.body.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "comment body must not be empty",
            400,
            false));
    }

    CommentThreadDraft validDraft = draft;
    if (validDraft.author.empty()) {
        validDraft.author = "viewer";
    }
    return validDraft;
}

utils::Expected<CommentReplyDraft> CollaborationService::validateReplyDraft(const CommentReplyDraft& draft) const {
    if (draft.body.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "reply body must not be empty",
            400,
            false));
    }

    CommentReplyDraft validDraft = draft;
    if (validDraft.author.empty()) {
        validDraft.author = "viewer";
    }
    return validDraft;
}

std::string CollaborationService::nextId(const std::string& prefix) {
    const auto epochMs = std::chrono::duration_cast<std::chrono::milliseconds>(
        utils::now().time_since_epoch())
                             .count();
    return prefix + "-" + std::to_string(epochMs) + "-" + std::to_string(nextIdCounter_++);
}

}  // namespace wikilive::services
