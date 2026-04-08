#pragma once

#include <string>

#include "src/models/page.h"
#include "src/utils/errors.h"
#include "src/wiki/wiki_renderer.h"

namespace wikilive::services {

class RenderService {
public:
    [[nodiscard]] utils::Expected<std::string> render(const std::string& content) const;
    [[nodiscard]] utils::Expected<models::Page> renderPage(const models::Page& page) const;

private:
    wiki::WikiRenderer renderer_{};
};

}  // namespace wikilive::services
