#include "src/storage/local_user_storage.h"

#include <filesystem>
#include <fstream>
#include <utility>

#include <nlohmann/json.hpp>

namespace wikilive::storage {

namespace {

models::User userFromJson(const nlohmann::json& value) {
    models::User user;
    user.id = value.value("id", std::string{});
    user.name = value.value("name", std::string{});
    user.email = value.value("email", std::string{});
    user.passwordHash = value.value("passwordHash", std::string{});
    user.role = value.value("role", std::string{});
    user.team = value.value("team", std::string{});
    if (value.contains("groups") && value["groups"].is_array()) {
        for (const auto& item : value["groups"]) {
            if (item.is_string()) {
                user.groups.push_back(item.get<std::string>());
            }
        }
    }
    return user;
}

models::Group groupFromJson(const nlohmann::json& value) {
    models::Group group;
    group.id = value.value("id", std::string{});
    group.name = value.value("name", std::string{});
    if (value.contains("members") && value["members"].is_array()) {
        for (const auto& item : value["members"]) {
            if (item.is_string()) {
                group.members.push_back(item.get<std::string>());
            }
        }
    }
    return group;
}

}  // namespace

LocalUserStorage::LocalUserStorage(std::string storagePath)
    : storagePath_(std::move(storagePath)) {
}

utils::Expected<std::vector<models::User>> LocalUserStorage::listUsers() const {
    std::vector<models::User> users;
    std::vector<models::Group> groups;
    const auto result = loadData(users, groups);
    if (!result) {
        return wikilive::utils::makeUnexpected(result.error());
    }
    return users;
}

utils::Expected<std::vector<models::Group>> LocalUserStorage::listGroups() const {
    std::vector<models::User> users;
    std::vector<models::Group> groups;
    const auto result = loadData(users, groups);
    if (!result) {
        return wikilive::utils::makeUnexpected(result.error());
    }
    return groups;
}

utils::Expected<void> LocalUserStorage::loadData(
    std::vector<models::User>& users,
    std::vector<models::Group>& groups) const {
    users.clear();
    groups.clear();

    if (storagePath_.empty() || !std::filesystem::exists(storagePath_)) {
        return {};
    }

    std::ifstream stream(storagePath_, std::ios::binary);
    if (!stream.is_open()) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            "Failed to open user storage: " + storagePath_,
            500,
            true));
    }

    nlohmann::json payload;
    try {
        stream >> payload;
    } catch (const std::exception& exception) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Failed to parse user storage: ") + exception.what(),
            500,
            true));
    }

    for (const auto& item : payload.value("users", nlohmann::json::array())) {
        const auto user = userFromJson(item);
        if (!user.id.empty()) {
            users.push_back(user);
        }
    }

    for (const auto& item : payload.value("groups", nlohmann::json::array())) {
        const auto group = groupFromJson(item);
        if (!group.id.empty()) {
            groups.push_back(group);
        }
    }

    return {};
}

}  // namespace wikilive::storage
