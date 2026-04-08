#include "src/services/render_service.h"

namespace wikilive::services {

RenderService::RenderService(api::MwsClient* mwsClient)
    : renderer_(mwsClient) {
}

utils::Expected<std::string> RenderService::render(const std::string& content) const {
    return renderer_.render(content);
}

utils::Expected<models::Page> RenderService::renderPage(const models::Page& page) const {
    auto renderedHtml = render(page.content);
    if (!renderedHtml) {
        return std::unexpected(renderedHtml.error());
    }

    auto renderedPage = page;
    renderedPage.renderedHtml = renderedHtml.value();
    return renderedPage;
}

}  // namespace wikilive::services
