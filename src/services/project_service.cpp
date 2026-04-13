#include "src/services/project_service.h"

#include <algorithm>
#include <charconv>
#include <string_view>

#include "src/utils/time_utils.h"

namespace wikilive::services {

    ProjectService::ProjectService(storage::ProjectStorage& storage)
        : storage_(storage) {
        const auto projects = storage_.listProjects();
        if (!projects) {
            return;
        }

        std::size_t maxProjectNumber = 0;
        for (const auto& project : projects.value()) {
            constexpr std::string_view prefix = "project-";
            if (project.projectId.rfind(prefix, 0) != 0) {
                continue;
            }

            const auto numberView = std::string_view(project.projectId).substr(prefix.size());
            std::size_t parsedNumber = 0;
            const auto result = std::from_chars(
                numberView.data(),
                numberView.data() + numberView.size(),
                parsedNumber);
            if (result.ec == std::errc{} && result.ptr == numberView.data() + numberView.size()) {
                maxProjectNumber = std::max(maxProjectNumber, parsedNumber);
            }
        }

        projectCounter_ = std::max<std::size_t>(projectCounter_, maxProjectNumber + 1);
    }

    utils::Expected<std::vector<models::Project>> ProjectService::listProjects() const {
        auto projects = storage_.listProjects();
        if (!projects) {
            return std::unexpected(projects.error());
        }

        auto value = projects.value();
        std::sort(value.begin(), value.end(), [](const models::Project& left, const models::Project& right) {
            if (left.updatedAt == right.updatedAt) {
                return left.projectId < right.projectId;
            }
            return left.updatedAt > right.updatedAt;
            });

        return value;
    }

    utils::Expected<models::Project> ProjectService::getProject(const std::string& projectId) const {
        return storage_.getProject(projectId);
    }

    utils::Expected<models::ProjectDraft> ProjectService::validateDraft(const models::ProjectDraft& draft) const {
        if (draft.name.empty()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Project name must not be empty",
                400,
                false));
        }

        if (draft.ownerId.empty()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Project ownerId must not be empty",
                400,
                false));
        }

        return draft;
    }

    utils::Expected<models::Project> ProjectService::createProject(const models::ProjectDraft& draft) {
        const auto validDraft = validateDraft(draft);
        if (!validDraft) {
            return std::unexpected(validDraft.error());
        }

        const auto now = utils::formatIso(utils::now());

        models::Project project{
            .projectId = "project-" + std::to_string(projectCounter_++),
            .name = validDraft->name,
            .description = validDraft->description,
            .createdAt = now,
            .updatedAt = now,
            .ownerId = validDraft->ownerId,
            .ownerName = validDraft->ownerName,
            .sharedWith = validDraft->sharedWith,
            .access = validDraft->access,
        };

        const auto result = storage_.saveProject(project);
        if (!result) {
            return std::unexpected(result.error());
        }

        return project;
    }

    utils::Expected<models::Project> ProjectService::updateProject(
        const std::string& projectId,
        const models::ProjectDraft& draft) {
        const auto existing = storage_.getProject(projectId);
        if (!existing) {
            return std::unexpected(existing.error());
        }

        const auto validDraft = validateDraft(draft);
        if (!validDraft) {
            return std::unexpected(validDraft.error());
        }

        auto project = existing.value();
        project.name = validDraft->name;
        project.description = validDraft->description;
        project.ownerId = validDraft->ownerId;
        project.ownerName = validDraft->ownerName;
        project.sharedWith = validDraft->sharedWith;
        project.access = validDraft->access;
        project.updatedAt = utils::formatIso(utils::now());

        const auto result = storage_.saveProject(project);
        if (!result) {
            return std::unexpected(result.error());
        }

        return project;
    }

    utils::VoidExpected ProjectService::updateAccess(const std::string& projectId, const models::PageAccess& access) {
        const auto existing = storage_.getProject(projectId);
        if (!existing) {
            return std::unexpected(existing.error());
        }

        auto project = existing.value();
        project.access = access;
        project.updatedAt = utils::formatIso(utils::now());

        return storage_.saveProject(project);
    }

    utils::VoidExpected ProjectService::deleteProject(const std::string& projectId) {
        return storage_.deleteProject(projectId);
    }

}  // namespace wikilive::services