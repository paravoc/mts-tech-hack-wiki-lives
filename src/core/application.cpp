#include "src/core/application.h"

#include <algorithm>
#include <cctype>
#include <filesystem>
#include <unordered_set>
#include <vector>

#include "config/config_loader.h"
#include "src/ai/ai_context_builder.h"
#include "src/ai/ai_field_verifier.h"
#include "src/ai/ai_provider_factory.h"
#include "src/ai/ai_service.h"
#include "src/ai/ai_suggestion_validator.h"
#include "src/api/mws_client.h"
#include "src/server/http_server.h"
#include "src/server/router.h"
#include "src/server/websocket_manager.h"
#include "src/services/collaboration_service.h"
#include "src/services/auth_service.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/in_memory_page_storage.h"
#include "src/storage/local_collaboration_storage.h"
#include "src/storage/local_file_page_storage.h"
#include "src/storage/local_file_project_storage.h"
#include "src/storage/local_user_storage.h"
#include "src/storage/mws_page_storage.h"
#include "src/utils/logger.h"

namespace wikilive::core {

namespace {

std::string normalizeKey(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

void ensureDefaultProjects(
    services::ProjectService& projectService,
    const std::vector<models::User>& users) {
    const auto projectsResult = projectService.listProjects();
    if (!projectsResult) {
        utils::Logger::instance().warn(
            "Failed to read projects for bootstrap: " + projectsResult.error().message);
        return;
    }

    std::unordered_set<std::string> existingOwners;
    for (const auto& project : projectsResult.value()) {
        if (!project.ownerId.empty()) {
            existingOwners.insert(normalizeKey(project.ownerId));
        }
    }

    for (const auto& user : users) {
        const std::string ownerId = user.id.empty() ? user.email : user.id;
        if (ownerId.empty()) {
            continue;
        }

        const auto ownerKey = normalizeKey(ownerId);
        const auto emailKey = normalizeKey(user.email);
        if (existingOwners.find(ownerKey) != existingOwners.end() ||
            (!emailKey.empty() && existingOwners.find(emailKey) != existingOwners.end())) {
            continue;
        }

        models::ProjectDraft draft;
        draft.name = user.name.empty() ? "Личный проект" : ("Проект " + user.name);
        draft.description = "Личная рабочая область";
        draft.ownerId = ownerId;
        draft.ownerName = user.name.empty() ? ownerId : user.name;
        draft.access.publicAccess = false;
        draft.access.userIds.push_back(ownerId);
        if (!user.email.empty() && user.email != ownerId) {
            draft.access.userIds.push_back(user.email);
        }

        const auto created = projectService.createProject(draft);
        if (!created) {
            utils::Logger::instance().warn(
                "Failed to create default project for " + ownerId + ": " + created.error().message);
            continue;
        }
        existingOwners.insert(ownerKey);
    }
}

std::vector<std::string> configCandidates(const char* envPath) {
    std::vector<std::string> candidates;
    if (envPath != nullptr && *envPath != '\0') {
        candidates.emplace_back(envPath);
    }

    for (const auto& candidate : {
             std::string(".env"),
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

    const auto localPagesPath = (std::filesystem::current_path() / "data" / "wikilive_pages.json").string();
    const auto localUsersPath = (std::filesystem::current_path() / "data" / "wikilive_users.json").string();
    const auto localProjectsPath = (std::filesystem::current_path() / "data" / "wikilive_projects.json").string();

    pageStorage_ = std::make_unique<storage::LocalFilePageStorage>(localPagesPath);
    if (!config_.wikiPagesTableId.empty() && !config_.wikiPagesViewId.empty()) {
        utils::Logger::instance().warn("WikiPages MWS storage is temporarily disabled for stable editing; local file storage is active");
    } else {
        utils::Logger::instance().warn("WikiPages configuration is incomplete, local file page storage is active");
    }

    pageService_ = std::make_unique<services::PageService>(*pageStorage_);
    collaborationStorage_ = std::make_unique<storage::LocalCollaborationStorage>(
        (std::filesystem::current_path() / "data" / "wikilive_collaboration.json").string());
    collaborationService_ = std::make_unique<services::CollaborationService>(*pageService_, *collaborationStorage_);
    renderService_ = std::make_unique<services::RenderService>(mwsClient_.get());
    projectStorage_ = std::make_unique<storage::LocalFileProjectStorage>(localProjectsPath);
    projectService_ = std::make_unique<services::ProjectService>(*projectStorage_);
    std::unique_ptr<ai::AiSuggestionValidator> aiSuggestionValidator;
    std::unique_ptr<ai::AiContextBuilder> aiContextBuilder;
    if (mwsClient_ != nullptr) {
        aiSuggestionValidator = std::make_unique<ai::AiSuggestionValidator>(
            std::make_unique<ai::MwsAiFieldVerifier>(*mwsClient_));
        aiContextBuilder = std::make_unique<ai::MwsAiContextBuilder>(*mwsClient_, config_.mwsTableId);
    } else {
        aiSuggestionValidator = std::make_unique<ai::AiSuggestionValidator>();
    }

    aiService_ = std::make_unique<ai::AiService>(
        ai::createAiProvider(config_),
        std::move(aiSuggestionValidator),
        std::move(aiContextBuilder));
    if (aiService_->isAvailable()) {
        const auto metadata = aiService_->metadata();
        utils::Logger::instance().info(
            "AI provider is configured: " + metadata.provider + " (" + metadata.model + ")");
    } else {
        utils::Logger::instance().info("AI provider is disabled");
    }

    std::vector<server::MwsTablePreset> tablePresets;
    if (!config_.mwsTableId.empty()) {
        tablePresets.push_back(server::MwsTablePreset{
            .key = "primary-data",
            .label = "Основная таблица данных",
            .tableId = config_.mwsTableId,
            .viewId = config_.mwsViewId,
            .role = "data",
        });
    }

    auto userStorage = std::make_unique<storage::LocalUserStorage>(localUsersPath);
    if (projectService_ != nullptr) {
        const auto usersResult = userStorage->listUsers();
        if (usersResult) {
            ensureDefaultProjects(*projectService_, usersResult.value());
        } else {
            utils::Logger::instance().warn(
                "Failed to load users for project bootstrap: " + usersResult.error().message);
        }
    }
    authService_ = std::make_unique<services::AuthService>(*userStorage);



    router_ = std::make_unique<server::Router>(
        *pageService_,
        *renderService_,
        mwsClient_.get(),
        projectService_.get(),
        aiService_.get(),
        collaborationService_.get(),
        webSocketManager_.get(),
        std::move(tablePresets),
        std::move(userStorage),
        authService_.get(),
        config_.aiBaseUrl,
        config_.aiApiKey,
        config_.aiModel);

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
    aiService_.reset();
    renderService_.reset();
    collaborationService_.reset();
    projectService_.reset();
    projectStorage_.reset();
    pageService_.reset();
    collaborationStorage_.reset();
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
