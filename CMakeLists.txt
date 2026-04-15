cmake_minimum_required(VERSION 3.20)

project(wikilive_backend LANGUAGES CXX)
enable_testing()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    message(FATAL_ERROR "CMAKE_TOOLCHAIN_FILE with vcpkg is required for WikiLive build")
endif()

if (NOT DEFINED VCPKG_TARGET_TRIPLET)
    if (WIN32)
        set(VCPKG_TARGET_TRIPLET "x64-windows" CACHE STRING "vcpkg triplet")
    else()
        set(VCPKG_TARGET_TRIPLET "x64-linux" CACHE STRING "vcpkg triplet")
    endif()
endif()

set(_wikilive_vcpkg_triplet "${VCPKG_TARGET_TRIPLET}")
set(_wikilive_local_vcpkg_installed_dir
    "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg_installed/${_wikilive_vcpkg_triplet}")

if (EXISTS "${_wikilive_local_vcpkg_installed_dir}")
    set(_wikilive_vcpkg_installed_dir "${_wikilive_local_vcpkg_installed_dir}")
elseif (DEFINED VCPKG_INSTALLED_DIR AND EXISTS "${VCPKG_INSTALLED_DIR}/${_wikilive_vcpkg_triplet}")
    set(_wikilive_vcpkg_installed_dir "${VCPKG_INSTALLED_DIR}/${_wikilive_vcpkg_triplet}")
else()
    get_filename_component(_vcpkg_scripts_dir "${CMAKE_TOOLCHAIN_FILE}" DIRECTORY)
    get_filename_component(_vcpkg_root "${_vcpkg_scripts_dir}" DIRECTORY)
    get_filename_component(_vcpkg_root "${_vcpkg_root}" DIRECTORY)
    set(_wikilive_vcpkg_installed_dir "${_vcpkg_root}/installed/${_wikilive_vcpkg_triplet}")
endif()

list(PREPEND CMAKE_PREFIX_PATH "${_wikilive_vcpkg_installed_dir}")

find_package(CURL CONFIG REQUIRED)
find_package(unofficial-uwebsockets CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

add_library(wikilive_core STATIC
    config/config_loader.cpp
    src/ai/ai_context_builder.cpp
    src/ai/ai_field_verifier.cpp
    src/ai/ai_provider_factory.cpp
    src/ai/ai_service.cpp
    src/ai/ai_suggestion_validator.cpp
    src/ai/ollama_ai_provider.cpp
    src/ai/openrouter_ai_provider.cpp
    src/ai/openrouter_prompt_builder.cpp
    src/core/app_config.cpp
    src/core/application.cpp
    src/server/http_server.cpp
    src/server/router.cpp
    src/server/websocket_manager.cpp
    src/api/mws_client.cpp
    src/services/auth_service.cpp
    src/services/collaboration_service.cpp
    src/services/page_service.cpp
    src/services/render_service.cpp
    src/wiki/wiki_parser.cpp
    src/wiki/wiki_renderer.cpp
    src/storage/in_memory_page_storage.cpp
    src/storage/hybrid_page_storage.cpp
    src/storage/local_collaboration_storage.cpp
    src/storage/local_file_page_storage.cpp
    src/storage/local_user_storage.cpp
    src/storage/mws_page_storage.cpp
    src/storage/cache.cpp
    src/utils/logger.cpp
    src/utils/errors.cpp
    src/utils/string_utils.cpp
    src/utils/time_utils.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")

target_include_directories(wikilive_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(wikilive_core PUBLIC
    unofficial::uwebsockets::uwebsockets
    CURL::libcurl
    nlohmann_json::nlohmann_json
)

add_executable(wikilive_backend
    src/main.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")

target_link_libraries(wikilive_backend PRIVATE
    wikilive_core
)

if (WIN32)
    set(_wikilive_libuv_release_dll
        "${_wikilive_vcpkg_installed_dir}/bin/uv.dll")
    set(_wikilive_libuv_debug_dll
        "${_wikilive_vcpkg_installed_dir}/debug/bin/uv.dll")
    set(_wikilive_libcurl_release_dll
        "${_wikilive_vcpkg_installed_dir}/bin/libcurl.dll")
    set(_wikilive_libcurl_debug_dll
        "${_wikilive_vcpkg_installed_dir}/debug/bin/libcurl-d.dll")

    add_custom_command(TARGET wikilive_backend POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libuv_release_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libuv_debug_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libcurl_release_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libcurl_debug_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND_EXPAND_LISTS
    )
endif()

target_compile_options(wikilive_core PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<CXX_COMPILER_ID:MSVC>:/EHsc>
    $<$<CXX_COMPILER_ID:MSVC>:/permissive->
    $<$<CXX_COMPILER_ID:MSVC>:/Zc:__cplusplus>
    $<$<CXX_COMPILER_ID:MSVC>:/utf-8>
    $<$<CXX_COMPILER_ID:MSVC>:/wd4996>
)

add_executable(wikilive_test_parser
    tests/test_parser.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_parser PRIVATE wikilive_core)

add_executable(wikilive_test_cache
    tests/test_cache.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_cache PRIVATE wikilive_core)

add_executable(wikilive_test_page_service
    tests/test_page_service.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_page_service PRIVATE wikilive_core)

add_executable(wikilive_test_router
    tests/test_router.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_router PRIVATE wikilive_core)

add_executable(wikilive_test_string_utils
    tests/test_string_utils.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_string_utils PRIVATE wikilive_core)

add_executable(wikilive_test_ai_service
    tests/test_ai_service.cpp
    "src/models/project.h" "src/storage/project_storage.h" "src/storage/local_file_project_storage.h" "src/storage/local_file_project_storage.cpp" "src/services/project_service.h" "src/services/project_service.cpp" "src/security/access_evaluator.h" "src/security/access_evaluator.cpp")
target_link_libraries(wikilive_test_ai_service PRIVATE wikilive_core)

add_test(NAME wikilive_test_parser COMMAND wikilive_test_parser)
add_test(NAME wikilive_test_cache COMMAND wikilive_test_cache)
add_test(NAME wikilive_test_page_service COMMAND wikilive_test_page_service)
add_test(NAME wikilive_test_router COMMAND wikilive_test_router)
add_test(NAME wikilive_test_string_utils COMMAND wikilive_test_string_utils)
add_test(NAME wikilive_test_ai_service COMMAND wikilive_test_ai_service)
