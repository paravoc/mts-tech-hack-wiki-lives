#pragma once

#include <string>
#include <vector>

#include "src/models/project.h"
#include "src/utils/errors.h"

namespace wikilive::storage {

    class ProjectStorage {
    public:
        virtual ~ProjectStorage() = default;

        virtual utils::Expected<std::vector<models::Project>> listProjects() const = 0;
        virtual utils::Expected<models::Project> getProject(const std::string& projectId) const = 0;
        virtual utils::VoidExpected saveProject(const models::Project& project) = 0;
        virtual utils::VoidExpected deleteProject(const std::string& projectId) = 0;
    };

}  // namespace wikilive::storage