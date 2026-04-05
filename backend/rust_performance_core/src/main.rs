//! TigerEx High-Performance Trading Core
//! Ultra-fast matching engine and order book implementation in Rust
//! Designed for sub-millisecond latency and millions of orders per second

use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::{Instant, SystemTime, UNIX_EPOCH};
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use dashmap::DashMap;
use crossbeam_queue::ArrayQueue;

// ============================================================================
// CORE TYPES AND STRUCTURES
// ============================================================================

/// Order side - Buy or Sell
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum OrderSide {
    Buy,
    Sell,
}

/// Order type
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum OrderType {
    Market,
    Limit,
    StopLoss,
    StopLossLimit,
    TakeProfit,
    TakeProfitLimit,
    TrailingStop,
    Iceberg,
    FillOrKill,
    ImmediateOrCancel,
    GoodTillDate,
}

/// Order status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum OrderStatus {
    New,
    PartiallyFilled,
    Filled,
    Cancelled,
    Rejected,
    Expired,
    PendingCancel,
    PendingReplace,
}

/// Time in force
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TimeInForce {
    GoodTillCancel,
    ImmediateOrCancel,
    FillOrKill,
    GoodTillDate,
}

/// Order structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub order_id: String,
    pub client_order_id: Option<String>,
    pub user_id: String,
    pub symbol: String,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub time_in_force: TimeInForce,
    pub price: u64, // Fixed-point representation (e.g., satoshis)
    pub quantity: u64,
    pub filled_quantity: u64,
    pub remaining_quantity: u64,
    pub stop_price: Option<u64>,
    pub iceberg_quantity: Option<u64>,
    pub status: OrderStatus,
    pub created_at: u64,
    pub updated_at: u64,
    pub expires_at: Option<u64>,
    pub fee: u64,
    pub fee_asset: String,
    pub is_reduce_only: bool,
    pub is_post_only: bool,
    pub is_hidden: bool,
}

impl Order {
    pub fn new(
        user_id: String,
        symbol: String,
        side: OrderSide,
        order_type: OrderType,
        price: u64,
        quantity: u64,
    ) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        
        Order {
            order_id: Uuid::new_v4().to_string(),
            client_order_id: None,
            user_id,
            symbol,
            side,
            order_type,
            time_in_force: TimeInForce::GoodTillCancel,
            price,
            quantity,
            filled_quantity: 0,
            remaining_quantity: quantity,
            stop_price: None,
            iceberg_quantity: None,
            status: OrderStatus::New,
            created_at: now,
            updated_at: now,
            expires_at: None,
            fee: 0,
            fee_asset: String::new(),
            is_reduce_only: false,
            is_post_only: false,
            is_hidden: false,
        }
    }
}

/// Trade structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub trade_id: String,
    pub symbol: String,
    pub price: u64,
    pub quantity: u64,
    pub buyer_order_id: String,
    pub seller_order_id: String,
    pub buyer_user_id: String,
    pub seller_user_id: String,
    pub timestamp: u64,
    pub buyer_fee: u64,
    pub seller_fee: u64,
    pub is_buyer_maker: bool,
}

/// Price level in the order book
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceLevel {
    pub price: u64,
    pub total_quantity: u64,
    pub order_count: usize,
    pub orders: Vec<Order>,
}

/// Order book structure
#[derive(Debug, Clone)]
pub struct OrderBook {
    pub symbol: String,
    pub bids: BTreeMap<u64, PriceLevel>, // Sorted descending
    pub asks: BTreeMap<u64, PriceLevel>, // Sorted ascending
    pub order_index: DashMap<String, Order>,
    pub user_orders: DashMap<String, Vec<String>>,
    pub last_update_id: u64,
    pub last_trade_price: u64,
    pub last_trade_quantity: u64,
}

impl OrderBook {
    pub fn new(symbol: String) -> Self {
        OrderBook {
            symbol,
            bids: BTreeMap::new(),
            asks: BTreeMap::new(),
            order_index: DashMap::new(),
            user_orders: DashMap::new(),
            last_update_id: 0,
            last_trade_price: 0,
            last_trade_quantity: 0,
        }
    }

    /// Add an order to the book
    pub fn add_order(&mut self, mut order: Order) -> Result<Vec<Trade>, String> {
        let mut trades = Vec::new();
        
        // Match against opposite side
        match order.side {
            OrderSide::Buy => {
                // Match against asks
                while order.remaining_quantity > 0 && !self.asks.is_empty() {
                    let best_ask_price = *self.asks.keys().next().unwrap();
                    
                    if order.order_type == OrderType::Limit && best_ask_price > order.price {
                        break;
                    }
                    
                    let level = self.asks.get_mut(&best_ask_price).unwrap();
                    
                    while order.remaining_quantity > 0 && !level.orders.is_empty() {
                        let mut maker_order = level.orders.remove(0);
                        let match_quantity = order.remaining_quantity.min(maker_order.remaining_quantity);
                        
                        // Create trade
                        let trade = Trade {
                            trade_id: Uuid::new_v4().to_string(),
                            symbol: self.symbol.clone(),
                            price: best_ask_price,
                            quantity: match_quantity,
                            buyer_order_id: order.order_id.clone(),
                            seller_order_id: maker_order.order_id.clone(),
                            buyer_user_id: order.user_id.clone(),
                            seller_user_id: maker_order.user_id.clone(),
                            timestamp: SystemTime::now()
                                .duration_since(UNIX_EPOCH)
                                .unwrap()
                                .as_millis() as u64,
                            buyer_fee: match_quantity / 1000, // 0.1% fee
                            seller_fee: match_quantity / 1000,
                            is_buyer_maker: false,
                        };
                        
                        trades.push(trade);
                        
                        // Update quantities
                        order.filled_quantity += match_quantity;
                        order.remaining_quantity -= match_quantity;
                        maker_order.filled_quantity += match_quantity;
                        maker_order.remaining_quantity -= match_quantity;
                        
                        // Update maker order
                        if maker_order.remaining_quantity == 0 {
                            maker_order.status = OrderStatus::Filled;
                            self.order_index.remove(&maker_order.order_id);
                        } else {
                            maker_order.status = OrderStatus::PartiallyFilled;
                            level.orders.push(maker_order.clone());
                        }
                        
                        level.total_quantity -= match_quantity;
                        level.order_count = level.orders.len();
                    }
                    
                    if level.orders.is_empty() {
                        self.asks.remove(&best_ask_price);
                    }
                }
                
                // Add remaining quantity to book if limit order
                if order.remaining_quantity > 0 && order.order_type == OrderType::Limit {
                    let price = order.price;
                    let level = self.bids.entry(price).or_insert(PriceLevel {
                        price,
                        total_quantity: 0,
                        order_count: 0,
                        orders: Vec::new(),
                    });
                    
                    level.total_quantity += order.remaining_quantity;
                    level.orders.push(order.clone());
                    level.order_count = level.orders.len();
                    
                    if order.filled_quantity > 0 {
                        order.status = OrderStatus::PartiallyFilled;
                    }
                }
            }
            OrderSide::Sell => {
                // Match against bids
                while order.remaining_quantity > 0 && !self.bids.is_empty() {
                    let best_bid_price = *self.bids.keys().next_back().unwrap();
                    
                    if order.order_type == OrderType::Limit && best_bid_price < order.price {
                        break;
                    }
                    
                    let level = self.bids.get_mut(&best_bid_price).unwrap();
                    
                    while order.remaining_quantity > 0 && !level.orders.is_empty() {
                        let mut maker_order = level.orders.remove(0);
                        let match_quantity = order.remaining_quantity.min(maker_order.remaining_quantity);
                        
                        // Create trade
                        let trade = Trade {
                            trade_id: Uuid::new_v4().to_string(),
                            symbol: self.symbol.clone(),
                            price: best_bid_price,
                            quantity: match_quantity,
                            buyer_order_id: maker_order.order_id.clone(),
                            seller_order_id: order.order_id.clone(),
                            buyer_user_id: maker_order.user_id.clone(),
                            seller_user_id: order.user_id.clone(),
                            timestamp: SystemTime::now()
                                .duration_since(UNIX_EPOCH)
                                .unwrap()
                                .as_millis() as u64,
                            buyer_fee: match_quantity / 1000,
                            seller_fee: match_quantity / 1000,
                            is_buyer_maker: true,
                        };
                        
                        trades.push(trade);
                        
                        // Update quantities
                        order.filled_quantity += match_quantity;
                        order.remaining_quantity -= match_quantity;
                        maker_order.filled_quantity += match_quantity;
                        maker_order.remaining_quantity -= match_quantity;
                        
                        // Update maker order
                        if maker_order.remaining_quantity == 0 {
                            maker_order.status = OrderStatus::Filled;
                            self.order_index.remove(&maker_order.order_id);
                        } else {
                            maker_order.status = OrderStatus::PartiallyFilled;
                            level.orders.push(maker_order.clone());
                        }
                        
                        level.total_quantity -= match_quantity;
                        level.order_count = level.orders.len();
                    }
                    
                    if level.orders.is_empty() {
                        self.bids.remove(&best_bid_price);
                    }
                }
                
                // Add remaining quantity to book if limit order
                if order.remaining_quantity > 0 && order.order_type == OrderType::Limit {
                    let price = order.price;
                    let level = self.asks.entry(price).or_insert(PriceLevel {
                        price,
                        total_quantity: 0,
                        order_count: 0,
                        orders: Vec::new(),
                    });
                    
                    level.total_quantity += order.remaining_quantity;
                    level.orders.push(order.clone());
                    level.order_count = level.orders.len();
                    
                    if order.filled_quantity > 0 {
                        order.status = OrderStatus::PartiallyFilled;
                    }
                }
            }
        }
        
        // Update order status
        if order.remaining_quantity == 0 {
            order.status = OrderStatus::Filled;
        }
        
        // Store order
        self.order_index.insert(order.order_id.clone(), order.clone());
        
        // Track user orders
        self.user_orders
            .entry(order.user_id.clone())
            .or_insert_with(Vec::new)
            .push(order.order_id.clone());
        
        self.last_update_id += 1;
        
        Ok(trades)
    }

    /// Cancel an order
    pub fn cancel_order(&mut self, order_id: &str) -> Result<Order, String> {
        let order = self.order_index.remove(order_id).ok_or("Order not found")?;
        
        let book = match order.side {
            OrderSide::Buy => &mut self.bids,
            OrderSide::Sell => &mut self.asks,
        };
        
        if let Some(level) = book.get_mut(&order.price) {
            level.orders.retain(|o| o.order_id != order_id);
            level.total_quantity -= order.remaining_quantity;
            level.order_count = level.orders.len();
            
            if level.orders.is_empty() {
                book.remove(&order.price);
            }
        }
        
        self.last_update_id += 1;
        
        Ok(order)
    }

    /// Get best bid price
    pub fn best_bid(&self) -> Option<u64> {
        self.bids.keys().next_back().copied()
    }

    /// Get best ask price
    pub fn best_ask(&self) -> Option<u64> {
        self.asks.keys().next().copied()
    }

    /// Get spread
    pub fn spread(&self) -> Option<u64> {
        match (self.best_ask(), self.best_bid()) {
            (Some(ask), Some(bid)) => Some(ask - bid),
            _ => None,
        }
    }

    /// Get order book snapshot
    pub fn snapshot(&self, depth: usize) -> OrderBookSnapshot {
        let bids: Vec<PriceLevelSnapshot> = self.bids
            .iter()
            .rev()
            .take(depth)
            .map(|(price, level)| PriceLevelSnapshot {
                price: *price,
                quantity: level.total_quantity,
            })
            .collect();
        
        let asks: Vec<PriceLevelSnapshot> = self.asks
            .iter()
            .take(depth)
            .map(|(price, level)| PriceLevelSnapshot {
                price: *price,
                quantity: level.total_quantity,
            })
            .collect();
        
        OrderBookSnapshot {
            symbol: self.symbol.clone(),
            bids,
            asks,
            last_update_id: self.last_update_id,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_millis() as u64,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceLevelSnapshot {
    pub price: u64,
    pub quantity: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderBookSnapshot {
    pub symbol: String,
    pub bids: Vec<PriceLevelSnapshot>,
    pub asks: Vec<PriceLevelSnapshot>,
    pub last_update_id: u64,
    pub timestamp: u64,
}

// ============================================================================
// MATCHING ENGINE
// ============================================================================

/// High-performance matching engine
pub struct MatchingEngine {
    order_books: DashMap<String, Arc<RwLock<OrderBook>>>,
    trade_queue: Arc<ArrayQueue<Trade>>,
    latency_stats: DashMap<String, Vec<u64>>,
}

impl MatchingEngine {
    pub fn new() -> Self {
        MatchingEngine {
            order_books: DashMap::new(),
            trade_queue: Arc::new(ArrayQueue::new(1_000_000)),
            latency_stats: DashMap::new(),
        }
    }

    /// Create or get order book for a symbol
    pub fn get_or_create_order_book(&self, symbol: &str) -> Arc<RwLock<OrderBook>> {
        self.order_books
            .entry(symbol.to_string())
            .or_insert_with(|| Arc::new(RwLock::new(OrderBook::new(symbol.to_string()))))
            .clone()
    }

    /// Process an order
    pub async fn process_order(&self, order: Order) -> Result<(Order, Vec<Trade>), String> {
        let start = Instant::now();
        
        let order_book = self.get_or_create_order_book(&order.symbol);
        let mut book = order_book.write().await;
        
        let trades = book.add_order(order.clone())?;
        
        // Record latency
        let latency = start.elapsed().as_micros() as u64;
        self.latency_stats
            .entry(order.symbol.clone())
            .or_insert_with(Vec::new)
            .push(latency);
        
        // Push trades to queue
        for trade in &trades {
            let _ = self.trade_queue.push(trade.clone());
        }
        
        Ok((order, trades))
    }

    /// Cancel an order
    pub async fn cancel_order(&self, symbol: &str, order_id: &str) -> Result<Order, String> {
        let order_book = self.get_or_create_order_book(symbol);
        let mut book = order_book.write().await;
        book.cancel_order(order_id)
    }

    /// Get order book snapshot
    pub async fn get_order_book_snapshot(&self, symbol: &str, depth: usize) -> Option<OrderBookSnapshot> {
        let order_book = self.order_books.get(symbol)?;
        let book = order_book.read().await;
        Some(book.snapshot(depth))
    }

    /// Get latency statistics
    pub fn get_latency_stats(&self, symbol: &str) -> Option<Vec<u64>> {
        self.latency_stats.get(symbol).map(|v| v.clone())
    }
}

impl Default for MatchingEngine {
    fn default() -> Self {
        Self::new()
    }
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

#[tokio::main]
async fn main() {
    println!("🚀 TigerEx High-Performance Trading Core");
    println!("========================================");
    println!("Starting matching engine...");
    
    let engine = Arc::new(MatchingEngine::new());
    
    // Create test orders
    let symbol = "BTCUSDT".to_string();
    
    // Add some buy orders
    for i in 1..=100 {
        let order = Order::new(
            format!("user_{}", i),
            symbol.clone(),
            OrderSide::Buy,
            OrderType::Limit,
            5000000000000 - (i * 1000000), // Decreasing prices
            100000000, // 1 BTC
        );
        
        let result = engine.process_order(order).await;
        if let Ok((order, trades)) = result {
            if !trades.is_empty() {
                println!("✅ Order {} matched {} trades", order.order_id, trades.len());
            }
        }
    }
    
    // Add some sell orders
    for i in 1..=100 {
        let order = Order::new(
            format!("user_{}", i + 100),
            symbol.clone(),
            OrderSide::Sell,
            OrderType::Limit,
            5000100000000 + (i * 1000000), // Increasing prices
            100000000, // 1 BTC
        );
        
        let result = engine.process_order(order).await;
        if let Ok((order, trades)) = result {
            if !trades.is_empty() {
                println!("✅ Order {} matched {} trades", order.order_id, trades.len());
            }
        }
    }
    
    // Print order book
    if let Some(snapshot) = engine.get_order_book_snapshot(&symbol, 5).await {
        println!("\n📊 Order Book Snapshot for {}", symbol);
        println!("=====================================");
        
        println!("\n🔴 ASKS (Sell Orders):");
        for level in snapshot.asks.iter().rev() {
            println!("  Price: {:.2} | Quantity: {:.4}", 
                level.price as f64 / 100000000.0,
                level.quantity as f64 / 100000000.0
            );
        }
        
        println!("\n🟢 BIDS (Buy Orders):");
        for level in &snapshot.bids {
            println!("  Price: {:.2} | Quantity: {:.4}", 
                level.price as f64 / 100000000.0,
                level.quantity as f64 / 100000000.0
            );
        }
        
        if let Some(book) = engine.order_books.get(&symbol) {
            let book = book.read().await;
            if let Some(spread) = book.spread() {
                println!("\n📈 Spread: {:.2}", spread as f64 / 100000000.0);
            }
        }
    }
    
    // Print latency stats
    if let Some(stats) = engine.get_latency_stats(&symbol) {
        let avg = stats.iter().sum::<u64>() as f64 / stats.len() as f64;
        let min = stats.iter().min().unwrap();
        let max = stats.iter().max().unwrap();
        
        println!("\n⏱️  Latency Statistics:");
        println!("  Average: {:.2} µs", avg);
        println!("  Min: {} µs", min);
        println!("  Max: {} µs", max);
    }
    
    println!("\n✅ TigerEx Trading Core is running!");
}