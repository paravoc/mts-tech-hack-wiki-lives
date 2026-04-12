#pragma once

#include <string>
#include <vector>

namespace wikilive::models {

struct Page {
    std::string pageId;
    std::string title;
    std::string description;
    std::string content;
    std::string createdAt;
    std::string updatedAt;
    std::string ownerId;
    std::string ownerName;
    std::vector<std::string> sharedWith;
    std::string renderedHtml;
};

}  // namespace wikilive::models
