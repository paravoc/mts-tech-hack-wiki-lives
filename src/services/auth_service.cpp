#include "src/services/auth_service.h"

#include <cstdint>
#include <sstream>

namespace wikilive::services {

namespace {

std::string toHex(std::uint32_t value) {
    std::ostringstream stream;
    stream << std::hex << value;
    return stream.str();
}

}  // namespace

AuthService::AuthService(storage::LocalUserStorage& userStorage)
    : userStorage_(userStorage) {
}

utils::Expected<models::User> AuthService::login(const std::string& email, const std::string& password) const {
    if (email.empty() || password.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Email and password are required",
            400,
            false));
    }

    const auto users = userStorage_.listUsers();
    if (!users) {
        return std::unexpected(users.error());
    }

    const auto expectedHash = hashPassword(password);
    for (const auto& user : users.value()) {
        if (user.email == email && user.passwordHash == expectedHash) {
            return user;
        }
    }

    return std::unexpected(utils::makeError(
        utils::ErrorCode::InvalidRequest,
        "Invalid credentials",
        401,
        false));
}

std::string AuthService::hashPassword(const std::string& value) {
    std::uint32_t hash = 5381u;
    for (unsigned char ch : value) {
        hash = ((hash << 5) + hash) + ch;
    }
    return toHex(hash);
}

}  // namespace wikilive::services
