#pragma once

#include <string>

#include "src/api/mws_client.h"
#include "src/models/page.h"
#include "src/utils/errors.h"
#include "src/wiki/wiki_renderer.h"

namespace wikilive::services {

class RenderService {
public:
    explicit RenderService(api::MwsClient* mwsClient = nullptr);

    [[nodiscard]] utils::Expected<std::string> render(const std::string& content) const;
    [[nodiscard]] utils::Expected<models::Page> renderPage(const models::Page& page) const;

private:
    wiki::WikiRenderer renderer_;
};

}  // namespace wikilive::services
