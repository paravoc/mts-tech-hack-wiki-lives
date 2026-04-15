#pragma once

#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <variant>

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

template <typename E>
class Unexpected {
public:
    explicit Unexpected(const E& error)
        : error_(error) {}

    explicit Unexpected(E&& error)
        : error_(std::move(error)) {}

    [[nodiscard]] const E& error() const& { return error_; }
    [[nodiscard]] E& error() & { return error_; }
    [[nodiscard]] E&& error() && { return std::move(error_); }

private:
    E error_;
};

template <typename E>
Unexpected(E) -> Unexpected<E>;

template <typename T, typename E = Error>
class Expected {
public:
    Expected(const T& value)
        : storage_(value) {}

    Expected(T&& value)
        : storage_(std::move(value)) {}

    Expected(const Unexpected<E>& error)
        : storage_(error.error()) {}

    Expected(Unexpected<E>&& error)
        : storage_(std::move(error.error())) {}

    [[nodiscard]] bool has_value() const { return std::holds_alternative<T>(storage_); }
    [[nodiscard]] explicit operator bool() const { return has_value(); }

    [[nodiscard]] T& value() & {
        if (!has_value()) {
            throw std::logic_error("bad expected access");
        }
        return std::get<T>(storage_);
    }

    [[nodiscard]] const T& value() const& {
        if (!has_value()) {
            throw std::logic_error("bad expected access");
        }
        return std::get<T>(storage_);
    }

    [[nodiscard]] T&& value() && {
        if (!has_value()) {
            throw std::logic_error("bad expected access");
        }
        return std::move(std::get<T>(storage_));
    }

    [[nodiscard]] E& error() & {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::get<E>(storage_);
    }

    [[nodiscard]] const E& error() const& {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::get<E>(storage_);
    }

    [[nodiscard]] E&& error() && {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::move(std::get<E>(storage_));
    }

    [[nodiscard]] T& operator*() & { return value(); }
    [[nodiscard]] const T& operator*() const& { return value(); }
    [[nodiscard]] T* operator->() { return &value(); }
    [[nodiscard]] const T* operator->() const { return &value(); }

private:
    std::variant<T, E> storage_;
};

template <typename E>
class Expected<void, E> {
public:
    Expected()
        : storage_(std::monostate{}) {}

    Expected(const Unexpected<E>& error)
        : storage_(error.error()) {}

    Expected(Unexpected<E>&& error)
        : storage_(std::move(error.error())) {}

    [[nodiscard]] bool has_value() const { return std::holds_alternative<std::monostate>(storage_); }
    [[nodiscard]] explicit operator bool() const { return has_value(); }

    void value() const {
        if (!has_value()) {
            throw std::logic_error("bad expected access");
        }
    }

    [[nodiscard]] E& error() & {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::get<E>(storage_);
    }

    [[nodiscard]] const E& error() const& {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::get<E>(storage_);
    }

    [[nodiscard]] E&& error() && {
        if (has_value()) {
            throw std::logic_error("bad expected error access");
        }
        return std::move(std::get<E>(storage_));
    }

private:
    std::variant<std::monostate, E> storage_;
};

using VoidExpected = Expected<void, Error>;

template <typename E>
[[nodiscard]] auto makeUnexpected(E&& error) {
    return Unexpected<std::decay_t<E>>(std::forward<E>(error));
}

[[nodiscard]] Error makeError(ErrorCode code, std::string message, int httpStatus = 500, bool retryable = false);
[[nodiscard]] std::string toString(ErrorCode code);

}  // namespace wikilive::utils
