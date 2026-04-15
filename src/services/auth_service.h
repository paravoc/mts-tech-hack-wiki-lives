#pragma once

#include <string>
#include <vector>

#include "src/models/user.h"
#include "src/storage/local_user_storage.h"
#include "src/utils/errors.h"

namespace wikilive::services {

class AuthService {
public:
    explicit AuthService(storage::LocalUserStorage& userStorage);

    [[nodiscard]] utils::Expected<models::User> login(const std::string& email, const std::string& password) const;
    [[nodiscard]] static std::string hashPassword(const std::string& value);

private:
    storage::LocalUserStorage& userStorage_;
};

}  // namespace wikilive::services
