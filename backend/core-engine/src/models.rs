//! Data models for the trading engine

use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use std::collections::HashMap;

/// Order types supported by the engine
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum OrderType {
    Market,
    Limit,
    StopLoss,
    StopLossLimit,
    TakeProfit,
    TakeProfitLimit,
    LimitMaker,
    TrailingStop,
    Iceberg,
    Twap,
    Vwap,
    FillOrKill,
    ImmediateOrCancel,
}

/// Order side (buy/sell)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum OrderSide {
    Buy,
    Sell,
}

/// Order status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum OrderStatus {
    New,
    PartiallyFilled,
    Filled,
    Canceled,
    PendingCancel,
    Rejected,
    Expired,
    Halted,
}

/// Time in force
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TimeInForce {
    Gtc, // Good Till Cancel
    Ioc, // Immediate or Cancel
    Fok, // Fill or Kill
    Gtx, // Good Till Crossing (Post Only)
}

/// Order representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub id: Uuid,
    pub client_order_id: Option<String>,
    pub user_id: Uuid,
    pub symbol: String,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub status: OrderStatus,
    pub price: Option<Decimal>,
    pub stop_price: Option<Decimal>,
    pub quantity: Decimal,
    pub filled_quantity: Decimal,
    pub remaining_quantity: Decimal,
    pub average_price: Decimal,
    pub time_in_force: TimeInForce,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub is_working: bool,
    pub iceberg_qty: Option<Decimal>,
    pub trailing_delta: Option<Decimal>,
    pub metadata: HashMap<String, String>,
}

impl Order {
    pub fn new(
        user_id: Uuid,
        symbol: String,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Option<Decimal>,
        time_in_force: TimeInForce,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            client_order_id: None,
            user_id,
            symbol,
            side,
            order_type,
            status: OrderStatus::New,
            price,
            stop_price: None,
            quantity,
            filled_quantity: Decimal::ZERO,
            remaining_quantity: quantity,
            average_price: Decimal::ZERO,
            time_in_force,
            created_at: now,
            updated_at: now,
            expires_at: None,
            is_working: true,
            iceberg_qty: None,
            trailing_delta: None,
            metadata: HashMap::new(),
        }
    }

    pub fn fill(&mut self, quantity: Decimal, price: Decimal) {
        let total_filled = self.filled_quantity + quantity;
        let total_value = (self.average_price * self.filled_quantity) + (price * quantity);
        
        self.filled_quantity = total_filled;
        self.remaining_quantity = self.quantity - total_filled;
        self.average_price = total_value / total_filled;
        self.updated_at = Utc::now();
        
        if self.remaining_quantity == Decimal::ZERO {
            self.status = OrderStatus::Filled;
        } else {
            self.status = OrderStatus::PartiallyFilled;
        }
    }

    pub fn cancel(&mut self) {
        self.status = OrderStatus::Canceled;
        self.is_working = false;
        self.updated_at = Utc::now();
    }

    pub fn reject(&mut self) {
        self.status = OrderStatus::Rejected;
        self.is_working = false;
        self.updated_at = Utc::now();
    }
}

/// Trade representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub id: Uuid,
    pub symbol: String,
    pub order_id: Uuid,
    pub counter_order_id: Uuid,
    pub user_id: Uuid,
    pub counter_user_id: Uuid,
    pub side: OrderSide,
    pub price: Decimal,
    pub quantity: Decimal,
    pub fee: Decimal,
    pub fee_currency: String,
    pub is_maker: bool,
    pub timestamp: DateTime<Utc>,
}

/// Order book level
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderBookLevel {
    pub price: Decimal,
    pub quantity: Decimal,
    pub order_count: u64,
}

/// Order book representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderBook {
    pub symbol: String,
    pub bids: Vec<OrderBookLevel>,
    pub asks: Vec<OrderBookLevel>,
    pub last_update_id: u64,
    pub timestamp: DateTime<Utc>,
}

/// Ticker information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Ticker {
    pub symbol: String,
    pub price_change: Decimal,
    pub price_change_percent: Decimal,
    pub weighted_avg_price: Decimal,
    pub prev_close_price: Decimal,
    pub last_price: Decimal,
    pub last_qty: Decimal,
    pub bid_price: Decimal,
    pub bid_qty: Decimal,
    pub ask_price: Decimal,
    pub ask_qty: Decimal,
    pub open_price: Decimal,
    pub high_price: Decimal,
    pub low_price: Decimal,
    pub volume: Decimal,
    pub quote_volume: Decimal,
    pub open_time: DateTime<Utc>,
    pub close_time: DateTime<Utc>,
    pub count: u64,
}

/// User account
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub user_id: Uuid,
    pub email: String,
    pub username: String,
    pub role: UserRole,
    pub status: AccountStatus,
    pub balances: Vec<Balance>,
    pub permissions: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub kyc_level: u8,
    pub trading_enabled: bool,
    pub withdrawal_enabled: bool,
    pub deposit_enabled: bool,
}

/// User role
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum UserRole {
    Admin,
    SuperAdmin,
    Moderator,
    User,
    Institutional,
    MarketMaker,
    LiquidityProvider,
    ApiUser,
}

/// Account status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AccountStatus {
    Active,
    Paused,
    Halted,
    Suspended,
    PendingVerification,
    Closed,
}

/// Balance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub asset: String,
    pub free: Decimal,
    pub locked: Decimal,
    pub freeze: Decimal,
    pub withdrawing: Decimal,
}

/// Trading pair
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TradingPair {
    pub id: Uuid,
    pub symbol: String,
    pub base_asset: String,
    pub quote_asset: String,
    pub status: TradingPairStatus,
    pub base_precision: u8,
    pub quote_precision: u8,
    pub min_qty: Decimal,
    pub max_qty: Decimal,
    pub min_price: Decimal,
    pub max_price: Decimal,
    pub tick_size: Decimal,
    pub step_size: Decimal,
    pub maker_fee: Decimal,
    pub taker_fee: Decimal,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Trading pair status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TradingPairStatus {
    Trading,
    Pause,
    Delist,
    PreTrading,
    PostTrading,
}

/// Candlestick/Kline
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Kline {
    pub open_time: DateTime<Utc>,
    pub open: Decimal,
    pub high: Decimal,
    pub low: Decimal,
    pub close: Decimal,
    pub volume: Decimal,
    pub close_time: DateTime<Utc>,
    pub quote_volume: Decimal,
    pub trades: u64,
    pub taker_buy_volume: Decimal,
    pub taker_buy_quote_volume: Decimal,
}

/// API Key
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKey {
    pub id: Uuid,
    pub user_id: Uuid,
    pub name: String,
    pub api_key: String,
    pub api_secret: String,
    pub permissions: Vec<String>,
    pub ip_whitelist: Vec<String>,
    pub rate_limit: u32,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
    pub last_used_at: Option<DateTime<Utc>>,
    pub enabled: bool,
}

/// Audit log entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditLog {
    pub id: Uuid,
    pub user_id: Option<Uuid>,
    pub action: String,
    pub resource_type: String,
    pub resource_id: String,
    pub old_value: Option<serde_json::Value>,
    pub new_value: Option<serde_json::Value>,
    pub ip_address: String,
    pub user_agent: String,
    pub timestamp: DateTime<Utc>,
    pub status: String,
    pub error_message: Option<String>,
}

/// Risk limits for a user
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskLimits {
    pub user_id: Uuid,
    pub max_order_value: Decimal,
    pub max_daily_volume: Decimal,
    pub max_position_size: Decimal,
    pub max_leverage: Decimal,
    pub max_open_orders: u32,
    pub rate_limit_per_second: u32,
    pub rate_limit_per_minute: u32,
    pub margin_required: Decimal,
}

/// WebSocket message types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "SCREAMING_SNAKE_CASE")]
pub enum WsMessage {
    Subscribe { streams: Vec<String> },
    Unsubscribe { streams: Vec<String> },
    OrderBookUpdate { symbol: String, data: OrderBook },
    TradeUpdate { symbol: String, data: Trade },
    KlineUpdate { symbol: String, interval: String, data: Kline },
    TickerUpdate { symbol: String, data: Ticker },
    AccountUpdate { balances: Vec<Balance> },
    OrderUpdate { order: Order },
}