#pragma once

#include <expected>
#include <string>

namespace wikilive::utils {

enum class ErrorCode {
    InvalidConfig,
    InvalidRequest,
    MwsApiError,
    MwsRateLimit,
    AiApiError,
    AiRateLimit,
    ParserError,
    PageNotFound,
    Timeout,
    NotImplemented,
    InternalError,
};

struct Error {
    ErrorCode code = ErrorCode::InternalError;
    std::string message;
    int httpStatus = 500;
    bool retryable = false;
};

template <typename T>
using Expected = std::expected<T, Error>;

using VoidExpected = std::expected<void, Error>;

[[nodiscard]] Error makeError(ErrorCode code, std::string message, int httpStatus = 500, bool retryable = false);
[[nodiscard]] std::string toString(ErrorCode code);

}  // namespace wikilive::utils
