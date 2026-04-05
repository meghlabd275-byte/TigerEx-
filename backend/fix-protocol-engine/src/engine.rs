//! Trading Engine Connector for FIX Protocol

use std::sync::Arc;
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use sqlx::PgPool;

/// Market Data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketData {
    pub symbol: String,
    pub best_bid: f64,
    pub best_ask: f64,
    pub bid_size: f64,
    pub ask_size: f64,
    pub last_price: f64,
    pub last_size: f64,
    pub volume_24h: f64,
    pub high_24h: f64,
    pub low_24h: f64,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Quote Data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quote {
    pub symbol: String,
    pub bid_price: f64,
    pub ask_price: f64,
    pub bid_size: f64,
    pub ask_size: f64,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Order Status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderStatus {
    pub order_id: String,
    pub symbol: String,
    pub side: String,
    pub quantity: f64,
    pub price: Option<f64>,
    pub filled_qty: f64,
    pub leaves_qty: f64,
    pub cum_qty: f64,
    pub avg_price: f64,
    pub status: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// Trading Session Status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TradingSessionStatus {
    pub session_id: String,
    pub status: String,
    pub start_time: chrono::DateTime<chrono::Utc>,
    pub end_time: chrono::DateTime<chrono::Utc>,
    pub is_trading: bool,
}

/// Trading Engine Connector
pub struct TradingEngineConnector {
    db_pool: PgPool,
    redis_client: Arc<redis::aio::ConnectionManager>,
    cache: Arc<RwLock<std::collections::HashMap<String, MarketData>>>,
}

impl TradingEngineConnector {
    pub async fn new(database_url: &str, redis_url: &str) -> Result<Self, sqlx::Error> {
        let db_pool = PgPool::connect(database_url).await?;
        
        let redis_client = redis::Client::open(redis_url)
            .expect("Failed to create Redis client");
        let redis_manager = redis::aio::ConnectionManager::new(redis_client)
            .await
            .expect("Failed to create Redis connection manager");
        
        Ok(Self {
            db_pool,
            redis_client: Arc::new(redis_manager),
            cache: Arc::new(RwLock::new(std::collections::HashMap::new())),
        })
    }
    
    /// Submit order to trading engine
    pub async fn submit_order(
        &self,
        symbol: &str,
        side: &str,
        quantity: f64,
        price: Option<f64>,
        order_type: &str,
        time_in_force: &str,
    ) -> Result<String, Box<dyn std::error::Error>> {
        // Generate order ID
        let order_id = uuid::Uuid::new_v4().to_string();
        
        // Insert order into database
        sqlx::query(
            r#"
            INSERT INTO orders (id, symbol, side, quantity, price, order_type, time_in_force, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'NEW', NOW())
            "#
        )
        .bind(&order_id)
        .bind(symbol)
        .bind(side)
        .bind(quantity)
        .bind(price)
        .bind(order_type)
        .bind(time_in_force)
        .execute(&self.db_pool)
        .await?;
        
        // Publish order event to Redis
        let order_event = serde_json::json!({
            "type": "NEW_ORDER",
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "order_type": order_type,
            "time_in_force": time_in_force,
            "source": "FIX"
        });
        
        let _: () = redis::cmd("PUBLISH")
            .arg("orders")
            .arg(serde_json::to_string(&order_event)?)
            .query_async(&mut *self.redis_client.clone())
            .await?;
        
        Ok(order_id)
    }
    
    /// Cancel order
    pub async fn cancel_order(&self, order_id: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Update order status in database
        sqlx::query(
            r#"
            UPDATE orders SET status = 'CANCELED', updated_at = NOW()
            WHERE id = $1 AND status IN ('NEW', 'PARTIALLY_FILLED')
            "#
        )
        .bind(order_id)
        .execute(&self.db_pool)
        .await?;
        
        // Publish cancel event to Redis
        let cancel_event = serde_json::json!({
            "type": "CANCEL_ORDER",
            "order_id": order_id,
            "source": "FIX"
        });
        
        let _: () = redis::cmd("PUBLISH")
            .arg("orders")
            .arg(serde_json::to_string(&cancel_event)?)
            .query_async(&mut *self.redis_client.clone())
            .await?;
        
        Ok(())
    }
    
    /// Replace order
    pub async fn replace_order(
        &self,
        order_id: &str,
        new_quantity: Option<f64>,
        new_price: Option<f64>,
    ) -> Result<String, Box<dyn std::error::Error>> {
        // Generate new order ID for replacement
        let new_order_id = uuid::Uuid::new_v4().to_string();
        
        // Get original order
        let original_order = sqlx::query!(
            r#"
            SELECT symbol, side, order_type, time_in_force, quantity, price
            FROM orders WHERE id = $1
            "#,
            order_id
        )
        .fetch_optional(&self.db_pool)
        .await?;
        
        if let Some(order) = original_order {
            let quantity = new_quantity.unwrap_or(order.quantity.unwrap_or(0.0));
            let price = new_price.or(order.price);
            
            // Cancel original order
            self.cancel_order(order_id).await?;
            
            // Create new order
            self.submit_order(
                &order.symbol,
                &order.side,
                quantity,
                price,
                &order.order_type,
                &order.time_in_force,
            ).await?;
            
            Ok(new_order_id)
        } else {
            Err("Order not found".into())
        }
    }
    
    /// Get order status
    pub async fn get_order_status(&self, order_id: &str) -> Option<OrderStatus> {
        let order = sqlx::query!(
            r#"
            SELECT id, symbol, side, quantity, price, filled_qty, status, created_at
            FROM orders WHERE id = $1
            "#,
            order_id
        )
        .fetch_optional(&self.db_pool)
        .await
        .ok()
        .flatten()?;
        
        let leaves_qty = order.quantity.unwrap_or(0.0) - order.filled_qty.unwrap_or(0.0);
        
        Some(OrderStatus {
            order_id: order.id,
            symbol: order.symbol,
            side: order.side,
            quantity: order.quantity.unwrap_or(0.0),
            price: order.price,
            filled_qty: order.filled_qty.unwrap_or(0.0),
            leaves_qty,
            cum_qty: order.filled_qty.unwrap_or(0.0),
            avg_price: 0.0, // TODO: Calculate from trades
            status: order.status,
            timestamp: order.created_at,
        })
    }
    
    /// Get market data for symbol
    pub async fn get_market_data(&self, symbol: &str) -> Option<MarketData> {
        // Try cache first
        {
            let cache = self.cache.read().await;
            if let Some(data) = cache.get(symbol) {
                return Some(data.clone());
            }
        }
        
        // Fetch from database
        let data = sqlx::query!(
            r#"
            SELECT 
                symbol,
                best_bid,
                best_ask,
                bid_size,
                ask_size,
                last_price,
                last_size,
                volume_24h,
                high_24h,
                low_24h,
                updated_at as timestamp
            FROM market_data WHERE symbol = $1
            "#,
            symbol
        )
        .fetch_optional(&self.db_pool)
        .await
        .ok()
        .flatten()?;
        
        let market_data = MarketData {
            symbol: data.symbol,
            best_bid: data.best_bid.unwrap_or(0.0),
            best_ask: data.best_ask.unwrap_or(0.0),
            bid_size: data.bid_size.unwrap_or(0.0),
            ask_size: data.ask_size.unwrap_or(0.0),
            last_price: data.last_price.unwrap_or(0.0),
            last_size: data.last_size.unwrap_or(0.0),
            volume_24h: data.volume_24h.unwrap_or(0.0),
            high_24h: data.high_24h.unwrap_or(0.0),
            low_24h: data.low_24h.unwrap_or(0.0),
            timestamp: data.timestamp,
        };
        
        // Update cache
        {
            let mut cache = self.cache.write().await;
            cache.insert(symbol.to_string(), market_data.clone());
        }
        
        Some(market_data)
    }
    
    /// Get quote for symbol
    pub async fn get_quote(&self, symbol: &str) -> Option<Quote> {
        let market_data = self.get_market_data(symbol).await?;
        
        Some(Quote {
            symbol: market_data.symbol,
            bid_price: market_data.best_bid,
            ask_price: market_data.best_ask,
            bid_size: market_data.bid_size,
            ask_size: market_data.ask_size,
            timestamp: market_data.timestamp,
        })
    }
    
    /// Get available symbols
    pub async fn get_available_symbols(&self) -> Vec<String> {
        sqlx::query!(
            r#"
            SELECT symbol FROM trading_pairs WHERE status = 'ACTIVE'
            ORDER BY symbol
            "#
        )
        .fetch_all(&self.db_pool)
        .await
        .map(|rows| rows.into_iter().map(|r| r.symbol).collect())
        .unwrap_or_default()
    }
    
    /// Get trading session status
    pub async fn get_trading_session_status(&self) -> TradingSessionStatus {
        // In production, this would check actual session status
        TradingSessionStatus {
            session_id: "DEFAULT".to_string(),
            status: "ACTIVE".to_string(),
            start_time: chrono::Utc::now() - chrono::Duration::hours(24),
            end_time: chrono::Utc::now() + chrono::Duration::hours(24),
            is_trading: true,
        }
    }
    
    /// Update market data cache
    pub async fn update_market_data(&self, data: MarketData) {
        let mut cache = self.cache.write().await;
        cache.insert(data.symbol.clone(), data);
        
        // Also update database
        let _ = sqlx::query(
            r#"
            INSERT INTO market_data (symbol, best_bid, best_ask, bid_size, ask_size, last_price, last_size, volume_24h, high_24h, low_24h, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            ON CONFLICT (symbol) DO UPDATE SET
                best_bid = EXCLUDED.best_bid,
                best_ask = EXCLUDED.best_ask,
                bid_size = EXCLUDED.bid_size,
                ask_size = EXCLUDED.ask_size,
                last_price = EXCLUDED.last_price,
                last_size = EXCLUDED.last_size,
                volume_24h = EXCLUDED.volume_24h,
                high_24h = EXCLUDED.high_24h,
                low_24h = EXCLUDED.low_24h,
                updated_at = NOW()
            "#
        )
        .bind(&data.symbol)
        .bind(data.best_bid)
        .bind(data.best_ask)
        .bind(data.bid_size)
        .bind(data.ask_size)
        .bind(data.last_price)
        .bind(data.last_size)
        .bind(data.volume_24h)
        .bind(data.high_24h)
        .bind(data.low_24h)
        .execute(&self.db_pool)
        .await;
    }
}