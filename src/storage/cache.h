#pragma once

#include <optional>
#include <string>
#include <unordered_map>

namespace wikilive::storage {

class Cache {
public:
    void put(const std::string& key, const std::string& value);
    [[nodiscard]] std::optional<std::string> get(const std::string& key) const;
    void invalidate(const std::string& key);

private:
    std::unordered_map<std::string, std::string> values_;
};

}  // namespace wikilive::storage
