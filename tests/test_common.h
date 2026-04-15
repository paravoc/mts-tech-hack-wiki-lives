#pragma once

#include <functional>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

namespace wikilive::tests {

template <typename T>
inline std::string toDebugString(const T& value) {
    if constexpr (requires(std::ostringstream& stream, const T& item) { stream << item; }) {
        std::ostringstream stream;
        stream << value;
        return stream.str();
    } else if constexpr (std::is_enum_v<T>) {
        using Underlying = std::underlying_type_t<T>;
        return std::to_string(static_cast<Underlying>(value));
    } else {
        return "<unprintable>";
    }
}

struct TestCase {
    const char* name;
    std::function<void()> run;
};

inline void expect(const bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

template <typename Left, typename Right>
inline void expectEqual(const Left& actual, const Right& expected, const std::string& message) {
    if (!(actual == expected)) {
        std::ostringstream stream;
        stream << message << " (actual=" << toDebugString(actual) << ", expected=" << toDebugString(expected) << ")";
        throw std::runtime_error(stream.str());
    }
}

inline int runAll(const std::vector<TestCase>& cases) {
    int failures = 0;
    for (const auto& testCase : cases) {
        try {
            testCase.run();
            std::cout << "[PASS] " << testCase.name << '\n';
        } catch (const std::exception& exception) {
            ++failures;
            std::cerr << "[FAIL] " << testCase.name << ": " << exception.what() << '\n';
        } catch (...) {
            ++failures;
            std::cerr << "[FAIL] " << testCase.name << ": unknown exception" << '\n';
        }
    }

    return failures == 0 ? 0 : 1;
}

}  // namespace wikilive::tests
