#include "src/server/http_server.h"

#include <exception>
#include <memory>
#include <string>
#include <string_view>
#include <utility>

#include "src/server/router.h"
#include "src/server/websocket_manager.h"
#include "src/utils/logger.h"
#include "uwebsockets/App.h"

namespace wikilive::server {

namespace {

using HttpRequest = uWS::HttpRequest;
using HttpResponse = uWS::HttpResponse<false>;

std::string_view reasonPhrase(const int statusCode) {
    switch (statusCode) {
        case 200:
            return "200 OK";
        case 201:
            return "201 Created";
        case 400:
            return "400 Bad Request";
        case 401:
            return "401 Unauthorized";
        case 403:
            return "403 Forbidden";
        case 404:
            return "404 Not Found";
        case 429:
            return "429 Too Many Requests";
        case 500:
            return "500 Internal Server Error";
        case 501:
            return "501 Not Implemented";
        default:
            return "500 Internal Server Error";
    }
}

void writeCommonHeaders(HttpResponse* response) {
    response->writeHeader("Content-Type", "application/json; charset=utf-8");
    response->writeHeader("Access-Control-Allow-Origin", "*");
    response->writeHeader("Access-Control-Allow-Headers", "content-type");
    response->writeHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
}

void writeResponse(HttpResponse* response, const RouteResponse& routeResponse) {
    response->writeStatus(reasonPhrase(routeResponse.statusCode));
    writeCommonHeaders(response);
    response->end(routeResponse.body);
}

template <typename Callback>
void collectRequestBody(HttpResponse* response, Callback&& callback) {
    auto body = std::make_shared<std::string>();
    auto aborted = std::make_shared<bool>(false);

    response->onAborted([aborted]() {
        *aborted = true;
    });

    response->onData([response, body, aborted, callback = std::forward<Callback>(callback)](
                         std::string_view chunk,
                         bool isLast) mutable {
        if (*aborted) {
            return;
        }

        body->append(chunk.data(), chunk.size());
        if (isLast) {
            callback(response, *body);
        }
    });
}

template <typename Callback>
void handleRequestBody(HttpResponse* response, HttpRequest* request, Callback&& callback) {
    const auto contentLength = request->getHeader("content-length");
    const auto transferEncoding = request->getHeader("transfer-encoding");

    if (contentLength.empty() && transferEncoding.empty()) {
        callback(response, std::string{});
        return;
    }

    collectRequestBody(response, std::forward<Callback>(callback));
}

}  // namespace

HttpServer::HttpServer(Router& router, WebSocketManager* webSocketManager)
    : router_(router), webSocketManager_(webSocketManager) {
}

utils::VoidExpected HttpServer::start(const int port) {
    try {
        uWS::App app;

        if (webSocketManager_ != nullptr) {
            app.ws<WebSocketSessionData>("/ws", {
                .open = [this](auto* socket) {
                    webSocketManager_->registerConnection(socket);
                    socket->send(R"({"event":"connected","status":"ok"})", uWS::OpCode::TEXT);
                },
                .message = [this](auto* socket, std::string_view message, uWS::OpCode opCode) {
                    if (opCode != uWS::OpCode::TEXT) {
                        return;
                    }

                    const auto response = webSocketManager_->handleMessage(socket, message);
                    if (!response.empty()) {
                        socket->send(response, uWS::OpCode::TEXT);
                    }
                },
                .close = [this](auto* socket, int /*code*/, std::string_view /*message*/) {
                    webSocketManager_->unregisterConnection(socket);
                },
            });
        }

        app.options("/*", [](HttpResponse* response, HttpRequest* /*request*/) {
            writeResponse(response, RouteResponse{
                                      .statusCode = 200,
                                      .body = R"({"success":true,"data":{"preflight":true}})",
                                  });
        });

        app.get("/health", [this](HttpResponse* response, HttpRequest* /*request*/) {
            writeResponse(response, router_.handleHealth());
        });

        app.get("/api/pages", [this](HttpResponse* response, HttpRequest* /*request*/) {
            writeResponse(response, router_.listPages());
        });

        app.get("/api/pages/:pageId", [this](HttpResponse* response, HttpRequest* request) {
            writeResponse(response, router_.getPage(std::string(request->getParameter(0))));
        });

        app.post("/api/pages", [this](HttpResponse* response, HttpRequest* request) {
            handleRequestBody(response, request, [this](HttpResponse* innerResponse, const std::string& body) {
                writeResponse(innerResponse, router_.createPage(body));
            });
        });

        app.put("/api/pages/:pageId", [this](HttpResponse* response, HttpRequest* request) {
            const std::string pageId(request->getParameter(0));
            handleRequestBody(response, request, [this, pageId](HttpResponse* innerResponse, const std::string& body) {
                writeResponse(innerResponse, router_.updatePage(pageId, body));
            });
        });

        app.del("/api/pages/:pageId", [this](HttpResponse* response, HttpRequest* request) {
            writeResponse(response, router_.deletePage(std::string(request->getParameter(0))));
        });

        app.post("/api/render", [this](HttpResponse* response, HttpRequest* request) {
            handleRequestBody(response, request, [this](HttpResponse* innerResponse, const std::string& body) {
                writeResponse(innerResponse, router_.renderContent(body));
            });
        });

        app.post("/api/ai/suggest-insert", [this](HttpResponse* response, HttpRequest* request) {
            handleRequestBody(response, request, [this](HttpResponse* innerResponse, const std::string& body) {
                writeResponse(innerResponse, router_.suggestInsert(body));
            });
        });

        app.listen("0.0.0.0", port, [this, port](auto* token) {
            listenSocket_ = token;
            if (token) {
                utils::Logger::instance().info("HTTP server is listening on port " + std::to_string(port));
            } else {
                utils::Logger::instance().error("Failed to listen on port " + std::to_string(port));
            }
        });

        if (listenSocket_ == nullptr) {
            return std::unexpected(utils::makeError(
                utils::ErrorCode::InternalError,
                "HTTP server failed to bind to port " + std::to_string(port),
                500,
                false));
        }

        app.run();
        listenSocket_ = nullptr;
        return {};
    } catch (const std::exception& exception) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("HTTP server start failed: ") + exception.what(),
            500,
            false));
    } catch (...) {
        return std::unexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            "HTTP server start failed with unknown exception",
            500,
            false));
    }
}

void HttpServer::stop() {
    listenSocket_ = nullptr;
}

}  // namespace wikilive::server
