#include "src/server/router.h"

#include <algorithm>
#include <exception>
#include <unordered_set>
#include <utility>

#include <nlohmann/json.hpp>

#include "src/utils/string_utils.h"

namespace {

std::string makeAbsoluteTablesUrl(const std::string& value) {
    if (value.empty()) {
        return {};
    }

    if (value.rfind("http://", 0) == 0 || value.rfind("https://", 0) == 0) {
        return value;
    }

    if (value.front() == '/') {
        return "https://tables.mws.ru" + value;
    }

    return "https://tables.mws.ru/" + value;
}

void applyFieldMeta(const nlohmann::json& value, nlohmann::json& meta) {
    if (value.is_array()) {
        for (const auto& item : value) {
            applyFieldMeta(item, meta);
        }
        return;
    }

    if (!value.is_object()) {
        return;
    }

    if (meta.value("value", std::string{}).empty() && value.contains("name") && value["name"].is_string()) {
        meta["value"] = value["name"].get<std::string>();
    }

    if (value.contains("url") && value["url"].is_string()) {
        meta["resourceUrl"] = makeAbsoluteTablesUrl(value["url"].get<std::string>());
    }

    if (value.contains("mimeType") && value["mimeType"].is_string()) {
        const auto mimeType = value["mimeType"].get<std::string>();
        meta["mimeType"] = mimeType;
        meta["isImage"] = mimeType.rfind("image/", 0) == 0;
    }
}

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

std::string pageVersionToJson(const wikilive::models::PageVersion& version) {
    return nlohmann::json{
        {"versionId", version.versionId},
        {"pageId", version.pageId},
        {"title", version.title},
        {"content", version.content},
        {"createdAt", version.createdAt},
        {"label", version.label},
        {"author", version.author},
    }
        .dump();
}

std::string commentThreadToJson(const wikilive::models::CommentThread& thread) {
    nlohmann::json messages = nlohmann::json::array();
    for (const auto& message : thread.messages) {
        messages.push_back({
            {"messageId", message.messageId},
            {"author", message.author},
            {"body", message.body},
            {"createdAt", message.createdAt},
            {"updatedAt", message.updatedAt},
            {"replyToMessageId", message.replyToMessageId},
            {"deleted", message.deleted},
        });
    }

    return nlohmann::json{
        {"threadId", thread.threadId},
        {"pageId", thread.pageId},
        {"targetId", thread.targetId},
        {"targetType", thread.targetType},
        {"selectionLabel", thread.selectionLabel},
        {"targetPreview", thread.targetPreview},
        {"createdAt", thread.createdAt},
        {"updatedAt", thread.updatedAt},
        {"resolved", thread.resolved},
        {"resolvedAt", thread.resolvedAt},
        {"resolvedBy", thread.resolvedBy},
        {"deleted", thread.deleted},
        {"deletedAt", thread.deletedAt},
        {"deletedBy", thread.deletedBy},
        {"likedBy", thread.likedBy},
        {"likeCount", thread.likedBy.size()},
        {"messages", messages},
    }
        .dump();
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
    services::CollaborationService* collaborationService,
    WebSocketManager* webSocketManager,
    std::vector<MwsTablePreset> tablePresets)
    : Router(
          pageService,
          renderService,
          nullptr,
          aiService,
          collaborationService,
          webSocketManager,
          std::move(tablePresets)) {
}

Router::Router(
    services::PageService& pageService,
    services::RenderService& renderService,
    api::MwsClient* mwsClient,
    ai::AiService* aiService,
    services::CollaborationService* collaborationService,
    WebSocketManager* webSocketManager,
    std::vector<MwsTablePreset> tablePresets)
    : pageService_(pageService),
      renderService_(renderService),
      mwsClient_(mwsClient),
      aiService_(aiService),
      collaborationService_(collaborationService),
      webSocketManager_(webSocketManager),
      tablePresets_(std::move(tablePresets)) {
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

        if (collaborationService_ != nullptr) {
            const auto versionResult = collaborationService_->captureVersion(createdPage.value(), "Created page");
            if (!versionResult) {
                return fail(versionResult.error());
            }
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

        if (collaborationService_ != nullptr) {
            const auto versionResult = collaborationService_->captureVersion(updatedPage.value(), "Saved changes");
            if (!versionResult) {
                return fail(versionResult.error());
            }
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

        if (collaborationService_ != nullptr) {
            const auto cleanupResult = collaborationService_->deletePageData(pageId);
            if (!cleanupResult) {
                return fail(cleanupResult.error());
            }
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

RouteResponse Router::listVersions(const std::string& pageId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto versions = collaborationService_->listVersions(pageId);
        if (!versions) {
            return fail(versions.error());
        }

        std::string items = "[";
        bool first = true;
        for (const auto& version : versions.value()) {
            if (!first) {
                items += ",";
            }
            first = false;
            items += pageVersionToJson(version);
        }
        items += "]";

        return ok("{\"items\":" + items + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::createVersion(const std::string& pageId, const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        std::string label = "Manual snapshot";
        std::string author = "manual";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            label = parsedPayload.value("label", label);
            author = parsedPayload.value("author", author);
        }

        const auto version = collaborationService_->createManualVersion(pageId, label, author);
        if (!version) {
            return fail(version.error());
        }

        return created("{\"item\":" + pageVersionToJson(version.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed version JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::restoreVersion(const std::string& pageId, const std::string& versionId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto restoredPage = collaborationService_->restoreVersion(pageId, versionId);
        if (!restoredPage) {
            return fail(restoredPage.error());
        }

        const auto renderedPage = renderService_.renderPage(restoredPage.value());
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

RouteResponse Router::listComments(const std::string& pageId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto threads = collaborationService_->listThreads(pageId);
        if (!threads) {
            return fail(threads.error());
        }

        std::string items = "[";
        bool first = true;
        for (const auto& thread : threads.value()) {
            if (!first) {
                items += ",";
            }
            first = false;
            items += commentThreadToJson(thread);
        }
        items += "]";

        return ok("{\"items\":" + items + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::listCommentHistory(const std::string& pageId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto threads = collaborationService_->listHistory(pageId);
        if (!threads) {
            return fail(threads.error());
        }

        std::string items = "[";
        bool first = true;
        for (const auto& thread : threads.value()) {
            if (!first) {
                items += ",";
            }
            first = false;
            items += commentThreadToJson(thread);
        }
        items += "]";

        return ok("{\"items\":" + items + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::createComment(const std::string& pageId, const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
        const auto thread = collaborationService_->createThread(
            pageId,
            services::CommentThreadDraft{
                .author = parsedPayload.value("author", std::string("viewer")),
                .body = parsedPayload.value("body", std::string{}),
                .selectionLabel = parsedPayload.value("selectionLabel", std::string{}),
                .targetId = parsedPayload.value("targetId", std::string{}),
                .targetType = parsedPayload.value("targetType", std::string("paragraph")),
                .targetPreview = parsedPayload.value("targetPreview", std::string{}),
            });
        if (!thread) {
            return fail(thread.error());
        }

        return created("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed comment JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::replyToComment(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
        const auto thread = collaborationService_->addReply(
            pageId,
            threadId,
            services::CommentReplyDraft{
                .author = parsedPayload.value("author", std::string("viewer")),
                .body = parsedPayload.value("body", std::string{}),
                .replyToMessageId = parsedPayload.value("replyToMessageId", std::string{}),
            });
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed reply JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::updateCommentMessage(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& messageId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
        const auto thread = collaborationService_->updateMessage(
            pageId,
            threadId,
            messageId,
            parsedPayload.value("body", std::string{}));
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed comment edit JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::deleteCommentMessage(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& messageId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        std::string author = "viewer";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            author = parsedPayload.value("author", author);
        }

        const auto thread = collaborationService_->deleteMessage(pageId, threadId, messageId, author);
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed comment delete JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::deleteCommentThread(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        std::string author = "viewer";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            author = parsedPayload.value("author", author);
        }

        const auto thread = collaborationService_->deleteThread(pageId, threadId, author);
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed thread delete JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::resolveComment(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        bool resolved = true;
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            resolved = parsedPayload.value("resolved", true);
        }

        const auto thread = collaborationService_->setResolved(pageId, threadId, resolved);
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed resolve JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::toggleCommentLike(
    const std::string& pageId,
    const std::string& threadId,
    const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        std::string author = "viewer";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            author = parsedPayload.value("author", author);
        }

        const auto thread = collaborationService_->toggleLike(pageId, threadId, author);
        if (!thread) {
            return fail(thread.error());
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed like JSON payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::getCommentAccess(const std::string& pageId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto accessMode = collaborationService_->getCommentAccess(pageId);
        if (!accessMode) {
            return fail(accessMode.error());
        }

        return ok("{\"mode\":\"" + utils::escapeJson(accessMode.value()) + "\"}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::setCommentAccess(const std::string& pageId, const std::string& payload) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        std::string mode = "all_users";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            mode = parsedPayload.value("mode", mode);
        }

        const auto savedMode = collaborationService_->setCommentAccess(pageId, mode);
        if (!savedMode) {
            return fail(savedMode.error());
        }

        return ok("{\"mode\":\"" + utils::escapeJson(savedMode.value()) + "\"}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed comment access JSON payload: ") + exception.what(),
            400,
            false));
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

RouteResponse Router::getMwsInsertOptions(const std::string& tableId, const std::string& viewId) {
    try {
        if (mwsClient_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is not configured",
                503,
                false));
        }

        const auto resolvedTableId = tableId.empty() ? mwsClient_->tableId() : tableId;
        const auto resolvedViewId = tableId.empty() ? mwsClient_->viewId() : viewId;
        const auto records = mwsClient_->getRecordsForTable(resolvedTableId, resolvedViewId);
        if (!records) {
            return fail(records.error());
        }

        std::string activeLabel = "Пользовательская таблица";
        std::string activeRole = "data";
        for (const auto& preset : tablePresets_) {
            if (preset.tableId == resolvedTableId && preset.viewId == resolvedViewId) {
                activeLabel = preset.label;
                activeRole = preset.role;
                break;
            }
        }

        nlohmann::json payload = {
            {"tableId", resolvedTableId},
            {"viewId", resolvedViewId},
            {"activeTable", {
                {"tableId", resolvedTableId},
                {"viewId", resolvedViewId},
                {"label", activeLabel},
                {"role", activeRole},
            }},
            {"tablePresets", nlohmann::json::array()},
            {"records", nlohmann::json::array()},
            {"fieldNames", nlohmann::json::array()},
        };

        for (const auto& preset : tablePresets_) {
            payload["tablePresets"].push_back({
                {"key", preset.key},
                {"label", preset.label},
                {"tableId", preset.tableId},
                {"viewId", preset.viewId},
                {"role", preset.role},
            });
        }

        std::unordered_set<std::string> fieldNames;
        for (const auto& record : records.value()) {
            nlohmann::json fieldsJson = nlohmann::json::object();
            nlohmann::json fieldMetaJson = nlohmann::json::object();
            for (const auto& [fieldName, fieldValue] : record.fields) {
                fieldsJson[fieldName] = fieldValue;
                fieldNames.insert(fieldName);

                nlohmann::json meta = {
                    {"value", fieldValue},
                    {"resourceUrl", ""},
                    {"mimeType", ""},
                    {"isImage", false},
                };
                if (const auto rawIt = record.rawFieldsJson.find(fieldName); rawIt != record.rawFieldsJson.end()) {
                    try {
                        applyFieldMeta(nlohmann::json::parse(rawIt->second), meta);
                    } catch (...) {
                    }
                }
                fieldMetaJson[fieldName] = std::move(meta);
            }

            payload["records"].push_back({
                {"recordId", record.recordId},
                {"fields", std::move(fieldsJson)},
                {"fieldMeta", std::move(fieldMetaJson)},
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
