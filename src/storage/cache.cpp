#include "src/storage/cache.h"

namespace wikilive::storage {

void Cache::put(const std::string& key, const std::string& value) {
    values_[key] = value;
}

std::optional<std::string> Cache::get(const std::string& key) const {
    const auto it = values_.find(key);
    if (it == values_.end()) {
        return std::nullopt;
    }
    return it->second;
}

void Cache::invalidate(const std::string& key) {
    values_.erase(key);
}

}  // namespace wikilive::storage
