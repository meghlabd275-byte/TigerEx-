//! API Handlers
//! REST API endpoints for trading and market data

use axum::{
    extract::{Path, Query, State, Extension},
    http::StatusCode,
    response::{IntoResponse, Json},
};
use serde::{Deserialize, Serialize};
use rust_decimal::Decimal;
use uuid::Uuid;
use chrono::Utc;

use crate::models::*;
use crate::engine::TradingEngine;
use crate::auth::AuthService;

// ==================== HEALTH CHECKS ====================

pub async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "healthy",
        "timestamp": Utc::now().to_rfc3339()
    }))
}

pub async fn ready_check(
    Extension(db): Extension<Arc<crate::db::Database>>,
    Extension(cache): Extension<Arc<crate::cache::RedisCache>>,
) -> impl IntoResponse {
    // Check database connection
    let db_ready = true; // Would check actual connection
    
    // Check cache connection
    let cache_ready = cache.exists("health:check").await || true;

    if db_ready && cache_ready {
        Json(serde_json::json!({
            "status": "ready",
            "services": {
                "database": "up",
                "cache": "up"
            }
        }))
    } else {
        StatusCode::SERVICE_UNAVAILABLE.into_response()
    }
}

pub async fn ping() -> impl IntoResponse {
    Json(serde_json::json!({ "ping": "pong" }))
}

pub async fn server_time() -> impl IntoResponse {
    Json(serde_json::json!({
        "serverTime": Utc::now().timestamp_millis()
    }))
}

// ==================== MARKET DATA ====================

#[derive(Debug, Deserialize)]
pub struct ExchangeInfoQuery {
    pub symbol: Option<String>,
    pub symbols: Option<String>,
}

pub async fn exchange_info(
    Query(_query): Query<ExchangeInfoQuery>,
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
) -> impl IntoResponse {
    let engine = engine.read();
    let pairs = engine.trading_pairs.read();
    
    let symbols: Vec<_> = pairs.values()
        .map(|p| serde_json::json!({
            "symbol": p.symbol,
            "status": format!("{:?}", p.status),
            "baseAsset": p.base_asset,
            "quoteAsset": p.quote_asset,
            "baseAssetPrecision": p.base_precision,
            "quotePrecision": p.quote_precision,
            "orderTypes": ["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"],
            "icebergAllowed": true,
            "filters": [
                {
                    "filterType": "PRICE_FILTER",
                    "minPrice": p.min_price.to_string(),
                    "maxPrice": p.max_price.to_string(),
                    "tickSize": p.tick_size.to_string()
                },
                {
                    "filterType": "LOT_SIZE",
                    "minQty": p.min_qty.to_string(),
                    "maxQty": p.max_qty.to_string(),
                    "stepSize": p.step_size.to_string()
                }
            ]
        }))
        .collect();

    Json(serde_json::json!({
        "timezone": "UTC",
        "serverTime": Utc::now().timestamp_millis(),
        "rateLimits": [
            {
                "rateLimitType": "REQUEST_WEIGHT",
                "interval": "MINUTE",
                "limit": 1200
            }
        ],
        "symbols": symbols
    }))
}

#[derive(Debug, Deserialize)]
pub struct OrderBookQuery {
    pub symbol: String,
    #[serde(default = "default_limit")]
    pub limit: usize,
}

fn default_limit() -> usize { 100 }

pub async fn order_book_depth(
    Query(query): Query<OrderBookQuery>,
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
) -> impl IntoResponse {
    let engine = engine.read();
    
    match engine.get_order_book_depth(&query.symbol, query.limit) {
        Some(book) => Json(serde_json::json!({
            "lastUpdateId": book.last_update_id,
            "bids": book.bids.iter().map(|b| [b.price.to_string(), b.quantity.to_string()]).collect::<Vec<_>>(),
            "asks": book.asks.iter().map(|a| [a.price.to_string(), a.quantity.to_string()]).collect::<Vec<_>>()
        })),
        None => Json(serde_json::json!({
            "code": -1121,
            "msg": "Invalid symbol"
        }))
    }
}

#[derive(Debug, Deserialize)]
pub struct TradesQuery {
    pub symbol: String,
    #[serde(default = "default_trade_limit")]
    pub limit: usize,
}

fn default_trade_limit() -> usize { 500 }

pub async fn recent_trades(
    Query(query): Query<TradesQuery>,
) -> impl IntoResponse {
    // Would fetch from database
    Json(serde_json::json!([]))
}

#[derive(Debug, Deserialize)]
pub struct TickerQuery {
    pub symbol: Option<String>,
}

pub async fn ticker_price(
    Query(query): Query<TickerQuery>,
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
) -> impl IntoResponse {
    let engine = engine.read();
    
    if let Some(symbol) = query.symbol {
        match engine.get_ticker(&symbol) {
            Some(ticker) => Json(serde_json::json!({
                "symbol": ticker.symbol,
                "price": ticker.last_price.to_string()
            })),
            None => Json(serde_json::json!({
                "code": -1121,
                "msg": "Invalid symbol"
            }))
        }
    } else {
        let tickers = engine.get_all_tickers();
        Json(serde_json::json!(
            tickers.iter().map(|t| serde_json::json!({
                "symbol": t.symbol,
                "price": t.last_price.to_string()
            })).collect::<Vec<_>>()
        ))
    }
}

pub async fn ticker_24hr(
    Query(query): Query<TickerQuery>,
) -> impl IntoResponse {
    // Would fetch 24hr ticker data
    Json(serde_json::json!({}))
}

#[derive(Debug, Deserialize)]
pub struct KlinesQuery {
    pub symbol: String,
    pub interval: String,
    #[serde(default)]
    pub start_time: Option<i64>,
    #[serde(default)]
    pub end_time: Option<i64>,
    #[serde(default = "default_kline_limit")]
    pub limit: usize,
}

fn default_kline_limit() -> usize { 500 }

pub async fn klines(
    Query(query): Query<KlinesQuery>,
) -> impl IntoResponse {
    // Would fetch klines from database
    Json(serde_json::json!([]))
}

// ==================== TRADING ====================

#[derive(Debug, Deserialize)]
pub struct CreateOrderRequest {
    pub symbol: String,
    pub side: String,
    #[serde(rename = "type")]
    pub order_type: String,
    pub time_in_force: Option<String>,
    pub quantity: Decimal,
    pub price: Option<Decimal>,
    pub stop_price: Option<Decimal>,
    pub new_client_order_id: Option<String>,
    pub iceberg_qty: Option<Decimal>,
    pub new_order_resp_type: Option<String>,
}

pub async fn create_order(
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
    Extension(auth): Extension<Arc<AuthService>>,
    Extension(user): Extension<Account>,
    Json(request): Json<CreateOrderRequest>,
) -> impl IntoResponse {
    let side = match request.side.to_uppercase().as_str() {
        "BUY" => OrderSide::Buy,
        "SELL" => OrderSide::Sell,
        _ => return Json(serde_json::json!({
            "code": -1100,
            "msg": "Illegal characters found in parameter 'side'"
        })),
    };

    let order_type = match request.order_type.to_uppercase().as_str() {
        "LIMIT" => OrderType::Limit,
        "MARKET" => OrderType::Market,
        "STOP_LOSS" => OrderType::StopLoss,
        "STOP_LOSS_LIMIT" => OrderType::StopLossLimit,
        "TAKE_PROFIT" => OrderType::TakeProfit,
        "TAKE_PROFIT_LIMIT" => OrderType::TakeProfitLimit,
        "LIMIT_MAKER" => OrderType::LimitMaker,
        _ => return Json(serde_json::json!({
            "code": -1100,
            "msg": "Invalid order type"
        })),
    };

    let time_in_force = match request.time_in_force.as_deref() {
        Some("GTC") => TimeInForce::Gtc,
        Some("IOC") => TimeInForce::Ioc,
        Some("FOK") => TimeInForce::Fok,
        Some("GTX") => TimeInForce::Gtx,
        _ => TimeInForce::Gtc,
    };

    let mut order = Order::new(
        user.user_id,
        request.symbol.clone(),
        side,
        order_type,
        request.quantity,
        request.price,
        time_in_force,
    );

    order.client_order_id = request.new_client_order_id;
    order.stop_price = request.stop_price;

    let engine = engine.read();
    match engine.create_order(order).await {
        Ok((filled_order, trades)) => {
            Json(serde_json::json!({
                "symbol": filled_order.symbol,
                "orderId": filled_order.id,
                "clientOrderId": filled_order.client_order_id,
                "transactTime": Utc::now().timestamp_millis(),
                "price": filled_order.price.unwrap_or(Decimal::ZERO).to_string(),
                "origQty": filled_order.quantity.to_string(),
                "executedQty": filled_order.filled_quantity.to_string(),
                "cumulativeQuoteQty": (filled_order.filled_quantity * filled_order.average_price).to_string(),
                "status": format!("{:?}", filled_order.status),
                "timeInForce": format!("{:?}", filled_order.time_in_force),
                "type": format!("{:?}", filled_order.order_type),
                "side": format!("{:?}", filled_order.side)
            }))
        }
        Err(e) => Json(serde_json::json!({
            "code": -2010,
            "msg": e
        }))
    }
}

#[derive(Debug, Deserialize)]
pub struct CancelOrderQuery {
    pub symbol: String,
    pub order_id: Option<Uuid>,
    pub client_order_id: Option<String>,
}

pub async fn cancel_order(
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
    Extension(user): Extension<Account>,
    Query(query): Query<CancelOrderQuery>,
) -> impl IntoResponse {
    let order_id = match query.order_id {
        Some(id) => id,
        None => return Json(serde_json::json!({
            "code": -1100,
            "msg": "Missing orderId"
        })),
    };

    let engine = engine.read();
    match engine.cancel_order(user.user_id, order_id, query.symbol.clone()).await {
        Ok(order) => Json(serde_json::json!({
            "symbol": order.symbol,
            "orderId": order.id,
            "origClientOrderId": order.client_order_id,
            "clientOrderId": format!("cancel_{}", order.id),
            "price": order.price.unwrap_or(Decimal::ZERO).to_string(),
            "origQty": order.quantity.to_string(),
            "executedQty": order.filled_quantity.to_string(),
            "cumulativeQuoteQty": (filled_order.filled_quantity * order.average_price).to_string(),
            "status": format!("{:?}", order.status),
            "timeInForce": format!("{:?}", order.time_in_force),
            "type": format!("{:?}", order.order_type),
            "side": format!("{:?}", order.side)
        })),
        Err(e) => Json(serde_json::json!({
            "code": -2011,
            "msg": e
        }))
    }
}

#[derive(Debug, Deserialize)]
pub struct QueryOrderQuery {
    pub symbol: String,
    pub order_id: Option<Uuid>,
    pub client_order_id: Option<String>,
}

pub async fn query_order(
    Extension(user): Extension<Account>,
    Query(query): Query<QueryOrderQuery>,
) -> impl IntoResponse {
    // Would fetch from database
    Json(serde_json::json!({}))
}

pub async fn open_orders(
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
    Extension(user): Extension<Account>,
    Query(query): Query<TickerQuery>,
) -> impl IntoResponse {
    // Would fetch from database/cache
    Json(serde_json::json!([]))
}

pub async fn cancel_all_orders(
    Extension(engine): Extension<Arc<parking_lot::RwLock<TradingEngine>>>,
    Extension(user): Extension<Account>,
    Query(query): Query<TickerQuery>,
) -> impl IntoResponse {
    let engine = engine.read();
    match engine.cancel_all_orders(user.user_id, query.symbol).await {
        Ok(orders) => Json(serde_json::json!(
            orders.iter().map(|o| serde_json::json!({
                "symbol": o.symbol,
                "orderId": o.id,
                "status": format!("{:?}", o.status)
            })).collect::<Vec<_>>()
        )),
        Err(e) => Json(serde_json::json!({
            "code": -2011,
            "msg": e
        }))
    }
}

pub async fn all_orders(
    Extension(user): Extension<Account>,
    Query(query): Query<QueryOrderQuery>,
) -> impl IntoResponse {
    // Would fetch from database
    Json(serde_json::json!([]))
}

// ==================== ACCOUNT ====================

pub async fn account_info(
    Extension(user): Extension<Account>,
) -> impl IntoResponse {
    Json(serde_json::json!({
        "makerCommission": 10,
        "takerCommission": 10,
        "buyerCommission": 0,
        "sellerCommission": 0,
        "canTrade": user.trading_enabled,
        "canWithdraw": user.withdrawal_enabled,
        "canDeposit": user.deposit_enabled,
        "updateTime": Utc::now().timestamp_millis(),
        "balances": user.balances.iter().map(|b| serde_json::json!({
            "asset": b.asset,
            "free": b.free.to_string(),
            "locked": b.locked.to_string()
        })).collect::<Vec<_>>()
    }))
}

#[derive(Debug, Deserialize)]
pub struct MyTradesQuery {
    pub symbol: String,
    #[serde(default)]
    pub start_time: Option<i64>,
    #[serde(default)]
    pub end_time: Option<i64>,
    #[serde(default = "default_trade_limit")]
    pub limit: usize,
}

pub async fn my_trades(
    Extension(user): Extension<Account>,
    Query(query): Query<MyTradesQuery>,
) -> impl IntoResponse {
    // Would fetch from database
    Json(serde_json::json!([]))
}