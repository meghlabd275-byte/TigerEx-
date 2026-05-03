//! Matching Algorithms
//! High-performance order matching with multiple algorithm support

use rust_decimal::Decimal;
use std::collections::VecDeque;
use chrono::{DateTime, Utc};
use uuid::Uuid;

use crate::models::*;

/// Matching algorithm types
#[derive(Debug, Clone, Copy)]
pub enum MatchingAlgorithm {
    /// Price-Time Priority (FIFO) - Standard for spot markets
    PriceTimePriority,
    /// Pro-Rata - Used in derivatives markets
    ProRata,
    /// Hybrid - Combination of FIFO and Pro-Rata
    Hybrid { fifo_percentage: u8 },
}

/// Match result
#[derive(Debug, Clone)]
pub struct MatchResult {
    pub taker_order_id: Uuid,
    pub maker_order_id: Uuid,
    pub price: Decimal,
    pub quantity: Decimal,
    pub taker_user_id: Uuid,
    pub maker_user_id: Uuid,
    pub timestamp: DateTime<Utc>,
}

/// Price level for matching
#[derive(Debug, Clone)]
pub struct PriceLevel {
    pub price: Decimal,
    pub orders: VecDeque<RestingOrder>,
    pub total_quantity: Decimal,
}

/// Resting order in the book
#[derive(Debug, Clone)]
pub struct RestingOrder {
    pub id: Uuid,
    pub user_id: Uuid,
    pub quantity: Decimal,
    pub filled_quantity: Decimal,
    pub timestamp: DateTime<Utc>,
    pub order_type: OrderType,
}

impl PriceLevel {
    pub fn new(price: Decimal) -> Self {
        Self {
            price,
            orders: VecDeque::new(),
            total_quantity: Decimal::ZERO,
        }
    }

    pub fn add_order(&mut self, order: RestingOrder) {
        self.total_quantity += order.remaining_quantity();
        self.orders.push_back(order);
    }

    pub fn remove_order(&mut self, order_id: Uuid) -> Option<RestingOrder> {
        if let Some(pos) = self.orders.iter().position(|o| o.id == order_id) {
            let order = self.orders.remove(pos).unwrap();
            self.total_quantity -= order.remaining_quantity();
            Some(order)
        } else {
            None
        }
    }

    pub fn is_empty(&self) -> bool {
        self.orders.is_empty()
    }
}

impl RestingOrder {
    pub fn remaining_quantity(&self) -> Decimal {
        self.quantity - self.filled_quantity
    }

    pub fn fill(&mut self, quantity: Decimal) {
        self.filled_quantity += quantity;
    }
}

/// FIFO Matching (Price-Time Priority)
pub fn match_fifo(
    taker_quantity: Decimal,
    price_levels: &mut [PriceLevel],
    taker_order_id: Uuid,
    taker_user_id: Uuid,
) -> (Decimal, Vec<MatchResult>) {
    let mut remaining = taker_quantity;
    let mut matches = Vec::new();

    for level in price_levels.iter_mut() {
        if remaining == Decimal::ZERO {
            break;
        }

        while let Some(mut order) = level.orders.front_mut() {
            if remaining == Decimal::ZERO {
                break;
            }

            let fill_qty = remaining.min(order.remaining_quantity());
            
            matches.push(MatchResult {
                taker_order_id,
                maker_order_id: order.id,
                price: level.price,
                quantity: fill_qty,
                taker_user_id,
                maker_user_id: order.user_id,
                timestamp: Utc::now(),
            });

            order.fill(fill_qty);
            remaining -= fill_qty;
            level.total_quantity -= fill_qty;

            if order.remaining_quantity() == Decimal::ZERO {
                level.orders.pop_front();
            }
        }
    }

    (remaining, matches)
}

/// Pro-Rata Matching
pub fn match_pro_rata(
    taker_quantity: Decimal,
    price_level: &mut PriceLevel,
    taker_order_id: Uuid,
    taker_user_id: Uuid,
) -> (Decimal, Vec<MatchResult>) {
    if price_level.orders.is_empty() || price_level.total_quantity == Decimal::ZERO {
        return (taker_quantity, Vec::new());
    }

    let mut matches = Vec::new();
    let fill_ratio = (taker_quantity / price_level.total_quantity).min(Decimal::ONE);

    let mut orders_to_remove = Vec::new();

    for (i, order) in price_level.orders.iter_mut().enumerate() {
        let fill_qty = (order.remaining_quantity() * fill_ratio)
            .min(taker_quantity - matches.iter().map(|m: &MatchResult| m.quantity).sum::<Decimal>());

        if fill_qty > Decimal::ZERO {
            matches.push(MatchResult {
                taker_order_id,
                maker_order_id: order.id,
                price: price_level.price,
                quantity: fill_qty,
                taker_user_id,
                maker_user_id: order.user_id,
                timestamp: Utc::now(),
            });

            order.fill(fill_qty);

            if order.remaining_quantity() == Decimal::ZERO {
                orders_to_remove.push(i);
            }
        }
    }

    // Remove filled orders
    for i in orders_to_remove.into_iter().rev() {
        price_level.orders.remove(i);
    }

    price_level.total_quantity = price_level.orders.iter()
        .map(|o| o.remaining_quantity())
        .sum();

    let total_filled: Decimal = matches.iter().map(|m| m.quantity).sum();
    (taker_quantity - total_filled, matches)
}

/// Hybrid Matching (FIFO + Pro-Rata)
pub fn match_hybrid(
    taker_quantity: Decimal,
    price_level: &mut PriceLevel,
    taker_order_id: Uuid,
    taker_user_id: Uuid,
    fifo_percentage: u8,
) -> (Decimal, Vec<MatchResult>) {
    let mut matches = Vec::new();
    let mut remaining = taker_quantity;

    // FIFO portion
    let fifo_qty = taker_quantity * Decimal::from(fifo_percentage) / Decimal::from(100);
    
    if let Some(mut first_order) = price_level.orders.front_mut() {
        let fill_qty = fifo_qty.min(first_order.remaining_quantity());
        
        matches.push(MatchResult {
            taker_order_id,
            maker_order_id: first_order.id,
            price: price_level.price,
            quantity: fill_qty,
            taker_user_id,
            maker_user_id: first_order.user_id,
            timestamp: Utc::now(),
        });

        first_order.fill(fill_qty);
        remaining -= fill_qty;
    }

    // Pro-Rata for remainder
    if remaining > Decimal::ZERO && price_level.total_quantity > Decimal::ZERO {
        let (rem, mut pro_rata_matches) = match_pro_rata(
            remaining,
            price_level,
            taker_order_id,
            taker_user_id,
        );
        matches.append(&mut pro_rata_matches);
        remaining = rem;
    }

    (remaining, matches)
}

/// Self-trade prevention
#[derive(Debug, Clone, Copy)]
pub enum SelfTradePrevention {
    None,
    CancelOldest,
    CancelNewest,
    CancelBoth,
    DecrementAndCancel,
}

/// Check for self-trade
pub fn check_self_trade(
    taker_user_id: Uuid,
    maker_user_id: Uuid,
) -> bool {
    taker_user_id == maker_user_id
}

/// Apply self-trade prevention
pub fn apply_stp(
    stp_mode: SelfTradePrevention,
    taker_order_id: Uuid,
    maker_order_id: Uuid,
) -> (bool, bool) {
    // Returns (cancel_taker, cancel_maker)
    match stp_mode {
        SelfTradePrevention::None => (false, false),
        SelfTradePrevention::CancelOldest => (false, true),
        SelfTradePrevention::CancelNewest => (true, false),
        SelfTradePrevention::CancelBoth => (true, true),
        SelfTradePrevention::DecrementAndCancel => (false, false),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_price_level() {
        let mut level = PriceLevel::new(Decimal::from(50000));
        
        level.add_order(RestingOrder {
            id: Uuid::new_v4(),
            user_id: Uuid::new_v4(),
            quantity: Decimal::from(10),
            filled_quantity: Decimal::ZERO,
            timestamp: Utc::now(),
            order_type: OrderType::Limit,
        });

        assert_eq!(level.orders.len(), 1);
        assert_eq!(level.total_quantity, Decimal::from(10));
    }
}pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}
