#pragma once

#include <mutex>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>

#include "uwebsockets/App.h"

namespace wikilive::server {

struct WebSocketSessionData {
    std::unordered_set<std::string> pageSubscriptions;
    std::string actorId = "viewer";
    std::string actorName = "Гость";
    std::string actorShort = "Г";
    std::string actorColor = "#a6afbf";
};

class WebSocketManager {
public:
    using Socket = uWS::WebSocket<false, true, WebSocketSessionData>;

    void registerConnection(Socket* socket);
    void unregisterConnection(Socket* socket);
    void subscribeToPage(Socket* socket, const std::string& pageId);
    void unsubscribeFromPage(Socket* socket, const std::string& pageId);
    [[nodiscard]] std::string handleMessage(Socket* socket, std::string_view message);
    void broadcastPageEvent(const std::string& pageId, const std::string& eventName) const;

private:
    [[nodiscard]] std::string buildPresenceMessageUnlocked(const std::string& pageId) const;
    void broadcastPresence(const std::string& pageId) const;

    mutable std::mutex mutex_{};
    std::unordered_map<std::string, std::unordered_set<Socket*>> pageSubscribers_{};
};

}  // namespace wikilive::server
