#pragma once

#include <string>

namespace wikilive::models {

struct Page {
    std::string pageId;
    std::string title;
    std::string content;
    std::string createdAt;
    std::string updatedAt;
    std::string renderedHtml;
};

}  // namespace wikilive::models
