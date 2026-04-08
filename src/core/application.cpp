#include "src/core/application.h"

#include "config/config_loader.h"
#include "src/utils/logger.h"

namespace wikilive::core {

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

    initialized_ = true;
    return true;
}

int Application::run() {
    if (!initialized_) {
        return 1;
    }

    utils::Logger::instance().info("WikiLive backend skeleton started");
    return 0;
}

void Application::stop() {
    initialized_ = false;
}

const AppConfig& Application::config() const {
    return config_;
}

}  // namespace wikilive::core
