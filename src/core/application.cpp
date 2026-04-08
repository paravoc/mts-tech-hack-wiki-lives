#include "src/core/application.h"

#include "config/config_loader.h"
#include "src/server/http_server.h"
#include "src/server/router.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "src/utils/logger.h"

namespace wikilive::core {

Application::Application() = default;

Application::~Application() = default;

bool Application::initialize(const char* envPath) {
    config::ConfigLoader loader;
    if (const auto loadResult = loader.loadFromFile(envPath); !loadResult) {
        utils::Logger::instance().warn(loadResult.error().message);
    }

    config_ = loadAppConfig(loader);
    utils::Logger::instance().setLevel(config_.logLevel);

    if (const auto validationResult = validateAppConfig(config_); !validationResult) {
        utils::Logger::instance().error(validationResult.error().message);
        return false;
    }

    if (config_.mwsToken.empty()) {
        utils::Logger::instance().warn("MWS_TOKEN is empty, MWS-backed endpoints are not ready yet");
    }

    pageStorage_ = std::make_unique<storage::InMemoryPageStorage>();
    pageService_ = std::make_unique<services::PageService>(*pageStorage_);
    renderService_ = std::make_unique<services::RenderService>();
    router_ = std::make_unique<server::Router>(*pageService_, *renderService_);
    httpServer_ = std::make_unique<server::HttpServer>(*router_);

    initialized_ = true;
    return true;
}

int Application::run() {
    if (!initialized_) {
        return 1;
    }

    const auto startResult = httpServer_->start(config_.httpPort);
    if (!startResult) {
        utils::Logger::instance().error(startResult.error().message);
        return 1;
    }

    return 0;
}

void Application::stop() {
    if (httpServer_) {
        httpServer_->stop();
    }

    router_.reset();
    renderService_.reset();
    pageService_.reset();
    pageStorage_.reset();
    initialized_ = false;
}

const AppConfig& Application::config() const {
    return config_;
}

}  // namespace wikilive::core
