#pragma once

#include <memory>

#include "src/core/app_config.h"

namespace wikilive::server {
class HttpServer;
class Router;
class WebSocketManager;
}

namespace wikilive::api {
class MwsClient;
}

namespace wikilive::ai {
class AiService;
}

namespace wikilive::services {
class PageService;
class RenderService;
}

namespace wikilive::storage {
class PageStorage;
}

namespace wikilive::core {

class Application {
public:
    Application();
    ~Application();

    bool initialize(const char* envPath = ".env");
    int run();
    void stop();

    [[nodiscard]] const AppConfig& config() const;

private:
    AppConfig config_{};
    bool initialized_ = false;
    std::unique_ptr<api::MwsClient> mwsClient_{};
    std::unique_ptr<api::MwsClient> wikiPagesClient_{};
    std::unique_ptr<storage::PageStorage> pageStorage_{};
    std::unique_ptr<services::PageService> pageService_{};
    std::unique_ptr<services::RenderService> renderService_{};
    std::unique_ptr<ai::AiService> aiService_{};
    std::unique_ptr<server::WebSocketManager> webSocketManager_{};
    std::unique_ptr<server::Router> router_{};
    std::unique_ptr<server::HttpServer> httpServer_{};
};

}  // namespace wikilive::core
