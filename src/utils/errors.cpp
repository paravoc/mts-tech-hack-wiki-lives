#include "src/utils/errors.h"

#include <utility>

namespace wikilive::utils {

Error makeError(const ErrorCode code, std::string message, const int httpStatus, const bool retryable) {
    return Error{
        .code = code,
        .message = std::move(message),
        .httpStatus = httpStatus,
        .retryable = retryable,
    };
}

std::string toString(const ErrorCode code) {
    switch (code) {
        case ErrorCode::InvalidConfig:
            return "InvalidConfig";
        case ErrorCode::InvalidRequest:
            return "InvalidRequest";
        case ErrorCode::MwsApiError:
            return "MwsApiError";
        case ErrorCode::MwsRateLimit:
            return "MwsRateLimit";
        case ErrorCode::AiApiError:
            return "AiApiError";
        case ErrorCode::AiRateLimit:
            return "AiRateLimit";
        case ErrorCode::ParserError:
            return "ParserError";
        case ErrorCode::PageNotFound:
            return "PageNotFound";
        case ErrorCode::Timeout:
            return "Timeout";
        case ErrorCode::NotImplemented:
            return "NotImplemented";
        case ErrorCode::InternalError:
            return "InternalError";
        default:
            return "UnknownError";
    }
}

}  // namespace wikilive::utils
