#pragma once

#include <cstddef>
#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>

#include "src/models/comment_thread.h"
#include "src/models/page_version.h"
#include "src/utils/errors.h"

namespace wikilive::storage {

class LocalCollaborationStorage {
public:
    explicit LocalCollaborationStorage(std::string storagePath, std::size_t maxVersionsPerPage = 50);

    [[nodiscard]] utils::Expected<std::vector<models::PageVersion>> listVersions(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::PageVersion> getVersion(
        const std::string& pageId,
        const std::string& versionId) const;
    [[nodiscard]] utils::VoidExpected appendVersion(const models::PageVersion& version);

    [[nodiscard]] utils::Expected<std::vector<models::CommentThread>> listThreads(const std::string& pageId) const;
    [[nodiscard]] utils::Expected<models::CommentThread> getThread(
        const std::string& pageId,
        const std::string& threadId) const;
    [[nodiscard]] utils::VoidExpected saveThread(const models::CommentThread& thread);
    [[nodiscard]] utils::Expected<std::string> getCommentAccess(const std::string& pageId) const;
    [[nodiscard]] utils::VoidExpected saveCommentAccess(const std::string& pageId, const std::string& accessMode);
    [[nodiscard]] utils::VoidExpected restoreCommentSnapshot(
        const std::string& pageId,
        const std::vector<models::CommentThread>& threads,
        const std::string& accessMode);

    [[nodiscard]] utils::VoidExpected deletePageData(const std::string& pageId);

private:
    struct State {
        std::vector<models::PageVersion> versions;
        std::vector<models::CommentThread> threads;
        std::unordered_map<std::string, std::string> commentAccessByPage;
    };

    [[nodiscard]] utils::Expected<State> loadStateUnlocked() const;
    [[nodiscard]] utils::VoidExpected persistStateUnlocked(const State& state) const;

    std::string storagePath_;
    std::size_t maxVersionsPerPage_ = 50;
    mutable std::mutex mutex_{};
};

}  // namespace wikilive::storage
