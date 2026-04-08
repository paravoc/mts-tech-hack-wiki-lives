#pragma once

#include "src/utils/errors.h"

namespace wikilive::server {

class Router;
class WebSocketManager;

class HttpServer {
public:
    HttpServer(Router& router, WebSocketManager* webSocketManager = nullptr);

    [[nodiscard]] utils::VoidExpected start(int port);
    void stop();

private:
    Router& router_;
    WebSocketManager* webSocketManager_ = nullptr;
    void* listenSocket_ = nullptr;
};

}  // namespace wikilive::server
