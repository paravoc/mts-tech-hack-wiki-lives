cmake_minimum_required(VERSION 3.20)

project(wikilive_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    message(FATAL_ERROR "CMAKE_TOOLCHAIN_FILE with vcpkg is required for WikiLive build")
endif()

get_filename_component(_vcpkg_scripts_dir "${CMAKE_TOOLCHAIN_FILE}" DIRECTORY)
get_filename_component(_vcpkg_root "${_vcpkg_scripts_dir}" DIRECTORY)
get_filename_component(_vcpkg_root "${_vcpkg_root}" DIRECTORY)

set(_wikilive_vcpkg_triplet "x64-windows")

set(_wikilive_uwebsockets_include_dir
    "${_vcpkg_root}/packages/uwebsockets_${_wikilive_vcpkg_triplet}/include")
set(_wikilive_usockets_include_dir
    "${_vcpkg_root}/packages/usockets_${_wikilive_vcpkg_triplet}/include")
set(_wikilive_libuv_include_dir
    "${_vcpkg_root}/packages/libuv_${_wikilive_vcpkg_triplet}/include")

set(_wikilive_usockets_release_lib
    "${_vcpkg_root}/packages/usockets_${_wikilive_vcpkg_triplet}/lib/uSockets.lib")
set(_wikilive_usockets_debug_lib
    "${_vcpkg_root}/packages/usockets_${_wikilive_vcpkg_triplet}/debug/lib/uSockets.lib")
set(_wikilive_libuv_release_lib
    "${_vcpkg_root}/packages/libuv_${_wikilive_vcpkg_triplet}/lib/uv.lib")
set(_wikilive_libuv_debug_lib
    "${_vcpkg_root}/packages/libuv_${_wikilive_vcpkg_triplet}/debug/lib/uv.lib")
set(_wikilive_libuv_release_dll
    "${_vcpkg_root}/packages/libuv_${_wikilive_vcpkg_triplet}/bin/uv.dll")
set(_wikilive_libuv_debug_dll
    "${_vcpkg_root}/packages/libuv_${_wikilive_vcpkg_triplet}/debug/bin/uv.dll")

foreach(_required_path IN ITEMS
    "${_wikilive_uwebsockets_include_dir}/uwebsockets/App.h"
    "${_wikilive_usockets_include_dir}/libusockets.h"
    "${_wikilive_libuv_include_dir}/uv.h"
    "${_wikilive_usockets_release_lib}"
    "${_wikilive_usockets_debug_lib}"
    "${_wikilive_libuv_release_lib}"
    "${_wikilive_libuv_debug_lib}")
    if (NOT EXISTS "${_required_path}")
        message(FATAL_ERROR "Required dependency file was not found: ${_required_path}")
    endif()
endforeach()

add_library(wikilive_libuv SHARED IMPORTED GLOBAL)
set_target_properties(wikilive_libuv PROPERTIES
    IMPORTED_IMPLIB_RELEASE "${_wikilive_libuv_release_lib}"
    IMPORTED_IMPLIB_DEBUG "${_wikilive_libuv_debug_lib}"
    IMPORTED_LOCATION_RELEASE "${_wikilive_libuv_release_dll}"
    IMPORTED_LOCATION_DEBUG "${_wikilive_libuv_debug_dll}"
    INTERFACE_INCLUDE_DIRECTORIES "${_wikilive_libuv_include_dir}"
)
add_library(wikilive::libuv ALIAS wikilive_libuv)

add_library(wikilive_usockets STATIC IMPORTED GLOBAL)
set_target_properties(wikilive_usockets PROPERTIES
    IMPORTED_LOCATION_RELEASE "${_wikilive_usockets_release_lib}"
    IMPORTED_LOCATION_DEBUG "${_wikilive_usockets_debug_lib}"
    INTERFACE_INCLUDE_DIRECTORIES "${_wikilive_usockets_include_dir}"
    INTERFACE_LINK_LIBRARIES "wikilive::libuv;ws2_32"
)
add_library(wikilive::usockets ALIAS wikilive_usockets)

add_library(wikilive_uwebsockets INTERFACE)
target_include_directories(wikilive_uwebsockets INTERFACE
    "${_wikilive_uwebsockets_include_dir}"
)
target_compile_definitions(wikilive_uwebsockets INTERFACE
    UWS_NO_ZLIB
)
target_link_libraries(wikilive_uwebsockets INTERFACE
    wikilive::usockets
)
add_library(wikilive::uwebsockets ALIAS wikilive_uwebsockets)

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
    src/services/page_service.cpp
    src/services/render_service.cpp
    src/wiki/wiki_insert.cpp
    src/wiki/wiki_parser.cpp
    src/wiki/wiki_renderer.cpp
    src/storage/page_storage.cpp
    src/storage/in_memory_page_storage.cpp
    src/storage/cache.cpp
    src/utils/logger.cpp
    src/utils/errors.cpp
    src/utils/string_utils.cpp
    src/utils/time_utils.cpp
)

target_include_directories(wikilive_backend PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(wikilive_backend PRIVATE
    wikilive::uwebsockets
    winhttp
)

if (WIN32)
    add_custom_command(TARGET wikilive_backend POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libuv_release_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${_wikilive_libuv_debug_dll}"
            $<TARGET_FILE_DIR:wikilive_backend>
        COMMAND_EXPAND_LISTS
    )
endif()

target_compile_options(wikilive_backend PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<CXX_COMPILER_ID:MSVC>:/EHsc>
    $<$<CXX_COMPILER_ID:MSVC>:/permissive->
    $<$<CXX_COMPILER_ID:MSVC>:/Zc:__cplusplus>
    $<$<CXX_COMPILER_ID:MSVC>:/utf-8>
    $<$<CXX_COMPILER_ID:MSVC>:/wd4996>
)
