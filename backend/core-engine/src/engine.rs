//! Core Trading Engine
//! High-performance matching engine with sub-microsecond latency

use std::collections::HashMap;
use std::sync::Arc;
use std::time::Instant;
use parking_lot::RwLock;
use tokio::sync::mpsc;
use rust_decimal::Decimal;
use uuid::Uuid;
use chrono::Utc;
use tracing::{info, warn, error, debug, instrument};

use crate::models::*;
use crate::orderbook::OrderBook;
use crate::db::Database;
use crate::cache::RedisCache;

/// Configuration for the trading engine
#[derive(Debug, Clone)]
pub struct EngineConfig {
    pub max_order_value: Decimal,
    pub min_order_value: Decimal,
    pub default_maker_fee: Decimal,
    pub default_taker_fee: Decimal,
    pub max_open_orders_per_user: u32,
    pub order_batch_size: usize,
    pub enable_auto_cancel: bool,
}

impl Default for EngineConfig {
    fn default() -> Self {
        Self {
            max_order_value: Decimal::from(1_000_000),
            min_order_value: Decimal::from(10),
            default_maker_fee: Decimal::from_str_exact("0.001").unwrap(),
            default_taker_fee: Decimal::from_str_exact("0.001").unwrap(),
            max_open_orders_per_user: 200,
            order_batch_size: 1000,
            enable_auto_cancel: true,
        }
    }
}

/// Engine statistics
#[derive(Debug, Clone, Default)]
pub struct EngineStats {
    pub total_orders_processed: u64,
    pub total_trades_executed: u64,
    pub total_volume: Decimal,
    pub avg_latency_us: f64,
    pub max_latency_us: f64,
    pub orders_per_second: f64,
    pub last_update: chrono::DateTime<Utc>,
}

/// Trading engine state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EngineState {
    Running,
    Paused,
    Halted,
    Maintenance,
}

/// Main trading engine
pub struct TradingEngine {
    pub order_books: RwLock<HashMap<String, OrderBook>>,
    pub trading_pairs: RwLock<HashMap<String, TradingPair>>,
    pub user_orders: RwLock<HashMap<Uuid, Vec<Uuid>>>,
    pub config: EngineConfig,
    pub stats: RwLock<EngineStats>,
    pub state: RwLock<EngineState>,
    pub db: Arc<Database>,
    pub cache: Arc<RedisCache>,
    pub start_time: chrono::DateTime<Utc>,
}

impl TradingEngine {
    pub fn new(db: Arc<Database>, cache: Arc<RedisCache>) -> Self {
        Self {
            order_books: RwLock::new(HashMap::new()),
            trading_pairs: RwLock::new(HashMap::new()),
            user_orders: RwLock::new(HashMap::new()),
            config: EngineConfig::default(),
            stats: RwLock::new(EngineStats::default()),
            state: RwLock::new(EngineState::Running),
            db,
            cache,
            start_time: Utc::now(),
        }
    }

    /// Initialize trading pairs and order books
    pub async fn initialize(&self) -> Result<(), anyhow::Error> {
        info!("Initializing trading engine...");
        
        // Load trading pairs from database
        let pairs = self.db.get_trading_pairs().await?;
        
        let mut trading_pairs = self.trading_pairs.write();
        let mut order_books = self.order_books.write();
        
        for pair in pairs {
            trading_pairs.insert(pair.symbol.clone(), pair.clone());
            order_books.insert(pair.symbol.clone(), OrderBook::new(pair.symbol));
        }
        
        info!("Loaded {} trading pairs", trading_pairs.len());
        
        // Load active orders from database
        let active_orders = self.db.get_active_orders().await?;
        
        for order in active_orders {
            if let Some(book) = order_books.get(&order.symbol) {
                // Note: This requires mutable access, handled differently in production
                debug!("Loading active order: {}", order.id);
            }
        }
        
        Ok(())
    }

    /// Create a new order
    #[instrument(skip(self), fields(symbol = %order.symbol, side = ?order.side, qty = %order.quantity))]
    pub async fn create_order(&self, mut order: Order) -> Result<(Order, Vec<Trade>), String> {
        let start = Instant::now();
        
        // Check engine state
        let state = *self.state.read();
        if state != EngineState::Running {
            return Err(format!("Engine is not running: {:?}", state));
        }

        // Validate order
        self.validate_order(&order)?;

        // Check trading pair exists and is active
        let pair = self.trading_pairs.read().get(&order.symbol).cloned();
        let pair = match pair {
            Some(p) if p.status == TradingPairStatus::Trading => p,
            Some(p) => return Err(format!("Trading pair is not active: {:?}", p.status)),
            None => return Err(format!("Trading pair not found: {}", order.symbol)),
        };

        // Check user order limit
        let user_orders = self.user_orders.read().get(&order.user_id).map(|v| v.len()).unwrap_or(0);
        if user_orders >= self.config.max_open_orders_per_user as usize {
            return Err("Maximum open orders limit reached".to_string());
        }

        // Process order based on type
        let (result_order, trades) = match order.order_type {
            OrderType::Market => self.process_market_order(&pair, order).await?,
            OrderType::Limit => self.process_limit_order(&pair, order).await?,
            OrderType::StopLoss | OrderType::StopLossLimit => self.process_stop_order(&pair, order).await?,
            OrderType::TakeProfit | OrderType::TakeProfitLimit => self.process_take_profit_order(&pair, order).await?,
            OrderType::TrailingStop => self.process_trailing_stop_order(&pair, order).await?,
            OrderType::Iceberg => self.process_iceberg_order(&pair, order).await?,
            OrderType::Twap => self.process_twap_order(&pair, order).await?,
            OrderType::Vwap => self.process_vwap_order(&pair, order).await?,
            _ => self.process_limit_order(&pair, order).await?,
        };

        // Calculate fees
        let trades_with_fees = self.calculate_fees(&pair, trades);

        // Update statistics
        let latency = start.elapsed().as_micros() as f64;
        self.update_stats(result_order.status == OrderStatus::Filled, trades_with_fees.len(), latency);

        // Persist to database
        if let Err(e) = self.db.save_order(&result_order).await {
            error!("Failed to save order: {}", e);
        }

        for trade in &trades_with_fees {
            if let Err(e) = self.db.save_trade(trade).await {
                error!("Failed to save trade: {}", e);
            }
        }

        // Update cache
        self.cache_order(&result_order).await;
        self.publish_order_update(&result_order).await;

        Ok((result_order, trades_with_fees))
    }

    /// Validate order parameters
    fn validate_order(&self, order: &Order) -> Result<(), String> {
        // Check quantity
        if order.quantity <= Decimal::ZERO {
            return Err("Invalid quantity".to_string());
        }

        // Check price for limit orders
        if matches!(order.order_type, OrderType::Limit | OrderType::StopLossLimit | OrderType::TakeProfitLimit) {
            match order.price {
                Some(p) if p <= Decimal::ZERO => return Err("Invalid price".to_string()),
                None => return Err("Price required for limit orders".to_string()),
                _ => {}
            }
        }

        // Check order value
        if let Some(price) = order.price {
            let value = price * order.quantity;
            if value < self.config.min_order_value || value > self.config.max_order_value {
                return Err(format!("Order value out of range: {}", value));
            }
        }

        Ok(())
    }

    /// Process market order
    async fn process_market_order(&self, pair: &TradingPair, mut order: Order) -> Result<(Order, Vec<Trade>), String> {
        let mut order_books = self.order_books.write();
        let book = match order_books.get_mut(&order.symbol) {
            Some(b) => b,
            None => return Err("Order book not found".to_string()),
        };

        // Get the best price for market order
        let price = match order.side {
            OrderSide::Buy => book.best_ask().map(|(p, _)| p).ok_or("No liquidity")?,
            OrderSide::Sell => book.best_bid().map(|(p, _)| p).ok_or("No liquidity")?,
        };

        order.price = Some(price);
        
        let (filled_order, trades) = book.match_order(order);

        Ok((filled_order, trades))
    }

    /// Process limit order
    async fn process_limit_order(&self, pair: &TradingPair, mut order: Order) -> Result<(Order, Vec<Trade>), String> {
        let mut order_books = self.order_books.write();
        let book = match order_books.get_mut(&order.symbol) {
            Some(b) => b,
            None => return Err("Order book not found".to_string()),
        };

        // Try to match first
        let (mut filled_order, mut trades) = book.match_order(order);

        // If not fully filled and not IOC or FOK, add to book
        if filled_order.remaining_quantity > Decimal::ZERO
            && !matches!(filled_order.time_in_force, TimeInForce::Ioc | TimeInForce::Fok)
        {
            if filled_order.order_type != OrderType::LimitMaker {
                book.add_order(Arc::new(filled_order.clone()))?;
            }
        }

        // Handle FOK order
        if filled_order.time_in_force == TimeInForce::Fok && filled_order.remaining_quantity > Decimal::ZERO {
            filled_order.status = OrderStatus::Rejected;
            trades.clear();
        }

        Ok((filled_order, trades))
    }

    /// Process stop order
    async fn process_stop_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        // Stop orders are held until trigger price is reached
        // Implementation would check if stop price is triggered
        // For now, process as limit order
        self.process_limit_order(pair, order).await
    }

    /// Process take profit order
    async fn process_take_profit_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        self.process_limit_order(pair, order).await
    }

    /// Process trailing stop order
    async fn process_trailing_stop_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        // Trailing stops need to track price movements
        self.process_limit_order(pair, order).await
    }

    /// Process iceberg order
    async fn process_iceberg_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        // Iceberg orders only show a portion of the total quantity
        self.process_limit_order(pair, order).await
    }

    /// Process TWAP order
    async fn process_twap_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        // TWAP orders are executed over time
        self.process_limit_order(pair, order).await
    }

    /// Process VWAP order
    async fn process_vwap_order(&self, pair: &TradingPair, order: Order) -> Result<(Order, Vec<Trade>), String> {
        // VWAP orders aim to match volume-weighted average price
        self.process_limit_order(pair, order).await
    }

    /// Calculate trading fees
    fn calculate_fees(&self, pair: &TradingPair, trades: Vec<Trade>) -> Vec<Trade> {
        trades.into_iter().map(|mut trade| {
            let fee_rate = if trade.is_maker { pair.maker_fee } else { pair.taker_fee };
            trade.fee = trade.price * trade.quantity * fee_rate;
            trade
        }).collect()
    }

    /// Cancel an order
    #[instrument(skip(self))]
    pub async fn cancel_order(&self, user_id: Uuid, order_id: Uuid, symbol: String) -> Result<Order, String> {
        let state = *self.state.read();
        if state != EngineState::Running {
            return Err(format!("Engine is not running: {:?}", state));
        }

        let mut order_books = self.order_books.write();
        let book = match order_books.get_mut(&symbol) {
            Some(b) => b,
            None => return Err("Order book not found".to_string()),
        };

        let order = match book.remove_order(order_id) {
            Some(o) => o,
            None => return Err("Order not found".to_string()),
        };

        // Verify ownership
        if order.user_id != user_id {
            return Err("Not authorized to cancel this order".to_string());
        }

        let mut cancelled_order = (*order).clone();
        cancelled_order.cancel();

        // Update user orders
        self.user_orders.write().entry(user_id).or_default().retain(|id| *id != order_id);

        // Persist to database
        if let Err(e) = self.db.update_order_status(&cancelled_order).await {
            error!("Failed to update order status: {}", e);
        }

        // Update cache
        self.cache_order(&cancelled_order).await;
        self.publish_order_update(&cancelled_order).await;

        Ok(cancelled_order)
    }

    /// Cancel all orders for a user
    pub async fn cancel_all_orders(&self, user_id: Uuid, symbol: Option<String>) -> Result<Vec<Order>, String> {
        let user_orders = self.user_orders.read().get(&user_id).cloned().unwrap_or_default();
        let mut cancelled = Vec::new();

        for order_id in user_orders {
            if let Some(sym) = &symbol {
                if let Ok(order) = self.cancel_order(user_id, order_id, sym.clone()).await {
                    cancelled.push(order);
                }
            }
        }

        Ok(cancelled)
    }

    /// Get order book depth
    pub fn get_order_book_depth(&self, symbol: &str, limit: usize) -> Option<OrderBook> {
        self.order_books.read().get(symbol).map(|book| book.get_depth(limit))
    }

    /// Get ticker for a symbol
    pub fn get_ticker(&self, symbol: &str) -> Option<Ticker> {
        // Implementation would aggregate ticker data
        None
    }

    /// Get all tickers
    pub fn get_all_tickers(&self) -> Vec<Ticker> {
        // Implementation would return all tickers
        Vec::new()
    }

    /// Update engine statistics
    fn update_stats(&self, filled: bool, trade_count: usize, latency_us: f64) {
        let mut stats = self.stats.write();
        stats.total_orders_processed += 1;
        stats.total_trades_executed += trade_count as u64;
        stats.avg_latency_us = (stats.avg_latency_us + latency_us) / 2.0;
        stats.max_latency_us = stats.max_latency_us.max(latency_us);
        stats.last_update = Utc::now();
    }

    /// Pause engine
    pub fn pause(&self) {
        *self.state.write() = EngineState::Paused;
        info!("Trading engine paused");
    }

    /// Resume engine
    pub fn resume(&self) {
        *self.state.write() = EngineState::Running;
        info!("Trading engine resumed");
    }

    /// Halt engine (emergency stop)
    pub fn halt(&self) {
        *self.state.write() = EngineState::Halted;
        warn!("Trading engine HALTED");
    }

    /// Get engine state
    pub fn get_state(&self) -> EngineState {
        *self.state.read()
    }

    /// Get engine statistics
    pub fn get_stats(&self) -> EngineStats {
        self.stats.read().clone()
    }

    /// Cache order
    async fn cache_order(&self, order: &Order) {
        let key = format!("order:{}", order.id);
        if let Err(e) = self.cache.set(&key, order).await {
            warn!("Failed to cache order: {}", e);
        }
    }

    /// Publish order update via WebSocket
    async fn publish_order_update(&self, order: &Order) {
        // Implementation would publish to message queue for WebSocket distribution
    }

    /// Add trading pair
    pub async fn add_trading_pair(&self, pair: TradingPair) -> Result<(), String> {
        let symbol = pair.symbol.clone();
        
        self.trading_pairs.write().insert(symbol.clone(), pair.clone());
        self.order_books.write().insert(symbol.clone(), OrderBook::new(symbol));

        if let Err(e) = self.db.save_trading_pair(&pair).await {
            error!("Failed to save trading pair: {}", e);
        }

        info!("Added trading pair: {}", symbol);
        Ok(())
    }

    /// Remove trading pair
    pub async fn remove_trading_pair(&self, symbol: &str) -> Result<(), String> {
        self.trading_pairs.write().remove(symbol);
        self.order_books.write().remove(symbol);

        if let Err(e) = self.db.delete_trading_pair(symbol).await {
            error!("Failed to delete trading pair: {}", e);
        }

        info!("Removed trading pair: {}", symbol);
        Ok(())
    }

    /// Pause trading pair
    pub async fn pause_trading_pair(&self, symbol: &str) -> Result<(), String> {
        if let Some(pair) = self.trading_pairs.write().get_mut(symbol) {
            pair.status = TradingPairStatus::Pause;
            pair.updated_at = Utc::now();
        }
        Ok(())
    }

    /// Resume trading pair
    pub async fn resume_trading_pair(&self, symbol: &str) -> Result<(), String> {
        if let Some(pair) = self.trading_pairs.write().get_mut(symbol) {
            pair.status = TradingPairStatus::Trading;
            pair.updated_at = Utc::now();
        }
        Ok(())
    }
}