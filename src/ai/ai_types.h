#pragma once

#include <string>
#include <vector>

namespace wikilive::ai {

struct AiProviderMetadata {
    std::string provider = "disabled";
    std::string model;
    std::string baseUrl;
    bool enabled = false;
};

struct AiAnalyzeRequest {
    std::string pageTitle;
    std::string content;
    std::string contextJson;
};

struct AiAnalysisResult {
    std::vector<std::string> findings;
    std::vector<std::string> suggestions;
};

struct AiSuggestInsertRequest {
    std::string userPrompt;
    std::string pageContent;
    std::string contextJson;
};

struct AiInsertCandidate {
    std::string tableId;
    std::string recordId;
    std::string fieldName;
    std::string insert;
    std::string reason;
    double confidence = 0.0;
};

struct AiSuggestInsertResult {
    std::vector<AiInsertCandidate> candidates;
};

struct AiGeneratePageRequest {
    std::string prompt;
    std::string contextJson;
};

struct AiGeneratedPage {
    std::string title;
    std::string content;
    std::vector<std::string> notes;
};

}  // namespace wikilive::ai
