#include "src/core/application.h"

#include <algorithm>
#include <filesystem>
#include <vector>

#include "config/config_loader.h"
#include "src/api/mws_client.h"
#include "src/server/http_server.h"
#include "src/server/router.h"
#include "src/server/websocket_manager.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "src/storage/mws_page_storage.h"
#include "src/utils/logger.h"

namespace wikilive::core {

namespace {

std::vector<std::string> configCandidates(const char* envPath) {
    std::vector<std::string> candidates;
    if (envPath != nullptr && *envPath != '\0') {
        candidates.emplace_back(envPath);
    }

    for (const auto& candidate : {
             std::string("out/build/x64-Debug/.env"),
             std::string("build/.env"),
             std::string("build-safe/.env"),
         }) {
        if (std::find(candidates.begin(), candidates.end(), candidate) == candidates.end()) {
            candidates.push_back(candidate);
        }
    }

    return candidates;
}

}  // namespace

Application::Application() = default;

Application::~Application() = default;

bool Application::initialize(const char* envPath) {
    config::ConfigLoader loader;
    bool configLoaded = false;
    for (const auto& candidate : configCandidates(envPath)) {
        if (!std::filesystem::exists(candidate)) {
            continue;
        }

        if (const auto loadResult = loader.loadFromFile(candidate); loadResult) {
            utils::Logger::instance().info("Loaded config from " + candidate);
            configLoaded = true;
            break;
        }
    }

    if (!configLoaded) {
        utils::Logger::instance().warn("Unable to locate .env file, continuing with environment defaults");
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

    mwsClient_ = std::make_unique<api::MwsClient>(
        config_.mwsToken,
        config_.mwsTableId,
        config_.mwsViewId,
        api::MwsClientOptions{
            .requestTimeoutMs = config_.requestTimeoutMs,
            .retryAttempts = config_.retryAttempts,
            .retryBaseDelayMs = config_.retryBaseDelayMs,
        });

    if (config_.enableWebSocket) {
        webSocketManager_ = std::make_unique<server::WebSocketManager>();
    }

    if (!config_.mwsToken.empty() && !config_.wikiPagesTableId.empty() && !config_.wikiPagesViewId.empty()) {
        wikiPagesClient_ = std::make_unique<api::MwsClient>(
            config_.mwsToken,
            config_.wikiPagesTableId,
            config_.wikiPagesViewId,
            api::MwsClientOptions{
                .requestTimeoutMs = config_.requestTimeoutMs,
                .retryAttempts = config_.retryAttempts,
                .retryBaseDelayMs = config_.retryBaseDelayMs,
            });
        pageStorage_ = std::make_unique<storage::MwsPageStorage>(*wikiPagesClient_);
        utils::Logger::instance().info("Wiki pages storage backend: MWS Tables");
    } else {
        pageStorage_ = std::make_unique<storage::InMemoryPageStorage>();
        utils::Logger::instance().warn("WikiPages configuration is incomplete, falling back to in-memory page storage");
    }

    pageService_ = std::make_unique<services::PageService>(*pageStorage_);
    renderService_ = std::make_unique<services::RenderService>(mwsClient_.get());
    router_ = std::make_unique<server::Router>(*pageService_, *renderService_, webSocketManager_.get());
    httpServer_ = std::make_unique<server::HttpServer>(*router_, webSocketManager_.get());

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
    wikiPagesClient_.reset();
    mwsClient_.reset();
    webSocketManager_.reset();
    initialized_ = false;
}

const AppConfig& Application::config() const {
    return config_;
}

}  // namespace wikilive::core
