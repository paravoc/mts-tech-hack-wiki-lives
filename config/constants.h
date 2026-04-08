#pragma once

#include <chrono>
#include <string_view>

namespace wikilive::config {

inline constexpr std::string_view kWikiInsertPattern = R"(\{\{([^:]+):([^:]+):([^:}]+)\}\})";
inline constexpr int kMwsRateLimitPerSecond = 5;
inline constexpr int kMwsMaxPageSize = 1000;
inline constexpr int kMwsMaxPatchBatchSize = 10;
inline constexpr int kDefaultHttpPort = 3000;
inline constexpr int kDefaultCacheTtlSeconds = 60;
inline constexpr std::chrono::seconds kDefaultRetryDelay{1};
inline constexpr int kDefaultRetryCount = 3;

}  // namespace wikilive::config
