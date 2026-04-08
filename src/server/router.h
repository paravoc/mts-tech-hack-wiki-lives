#pragma once

#include <cstddef>
#include <string>

#include "src/storage/page_storage.h"
#include "src/utils/errors.h"
#include "src/wiki/wiki_renderer.h"

namespace wikilive::server {

struct RouteResponse {
    int statusCode = 200;
    std::string body;
};

class Router {
public:
    [[nodiscard]] RouteResponse handleHealth() const;
    [[nodiscard]] RouteResponse listPages();
    [[nodiscard]] RouteResponse getPage(const std::string& pageId);
    [[nodiscard]] RouteResponse savePage(const std::string& payload);
    [[nodiscard]] RouteResponse deletePage(const std::string& pageId);
    [[nodiscard]] RouteResponse renderContent(const std::string& payload);

private:
    [[nodiscard]] RouteResponse ok(const std::string& dataJson) const;
    [[nodiscard]] RouteResponse fail(const utils::Error& error) const;
    [[nodiscard]] utils::Expected<storage::Page> parsePagePayload(const std::string& payload);
    [[nodiscard]] utils::Expected<std::string> extractJsonString(const std::string& payload, const std::string& key) const;

    storage::PageStorage pageStorage_{};
    wiki::WikiRenderer wikiRenderer_{};
    std::size_t nextPageId_ = 1;
};

}  // namespace wikilive::server
