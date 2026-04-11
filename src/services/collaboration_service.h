#pragma once

#include <string>
#include <vector>

#include "src/models/comment_thread.h"
#include "src/models/page.h"
#include "src/models/page_version.h"
#include "src/services/page_service.h"
#include "src/storage/local_collaboration_storage.h"
#include "src/utils/errors.h"

namespace wikilive::services {

struct CommentThreadDraft {
    std::string author;
    std::string body;
    std::string selectionLabel;
    std::string targetId;
    std::string targetType;
    std::string targetPreview;
};

struct CommentReplyDraft {
    std::string author;
    std::string body;
    std::string replyToMessageId;
};

class CollaborationService {
public:
    CollaborationService(PageService& pageService, storage::LocalCollaborationStorage& storage);

    [[nodiscard]] utils::Expected<std::vector<models::PageVersion>> listVersions(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::PageVersion> captureVersion(
        const models::Page& page,
        const std::string& label,
        const std::string& author = "system");
    [[nodiscard]] utils::Expected<models::PageVersion> createManualVersion(
        const std::string& pageId,
        const std::string& label,
        const std::string& author = "manual");
    [[nodiscard]] utils::Expected<models::Page> restoreVersion(
        const std::string& pageId,
        const std::string& versionId,
        const std::string& author = "restore");

    [[nodiscard]] utils::Expected<std::vector<models::CommentThread>> listThreads(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<std::vector<models::CommentThread>> listHistory(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::CommentThread> createThread(
        const std::string& pageId,
        const CommentThreadDraft& draft);
    [[nodiscard]] utils::Expected<models::CommentThread> addReply(
        const std::string& pageId,
        const std::string& threadId,
        const CommentReplyDraft& draft);
    [[nodiscard]] utils::Expected<models::CommentThread> setResolved(
        const std::string& pageId,
        const std::string& threadId,
        bool resolved,
        const std::string& actor = {});
    [[nodiscard]] utils::Expected<models::CommentThread> toggleLike(
        const std::string& pageId,
        const std::string& threadId,
        const std::string& actor);
    [[nodiscard]] utils::Expected<models::CommentThread> updateMessage(
        const std::string& pageId,
        const std::string& threadId,
        const std::string& messageId,
        const std::string& body,
        const std::string& actor);
    [[nodiscard]] utils::Expected<models::CommentThread> deleteMessage(
        const std::string& pageId,
        const std::string& threadId,
        const std::string& messageId,
        const std::string& actor);
    [[nodiscard]] utils::Expected<models::CommentThread> deleteThread(
        const std::string& pageId,
        const std::string& threadId,
        const std::string& actor);
    [[nodiscard]] utils::Expected<std::string> getCommentAccess(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<std::string> setCommentAccess(
        const std::string& pageId,
        const std::string& accessMode);

    [[nodiscard]] utils::VoidExpected deletePageData(const std::string& pageId);

private:
    [[nodiscard]] utils::Expected<void> ensurePageExists(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<CommentThreadDraft> validateThreadDraft(const CommentThreadDraft& draft) const;
    [[nodiscard]] utils::Expected<CommentReplyDraft> validateReplyDraft(const CommentReplyDraft& draft) const;
    [[nodiscard]] std::string nextId(const std::string& prefix);

    PageService& pageService_;
    storage::LocalCollaborationStorage& storage_;
    std::size_t nextIdCounter_ = 1;
};

}  // namespace wikilive::services
