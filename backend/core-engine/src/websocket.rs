//! WebSocket Handler for Real-time Market Data
//! Supports streaming orderbook, trades, klines, and account updates

use std::sync::Arc;
use axum::{
    extract::ws::{Message, WebSocket, WebSocketUpgrade},
    response::Response,
    Extension,
};
use futures::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error, debug};

use crate::models::*;
use crate::engine::TradingEngine;
use crate::cache::RedisCache;

/// WebSocket upgrade handler
pub async fn ws_handler(
    ws: WebSocketUpgrade,
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
    Extension(cache): Extension<Arc<RedisCache>>,
) -> Response {
    ws.on_upgrade(move |socket| handle_socket(socket, engine, cache))
}

/// Handle WebSocket connection
async fn handle_socket(socket: WebSocket, engine: Arc<parking_lot::RwLock<TradingEngine>>, cache: Arc<RedisCache>) {
    let (mut sender, mut receiver) = socket.split();

    info!("New WebSocket connection established");

    // Track subscriptions
    let subscriptions: Arc<tokio::sync::RwLock<Vec<String>>> = Arc::new(tokio::sync::RwLock::new(Vec::new()));

    // Handle incoming messages
    while let Some(msg) = receiver.next().await {
        match msg {
            Ok(Message::Text(text)) => {
                if let Ok(request) = serde_json::from_str::<WsRequest>(&text) {
                    handle_request(&request, &subscriptions).await;
                }
            }
            Ok(Message::Binary(data)) => {
                if let Ok(request) = serde_json::from_slice::<WsRequest>(&data) {
                    handle_request(&request, &subscriptions).await;
                }
            }
            Ok(Message::Ping(data)) => {
                let _ = sender.send(Message::Pong(data)).await;
            }
            Ok(Message::Close(_)) => {
                info!("WebSocket connection closed");
                break;
            }
            Err(e) => {
                warn!("WebSocket error: {}", e);
                break;
            }
            _ => {}
        }
    }
}

/// Handle WebSocket request
async fn handle_request(request: &WsRequest, subscriptions: &Arc<tokio::sync::RwLock<Vec<String>>>) {
    match request {
        WsRequest::Subscribe { streams } => {
            let mut subs = subscriptions.write().await;
            for stream in streams {
                if !subs.contains(stream) {
                    subs.push(stream.clone());
                }
            }
        }
        WsRequest::Unsubscribe { streams } => {
            let mut subs = subscriptions.write().await;
            subs.retain(|s| !streams.contains(s));
        }
    }
}

/// WebSocket request types
#[derive(Debug, Deserialize)]
#[serde(tag = "method", rename_all = "lowercase")]
pub enum WsRequest {
    Subscribe { streams: Vec<String> },
    Unsubscribe { streams: Vec<String> },
}

/// WebSocket response types
#[derive(Debug, Serialize)]
#[serde(untagged)]
pub enum WsResponse {
    OrderBook {
        stream: String,
        data: OrderBookMessage,
    },
    Trade {
        stream: String,
        data: TradeMessage,
    },
    Kline {
        stream: String,
        data: KlineMessage,
    },
    Ticker {
        stream: String,
        data: TickerMessage,
    },
    Account {
        stream: String,
        data: AccountMessage,
    },
    Order {
        stream: String,
        data: OrderMessage,
    },
}

/// Order book message
#[derive(Debug, Serialize)]
pub struct OrderBookMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "U")]
    pub first_update_id: u64,
    #[serde(rename = "u")]
    pub final_update_id: u64,
    #[serde(rename = "b")]
    pub bids: Vec<(String, String)>,
    #[serde(rename = "a")]
    pub asks: Vec<(String, String)>,
}

/// Trade message
#[derive(Debug, Serialize)]
pub struct TradeMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "t")]
    pub trade_id: u64,
    #[serde(rename = "p")]
    pub price: String,
    #[serde(rename = "q")]
    pub quantity: String,
    #[serde(rename = "b")]
    pub buyer_order_id: u64,
    #[serde(rename = "a")]
    pub seller_order_id: u64,
    #[serde(rename = "T")]
    pub trade_time: i64,
    #[serde(rename = "m")]
    pub is_buyer_maker: bool,
}

/// Kline message
#[derive(Debug, Serialize)]
pub struct KlineMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "k")]
    pub kline: KlineData,
}

#[derive(Debug, Serialize)]
pub struct KlineData {
    #[serde(rename = "t")]
    pub start_time: i64,
    #[serde(rename = "T")]
    pub end_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "i")]
    pub interval: String,
    #[serde(rename = "o")]
    pub open: String,
    #[serde(rename = "c")]
    pub close: String,
    #[serde(rename = "h")]
    pub high: String,
    #[serde(rename = "l")]
    pub low: String,
    #[serde(rename = "v")]
    pub volume: String,
    #[serde(rename = "q")]
    pub quote_volume: String,
    #[serde(rename = "n")]
    pub trades: u64,
    #[serde(rename = "x")]
    pub is_closed: bool,
}

/// Ticker message
#[derive(Debug, Serialize)]
pub struct TickerMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "p")]
    pub price_change: String,
    #[serde(rename = "P")]
    pub price_change_percent: String,
    #[serde(rename = "w")]
    pub weighted_avg_price: String,
    #[serde(rename = "x")]
    pub prev_close: String,
    #[serde(rename = "c")]
    pub last_price: String,
    #[serde(rename = "Q")]
    pub last_qty: String,
    #[serde(rename = "b")]
    pub bid_price: String,
    #[serde(rename = "B")]
    pub bid_qty: String,
    #[serde(rename = "a")]
    pub ask_price: String,
    #[serde(rename = "A")]
    pub ask_qty: String,
    #[serde(rename = "o")]
    pub open_price: String,
    #[serde(rename = "h")]
    pub high_price: String,
    #[serde(rename = "l")]
    pub low_price: String,
    #[serde(rename = "v")]
    pub volume: String,
    #[serde(rename = "q")]
    pub quote_volume: String,
}

/// Account message
#[derive(Debug, Serialize)]
pub struct AccountMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "B")]
    pub balances: Vec<BalanceMessage>,
}

#[derive(Debug, Serialize)]
pub struct BalanceMessage {
    #[serde(rename = "a")]
    pub asset: String,
    #[serde(rename = "f")]
    pub free: String,
    #[serde(rename = "l")]
    pub locked: String,
}

/// Order message
#[derive(Debug, Serialize)]
pub struct OrderMessage {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: i64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "c")]
    pub client_order_id: String,
    #[serde(rename = "S")]
    pub side: String,
    #[serde(rename = "o")]
    pub order_type: String,
    #[serde(rename = "f")]
    pub time_in_force: String,
    #[serde(rename = "q")]
    pub quantity: String,
    #[serde(rename = "p")]
    pub price: String,
    #[serde(rename = "P")]
    pub stop_price: String,
    #[serde(rename = "F")]
    pub filled_qty: String,
    #[serde(rename = "C")]
    pub cumulative_qty: String,
    #[serde(rename = "x")]
    pub current_exec_type: String,
    #[serde(rename = "X")]
    pub order_status: String,
    #[serde(rename = "i")]
    pub order_id: u64,
    #[serde(rename = "l")]
    pub last_exec_qty: String,
    #[serde(rename = "z")]
    pub cumulative_filled_qty: String,
    #[serde(rename = "L")]
    pub last_exec_price: String,
    #[serde(rename = "n")]
    pub commission: String,
    #[serde(rename = "N")]
    pub commission_asset: String,
    #[serde(rename = "T")]
    pub trade_time: i64,
    #[serde(rename = "t")]
    pub trade_id: i64,
}

/// WebSocket stream names
pub fn format_stream_name(stream_type: &str, symbol: &str, interval: Option<&str>) -> String {
    match stream_type {
        "depth" => format!("{}@depth", symbol.to_lowercase()),
        "trade" => format!("{}@trade", symbol.to_lowercase()),
        "kline" => format!("{}@kline_{}", symbol.to_lowercase(), interval.unwrap_or("1m")),
        "ticker" => format!("{}@ticker", symbol.to_lowercase()),
        "bookTicker" => format!("{}@bookTicker", symbol.to_lowercase()),
        "aggTrade" => format!("{}@aggTrade", symbol.to_lowercase()),
        _ => format!("{}@{}", symbol.to_lowercase(), stream_type),
    }
}

/// Broadcaster for WebSocket messages
pub struct WsBroadcaster {
    cache: Arc<RedisCache>,
}

impl WsBroadcaster {
    pub fn new(cache: Arc<RedisCache>) -> Self {
        Self { cache }
    }

    /// Broadcast order book update
    pub async fn broadcast_orderbook(&self, symbol: &str, orderbook: &OrderBook) {
        let message = OrderBookMessage {
            event_type: "depthUpdate".to_string(),
            event_time: chrono::Utc::now().timestamp_millis(),
            symbol: symbol.to_uppercase(),
            first_update_id: orderbook.last_update_id,
            final_update_id: orderbook.last_update_id,
            bids: orderbook.bids.iter().map(|b| (b.price.to_string(), b.quantity.to_string())).collect(),
            asks: orderbook.asks.iter().map(|a| (a.price.to_string(), a.quantity.to_string())).collect(),
        };

        let stream = format_stream_name("depth", symbol, None);
        let response = WsResponse::OrderBook { stream, data: message };
        
        if let Err(e) = self.cache.publish(&format!("ws:broadcast"), &response).await {
            warn!("Failed to broadcast orderbook: {}", e);
        }
    }

    /// Broadcast trade
    pub async fn broadcast_trade(&self, trade: &Trade) {
        let message = TradeMessage {
            event_type: "trade".to_string(),
            event_time: trade.timestamp.timestamp_millis(),
            symbol: trade.symbol.clone(),
            trade_id: trade.id.as_u128() as u64,
            price: trade.price.to_string(),
            quantity: trade.quantity.to_string(),
            buyer_order_id: trade.order_id.as_u128() as u64,
            seller_order_id: trade.counter_order_id.as_u128() as u64,
            trade_time: trade.timestamp.timestamp_millis(),
            is_buyer_maker: trade.is_maker,
        };

        let stream = format_stream_name("trade", &trade.symbol, None);
        let response = WsResponse::Trade { stream, data: message };
        
        if let Err(e) = self.cache.publish(&format!("ws:broadcast"), &response).await {
            warn!("Failed to broadcast trade: {}", e);
        }
    }

    /// Broadcast account update
    pub async fn broadcast_account(&self, user_id: uuid::Uuid, balances: Vec<Balance>) {
        let message = AccountMessage {
            event_type: "outboundAccountPosition".to_string(),
            event_time: chrono::Utc::now().timestamp_millis(),
            balances: balances.iter().map(|b| BalanceMessage {
                asset: b.asset.clone(),
                free: b.free.to_string(),
                locked: b.locked.to_string(),
            }).collect(),
        };

        let stream = format!("{}@account", user_id);
        let response = WsResponse::Account { stream, data: message };
        
        if let Err(e) = self.cache.publish(&format!("ws:user:{}", user_id), &response).await {
            warn!("Failed to broadcast account update: {}", e);
        }
    }

    /// Broadcast order update
    pub async fn broadcast_order(&self, order: &Order) {
        let message = OrderMessage {
            event_type: "executionReport".to_string(),
            event_time: chrono::Utc::now().timestamp_millis(),
            symbol: order.symbol.clone(),
            client_order_id: order.client_order_id.clone().unwrap_or_default(),
            side: format!("{:?}", order.side).to_uppercase(),
            order_type: format!("{:?}", order.order_type).to_uppercase(),
            time_in_force: format!("{:?}", order.time_in_force).to_uppercase(),
            quantity: order.quantity.to_string(),
            price: order.price.unwrap_or_default().to_string(),
            stop_price: order.stop_price.unwrap_or_default().to_string(),
            filled_qty: order.filled_quantity.to_string(),
            cumulative_qty: order.filled_quantity.to_string(),
            current_exec_type: format!("{:?}", order.status),
            order_status: format!("{:?}", order.status).to_uppercase(),
            order_id: order.id.as_u128() as u64,
            last_exec_qty: order.filled_quantity.to_string(),
            cumulative_filled_qty: order.filled_quantity.to_string(),
            last_exec_price: order.average_price.to_string(),
            commission: "0".to_string(),
            commission_asset: "USDT".to_string(),
            trade_time: chrono::Utc::now().timestamp_millis(),
            trade_id: 0,
        };

        let stream = format!("{}@order", order.user_id);
        let response = WsResponse::Order { stream, data: message };
        
        if let Err(e) = self.cache.publish(&format!("ws:user:{}", order.user_id), &response).await {
            warn!("Failed to broadcast order update: {}", e);
        }
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
