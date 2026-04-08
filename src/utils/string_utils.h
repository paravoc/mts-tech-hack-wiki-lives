#pragma once

#include <string>
#include <vector>

namespace wikilive::utils {

[[nodiscard]] std::string trim(const std::string& value);
[[nodiscard]] std::vector<std::string> split(const std::string& value, char delimiter);
[[nodiscard]] std::string replaceAll(std::string value, const std::string& from, const std::string& to);
[[nodiscard]] std::string stripQuotes(const std::string& value);
[[nodiscard]] std::string escapeJson(const std::string& value);
[[nodiscard]] std::string escapeHtml(const std::string& value);

}  // namespace wikilive::utils
