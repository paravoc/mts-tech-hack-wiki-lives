#include "src/server/router.h"

#include <algorithm>
#include <cctype>
#include <exception>
#include <filesystem>
#include <fstream>
#include <optional>
#include <unordered_set>
#include <vector>
#include <utility>
#include "src/security/access_evaluator.h"
#include "src/services/project_service.h"


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

std::string pageAccessToJson(const wikilive::models::PageAccess& access) {
    nlohmann::json payload{
        {"public", access.publicAccess},
        {"users", access.userIds},
        {"groups", access.groupIds},
        {"roles", access.roles},
    };
    return payload.dump();
}

std::string toLower(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

bool containsValue(const std::vector<std::string>& items, const std::string& value) {
    return std::any_of(items.begin(), items.end(), [&](const std::string& item) {
        return item == value;
    });
}

std::optional<wikilive::models::User> findUserByToken(
    const std::vector<wikilive::models::User>& users,
    const std::string& token) {
    if (token.empty()) {
        return std::nullopt;
    }
    const auto normalized = toLower(token);
    for (const auto& user : users) {
        if (toLower(user.id) == normalized || toLower(user.email) == normalized) {
            return user;
        }
    }
    return std::nullopt;
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

struct ParsedTableLink {
    std::string tableId;
    std::string viewId;
};

std::optional<ParsedTableLink> parseMwsTableLink(const std::string& rawValue) {
    const auto trimmed = wikilive::utils::trim(rawValue);
    if (trimmed.empty()) {
        return std::nullopt;
    }

    std::string tail;
    const std::string workbenchMarker = "workbench/";
    const auto workbenchPos = trimmed.find(workbenchMarker);
    if (workbenchPos != std::string::npos) {
        tail = trimmed.substr(workbenchPos + workbenchMarker.size());
    } else if (trimmed.rfind("dst", 0) == 0) {
        tail = trimmed;
    } else {
        return std::nullopt;
    }

    const auto fragmentPos = tail.find_first_of("?#");
    if (fragmentPos != std::string::npos) {
        tail = tail.substr(0, fragmentPos);
    }

    while (!tail.empty() && tail.front() == '/') {
        tail.erase(tail.begin());
    }

    if (tail.empty()) {
        return std::nullopt;
    }

    ParsedTableLink parsed;
    const auto slashPos = tail.find('/');
    if (slashPos == std::string::npos) {
        parsed.tableId = tail;
        return parsed;
    }

    parsed.tableId = tail.substr(0, slashPos);
    auto rest = tail.substr(slashPos + 1);
    const auto nextSlash = rest.find('/');
    parsed.viewId = nextSlash == std::string::npos ? rest : rest.substr(0, nextSlash);
    return parsed;
}

ParsedTableLink resolveTableSelection(
    const wikilive::api::MwsClient* client,
    const std::string& tableId,
    const std::string& viewId,
    const std::string& tableUrl = {}) {
    ParsedTableLink selection;
    selection.tableId = tableId;
    selection.viewId = viewId;

    const std::string candidate = tableUrl.empty() ? tableId : tableUrl;
    if (const auto parsed = parseMwsTableLink(candidate)) {
        selection.tableId = parsed->tableId;
        if (!parsed->viewId.empty()) {
            selection.viewId = parsed->viewId;
        }
    }

    if (selection.tableId.empty() && client != nullptr) {
        selection.tableId = client->tableId();
    }
    if (selection.viewId.empty() && client != nullptr) {
        selection.viewId = client->viewId();
    }

    return selection;
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

std::vector<unsigned char> decodeBase64(const std::string& input, bool& ok) {
    static const std::string kTable =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789+/";
    std::vector<int> reverseTable(256, -1);
    for (std::size_t i = 0; i < kTable.size(); ++i) {
        reverseTable[static_cast<unsigned char>(kTable[i])] = static_cast<int>(i);
    }

    ok = true;
    std::vector<unsigned char> output;
    int val = 0;
    int valb = -8;
    for (unsigned char c : input) {
        if (c == '=') {
            break;
        }
        const int decoded = reverseTable[c];
        if (decoded == -1) {
            if (c == '\r' || c == '\n' || c == ' ' || c == '\t') {
                continue;
            }
            ok = false;
            return {};
        }
        val = (val << 6) + decoded;
        valb += 6;
        if (valb >= 0) {
            output.push_back(static_cast<unsigned char>((val >> valb) & 0xFF));
            valb -= 8;
        }
    }
    return output;
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

wikilive::utils::Expected<wikilive::models::ProjectDraft> parseProjectDraft(const std::string& payload) {
    if (payload.empty()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::InvalidRequest,
            "Project payload must not be empty",
            400,
            false));
    }

    const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);

    const auto name = parsed.value("name", std::string{});
    if (name.empty()) {
        return std::unexpected(wikilive::utils::makeError(
            wikilive::utils::ErrorCode::InvalidRequest,
            "Project name must not be empty",
            400,
            false));
    }

    wikilive::models::ProjectDraft draft;
    draft.name = name;
    draft.description = parsed.value("description", std::string{});
    draft.ownerId = parsed.value("ownerId", std::string{});
    if (draft.ownerId.empty()) {
        draft.ownerId = parsed.value("actorId", std::string{});
    }
    if (draft.ownerId.empty()) {
        draft.ownerId = parsed.value("actorEmail", std::string{});
    }
    draft.ownerName = parsed.value("ownerName", std::string{});

    if (parsed.contains("sharedWith")) {
        if (!parsed["sharedWith"].is_array()) {
            return std::unexpected(wikilive::utils::makeError(
                wikilive::utils::ErrorCode::InvalidRequest,
                "Expected array field: sharedWith",
                400,
                false));
        }

        for (const auto& item : parsed["sharedWith"]) {
            if (item.is_string()) {
                draft.sharedWith.push_back(item.get<std::string>());
            }
        }
    }

    if (parsed.contains("access") && parsed["access"].is_object()) {
        const auto& accessJson = parsed["access"];
        draft.access.publicAccess = accessJson.value("public", false);

        if (accessJson.contains("users") && accessJson["users"].is_array()) {
            for (const auto& item : accessJson["users"]) {
                if (item.is_string()) {
                    draft.access.userIds.push_back(item.get<std::string>());
                }
            }
        }

        if (accessJson.contains("groups") && accessJson["groups"].is_array()) {
            for (const auto& item : accessJson["groups"]) {
                if (item.is_string()) {
                    draft.access.groupIds.push_back(item.get<std::string>());
                }
            }
        }

        if (accessJson.contains("roles") && accessJson["roles"].is_array()) {
            for (const auto& item : accessJson["roles"]) {
                if (item.is_string()) {
                    draft.access.roles.push_back(item.get<std::string>());
                }
            }
        }
    }

    return draft;
}
std::string projectToJson(const wikilive::models::Project& project) {
    std::string json =
        "{\"projectId\":\"" + wikilive::utils::escapeJson(project.projectId) +
        "\",\"name\":\"" + wikilive::utils::escapeJson(project.name) +
        "\",\"description\":\"" + wikilive::utils::escapeJson(project.description) +
        "\",\"createdAt\":\"" + wikilive::utils::escapeJson(project.createdAt) +
        "\",\"updatedAt\":\"" + wikilive::utils::escapeJson(project.updatedAt) +
        "\",\"ownerId\":\"" + wikilive::utils::escapeJson(project.ownerId) +
        "\",\"ownerName\":\"" + wikilive::utils::escapeJson(project.ownerName) +
        "\",\"sharedWith\":" + toJsonArray(project.sharedWith);

    json += ",\"access\":" + pageAccessToJson(project.access);
    json += "}";

    return json;
}

std::string pageToJson(const wikilive::models::Page& page, const bool includeRenderedHtml) {
    std::string json =
        "{\"pageId\":\"" + wikilive::utils::escapeJson(page.pageId) +
        "\",\"projectId\":\"" + wikilive::utils::escapeJson(page.projectId) +
        "\",\"title\":\"" + wikilive::utils::escapeJson(page.title) +
        "\",\"description\":\"" + wikilive::utils::escapeJson(page.description) +
        "\",\"content\":\"" + wikilive::utils::escapeJson(page.content) +
        "\",\"createdAt\":\"" + wikilive::utils::escapeJson(page.createdAt) +
        "\",\"updatedAt\":\"" + wikilive::utils::escapeJson(page.updatedAt) +
        "\",\"ownerId\":\"" + wikilive::utils::escapeJson(page.ownerId) +
        "\",\"ownerName\":\"" + wikilive::utils::escapeJson(page.ownerName) + "\"" + ",\"sharedWith\":" + toJsonArray(page.sharedWith);

    json += ",\"access\":" + pageAccessToJson(page.access);

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
        {"projectId", version.projectId},
        {"title", version.title},
        {"description", version.description},
        {"createdAt", version.createdAt},
        {"label", version.label},
        {"author", version.author},
        {"sharedWith", version.sharedWith},
        {"access", nlohmann::json::parse(pageAccessToJson(version.access))},
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
        {"anchor", {
            {"anchorId", thread.anchor.anchorId},
            {"quote", thread.anchor.quote},
            {"selector", thread.anchor.selector},
            {"blockId", thread.anchor.blockId},
            {"blockType", thread.anchor.blockType},
            {"startOffset", thread.anchor.startOffset},
            {"endOffset", thread.anchor.endOffset},
        }},
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
        services::ProjectService* projectService,
        ai::AiService* aiService,
        services::CollaborationService* collaborationService,
        WebSocketManager* webSocketManager,
        std::vector<MwsTablePreset> tablePresets)
        : Router(
            pageService,
            renderService,
            nullptr,
            projectService,
            aiService,
            collaborationService,
            webSocketManager,
            std::move(tablePresets),
            nullptr,
            nullptr) {
    }

    Router::Router(
        services::PageService& pageService,
        services::RenderService& renderService,
        api::MwsClient* mwsClient,
        services::ProjectService* projectService,
        ai::AiService* aiService,
        services::CollaborationService* collaborationService,
        WebSocketManager* webSocketManager,
        std::vector<MwsTablePreset> tablePresets,
        std::unique_ptr<storage::LocalUserStorage> userStorage,
        services::AuthService* authService)
        : pageService_(pageService),
        renderService_(renderService),
        mwsClient_(mwsClient),
        projectService_(projectService),
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

RouteResponse Router::listPagesForActor(const std::string& actorId) {
    try {
        const auto pages = pageService_.listPages();
        if (!pages) {
            return fail(pages.error());
        }

        std::vector<models::User> users;
        if (userStorage_ != nullptr) {
            const auto usersResult = userStorage_->listUsers();
            if (!usersResult) {
                return fail(usersResult.error());
            }
            users = usersResult.value();
        }

        const auto normalizedActor = toLower(actorId);
        const models::User* actor = nullptr;
        for (const auto& user : users) {
            if (toLower(user.id) == normalizedActor || toLower(user.email) == normalizedActor) {
                actor = &user;
                break;
            }
        }

        const auto accessActor = actor != nullptr
            ? security::makeAccessActor(*actor)
            : security::AccessActor{.userId = actorId, .email = actorId};

        std::string items = "[";
        bool first = true;
        for (const auto& page : pages.value()) {
            bool visible = page.access.publicAccess;
            if (projectService_ != nullptr && !page.projectId.empty()) {
                const auto project = projectService_->getProject(page.projectId);
                if (project) {
                    visible = security::canReadPage(accessActor, project.value(), page);
                } else if (!actorId.empty()) {
                    visible = security::hasDirectAccess(accessActor, page.access);
                }
            } else if (!actorId.empty()) {
                visible = security::hasDirectAccess(accessActor, page.access);
            }

            if (!visible) {
                continue;
            }

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

RouteResponse Router::listPagesForProject(const std::string& projectId, const std::string& actorId) {
    try {
        if (projectId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "projectId must not be empty",
                400,
                false));
        }

        const auto pages = pageService_.listPages();
        if (!pages) {
            return fail(pages.error());
        }

        std::optional<models::Project> project;
        if (projectService_ != nullptr) {
            const auto projectResult = projectService_->getProject(projectId);
            if (!projectResult) {
                return fail(projectResult.error());
            }
            project = projectResult.value();
        }

        std::vector<models::User> users;
        if (userStorage_ != nullptr && !actorId.empty()) {
            const auto usersResult = userStorage_->listUsers();
            if (!usersResult) {
                return fail(usersResult.error());
            }
            users = usersResult.value();
        }

        const auto actorOpt = actorId.empty() ? std::nullopt : findUserByToken(users, actorId);
        const auto accessActor = actorOpt
            ? security::makeAccessActor(*actorOpt)
            : security::AccessActor{.userId = actorId, .email = actorId};

        std::string items = "[";
        bool first = true;
        for (const auto& page : pages.value()) {
            if (page.projectId != projectId) {
                continue;
            }

            bool visible = page.access.publicAccess;
            if (project.has_value()) {
                visible = security::canReadPage(accessActor, project.value(), page);
            } else if (!actorId.empty()) {
                visible = security::hasDirectAccess(accessActor, page.access);
            }

            if (!visible) {
                continue;
            }

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

RouteResponse Router::getPage(const std::string& pageId, const std::string& actorId) {
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

        if (!actorId.empty() && userStorage_ != nullptr) {
            const auto usersResult = userStorage_->listUsers();
            if (!usersResult) {
                return fail(usersResult.error());
            }
            const auto userOpt = findUserByToken(usersResult.value(), actorId);
            const auto actor = userOpt
                ? security::makeAccessActor(*userOpt)
                : security::AccessActor{.userId = actorId, .email = actorId};

            if (projectService_ != nullptr && !page->projectId.empty()) {
                const auto projectResult = projectService_->getProject(page->projectId);
                if (projectResult) {
                    if (!security::canReadPage(actor, projectResult.value(), page.value())) {
                        return fail(utils::makeError(
                            utils::ErrorCode::InvalidRequest,
                            "Access denied for page",
                            403,
                            false));
                    }
                } else if (!security::hasDirectAccess(actor, page->access)) {
                    return fail(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Access denied for page",
                        403,
                        false));
                }
            } else if (!security::hasDirectAccess(actor, page->access)) {
                return fail(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "Access denied for page",
                    403,
                    false));
            }
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

        std::string actorToken;
        try {
            const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
            actorToken = parsed.value("actorId", std::string{});
            if (actorToken.empty()) {
                actorToken = parsed.value("actorEmail", std::string{});
            }
            if (actorToken.empty()) {
                actorToken = parsed.value("ownerId", std::string{});
            }
        } catch (const nlohmann::json::exception&) {
        }

        if (projectService_ != nullptr) {
            const auto projectResult = projectService_->getProject(draft->projectId);
            if (!projectResult) {
                return fail(projectResult.error());
            }

            if (!actorToken.empty() && userStorage_ != nullptr) {
                const auto usersResult = userStorage_->listUsers();
                if (!usersResult) {
                    return fail(usersResult.error());
                }
                const auto userOpt = findUserByToken(usersResult.value(), actorToken);
                const auto actor = userOpt
                    ? security::makeAccessActor(*userOpt)
                    : security::AccessActor{.userId = actorToken, .email = actorToken};
                if (!security::canEditProject(actor, projectResult.value())) {
                    return fail(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Access denied for project",
                        403,
                        false));
                }
            }
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

        const auto existingPage = pageService_.getPage(pageId);
        if (!existingPage) {
            return fail(existingPage.error());
        }

        if (!draft->projectId.empty() && !existingPage->projectId.empty() &&
            draft->projectId != existingPage->projectId) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "projectId mismatch for page update",
                400,
                false));
        }

        std::string targetProjectId = existingPage->projectId.empty()
            ? draft->projectId
            : existingPage->projectId;

        std::string actorToken;
        try {
            const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
            actorToken = parsed.value("actorId", std::string{});
            if (actorToken.empty()) {
                actorToken = parsed.value("actorEmail", std::string{});
            }
            if (actorToken.empty()) {
                actorToken = parsed.value("ownerId", std::string{});
            }
        } catch (const nlohmann::json::exception&) {
        }

        if (projectService_ != nullptr) {
            if (targetProjectId.empty()) {
                const auto projectsResult = projectService_->listProjects();
                if (!projectsResult) {
                    return fail(projectsResult.error());
                }
                const auto& projects = projectsResult.value();
                if (projects.size() == 1) {
                    targetProjectId = projects.front().projectId;
                } else if (!existingPage->ownerId.empty()) {
                    for (const auto& project : projects) {
                        if (project.ownerId == existingPage->ownerId) {
                            targetProjectId = project.projectId;
                            break;
                        }
                    }
                }
            }

            if (targetProjectId.empty()) {
                return fail(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "projectId must not be empty for page update",
                    400,
                    false));
            }

            const auto projectResult = projectService_->getProject(targetProjectId);
            if (!projectResult) {
                return fail(projectResult.error());
            }

            if (!actorToken.empty() && userStorage_ != nullptr) {
                const auto usersResult = userStorage_->listUsers();
                if (!usersResult) {
                    return fail(usersResult.error());
                }
                const auto userOpt = findUserByToken(usersResult.value(), actorToken);
                const auto actor = userOpt
                    ? security::makeAccessActor(*userOpt)
                    : security::AccessActor{.userId = actorToken, .email = actorToken};
                if (!security::canEditPage(actor, projectResult.value(), existingPage.value())) {
                    return fail(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Access denied for page update",
                        403,
                        false));
                }
            }
        }

        const auto versionLabel = extractJsonString(payload, "versionLabel", false);
        if (!versionLabel) {
            return fail(versionLabel.error());
        }
        const auto versionAuthor = extractJsonString(payload, "versionAuthor", false);
        if (!versionAuthor) {
            return fail(versionAuthor.error());
        }
        bool skipVersion = false;
        try {
            const auto parsedPayload = nlohmann::json::parse(payload);
            if (parsedPayload.contains("skipVersion") && parsedPayload["skipVersion"].is_boolean()) {
                skipVersion = parsedPayload["skipVersion"].get<bool>();
            }
        } catch (const nlohmann::json::exception&) {
        }

        auto adjustedDraft = draft.value();
        if (adjustedDraft.projectId.empty()) {
            adjustedDraft.projectId = targetProjectId;
        }

        const auto updatedPage = pageService_.updatePage(pageId, adjustedDraft);
        if (!updatedPage) {
            return fail(updatedPage.error());
        }

        const auto renderedPage = renderService_.renderPage(updatedPage.value());
        if (!renderedPage) {
            return fail(renderedPage.error());
        }

        if (collaborationService_ != nullptr && !skipVersion) {
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

RouteResponse Router::getPageAccess(const std::string& pageId) {
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

        const auto& access = page->access;
        nlohmann::json payload{
            {"pageId", page->pageId},
            {"ownerId", page->ownerId},
            {"ownerName", page->ownerName},
            {"access", {
                {"public", access.publicAccess},
                {"users", access.userIds},
                {"groups", access.groupIds},
                {"roles", access.roles},
            }},
            {"sharedWith", page->sharedWith},
        };

        return ok(payload.dump());
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::setProjectAccess(const std::string& projectId, const std::string& payload) {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    if (payload.empty()) {
        return {
            .statusCode = 400,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Project access payload must not be empty",
                400,
                false)),
        };
    }

    nlohmann::json parsed;
    try {
        parsed = nlohmann::json::parse(payload);
    }
    catch (const std::exception& exception) {
        return {
            .statusCode = 400,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                std::string("Invalid project access JSON: ") + exception.what(),
                400,
                false)),
        };
    }

    const auto existing = projectService_->getProject(projectId);
    if (!existing) {
        return {
            .statusCode = existing.error().httpStatus,
            .body = buildErrorJson(existing.error()),
        };
    }

    std::string actorToken = parsed.value("actorId", std::string{});
    if (actorToken.empty()) {
        actorToken = parsed.value("actorEmail", std::string{});
    }
    if (!actorToken.empty() && userStorage_ != nullptr) {
        const auto usersResult = userStorage_->listUsers();
        if (!usersResult) {
            return {
                .statusCode = usersResult.error().httpStatus,
                .body = buildErrorJson(usersResult.error()),
            };
        }
        const auto userOpt = findUserByToken(usersResult.value(), actorToken);
        const auto actor = userOpt
            ? security::makeAccessActor(*userOpt)
            : security::AccessActor{.userId = actorToken, .email = actorToken};
        if (!security::canEditProjectAccess(actor, existing.value())) {
            return {
                .statusCode = 403,
                .body = buildErrorJson(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "Access denied for project",
                    403,
                    false)),
            };
        }
    }

    auto access = existing.value().access;

    if (parsed.contains("access") && parsed["access"].is_object()) {
        const auto& accessJson = parsed["access"];

        access.publicAccess = accessJson.value("public", access.publicAccess);

        if (accessJson.contains("users") && accessJson["users"].is_array()) {
            access.userIds.clear();
            for (const auto& item : accessJson["users"]) {
                if (item.is_string()) {
                    access.userIds.push_back(item.get<std::string>());
                }
            }
        }

        if (accessJson.contains("groups") && accessJson["groups"].is_array()) {
            access.groupIds.clear();
            for (const auto& item : accessJson["groups"]) {
                if (item.is_string()) {
                    access.groupIds.push_back(item.get<std::string>());
                }
            }
        }

        if (accessJson.contains("roles") && accessJson["roles"].is_array()) {
            access.roles.clear();
            for (const auto& item : accessJson["roles"]) {
                if (item.is_string()) {
                    access.roles.push_back(item.get<std::string>());
                }
            }
        }
    }
    else {
        if (parsed.contains("publicAccess") && parsed["publicAccess"].is_boolean()) {
            access.publicAccess = parsed["publicAccess"].get<bool>();
        }

        if (parsed.contains("accessUsers") && parsed["accessUsers"].is_array()) {
            access.userIds.clear();
            for (const auto& item : parsed["accessUsers"]) {
                if (item.is_string()) {
                    access.userIds.push_back(item.get<std::string>());
                }
            }
        }

        if (parsed.contains("accessGroups") && parsed["accessGroups"].is_array()) {
            access.groupIds.clear();
            for (const auto& item : parsed["accessGroups"]) {
                if (item.is_string()) {
                    access.groupIds.push_back(item.get<std::string>());
                }
            }
        }

        if (parsed.contains("accessRoles") && parsed["accessRoles"].is_array()) {
            access.roles.clear();
            for (const auto& item : parsed["accessRoles"]) {
                if (item.is_string()) {
                    access.roles.push_back(item.get<std::string>());
                }
            }
        }
    }

    const auto updated = projectService_->updateAccess(projectId, access);
    if (!updated) {
        return {
            .statusCode = updated.error().httpStatus,
            .body = buildErrorJson(updated.error()),
        };
    }

    const auto refreshed = projectService_->getProject(projectId);
    if (!refreshed) {
        return {
            .statusCode = refreshed.error().httpStatus,
            .body = buildErrorJson(refreshed.error()),
        };
    }

    return {
        .statusCode = 200,
        .body = buildSuccessJson(projectToJson(refreshed.value())),
    };
}

RouteResponse Router::getProject(const std::string& projectId, const std::string& actorId) {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    const auto project = projectService_->getProject(projectId);
    if (!project) {
        return {
            .statusCode = project.error().httpStatus,
            .body = buildErrorJson(project.error()),
        };
    }

    if (!actorId.empty() && userStorage_ != nullptr) {
        const auto usersResult = userStorage_->listUsers();
        if (!usersResult) {
            return {
                .statusCode = usersResult.error().httpStatus,
                .body = buildErrorJson(usersResult.error()),
            };
        }
        const auto userOpt = findUserByToken(usersResult.value(), actorId);
        const auto actor = userOpt
            ? security::makeAccessActor(*userOpt)
            : security::AccessActor{.userId = actorId, .email = actorId};
        if (!security::canReadProject(actor, project.value())) {
            return {
                .statusCode = 403,
                .body = buildErrorJson(utils::makeError(
                    utils::ErrorCode::InvalidRequest,
                    "Access denied for project",
                    403,
                    false)),
            };
        }
    }

    return {
        .statusCode = 200,
        .body = buildSuccessJson(projectToJson(project.value())),
    };
}

RouteResponse Router::createProject(const std::string& payload) {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    const auto draft = parseProjectDraft(payload);
    if (!draft) {
        return {
            .statusCode = draft.error().httpStatus,
            .body = buildErrorJson(draft.error()),
        };
    }

    auto resolvedDraft = draft.value();
    if (resolvedDraft.ownerName.empty() && userStorage_ != nullptr && !resolvedDraft.ownerId.empty()) {
        const auto usersResult = userStorage_->listUsers();
        if (usersResult) {
            const auto userOpt = findUserByToken(usersResult.value(), resolvedDraft.ownerId);
            if (userOpt) {
                resolvedDraft.ownerName = userOpt->name;
            }
        }
    }

    const auto created = projectService_->createProject(resolvedDraft);
    if (!created) {
        return {
            .statusCode = created.error().httpStatus,
            .body = buildErrorJson(created.error()),
        };
    }

    return {
        .statusCode = 201,
        .body = buildSuccessJson(projectToJson(created.value())),
    };
}

RouteResponse Router::listProjects() {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    const auto projects = projectService_->listProjects();
    if (!projects) {
        return {
            .statusCode = projects.error().httpStatus,
            .body = buildErrorJson(projects.error()),
        };
    }

    std::string payload = "[";
    bool first = true;
    for (const auto& project : projects.value()) {
        if (!first) {
            payload += ",";
        }
        first = false;
        payload += projectToJson(project);
    }
    payload += "]";

    return {
        .statusCode = 200,
        .body = buildSuccessJson(payload),
    };
}

RouteResponse Router::listProjectsForActor(const std::string& actorId) {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    const auto projects = projectService_->listProjects();
    if (!projects) {
        return {
            .statusCode = projects.error().httpStatus,
            .body = buildErrorJson(projects.error()),
        };
    }

    std::vector<models::User> users;
    if (userStorage_ != nullptr) {
        const auto usersResult = userStorage_->listUsers();
        if (!usersResult) {
            return {
                .statusCode = usersResult.error().httpStatus,
                .body = buildErrorJson(usersResult.error()),
            };
        }
        users = usersResult.value();
    }

    const auto userOpt = findUserByToken(users, actorId);
    const auto actor = userOpt
        ? security::makeAccessActor(*userOpt)
        : security::AccessActor{.userId = actorId, .email = actorId};

    std::string payload = "[";
    bool first = true;
    for (const auto& project : projects.value()) {
        if (!security::canReadProject(actor, project)) {
            continue;
        }
        if (!first) {
            payload += ",";
        }
        first = false;
        payload += projectToJson(project);
    }
    payload += "]";

    return {
        .statusCode = 200,
        .body = buildSuccessJson(payload),
    };
}

RouteResponse Router::listWorkspace(const std::string& actorId) {
    if (projectService_ == nullptr) {
        return {
            .statusCode = 503,
            .body = buildErrorJson(utils::makeError(
                utils::ErrorCode::InvalidConfig,
                "Project service is not configured",
                503,
                false)),
        };
    }

    const auto projectsResult = projectService_->listProjects();
    if (!projectsResult) {
        return {
            .statusCode = projectsResult.error().httpStatus,
            .body = buildErrorJson(projectsResult.error()),
        };
    }

    const auto pagesResult = pageService_.listPages();
    if (!pagesResult) {
        return fail(pagesResult.error());
    }

    std::vector<models::User> users;
    if (userStorage_ != nullptr && !actorId.empty()) {
        const auto usersResult = userStorage_->listUsers();
        if (!usersResult) {
            return fail(usersResult.error());
        }
        users = usersResult.value();
    }

    const auto actorOpt = actorId.empty() ? std::nullopt : findUserByToken(users, actorId);
    const auto accessActor = actorOpt
        ? security::makeAccessActor(*actorOpt)
        : security::AccessActor{.userId = actorId, .email = actorId};

    std::string projectsJson = "[";
    bool firstProject = true;
    for (const auto& project : projectsResult.value()) {
        if (!actorId.empty() && !security::canReadProject(accessActor, project)) {
            continue;
        }
        if (!firstProject) {
            projectsJson += ",";
        }
        firstProject = false;
        projectsJson += projectToJson(project);
    }
    projectsJson += "]";

    std::string pagesJson = "[";
    bool firstPage = true;
    for (const auto& page : pagesResult.value()) {
        bool visible = true;
        if (!actorId.empty()) {
            visible = page.access.publicAccess;
            if (projectService_ != nullptr && !page.projectId.empty()) {
                const auto project = projectService_->getProject(page.projectId);
                if (project) {
                    visible = security::canReadPage(accessActor, project.value(), page);
                } else {
                    visible = security::hasDirectAccess(accessActor, page.access);
                }
            } else {
                visible = security::hasDirectAccess(accessActor, page.access);
            }
        }

        if (!visible) {
            continue;
        }

        if (!firstPage) {
            pagesJson += ",";
        }
        firstPage = false;
        pagesJson += pageToJson(page, false);
    }
    pagesJson += "]";

    return ok("{\"projects\":" + projectsJson + ",\"pages\":" + pagesJson + "}");
}


RouteResponse Router::setPageAccess(const std::string& pageId, const std::string& payload) {
    try {
        if (pageId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "pageId must not be empty",
                400,
                false));
        }
        if (payload.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Access payload must not be empty",
                400,
                false));
        }

        const auto page = pageService_.getPage(pageId);
        if (!page) {
            return fail(page.error());
        }

        const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
        const auto actorId = parsed.value("actorId", std::string{});
        const auto actorEmail = parsed.value("actorEmail", std::string{});
        const auto actorToken = !actorId.empty() ? actorId : actorEmail;

        if (!actorToken.empty() && userStorage_ != nullptr) {
            const auto usersResult = userStorage_->listUsers();
            if (!usersResult) {
                return fail(usersResult.error());
            }

            const auto normalizedActor = toLower(actorToken);
            const models::User* actor = nullptr;
            for (const auto& user : usersResult.value()) {
                if (toLower(user.id) == normalizedActor || toLower(user.email) == normalizedActor) {
                    actor = &user;
                    break;
                }
            }

            if (actor != nullptr) {
                const bool isAdmin = toLower(actor->role) == "admin";
                const bool isOwner = (page->ownerId == actor->id || page->ownerId == actor->email);
                if (!isAdmin && !isOwner) {
                    return fail(utils::makeError(
                        utils::ErrorCode::InvalidRequest,
                        "Only the owner or admin may update access",
                        403,
                        false));
                }
            }
        }

        models::PageAccess access = page->access;
        if (parsed.contains("access") && parsed["access"].is_object()) {
            const auto& accessJson = parsed["access"];
            access.publicAccess = accessJson.value("public", access.publicAccess);
            if (accessJson.contains("users") && accessJson["users"].is_array()) {
                access.userIds.clear();
                for (const auto& item : accessJson["users"]) {
                    if (item.is_string()) {
                        access.userIds.push_back(item.get<std::string>());
                    }
                }
            }
            if (accessJson.contains("groups") && accessJson["groups"].is_array()) {
                access.groupIds.clear();
                for (const auto& item : accessJson["groups"]) {
                    if (item.is_string()) {
                        access.groupIds.push_back(item.get<std::string>());
                    }
                }
            }
            if (accessJson.contains("roles") && accessJson["roles"].is_array()) {
                access.roles.clear();
                for (const auto& item : accessJson["roles"]) {
                    if (item.is_string()) {
                        access.roles.push_back(item.get<std::string>());
                    }
                }
            }
        }

        if (parsed.contains("publicAccess") && parsed["publicAccess"].is_boolean()) {
            access.publicAccess = parsed["publicAccess"].get<bool>();
        }
        if (parsed.contains("accessUsers") && parsed["accessUsers"].is_array()) {
            access.userIds.clear();
            for (const auto& item : parsed["accessUsers"]) {
                if (item.is_string()) {
                    access.userIds.push_back(item.get<std::string>());
                }
            }
        }
        if (parsed.contains("accessGroups") && parsed["accessGroups"].is_array()) {
            access.groupIds.clear();
            for (const auto& item : parsed["accessGroups"]) {
                if (item.is_string()) {
                    access.groupIds.push_back(item.get<std::string>());
                }
            }
        }
        if (parsed.contains("accessRoles") && parsed["accessRoles"].is_array()) {
            access.roles.clear();
            for (const auto& item : parsed["accessRoles"]) {
                if (item.is_string()) {
                    access.roles.push_back(item.get<std::string>());
                }
            }
        }

        const auto updatedPage = pageService_.updateAccess(pageId, access);
        if (!updatedPage) {
            return fail(updatedPage.error());
        }

        nlohmann::json response{
            {"pageId", updatedPage->pageId},
            {"access", {
                {"public", access.publicAccess},
                {"users", access.userIds},
                {"groups", access.groupIds},
                {"roles", access.roles},
            }},
        };
        return ok(response.dump());
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed access JSON payload: ") + exception.what(),
            400,
            false));
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
        models::CommentAnchor anchor{};
        if (parsedPayload.contains("anchor") && parsedPayload["anchor"].is_object()) {
            const auto& anchorJson = parsedPayload["anchor"];
            anchor.anchorId = anchorJson.value("anchorId", std::string{});
            anchor.quote = anchorJson.value("quote", std::string{});
            anchor.selector = anchorJson.value("selector", std::string{});
            anchor.blockId = anchorJson.value("blockId", std::string{});
            anchor.blockType = anchorJson.value("blockType", std::string{});
            anchor.startOffset = anchorJson.value("startOffset", -1);
            anchor.endOffset = anchorJson.value("endOffset", -1);
        }
        if (parsedPayload.contains("anchorId") && parsedPayload["anchorId"].is_string()) {
            anchor.anchorId = parsedPayload.value("anchorId", std::string{});
        }
        if (parsedPayload.contains("anchorQuote") && parsedPayload["anchorQuote"].is_string()) {
            anchor.quote = parsedPayload.value("anchorQuote", std::string{});
        }
        if (parsedPayload.contains("anchorSelector") && parsedPayload["anchorSelector"].is_string()) {
            anchor.selector = parsedPayload.value("anchorSelector", std::string{});
        }
        if (parsedPayload.contains("anchorBlockId") && parsedPayload["anchorBlockId"].is_string()) {
            anchor.blockId = parsedPayload.value("anchorBlockId", std::string{});
        }
        if (parsedPayload.contains("anchorBlockType") && parsedPayload["anchorBlockType"].is_string()) {
            anchor.blockType = parsedPayload.value("anchorBlockType", std::string{});
        }
        if (parsedPayload.contains("anchorStartOffset") && parsedPayload["anchorStartOffset"].is_number_integer()) {
            anchor.startOffset = parsedPayload.value("anchorStartOffset", -1);
        }
        if (parsedPayload.contains("anchorEndOffset") && parsedPayload["anchorEndOffset"].is_number_integer()) {
            anchor.endOffset = parsedPayload.value("anchorEndOffset", -1);
        }
        const auto thread = collaborationService_->createThread(
            pageId,
            services::CommentThreadDraft{
                .author = parsedPayload.value("author", std::string("viewer")),
                .body = parsedPayload.value("body", std::string{}),
                .selectionLabel = parsedPayload.value("selectionLabel", std::string{}),
                .targetId = parsedPayload.value("targetId", std::string{}),
                .targetType = parsedPayload.value("targetType", std::string("paragraph")),
                .targetPreview = parsedPayload.value("targetPreview", std::string{}),
                .anchor = anchor,
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

        const auto resolved = resolveTableSelection(mwsClient_, tableId, viewId);
        const auto& resolvedTableId = resolved.tableId;
        const auto& resolvedViewId = resolved.viewId;
        if (resolvedTableId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "tableId must not be empty",
                400,
                false));
        }
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

        const auto resolved = resolveTableSelection(mwsClient_, tableId, viewId);
        const auto& resolvedTableId = resolved.tableId;
        const auto& resolvedViewId = resolved.viewId;
        if (resolvedTableId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "tableId must not be empty",
                400,
                false));
        }
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
        const auto tableUrl = parsed.value("tableUrl", parsed.value("tableLink", std::string{}));
        const auto resolved = resolveTableSelection(
            mwsClient_,
            parsed.value("tableId", mwsClient_->tableId()),
            parsed.value("viewId", mwsClient_->viewId()),
            tableUrl);
        const auto& resolvedTableId = resolved.tableId;
        const auto& resolvedViewId = resolved.viewId;
        if (resolvedTableId.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "tableId must not be empty",
                400,
                false));
        }
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

RouteResponse Router::uploadAttachment(const std::string& payload) {
    try {
        if (payload.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Upload payload must not be empty",
                400,
                false));
        }

        const auto parsed = nlohmann::json::parse(payload, nullptr, true, true);
        const auto filenameRaw = parsed.value("filename", std::string{});
        const auto dataUrl = parsed.value("dataUrl", std::string{});
        const auto mimeType = parsed.value("mimeType", std::string{});
        if (dataUrl.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Upload payload must include dataUrl",
                400,
                false));
        }

        std::string base64Data = dataUrl;
        const auto marker = dataUrl.find("base64,");
        if (marker != std::string::npos) {
            base64Data = dataUrl.substr(marker + 7);
        }

        bool ok = false;
        const auto decoded = decodeBase64(base64Data, ok);
        if (!ok || decoded.empty()) {
            return fail(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                "Failed to decode base64 payload",
                400,
                false));
        }

        std::string safeName;
        for (const char ch : filenameRaw) {
            if (std::isalnum(static_cast<unsigned char>(ch)) || ch == '.' || ch == '_' || ch == '-') {
                safeName.push_back(ch);
            }
        }
        if (safeName.empty()) {
            safeName = "upload";
        }

        const auto now = utils::formatIso(utils::now());
        std::string stem = safeName;
        std::string extension;
        const auto dotPos = safeName.find_last_of('.');
        if (dotPos != std::string::npos && dotPos > 0) {
            stem = safeName.substr(0, dotPos);
            extension = safeName.substr(dotPos);
        }
        std::string finalName = stem + extension;
        auto uploadsDir = std::filesystem::current_path() / "uploads";
        std::filesystem::create_directories(uploadsDir);

        std::filesystem::path outputPath = uploadsDir / finalName;
        int attempt = 0;
        while (std::filesystem::exists(outputPath)) {
            ++attempt;
            finalName = stem + "-" + std::to_string(attempt) + extension;
            outputPath = uploadsDir / finalName;
        }

        std::ofstream output(outputPath, std::ios::binary);
        if (!output) {
            return fail(utils::makeError(
                utils::ErrorCode::InternalError,
                "Unable to write uploaded file",
                500,
                false));
        }
        output.write(reinterpret_cast<const char*>(decoded.data()), static_cast<std::streamsize>(decoded.size()));
        output.close();

        const auto url = "/uploads/" + finalName;
        const nlohmann::json response{
            {"url", url},
            {"name", filenameRaw.empty() ? finalName : filenameRaw},
            {"mimeType", mimeType},
            {"uploadedAt", now},
        };
        return created(response.dump());
    } catch (const nlohmann::json::exception& exception) {
        return fail(utils::makeError(
            utils::ErrorCode::InvalidRequest,
            std::string("Malformed upload JSON payload: ") + exception.what(),
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

    auto projectId = extractJsonString(payload, "projectId", false);
    if (!projectId) {
        return std::unexpected(projectId.error());
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

    bool accessProvided = false;
    models::PageAccess access{};
    if (payload.find("\"access\"") != std::string::npos ||
        payload.find("\"accessUsers\"") != std::string::npos ||
        payload.find("\"accessGroups\"") != std::string::npos ||
        payload.find("\"accessRoles\"") != std::string::npos ||
        payload.find("\"publicAccess\"") != std::string::npos) {
        try {
            const auto parsedPayload = nlohmann::json::parse(payload, nullptr, true, true);
            if (parsedPayload.contains("access") && parsedPayload["access"].is_object()) {
                const auto& accessJson = parsedPayload["access"];
                access.publicAccess = accessJson.value("public", false);
                if (accessJson.contains("users") && accessJson["users"].is_array()) {
                    for (const auto& item : accessJson["users"]) {
                        if (item.is_string()) {
                            access.userIds.push_back(item.get<std::string>());
                        }
                    }
                }
                if (accessJson.contains("groups") && accessJson["groups"].is_array()) {
                    for (const auto& item : accessJson["groups"]) {
                        if (item.is_string()) {
                            access.groupIds.push_back(item.get<std::string>());
                        }
                    }
                }
                if (accessJson.contains("roles") && accessJson["roles"].is_array()) {
                    for (const auto& item : accessJson["roles"]) {
                        if (item.is_string()) {
                            access.roles.push_back(item.get<std::string>());
                        }
                    }
                }
                accessProvided = true;
            }

            if (parsedPayload.contains("publicAccess") && parsedPayload["publicAccess"].is_boolean()) {
                access.publicAccess = parsedPayload["publicAccess"].get<bool>();
                accessProvided = true;
            }

            if (parsedPayload.contains("accessUsers") && parsedPayload["accessUsers"].is_array()) {
                accessProvided = true;
                for (const auto& item : parsedPayload["accessUsers"]) {
                    if (item.is_string()) {
                        access.userIds.push_back(item.get<std::string>());
                    }
                }
            }
            if (parsedPayload.contains("accessGroups") && parsedPayload["accessGroups"].is_array()) {
                accessProvided = true;
                for (const auto& item : parsedPayload["accessGroups"]) {
                    if (item.is_string()) {
                        access.groupIds.push_back(item.get<std::string>());
                    }
                }
            }
            if (parsedPayload.contains("accessRoles") && parsedPayload["accessRoles"].is_array()) {
                accessProvided = true;
                for (const auto& item : parsedPayload["accessRoles"]) {
                    if (item.is_string()) {
                        access.roles.push_back(item.get<std::string>());
                    }
                }
            }
        } catch (const std::exception& exception) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InvalidRequest,
                std::string("Failed to parse access payload: ") + exception.what(),
                400,
                false));
        }
    }

    return services::PageDraft{
        .projectId = projectId.value(),
        .title = title.value(),
        .description = description.value(),
        .content = content.value(),
        .ownerId = ownerId.value(),
        .ownerName = ownerName.value(),
        .sharedWith = sharedWith,
        .sharedWithProvided = sharedWithProvided,
        .access = access,
        .accessProvided = accessProvided,
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
