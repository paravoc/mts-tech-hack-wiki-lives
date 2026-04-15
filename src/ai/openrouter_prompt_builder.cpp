#include "src/ai/openrouter_prompt_builder.h"

namespace wikilive::ai {

std::string buildSuggestInsertSystemPrompt() {
    return
        "You are the AI insert assistant for WikiLive. "
        "Your job is to suggest valid live wiki inserts for MWS Tables. "
        "Use only the ids, fields, and records present in the provided context. "
        "Never invent tableId, recordId, or fieldName. "
        "Return only candidates that can be safely transformed into the syntax "
        "{{tableId:recordId:fieldName}}. "
        "If the context is insufficient, return an empty candidates array. "
        "Prefer the most relevant business field for the user's request. "
        "The response must strictly follow the provided JSON schema.";
}

std::string buildSuggestInsertUserPrompt(const AiSuggestInsertRequest& request) {
    return
        "User request:\n" + request.userPrompt +
        "\n\nCurrent page content:\n" + request.pageContent +
        "\n\nAvailable context JSON:\n" + request.contextJson +
        "\n\nReturn up to 5 candidates ordered by confidence.";
}

nlohmann::json buildSuggestInsertJsonSchema() {
    return nlohmann::json{
        {"type", "object"},
        {"additionalProperties", false},
        {"required", nlohmann::json::array({"candidates"})},
        {"properties", {
            {"candidates", {
                {"type", "array"},
                {"items", {
                    {"type", "object"},
                    {"additionalProperties", false},
                    {"required", nlohmann::json::array({
                        "tableId",
                        "recordId",
                        "fieldName",
                        "insert",
                        "reason",
                        "confidence",
                    })},
                    {"properties", {
                        {"tableId", {{"type", "string"}}},
                        {"recordId", {{"type", "string"}}},
                        {"fieldName", {{"type", "string"}}},
                        {"insert", {{"type", "string"}}},
                        {"reason", {{"type", "string"}}},
                        {"confidence", {{"type", "number"}}},
                    }},
                }},
            }},
        }},
    };
}

}  // namespace wikilive::ai
