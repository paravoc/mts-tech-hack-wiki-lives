#pragma once

#include <string>
#include <vector>

namespace wikilive::models {

struct PageAccess {
    std::vector<std::string> userIds;
    std::vector<std::string> groupIds;
    std::vector<std::string> roles;
    bool publicAccess = false;
};

struct Page {
    std::string pageId;
    std::string projectId;
    std::string title;
    std::string description;
    std::string content;
    std::string createdAt;
    std::string updatedAt;
    std::string ownerId;
    std::string ownerName;
    std::vector<std::string> sharedWith;
    PageAccess access;
    std::string renderedHtml;
};

}  // namespace wikilive::models
