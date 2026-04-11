cmake_minimum_required(VERSION 3.20)
project(tigerex_matching_engine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Optimization flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -fsanitize=address,undefined")

# Dependencies
find_package(Threads REQUIRED)

# Include nlohmann/json (header-only)
include(FetchContent)
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(json)

# Include cpp-httplib (header-only)
FetchContent_Declare(
    httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
    GIT_TAG v0.14.3
)
FetchContent_MakeAvailable(httplib)

# Main executable
add_executable(tigerex_matching
    src/main.cpp
)

target_include_directories(tigerex_matching PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${nlohmann_json_SOURCE_DIR}/single_include
    ${httplib_SOURCE_DIR}
)

target_link_libraries(tigerex_matching PRIVATE
    Threads::Threads
)

# Install target
install(TARGETS tigerex_matching DESTINATION bin)

# Testing
option(BUILD_TESTS "Build tests" OFF)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()