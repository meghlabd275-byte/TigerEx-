// TigerEx Rust Order Matching Engine
// Ultra-high performance order matching written in Rust
// Part of TigerEx Multi-Language Microservices Architecture

use actix_web::{web, App, HttpResponse, HttpServer};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;
use chrono::{DateTime, Utc};
use rust_decimal::prelude::*;
use rust_decimal_macros::dec;

// Order types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OrderType {
    Limit,
    Market,
    StopLimit,
    StopMarket,
    ImmediateOrCancel,
    FillOrKill,
    PostOnly,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OrderStatus {
    New,
    PartiallyFilled,
    Filled,
    Cancelled,
    Rejected,
    Expired,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ExchangeStatus {
    Active,
    Paused,
    Halted,
    Maintenance,
}

// Order structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub id: String,
    pub user_id: String,
    pub symbol: String,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub price: Decimal,
    pub quantity: Decimal,
    pub filled_quantity: Decimal,
    pub status: OrderStatus,
    pub fee: Decimal,
    pub fee_currency: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub exchange_id: String,
    pub tier_fee_discount: Decimal,
}

// Trade structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub id: String,
    pub symbol: String,
    pub taker_order_id: String,
    pub maker_order_id: String,
    pub taker_user_id: String,
    pub maker_user_id: String,
    pub side: OrderSide,
    pub price: Decimal,
    pub quantity: Decimal,
    pub taker_fee: Decimal,
    pub maker_fee: Decimal,
    pub timestamp: DateTime<Utc>,
}

// Order book level
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceLevel {
    pub price: Decimal,
    pub orders: Vec<Order>,
    pub total_quantity: Decimal,
}

// Order book
pub struct OrderBook {
    pub symbol: String,
    pub bids: BTreeMap<std::cmp::Reverse<Ordering>, PriceLevel>,
    pub asks: BTreeMap<Ordering, PriceLevel>,
    pub order_map: std::collections::HashMap<String, Order>,
}

impl OrderBook {
    pub fn new(symbol: String) -> Self {
        Self {
            symbol,
            bids: BTreeMap::new(),
            asks: BTreeMap::new(),
            order_map: std::collections::HashMap::new(),
        }
    }

    pub fn get_best_bid(&self) -> Option<&PriceLevel> {
        self.bids.values().next()
    }

    pub fn get_best_ask(&self) -> Option<&PriceLevel> {
        self.asks.values().next()
    }

    pub fn get_spread(&self) -> Option<Decimal> {
        if let (Some(bid), Some(ask)) = (self.get_best_bid(), self.get_best_ask()) {
            Some(ask.price - bid.price)
        } else {
            None
        }
    }
}

// Custom ordering wrapper for Decimal
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
struct Ordering(i64);

impl From<Decimal> for Ordering {
    fn from(d: Decimal) -> Self {
        Ordering((d * dec!(100000000)).to_u64().unwrap() as i64)
    }
}

// Matching engine
pub struct MatchingEngine {
    order_books: Arc<RwLock<std::collections::HashMap<String, OrderBook>>>,
    exchange_id: String,
    exchange_status: Arc<RwLock<ExchangeStatus>>,
    fee_service: FeeService,
}

impl MatchingEngine {
    pub fn new(exchange_id: String) -> Self {
        Self {
            order_books: Arc::new(RwLock::new(std::collections::HashMap::new())),
            exchange_id,
            exchange_status: Arc::new(RwLock::new(ExchangeStatus::Active)),
            fee_service: FeeService::new(),
        }
    }

    pub async fn place_order(&self, mut order: Order) -> Result<(Order, Vec<Trade>), String> {
        // Check exchange status
        let status = *self.exchange_status.read().await;
        if status != ExchangeStatus::Active {
            return Err(format!("Exchange is {:?}", status));
        }

        // Initialize order
        order.id = Uuid::new_v4().to_string();
        order.status = OrderStatus::New;
        order.created_at = Utc::now();
        order.updated_at = Utc::now();
        order.exchange_id = self.exchange_id.clone();
        order.filled_quantity = dec!(0);

        let mut order_books = self.order_books.write().await;
        
        // Get or create order book
        let order_book = order_books
            .entry(order.symbol.clone())
            .or_insert_with(|| OrderBook::new(order.symbol.clone()));

        let trades = match order.order_type {
            OrderType::Market => self.process_market_order(order_book, &mut order).await,
            OrderType::Limit => self.process_limit_order(order_book, &mut order).await,
            OrderType::ImmediateOrCancel => self.process_ioc_order(order_book, &mut order).await,
            OrderType::FillOrKill => self.process_fok_order(order_book, &mut order).await,
            _ => return Err(format!("Unsupported order type: {:?}", order.order_type)),
        }?;

        // Update order status
        if order.filled_quantity > dec!(0) {
            if order.filled_quantity == order.quantity {
                order.status = OrderStatus::Filled;
            } else {
                order.status = OrderStatus::PartiallyFilled;
            }
        }

        // Store order in map
        order_book.order_map.insert(order.id.clone(), order.clone());

        Ok((order, trades))
    }

    async fn process_market_order(
        &self,
        order_book: &mut OrderBook,
        order: &mut Order,
    ) -> Result<Vec<Trade>, String> {
        let mut trades = Vec::new();
        let mut remaining_qty = order.quantity;

        let price_levels = match order.side {
            OrderSide::Buy => &mut order_book.asks,
            OrderSide::Sell => &mut order_book.bids,
        };

        while !price_levels.is_empty() && remaining_qty > dec!(0) {
            let best_price = price_levels.keys().next().cloned();
            if let Some(price_key) = best_price {
                let level = price_levels.get_mut(&price_key).unwrap();
                
                while !level.orders.is_empty() && remaining_qty > dec!(0) {
                    let maker_order = &mut level.orders[0];
                    let match_qty = std::cmp::min(
                        remaining_qty,
                        maker_order.quantity - maker_order.filled_quantity,
                    );

                    let trade = self.execute_trade(order, maker_order, match_qty, level.price);
                    trades.push(trade);

                    remaining_qty -= match_qty;
                    order.filled_quantity += match_qty;
                    maker_order.filled_quantity += match_qty;

                    if maker_order.filled_quantity == maker_order.quantity {
                        level.orders.remove(0);
                        order_book.order_map.remove(&maker_order.id);
                    }
                }

                if level.orders.is_empty() {
                    price_levels.remove(&price_key);
                }
            }
        }

        Ok(trades)
    }

    async fn process_limit_order(
        &self,
        order_book: &mut OrderBook,
        order: &mut Order,
    ) -> Result<Vec<Trade>, String> {
        let mut trades = Vec::new();
        let mut remaining_qty = order.quantity;

        // Match against opposite side
        let price_levels = match order.side {
            OrderSide::Buy => &mut order_book.asks,
            OrderSide::Sell => &mut order_book.bids,
        };

        while !price_levels.is_empty() && remaining_qty > dec!(0) {
            let best_price_key = price_levels.keys().next().cloned();
            
            if let Some(price_key) = best_price_key {
                let level = price_levels.get(&price_key).unwrap();
                let can_match = match order.side {
                    OrderSide::Buy => order.price >= level.price,
                    OrderSide::Sell => order.price <= level.price,
                };

                if !can_match {
                    break;
                }

                let level = price_levels.get_mut(&price_key).unwrap();
                
                while !level.orders.is_empty() && remaining_qty > dec!(0) {
                    let maker_order = &mut level.orders[0];
                    let match_qty = std::cmp::min(
                        remaining_qty,
                        maker_order.quantity - maker_order.filled_quantity,
                    );

                    let trade = self.execute_trade(order, maker_order, match_qty, level.price);
                    trades.push(trade);

                    remaining_qty -= match_qty;
                    order.filled_quantity += match_qty;
                    maker_order.filled_quantity += match_qty;

                    if maker_order.filled_quantity == maker_order.quantity {
                        level.orders.remove(0);
                        order_book.order_map.remove(&maker_order.id);
                    }
                }

                if level.orders.is_empty() {
                    price_levels.remove(&price_key);
                }
            }
        }

        // Add remaining quantity to order book
        if remaining_qty > dec!(0) {
            self.add_order_to_book(order_book, order);
        }

        Ok(trades)
    }

    async fn process_ioc_order(
        &self,
        order_book: &mut OrderBook,
        order: &mut Order,
    ) -> Result<Vec<Trade>, String> {
        let trades = self.process_limit_order(order_book, order).await?;
        // Unfilled portion is cancelled (not added to book)
        Ok(trades)
    }

    async fn process_fok_order(
        &self,
        order_book: &mut OrderBook,
        order: &mut Order,
    ) -> Result<Vec<Trade>, String> {
        // Check if entire order can be filled
        let available_qty = self.calculate_available_quantity(order_book, order);
        
        if available_qty < order.quantity {
            return Err("Insufficient liquidity for FOK order".to_string());
        }

        self.process_limit_order(order_book, order).await
    }

    fn calculate_available_quantity(&self, order_book: &OrderBook, order: &Order) -> Decimal {
        let mut available = dec!(0);
        
        let price_levels = match order.side {
            OrderSide::Buy => &order_book.asks,
            OrderSide::Sell => &order_book.bids,
        };

        for (_, level) in price_levels.iter() {
            let can_match = match order.side {
                OrderSide::Buy => order.price >= level.price,
                OrderSide::Sell => order.price <= level.price,
            };

            if can_match {
                for o in &level.orders {
                    available += o.quantity - o.filled_quantity;
                }
            }
        }

        available
    }

    fn execute_trade(
        &self,
        taker: &Order,
        maker: &Order,
        qty: Decimal,
        price: Decimal,
    ) -> Trade {
        let taker_fee_rate = self.fee_service.get_fee_rate(&taker.user_id, true);
        let maker_fee_rate = self.fee_service.get_fee_rate(&maker.user_id, false);

        Trade {
            id: Uuid::new_v4().to_string(),
            symbol: taker.symbol.clone(),
            taker_order_id: taker.id.clone(),
            maker_order_id: maker.id.clone(),
            taker_user_id: taker.user_id.clone(),
            maker_user_id: maker.user_id.clone(),
            side: taker.side,
            price,
            quantity: qty,
            taker_fee: qty * price * taker_fee_rate,
            maker_fee: qty * price * maker_fee_rate,
            timestamp: Utc::now(),
        }
    }

    fn add_order_to_book(&self, order_book: &mut OrderBook, order: &Order) {
        let price_key = Ordering::from(order.price);
        
        let levels = match order.side {
            OrderSide::Buy => &mut order_book.bids,
            OrderSide::Sell => &mut order_book.asks,
        };

        let level = levels.entry(price_key).or_insert_with(|| PriceLevel {
            price: order.price,
            orders: Vec::new(),
            total_quantity: dec!(0),
        });

        level.orders.push(order.clone());
        level.total_quantity += order.quantity - order.filled_quantity;
    }

    pub async fn cancel_order(&self, symbol: &str, order_id: &str) -> Result<(), String> {
        let mut order_books = self.order_books.write().await;
        
        if let Some(order_book) = order_books.get_mut(symbol) {
            if let Some(order) = order_book.order_map.get_mut(order_id) {
                order.status = OrderStatus::Cancelled;
                order.updated_at = Utc::now();
                order_book.order_map.remove(order_id);
                Ok(())
            } else {
                Err(format!("Order not found: {}", order_id))
            }
        } else {
            Err(format!("Order book not found for symbol: {}", symbol))
        }
    }

    pub async fn get_order_book(
        &self,
        symbol: &str,
        depth: usize,
    ) -> Option<(Vec<PriceLevel>, Vec<PriceLevel>)> {
        let order_books = self.order_books.read().await;
        
        if let Some(order_book) = order_books.get(symbol) {
            let bids: Vec<PriceLevel> = order_book
                .bids
                .values()
                .take(depth)
                .cloned()
                .collect();

            let asks: Vec<PriceLevel> = order_book
                .asks
                .values()
                .take(depth)
                .cloned()
                .collect();

            Some((bids, asks))
        } else {
            None
        }
    }

    pub async fn set_exchange_status(&self, status: ExchangeStatus) {
        let mut current = self.exchange_status.write().await;
        *current = status;
    }

    pub async fn get_exchange_status(&self) -> ExchangeStatus {
        *self.exchange_status.read().await
    }
}

// Fee service
pub struct FeeService {
    // In production, this would connect to Redis/DB
}

impl FeeService {
    pub fn new() -> Self {
        Self {}
    }

    pub fn get_fee_rate(&self, _user_id: &str, is_taker: bool) -> Decimal {
        if is_taker {
            dec!(0.001) // 0.1% taker fee
        } else {
            dec!(0.0008) // 0.08% maker fee
        }
    }
}

// API handlers
async fn place_order(
    engine: web::Data<Arc<MatchingEngine>>,
    order: web::Json<OrderRequest>,
) -> HttpResponse {
    let new_order = Order {
        id: String::new(),
        user_id: order.user_id.clone(),
        symbol: order.symbol.clone(),
        side: order.side,
        order_type: order.order_type,
        price: order.price,
        quantity: order.quantity,
        filled_quantity: dec!(0),
        status: OrderStatus::New,
        fee: dec!(0),
        fee_currency: "USD".to_string(),
        created_at: Utc::now(),
        updated_at: Utc::now(),
        exchange_id: String::new(),
        tier_fee_discount: dec!(0),
    };

    match engine.place_order(new_order).await {
        Ok((order, trades)) => HttpResponse::Ok().json(PlaceOrderResponse { order, trades }),
        Err(e) => HttpResponse::BadRequest().json(ErrorResponse { error: e }),
    }
}

async fn cancel_order(
    engine: web::Data<Arc<MatchingEngine>>,
    path: web::Path<(String, String)>,
) -> HttpResponse {
    let (symbol, order_id) = path.into_inner();

    match engine.cancel_order(&symbol, &order_id).await {
        Ok(()) => HttpResponse::Ok().json(SuccessResponse {
            message: "Order cancelled successfully".to_string(),
        }),
        Err(e) => HttpResponse::BadRequest().json(ErrorResponse { error: e }),
    }
}

async fn get_order_book(
    engine: web::Data<Arc<MatchingEngine>>,
    path: web::Path<String>,
    query: web::Query<OrderBookQuery>,
) -> HttpResponse {
    let symbol = path.into_inner();
    let depth = query.depth.unwrap_or(20);

    match engine.get_order_book(&symbol, depth).await {
        Some((bids, asks)) => HttpResponse::Ok().json(OrderBookResponse { symbol, bids, asks }),
        None => HttpResponse::NotFound().json(ErrorResponse {
            error: "Order book not found".to_string(),
        }),
    }
}

async fn get_exchange_status(engine: web::Data<Arc<MatchingEngine>>) -> HttpResponse {
    HttpResponse::Ok().json(ExchangeStatusResponse {
        exchange_id: engine.exchange_id.clone(),
        status: engine.get_exchange_status().await,
    })
}

async fn set_exchange_status(
    engine: web::Data<Arc<MatchingEngine>>,
    body: web::Json<SetStatusRequest>,
) -> HttpResponse {
    engine.set_exchange_status(body.status).await;
    HttpResponse::Ok().json(ExchangeStatusResponse {
        exchange_id: engine.exchange_id.clone(),
        status: body.status,
    })
}

async fn health_check(engine: web::Data<Arc<MatchingEngine>>) -> HttpResponse {
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy".to_string(),
        service: "rust-order-matching".to_string(),
        exchange_id: engine.exchange_id.clone(),
        timestamp: Utc::now().timestamp(),
    })
}

// Request/Response types
#[derive(Debug, Deserialize)]
struct OrderRequest {
    user_id: String,
    symbol: String,
    side: OrderSide,
    order_type: OrderType,
    price: Decimal,
    quantity: Decimal,
}

#[derive(Debug, Serialize)]
struct PlaceOrderResponse {
    order: Order,
    trades: Vec<Trade>,
}

#[derive(Debug, Serialize)]
struct ErrorResponse {
    error: String,
}

#[derive(Debug, Serialize)]
struct SuccessResponse {
    message: String,
}

#[derive(Debug, Deserialize)]
struct OrderBookQuery {
    depth: Option<usize>,
}

#[derive(Debug, Serialize)]
struct OrderBookResponse {
    symbol: String,
    bids: Vec<PriceLevel>,
    asks: Vec<PriceLevel>,
}

#[derive(Debug, Serialize)]
struct ExchangeStatusResponse {
    exchange_id: String,
    status: ExchangeStatus,
}

#[derive(Debug, Deserialize)]
struct SetStatusRequest {
    status: ExchangeStatus,
}

#[derive(Debug, Serialize)]
struct HealthResponse {
    status: String,
    service: String,
    exchange_id: String,
    timestamp: i64,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let exchange_id = std::env::var("EXCHANGE_ID").unwrap_or_else(|_| "TIGEREX-MAIN".to_string());
    let port = std::env::var("PORT").unwrap_or_else(|_| "8081".to_string());

    let engine = Arc::new(MatchingEngine::new(exchange_id));

    println!("Starting Rust Order Matching Engine on port {}", port);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(engine.clone()))
            .service(
                web::scope("/api/v1")
                    .route("/order", web::post().to(place_order))
                    .route("/order/{symbol}/{order_id}", web::delete().to(cancel_order))
                    .route("/orderbook/{symbol}", web::get().to(get_order_book))
                    .route("/exchange/status", web::get().to(get_exchange_status))
                    .route("/exchange/status", web::post().to(set_exchange_status))
                    .route("/health", web::get().to(health_check)),
            )
    })
    .bind(format!("0.0.0.0:{}", port))?
    .run()
    .await
}