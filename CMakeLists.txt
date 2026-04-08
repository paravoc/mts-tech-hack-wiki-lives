cmake_minimum_required(VERSION 3.20)

project(wikilive_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(wikilive_backend
    src/main.cpp
    config/config_loader.cpp
    src/core/app_config.cpp
    src/core/application.cpp
    src/server/http_server.cpp
    src/server/router.cpp
    src/server/websocket_manager.cpp
    src/api/mws_client.cpp
    src/api/retry_policy.cpp
    src/wiki/wiki_insert.cpp
    src/wiki/wiki_parser.cpp
    src/wiki/wiki_renderer.cpp
    src/storage/page_storage.cpp
    src/storage/cache.cpp
    src/utils/logger.cpp
    src/utils/errors.cpp
    src/utils/string_utils.cpp
    src/utils/time_utils.cpp
)

target_include_directories(wikilive_backend PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_options(wikilive_backend PRIVATE
    /W4
    /EHsc
    /permissive-
    /Zc:__cplusplus
    /utf-8
)
