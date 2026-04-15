#pragma once

#include <memory>

#include "src/ai/ai_provider.h"

namespace wikilive::core {
struct AppConfig;
}

namespace wikilive::ai {

[[nodiscard]] std::unique_ptr<AiProvider> createAiProvider(const core::AppConfig& config);

}  // namespace wikilive::ai
