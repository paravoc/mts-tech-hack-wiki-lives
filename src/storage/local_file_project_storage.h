#pragma once

#include <string>

#include "src/storage/project_storage.h"

namespace wikilive::storage {

    class LocalFileProjectStorage final : public ProjectStorage {
    public:
        explicit LocalFileProjectStorage(std::string storagePath);

        utils::Expected<std::vector<models::Project>> listProjects() const override;
        utils::Expected<models::Project> getProject(const std::string& projectId) const override;
        utils::VoidExpected saveProject(const models::Project& project) override;
        utils::VoidExpected deleteProject(const std::string& projectId) override;

    private:
        std::string storagePath_;
    };

}  // namespace wikilive::storage