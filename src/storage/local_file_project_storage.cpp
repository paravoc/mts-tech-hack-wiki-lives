#include "src/storage/local_file_project_storage.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <utility>

#include <nlohmann/json.hpp>

namespace wikilive::storage {

    namespace {

        nlohmann::json accessToJson(const models::PageAccess& access) {
            return {
                {"public", access.publicAccess},
                {"users", access.userIds},
                {"groups", access.groupIds},
                {"roles", access.roles},
            };
        }

        models::PageAccess accessFromJson(const nlohmann::json& value) {
            models::PageAccess access;
            if (!value.is_object()) {
                return access;
            }

            if (value.contains("public") && value["public"].is_boolean()) {
                access.publicAccess = value["public"].get<bool>();
            }

            if (value.contains("users") && value["users"].is_array()) {
                for (const auto& item : value["users"]) {
                    if (item.is_string()) {
                        access.userIds.push_back(item.get<std::string>());
                    }
                }
            }

            if (value.contains("groups") && value["groups"].is_array()) {
                for (const auto& item : value["groups"]) {
                    if (item.is_string()) {
                        access.groupIds.push_back(item.get<std::string>());
                    }
                }
            }

            if (value.contains("roles") && value["roles"].is_array()) {
                for (const auto& item : value["roles"]) {
                    if (item.is_string()) {
                        access.roles.push_back(item.get<std::string>());
                    }
                }
            }

            return access;
        }

        nlohmann::json projectToJson(const models::Project& project) {
            return {
                {"projectId", project.projectId},
                {"name", project.name},
                {"description", project.description},
                {"createdAt", project.createdAt},
                {"updatedAt", project.updatedAt},
                {"ownerId", project.ownerId},
                {"ownerName", project.ownerName},
                {"sharedWith", project.sharedWith},
                {"access", accessToJson(project.access)},
            };
        }

        models::Project projectFromJson(const nlohmann::json& value) {
            return {
                .projectId = value.value("projectId", std::string{}),
                .name = value.value("name", std::string{}),
                .description = value.value("description", std::string{}),
                .createdAt = value.value("createdAt", std::string{}),
                .updatedAt = value.value("updatedAt", std::string{}),
                .ownerId = value.value("ownerId", std::string{}),
                .ownerName = value.value("ownerName", std::string{}),
                .sharedWith = value.value("sharedWith", std::vector<std::string>{}),
                .access = accessFromJson(value.value("access", nlohmann::json::object())),
            };
        }

    }  // namespace

    LocalFileProjectStorage::LocalFileProjectStorage(std::string storagePath)
        : storagePath_(std::move(storagePath)) {
    }

    utils::Expected<std::vector<models::Project>> LocalFileProjectStorage::listProjects() const {
        if (!std::filesystem::exists(storagePath_)) {
            return std::vector<models::Project>{};
        }

        std::ifstream input(storagePath_);
        if (!input.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to open project storage: " + storagePath_,
                500,
                false));
        }

        nlohmann::json payload;
        input >> payload;

        std::vector<models::Project> projects;
        if (payload.is_array()) {
            for (const auto& item : payload) {
                projects.push_back(projectFromJson(item));
            }
        }

        return projects;
    }

    utils::Expected<models::Project> LocalFileProjectStorage::getProject(const std::string& projectId) const {
        const auto projects = listProjects();
        if (!projects) {
            return std::unexpected(projects.error());
        }

        for (const auto& project : projects.value()) {
            if (project.projectId == projectId) {
                return project;
            }
        }

        return std::unexpected(utils::makeError(
            utils::ErrorCode::PageNotFound,
            "Project not found: " + projectId,
            404,
            false));
    }

    utils::VoidExpected LocalFileProjectStorage::saveProject(const models::Project& project) {
        auto projects = listProjects();
        if (!projects) {
            return std::unexpected(projects.error());
        }

        auto values = projects.value();
        bool updated = false;
        for (auto& item : values) {
            if (item.projectId == project.projectId) {
                item = project;
                updated = true;
                break;
            }
        }

        if (!updated) {
            values.push_back(project);
        }

        nlohmann::json payload = nlohmann::json::array();
        for (const auto& item : values) {
            payload.push_back(projectToJson(item));
        }

        std::ofstream output(storagePath_);
        if (!output.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to write project storage: " + storagePath_,
                500,
                false));
        }

        output << payload.dump(2, ' ', false, nlohmann::json::error_handler_t::replace);
        return {};
    }

    utils::VoidExpected LocalFileProjectStorage::deleteProject(const std::string& projectId) {
        auto projects = listProjects();
        if (!projects) {
            return std::unexpected(projects.error());
        }

        auto values = projects.value();
        const auto newEnd = std::remove_if(values.begin(), values.end(), [&](const models::Project& project) {
            return project.projectId == projectId;
            });

        if (newEnd == values.end()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::PageNotFound,
                "Project not found: " + projectId,
                404,
                false));
        }

        values.erase(newEnd, values.end());

        nlohmann::json payload = nlohmann::json::array();
        for (const auto& item : values) {
            payload.push_back(projectToJson(item));
        }

        std::ofstream output(storagePath_);
        if (!output.is_open()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "Failed to write project storage: " + storagePath_,
                500,
                false));
        }

        output << payload.dump(2, ' ', false, nlohmann::json::error_handler_t::replace);
        return {};
    }

}  // namespace wikilive::storage
