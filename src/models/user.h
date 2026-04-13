#pragma once

#include <string>
#include <vector>

namespace wikilive::models {

struct User {
    std::string id;
    std::string name;
    std::string email;
    std::string passwordHash;
    std::string role;
    std::string team;
    std::vector<std::string> groups;
};

struct Group {
    std::string id;
    std::string name;
    std::vector<std::string> members;
};

}  // namespace wikilive::models
