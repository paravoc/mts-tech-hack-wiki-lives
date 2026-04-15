#pragma once

#include <cstddef>
#include <memory>
#include <optional>
#include <string>

#include "src/ai/ai_field_verifier.h"
#include "src/ai/ai_types.h"
#include "src/utils/errors.h"

namespace wikilive::ai {

struct AiSuggestionValidatorOptions {
    std::size_t maxCandidates = 5;
    bool sortByConfidence = true;
};

class AiSuggestionValidator {
public:
    explicit AiSuggestionValidator(
        std::unique_ptr<AiFieldVerifier> fieldVerifier = nullptr,
        AiSuggestionValidatorOptions options = {});

    [[nodiscard]] utils::Expected<AiSuggestInsertResult> validate(const AiSuggestInsertResult& result) const;

private:
    [[nodiscard]] std::optional<AiInsertCandidate> normalize(const AiInsertCandidate& candidate) const;
    [[nodiscard]] utils::Expected<bool> verify(const AiInsertCandidate& candidate) const;
    [[nodiscard]] std::string makeCandidateKey(const AiInsertCandidate& candidate) const;

    std::unique_ptr<AiFieldVerifier> fieldVerifier_;
    AiSuggestionValidatorOptions options_{};
};

}  // namespace wikilive::ai
