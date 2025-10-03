use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use std::time::{SystemTime, UNIX_EPOCH};
use rust_decimal::Decimal;
use uuid::Uuid;

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
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum OrderType {
    Market,
    Limit,
    StopLoss,
    TakeProfit,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum OrderStatus {
    New,
    PartiallyFilled,
    Filled,
    Cancelled,
    Rejected,
}

#[derive(Debug, Clone)]
pub struct OrderBook {
    symbol: String,
    bids: Arc<RwLock<Vec<Order>>>,
    asks: Arc<RwLock<Vec<Order>>>,
}

impl OrderBook {
    pub fn new(symbol: String) -> Self {
        Self {
            symbol,
            bids: Arc::new(RwLock::new(Vec::new())),
            asks: Arc::new(RwLock::new(Vec::new())),
        }
    }

    pub async fn add_order(&self, order: Order) {
        match order.side {
            OrderSide::Buy => {
                let mut bids = self.bids.write().await;
                bids.push(order);
                bids.sort_by(|a, b| b.price.cmp(&a.price));
            }
            OrderSide::Sell => {
                let mut asks = self.asks.write().await;
                asks.push(order);
                asks.sort_by(|a, b| a.price.cmp(&b.price));
            }
        }
    }

    pub async fn get_best_bid_ask(&self) -> (Option<Decimal>, Option<Decimal>) {
        let bids = self.bids.read().await;
        let asks = self.asks.read().await;
        
        let best_bid = bids.first().map(|o| o.price);
        let best_ask = asks.first().map(|o| o.price);
        
        (best_bid, best_ask)
    }

    pub async fn match_order(&self, incoming: &mut Order) -> Vec<Trade> {
        let mut trades = Vec::new();
        
        match incoming.side {
            OrderSide::Buy => {
                let mut asks = self.asks.write().await;
                let mut i = 0;
                
                while i < asks.len() && incoming.filled_quantity < incoming.quantity {
                    let ask = &mut asks[i];
                    
                    if incoming.order_type == OrderType::Limit && ask.price > incoming.price {
                        break;
                    }
                    
                    let match_qty = (incoming.quantity - incoming.filled_quantity)
                        .min(ask.quantity - ask.filled_quantity);
                    
                    incoming.filled_quantity += match_qty;
                    ask.filled_quantity += match_qty;
                    
                    trades.push(Trade {
                        id: Uuid::new_v4().to_string(),
                        symbol: self.symbol.clone(),
                        price: ask.price,
                        quantity: match_qty,
                        buyer_order_id: incoming.id.clone(),
                        seller_order_id: ask.id.clone(),
                        timestamp: current_timestamp(),
                    });
                    
                    if ask.filled_quantity >= ask.quantity {
                        ask.status = OrderStatus::Filled;
                        asks.remove(i);
                    } else {
                        ask.status = OrderStatus::PartiallyFilled;
                        i += 1;
                    }
                }
            }
            OrderSide::Sell => {
                let mut bids = self.bids.write().await;
                let mut i = 0;
                
                while i < bids.len() && incoming.filled_quantity < incoming.quantity {
                    let bid = &mut bids[i];
                    
                    if incoming.order_type == OrderType::Limit && bid.price < incoming.price {
                        break;
                    }
                    
                    let match_qty = (incoming.quantity - incoming.filled_quantity)
                        .min(bid.quantity - bid.filled_quantity);
                    
                    incoming.filled_quantity += match_qty;
                    bid.filled_quantity += match_qty;
                    
                    trades.push(Trade {
                        id: Uuid::new_v4().to_string(),
                        symbol: self.symbol.clone(),
                        price: bid.price,
                        quantity: match_qty,
                        buyer_order_id: bid.id.clone(),
                        seller_order_id: incoming.id.clone(),
                        timestamp: current_timestamp(),
                    });
                    
                    if bid.filled_quantity >= bid.quantity {
                        bid.status = OrderStatus::Filled;
                        bids.remove(i);
                    } else {
                        bid.status = OrderStatus::PartiallyFilled;
                        i += 1;
                    }
                }
            }
        }
        
        if incoming.filled_quantity >= incoming.quantity {
            incoming.status = OrderStatus::Filled;
        } else if incoming.filled_quantity > Decimal::ZERO {
            incoming.status = OrderStatus::PartiallyFilled;
        }
        
        trades
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub id: String,
    pub symbol: String,
    pub price: Decimal,
    pub quantity: Decimal,
    pub buyer_order_id: String,
    pub seller_order_id: String,
    pub timestamp: u64,
}

pub struct TradingEngine {
    order_books: Arc<DashMap<String, OrderBook>>,
    orders: Arc<DashMap<String, Order>>,
    trades: Arc<RwLock<Vec<Trade>>>,
}

impl TradingEngine {
    pub fn new() -> Self {
        let engine = Self {
            order_books: Arc::new(DashMap::new()),
            orders: Arc::new(DashMap::new()),
            trades: Arc::new(RwLock::new(Vec::new())),
        };
        
        // Initialize common trading pairs
        engine.add_symbol("BTCUSDT".to_string());
        engine.add_symbol("ETHUSDT".to_string());
        engine.add_symbol("BNBUSDT".to_string());
        
        engine
    }

    pub fn add_symbol(&self, symbol: String) {
        self.order_books.insert(symbol.clone(), OrderBook::new(symbol));
    }

    pub async fn submit_order(&self, mut order: Order) -> Result<OrderResponse, String> {
        let order_book = self.order_books
            .get(&order.symbol)
            .ok_or("Symbol not found")?;
        
        // Match order
        let trades = order_book.match_order(&mut order).await;
        
        // Store trades
        if !trades.is_empty() {
            let mut all_trades = self.trades.write().await;
            all_trades.extend(trades.clone());
        }
        
        // If not fully filled and it's a limit order, add to book
        if order.status != OrderStatus::Filled && order.order_type == OrderType::Limit {
            order_book.add_order(order.clone()).await;
        }
        
        // Store order
        self.orders.insert(order.id.clone(), order.clone());
        
        Ok(OrderResponse {
            order_id: order.id,
            status: order.status,
            filled_quantity: order.filled_quantity,
            trades,
        })
    }

    pub async fn get_order_book(&self, symbol: &str) -> Result<OrderBookResponse, String> {
        let order_book = self.order_books
            .get(symbol)
            .ok_or("Symbol not found")?;
        
        let (best_bid, best_ask) = order_book.get_best_bid_ask().await;
        
        Ok(OrderBookResponse {
            symbol: symbol.to_string(),
            best_bid,
            best_ask,
            timestamp: current_timestamp(),
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OrderRequest {
    pub user_id: String,
    pub symbol: String,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub price: Decimal,
    pub quantity: Decimal,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OrderResponse {
    pub order_id: String,
    pub status: OrderStatus,
    pub filled_quantity: Decimal,
    pub trades: Vec<Trade>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OrderBookResponse {
    pub symbol: String,
    pub best_bid: Option<Decimal>,
    pub best_ask: Option<Decimal>,
    pub timestamp: u64,
}

fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64
}

// API Handlers
async fn submit_order_handler(
    engine: web::Data<Arc<TradingEngine>>,
    req: web::Json<OrderRequest>,
) -> impl Responder {
    let order = Order {
        id: Uuid::new_v4().to_string(),
        user_id: req.user_id.clone(),
        symbol: req.symbol.clone(),
        side: req.side.clone(),
        order_type: req.order_type.clone(),
        price: req.price,
        quantity: req.quantity,
        filled_quantity: Decimal::ZERO,
        status: OrderStatus::New,
        timestamp: current_timestamp(),
    };
    
    match engine.submit_order(order).await {
        Ok(response) => HttpResponse::Ok().json(response),
        Err(e) => HttpResponse::BadRequest().json(serde_json::json!({
            "error": e
        })),
    }
}

async fn get_order_book_handler(
    engine: web::Data<Arc<TradingEngine>>,
    symbol: web::Path<String>,
) -> impl Responder {
    match engine.get_order_book(&symbol).await {
        Ok(response) => HttpResponse::Ok().json(response),
        Err(e) => HttpResponse::NotFound().json(serde_json::json!({
            "error": e
        })),
    }
}

async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "service": "TigerEx Rust Performance Engine",
        "version": "1.0.0"
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt::init();
    
    println!(r#"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🦀 TigerEx Rust Performance Engine v1.0.0                   ║
║   Ultra-High Performance • Zero-Cost Abstractions             ║
║   Memory Safe • Concurrent • Blazing Fast                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    "#);
    
    let engine = Arc::new(TradingEngine::new());
    
    println!("🚀 Starting server on http://0.0.0.0:8083");
    
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(engine.clone()))
            .route("/health", web::get().to(health_check))
            .route("/api/v1/order", web::post().to(submit_order_handler))
            .route("/api/v1/orderbook/{symbol}", web::get().to(get_order_book_handler))
    })
    .bind(("0.0.0.0", 8083))?
    .run()
    .await
}