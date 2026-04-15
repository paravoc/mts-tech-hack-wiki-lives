#pragma once

#include <chrono>
#include <string>

namespace wikilive::utils {

[[nodiscard]] std::chrono::system_clock::time_point now();
[[nodiscard]] std::string formatIso(std::chrono::system_clock::time_point timePoint);
void sleepMs(int milliseconds);

}  // namespace wikilive::utils
