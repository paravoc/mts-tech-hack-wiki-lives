#include "src/server/websocket_manager.h"

#include <algorithm>
#include <vector>

#include <nlohmann/json.hpp>

namespace {

using json = nlohmann::json;

std::string buildMessage(const std::string& eventName, const std::string& pageId = {}, const std::string& status = "ok") {
    json payload = {
        {"event", eventName},
        {"status", status},
    };

    if (!pageId.empty()) {
        payload["pageId"] = pageId;
    }

    return payload.dump();
}

std::string normalizeActorField(const json& payload, const char* key, const std::string& fallback) {
    if (!payload.contains(key) || !payload[key].is_string()) {
        return fallback;
    }
    const auto value = payload[key].get<std::string>();
    return value.empty() ? fallback : value;
}

void applyActorPayload(wikilive::server::WebSocketSessionData* session, const json& payload) {
    if (session == nullptr) {
        return;
    }

    session->actorId = normalizeActorField(payload, "actorId", session->actorId.empty() ? "viewer" : session->actorId);
    session->actorName = normalizeActorField(payload, "actorName", session->actorName.empty() ? "Гость" : session->actorName);
    session->actorShort = normalizeActorField(payload, "actorShort", session->actorShort.empty() ? "Г" : session->actorShort);
    session->actorColor = normalizeActorField(payload, "actorColor", session->actorColor.empty() ? "#a6afbf" : session->actorColor);
}

}  // namespace

namespace wikilive::server {

void WebSocketManager::registerConnection(Socket* socket) {
    if (socket == nullptr) {
        return;
    }

    if (auto* userData = socket->getUserData(); userData != nullptr) {
        if (userData->actorId.empty()) {
            userData->actorId = "viewer";
        }
        if (userData->actorName.empty()) {
            userData->actorName = "Гость";
        }
        if (userData->actorShort.empty()) {
            userData->actorShort = "Г";
        }
        if (userData->actorColor.empty()) {
            userData->actorColor = "#a6afbf";
        }
    }
}

void WebSocketManager::unregisterConnection(Socket* socket) {
    if (socket == nullptr) {
        return;
    }

    std::vector<std::string> affectedPages;
    {
        std::scoped_lock lock(mutex_);
        for (auto& [pageId, subscribers] : pageSubscribers_) {
            if (subscribers.erase(socket) != 0) {
                affectedPages.push_back(pageId);
            }
        }

        auto* userData = socket->getUserData();
        if (userData != nullptr) {
            userData->pageSubscriptions.clear();
        }
    }

    for (const auto& pageId : affectedPages) {
        broadcastPresence(pageId);
    }
}

void WebSocketManager::subscribeToPage(Socket* socket, const std::string& pageId) {
    if (socket == nullptr || pageId.empty()) {
        return;
    }

    {
        std::scoped_lock lock(mutex_);
        pageSubscribers_[pageId].insert(socket);
        auto* userData = socket->getUserData();
        if (userData != nullptr) {
            userData->pageSubscriptions.insert(pageId);
        }
    }

    broadcastPresence(pageId);
}

void WebSocketManager::unsubscribeFromPage(Socket* socket, const std::string& pageId) {
    if (socket == nullptr || pageId.empty()) {
        return;
    }

    bool changed = false;
    {
        std::scoped_lock lock(mutex_);
        if (const auto it = pageSubscribers_.find(pageId); it != pageSubscribers_.end()) {
            changed = it->second.erase(socket) != 0;
            if (it->second.empty()) {
                pageSubscribers_.erase(it);
            }
        }

        auto* userData = socket->getUserData();
        if (userData != nullptr) {
            userData->pageSubscriptions.erase(pageId);
        }
    }

    if (changed) {
        broadcastPresence(pageId);
    }
}

std::string WebSocketManager::handleMessage(Socket* socket, std::string_view message) {
    if (socket == nullptr) {
        return buildMessage("error", {}, "invalid_socket");
    }

    try {
        const auto parsed = json::parse(message);
        const auto action = parsed.value("action", std::string{});
        const auto pageId = parsed.value("pageId", std::string{});

        applyActorPayload(socket->getUserData(), parsed);

        if (action == "subscribe") {
            subscribeToPage(socket, pageId);
            return buildMessage("subscribed", pageId);
        }

        if (action == "unsubscribe") {
            unsubscribeFromPage(socket, pageId);
            return buildMessage("unsubscribed", pageId);
        }

        if (action == "ping") {
            return buildMessage("pong");
        }

        return buildMessage("error", pageId, "unknown_action");
    } catch (...) {
        return buildMessage("error", {}, "invalid_json");
    }
}

void WebSocketManager::broadcastPageEvent(const std::string& pageId, const std::string& eventName) const {
    if (pageId.empty()) {
        return;
    }

    std::scoped_lock lock(mutex_);
    const auto it = pageSubscribers_.find(pageId);
    if (it == pageSubscribers_.end()) {
        return;
    }

    const auto payload = buildMessage(eventName, pageId);
    for (auto* socket : it->second) {
        if (socket != nullptr) {
            socket->send(payload, uWS::OpCode::TEXT);
        }
    }
}

std::string WebSocketManager::buildPresenceMessageUnlocked(const std::string& pageId) const {
    const auto it = pageSubscribers_.find(pageId);
    if (it == pageSubscribers_.end()) {
        return json{
            {"event", "presence.changed"},
            {"status", "ok"},
            {"pageId", pageId},
            {"count", 0},
            {"people", json::array()},
        }
            .dump();
    }

    std::unordered_set<std::string> seenActorIds;
    std::vector<json> people;
    people.reserve(it->second.size());
    for (auto* socket : it->second) {
        if (socket == nullptr) {
            continue;
        }
        const auto* session = socket->getUserData();
        if (session == nullptr) {
            continue;
        }

        const auto actorId = session->actorId.empty() ? "viewer" : session->actorId;
        if (!seenActorIds.insert(actorId).second) {
            continue;
        }

        people.push_back({
            {"actorId", actorId},
            {"actorName", session->actorName.empty() ? "Гость" : session->actorName},
            {"actorShort", session->actorShort.empty() ? "Г" : session->actorShort},
            {"actorColor", session->actorColor.empty() ? "#a6afbf" : session->actorColor},
        });
    }

    std::sort(people.begin(), people.end(), [](const json& left, const json& right) {
        return left.value("actorName", std::string{}) < right.value("actorName", std::string{});
    });

    return json{
        {"event", "presence.changed"},
        {"status", "ok"},
        {"pageId", pageId},
        {"count", people.size()},
        {"people", people},
    }
        .dump();
}

void WebSocketManager::broadcastPresence(const std::string& pageId) const {
    if (pageId.empty()) {
        return;
    }

    std::scoped_lock lock(mutex_);
    const auto it = pageSubscribers_.find(pageId);
    const auto payload = buildPresenceMessageUnlocked(pageId);
    if (it == pageSubscribers_.end()) {
        return;
    }

    for (auto* socket : it->second) {
        if (socket != nullptr) {
            socket->send(payload, uWS::OpCode::TEXT);
        }
    }
}

}  // namespace wikilive::server
