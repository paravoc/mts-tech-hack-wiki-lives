#pragma once

#include <string>
#include <vector>

#include "src/models/page.h"
#include "src/models/project.h"
#include "src/models/user.h"

namespace wikilive::security {

    struct AccessActor {
        std::string userId;
        std::string email;
        std::string role;
        std::vector<std::string> groups;
        bool isAdmin = false;
    };

    AccessActor makeAccessActor(const models::User& user);

    bool hasDirectAccess(const AccessActor& actor, const models::PageAccess& access);

    bool canReadProject(const AccessActor& actor, const models::Project& project);
    bool canEditProject(const AccessActor& actor, const models::Project& project);
    bool canEditProjectAccess(const AccessActor& actor, const models::Project& project);

    bool canReadPage(const AccessActor& actor, const models::Project& project, const models::Page& page);
    bool canEditPage(const AccessActor& actor, const models::Project& project, const models::Page& page);
    bool canEditPageAccess(const AccessActor& actor, const models::Project& project, const models::Page& page);

}  // namespace wikilive::security