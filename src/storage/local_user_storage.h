#pragma once

#include <string>
#include <vector>

#include "src/models/user.h"
#include "src/utils/errors.h"

namespace wikilive::storage {

class LocalUserStorage {
public:
    explicit LocalUserStorage(std::string storagePath);

    [[nodiscard]] utils::Expected<std::vector<models::User>> listUsers() const;
    [[nodiscard]] utils::Expected<std::vector<models::Group>> listGroups() const;

private:
    [[nodiscard]] utils::Expected<void> loadData(
        std::vector<models::User>& users,
        std::vector<models::Group>& groups) const;

    std::string storagePath_;
};

}  // namespace wikilive::storage
