#include "src/security/access_evaluator.h"

#include <algorithm>

namespace wikilive::security {
    namespace {

        bool contains(const std::vector<std::string>& values, const std::string& value) {
            return std::find(values.begin(), values.end(), value) != values.end();
        }

        bool intersects(const std::vector<std::string>& left, const std::vector<std::string>& right) {
            return std::any_of(left.begin(), left.end(), [&](const std::string& item) {
                return contains(right, item);
                });
        }

    }  // namespace

    AccessActor makeAccessActor(const models::User& user) {
        return AccessActor{
            .userId = user.id,
            .email = user.email,
            .role = user.role,
            .groups = user.groups,
            .isAdmin = user.role == "admin",
        };
    }

    bool hasDirectAccess(const AccessActor& actor, const models::PageAccess& access) {
        if (access.publicAccess) {
            return true;
        }

        if (!actor.userId.empty() && contains(access.userIds, actor.userId)) {
            return true;
        }

        if (!actor.email.empty() && contains(access.userIds, actor.email)) {
            return true;
        }

        if (!actor.role.empty() && contains(access.roles, actor.role)) {
            return true;
        }

        if (!actor.groups.empty() && intersects(actor.groups, access.groupIds)) {
            return true;
        }

        return false;
    }

    bool canReadProject(const AccessActor& actor, const models::Project& project) {
        if (actor.isAdmin) {
            return true;
        }

        if (actor.userId == project.ownerId) {
            return true;
        }

        if (!actor.userId.empty() && contains(project.sharedWith, actor.userId)) {
            return true;
        }
        if (!actor.email.empty() && contains(project.sharedWith, actor.email)) {
            return true;
        }

        return hasDirectAccess(actor, project.access);
    }

    bool canEditProject(const AccessActor& actor, const models::Project& project) {
        return actor.isAdmin || actor.userId == project.ownerId || hasDirectAccess(actor, project.access);
    }

    bool canEditProjectAccess(const AccessActor& actor, const models::Project& project) {
        return canEditProject(actor, project);
    }

    bool canReadPage(const AccessActor& actor, const models::Project& project, const models::Page& page) {
        if (actor.isAdmin) {
            return true;
        }

        if (actor.userId == page.ownerId) {
            return true;
        }

        if (!actor.userId.empty() && contains(page.sharedWith, actor.userId)) {
            return true;
        }
        if (!actor.email.empty() && contains(page.sharedWith, actor.email)) {
            return true;
        }

        if (!canReadProject(actor, project)) {
            return false;
        }

        return hasDirectAccess(actor, page.access);
    }

    bool canEditPage(const AccessActor& actor, const models::Project& project, const models::Page& page) {
        return actor.isAdmin ||
            actor.userId == page.ownerId ||
            actor.userId == project.ownerId ||
            hasDirectAccess(actor, page.access);
    }

    bool canEditPageAccess(const AccessActor& actor, const models::Project& project, const models::Page& page) {
        return canEditPage(actor, project, page);
    }

}  // namespace wikilive::security
