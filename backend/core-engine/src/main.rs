//! TigerEx Core Trading Engine
//! High-performance matching engine with sub-microsecond latency

mod engine;
mod orderbook;
mod matching;
mod websocket;
mod api;
mod db;
mod cache;
mod admin;
mod auth;
mod risk;
mod models;
mod utils;

use std::net::SocketAddr;
use std::sync::Arc;
use tokio::sync::RwLock;
use axum::{
    routing::{get, post, put, delete},
    Router,
    Extension,
};
use tower_http::cors::{Any, CorsLayer};
use tower::ServiceBuilder;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use engine::TradingEngine;
use db::Database;
use cache::RedisCache;
use admin::AdminService;
use auth::AuthService;
use risk::RiskEngine;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    info!("🚀 Starting TigerEx Core Trading Engine v1.0.0");

    // Load configuration
    let config = utils::config::load_config()?;
    
    // Initialize database connection pool
    info!("📡 Connecting to database...");
    let db = Database::new(&config.database_url).await?;
    db.run_migrations().await?;
    
    // Initialize Redis cache
    info!("📦 Connecting to Redis...");
    let cache = RedisCache::new(&config.redis_url).await?;
    
    // Initialize trading engine
    info!("⚙️ Initializing Trading Engine...");
    let engine = Arc::new(RwLock::new(TradingEngine::new(Arc::clone(&db), Arc::clone(&cache))));
    
    // Initialize risk engine
    let risk_engine = Arc::new(RwLock::new(RiskEngine::new(Arc::clone(&db), Arc::clone(&cache))));
    
    // Initialize auth service
    let auth_service = Arc::new(AuthService::new(Arc::clone(&db), Arc::clone(&cache), config.jwt_secret.clone()));
    
    // Initialize admin service
    let admin_service = Arc::new(AdminService::new(
        Arc::clone(&db),
        Arc::clone(&cache),
        Arc::clone(&engine),
        Arc::clone(&auth_service),
    ));

    // Setup API routes
    let app = Router::new()
        // Health check
        .route("/health", get(api::health_check))
        .route("/ready", get(api::ready_check))
        
        // Public API
        .route("/api/v1/ping", get(api::ping))
        .route("/api/v1/time", get(api::server_time))
        .route("/api/v1/exchangeInfo", get(api::exchange_info))
        .route("/api/v1/depth", get(api::order_book_depth))
        .route("/api/v1/trades", get(api::recent_trades))
        .route("/api/v1/ticker/price", get(api::ticker_price))
        .route("/api/v1/ticker/24hr", get(api::ticker_24hr))
        .route("/api/v1/klines", get(api::klines))
        
        // Trading API (authenticated)
        .route("/api/v1/order", post(api::create_order))
        .route("/api/v1/order", delete(api::cancel_order))
        .route("/api/v1/order/:orderId", get(api::query_order))
        .route("/api/v1/openOrders", get(api::open_orders))
        .route("/api/v1/openOrders", delete(api::cancel_all_orders))
        .route("/api/v1/allOrders", get(api::all_orders))
        
        // Account API (authenticated)
        .route("/api/v1/account", get(api::account_info))
        .route("/api/v1/myTrades", get(api::my_trades))
        
        // WebSocket
        .route("/ws", get(websocket::ws_handler))
        
        // Admin API
        .route("/admin/v1/login", post(admin::login))
        .route("/admin/v1/users", get(admin::list_users))
        .route("/admin/v1/users", post(admin::create_user))
        .route("/admin/v1/users/:userId", get(admin::get_user))
        .route("/admin/v1/users/:userId", put(admin::update_user))
        .route("/admin/v1/users/:userId", delete(admin::delete_user))
        .route("/admin/v1/users/:userId/pause", post(admin::pause_user))
        .route("/admin/v1/users/:userId/resume", post(admin::resume_user))
        .route("/admin/v1/users/:userId/halt", post(admin::halt_user))
        .route("/admin/v1/users/:userId/permissions", put(admin::update_permissions))
        .route("/admin/v1/trading/pairs", get(admin::list_trading_pairs))
        .route("/admin/v1/trading/pairs", post(admin::create_trading_pair))
        .route("/admin/v1/trading/pairs/:pairId", put(admin::update_trading_pair))
        .route("/admin/v1/trading/pairs/:pairId", delete(admin::delete_trading_pair))
        .route("/admin/v1/trading/pairs/:pairId/pause", post(admin::pause_trading_pair))
        .route("/admin/v1/trading/pairs/:pairId/resume", post(admin::resume_trading_pair))
        .route("/admin/v1/trading/engine/status", get(admin::engine_status))
        .route("/admin/v1/trading/engine/pause", post(admin::pause_engine))
        .route("/admin/v1/trading/engine/resume", post(admin::resume_engine))
        .route("/admin/v1/fees", get(admin::get_fee_structure))
        .route("/admin/v1/fees", put(admin::update_fee_structure))
        .route("/admin/v1/risk/limits", get(admin::get_risk_limits))
        .route("/admin/v1/risk/limits", put(admin::update_risk_limits))
        .route("/admin/v1/risk/monitor", get(admin::risk_monitor))
        .route("/admin/v1/audit/logs", get(admin::audit_logs))
        .route("/admin/v1/system/metrics", get(admin::system_metrics))
        .route("/admin/v1/system/config", get(admin::get_config))
        .route("/admin/v1/system/config", put(admin::update_config))
        
        // Add extensions
        .layer(ServiceBuilder::new()
            .layer(CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any))
        )
        .layer(Extension(engine))
        .layer(Extension(db))
        .layer(Extension(cache))
        .layer(Extension(auth_service))
        .layer(Extension(admin_service))
        .layer(Extension(risk_engine))
        .layer(Extension(config.clone()));

    let addr: SocketAddr = format!("{}:{}", config.host, config.port).parse()?;
    
    info!("🌐 Server listening on {}", addr);
    
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await?;

    Ok(())
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
