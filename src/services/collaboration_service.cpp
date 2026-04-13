#include "src/services/collaboration_service.h"

#include <algorithm>
#include <chrono>
#include <cctype>
#include <unordered_set>

#include <nlohmann/json.hpp>

#include "src/utils/time_utils.h"

namespace wikilive::services {
namespace {

using json = nlohmann::json;

std::string normalizeActor(std::string actor) {
    std::transform(actor.begin(), actor.end(), actor.begin(), [](unsigned char value) {
        return static_cast<char>(std::tolower(value));
    });
    return actor;
}

bool isAdminActor(const std::string& actor) {
    static const std::unordered_set<std::string> kAdminActors = {"admin", "anton", "ivan"};
    return kAdminActors.contains(normalizeActor(actor));
}

utils::Error forbiddenError(const std::string& message) {
    return utils::makeError(
        utils::ErrorCode::InvalidRequest,
        message,
        403,
        false);
}

json commentMessageToJson(const models::CommentMessage& message) {
    return {
        {"messageId", message.messageId},
        {"author", message.author},
        {"body", message.body},
        {"createdAt", message.createdAt},
        {"updatedAt", message.updatedAt},
        {"replyToMessageId", message.replyToMessageId},
        {"deleted", message.deleted},
        {"likedBy", message.likedBy},
        {"likeCount", message.likedBy.size()},
    };
}

json commentThreadToJson(const models::CommentThread& thread) {
    json messages = json::array();
    for (const auto& message : thread.messages) {
        messages.push_back(commentMessageToJson(message));
    }

    return {
        {"threadId", thread.threadId},
        {"pageId", thread.pageId},
        {"targetId", thread.targetId},
        {"targetType", thread.targetType},
        {"selectionLabel", thread.selectionLabel},
        {"targetPreview", thread.targetPreview},
        {"anchor", {
            {"anchorId", thread.anchor.anchorId},
            {"quote", thread.anchor.quote},
            {"selector", thread.anchor.selector},
            {"blockId", thread.anchor.blockId},
            {"blockType", thread.anchor.blockType},
            {"startOffset", thread.anchor.startOffset},
            {"endOffset", thread.anchor.endOffset},
        }},
        {"createdAt", thread.createdAt},
        {"updatedAt", thread.updatedAt},
        {"resolved", thread.resolved},
        {"resolvedAt", thread.resolvedAt},
        {"resolvedBy", thread.resolvedBy},
        {"paused", thread.paused},
        {"pausedAt", thread.pausedAt},
        {"pausedBy", thread.pausedBy},
        {"deleted", thread.deleted},
        {"deletedAt", thread.deletedAt},
        {"deletedBy", thread.deletedBy},
        {"likedBy", thread.likedBy},
        {"likeCount", thread.messages.empty() ? thread.likedBy.size() : thread.messages.front().likedBy.size()},
        {"messages", messages},
    };
}

json commentThreadSnapshotToJson(const std::vector<models::CommentThread>& threads) {
    json items = json::array();
    for (const auto& thread : threads) {
        items.push_back(commentThreadToJson(thread));
    }
    return items;
}

bool isSameVersionSnapshot(
    const models::PageVersion& version,
    const models::Page& page,
    const std::vector<models::CommentThread>& threads,
    const std::string& commentAccessMode) {
    return version.title == page.title &&
           version.projectId == page.projectId &&
           version.description == page.description &&
           version.content == page.content &&
           version.sharedWith == page.sharedWith &&
           version.access.publicAccess == page.access.publicAccess &&
           version.access.userIds == page.access.userIds &&
           version.access.groupIds == page.access.groupIds &&
           version.access.roles == page.access.roles &&
           version.commentAccessMode == commentAccessMode &&
           commentThreadSnapshotToJson(version.threadSnapshot) == commentThreadSnapshotToJson(threads);
}

std::size_t countThreadMessages(const std::vector<models::CommentThread>& threads) {
    std::size_t total = 0;
    for (const auto& thread : threads) {
        total += thread.messages.size();
    }
    return total;
}

}  // namespace

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

utils::Expected<models::PageVersion> CollaborationService::getVersion(
    const std::string& pageId,
    const std::string& versionId) const {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    return storage_.getVersion(pageId, versionId);
}

utils::Expected<models::PageVersion> CollaborationService::captureVersion(
    const models::Page& page,
    const std::string& label,
    const std::string& author) {
    const auto versions = storage_.listVersions(page.pageId);
    if (!versions) {
        return std::unexpected(versions.error());
    }

    const auto threads = storage_.listThreads(page.pageId);
    if (!threads) {
        return std::unexpected(threads.error());
    }

    const auto accessMode = storage_.getCommentAccess(page.pageId);
    if (!accessMode) {
        return std::unexpected(accessMode.error());
    }

    if (!versions->empty()) {
        const auto& latest = versions->front();
        if (isSameVersionSnapshot(latest, page, threads.value(), accessMode.value())) {
            return latest;
        }
    }

    models::PageVersion version{
        .versionId = nextId("ver"),
        .pageId = page.pageId,
        .projectId = page.projectId,
        .title = page.title,
        .description = page.description,
        .content = page.content,
        .createdAt = utils::formatIso(utils::now()),
        .label = label,
        .author = author.empty() ? "system" : author,
        .sharedWith = page.sharedWith,
        .access = page.access,
        .threadSnapshot = threads.value(),
        .commentAccessMode = accessMode.value(),
        .threadCount = threads->size(),
        .commentCount = countThreadMessages(threads.value()),
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
            .description = version->description,
            .content = version->content,
            .sharedWith = version->sharedWith,
            .sharedWithProvided = true,
            .access = version->access,
            .accessProvided = true,
        });
    if (!restored) {
        return std::unexpected(restored.error());
    }

    const auto restoreSnapshot = storage_.restoreCommentSnapshot(
        pageId,
        version->threadSnapshot,
        version->commentAccessMode.empty() ? "all_users" : version->commentAccessMode);
    if (!restoreSnapshot) {
        return std::unexpected(restoreSnapshot.error());
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

    auto threads = storage_.listThreads(pageId);
    if (!threads) {
        return std::unexpected(threads.error());
    }

    std::vector<models::CommentThread> activeThreads;
    for (const auto& thread : threads.value()) {
        if (!thread.deleted) {
            auto filteredThread = thread;
            filteredThread.messages.erase(
                std::remove_if(
                    filteredThread.messages.begin(),
                    filteredThread.messages.end(),
                    [](const models::CommentMessage& message) { return message.deleted; }),
                filteredThread.messages.end());
            activeThreads.push_back(std::move(filteredThread));
        }
    }
    return activeThreads;
}

utils::Expected<std::vector<models::CommentThread>> CollaborationService::listHistory(const std::string& pageId) const {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    auto threads = storage_.listThreads(pageId);
    if (!threads) {
        return std::unexpected(threads.error());
    }

    std::vector<models::CommentThread> historyThreads;
    for (const auto& thread : threads.value()) {
        if (thread.deleted || thread.resolved || thread.paused) {
            historyThreads.push_back(thread);
        }
    }
    return historyThreads;
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

    const auto existingThreads = storage_.listThreads(pageId);
    if (!existingThreads) {
        return std::unexpected(existingThreads.error());
    }

    auto duplicateThread = std::find_if(
        existingThreads->begin(),
        existingThreads->end(),
        [&](const models::CommentThread& thread) {
            return !thread.deleted && thread.targetId == validDraft->targetId;
        });
    if (duplicateThread != existingThreads->end()) {
        auto preservedThread = *duplicateThread;
        bool changed = false;
        if (preservedThread.targetType.empty() && !validDraft->targetType.empty()) {
            preservedThread.targetType = validDraft->targetType;
            changed = true;
        }
        if (preservedThread.selectionLabel.empty() && !validDraft->selectionLabel.empty()) {
            preservedThread.selectionLabel = validDraft->selectionLabel;
            changed = true;
        }
        if (preservedThread.targetPreview.empty() && !validDraft->targetPreview.empty()) {
            preservedThread.targetPreview = validDraft->targetPreview;
            changed = true;
        }
        if (changed) {
            const auto saveResult = storage_.saveThread(preservedThread);
            if (!saveResult) {
                return std::unexpected(saveResult.error());
            }
        }
        return preservedThread;
    }

    const auto timestamp = utils::formatIso(utils::now());
    models::CommentThread thread{
        .threadId = nextId("thread"),
        .pageId = pageId,
        .targetId = validDraft->targetId,
        .targetType = validDraft->targetType,
        .selectionLabel = validDraft->selectionLabel,
        .targetPreview = validDraft->targetPreview,
        .anchor = validDraft->anchor,
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
                .updatedAt = timestamp,
                .likedBy = {},
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
        .updatedAt = timestamp,
        .replyToMessageId = validDraft->replyToMessageId,
        .likedBy = {},
    });
    thread->updatedAt = timestamp;
    thread->deleted = false;
    thread->deletedAt.clear();
    thread->deletedBy.clear();

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::setResolved(
    const std::string& pageId,
    const std::string& threadId,
    const bool resolved,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto normalizedActor = actor.empty() ? std::string("viewer") : actor;
    thread->resolved = resolved;
    thread->updatedAt = utils::formatIso(utils::now());
    if (resolved) {
        thread->resolvedAt = thread->updatedAt;
        thread->resolvedBy = normalizedActor;
        thread->paused = false;
        thread->pausedAt.clear();
        thread->pausedBy.clear();
    } else {
        thread->resolvedAt.clear();
        thread->resolvedBy.clear();
    }

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::setPaused(
    const std::string& pageId,
    const std::string& threadId,
    const bool paused,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto normalizedActor = actor.empty() ? std::string("viewer") : actor;
    const auto rootAuthor = thread->messages.empty() ? std::string("viewer") : thread->messages.front().author;
    if (!isAdminActor(normalizedActor) && normalizeActor(rootAuthor) != normalizeActor(normalizedActor)) {
        return std::unexpected(forbiddenError("Only the thread author or admin may pause this discussion"));
    }

    thread->paused = paused;
    thread->updatedAt = utils::formatIso(utils::now());
    if (paused) {
        thread->pausedAt = thread->updatedAt;
        thread->pausedBy = normalizedActor;
        thread->resolved = false;
        thread->resolvedAt.clear();
        thread->resolvedBy.clear();
    } else {
        thread->pausedAt.clear();
        thread->pausedBy.clear();
    }

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::toggleLike(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& messageId,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    auto messageIt = thread->messages.end();
    if (!messageId.empty()) {
        messageIt = std::find_if(
            thread->messages.begin(),
            thread->messages.end(),
            [&](const models::CommentMessage& message) { return message.messageId == messageId && !message.deleted; });
    } else {
        messageIt = std::find_if(
            thread->messages.begin(),
            thread->messages.end(),
            [](const models::CommentMessage& message) { return !message.deleted; });
    }
    if (messageIt == thread->messages.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Comment message was not found",
            404,
            false));
    }

    const auto user = normalizeActor(actor.empty() ? std::string("viewer") : actor);
    const auto likeIt = std::find_if(
        messageIt->likedBy.begin(),
        messageIt->likedBy.end(),
        [&](const std::string& existingActor) { return normalizeActor(existingActor) == user; });
    if (likeIt == messageIt->likedBy.end()) {
        messageIt->likedBy.push_back(user);
    } else {
        messageIt->likedBy.erase(likeIt);
    }
    if (messageIt == thread->messages.begin()) {
        thread->likedBy = messageIt->likedBy;
    }
    thread->updatedAt = utils::formatIso(utils::now());

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::updateMessage(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& messageId,
    const std::string& body,
    const std::string& actor) {
    if (body.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "comment body must not be empty",
            400,
            false));
    }

    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto messageIt = std::find_if(
        thread->messages.begin(),
        thread->messages.end(),
        [&](const models::CommentMessage& message) { return message.messageId == messageId; });
    if (messageIt == thread->messages.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Comment message not found: " + messageId,
            404,
            false));
    }

    const auto normalizedActor = actor.empty() ? std::string("viewer") : actor;
    if (!isAdminActor(normalizedActor) && normalizeActor(messageIt->author) != normalizeActor(normalizedActor)) {
        return std::unexpected(forbiddenError("Only the comment author or admin may edit this comment"));
    }
    messageIt->body = body;
    messageIt->updatedAt = utils::formatIso(utils::now());
    thread->updatedAt = messageIt->updatedAt;

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::deleteMessage(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& messageId,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto messageIt = std::find_if(
        thread->messages.begin(),
        thread->messages.end(),
        [&](const models::CommentMessage& message) { return message.messageId == messageId; });
    if (messageIt == thread->messages.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Comment message not found: " + messageId,
            404,
            false));
    }

    const auto normalizedActor = actor.empty() ? std::string("viewer") : actor;
    if (!isAdminActor(normalizedActor) && normalizeActor(messageIt->author) != normalizeActor(normalizedActor)) {
        return std::unexpected(forbiddenError("Only the comment author or admin may delete this comment"));
    }

    messageIt->deleted = true;
    messageIt->updatedAt = utils::formatIso(utils::now());
    thread->updatedAt = messageIt->updatedAt;

    const bool allDeleted = std::all_of(
        thread->messages.begin(),
        thread->messages.end(),
        [](const models::CommentMessage& message) { return message.deleted; });
    if (allDeleted) {
        thread->deleted = true;
        thread->deletedAt = thread->updatedAt;
        thread->deletedBy = normalizedActor;
    }

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<models::CommentThread> CollaborationService::deleteThread(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& actor) {
    auto thread = storage_.getThread(pageId, threadId);
    if (!thread) {
        return std::unexpected(thread.error());
    }

    const auto normalizedActor = actor.empty() ? std::string("viewer") : actor;
    const auto rootAuthor = thread->messages.empty() ? std::string("viewer") : thread->messages.front().author;
    if (!isAdminActor(normalizedActor) && normalizeActor(rootAuthor) != normalizeActor(normalizedActor)) {
        return std::unexpected(forbiddenError("Only the thread author or admin may delete this thread"));
    }

    thread->deleted = true;
    thread->deletedAt = utils::formatIso(utils::now());
    thread->deletedBy = normalizedActor;
    thread->updatedAt = thread->deletedAt;

    const auto saveResult = storage_.saveThread(thread.value());
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return thread.value();
}

utils::Expected<std::string> CollaborationService::getCommentAccess(const std::string& pageId) const {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    return storage_.getCommentAccess(pageId);
}

utils::Expected<std::string> CollaborationService::setCommentAccess(
    const std::string& pageId,
    const std::string& accessMode) {
    const auto pageExists = ensurePageExists(pageId);
    if (!pageExists) {
        return std::unexpected(pageExists.error());
    }

    const auto normalized = accessMode == "owner_only" ? std::string("owner_only") : std::string("all_users");
    const auto saveResult = storage_.saveCommentAccess(pageId, normalized);
    if (!saveResult) {
        return std::unexpected(saveResult.error());
    }

    return normalized;
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
    if (draft.targetId.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "comment targetId must not be empty",
            400,
            false));
    }

    CommentThreadDraft validDraft = draft;
    if (validDraft.author.empty()) {
        validDraft.author = "viewer";
    }
    if (validDraft.targetType.empty()) {
        validDraft.targetType = "paragraph";
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
