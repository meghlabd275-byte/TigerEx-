//! FIX Protocol Engine for TigerEx
//! Supports FIX 4.4 and FIX 5.0 for institutional trading

mod fix;
mod session;
mod messages;
mod engine;
mod admin;
mod security;

use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::signal;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use fix::FixServer;
use session::SessionManager;
use engine::TradingEngineConnector;

#[derive(Clone)]
pub struct Config {
    pub fix_host: String,
    pub fix_port: u16,
    pub fix_ssl_port: u16,
    pub database_url: String,
    pub redis_url: String,
    pub default_heartbeat_interval: u32,
    pub max_sessions: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            fix_host: "0.0.0.0".to_string(),
            fix_port: 9876,
            fix_ssl_port: 9877,
            database_url: std::env::var("DATABASE_URL").unwrap_or_else(|_| "postgres://tiger:password@localhost/tigerex".to_string()),
            redis_url: std::env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            default_heartbeat_interval: 30,
            max_sessions: 1000,
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let config = Config::default();
    info!("Starting TigerEx FIX Protocol Engine...");
    
    // Initialize session manager
    let session_manager = Arc::new(SessionManager::new(config.max_sessions));
    
    // Initialize trading engine connector
    let engine_connector = Arc::new(TradingEngineConnector::new(&config.database_url, &config.redis_url).await?);
    
    // Start FIX server
    let fix_server = FixServer::new(
        config.clone(),
        session_manager.clone(),
        engine_connector.clone(),
    );
    
    // Bind TCP listener for FIX connections
    let addr: SocketAddr = format!("{}:{}", config.fix_host, config.fix_port).parse()?;
    let listener = TcpListener::bind(addr).await?;
    
    info!("FIX Protocol Engine listening on {}", addr);
    
    // Accept connections
    loop {
        tokio::select! {
            result = listener.accept() => {
                match result {
                    Ok((stream, peer_addr)) => {
                        info!("New FIX connection from {}", peer_addr);
                        let server = fix_server.clone();
                        tokio::spawn(async move {
                            if let Err(e) = server.handle_connection(stream).await {
                                error!("Error handling FIX connection: {}", e);
                            }
                        });
                    }
                    Err(e) => {
                        error!("Error accepting connection: {}", e);
                    }
                }
            }
            _ = signal::ctrl_c() => {
                info!("Shutting down FIX Protocol Engine...");
                break;
            }
        }
    }
    
    Ok(())
}