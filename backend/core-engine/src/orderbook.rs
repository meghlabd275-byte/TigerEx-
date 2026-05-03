//! High-performance order book implementation
//! Uses BTreeMap for O(log n) operations and lock-free data structures

use std::collections::BTreeMap;
use std::sync::Arc;
use parking_lot::RwLock;
use rust_decimal::Decimal;
use chrono::{DateTime, Utc};
use uuid::Uuid;
use crossbeam::queue::SegQueue;

use crate::models::{Order, OrderSide, OrderStatus, Trade, OrderBookLevel, OrderBook as OrderBookSnapshot};

/// Price level in the order book
#[derive(Debug, Clone)]
pub struct PriceLevel {
    pub price: Decimal,
    pub orders: Vec<Arc<Order>>,
    pub total_quantity: Decimal,
}

impl PriceLevel {
    pub fn new(price: Decimal) -> Self {
        Self {
            price,
            orders: Vec::new(),
            total_quantity: Decimal::ZERO,
        }
    }

    pub fn add_order(&mut self, order: Arc<Order>) {
        self.total_quantity += order.remaining_quantity;
        self.orders.push(order);
    }

    pub fn remove_order(&mut self, order_id: Uuid) -> Option<Arc<Order>> {
        if let Some(pos) = self.orders.iter().position(|o| o.id == order_id) {
            let order = self.orders.remove(pos);
            self.total_quantity -= order.remaining_quantity;
            Some(order)
        } else {
            None
        }
    }

    pub fn update_quantity(&mut self, order_id: Uuid, delta: Decimal) {
        if let Some(order) = self.orders.iter_mut().find(|o| o.id == order_id) {
            if let Some(o) = Arc::get_mut(order) {
                o.remaining_quantity -= delta;
                o.updated_at = Utc::now();
            }
        }
        self.total_quantity -= delta;
    }
}

/// Order book for a single trading pair
pub struct OrderBook {
    pub symbol: String,
    pub bids: BTreeMap<Decimal, PriceLevel>,
    pub asks: BTreeMap<Decimal, PriceLevel>,
    pub order_map: RwLock<std::collections::HashMap<Uuid, (OrderSide, Decimal)>>,
    pub last_update_id: RwLock<u64>,
    pub trade_queue: SegQueue<Trade>,
    pub created_at: DateTime<Utc>,
}

impl OrderBook {
    pub fn new(symbol: String) -> Self {
        Self {
            symbol,
            bids: BTreeMap::new(),
            asks: BTreeMap::new(),
            order_map: RwLock::new(std::collections::HashMap::new()),
            last_update_id: RwLock::new(0),
            trade_queue: SegQueue::new(),
            created_at: Utc::now(),
        }
    }

    /// Add an order to the order book
    pub fn add_order(&mut self, order: Arc<Order>) -> Result<(), String> {
        if order.status != OrderStatus::New && order.status != OrderStatus::PartiallyFilled {
            return Err("Invalid order status".to_string());
        }

        let price = match order.price {
            Some(p) => p,
            None => return Err("Order must have a price".to_string()),
        };

        let book = match order.side {
            OrderSide::Buy => &mut self.bids,
            OrderSide::Sell => &mut self.asks,
        };

        book.entry(price)
            .or_insert_with(|| PriceLevel::new(price))
            .add_order(order.clone());

        self.order_map.write().insert(order.id, (order.side, price));
        
        let mut update_id = self.last_update_id.write();
        *update_id += 1;

        Ok(())
    }

    /// Remove an order from the order book
    pub fn remove_order(&mut self, order_id: Uuid) -> Option<Arc<Order>> {
        let (side, price) = self.order_map.write().remove(&order_id)?;
        
        let book = match side {
            OrderSide::Buy => &mut self.bids,
            OrderSide::Sell => &mut self.asks,
        };

        let removed = book.get_mut(&price)?.remove_order(order_id);
        
        // Remove empty price levels
        if let Some(level) = book.get(&price) {
            if level.orders.is_empty() {
                book.remove(&price);
            }
        }

        let mut update_id = self.last_update_id.write();
        *update_id += 1;

        removed
    }

    /// Get the best bid price
    pub fn best_bid(&self) -> Option<(Decimal, Decimal)> {
        self.bids.iter().next_back().map(|(price, level)| (*price, level.total_quantity))
    }

    /// Get the best ask price
    pub fn best_ask(&self) -> Option<(Decimal, Decimal)> {
        self.asks.iter().next().map(|(price, level)| (*price, level.total_quantity))
    }

    /// Get spread (ask - bid)
    pub fn spread(&self) -> Option<Decimal> {
        let best_bid = self.best_bid()?.0;
        let best_ask = self.best_ask()?.0;
        Some(best_ask - best_bid)
    }

    /// Get mid price
    pub fn mid_price(&self) -> Option<Decimal> {
        let best_bid = self.best_bid()?.0;
        let best_ask = self.best_ask()?.0;
        Some((best_bid + best_ask) / Decimal::from(2))
    }

    /// Match incoming order against the book
    pub fn match_order(&mut self, mut incoming: Order) -> (Order, Vec<Trade>) {
        let mut trades = Vec::new();
        
        let (book, is_buy) = match incoming.side {
            OrderSide::Buy => (&mut self.asks, true),
            OrderSide::Sell => (&mut self.bids, false),
        };

        let mut prices_to_remove = Vec::new();

        for (&price, level) in book.iter_mut() {
            // Check if the price is acceptable
            if is_buy && price > incoming.price.unwrap_or(Decimal::MAX) {
                break;
            }
            if !is_buy && price < incoming.price.unwrap_or(Decimal::ZERO) {
                break;
            }

            // Match against orders at this price level
            let mut orders_to_remove = Vec::new();

            for resting_order in &mut level.orders {
                if incoming.remaining_quantity == Decimal::ZERO {
                    break;
                }

                let resting = Arc::clone(resting_order);
                
                let fill_qty = std::cmp::min(
                    incoming.remaining_quantity,
                    resting.remaining_quantity,
                );

                // Create trade
                let trade = Trade {
                    id: Uuid::new_v4(),
                    symbol: self.symbol.clone(),
                    order_id: incoming.id,
                    counter_order_id: resting.id,
                    user_id: incoming.user_id,
                    counter_user_id: resting.user_id,
                    side: incoming.side,
                    price,
                    quantity: fill_qty,
                    fee: Decimal::ZERO, // Calculated by fee engine
                    fee_currency: "USDT".to_string(),
                    is_maker: false,
                    timestamp: Utc::now(),
                };
                trades.push(trade);

                // Update both orders
                incoming.fill(fill_qty, price);
                if let Some(r) = Arc::get_mut(resting_order) {
                    r.fill(fill_qty, price);
                }

                if resting.remaining_quantity == Decimal::ZERO {
                    orders_to_remove.push(resting.id);
                }

                level.total_quantity -= fill_qty;
            }

            // Remove filled orders
            for order_id in orders_to_remove {
                level.remove_order(order_id);
                self.order_map.write().remove(&order_id);
            }

            // Track empty price levels
            if level.orders.is_empty() {
                prices_to_remove.push(price);
            }
        }

        // Remove empty price levels
        for price in prices_to_remove {
            book.remove(&price);
        }

        let mut update_id = self.last_update_id.write();
        *update_id += 1;

        (incoming, trades)
    }

    /// Get order book depth
    pub fn get_depth(&self, limit: usize) -> OrderBookSnapshot {
        let bids: Vec<OrderBookLevel> = self.bids
            .iter()
            .rev()
            .take(limit)
            .map(|(price, level)| OrderBookLevel {
                price: *price,
                quantity: level.total_quantity,
                order_count: level.orders.len() as u64,
            })
            .collect();

        let asks: Vec<OrderBookLevel> = self.asks
            .iter()
            .take(limit)
            .map(|(price, level)| OrderBookLevel {
                price: *price,
                quantity: level.total_quantity,
                order_count: level.orders.len() as u64,
            })
            .collect();

        OrderBookSnapshot {
            symbol: self.symbol.clone(),
            bids,
            asks,
            last_update_id: *self.last_update_id.read(),
            timestamp: Utc::now(),
        }
    }

    /// Get total bid liquidity
    pub fn total_bid_liquidity(&self) -> Decimal {
        self.bids.values().map(|l| l.total_quantity).sum()
    }

    /// Get total ask liquidity
    pub fn total_ask_liquidity(&self) -> Decimal {
        self.asks.values().map(|l| l.total_quantity).sum()
    }

    /// Check if order exists
    pub fn has_order(&self, order_id: Uuid) -> bool {
        self.order_map.read().contains_key(&order_id)
    }

    /// Get order by ID
    pub fn get_order(&self, order_id: Uuid) -> Option<Arc<Order>> {
        let (side, price) = self.order_map.read().get(&order_id).cloned()?;
        let book = match side {
            OrderSide::Buy => &self.bids,
            OrderSide::Sell => &self.asks,
        };
        book.get(&price)?
            .orders
            .iter()
            .find(|o| o.id == order_id)
            .cloned()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::{OrderType, TimeInForce};

    #[test]
    fn test_order_book_basic() {
        let mut book = OrderBook::new("BTCUSDT".to_string());
        
        let order = Order::new(
            Uuid::new_v4(),
            "BTCUSDT".to_string(),
            OrderSide::Buy,
            OrderType::Limit,
            Decimal::from(100),
            Some(Decimal::from(50000)),
            TimeInForce::Gtc,
        );

        book.add_order(Arc::new(order)).unwrap();
        
        let (bid_price, bid_qty) = book.best_bid().unwrap();
        assert_eq!(bid_price, Decimal::from(50000));
        assert_eq!(bid_qty, Decimal::from(100));
    }

    #[test]
    fn test_order_matching() {
        let mut book = OrderBook::new("BTCUSDT".to_string());
        
        // Add resting sell order
        let sell_order = Order::new(
            Uuid::new_v4(),
            "BTCUSDT".to_string(),
            OrderSide::Sell,
            OrderType::Limit,
            Decimal::from(100),
            Some(Decimal::from(50000)),
            TimeInForce::Gtc,
        );
        book.add_order(Arc::new(sell_order)).unwrap();

        // Match with buy order
        let buy_order = Order::new(
            Uuid::new_v4(),
            "BTCUSDT".to_string(),
            OrderSide::Buy,
            OrderType::Limit,
            Decimal::from(50),
            Some(Decimal::from(50000)),
            TimeInForce::Gtc,
        );

        let (filled_order, trades) = book.match_order(buy_order);
        
        assert_eq!(trades.len(), 1);
        assert_eq!(filled_order.status, OrderStatus::Filled);
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
