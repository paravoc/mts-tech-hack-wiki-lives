#include "src/core/app_config.h"

#include "config/config_loader.h"
#include "config/constants.h"
#include "src/utils/errors.h"

namespace {

int toInt(const std::string& value, const int fallback) {
    if (value.empty()) {
        return fallback;
    }

    try {
        return std::stoi(value);
    } catch (...) {
        return fallback;
    }
}

bool toBool(const std::string& value, const bool fallback) {
    if (value == "true" || value == "1") {
        return true;
    }
    if (value == "false" || value == "0") {
        return false;
    }
    return fallback;
}

}  // namespace

namespace wikilive::core {

AppConfig loadAppConfig(const config::ConfigLoader& loader) {
    AppConfig config;
    config.mwsToken = loader.get("MWS_TOKEN");
    config.mwsTableId = loader.get("MWS_TABLE_ID");
    config.mwsViewId = loader.get("MWS_VIEW_ID");
    config.wikiPagesTableId = loader.get("WIKI_PAGES_TABLE_ID");
    config.wikiPagesViewId = loader.get("WIKI_PAGES_VIEW_ID");
    config.aiProvider = loader.get("AI_PROVIDER", "none");
    config.aiBaseUrl = loader.get("AI_BASE_URL");
    config.aiApiKey = loader.get("AI_API_KEY");
    config.aiModel = loader.get("AI_MODEL");
    config.logLevel = loader.get("LOG_LEVEL", "info");
    config.httpPort = toInt(loader.get("HTTP_PORT"), config::kDefaultHttpPort);
    config.cacheTtlSeconds = toInt(loader.get("CACHE_TTL_SECONDS"), config::kDefaultCacheTtlSeconds);
    config.requestTimeoutMs = toInt(loader.get("REQUEST_TIMEOUT_MS"), 10000);
    config.retryAttempts = toInt(loader.get("RETRY_ATTEMPTS"), config::kDefaultRetryCount);
    config.retryBaseDelayMs = toInt(loader.get("RETRY_BASE_DELAY_MS"), 1000);
    config.wsHeartbeatSeconds = toInt(loader.get("WS_HEARTBEAT_SECONDS"), 20);
    config.enableWebSocket = toBool(loader.get("ENABLE_WEBSOCKET"), true);
    config.enableAi = toBool(loader.get("ENABLE_AI"), false);
    return config;
}

utils::VoidExpected validateAppConfig(const AppConfig& config) {
    if (config.httpPort <= 0 || config.httpPort > 65535) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "HTTP_PORT must be in range 1..65535",
            500,
            false));
    }

    if (config.cacheTtlSeconds < 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "CACHE_TTL_SECONDS must be non-negative",
            500,
            false));
    }

    if (config.requestTimeoutMs <= 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "REQUEST_TIMEOUT_MS must be positive",
            500,
            false));
    }

    if (config.retryAttempts <= 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "RETRY_ATTEMPTS must be positive",
            500,
            false));
    }

    if (config.retryBaseDelayMs < 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "RETRY_BASE_DELAY_MS must be non-negative",
            500,
            false));
    }

    if (config.wsHeartbeatSeconds <= 0) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "WS_HEARTBEAT_SECONDS must be positive",
            500,
            false));
    }

    if (config.enableAi) {
        if (config.aiProvider.empty() || config.aiProvider == "none") {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "ENABLE_AI=true requires AI_PROVIDER to be set",
                500,
                false));
        }

        if (config.aiModel.empty()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "ENABLE_AI=true requires AI_MODEL to be set",
                500,
                false));
        }

        if (config.aiProvider == "openrouter" && config.aiApiKey.empty()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "AI_PROVIDER=openrouter requires AI_API_KEY to be set",
                500,
                false));
        }
    }

    return {};
}

}  // namespace wikilive::core
