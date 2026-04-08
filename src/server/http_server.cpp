#include "src/server/http_server.h"

namespace wikilive::server {

bool HttpServer::start(const int port) {
    (void)port;
    return true;
}

void HttpServer::stop() {
}

}  // namespace wikilive::server
