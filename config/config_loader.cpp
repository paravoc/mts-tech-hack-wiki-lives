#include "config/config_loader.h"

#include <fstream>

#include "src/utils/string_utils.h"

namespace wikilive::config {

utils::VoidExpected ConfigLoader::loadFromFile(const std::string& path) {
    std::ifstream input(path);
    if (!input.is_open()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidConfig,
            "Unable to open config file: " + path,
            500,
            false));
    }

    values_.clear();

    std::string line;
    while (std::getline(input, line)) {
        line = utils::trim(line);
        if (line.empty() || line.starts_with('#')) {
            continue;
        }

        const auto separator = line.find('=');
        if (separator == std::string::npos) {
            continue;
        }

        auto key = utils::trim(line.substr(0, separator));
        auto value = utils::trim(line.substr(separator + 1));
        value = utils::stripQuotes(value);
        values_[key] = value;
    }

    return {};
}

const ConfigLoader::Values& ConfigLoader::values() const {
    return values_;
}

std::string ConfigLoader::get(const std::string& key, const std::string& fallback) const {
    const auto it = values_.find(key);
    return it == values_.end() ? fallback : it->second;
}

}  // namespace wikilive::config
