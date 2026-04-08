#pragma once

#include "src/ai/ai_types.h"
#include "src/utils/errors.h"

namespace wikilive::ai {

class AiProvider {
public:
    virtual ~AiProvider() = default;

    [[nodiscard]] virtual const AiProviderMetadata& metadata() const = 0;
    [[nodiscard]] virtual utils::Expected<AiAnalysisResult> analyzeText(const AiAnalyzeRequest& request) const = 0;
    [[nodiscard]] virtual utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const = 0;
    [[nodiscard]] virtual utils::Expected<AiGeneratedPage> generatePage(const AiGeneratePageRequest& request) const = 0;
};

}  // namespace wikilive::ai
