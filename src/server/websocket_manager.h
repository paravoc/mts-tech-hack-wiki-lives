#pragma once

#include <string>

namespace wikilive::server {

class WebSocketManager {
public:
    void subscribeToPage(const std::string& pageId);
    void unsubscribeFromPage(const std::string& pageId);
    void broadcastPageUpdated(const std::string& pageId) const;
};

}  // namespace wikilive::server
