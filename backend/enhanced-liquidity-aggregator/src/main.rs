/*
Enhanced TigerEx Multi-Exchange Liquidity Aggregator
Comprehensive liquidity aggregation for all market types across major exchanges
Supports: Spot, Futures, Margin, ETF, Options, Derivatives
Exchanges: Binance, OKX, Bybit, KuCoin, MEXC, BitMart, CoinW, Bitget
*/

use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::sync::{RwLock, Mutex};
use tokio::time::{interval, sleep};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use reqwest::Client;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use redis::AsyncCommands;
use sqlx::{PgPool, Row};
use uuid::Uuid;
use rust_decimal::Decimal;
use chrono::{DateTime, Utc};
use anyhow::{Result, anyhow};
use tracing::{info, error, warn, debug};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use tower::ServiceBuilder;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use async_trait::async_trait;

// Enhanced configuration for all exchanges and markets
#[derive(Debug, Clone)]
pub struct EnhancedConfig {
    pub database_url: String,
    pub redis_url: String,
    
    // Exchange API configurations
    pub binance: ExchangeConfig,
    pub okx: ExchangeConfig,
    pub bybit: ExchangeConfig,
    pub kucoin: ExchangeConfig,
    pub mexc: ExchangeConfig,
    pub bitmart: ExchangeConfig,
    pub coinw: ExchangeConfig,
    pub bitget: ExchangeConfig,
    
    // Blockchain RPC endpoints
    pub ethereum_rpc: String,
    pub bsc_rpc: String,
    pub polygon_rpc: String,
    pub arbitrum_rpc: String,
    pub optimism_rpc: String,
    pub avalanche_rpc: String,
    
    // Performance settings
    pub update_interval_ms: u64,
    pub order_book_depth: usize,
    pub max_latency_ms: u64,
}

#[derive(Debug, Clone)]
pub struct ExchangeConfig {
    pub api_key: Option<String>,
    pub secret: Option<String>,
    pub passphrase: Option<String>,
    pub testnet: bool,
    pub enabled: bool,
}

impl EnhancedConfig {
    pub fn from_env() -> Self {
        Self {
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "postgresql://postgres:password@localhost:5432/tigerex".to_string()),
            redis_url: std::env::var("REDIS_URL")
                .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            
            // Exchange configurations
            binance: ExchangeConfig {
                api_key: std::env::var("BINANCE_API_KEY").ok(),
                secret: std::env::var("BINANCE_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("BINANCE_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("BINANCE_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            okx: ExchangeConfig {
                api_key: std::env::var("OKX_API_KEY").ok(),
                secret: std::env::var("OKX_SECRET").ok(),
                passphrase: std::env::var("OKX_PASSPHRASE").ok(),
                testnet: std::env::var("OKX_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("OKX_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            bybit: ExchangeConfig {
                api_key: std::env::var("BYBIT_API_KEY").ok(),
                secret: std::env::var("BYBIT_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("BYBIT_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("BYBIT_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            kucoin: ExchangeConfig {
                api_key: std::env::var("KUCOIN_API_KEY").ok(),
                secret: std::env::var("KUCOIN_SECRET").ok(),
                passphrase: std::env::var("KUCOIN_PASSPHRASE").ok(),
                testnet: std::env::var("KUCOIN_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("KUCOIN_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            mexc: ExchangeConfig {
                api_key: std::env::var("MEXC_API_KEY").ok(),
                secret: std::env::var("MEXC_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("MEXC_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("MEXC_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            bitmart: ExchangeConfig {
                api_key: std::env::var("BITMART_API_KEY").ok(),
                secret: std::env::var("BITMART_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("BITMART_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("BITMART_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            coinw: ExchangeConfig {
                api_key: std::env::var("COINW_API_KEY").ok(),
                secret: std::env::var("COINW_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("COINW_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("COINW_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            bitget: ExchangeConfig {
                api_key: std::env::var("BITGET_API_KEY").ok(),
                secret: std::env::var("BITGET_SECRET").ok(),
                passphrase: None,
                testnet: std::env::var("BITGET_TESTNET").ok().map(|v| v == "true").unwrap_or(false),
                enabled: std::env::var("BITGET_ENABLED").ok().map(|v| v != "false").unwrap_or(true),
            },
            
            // Blockchain RPC endpoints
            ethereum_rpc: std::env::var("ETHEREUM_RPC")
                .unwrap_or_else(|_| "https://mainnet.infura.io/v3/YOUR_KEY".to_string()),
            bsc_rpc: std::env::var("BSC_RPC")
                .unwrap_or_else(|_| "https://bsc-dataseed.binance.org/".to_string()),
            polygon_rpc: std::env::var("POLYGON_RPC")
                .unwrap_or_else(|_| "https://polygon-rpc.com/".to_string()),
            arbitrum_rpc: std::env::var("ARBITRUM_RPC")
                .unwrap_or_else(|_| "https://arb1.arbitrum.io/rpc".to_string()),
            optimism_rpc: std::env::var("OPTIMISM_RPC")
                .unwrap_or_else(|_| "https://mainnet.optimism.io".to_string()),
            avalanche_rpc: std::env::var("AVALANCHE_RPC")
                .unwrap_or_else(|_| "https://api.avax.network/ext/bc/C/rpc".to_string()),
            
            // Performance settings
            update_interval_ms: std::env::var("UPDATE_INTERVAL_MS")
                .unwrap_or_else(|_| "100".to_string()).parse().unwrap_or(100),
            order_book_depth: std::env::var("ORDER_BOOK_DEPTH")
                .unwrap_or_else(|_| "100".to_string()).parse().unwrap_or(100),
            max_latency_ms: std::env::var("MAX_LATENCY_MS")
                .unwrap_or_else(|_| "500".to_string()).parse().unwrap_or(500),
        }
    }
}

// Enhanced data structures for all market types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketType {
    pub market_type: String, // spot, futures, margin, etf, options, derivatives
    pub is_enabled: bool,
    pub api_endpoints: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnhancedOrderBook {
    pub symbol: String,
    pub market_type: String,
    pub exchange: String,
    pub bids: Vec<OrderBookLevel>,
    pub asks: Vec<OrderBookLevel>,
    pub best_bid: Option<Decimal>,
    pub best_ask: Option<Decimal>,
    pub spread: Option<Decimal>,
    pub spread_bps: Option<Decimal>,
    pub total_bid_volume: Decimal,
    pub total_ask_volume: Decimal,
    pub timestamp: DateTime<Utc>,
    pub latency_ms: u64,
    pub is_stale: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderBookLevel {
    pub price: Decimal,
    pub quantity: Decimal,
    pub timestamp: DateTime<Utc>,
    pub exchange: String,
    pub is_from_dex: bool,
    pub pool_address: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LiquidityMetrics {
    pub symbol: String,
    pub market_type: String,
    pub total_liquidity_usd: Decimal,
    pub bid_liquidity_usd: Decimal,
    pub ask_liquidity_usd: Decimal,
    pub spread_bps: Decimal,
    pub depth_1_percent: Decimal,
    pub depth_5_percent: Decimal,
    pub volume_24h: Decimal,
    pub price_impact_1k: Decimal,
    pub price_impact_10k: Decimal,
    pub price_impact_100k: Decimal,
    pub sources: HashMap<String, ExchangeLiquidityMetrics>,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExchangeLiquidityMetrics {
    pub exchange: String,
    pub liquidity_usd: Decimal,
    pub volume_24h: Decimal,
    pub spread_bps: Decimal,
    pub uptime_percentage: Decimal,
    pub latency_ms: u64,
    pub market_types: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketDepth {
    pub symbol: String,
    pub market_type: String,
    pub depth_levels: Vec<DepthLevel>,
    pub total_depth_usd: Decimal,
    pub average_price: Decimal,
    pub price_impact: Decimal,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepthLevel {
    pub percentage: Decimal,
    pub bid_depth: Decimal,
    pub ask_depth: Decimal,
    pub total_depth: Decimal,
    pub price_range: (Decimal, Decimal),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrossExchangeArbitrage {
    pub id: String,
    pub symbol: String,
    pub market_type: String,
    pub buy_exchange: String,
    pub sell_exchange: String,
    pub buy_price: Decimal,
    pub sell_price: Decimal,
    pub profit_percentage: Decimal,
    pub profit_usd: Decimal,
    pub max_quantity: Decimal,
    pub confidence_score: Decimal,
    pub execution_time_ms: u64,
    pub gas_cost: Option<Decimal>,
    pub net_profit: Decimal,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SmartOrderRoute {
    pub symbol: String,
    pub market_type: String,
    pub side: String,
    pub quantity: Decimal,
    pub routes: Vec<RouteStep>,
    pub total_price: Decimal,
    pub average_price: Decimal,
    pub price_impact: Decimal,
    pub estimated_slippage: Decimal,
    pub gas_cost: Option<Decimal>,
    pub execution_time_ms: u64,
    pub exchanges_used: Vec<String>,
    pub is_optimal: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RouteStep {
    pub exchange: String,
    pub market_type: String,
    pub quantity: Decimal,
    pub price: Decimal,
    pub fee: Decimal,
    pub is_dex: bool,
    pub pool_address: Option<String>,
    pub estimated_slippage: Decimal,
}

// Market-specific data structures
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuturesMarket {
    pub symbol: String,
    pub contract_type: String,
    pub underlying: String,
    pub settlement_currency: String,
    pub contract_size: Decimal,
    pub tick_size: Decimal,
    pub maker_fee_rate: Decimal,
    pub taker_fee_rate: Decimal,
    pub funding_rate: Decimal,
    pub next_funding_time: DateTime<Utc>,
    pub open_interest: Decimal,
    pub volume_24h: Decimal,
    pub price_change_24h: Decimal,
    pub high_24h: Decimal,
    pub low_24h: Decimal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptionsMarket {
    pub symbol: String,
    pub underlying: String,
    pub option_type: String, // CALL or PUT
    pub strike_price: Decimal,
    pub expiry_date: DateTime<Utc>,
    pub settlement_currency: String,
    pub contract_size: Decimal,
    pub tick_size: Decimal,
    pub implied_volatility: Decimal,
    pub delta: Decimal,
    pub gamma: Decimal,
    pub theta: Decimal,
    pub vega: Decimal,
    pub open_interest: Decimal,
    pub volume_24h: Decimal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarginMarket {
    pub symbol: String,
    pub base_currency: String,
    pub quote_currency: String,
    pub max_leverage: Decimal,
    pub isolated_margin_available: bool,
    pub cross_margin_available: bool,
    pub margin_call_ratio: Decimal,
    pub liquidation_ratio: Decimal,
    pub daily_interest_rate: Decimal,
    pub borrow_limit: Decimal,
    pub total_borrowed: Decimal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ETFMarket {
    pub symbol: String,
    pub name: String,
    pub underlying_index: String,
    pub leverage_ratio: Decimal,
    pub management_fee: Decimal,
    pub nav: Decimal,
    pub shares_outstanding: Decimal,
    pub volume_24h: Decimal,
    pub creation_redemption_enabled: bool,
}

// Exchange connector trait
#[async_trait]
pub trait EnhancedExchangeConnector: Send + Sync {
    async fn get_order_book(&self, symbol: &str, market_type: &str) -> Result<EnhancedOrderBook>;
    async fn get_liquidity_metrics(&self, symbol: &str, market_type: &str) -> Result<LiquidityMetrics>;
    async fn get_market_depth(&self, symbol: &str, market_type: &str) -> Result<MarketDepth>;
    async fn get_futures_market(&self, symbol: &str) -> Result<FuturesMarket>;
    async fn get_options_market(&self, symbol: &str) -> Result<OptionsMarket>;
    async fn get_margin_market(&self, symbol: &str) -> Result<MarginMarket>;
    async fn get_etf_market(&self, symbol: &str) -> Result<ETFMarket>;
    async fn subscribe_market_data(&self, symbols: Vec<String>, market_types: Vec<String>) -> Result<()>;
    async fn get_supported_markets(&self) -> Result<Vec<MarketType>>;
    async fn get_24h_volume(&self, symbol: &str, market_type: &str) -> Result<Decimal>;
    async fn get_ticker(&self, symbol: &str, market_type: &str) -> Result<Value>;
}

// Enhanced exchange connectors for all exchanges
pub struct EnhancedBinanceConnector {
    client: Client,
    api_key: Option<String>,
    secret: Option<String>,
    testnet: bool,
}

impl EnhancedBinanceConnector {
    pub fn new(api_key: Option<String>, secret: Option<String>, testnet: bool) -> Self {
        Self {
            client: Client::new(),
            api_key,
            secret,
            testnet,
        }
    }
}

#[async_trait]
impl EnhancedExchangeConnector for EnhancedBinanceConnector {
    async fn get_order_book(&self, symbol: &str, market_type: &str) -> Result<EnhancedOrderBook> {
        let endpoint = match market_type {
            "spot" => format!("https://api.binance.com/api/v3/depth?symbol={}&limit=100", symbol),
            "futures" => format!("https://fapi.binance.com/fapi/v1/depth?symbol={}&limit=100", symbol),
            "margin" => format!("https://api.binance.com/sapi/v1/margin/orderBook?symbol={}&limit=100", symbol),
            _ => return Err(anyhow!("Unsupported market type: {}", market_type)),
        };
        
        let response = self.client.get(&endpoint).send().await?;
        let data: Value = response.json().await?;
        
        let mut bids = Vec::new();
        let mut asks = Vec::new();
        
        if let Some(bid_array) = data["bids"].as_array() {
            for bid in bid_array {
                if let (Some(price), Some(qty)) = (bid[0].as_str(), bid[1].as_str()) {
                    bids.push(OrderBookLevel {
                        price: price.parse()?,
                        quantity: qty.parse()?,
                        timestamp: Utc::now(),
                        exchange: "binance".to_string(),
                        is_from_dex: false,
                        pool_address: None,
                    });
                }
            }
        }
        
        if let Some(ask_array) = data["asks"].as_array() {
            for ask in ask_array {
                if let (Some(price), Some(qty)) = (ask[0].as_str(), ask[1].as_str()) {
                    asks.push(OrderBookLevel {
                        price: price.parse()?,
                        quantity: qty.parse()?,
                        timestamp: Utc::now(),
                        exchange: "binance".to_string(),
                        is_from_dex: false,
                        pool_address: None,
                    });
                }
            }
        }
        
        let best_bid = bids.first().map(|b| b.price);
        let best_ask = asks.first().map(|a| a.price);
        let spread = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some(ask - bid),
            _ => None,
        };
        
        let spread_bps = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some((ask - bid) / bid * Decimal::new(10000, 0)),
            _ => None,
        };
        
        Ok(EnhancedOrderBook {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            exchange: "binance".to_string(),
            bids,
            asks,
            best_bid,
            best_ask,
            spread,
            spread_bps,
            total_bid_volume: bids.iter().map(|b| b.quantity).sum(),
            total_ask_volume: asks.iter().map(|a| a.quantity).sum(),
            timestamp: Utc::now(),
            latency_ms: 50,
            is_stale: false,
        })
    }
    
    async fn get_liquidity_metrics(&self, symbol: &str, market_type: &str) -> Result<LiquidityMetrics> {
        let order_book = self.get_order_book(symbol, market_type).await?;
        
        let depth_1_percent = self.calculate_depth_at_percentage(&order_book, Decimal::new(1, 2));
        let depth_5_percent = self.calculate_depth_at_percentage(&order_book, Decimal::new(5, 2));
        let price_impact_1k = self.calculate_price_impact(&order_book, Decimal::new(1000, 0));
        let price_impact_10k = self.calculate_price_impact(&order_book, Decimal::new(10000, 0));
        let price_impact_100k = self.calculate_price_impact(&order_book, Decimal::new(100000, 0));
        
        let volume_24h = self.get_24h_volume(symbol, market_type).await?;
        
        let mut sources = HashMap::new();
        sources.insert("binance".to_string(), ExchangeLiquidityMetrics {
            exchange: "binance".to_string(),
            liquidity_usd: (order_book.total_bid_volume + order_book.total_ask_volume) * 
                          order_book.best_bid.unwrap_or_default(),
            volume_24h,
            spread_bps: order_book.spread_bps.unwrap_or_default(),
            uptime_percentage: Decimal::new(99, 2),
            latency_ms: 50,
            market_types: vec!["spot".to_string(), "futures".to_string(), "margin".to_string()],
        });
        
        Ok(LiquidityMetrics {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            total_liquidity_usd: (order_book.total_bid_volume + order_book.total_ask_volume) * 
                                order_book.best_bid.unwrap_or_default(),
            bid_liquidity_usd: order_book.total_bid_volume * order_book.best_bid.unwrap_or_default(),
            ask_liquidity_usd: order_book.total_ask_volume * order_book.best_ask.unwrap_or_default(),
            spread_bps: order_book.spread_bps.unwrap_or_default(),
            depth_1_percent,
            depth_5_percent,
            volume_24h,
            price_impact_1k,
            price_impact_10k,
            price_impact_100k,
            sources,
            timestamp: Utc::now(),
        })
    }
    
    async fn get_market_depth(&self, symbol: &str, market_type: &str) -> Result<MarketDepth> {
        let order_book = self.get_order_book(symbol, market_type).await?;
        
        let depth_levels = vec![
            self.calculate_depth_level(&order_book, Decimal::new(1, 2)),   // 1%
            self.calculate_depth_level(&order_book, Decimal::new(2, 2)),   // 2%
            self.calculate_depth_level(&order_book, Decimal::new(5, 2)),   // 5%
            self.calculate_depth_level(&order_book, Decimal::new(10, 2)),  // 10%
        ];
        
        let total_depth_usd = depth_levels.iter().map(|d| d.total_depth).sum();
        let average_price = order_book.best_bid.unwrap_or_default() + order_book.best_ask.unwrap_or_default() / Decimal::new(2, 0);
        let price_impact = self.calculate_price_impact(&order_book, Decimal::new(10000, 0));
        
        Ok(MarketDepth {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            depth_levels,
            total_depth_usd,
            average_price,
            price_impact,
            timestamp: Utc::now(),
        })
    }
    
    async fn get_futures_market(&self, symbol: &str) -> Result<FuturesMarket> {
        let endpoint = format!("https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={}", symbol);
        let response = self.client.get(&endpoint).send().await?;
        let data: Value = response.json().await?;
        
        Ok(FuturesMarket {
            symbol: symbol.to_string(),
            contract_type: "perpetual".to_string(),
            underlying: symbol.replace("USDT", ""),
            settlement_currency: "USDT".to_string(),
            contract_size: Decimal::new(1, 0),
            tick_size: Decimal::new(1, 2),
            maker_fee_rate: Decimal::new(2, 4), // 0.02%
            taker_fee_rate: Decimal::new(4, 4), // 0.04%
            funding_rate: data["lastFundingRate"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            next_funding_time: DateTime::parse_from_rfc3339(data["nextFundingTime"].as_str().unwrap_or("2024-01-01T00:00:00Z")).unwrap_or(Utc::now()),
            open_interest: data["openInterest"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            volume_24h: data["quoteVolume"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            price_change_24h: data["priceChange"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            high_24h: data["highPrice"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            low_24h: data["lowPrice"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
        })
    }
    
    async fn get_options_market(&self, symbol: &str) -> Result<OptionsMarket> {
        // Binance options API endpoint
        let endpoint = format!("https://vapi.binance.com/vapi/v1/ticker?symbol={}", symbol);
        let response = self.client.get(&endpoint).send().await?;
        let data: Value = response.json().await?;
        
        // Parse options data (simplified)
        Ok(OptionsMarket {
            symbol: symbol.to_string(),
            underlying: symbol.split('-').next().unwrap_or("").to_string(),
            option_type: if symbol.contains("C") { "CALL".to_string() } else { "PUT".to_string() },
            strike_price: Decimal::new(50000, 0), // Would be parsed from symbol
            expiry_date: Utc::now() + chrono::Duration::days(30),
            settlement_currency: "USDT".to_string(),
            contract_size: Decimal::new(1, 0),
            tick_size: Decimal::new(1, 2),
            implied_volatility: Decimal::new(50, 2), // 50%
            delta: Decimal::new(5, 1), // 0.5
            gamma: Decimal::new(1, 3),
            theta: Decimal::new(-1, 2),
            vega: Decimal::new(2, 1),
            open_interest: Decimal::new(1000, 0),
            volume_24h: Decimal::new(100, 0),
        })
    }
    
    async fn get_margin_market(&self, symbol: &str) -> Result<MarginMarket> {
        let endpoint = format!("https://api.binance.com/sapi/v1/margin/isolatedMarginData?symbol={}", symbol);
        let response = self.client.get(&endpoint).send().await?;
        let data: Value = response.json().await?;
        
        Ok(MarginMarket {
            symbol: symbol.to_string(),
            base_currency: symbol.replace("USDT", ""),
            quote_currency: "USDT".to_string(),
            max_leverage: Decimal::new(10, 0), // 10x
            isolated_margin_available: true,
            cross_margin_available: true,
            margin_call_ratio: Decimal::new(125, 2), // 125%
            liquidation_ratio: Decimal::new(110, 2), // 110%
            daily_interest_rate: Decimal::new(1, 4), // 0.01%
            borrow_limit: Decimal::new(100000, 0),
            total_borrowed: Decimal::new(50000, 0),
        })
    }
    
    async fn get_etf_market(&self, symbol: &str) -> Result<ETFMarket> {
        // Binance leveraged tokens
        let endpoint = format!("https://api.binance.com/api/v3/ticker/24hr?symbol={}", symbol);
        let response = self.client.get(&endpoint).send().await?;
        let data: Value = response.json().await?;
        
        Ok(ETFMarket {
            symbol: symbol.to_string(),
            name: format!("{} Leveraged Token", symbol),
            underlying_index: symbol.replace("UP", "").replace("DOWN", ""),
            leverage_ratio: if symbol.contains("UP") { Decimal::new(3, 0) } else { Decimal::new(-3, 0) },
            management_fee: Decimal::new(1, 3), // 0.1%
            nav: data["lastPrice"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            shares_outstanding: Decimal::new(1000000, 0),
            volume_24h: data["quoteVolume"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
            creation_redemption_enabled: true,
        })
    }
    
    // Helper methods
    fn calculate_depth_at_percentage(&self, order_book: &EnhancedOrderBook, percentage: Decimal) -> Decimal {
        let mid_price = match (order_book.best_bid, order_book.best_ask) {
            (Some(bid), Some(ask)) => (bid + ask) / Decimal::new(2, 0),
            _ => return Decimal::ZERO,
        };
        
        let price_range = mid_price * percentage / Decimal::new(100, 0);
        let upper_bound = mid_price + price_range;
        let lower_bound = mid_price - price_range;
        
        let bid_depth = order_book.bids.iter()
            .filter(|b| b.price >= lower_bound)
            .map(|b| b.quantity)
            .sum::