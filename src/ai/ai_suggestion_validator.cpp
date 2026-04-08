#include "src/ai/ai_suggestion_validator.h"

#include <algorithm>
#include <unordered_set>
#include <utility>

#include "src/utils/string_utils.h"

namespace {

double clampConfidence(const double value) {
    return std::clamp(value, 0.0, 1.0);
}

std::string buildCanonicalInsert(
    const std::string& tableId,
    const std::string& recordId,
    const std::string& fieldName) {
    return "{{" + tableId + ":" + recordId + ":" + fieldName + "}}";
}

}  // namespace

namespace wikilive::ai {

AiSuggestionValidator::AiSuggestionValidator(
    std::unique_ptr<AiFieldVerifier> fieldVerifier,
    AiSuggestionValidatorOptions options)
    : fieldVerifier_(std::move(fieldVerifier)),
      options_(options) {
}

utils::Expected<AiSuggestInsertResult> AiSuggestionValidator::validate(const AiSuggestInsertResult& result) const {
    std::vector<AiInsertCandidate> orderedCandidates = result.candidates;
    if (options_.sortByConfidence) {
        std::stable_sort(
            orderedCandidates.begin(),
            orderedCandidates.end(),
            [](const AiInsertCandidate& lhs, const AiInsertCandidate& rhs) {
                return lhs.confidence > rhs.confidence;
            });
    }

    AiSuggestInsertResult validated;
    std::unordered_set<std::string> seen;

    for (const auto& candidate : orderedCandidates) {
        const auto normalized = normalize(candidate);
        if (!normalized) {
            continue;
        }

        const auto key = makeCandidateKey(*normalized);
        if (seen.contains(key)) {
            continue;
        }

        const auto verified = verify(*normalized);
        if (!verified) {
            return std::unexpected(verified.error());
        }

        if (!verified.value()) {
            continue;
        }

        seen.insert(key);
        validated.candidates.push_back(*normalized);

        if (validated.candidates.size() >= options_.maxCandidates) {
            break;
        }
    }

    return validated;
}

std::optional<AiInsertCandidate> AiSuggestionValidator::normalize(const AiInsertCandidate& candidate) const {
    AiInsertCandidate normalized = candidate;
    normalized.tableId = utils::trim(normalized.tableId);
    normalized.recordId = utils::trim(normalized.recordId);
    normalized.fieldName = utils::trim(normalized.fieldName);
    normalized.reason = utils::trim(normalized.reason);
    normalized.confidence = clampConfidence(normalized.confidence);

    if (normalized.tableId.empty() || normalized.recordId.empty() || normalized.fieldName.empty()) {
        return std::nullopt;
    }

    if (normalized.reason.empty()) {
        normalized.reason = "Suggested by AI";
    }

    normalized.insert = buildCanonicalInsert(normalized.tableId, normalized.recordId, normalized.fieldName);
    return normalized;
}

utils::Expected<bool> AiSuggestionValidator::verify(const AiInsertCandidate& candidate) const {
    if (fieldVerifier_ == nullptr) {
        return true;
    }

    return fieldVerifier_->exists(candidate.tableId, candidate.recordId, candidate.fieldName);
}

std::string AiSuggestionValidator::makeCandidateKey(const AiInsertCandidate& candidate) const {
    return candidate.tableId + "\n" + candidate.recordId + "\n" + candidate.fieldName;
}

}  // namespace wikilive::ai
