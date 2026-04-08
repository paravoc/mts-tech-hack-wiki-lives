#pragma once

#include "src/utils/errors.h"

namespace wikilive::server {

class Router;

class HttpServer {
public:
    explicit HttpServer(Router& router);

    [[nodiscard]] utils::VoidExpected start(int port);
    void stop();

private:
    Router& router_;
    void* listenSocket_ = nullptr;
};

}  // namespace wikilive::server
