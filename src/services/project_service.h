#pragma once

#include <string>
#include <vector>

#include "src/models/project.h"
#include "src/storage/project_storage.h"
#include "src/utils/errors.h"

namespace wikilive::services {

    class ProjectService {
    public:
        explicit ProjectService(storage::ProjectStorage& storage);

        utils::Expected<std::vector<models::Project>> listProjects() const;
        utils::Expected<models::Project> getProject(const std::string& projectId) const;
        utils::Expected<models::Project> createProject(const models::ProjectDraft& draft);
        utils::Expected<models::Project> updateProject(const std::string& projectId, const models::ProjectDraft& draft);
        utils::VoidExpected updateAccess(const std::string& projectId, const models::PageAccess& access);
        utils::VoidExpected deleteProject(const std::string& projectId);

    private:
        utils::Expected<models::ProjectDraft> validateDraft(const models::ProjectDraft& draft) const;

        storage::ProjectStorage& storage_;
        std::size_t projectCounter_ = 1;
    };

}  // namespace wikilive::services