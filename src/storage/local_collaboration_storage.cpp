#include "src/storage/local_collaboration_storage.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <unordered_map>
#include <utility>

#include <nlohmann/json.hpp>

namespace {

using json = nlohmann::json;

json toJson(const wikilive::models::CommentThread& thread);
wikilive::models::CommentThread commentThreadFromJson(const json& item);

json toJson(const wikilive::models::PageVersion& version) {
    json threads = json::array();
    for (const auto& thread : version.threadSnapshot) {
        threads.push_back(toJson(thread));
    }

    return {
        {"versionId", version.versionId},
        {"pageId", version.pageId},
        {"projectId", version.projectId},
        {"title", version.title},
        {"description", version.description},
        {"content", version.content},
        {"createdAt", version.createdAt},
        {"label", version.label},
        {"author", version.author},
        {"sharedWith", version.sharedWith},
        {"access", {
            {"public", version.access.publicAccess},
            {"users", version.access.userIds},
            {"groups", version.access.groupIds},
            {"roles", version.access.roles},
        }},
        {"threadSnapshot", threads},
        {"commentAccessMode", version.commentAccessMode},
        {"threadCount", version.threadCount},
        {"commentCount", version.commentCount},
    };
}

json toJson(const wikilive::models::CommentMessage& message) {
    return {
        {"messageId", message.messageId},
        {"author", message.author},
        {"body", message.body},
        {"createdAt", message.createdAt},
        {"updatedAt", message.updatedAt},
        {"replyToMessageId", message.replyToMessageId},
        {"deleted", message.deleted},
        {"likedBy", message.likedBy},
    };
}

json toJson(const wikilive::models::CommentThread& thread) {
    json messages = json::array();
    for (const auto& message : thread.messages) {
        messages.push_back(toJson(message));
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
        {"messages", messages},
    };
}

wikilive::models::PageVersion versionFromJson(const json& item) {
    wikilive::models::PageVersion version{
        .versionId = item.value("versionId", std::string{}),
        .pageId = item.value("pageId", std::string{}),
        .projectId = item.value("projectId", std::string{}),
        .title = item.value("title", std::string{}),
        .description = item.value("description", std::string{}),
        .content = item.value("content", std::string{}),
        .createdAt = item.value("createdAt", std::string{}),
        .label = item.value("label", std::string{}),
        .author = item.value("author", std::string{}),
        .sharedWith = item.value("sharedWith", std::vector<std::string>{}),
        .access = {},
        .commentAccessMode = item.value("commentAccessMode", std::string{"all_users"}),
    };

    if (item.contains("access") && item["access"].is_object()) {
        const auto& access = item["access"];
        version.access.publicAccess = access.value("public", false);
        if (access.contains("users") && access["users"].is_array()) {
            for (const auto& value : access["users"]) {
                if (value.is_string()) {
                    version.access.userIds.push_back(value.get<std::string>());
                }
            }
        }
        if (access.contains("groups") && access["groups"].is_array()) {
            for (const auto& value : access["groups"]) {
                if (value.is_string()) {
                    version.access.groupIds.push_back(value.get<std::string>());
                }
            }
        }
        if (access.contains("roles") && access["roles"].is_array()) {
            for (const auto& value : access["roles"]) {
                if (value.is_string()) {
                    version.access.roles.push_back(value.get<std::string>());
                }
            }
        }
    }

    if (item.contains("threadSnapshot") && item["threadSnapshot"].is_array()) {
        for (const auto& threadItem : item["threadSnapshot"]) {
            version.threadSnapshot.push_back(commentThreadFromJson(threadItem));
        }
    }

    if (item.contains("threadCount")) {
        version.threadCount = item.value("threadCount", static_cast<std::size_t>(0));
    }
    if (item.contains("commentCount")) {
        version.commentCount = item.value("commentCount", static_cast<std::size_t>(0));
    }

    if (version.threadCount == 0 && !version.threadSnapshot.empty()) {
        version.threadCount = version.threadSnapshot.size();
    }
    if (version.commentCount == 0 && !version.threadSnapshot.empty()) {
        for (const auto& thread : version.threadSnapshot) {
            version.commentCount += thread.messages.size();
        }
    }

    return version;
}

wikilive::models::CommentMessage commentMessageFromJson(const json& item) {
    return wikilive::models::CommentMessage{
        .messageId = item.value("messageId", std::string{}),
        .author = item.value("author", std::string{}),
        .body = item.value("body", std::string{}),
        .createdAt = item.value("createdAt", std::string{}),
        .updatedAt = item.value("updatedAt", std::string{}),
        .replyToMessageId = item.value("replyToMessageId", std::string{}),
        .deleted = item.value("deleted", false),
        .likedBy = item.value("likedBy", std::vector<std::string>{}),
    };
}

wikilive::models::CommentThread commentThreadFromJson(const json& item) {
    wikilive::models::CommentThread thread{
        .threadId = item.value("threadId", std::string{}),
        .pageId = item.value("pageId", std::string{}),
        .targetId = item.value("targetId", std::string{}),
        .targetType = item.value("targetType", std::string{}),
        .selectionLabel = item.value("selectionLabel", std::string{}),
        .targetPreview = item.value("targetPreview", std::string{}),
        .anchor = {},
        .createdAt = item.value("createdAt", std::string{}),
        .updatedAt = item.value("updatedAt", std::string{}),
        .resolved = item.value("resolved", false),
        .resolvedAt = item.value("resolvedAt", std::string{}),
        .resolvedBy = item.value("resolvedBy", std::string{}),
        .paused = item.value("paused", false),
        .pausedAt = item.value("pausedAt", std::string{}),
        .pausedBy = item.value("pausedBy", std::string{}),
        .deleted = item.value("deleted", false),
        .deletedAt = item.value("deletedAt", std::string{}),
        .deletedBy = item.value("deletedBy", std::string{}),
        .likedBy = item.value("likedBy", std::vector<std::string>{}),
    };

    if (item.contains("anchor") && item["anchor"].is_object()) {
        const auto& anchor = item["anchor"];
        thread.anchor.anchorId = anchor.value("anchorId", std::string{});
        thread.anchor.quote = anchor.value("quote", std::string{});
        thread.anchor.selector = anchor.value("selector", std::string{});
        thread.anchor.blockId = anchor.value("blockId", std::string{});
        thread.anchor.blockType = anchor.value("blockType", std::string{});
        thread.anchor.startOffset = anchor.value("startOffset", -1);
        thread.anchor.endOffset = anchor.value("endOffset", -1);
    }

    if (item.contains("messages") && item["messages"].is_array()) {
        for (const auto& message : item["messages"]) {
            thread.messages.push_back(commentMessageFromJson(message));
        }
    }

    if (!thread.messages.empty() && thread.messages.front().likedBy.empty() && !thread.likedBy.empty()) {
        thread.messages.front().likedBy = thread.likedBy;
    }

    return thread;
}

}  // namespace

namespace wikilive::storage {

LocalCollaborationStorage::LocalCollaborationStorage(std::string storagePath, const std::size_t maxVersionsPerPage)
    : storagePath_(std::move(storagePath)),
      maxVersionsPerPage_(maxVersionsPerPage == 0 ? 50 : maxVersionsPerPage) {
}

utils::Expected<std::vector<models::PageVersion>> LocalCollaborationStorage::listVersions(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    std::vector<models::PageVersion> output;
    for (const auto& version : (*state)->versions) {
        if (version.pageId == pageId) {
            auto summary = version;
            if (summary.threadCount == 0 && !summary.threadSnapshot.empty()) {
                summary.threadCount = summary.threadSnapshot.size();
            }
            if (summary.commentCount == 0 && !summary.threadSnapshot.empty()) {
                for (const auto& thread : summary.threadSnapshot) {
                    summary.commentCount += thread.messages.size();
                }
            }

            summary.content.clear();
            summary.threadSnapshot.clear();
            output.push_back(std::move(summary));
        }
    }
    return output;
}

utils::Expected<models::PageVersion> LocalCollaborationStorage::getVersion(
    const std::string& pageId,
    const std::string& versionId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    const auto it = std::find_if((*state)->versions.begin(), (*state)->versions.end(), [&](const models::PageVersion& version) {
        return version.pageId == pageId && version.versionId == versionId;
    });
    if (it == (*state)->versions.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Page version not found: " + versionId,
            404,
            false));
    }

    return *it;
}

utils::VoidExpected LocalCollaborationStorage::appendVersion(const models::PageVersion& version) {
    std::scoped_lock lock(mutex_);
    auto state = loadMutableStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    (*state)->versions.push_back(version);
    std::stable_sort((*state)->versions.begin(), (*state)->versions.end(), [](const models::PageVersion& left, const models::PageVersion& right) {
        if (left.pageId == right.pageId) {
            return left.createdAt > right.createdAt;
        }
        return left.pageId < right.pageId;
    });

    std::vector<models::PageVersion> trimmed;
    trimmed.reserve((*state)->versions.size());
    std::unordered_map<std::string, std::size_t> perPageCount;
    for (const auto& item : (*state)->versions) {
        auto& count = perPageCount[item.pageId];
        if (count >= maxVersionsPerPage_) {
            continue;
        }
        trimmed.push_back(item);
        ++count;
    }
    (*state)->versions = std::move(trimmed);
    return persistStateUnlocked(**state);
}

utils::Expected<std::vector<models::CommentThread>> LocalCollaborationStorage::listThreads(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    std::vector<models::CommentThread> output;
    for (const auto& thread : (*state)->threads) {
        if (thread.pageId == pageId) {
            output.push_back(thread);
        }
    }
    return output;
}

utils::Expected<models::CommentThread> LocalCollaborationStorage::getThread(
    const std::string& pageId,
    const std::string& threadId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    const auto it = std::find_if((*state)->threads.begin(), (*state)->threads.end(), [&](const models::CommentThread& thread) {
        return thread.pageId == pageId && thread.threadId == threadId;
    });
    if (it == (*state)->threads.end()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Comment thread not found: " + threadId,
            404,
            false));
    }

    return *it;
}

utils::VoidExpected LocalCollaborationStorage::saveThread(const models::CommentThread& thread) {
    std::scoped_lock lock(mutex_);
    auto state = loadMutableStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    const auto it = std::find_if((*state)->threads.begin(), (*state)->threads.end(), [&](const models::CommentThread& current) {
        return current.pageId == thread.pageId && current.threadId == thread.threadId;
    });

    if (it == (*state)->threads.end()) {
        (*state)->threads.push_back(thread);
    } else {
        *it = thread;
    }

    std::stable_sort((*state)->threads.begin(), (*state)->threads.end(), [](const models::CommentThread& left, const models::CommentThread& right) {
        return left.updatedAt > right.updatedAt;
    });
    return persistStateUnlocked(**state);
}

utils::Expected<std::string> LocalCollaborationStorage::getCommentAccess(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    const auto it = (*state)->commentAccessByPage.find(pageId);
    if (it == (*state)->commentAccessByPage.end()) {
        return std::string("all_users");
    }
    return it->second;
}

utils::VoidExpected LocalCollaborationStorage::saveCommentAccess(const std::string& pageId, const std::string& accessMode) {
    std::scoped_lock lock(mutex_);
    auto state = loadMutableStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    (*state)->commentAccessByPage[pageId] = accessMode;
    return persistStateUnlocked(**state);
}

utils::VoidExpected LocalCollaborationStorage::restoreCommentSnapshot(
    const std::string& pageId,
    const std::vector<models::CommentThread>& threads,
    const std::string& accessMode) {
    std::scoped_lock lock(mutex_);
    auto state = loadMutableStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    (*state)->threads.erase(
        std::remove_if((*state)->threads.begin(), (*state)->threads.end(), [&](const models::CommentThread& item) {
            return item.pageId == pageId;
        }),
        (*state)->threads.end());

    for (const auto& thread : threads) {
        (*state)->threads.push_back(thread);
    }

    std::stable_sort((*state)->threads.begin(), (*state)->threads.end(), [](const models::CommentThread& left, const models::CommentThread& right) {
        return left.updatedAt > right.updatedAt;
    });

    (*state)->commentAccessByPage[pageId] = accessMode.empty() ? "all_users" : accessMode;
    return persistStateUnlocked(**state);
}

utils::VoidExpected LocalCollaborationStorage::deletePageData(const std::string& pageId) {
    std::scoped_lock lock(mutex_);
    auto state = loadMutableStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    (*state)->versions.erase(
        std::remove_if((*state)->versions.begin(), (*state)->versions.end(), [&](const models::PageVersion& item) {
            return item.pageId == pageId;
        }),
        (*state)->versions.end());
    (*state)->threads.erase(
        std::remove_if((*state)->threads.begin(), (*state)->threads.end(), [&](const models::CommentThread& item) {
            return item.pageId == pageId;
        }),
        (*state)->threads.end());
    (*state)->commentAccessByPage.erase(pageId);

    return persistStateUnlocked(**state);
}

utils::Expected<const LocalCollaborationStorage::State*> LocalCollaborationStorage::loadStateUnlocked() const {
    if (storagePath_.empty()) {
        if (!cacheLoaded_) {
            cachedState_ = State{};
            cacheLoaded_ = true;
            cacheHasWriteTime_ = false;
        }
        return &*cachedState_;
    }

    const auto path = std::filesystem::path(storagePath_);
    if (!std::filesystem::exists(path)) {
        if (!cacheLoaded_) {
            cachedState_ = State{};
            cacheLoaded_ = true;
        }
        cacheHasWriteTime_ = false;
        return &*cachedState_;
    }

    const auto currentWriteTime = std::filesystem::last_write_time(path);
    if (cacheLoaded_ && cacheHasWriteTime_ && currentWriteTime == cachedWriteTime_ && cachedState_.has_value()) {
        return &*cachedState_;
    }

    std::ifstream stream(storagePath_, std::ios::binary);
    if (!stream.is_open()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            "Failed to open collaboration storage: " + storagePath_,
            500,
            true));
    }

    json root;
    try {
        stream >> root;
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Failed to parse collaboration storage: ") + exception.what(),
            500,
            false));
    }

    State state;
    if (root.contains("versions") && root["versions"].is_array()) {
        for (const auto& item : root["versions"]) {
            state.versions.push_back(versionFromJson(item));
        }
    }
    if (root.contains("threads") && root["threads"].is_array()) {
        for (const auto& item : root["threads"]) {
            state.threads.push_back(commentThreadFromJson(item));
        }
    }
    if (root.contains("commentAccess") && root["commentAccess"].is_object()) {
        for (auto it = root["commentAccess"].begin(); it != root["commentAccess"].end(); ++it) {
            state.commentAccessByPage[it.key()] = it.value().get<std::string>();
        }
    }

    cachedState_ = std::move(state);
    cachedWriteTime_ = currentWriteTime;
    cacheLoaded_ = true;
    cacheHasWriteTime_ = true;
    return &*cachedState_;
}

utils::Expected<LocalCollaborationStorage::State*> LocalCollaborationStorage::loadMutableStateUnlocked() {
    const auto state = static_cast<const LocalCollaborationStorage*>(this)->loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }
    return const_cast<State*>(state.value());
}

utils::VoidExpected LocalCollaborationStorage::persistStateUnlocked(const State& state) const {
    if (storagePath_.empty()) {
        cachedState_ = state;
        cacheLoaded_ = true;
        cacheHasWriteTime_ = false;
        return {};
    }

    try {
        const auto path = std::filesystem::path(storagePath_);
        if (path.has_parent_path()) {
            std::filesystem::create_directories(path.parent_path());
        }

        json root = {
            {"versions", json::array()},
            {"threads", json::array()},
            {"commentAccess", json::object()},
        };
        for (const auto& version : state.versions) {
            root["versions"].push_back(toJson(version));
        }
        for (const auto& thread : state.threads) {
            root["threads"].push_back(toJson(thread));
        }
        for (const auto& [pageId, accessMode] : state.commentAccessByPage) {
            root["commentAccess"][pageId] = accessMode;
        }

        std::ofstream stream(storagePath_, std::ios::binary | std::ios::trunc);
        if (!stream.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to write collaboration storage: " + storagePath_,
                500,
                true));
        }

        stream << root.dump(2, ' ', false, json::error_handler_t::replace);
        stream.flush();
        cachedState_ = state;
        cacheLoaded_ = true;
        if (std::filesystem::exists(path)) {
            cachedWriteTime_ = std::filesystem::last_write_time(path);
            cacheHasWriteTime_ = true;
        } else {
            cacheHasWriteTime_ = false;
        }
        return {};
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Failed to persist collaboration storage: ") + exception.what(),
            500,
            true));
    }
}

}  // namespace wikilive::storage
