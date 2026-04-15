#pragma once

#include <string>

#include <nlohmann/json.hpp>

#include "src/ai/ai_types.h"

namespace wikilive::ai {

[[nodiscard]] std::string buildSuggestInsertSystemPrompt();
[[nodiscard]] std::string buildSuggestInsertUserPrompt(const AiSuggestInsertRequest& request);
[[nodiscard]] nlohmann::json buildSuggestInsertJsonSchema();

}  // namespace wikilive::ai
