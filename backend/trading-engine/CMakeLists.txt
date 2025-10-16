cmake_minimum_required(VERSION 3.16)
project(TigerExTradingEngine VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O3 -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0 -DDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Threads REQUIRED)
find_package(Boost REQUIRED COMPONENTS system filesystem thread)

# Find PostgreSQL
find_package(PostgreSQL REQUIRED)

# Find Redis (hiredis)
pkg_check_modules(HIREDIS REQUIRED hiredis)

# Find librdkafka
pkg_check_modules(RDKAFKA REQUIRED rdkafka++)

# Find JSON library
find_package(nlohmann_json REQUIRED)

# Find WebSocket++ (header-only)
find_path(WEBSOCKETPP_INCLUDE_DIR websocketpp/config/asio_no_tls.hpp)

# Find Beast (part of Boost)
find_package(Boost REQUIRED COMPONENTS beast)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${PostgreSQL_INCLUDE_DIRS}
    ${HIREDIS_INCLUDE_DIRS}
    ${RDKAFKA_INCLUDE_DIRS}
    ${WEBSOCKETPP_INCLUDE_DIR}
    ${Boost_INCLUDE_DIRS}
)

# Source files
set(SOURCES
    main.cpp
    src/engine/trading_engine.cpp
    src/engine/order_book.cpp
    src/engine/matching_engine.cpp
    src/engine/risk_manager.cpp
    src/engine/position_manager.cpp
    src/server/http_server.cpp
    src/server/websocket_server.cpp
    src/database/database_manager.cpp
    src/redis/redis_manager.cpp
    src/kafka/kafka_producer.cpp
    src/kafka/kafka_consumer.cpp
    src/config/config.cpp
    src/logger/logger.cpp
    src/utils/utils.cpp
    src/models/order.cpp
    src/models/trade.cpp
    src/models/market_data.cpp
    src/models/user_balance.cpp
)

# Header files
set(HEADERS
    include/engine/trading_engine.h
    include/engine/order_book.h
    include/engine/matching_engine.h
    include/engine/risk_manager.h
    include/engine/position_manager.h
    include/server/http_server.h
    include/server/websocket_server.h
    include/database/database_manager.h
    include/redis/redis_manager.h
    include/kafka/kafka_producer.h
    include/kafka/kafka_consumer.h
    include/config/config.h
    include/logger/logger.h
    include/utils/utils.h
    include/models/order.h
    include/models/trade.h
    include/models/market_data.h
    include/models/user_balance.h
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(${PROJECT_NAME}
    ${PostgreSQL_LIBRARIES}
    ${HIREDIS_LIBRARIES}
    ${RDKAFKA_LIBRARIES}
    ${Boost_LIBRARIES}
    Threads::Threads
    nlohmann_json::nlohmann_json
)

# Compiler definitions
target_compile_definitions(${PROJECT_NAME} PRIVATE
    BOOST_BEAST_USE_STD_STRING_VIEW
    BOOST_ASIO_HAS_STD_STRING_VIEW
)

# Installation
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)

# Copy configuration files
install(FILES
    config/trading_pairs.json
    config/risk_limits.json
    DESTINATION etc/tigerex
)

# Create directories for logs and data
install(DIRECTORY DESTINATION var/log/tigerex)
install(DIRECTORY DESTINATION var/lib/tigerex)

# Testing
enable_testing()

# Find Google Test
find_package(GTest)
if(GTest_FOUND)
    add_subdirectory(tests)
endif()

# Benchmarking
find_package(benchmark)
if(benchmark_FOUND)
    add_subdirectory(benchmarks)
endif()

# Documentation
find_package(Doxygen)
if(DOXYGEN_FOUND)
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)
    add_custom_target(doc
        ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen" VERBATIM
    )
endif()

# Package configuration
set(CPACK_PACKAGE_NAME "TigerExTradingEngine")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "High-performance cryptocurrency trading engine")
set(CPACK_PACKAGE_VENDOR "TigerEx Team")
set(CPACK_PACKAGE_CONTACT "support@tigerex.com")

include(CPack)