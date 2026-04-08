#include "src/server/websocket_manager.h"

#include <nlohmann/json.hpp>

#include "src/utils/string_utils.h"

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

}  // namespace

namespace wikilive::server {

void WebSocketManager::registerConnection(Socket* socket) {
    (void)socket;
}

void WebSocketManager::unregisterConnection(Socket* socket) {
    if (socket == nullptr) {
        return;
    }

    std::scoped_lock lock(mutex_);
    for (auto& [pageId, subscribers] : pageSubscribers_) {
        (void)pageId;
        subscribers.erase(socket);
    }

    auto* userData = socket->getUserData();
    if (userData != nullptr) {
        userData->pageSubscriptions.clear();
    }
}

void WebSocketManager::subscribeToPage(Socket* socket, const std::string& pageId) {
    if (socket == nullptr || pageId.empty()) {
        return;
    }

    std::scoped_lock lock(mutex_);
    pageSubscribers_[pageId].insert(socket);
    auto* userData = socket->getUserData();
    if (userData != nullptr) {
        userData->pageSubscriptions.insert(pageId);
    }
}

void WebSocketManager::unsubscribeFromPage(Socket* socket, const std::string& pageId) {
    if (socket == nullptr || pageId.empty()) {
        return;
    }

    std::scoped_lock lock(mutex_);
    if (const auto it = pageSubscribers_.find(pageId); it != pageSubscribers_.end()) {
        it->second.erase(socket);
        if (it->second.empty()) {
            pageSubscribers_.erase(it);
        }
    }

    auto* userData = socket->getUserData();
    if (userData != nullptr) {
        userData->pageSubscriptions.erase(pageId);
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

}  // namespace wikilive::server
