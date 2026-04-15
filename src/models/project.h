#pragma once

#include <string>
#include <vector>

#include "src/models/page.h"

namespace wikilive::models {

    struct Project {
        std::string projectId;
        std::string name;
        std::string description;
        std::string createdAt;
        std::string updatedAt;
        std::string ownerId;
        std::string ownerName;
        std::vector<std::string> sharedWith;
        PageAccess access;
    };

    struct ProjectDraft {
        std::string name;
        std::string description;
        std::string ownerId;
        std::string ownerName;
        std::vector<std::string> sharedWith;
        PageAccess access;
    };

}  // namespace wikilive::models