#pragma once

namespace wikilive::server {

class HttpServer {
public:
    bool start(int port);
    void stop();
};

}  // namespace wikilive::server
