#pragma once

#include <exception>
#include <functional>
#include <type_traits>
#include <utility>

#include "src/utils/errors.h"
#include "src/utils/time_utils.h"

namespace wikilive::api {

class RetryPolicy {
public:
    template <typename Function>
    auto run(Function&& fn, int attempts, int baseDelayMs) const -> std::invoke_result_t<Function&> {
        using Result = std::invoke_result_t<Function&>;

        utils::Error lastError = utils::makeError(
            utils::ErrorCode::InternalError,
            "Retry policy did not execute",
            500,
            false);

        const int normalizedAttempts = attempts > 0 ? attempts : 1;

        for (int attempt = 1; attempt <= normalizedAttempts; ++attempt) {
            try {
                Result result = std::forward<Function>(fn)();
                if (result) {
                    return result;
                }

                lastError = result.error();
                if (!lastError.retryable || attempt == normalizedAttempts) {
                    break;
                }
            } catch (const std::exception& exception) {
                lastError = utils::makeError(
                    utils::ErrorCode::InternalError,
                    std::string("Unhandled exception inside retry policy: ") + exception.what(),
                    500,
                    false);
                break;
            } catch (...) {
                lastError = utils::makeError(
                    utils::ErrorCode::InternalError,
                    "Unhandled unknown exception inside retry policy",
                    500,
                    false);
                break;
            }

            if (baseDelayMs > 0) {
                utils::sleepMs(baseDelayMs * attempt);
            }
        }

        return wikilive::utils::makeUnexpected(lastError);
    }
};

}  // namespace wikilive::api
