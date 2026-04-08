#pragma once

#include <memory>

#include "src/ai/ai_provider.h"

namespace wikilive::ai {

class AiService {
public:
    explicit AiService(std::unique_ptr<AiProvider> provider);

    [[nodiscard]] bool isAvailable() const;
    [[nodiscard]] AiProviderMetadata metadata() const;
    [[nodiscard]] utils::Expected<AiAnalysisResult> analyzeText(const AiAnalyzeRequest& request) const;
    [[nodiscard]] utils::Expected<AiSuggestInsertResult> suggestInsert(const AiSuggestInsertRequest& request) const;
    [[nodiscard]] utils::Expected<AiGeneratedPage> generatePage(const AiGeneratePageRequest& request) const;

private:
    [[nodiscard]] utils::Error unavailableError() const;

    std::unique_ptr<AiProvider> provider_;
};

}  // namespace wikilive::ai
