#include "src/server/router.h"

#include <algorithm>
#include <exception>
#include <unordered_set>
#include <vector>
#include <utility>

#include <nlohmann/json.hpp>

#include "src/utils/string_utils.h"

namespace {

std::string toJsonArray(const std::vector<std::string>& items) {
    std::string result = "[";
    bool first = true;
    for (const auto& item : items) {
        if (!first) {
            result += ",";
        }
        first = false;
        result += "\"" + wikilive::utils::escapeJson(item) + "\"";
    }
    result += "]";
    return result;
}


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
        const auto url = value["url"].get<std::string>();
        meta["resourceUrl"] = makeAbsoluteTablesUrl(url);
        if (!meta.contains("attachments") || !meta["attachments"].is_array()) {
            meta["attachments"] = nlohmann::json::array();
        }
        nlohmann::json attachment{
            {"url", url},
            {"resourceUrl", makeAbsoluteTablesUrl(url)},
            {"name", value.value("name", value.value("fileName", std::string{}))},
            {"mimeType", value.value("mimeType", std::string{})},
        };
        const auto mimeType = attachment.value("mimeType", std::string{});
        attachment["isImage"] = mimeType.rfind("image/", 0) == 0;
        meta["attachments"].push_back(attachment);
        meta["isAttachment"] = true;
    }

    if (value.contains("mimeType") && value["mimeType"].is_string()) {
        const auto mimeType = value["mimeType"].get<std::string>();
        meta["mimeType"] = mimeType;
        meta["isImage"] = mimeType.rfind("image/", 0) == 0;
    }
}

std::vector<std::string> parseCsvList(const std::string& value) {
    std::vector<std::string> items;
    for (const auto& rawItem : wikilive::utils::split(value, ',')) {
        const auto item = wikilive::utils::trim(rawItem);
        if (!item.empty()) {
            items.push_back(item);
        }
    }
    return items;
}

std::vector<std::string> resolveRequestedFieldNames(
    const std::vector<std::string>& requestedFields,
    const std::unordered_set<std::string>& discoveredFields) {
    if (!requestedFields.empty()) {
        return requestedFields;
    }

    std::vector<std::string> sortedFieldNames(discoveredFields.begin(), discoveredFields.end());
    std::sort(sortedFieldNames.begin(), sortedFieldNames.end());
    return sortedFieldNames;
}

nlohmann::json buildMwsGridPayload(
    const std::string& resolvedTableId,
    const std::string& resolvedViewId,
    const std::vector<wikilive::server::MwsTablePreset>& tablePresets,
    const std::vector<wikilive::api::MwsRecord>& records,
    const std::vector<std::string>& requestedFields) {
    std::string activeLabel = "Пользовательская таблица";
    std::string activeRole = "data";
    for (const auto& preset : tablePresets) {
        if (preset.tableId == resolvedTableId && preset.viewId == resolvedViewId) {
            activeLabel = preset.label;
            activeRole = preset.role;
            break;
        }
    }

    std::unordered_set<std::string> discoveredFields;
    for (const auto& record : records) {
        for (const auto& [fieldName, _] : record.fields) {
            discoveredFields.insert(fieldName);
        }
    }

    const auto fieldNames = resolveRequestedFieldNames(requestedFields, discoveredFields);
    const std::unordered_set<std::string> fieldFilter(fieldNames.begin(), fieldNames.end());

    nlohmann::json payload = {
        {"tableId", resolvedTableId},
        {"viewId", resolvedViewId},
        {"activeTable", {
            {"tableId", resolvedTableId},
            {"viewId", resolvedViewId},
            {"label", activeLabel},
            {"role", activeRole},
        }},
        {"records", nlohmann::json::array()},
        {"fieldNames", fieldNames},
    };

    for (const auto& record : records) {
        nlohmann::json fieldsJson = nlohmann::json::object();
        nlohmann::json fieldMetaJson = nlohmann::json::object();

        for (const auto& fieldName : fieldNames) {
            const auto fieldIt = record.fields.find(fieldName);
            if (fieldIt == record.fields.end()) {
                continue;
            }

            fieldsJson[fieldName] = fieldIt->second;
            nlohmann::json meta = {
                {"value", fieldIt->second},
                {"resourceUrl", ""},
                {"mimeType", ""},
                {"isImage", false},
                {"isAttachment", false},
                {"attachments", nlohmann::json::array()},
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

    return payload;
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
        "\",\"description\":\"" + wikilive::utils::escapeJson(page.description) +
        "\",\"content\":\"" + wikilive::utils::escapeJson(page.content) +
        "\",\"createdAt\":\"" + wikilive::utils::escapeJson(page.createdAt) +
        "\",\"updatedAt\":\"" + wikilive::utils::escapeJson(page.updatedAt) +
        "\",\"ownerId\":\"" + wikilive::utils::escapeJson(page.ownerId) +
        "\",\"ownerName\":\"" + wikilive::utils::escapeJson(page.ownerName) + "\"" + ",\"sharedWith\":" + toJsonArray(page.sharedWith);

    if (includeRenderedHtml) {
        json += ",\"renderedHtml\":\"" + wikilive::utils::escapeJson(page.renderedHtml) + "\"";
    }

    json += "}";
    return json;
}

std::string pageVersionToJson(const wikilive::models::PageVersion& version, const bool includeContent = true) {
    std::size_t threadCount = version.threadSnapshot.empty() ? version.threadCount : version.threadSnapshot.size();
    std::size_t messageCount = version.threadSnapshot.empty() ? version.commentCount : 0;
    if (!version.threadSnapshot.empty()) {
        for (const auto& thread : version.threadSnapshot) {
            messageCount += thread.messages.size();
        }
    }

    nlohmann::json payload{
        {"versionId", version.versionId},
        {"pageId", version.pageId},
        {"title", version.title},
        {"description", version.description},
        {"createdAt", version.createdAt},
        {"label", version.label},
        {"author", version.author},
        {"sharedWith", version.sharedWith},
        {"commentAccessMode", version.commentAccessMode},
        {"threadCount", threadCount},
        {"commentCount", messageCount},
    };

    if (includeContent) {
        payload["content"] = version.content;
    }

    return payload.dump();
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
            {"likedBy", message.likedBy},
            {"likeCount", message.likedBy.size()},
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
        {"paused", thread.paused},
        {"pausedAt", thread.pausedAt},
        {"pausedBy", thread.pausedBy},
        {"deleted", thread.deleted},
        {"deletedAt", thread.deletedAt},
        {"deletedBy", thread.deletedBy},
        {"likedBy", thread.likedBy},
        {"likeCount", thread.messages.empty() ? thread.likedBy.size() : thread.messages.front().likedBy.size()},
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
          std::move(tablePresets),
          nullptr) {
}

Router::Router(
    services::PageService& pageService,
    services::RenderService& renderService,
    api::MwsClient* mwsClient,
    ai::AiService* aiService,
    services::CollaborationService* collaborationService,
    WebSocketManager* webSocketManager,
    std::vector<MwsTablePreset> tablePresets,
    std::unique_ptr<storage::LocalUserStorage> userStorage,
    services::AuthService* authService)
    : pageService_(pageService),
      renderService_(renderService),
      mwsClient_(mwsClient),
      aiService_(aiService),
      collaborationService_(collaborationService),
      webSocketManager_(webSocketManager),
      tablePresets_(std::move(tablePresets)),
      userStorage_(std::move(userStorage)),
      authService_(authService) {
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

        const auto versionLabel = extractJsonString(payload, "versionLabel", false);
        if (!versionLabel) {
            return fail(versionLabel.error());
        }
        const auto versionAuthor = extractJsonString(payload, "versionAuthor", false);
        if (!versionAuthor) {
            return fail(versionAuthor.error());
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
            const auto versionResult = collaborationService_->captureVersion(
                createdPage.value(),
                versionLabel.value().empty() ? "Created page" : versionLabel.value(),
                versionAuthor.value().empty() ? "system" : versionAuthor.value());
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

        const auto versionLabel = extractJsonString(payload, "versionLabel", false);
        if (!versionLabel) {
            return fail(versionLabel.error());
        }
        const auto versionAuthor = extractJsonString(payload, "versionAuthor", false);
        if (!versionAuthor) {
            return fail(versionAuthor.error());
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
            const auto versionResult = collaborationService_->captureVersion(
                updatedPage.value(),
                versionLabel.value().empty() ? "Saved changes" : versionLabel.value(),
                versionAuthor.value().empty() ? "system" : versionAuthor.value());
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
            items += pageVersionToJson(version, false);
        }
        items += "]";

        return ok("{\"items\":" + items + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::getVersion(const std::string& pageId, const std::string& versionId) {
    try {
        if (collaborationService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Collaboration service is not configured",
                503,
                false));
        }

        const auto version = collaborationService_->getVersion(pageId, versionId);
        if (!version) {
            return fail(version.error());
        }

        return ok("{\"item\":" + pageVersionToJson(version.value(), true) + "}");
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

        return created("{\"item\":" + pageVersionToJson(version.value(), false) + "}");
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

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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
        const auto author = parsedPayload.value("author", std::string("viewer"));
        const auto thread = collaborationService_->updateMessage(
            pageId,
            threadId,
            messageId,
            parsedPayload.value("body", std::string{}),
            author);
        if (!thread) {
            return fail(thread.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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
        std::string author = "viewer";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            resolved = parsedPayload.value("resolved", true);
            author = parsedPayload.value("author", author);
        }

        const auto thread = collaborationService_->setResolved(pageId, threadId, resolved, author);
        if (!thread) {
            return fail(thread.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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

RouteResponse Router::pauseComment(
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

        bool paused = true;
        std::string author = "viewer";
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            paused = parsedPayload.value("paused", true);
            author = parsedPayload.value("author", author);
        }

        const auto thread = collaborationService_->setPaused(pageId, threadId, paused, author);
        if (!thread) {
            return fail(thread.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
        }

        return ok("{\"item\":" + commentThreadToJson(thread.value()) + "}");
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed pause JSON payload: ") + exception.what(),
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
        std::string messageId;
        if (!payload.empty()) {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            author = parsedPayload.value("author", author);
            messageId = parsedPayload.value("messageId", std::string{});
        }

        const auto thread = collaborationService_->toggleLike(pageId, threadId, messageId, author);
        if (!thread) {
            return fail(thread.error());
        }

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.changed");
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

        if (webSocketManager_ != nullptr) {
            webSocketManager_->broadcastPageEvent(pageId, "comments.access.changed");
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
        const auto resolvedViewId = viewId.empty() ? mwsClient_->viewId() : viewId;
        const auto records = mwsClient_->getRecordsForTable(resolvedTableId, resolvedViewId);
        if (!records) {
            return fail(records.error());
        }

        nlohmann::json payload = buildMwsGridPayload(
            resolvedTableId,
            resolvedViewId,
            tablePresets_,
            records.value(),
            {});
        payload["tablePresets"] = nlohmann::json::array();

        for (const auto& preset : tablePresets_) {
            payload["tablePresets"].push_back({
                {"key", preset.key},
                {"label", preset.label},
                {"tableId", preset.tableId},
                {"viewId", preset.viewId},
                {"role", preset.role},
            });
        }

        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::getMwsGrid(
    const std::string& tableId,
    const std::string& viewId,
    const std::string& recordIdsCsv,
    const std::string& fieldNamesCsv) {
    try {
        if (mwsClient_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is not configured",
                503,
                false));
        }

        const auto resolvedTableId = tableId.empty() ? mwsClient_->tableId() : tableId;
        const auto resolvedViewId = viewId.empty() ? mwsClient_->viewId() : viewId;
        const auto recordIds = parseCsvList(recordIdsCsv);
        const auto fieldNames = parseCsvList(fieldNamesCsv);
        const auto records = mwsClient_->getRecordsForTable(resolvedTableId, resolvedViewId, recordIds);
        if (!records) {
            return fail(records.error());
        }

        const auto payload = buildMwsGridPayload(
            resolvedTableId,
            resolvedViewId,
            tablePresets_,
            records.value(),
            fieldNames);
        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::updateMwsGrid(const std::string& payload) {
    try {
        if (mwsClient_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "MWS client is not configured",
                503,
                false));
        }

        if (payload.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "MWS grid payload must not be empty",
                400,
                false));
        }

        const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
        const auto resolvedTableId = parsed.value("tableId", mwsClient_->tableId());
        const auto resolvedViewId = parsed.value("viewId", mwsClient_->viewId());
        const auto fieldNames = parsed.contains("fieldNames") && parsed["fieldNames"].is_array()
            ? parsed["fieldNames"].get<std::vector<std::string>>()
            : std::vector<std::string>{};
        const auto recordIds = parsed.contains("recordIds") && parsed["recordIds"].is_array()
            ? parsed["recordIds"].get<std::vector<std::string>>()
            : std::vector<std::string>{};

        if (!parsed.contains("updates") || !parsed["updates"].is_array()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "MWS grid updates must be an array",
                400,
                false));
        }

        std::vector<std::string> touchedRecordIds;
        for (const auto& update : parsed["updates"]) {
            if (!update.is_object()) {
                continue;
            }

            const auto recordId = update.value("recordId", std::string{});
            if (recordId.empty()) {
                return fail(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "Each MWS grid update must include recordId",
                    400,
                    false));
            }

            if (!update.contains("fields") || !update["fields"].is_object()) {
                return fail(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "Each MWS grid update must include object field: fields",
                    400,
                    false));
            }

            nlohmann::json updatePayload = {
                {"records", nlohmann::json::array({
                    {
                        {"recordId", recordId},
                        {"fields", update["fields"]},
                    },
                })},
            };

            const auto result = mwsClient_->updateRecordForTable(
                resolvedTableId,
                resolvedViewId,
                recordId,
                updatePayload.dump());
            if (!result) {
                return fail(result.error());
            }

            touchedRecordIds.push_back(recordId);
        }

        const auto refreshedRecordIds = recordIds.empty() ? touchedRecordIds : recordIds;
        const auto refreshed = mwsClient_->getRecordsForTable(resolvedTableId, resolvedViewId, refreshedRecordIds);
        if (!refreshed) {
            return fail(refreshed.error());
        }

        const auto responsePayload = buildMwsGridPayload(
            resolvedTableId,
            resolvedViewId,
            tablePresets_,
            refreshed.value(),
            fieldNames);
        return ok(responsePayload.dump());
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed MWS grid JSON payload: ") + exception.what(),
            400,
            false));
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

    auto description = extractJsonString(payload, "description", false);
    if (!description) {
        return std::unexpected(description.error());
    }

    auto ownerId = extractJsonString(payload, "ownerId", false);
    if (!ownerId) {
        return std::unexpected(ownerId.error());
    }

    auto ownerName = extractJsonString(payload, "ownerName", false);
    if (!ownerName) {
        return std::unexpected(ownerName.error());
    }

    bool sharedWithProvided = false;
    std::vector<std::string> sharedWith;
    if (payload.find("\"sharedWith\"") != std::string::npos) {
        try {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            if (parsedPayload.contains("sharedWith")) {
                sharedWithProvided = true;
                if (!parsedPayload["sharedWith"].is_array()) {
                    return std::unexpected(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Expected array field: sharedWith",
                        400,
                        false));
                }
                for (const auto& item : parsedPayload["sharedWith"]) {
                    if (item.is_string()) {
                        sharedWith.push_back(item.get<std::string>());
                    }
                }
            }
        } catch (const std::exception& exception) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                std::string("Failed to parse sharedWith: ") + exception.what(),
                400,
                false));
        }
    }

    return services::PageDraft{
        .title = title.value(),
        .description = description.value(),
        .content = content.value(),
        .ownerId = ownerId.value(),
        .ownerName = ownerName.value(),
        .sharedWith = sharedWith,
        .sharedWithProvided = sharedWithProvided,
    };
}

RouteResponse Router::listUsers() {
    try {
        nlohmann::json payload;
        payload["users"] = nlohmann::json::array();
        if (userStorage_ != nullptr) {
            const auto users = userStorage_->listUsers();
            if (!users) {
                return fail(users.error());
            }
            for (const auto& user : users.value()) {
                payload["users"].push_back({
                    {"id", user.id},
                    {"name", user.name},
                    {"email", user.email},
                    {"role", user.role},
                    {"team", user.team},
                    {"groups", user.groups},
                });
            }
        }
        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::listGroups() {
    try {
        nlohmann::json payload;
        payload["groups"] = nlohmann::json::array();
        if (userStorage_ != nullptr) {
            const auto groups = userStorage_->listGroups();
            if (!groups) {
                return fail(groups.error());
            }
            for (const auto& group : groups.value()) {
                payload["groups"].push_back({
                    {"id", group.id},
                    {"name", group.name},
                    {"members", group.members},
                });
            }
        }
        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::login(const std::string& payload) {
    try {
        if (authService_ == nullptr) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Auth service is not configured",
                503,
                false));
        }

        if (payload.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Auth payload must not be empty",
                400,
                false));
        }

        const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
        const auto email = parsed.value("email", std::string{});
        const auto password = parsed.value("password", std::string{});

        const auto user = authService_->login(email, password);
        if (!user) {
            return fail(user.error());
        }

        const auto& info = user.value();
        nlohmann::json response{
            {"user", {
                {"id", info.id},
                {"name", info.name},
                {"email", info.email},
                {"role", info.role},
                {"team", info.team},
                {"groups", info.groups},
            }},
        };
        return ok(response.dump());
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed auth payload: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
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

utils::Expected<std::vector<std::string>> Router::extractJsonStringArray(
    const std::string& payload,
    const std::string& key,
    const bool required) const {
    try {
        auto parsed = nlohmann::json::parse(payload);
        if (!parsed.contains(key)) {
            if (!required) {
                return std::vector<std::string>{};
            }
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Missing JSON field: " + key,
                400,
                false));
        }

        if (!parsed[key].is_array()) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Expected array field: " + key,
                400,
                false));
        }

        std::vector<std::string> result;
        for (const auto& item : parsed[key]) {
            if (!item.is_string()) {
                continue;
            }
            result.push_back(item.get<std::string>());
        }
        return result;
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Failed to parse array field: ") + exception.what(),
            400,
            false));
    }
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
