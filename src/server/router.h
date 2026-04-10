#pragma once

#include <cstddef>
#include <string>
#include <vector>

#include "src/ai/ai_service.h"
#include "src/api/mws_client.h"
#include "src/server/websocket_manager.h"
#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/utils/errors.h"

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
};

class Router {
public:
    Router(
        services::PageService& pageService,
        services::RenderService& renderService,
        ai::AiService* aiService,
        WebSocketManager* webSocketManager = nullptr,
        std::vector<MwsTablePreset> tablePresets = {});
    Router(
        services::PageService& pageService,
        services::RenderService& renderService,
        api::MwsClient* mwsClient = nullptr,
        ai::AiService* aiService = nullptr,
        WebSocketManager* webSocketManager = nullptr,
        std::vector<MwsTablePreset> tablePresets = {});

    [[nodiscard]] RouteResponse handleHealth() const;
    [[nodiscard]] RouteResponse listPages();
    [[nodiscard]] RouteResponse getPage(const std::string& pageId);
    [[nodiscard]] RouteResponse createPage(const std::string& payload);
    [[nodiscard]] RouteResponse updatePage(const std::string& pageId, const std::string& payload);
    [[nodiscard]] RouteResponse deletePage(const std::string& pageId);
    [[nodiscard]] RouteResponse renderContent(const std::string& payload);
    [[nodiscard]] RouteResponse getMwsInsertOptions(
        const std::string& tableId = {},
        const std::string& viewId = {});
    [[nodiscard]] RouteResponse suggestInsert(const std::string& payload);

private:
    [[nodiscard]] RouteResponse ok(const std::string& dataJson) const;
    [[nodiscard]] RouteResponse fail(const utils::Error& error) const;
    [[nodiscard]] RouteResponse created(const std::string& dataJson) const;
    [[nodiscard]] utils::Expected<services::PageDraft> parsePagePayload(const std::string& payload) const;
    [[nodiscard]] utils::Expected<std::string> extractJsonString(
        const std::string& payload,
        const std::string& key,
        bool required = true) const;
    [[nodiscard]] std::string aiSuggestInsertResultToJson(const ai::AiSuggestInsertResult& result) const;

    services::PageService& pageService_;
    services::RenderService& renderService_;
    api::MwsClient* mwsClient_ = nullptr;
    ai::AiService* aiService_ = nullptr;
    WebSocketManager* webSocketManager_ = nullptr;
    std::vector<MwsTablePreset> tablePresets_{};
};

}  // namespace wikilive::server
