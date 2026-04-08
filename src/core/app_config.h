#pragma once

#include <string>

#include "src/utils/errors.h"

namespace wikilive::config {
class ConfigLoader;
}

namespace wikilive::core {

struct AppConfig {
    std::string mwsToken;
    std::string mwsTableId;
    std::string mwsViewId;
    std::string wikiPagesTableId;
    std::string wikiPagesViewId;
    std::string aiProvider = "none";
    std::string aiBaseUrl;
    std::string aiApiKey;
    std::string aiModel;
    std::string logLevel = "info";
    int httpPort = 3000;
    int cacheTtlSeconds = 60;
    int requestTimeoutMs = 10000;
    int retryAttempts = 3;
    int retryBaseDelayMs = 1000;
    int wsHeartbeatSeconds = 20;
    bool enableWebSocket = true;
    bool enableAi = false;
};

AppConfig loadAppConfig(const config::ConfigLoader& loader);
utils::VoidExpected validateAppConfig(const AppConfig& config);

}  // namespace wikilive::core
