#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <chrono>
#include <signal.h>

#include "engine/trading_engine.h"
#include "server/http_server.h"
#include "server/websocket_server.h"
#include "database/database_manager.h"
#include "redis/redis_manager.h"
#include "kafka/kafka_producer.h"
#include "config/config.h"
#include "logger/logger.h"

class TigerExTradingEngine {
private:
    std::unique_ptr<Config> config_;
    std::unique_ptr<DatabaseManager> db_manager_;
    std::unique_ptr<RedisManager> redis_manager_;
    std::unique_ptr<KafkaProducer> kafka_producer_;
    std::unique_ptr<TradingEngine> trading_engine_;
    std::unique_ptr<HttpServer> http_server_;
    std::unique_ptr<WebSocketServer> ws_server_;
    std::unique_ptr<Logger> logger_;
    
    bool running_;

public:

    std::string HealthCheck() {
        return R"({"status": "healthy", "service": ")trading-engineR"("})";
    }

    TigerExTradingEngine() : running_(false) {}

    bool Initialize() {
        try {
            // Initialize logger
            logger_ = std::make_unique<Logger>("trading-engine");
            logger_->Info("Initializing TigerEx Trading Engine...");

            // Load configuration
            config_ = std::make_unique<Config>();
            if (!config_->Load()) {
                logger_->Error("Failed to load configuration");
                return false;
            }

            // Initialize database connection
            db_manager_ = std::make_unique<DatabaseManager>(config_->GetDatabaseURL());
            if (!db_manager_->Connect()) {
                logger_->Error("Failed to connect to database");
                return false;
            }

            // Initialize Redis connection
            redis_manager_ = std::make_unique<RedisManager>(config_->GetRedisURL());
            if (!redis_manager_->Connect()) {
                logger_->Error("Failed to connect to Redis");
                return false;
            }

            // Initialize Kafka producer
            kafka_producer_ = std::make_unique<KafkaProducer>(config_->GetKafkaBrokers());
            if (!kafka_producer_->Initialize()) {
                logger_->Error("Failed to initialize Kafka producer");
                return false;
            }

            // Initialize trading engine
            trading_engine_ = std::make_unique<TradingEngine>(
                db_manager_.get(),
                redis_manager_.get(),
                kafka_producer_.get(),
                logger_.get()
            );
            
            if (!trading_engine_->Initialize()) {
                logger_->Error("Failed to initialize trading engine");
                return false;
            }

            // Initialize HTTP server
            http_server_ = std::make_unique<HttpServer>(
                config_->GetHttpPort(),
                trading_engine_.get(),
                logger_.get()
            );

            // Initialize WebSocket server
            ws_server_ = std::make_unique<WebSocketServer>(
                config_->GetWebSocketPort(),
                trading_engine_.get(),
                logger_.get()
            );

            logger_->Info("TigerEx Trading Engine initialized successfully");
            return true;

        } catch (const std::exception& e) {
            if (logger_) {
                logger_->Error("Exception during initialization: " + std::string(e.what()));
            }
            return false;
        }
    }

    void Start() {
        if (!Initialize()) {
            std::cerr << "Failed to initialize trading engine" << std::endl;
            return;
        }

        running_ = true;
        logger_->Info("Starting TigerEx Trading Engine...");

        // Start trading engine
        trading_engine_->Start();

        // Start HTTP server in separate thread
        std::thread http_thread([this]() {
            http_server_->Start();
        });

        // Start WebSocket server in separate thread
        std::thread ws_thread([this]() {
            ws_server_->Start();
        });

        logger_->Info("TigerEx Trading Engine started successfully");
        logger_->Info("HTTP Server running on port: " + std::to_string(config_->GetHttpPort()));
        logger_->Info("WebSocket Server running on port: " + std::to_string(config_->GetWebSocketPort()));

        // Main loop
        while (running_) {
            // Perform periodic tasks
            trading_engine_->ProcessPendingOrders();
            trading_engine_->UpdateMarketData();
            trading_engine_->CheckRiskLimits();
            
            // Sleep for a short interval
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        // Wait for threads to complete
        http_thread.join();
        ws_thread.join();

        logger_->Info("TigerEx Trading Engine stopped");
    }

    void Stop() {
        logger_->Info("Stopping TigerEx Trading Engine...");
        running_ = false;

        if (trading_engine_) {
            trading_engine_->Stop();
        }

        if (http_server_) {
            http_server_->Stop();
        }

        if (ws_server_) {
            ws_server_->Stop();
        }
    }
};

// Global instance for signal handling
std::unique_ptr<TigerExTradingEngine> g_engine;

void SignalHandler(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down gracefully..." << std::endl;
    if (g_engine) {
        g_engine->Stop();
    }
    exit(0);
}

int main(int argc, char* argv[]) {
    // Set up signal handlers
    signal(SIGINT, SignalHandler);
    signal(SIGTERM, SignalHandler);

    std::cout << "TigerEx Trading Engine v1.0.0" << std::endl;
    std::cout << "Copyright (c) 2024 TigerEx Team" << std::endl;
    std::cout << "Starting..." << std::endl;

    try {
        g_engine = std::make_unique<TigerExTradingEngine>();
        g_engine->Start();
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}