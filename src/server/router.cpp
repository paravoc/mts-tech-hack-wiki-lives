#include "src/server/router.h"

#include <exception>
#include <utility>

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

std::string pageToJson(const wikilive::storage::Page& page) {
    return
        "{\"pageId\":\"" + wikilive::utils::escapeJson(page.pageId) +
        "\",\"title\":\"" + wikilive::utils::escapeJson(page.title) +
        "\",\"content\":\"" + wikilive::utils::escapeJson(page.content) + "\"}";
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

RouteResponse Router::handleHealth() const {
    try {
        return ok(R"({"status":"ok","service":"wikilive_backend"})");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::listPages() {
    try {
        const auto pages = pageStorage_.listPages();
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
            items += pageToJson(page);
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

        const auto page = pageStorage_.getPage(pageId);
        if (!page) {
            return fail(page.error());
        }

        return ok("{\"item\":" + pageToJson(page.value()) + "}");
    } catch (const std::exception& exception) {
        return unexpectedExceptionResponse(exception);
    } catch (...) {
        return unknownExceptionResponse();
    }
}

RouteResponse Router::savePage(const std::string& payload) {
    try {
        const auto page = parsePagePayload(payload);
        if (!page) {
            return fail(page.error());
        }

        auto value = page.value();
        if (value.pageId.empty()) {
            value.pageId = "page-" + std::to_string(nextPageId_++);
        }

        const auto saveResult = pageStorage_.savePage(value);
        if (!saveResult) {
            return fail(saveResult.error());
        }

        return ok("{\"item\":" + pageToJson(value) + "}");
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

        const auto removeResult = pageStorage_.deletePage(pageId);
        if (!removeResult) {
            return fail(removeResult.error());
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

        const auto rendered = wikiRenderer_.render(content);
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

RouteResponse Router::ok(const std::string& dataJson) const {
    return RouteResponse{
        .statusCode = 200,
        .body = buildSuccessJson(dataJson),
    };
}

RouteResponse Router::fail(const utils::Error& error) const {
    return RouteResponse{
        .statusCode = error.httpStatus,
        .body = buildErrorJson(error),
    };
}

utils::Expected<storage::Page> Router::parsePagePayload(const std::string& payload) {
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

    std::string pageId;
    if (payload.find("\"pageId\"") != std::string::npos) {
        const auto pageIdValue = extractJsonString(payload, "pageId");
        if (!pageIdValue) {
            return std::unexpected(pageIdValue.error());
        }
        pageId = pageIdValue.value();
    }

    return storage::Page{
        .pageId = std::move(pageId),
        .title = title.value(),
        .content = content.value(),
    };
}

utils::Expected<std::string> Router::extractJsonString(const std::string& payload, const std::string& key) const {
    const auto keyToken = "\"" + key + "\"";
    const auto keyPosition = payload.find(keyToken);
    if (keyPosition == std::string::npos) {
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

    std::string result;
    bool escape = false;
    for (std::size_t index = openingQuote + 1; index < payload.size(); ++index) {
        const char current = payload[index];
        if (escape) {
            switch (current) {
                case '"':
                    result.push_back('"');
                    break;
                case '\\':
                    result.push_back('\\');
                    break;
                case 'n':
                    result.push_back('\n');
                    break;
                case 'r':
                    result.push_back('\r');
                    break;
                case 't':
                    result.push_back('\t');
                    break;
                default:
                    result.push_back(current);
                    break;
            }
            escape = false;
            continue;
        }

        if (current == '\\') {
            escape = true;
            continue;
        }

        if (current == '"') {
            return result;
        }

        result.push_back(current);
    }

    return std::unexpected(utils::makeError(
        utils::ErrorCode::InvalidRequest,
        "Unterminated JSON string field: " + key,
        400,
        false));
}

}  // namespace wikilive::server
