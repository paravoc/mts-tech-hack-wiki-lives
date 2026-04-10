#include "src/storage/local_collaboration_storage.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <unordered_map>
#include <utility>

#include <nlohmann/json.hpp>

namespace {

using json = nlohmann::json;

json toJson(const wikilive::models::PageVersion& version) {
    return {
        {"versionId", version.versionId},
        {"pageId", version.pageId},
        {"title", version.title},
        {"content", version.content},
        {"createdAt", version.createdAt},
        {"label", version.label},
        {"author", version.author},
    };
}

json toJson(const wikilive::models::CommentMessage& message) {
    return {
        {"messageId", message.messageId},
        {"author", message.author},
        {"body", message.body},
        {"createdAt", message.createdAt},
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
        {"selectionLabel", thread.selectionLabel},
        {"createdAt", thread.createdAt},
        {"updatedAt", thread.updatedAt},
        {"resolved", thread.resolved},
        {"likedBy", thread.likedBy},
        {"messages", messages},
    };
}

wikilive::models::PageVersion versionFromJson(const json& item) {
    return wikilive::models::PageVersion{
        .versionId = item.value("versionId", std::string{}),
        .pageId = item.value("pageId", std::string{}),
        .title = item.value("title", std::string{}),
        .content = item.value("content", std::string{}),
        .createdAt = item.value("createdAt", std::string{}),
        .label = item.value("label", std::string{}),
        .author = item.value("author", std::string{}),
    };
}

wikilive::models::CommentMessage commentMessageFromJson(const json& item) {
    return wikilive::models::CommentMessage{
        .messageId = item.value("messageId", std::string{}),
        .author = item.value("author", std::string{}),
        .body = item.value("body", std::string{}),
        .createdAt = item.value("createdAt", std::string{}),
    };
}

wikilive::models::CommentThread commentThreadFromJson(const json& item) {
    wikilive::models::CommentThread thread{
        .threadId = item.value("threadId", std::string{}),
        .pageId = item.value("pageId", std::string{}),
        .selectionLabel = item.value("selectionLabel", std::string{}),
        .createdAt = item.value("createdAt", std::string{}),
        .updatedAt = item.value("updatedAt", std::string{}),
        .resolved = item.value("resolved", false),
        .likedBy = item.value("likedBy", std::vector<std::string>{}),
    };

    if (item.contains("messages") && item["messages"].is_array()) {
        for (const auto& message : item["messages"]) {
            thread.messages.push_back(commentMessageFromJson(message));
        }
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
    for (const auto& version : state->versions) {
        if (version.pageId == pageId) {
            output.push_back(version);
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

    const auto it = std::find_if(state->versions.begin(), state->versions.end(), [&](const models::PageVersion& version) {
        return version.pageId == pageId && version.versionId == versionId;
    });
    if (it == state->versions.end()) {
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
    auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    state->versions.push_back(version);
    std::stable_sort(state->versions.begin(), state->versions.end(), [](const models::PageVersion& left, const models::PageVersion& right) {
        if (left.pageId == right.pageId) {
            return left.createdAt > right.createdAt;
        }
        return left.pageId < right.pageId;
    });

    std::vector<models::PageVersion> trimmed;
    trimmed.reserve(state->versions.size());
    std::unordered_map<std::string, std::size_t> perPageCount;
    for (const auto& item : state->versions) {
        auto& count = perPageCount[item.pageId];
        if (count >= maxVersionsPerPage_) {
            continue;
        }
        trimmed.push_back(item);
        ++count;
    }
    state->versions = std::move(trimmed);
    return persistStateUnlocked(*state);
}

utils::Expected<std::vector<models::CommentThread>> LocalCollaborationStorage::listThreads(const std::string& pageId) const {
    std::scoped_lock lock(mutex_);
    const auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    std::vector<models::CommentThread> output;
    for (const auto& thread : state->threads) {
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

    const auto it = std::find_if(state->threads.begin(), state->threads.end(), [&](const models::CommentThread& thread) {
        return thread.pageId == pageId && thread.threadId == threadId;
    });
    if (it == state->threads.end()) {
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
    auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    const auto it = std::find_if(state->threads.begin(), state->threads.end(), [&](const models::CommentThread& current) {
        return current.pageId == thread.pageId && current.threadId == thread.threadId;
    });

    if (it == state->threads.end()) {
        state->threads.push_back(thread);
    } else {
        *it = thread;
    }

    std::stable_sort(state->threads.begin(), state->threads.end(), [](const models::CommentThread& left, const models::CommentThread& right) {
        return left.updatedAt > right.updatedAt;
    });
    return persistStateUnlocked(*state);
}

utils::VoidExpected LocalCollaborationStorage::deletePageData(const std::string& pageId) {
    std::scoped_lock lock(mutex_);
    auto state = loadStateUnlocked();
    if (!state) {
        return std::unexpected(state.error());
    }

    state->versions.erase(
        std::remove_if(state->versions.begin(), state->versions.end(), [&](const models::PageVersion& item) {
            return item.pageId == pageId;
        }),
        state->versions.end());
    state->threads.erase(
        std::remove_if(state->threads.begin(), state->threads.end(), [&](const models::CommentThread& item) {
            return item.pageId == pageId;
        }),
        state->threads.end());

    return persistStateUnlocked(*state);
}

utils::Expected<LocalCollaborationStorage::State> LocalCollaborationStorage::loadStateUnlocked() const {
    if (storagePath_.empty()) {
        return State{};
    }

    if (!std::filesystem::exists(storagePath_)) {
        return State{};
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

    return state;
}

utils::VoidExpected LocalCollaborationStorage::persistStateUnlocked(const State& state) const {
    if (storagePath_.empty()) {
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
        };
        for (const auto& version : state.versions) {
            root["versions"].push_back(toJson(version));
        }
        for (const auto& thread : state.threads) {
            root["threads"].push_back(toJson(thread));
        }

        std::ofstream stream(storagePath_, std::ios::binary | std::ios::trunc);
        if (!stream.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to write collaboration storage: " + storagePath_,
                500,
                true));
        }

        stream << root.dump(2);
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
