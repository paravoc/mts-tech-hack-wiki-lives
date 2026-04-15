#pragma once

#include <cstddef>
#include <memory>
#include <string>
#include <vector>

#include "src/ai/ai_service.h"
#include "src/api/mws_client.h"
#include "src/server/websocket_manager.h"
#include "src/services/auth_service.h"
#include "src/services/collaboration_service.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/storage/local_user_storage.h"
#include "src/utils/errors.h"
#include "src/services/project_service.h"
#include "src/security/access_evaluator.h"


namespace wikilive::server {

    struct MwsTablePreset {
        std::string key;
        std::string label;
        std::string tableId;
        std::string viewId;
        std::string role = "data";
    };

    struct RouteResponse {
        int statusCode = 200;
        std::string body;
        std::string contentType = "application/json; charset=utf-8";
    };

    class Router {
    public:
        Router(
            services::PageService& pageService,
            services::RenderService& renderService,
            services::ProjectService* projectService,
            ai::AiService* aiService,
            services::CollaborationService* collaborationService,
            WebSocketManager* webSocketManager,
            std::vector<MwsTablePreset> tablePresets);

        RouteResponse listProjects();
        RouteResponse listProjectsForActor(const std::string& actorId);
        RouteResponse listWorkspace(const std::string& actorId);
        RouteResponse createProject(const std::string& payload);
        RouteResponse getProject(const std::string& projectId, const std::string& actorId = {});
        RouteResponse setProjectAccess(const std::string& projectId, const std::string& payload);


        Router(
            services::PageService& pageService,
            services::RenderService& renderService,
            api::MwsClient* mwsClient,
            services::ProjectService* projectService,
            ai::AiService* aiService,
            services::CollaborationService* collaborationService,
            WebSocketManager* webSocketManager,
            std::vector<MwsTablePreset> tablePresets,
            std::unique_ptr<storage::LocalUserStorage> userStorage,
            services::AuthService* authService,
            std::string aiBaseUrl = {},
            std::string aiApiKey = {},
            std::string aiModel = {});

        RouteResponse downloadMwsAttachment(
            const std::string& tableId,
            const std::string& token,
            const std::string& path);

        [[nodiscard]] RouteResponse fixCommentText(const std::string& payload);
        [[nodiscard]] RouteResponse handleHealth() const;
        [[nodiscard]] RouteResponse listPages();
        [[nodiscard]] RouteResponse listPagesForActor(const std::string& actorId);
        [[nodiscard]] RouteResponse listPagesForProject(const std::string& projectId, const std::string& actorId = {});
        [[nodiscard]] RouteResponse getPage(const std::string& pageId, const std::string& actorId = {});
        [[nodiscard]] RouteResponse createPage(const std::string& payload);
        [[nodiscard]] RouteResponse updatePage(const std::string& pageId, const std::string& payload);
        [[nodiscard]] RouteResponse deletePage(const std::string& pageId);
        [[nodiscard]] RouteResponse getPageAccess(const std::string& pageId);
        [[nodiscard]] RouteResponse setPageAccess(const std::string& pageId, const std::string& payload);
        [[nodiscard]] RouteResponse listVersions(const std::string& pageId);
        [[nodiscard]] RouteResponse getVersion(const std::string& pageId, const std::string& versionId);
        [[nodiscard]] RouteResponse createVersion(const std::string& pageId, const std::string& payload);
        [[nodiscard]] RouteResponse restoreVersion(const std::string& pageId, const std::string& versionId);
        [[nodiscard]] RouteResponse listComments(const std::string& pageId);
        [[nodiscard]] RouteResponse listCommentHistory(const std::string& pageId);
        [[nodiscard]] RouteResponse createComment(const std::string& pageId, const std::string& payload);
        [[nodiscard]] RouteResponse replyToComment(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& payload);
        [[nodiscard]] RouteResponse resolveComment(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& payload);
        [[nodiscard]] RouteResponse pauseComment(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& payload);
        [[nodiscard]] RouteResponse toggleCommentLike(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& payload);
        [[nodiscard]] RouteResponse updateCommentMessage(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& messageId,
            const std::string& payload);
        [[nodiscard]] RouteResponse deleteCommentMessage(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& messageId,
            const std::string& payload);
        [[nodiscard]] RouteResponse deleteCommentThread(
            const std::string& pageId,
            const std::string& threadId,
            const std::string& payload);
        [[nodiscard]] RouteResponse getCommentAccess(const std::string& pageId);
        [[nodiscard]] RouteResponse setCommentAccess(const std::string& pageId, const std::string& payload);
        [[nodiscard]] RouteResponse listUsers();
        [[nodiscard]] RouteResponse listGroups();
        [[nodiscard]] RouteResponse login(const std::string& payload);
        [[nodiscard]] RouteResponse renderContent(const std::string& payload);
        [[nodiscard]] RouteResponse getMwsInsertOptions(
            const std::string& tableId = {},
            const std::string& viewId = {});
        [[nodiscard]] RouteResponse getMwsGrid(
            const std::string& tableId = {},
            const std::string& viewId = {},
            const std::string& recordIdsCsv = {},
            const std::string& fieldNamesCsv = {});
        [[nodiscard]] RouteResponse updateMwsGrid(const std::string& payload);
        [[nodiscard]] RouteResponse uploadAttachment(const std::string& payload);
        [[nodiscard]] RouteResponse suggestInsert(const std::string& payload);

    private:
        services::ProjectService* projectService_ = nullptr;
        std::string aiBaseUrl_;
        std::string aiApiKey_;
        std::string aiModel_;
        [[nodiscard]] RouteResponse ok(const std::string& dataJson) const;
        [[nodiscard]] RouteResponse fail(const utils::Error& error) const;
        [[nodiscard]] RouteResponse created(const std::string& dataJson) const;
        [[nodiscard]] utils::Expected<services::PageDraft> parsePagePayload(const std::string& payload) const;
        [[nodiscard]] utils::Expected<std::string> extractJsonString(
            const std::string& payload,
            const std::string& key,
            bool required = true) const;
        [[nodiscard]] utils::Expected<std::vector<std::string>> extractJsonStringArray(
            const std::string& payload,
            const std::string& key,
            bool required = false) const;
        [[nodiscard]] std::string aiSuggestInsertResultToJson(const ai::AiSuggestInsertResult& result) const;


        services::PageService& pageService_;
        services::RenderService& renderService_;
        api::MwsClient* mwsClient_ = nullptr;
        ai::AiService* aiService_ = nullptr;
        services::CollaborationService* collaborationService_ = nullptr;
        WebSocketManager* webSocketManager_ = nullptr;
        std::vector<MwsTablePreset> tablePresets_{};
        std::unique_ptr<storage::LocalUserStorage> userStorage_{};
        services::AuthService* authService_ = nullptr;
    };

}  // namespace wikilive::server
