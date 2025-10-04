cmake_minimum_required(VERSION 3.20)
project(TigerExHighSpeedEngine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -mtune=native -flto")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")

# Find required packages
find_package(Boost REQUIRED COMPONENTS system thread)
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${Boost_INCLUDE_DIRS}
    ${OPENSSL_INCLUDE_DIR}
)

# Source files
set(SOURCES
    src/main.cpp
    src/matching_engine.cpp
    src/order_book.cpp
    src/market_data_handler.cpp
    src/risk_manager.cpp
    src/websocket_server.cpp
    src/database_connector.cpp
    src/memory_pool.cpp
    src/lock_free_queue.cpp
)

# Create executable
add_executable(tigerex_engine ${SOURCES})

# Link libraries
target_link_libraries(tigerex_engine
    ${Boost_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    Threads::Threads
    pthread
)

# Install
install(TARGETS tigerex_engine DESTINATION bin)