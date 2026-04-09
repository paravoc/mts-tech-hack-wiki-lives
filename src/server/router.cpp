#include "src/server/router.h"

#include <algorithm>
#include <exception>
#include <unordered_set>
#include <utility>

#include <nlohmann/json.hpp>

#include "src/utils/string_utils.h"

namespace {

std::string buildSuccessJson(const std::string& dataJson) {
    return "{\"success\":true,\"data\":" + dataJson + "}";
}

std::string buildErrorJson(const wikilive::utils::Error& error) {
    return
        "{\"success\":false,\"error\":{\"code\":\"" + wikilive::utils::toString(error.code) +
        "\",\"message\":\"" + wikilive::utils::escapeJson(error.message) +
        "\",\"retryable\":" + std::string(error.retryable ? "true" : "false") + "}}";
}

std::string pageToJson(const wikilive::models::Page& page, const bool includeRenderedHtml) {
    std::string json =
        "{\"pageId\":\"" + wikilive::utils::escapeJson(page.pageId) +
        "\",\"title\":\"" + wikilive::utils::escapeJson(page.title) +
        "\",\"content\":\"" + wikilive::utils::escapeJson(page.content) +
        "\",\"createdAt\":\"" + wikilive::utils::escapeJson(page.createdAt) +
        "\",\"updatedAt\":\"" + wikilive::utils::escapeJson(page.updatedAt) + "\"";

    if (includeRenderedHtml) {
        json += ",\"renderedHtml\":\"" + wikilive::utils::escapeJson(page.renderedHtml) + "\"";
    }

    json += "}";
    return json;
}

std::string aiInsertCandidateToJson(const wikilive::ai::AiInsertCandidate& candidate) {
    return
        "{\"tableId\":\"" + wikilive::utils::escapeJson(candidate.tableId) +
        "\",\"recordId\":\"" + wikilive::utils::escapeJson(candidate.recordId) +
        "\",\"fieldName\":\"" + wikilive::utils::escapeJson(candidate.fieldName) +
        "\",\"insert\":\"" + wikilive::utils::escapeJson(candidate.insert) +
        "\",\"reason\":\"" + wikilive::utils::escapeJson(candidate.reason) +
        "\",\"confidence\":" + std::to_string(candidate.confidence) + "}";
}

wikilive::server::RouteResponse unexpectedExceptionResponse(const std::exception& exception) {
    const auto error = wikilive::utils::makeError(
        wikilive::utils::ErrorCode::InternalError,
        std::string("Unhandled router exception: ") + exception.what(),
        500,
        false);
    return wikilive::server::RouteResponse{
        .statusCode = error.httpStatus,
        .body = buildErrorJson(error),
    };
}

wikilive::server::RouteResponse unknownExceptionResponse() {
    const auto error = wikilive::utils::makeError(
        wikilive::utils::ErrorCode::InternalError,
        "Unhandled unknown router exception",
        500,
        false);
    return wikilive::server::RouteResponse{
        .statusCode = error.httpStatus,
        .body = buildErrorJson(error),
    };
}

}  // namespace

namespace wikilive::server {

Router::Router(
    services::PageService& pageService,
    services::RenderService& renderService,
    ai::AiService* aiService,
    WebSocketManager* webSocketManager)
    : Router(pageService, renderService, nullptr, aiService, webSocketManager) {
}

Router::Router(
    services::PageService& pageService,
    services::RenderService& renderService,
    api::MwsClient* mwsClient,
    ai::AiService* aiService,
    WebSocketManager* webSocketManager)
    : pageService_(pageService),
      renderService_(renderService),
      mwsClient_(mwsClient),
      aiService_(aiService),
      webSocketManager_(webSocketManager) {
}

RouteResponse Router::handleHealth() const {
    try {
        return ok(R"({"status":"ok","service":"wikilive_backend","version":"mvp"})");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::listPages() {
    try {
        const auto pages = pageService_.listPages();
        if (!pages) {
            return fail(pages.error());
        }

        std::string items = "[";
        bool first = true;
        for (const auto& page : pages.value()) {
            if (!first) {
                items += ",";
            }
            first = false;
            items += pageToJson(page, false);
        }
        items += "]";

        return ok("{\"items\":" + items + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::getPage(const std::string& pageId) {
    try {
        if (pageId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "pageId must not be empty",
                400,
                false));
        }

        const auto page = pageService_.getPage(pageId);
        if (!page) {
            return fail(page.error());
        }

        const auto renderedPage = renderService_.renderPage(page.value());
        if (!renderedPage) {
            return fail(renderedPage.error());
        }

        return ok("{\"item\":" + pageToJson(renderedPage.value(), true) + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::createPage(const std::string& payload) {
    try {
        const auto draft = parsePagePayload(payload);
        if (!draft) {
            return fail(draft.error());
        }

        const auto createdPage = pageService_.createPage(draft.value());
        if (!createdPage) {
            return fail(createdPage.error());
        }

        const auto renderedPage = renderService_.renderPage(createdPage.value());
        if (!renderedPage) {
            return fail(renderedPage.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(renderedPage->pageId, "page.created");
        }

        return created("{\"item\":" + pageToJson(renderedPage.value(), true) + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::updatePage(const std::string& pageId, const std::string& payload) {
    try {
        if (pageId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "pageId must not be empty",
                400,
                false));
        }

        const auto draft = parsePagePayload(payload);
        if (!draft) {
            return fail(draft.error());
        }

        const auto updatedPage = pageService_.updatePage(pageId, draft.value());
        if (!updatedPage) {
            return fail(updatedPage.error());
        }

        const auto renderedPage = renderService_.renderPage(updatedPage.value());
        if (!renderedPage) {
            return fail(renderedPage.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(renderedPage->pageId, "page.updated");
        }

        return ok("{\"item\":" + pageToJson(renderedPage.value(), true) + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::deletePage(const std::string& pageId) {
    try {
        if (pageId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "pageId must not be empty",
                400,
                false));
        }

        const auto removeResult = pageService_.deletePage(pageId);
        if (!removeResult) {
            return fail(removeResult.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "page.deleted");
        }

        return ok("{\"deleted\":true,\"pageId\":\"" + utils::escapeJson(pageId) + "\"}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::renderContent(const std::string& payload) {
    try {
        std::string content = payload;
        if (payload.find("\"content\"") != std::string::npos) {
            const auto extractedContent = extractJsonString(payload, "content");
            if (!extractedContent) {
                return fail(extractedContent.error());
            }
            content = extractedContent.value();
        }

        const auto rendered = renderService_.render(content);
        if (!rendered) {
            return fail(rendered.error());
        }

        return ok("{\"html\":\"" + utils::escapeJson(rendered.value()) + "\"}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::getMwsInsertOptions() {
    try {
        if (mwsClient_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is not configured",
                503,
                false));
        }

        const auto records = mwsClient_->getRecords();
        if (!records) {
            return fail(records.error());
        }

        nlohmann::json payload = {
            {"tableId", mwsClient_->tableId()},
            {"viewId", mwsClient_->viewId()},
            {"records", nlohmann::json::array()},
            {"fieldNames", nlohmann::json::array()},
        };

        std::unordered_set<std::string> fieldNames;
        for (const auto& record : records.value()) {
            nlohmann::json fieldsJson = nlohmann::json::object();
            for (const auto& [fieldName, fieldValue] : record.fields) {
                fieldsJson[fieldName] = fieldValue;
                fieldNames.insert(fieldName);
            }

            payload["records"].push_back({
                {"recordId", record.recordId},
                {"fields", std::move(fieldsJson)},
            });
        }

        std::vector<std::string> sortedFieldNames(fieldNames.begin(), fieldNames.end());
        std::sort(sortedFieldNames.begin(), sortedFieldNames.end());
        payload["fieldNames"] = sortedFieldNames;

        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::suggestInsert(const std::string& payload) {
    try {
        if (aiService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "AI service is not configured",
                503,
                false));
        }

        if (payload.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "AI payload must not be empty",
                400,
                false));
        }

        const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
        const auto userPrompt = parsedPayload.value("userPrompt", std::string{});
        const auto pageContent = parsedPayload.value("pageContent", std::string{});

        std::string contextJson;
        if (parsedPayload.contains("context")) {
            if (parsedPayload["context"].is_string()) {
                contextJson = parsedPayload["context"].get<std::string>();
            } else {
                contextJson = parsedPayload["context"].dump();
            }
        }

        if (userPrompt.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "AI field userPrompt must not be empty",
                400,
                false));
        }

        const auto aiResult = aiService_->suggestInsert(ai::AiSuggestInsertRequest{
            .userPrompt = userPrompt,
            .pageContent = pageContent,
            .contextJson = contextJson,
        });
        if (!aiResult) {
            return fail(aiResult.error());
        }

        return ok(aiSuggestInsertResultToJson(aiResult.value()));
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed AI JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::ok(const std::string& dataJson) const {
    return RouteResponse{
        .statusCode = 200,
        .body = buildSuccessJson(dataJson),
    };
}

RouteResponse Router::created(const std::string& dataJson) const {
    return RouteResponse{
        .statusCode = 201,
        .body = buildSuccessJson(dataJson),
    };
}

RouteResponse Router::fail(const utils::Error& error) const {
    return RouteResponse{
        .statusCode = error.httpStatus,
        .body = buildErrorJson(error),
    };
}

utils::Expected<services::PageDraft> Router::parsePagePayload(const std::string& payload) const {
    if (payload.empty()) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Page payload must not be empty",
            400,
            false));
    }

    auto title = extractJsonString(payload, "title");
    if (!title) {
        return std::unexpected(title.error());
    }

    auto content = extractJsonString(payload, "content");
    if (!content) {
        return std::unexpected(content.error());
    }

    return services::PageDraft{
        .title = title.value(),
        .content = content.value(),
    };
}

utils::Expected<std::string> Router::extractJsonString(
    const std::string& payload,
    const std::string& key,
    const bool required) const {
    const auto keyToken = "\"" + key + "\"";
    const auto keyPosition = payload.find(keyToken);
    if (keyPosition == std::string::npos) {
        if (!required) {
            return std::string{};
        }
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Missing JSON field: " + key,
            400,
            false));
    }

    const auto colonPosition = payload.find(':', keyPosition + keyToken.size());
    if (colonPosition == std::string::npos) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Malformed JSON field: " + key,
            400,
            false));
    }

    const auto openingQuote = payload.find('"', colonPosition + 1);
    if (openingQuote == std::string::npos) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            "Expected quoted string field: " + key,
            400,
            false));
    }

    std::string rawValue;
    bool escape = false;
    for (std::size_t index = openingQuote + 1; index < payload.size(); ++index) {
        const char current = payload[index];
        if (escape) {
            rawValue.push_back(current);
            escape = false;
            continue;
        }

        if (current == '\\') {
            rawValue.push_back(current);
            escape = true;
            continue;
        }

        if (current == '"') {
            return utils::unescapeJson(rawValue);
        }

        rawValue.push_back(current);
    }

    return std::unexpected(utils::makeError(
        utils::ErrorCode::InvalidRequest,
        "Unterminated JSON string field: " + key,
        400,
        false));
}

std::string Router::aiSuggestInsertResultToJson(const ai::AiSuggestInsertResult& result) const {
    std::string items = "[";
    bool first = true;
    for (const auto& candidate : result.candidates) {
        if (!first) {
            items += ",";
        }
        first = false;
        items += aiInsertCandidateToJson(candidate);
    }
    items += "]";

    return "{\"candidates\":" + items + "}";
}

}  // namespace wikilive::server
