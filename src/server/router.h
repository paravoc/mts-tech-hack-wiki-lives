#pragma once

#include <cstddef>
#include <string>

#include "src/services/page_service.h"
#include "src/services/render_service.h"
#include "src/utils/errors.h"

namespace wikilive::server {

struct RouteResponse {
    int statusCode = 200;
    std::string body;
};

class Router {
public:
    Router(services::PageService& pageService, services::RenderService& renderService);

    [[nodiscard]] RouteResponse handleHealth() const;
    [[nodiscard]] RouteResponse listPages();
    [[nodiscard]] RouteResponse getPage(const std::string& pageId);
    [[nodiscard]] RouteResponse createPage(const std::string& payload);
    [[nodiscard]] RouteResponse updatePage(const std::string& pageId, const std::string& payload);
    [[nodiscard]] RouteResponse deletePage(const std::string& pageId);
    [[nodiscard]] RouteResponse renderContent(const std::string& payload);

private:
    [[nodiscard]] RouteResponse ok(const std::string& dataJson) const;
    [[nodiscard]] RouteResponse fail(const utils::Error& error) const;
    [[nodiscard]] RouteResponse created(const std::string& dataJson) const;
    [[nodiscard]] utils::Expected<services::PageDraft> parsePagePayload(const std::string& payload) const;
    [[nodiscard]] utils::Expected<std::string> extractJsonString(
        const std::string& payload,
        const std::string& key,
        bool required = true) const;

    services::PageService& pageService_;
    services::RenderService& renderService_;
};

}  // namespace wikilive::server
