#pragma once

#include <string>
#include <unordered_map>

#include "src/utils/errors.h"

namespace wikilive::config {

class ConfigLoader {
public:
    using Values = std::unordered_map<std::string, std::string>;

    [[nodiscard]] utils::VoidExpected loadFromFile(const std::string& path);
    [[nodiscard]] const Values& values() const;
    [[nodiscard]] std::string get(const std::string& key, const std::string& fallback = "") const;

private:
    Values values_;
};

}  // namespace wikilive::config
