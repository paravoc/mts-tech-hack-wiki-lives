#include "src/server/websocket_manager.h"

namespace wikilive::server {

void WebSocketManager::subscribeToPage(const std::string& pageId) {
    (void)pageId;
}

void WebSocketManager::unsubscribeFromPage(const std::string& pageId) {
    (void)pageId;
}

void WebSocketManager::broadcastPageUpdated(const std::string& pageId) const {
    (void)pageId;
}

}  // namespace wikilive::server
