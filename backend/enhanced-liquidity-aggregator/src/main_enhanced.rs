/*
Enhanced TigerEx Multi-Exchange Liquidity Aggregator Main Implementation
Comprehensive liquidity aggregation for all market types across major exchanges
*/

mod exchange_connectors;
use exchange_connectors::*;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::sync::{RwLock, Mutex};
use tokio::time::{interval, sleep};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use reqwest::Client;
use uuid::Uuid;
use rust_decimal::Decimal;
use chrono::{DateTime, Utc};
use anyhow::{Result, anyhow};
use tracing::{info, error, warn, debug};
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use tower::ServiceBuilder;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;

// Enhanced liquidity aggregator
pub struct EnhancedLiquidityAggregator {
    connectors: HashMap<String, Arc<dyn EnhancedExchangeConnector>>,
    market_data: Arc<RwLock<HashMap<String, HashMap<String, EnhancedOrderBook>>>>,
    liquidity_metrics: Arc<RwLock<HashMap<String, HashMap<String, LiquidityMetrics>>>>,
    arbitrage_opportunities: Arc<RwLock<Vec<CrossExchangeArbitrage>>>,
    smart_routes: Arc<RwLock<HashMap<String, SmartOrderRoute>>>,
    db_pool: Option<PgPool>,
    redis_client: Option<Arc<Mutex<redis::aio::Connection>>>,
}

impl EnhancedLiquidityAggregator {
    pub async fn new(config: &EnhancedConfig) -> Result<Self> {
        let mut connectors: HashMap<String, Arc<dyn EnhancedExchangeConnector>> = HashMap::new();
        
        // Initialize all exchange connectors
        if config.binance.enabled {
            connectors.insert(
                "binance".to_string(),
                Arc::new(EnhancedBinanceConnector::new(
                    config.binance.api_key.clone(),
                    config.binance.secret.clone(),
                    config.binance.testnet
                ))
            );
        }
        
        if config.okx.enabled {
            connectors.insert(
                "okx".to_string(),
                Arc::new(EnhancedOKXConnector::new(
                    config.okx.api_key.clone(),
                    config.okx.secret.clone(),
                    config.okx.passphrase.clone(),
                    config.okx.testnet
                ))
            );
        }
        
        if config.bybit.enabled {
            connectors.insert(
                "bybit".to_string(),
                Arc::new(EnhancedBybitConnector::new(
                    config.bybit.api_key.clone(),
                    config.bybit.secret.clone(),
                    config.bybit.testnet
                ))
            );
        }
        
        if config.kucoin.enabled {
            connectors.insert(
                "kucoin".to_string(),
                Arc::new(EnhancedKuCoinConnector::new(
                    config.kucoin.api_key.clone(),
                    config.kucoin.secret.clone(),
                    config.kucoin.passphrase.clone(),
                    config.kucoin.testnet
                ))
            );
        }
        
        if config.mexc.enabled {
            connectors.insert(
                "mexc".to_string(),
                Arc::new(EnhancedMEXCConnector::new(
                    config.mexc.api_key.clone(),
                    config.mexc.secret.clone(),
                    config.mexc.testnet
                ))
            );
        }
        
        if config.bitmart.enabled {
            connectors.insert(
                "bitmart".to_string(),
                Arc::new(EnhancedBitMartConnector::new(
                    config.bitmart.api_key.clone(),
                    config.bitmart.secret.clone(),
                    config.bitmart.testnet
                ))
            );
        }
        
        if config.coinw.enabled {
            connectors.insert(
                "coinw".to_string(),
                Arc::new(EnhancedCoinWConnector::new(
                    config.coinw.api_key.clone(),
                    config.coinw.secret.clone(),
                    config.coinw.testnet
                ))
            );
        }
        
        if config.bitget.enabled {
            connectors.insert(
                "bitget".to_string(),
                Arc::new(EnhancedBitgetConnector::new(
                    config.bitget.api_key.clone(),
                    config.bitget.secret.clone(),
                    config.bitget.testnet
                ))
            );
        }
        
        // Initialize database and Redis connections (optional for now)
        let db_pool = None; // Would be initialized with real database
        let redis_client = None; // Would be initialized with real Redis
        
        Ok(Self {
            connectors,
            market_data: Arc::new(RwLock::new(HashMap::new())),
            liquidity_metrics: Arc::new(RwLock::new(HashMap::new())),
            arbitrage_opportunities: Arc::new(RwLock::new(Vec::new())),
            smart_routes: Arc::new(RwLock::new(HashMap::new())),
            db_pool,
            redis_client,
        })
    }
    
    pub async fn start_aggregation(&self, symbols_by_market: HashMap<String, Vec<String>>) -> Result<()> {
        info!("Starting enhanced liquidity aggregation for {} market types", symbols_by_market.len());
        
        for (market_type, symbols) in symbols_by_market {
            info!("Starting aggregation for {} market type with {} symbols", market_type, symbols.len());
            
            let connectors = self.connectors.clone();
            let market_data = self.market_data.clone();
            let liquidity_metrics = self.liquidity_metrics.clone();
            let market_type_clone = market_type.clone();
            
            // Start aggregation for each market type
            tokio::spawn(async move {
                let mut interval = interval(Duration::from_millis(100)); // 100ms updates
                
                loop {
                    interval.tick().await;
                    
                    for symbol in &symbols {
                        let mut symbol_data = HashMap::new();
                        
                        // Fetch data from all enabled exchanges
                        for (exchange_name, connector) in &connectors {
                            match connector.get_order_book(symbol, &market_type_clone).await {
                                Ok(order_book) => {
                                    symbol_data.insert(exchange_name.clone(), order_book);
                                }
                                Err(e) => {
                                    warn!("Failed to get order book from {} for {}: {}", exchange_name, symbol, e);
                                }
                            }
                        }
                        
                        // Update market data
                        {
                            let mut data = market_data.write().await;
                            if !data.contains_key(symbol) {
                                data.insert(symbol.clone(), HashMap::new());
                            }
                            data.get_mut(symbol).unwrap().insert(market_type_clone.clone(), symbol_data);
                        }
                        
                        // Calculate liquidity metrics
                        if !symbol_data.is_empty() {
                            let order_books: Vec<_> = symbol_data.values().cloned().collect();
                            let metrics = Self::calculate_enhanced_liquidity_metrics(symbol, &market_type_clone, &order_books);
                            
                            {
                                let mut metrics_map = liquidity_metrics.write().await;
                                if !metrics_map.contains_key(symbol) {
                                    metrics_map.insert(symbol.clone(), HashMap::new());
                                }
                                metrics_map.get_mut(symbol).unwrap().insert(market_type_clone.clone(), metrics);
                            }
                        }
                    }
                }
            });
        }
        
        // Start arbitrage detection
        self.start_enhanced_arbitrage_detection().await?;
        
        // Start smart order routing
        self.start_smart_order_routing().await?;
        
        Ok(())
    }
    
    pub async fn start_enhanced_arbitrage_detection(&self) -> Result<()> {
        let market_data = self.market_data.clone();
        let arbitrage_opportunities = self.arbitrage_opportunities.clone();
        
        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(1)); // Check every second
            
            loop {
                interval.tick().await;
                
                let data = market_data.read().await;
                let mut opportunities = Vec::new();
                
                for (symbol, market_types) in data.iter() {
                    for (market_type, exchange_data) in market_types.iter() {
                        if exchange_data.len() >= 2 {
                            // Find arbitrage opportunities between exchanges
                            let exchange_names: Vec<_> = exchange_data.keys().cloned().collect();
                            
                            for i in 0..exchange_names.len() {
                                for j in (i + 1)..exchange_names.len() {
                                    let exchange1 = &exchange_names[i];
                                    let exchange2 = &exchange_names[j];
                                    
                                    if let (Some(book1), Some(book2)) = (exchange_data.get(exchange1), exchange_data.get(exchange2)) {
                                        if let Some(opportunity) = Self::detect_enhanced_arbitrage(
                                            symbol,
                                            market_type,
                                            book1,
                                            book2,
                                            exchange1,
                                            exchange2
                                        ) {
                                            opportunities.push(opportunity);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Update arbitrage opportunities
                {
                    let mut arb_opps = arbitrage_opportunities.write().await;
                    *arb_opps = opportunities;
                }
            }
        });
        
        Ok(())
    }
    
    pub async fn start_smart_order_routing(&self) -> Result<()> {
        let market_data = self.market_data.clone();
        let smart_routes = self.smart_routes.clone();
        
        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(5)); // Update every 5 seconds
            
            loop {
                interval.tick().await;
                
                let data = market_data.read().await;
                let mut routes = HashMap::new();
                
                for (symbol, market_types) in data.iter() {
                    for (market_type, exchange_data) in market_types.iter() {
                        if !exchange_data.is_empty() {
                            // Calculate optimal routing
                            let route = Self::calculate_optimal_route(
                                symbol,
                                market_type,
                                exchange_data
                            );
                            
                            let key = format!("{}:{}", symbol, market_type);
                            routes.insert(key, route);
                        }
                    }
                }
                
                // Update smart routes
                {
                    let mut routes_map = smart_routes.write().await;
                    *routes_map = routes;
                }
            }
        });
        
        Ok(())
    }
    
    pub async fn get_aggregated_order_book(&self, symbol: &str, market_type: &str) -> Result<EnhancedOrderBook> {
        let data = self.market_data.read().await;
        
        if let Some(market_types) = data.get(symbol) {
            if let Some(exchange_data) = market_types.get(market_type) {
                Ok(Self::aggregate_enhanced_order_books(symbol, market_type, exchange_data))
            } else {
                Err(anyhow!("No order book data found for {} in {} market", symbol, market_type))
            }
        } else {
            Err(anyhow!("No data found for symbol: {}", symbol))
        }
    }
    
    pub async fn get_best_liquidity_route(&self, symbol: &str, market_type: &str, side: &str, quantity: Decimal) -> Result<SmartOrderRoute> {
        let data = self.market_data.read().await;
        
        if let Some(market_types) = data.get(symbol) {
            if let Some(exchange_data) = market_types.get(market_type) {
                Ok(Self::calculate_optimal_route_for_order(
                    symbol,
                    market_type,
                    side,
                    quantity,
                    exchange_data
                ))
            } else {
                Err(anyhow!("No liquidity data found for {} in {} market", symbol, market_type))
            }
        } else {
            Err(anyhow!("No data found for symbol: {}", symbol))
        }
    }
    
    pub async fn get_arbitrage_opportunities(&self) -> Result<Vec<CrossExchangeArbitrage>> {
        let opportunities = self.arbitrage_opportunities.read().await;
        Ok(opportunities.clone())
    }
    
    pub async fn get_smart_routes(&self) -> Result<HashMap<String, SmartOrderRoute>> {
        let routes = self.smart_routes.read().await;
        Ok(routes.clone())
    }
    
    // Helper methods
    fn calculate_enhanced_liquidity_metrics(symbol: &str, market_type: &str, order_books: &[EnhancedOrderBook]) -> LiquidityMetrics {
        let aggregated = Self::aggregate_enhanced_order_books(symbol, market_type, order_books);
        
        let total_liquidity_usd = (aggregated.total_bid_volume + aggregated.total_ask_volume) * 
            aggregated.best_bid.unwrap_or_default();
        
        let spread_bps = match (aggregated.best_bid, aggregated.best_ask) {
            (Some(bid), Some(ask)) => (ask - bid) / bid * Decimal::new(10000, 0),
            _ => Decimal::ZERO,
        };
        
        // Calculate depth at different levels
        let depth_1_percent = Self::calculate_enhanced_depth_at_percentage(&aggregated, Decimal::new(1, 2));
        let depth_5_percent = Self::calculate_enhanced_depth_at_percentage(&aggregated, Decimal::new(5, 2));
        
        // Calculate price impact for different trade sizes
        let price_impact_1k = Self::calculate_enhanced_price_impact(&aggregated, Decimal::new(1000, 0));
        let price_impact_10k = Self::calculate_enhanced_price_impact(&aggregated, Decimal::new(10000, 0));
        let price_impact_100k = Self::calculate_enhanced_price_impact(&aggregated, Decimal::new(100000, 0));
        
        // Build per-exchange metrics
        let mut sources = HashMap::new();
        for book in order_books {
            sources.insert(book.exchange.clone(), ExchangeLiquidityMetrics {
                exchange: book.exchange.clone(),
                liquidity_usd: (book.total_bid_volume + book.total_ask_volume) * book.best_bid.unwrap_or_default(),
                volume_24h: Decimal::ZERO, // Would be fetched separately
                spread_bps: book.spread_bps.unwrap_or_default(),
                uptime_percentage: Decimal::new(99, 2),
                latency_ms: book.latency_ms,
                market_types: vec![market_type.to_string()],
            });
        }
        
        LiquidityMetrics {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            total_liquidity_usd,
            bid_liquidity_usd: aggregated.total_bid_volume * aggregated.best_bid.unwrap_or_default(),
            ask_liquidity_usd: aggregated.total_ask_volume * aggregated.best_ask.unwrap_or_default(),
            spread_bps,
            depth_1_percent,
            depth_5_percent,
            volume_24h: Decimal::ZERO, // Would be aggregated from exchanges
            price_impact_1k,
            price_impact_10k,
            price_impact_100k,
            sources,
            timestamp: Utc::now(),
        }
    }
    
    fn aggregate_enhanced_order_books(symbol: &str, market_type: &str, order_books: &HashMap<String, EnhancedOrderBook>) -> EnhancedOrderBook {
        let mut all_bids = Vec::new();
        let mut all_asks = Vec::new();
        let mut exchanges = Vec::new();
        
        for (exchange, book) in order_books {
            all_bids.extend(book.bids.clone());
            all_asks.extend(book.asks.clone());
            exchanges.push(exchange.clone());
        }
        
        // Sort and aggregate
        all_bids.sort_by(|a, b| b.price.cmp(&a.price));
        all_asks.sort_by(|a, b| a.price.cmp(&b.price));
        
        // Remove duplicates and aggregate at same price levels
        let mut bid_map: HashMap<Decimal, Decimal> = HashMap::new();
        let mut ask_map: HashMap<Decimal, Decimal> = HashMap::new();
        
        for bid in all_bids {
            *bid_map.entry(bid.price).or_insert(Decimal::ZERO) += bid.quantity;
        }
        
        for ask in all_asks {
            *ask_map.entry(ask.price).or_insert(Decimal::ZERO) += ask.quantity;
        }
        
        // Rebuild aggregated order book
        let mut aggregated_bids = Vec::new();
        let mut aggregated_asks = Vec::new();
        
        for (price, quantity) in bid_map {
            aggregated_bids.push(OrderBookLevel {
                price,
                quantity,
                timestamp: Utc::now(),
                exchange: "aggregated".to_string(),
                is_from_dex: false,
                pool_address: None,
            });
        }
        
        for (price, quantity) in ask_map {
            aggregated_asks.push(OrderBookLevel {
                price,
                quantity,
                timestamp: Utc::now(),
                exchange: "aggregated".to_string(),
                is_from_dex: false,
                pool_address: None,
            });
        }
        
        // Sort again
        aggregated_bids.sort_by(|a, b| b.price.cmp(&a.price));
        aggregated_asks.sort_by(|a, b| a.price.cmp(&b.price));
        
        let best_bid = aggregated_bids.first().map(|b| b.price);
        let best_ask = aggregated_asks.first().map(|a| a.price);
        let spread = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some(ask - bid),
            _ => None,
        };
        
        let spread_bps = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some((ask - bid) / bid * Decimal::new(10000, 0)),
            _ => None,
        };
        
        EnhancedOrderBook {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            exchange: "aggregated".to_string(),
            bids: aggregated_bids,
            asks: aggregated_asks,
            best_bid,
            best_ask,
            spread,
            spread_bps,
            total_bid_volume: aggregated_bids.iter().map(|b| b.quantity).sum(),
            total_ask_volume: aggregated_asks.iter().map(|a| a.quantity).sum(),
            timestamp: Utc::now(),
            latency_ms: 50,
            is_stale: false,
        }
    }
    
    fn calculate_enhanced_depth_at_percentage(order_book: &EnhancedOrderBook, percentage: Decimal) -> Decimal {
        let mid_price = match (order_book.best_bid, order_book.best_ask) {
            (Some(bid), Some(ask)) => (bid + ask) / Decimal::new(2, 0),
            _ => return Decimal::ZERO,
        };
        
        let price_range = mid_price * percentage / Decimal::new(100, 0);
        let upper_bound = mid_price + price_range;
        let lower_bound = mid_price - price_range;
        
        let bid_depth = order_book.bids.iter()
            .filter(|b| b.price >= lower_bound)
            .map(|b| b.quantity)
            .sum::<Decimal>();
            
        let ask_depth = order_book.asks.iter()
            .filter(|a| a.price <= upper_bound)
            .map(|a| a.quantity)
            .sum::<Decimal>();
        
        bid_depth + ask_depth
    }
    
    fn calculate_enhanced_price_impact(order_book: &EnhancedOrderBook, trade_size_usd: Decimal) -> Decimal {
        let mid_price = match (order_book.best_bid, order_book.best_ask) {
            (Some(bid), Some(ask)) => (bid + ask) / Decimal::new(2, 0),
            _ => return Decimal::ZERO,
        };
        
        let trade_quantity = trade_size_usd / mid_price;
        let mut remaining_quantity = trade_quantity;
        let mut total_cost = Decimal::ZERO;
        
        // Simulate buying through the order book
        for ask in &order_book.asks {
            if remaining_quantity <= Decimal::ZERO {
                break;
            }
            
            let quantity_to_buy = remaining_quantity.min(ask.quantity);
            let cost = quantity_to_buy * ask.price;
            total_cost += cost;
            remaining_quantity -= quantity_to_buy;
        }
        
        if remaining_quantity > Decimal::ZERO {
            return Decimal::new(100, 0); // 100% impact if not enough liquidity
        }
        
        let average_price = total_cost / trade_quantity;
        (average_price - mid_price) / mid_price * Decimal::new(100, 0)
    }
    
    fn detect_enhanced_arbitrage(
        symbol: &str,
        market_type: &str,
        book1: &EnhancedOrderBook,
        book2: &EnhancedOrderBook,
        exchange1: &str,
        exchange2: &str
    ) -> Option<CrossExchangeArbitrage> {
        let best_bid1 = book1.bids.first()?.price;
        let best_ask1 = book1.asks.first()?.price;
        let best_bid2 = book2.bids.first()?.price;
        let best_ask2 = book2.asks.first()?.price;
        
        // Check if we can buy on one exchange and sell on another for profit
        let profit_1_to_2 = best_bid2 - best_ask1;
        let profit_2_to_1 = best_bid1 - best_ask2;
        
        let min_profit_threshold = Decimal::new(5, 2); // 0.5% minimum profit
        
        if profit_1_to_2 > min_profit_threshold {
            let profit_percentage = profit_1_to_2 / best_ask1 * Decimal::new(100, 0);
            let max_quantity = best_ask1.min(best_bid2);
            
            Some(CrossExchangeArbitrage {
                id: Uuid::new_v4().to_string(),
                symbol: symbol.to_string(),
                market_type: market_type.to_string(),
                buy_exchange: exchange1.to_string(),
                sell_exchange: exchange2.to_string(),
                buy_price: best_ask1,
                sell_price: best_bid2,
                profit_percentage,
                profit_usd: profit_1_to_2 * max_quantity,
                max_quantity,
                confidence_score: Decimal::new(85, 2), // 85%
                execution_time_ms: 100,
                gas_cost: Some(Decimal::new(25, 0)), // $25 gas cost
                net_profit: profit_1_to_2 * max_quantity - Decimal::new(25, 0),
                timestamp: Utc::now(),
            })
        } else if profit_2_to_1 > min_profit_threshold {
            let profit_percentage = profit_2_to_1 / best_ask2 * Decimal::new(100, 0);
            let max_quantity = best_ask2.min(best_bid1);
            
            Some(CrossExchangeArbitrage {
                id: Uuid::new_v4().to_string(),
                symbol: symbol.to_string(),
                market_type: market_type.to_string(),
                buy_exchange: exchange2.to_string(),
                sell_exchange: exchange1.to_string(),
                buy_price: best_ask2,
                sell_price: best_bid1,
                profit_percentage,
                profit_usd: profit_2_to_1 * max_quantity,
                max_quantity,
                confidence_score: Decimal::new(85, 2),
                execution_time_ms: 100,
                gas_cost: Some(Decimal::new(25, 0)),
                net_profit: profit_2_to_1 * max_quantity - Decimal::new(25, 0),
                timestamp: Utc::now(),
            })
        } else {
            None
        }
    }
    
    fn calculate_optimal_route(
        symbol: &str,
        market_type: &str,
        exchange_data: &HashMap<String, EnhancedOrderBook>
    ) -> SmartOrderRoute {
        // Simple implementation - would be more sophisticated in production
        let mut routes = Vec::new();
        let mut total_quantity = Decimal::ZERO;
        let mut total_cost = Decimal::ZERO;
        let mut exchanges_used = Vec::new();
        
        // Route through exchanges with best prices
        for (exchange, book) in exchange_data {
            if !book.bids.is_empty() && !book.asks.is_empty() {
                let mid_price = (book.best_bid.unwrap_or_default() + book.best_ask.unwrap_or_default()) / Decimal::new(2, 0);
                let quantity = Decimal::new(1, 0); // Simplified quantity
                
                routes.push(RouteStep {
                    exchange: exchange.clone(),
                    market_type: market_type.to_string(),
                    quantity,
                    price: mid_price,
                    fee: quantity * mid_price * Decimal::new(1, 3), // 0.1% fee
                    is_dex: false,
                    pool_address: None,
                    estimated_slippage: Decimal::new(5, 3), // 0.5%
                });
                
                total_quantity += quantity;
                total_cost += quantity * mid_price;
                exchanges_used.push(exchange.clone());
            }
        }
        
        let average_price = if total_quantity > Decimal::ZERO {
            total_cost / total_quantity
        } else {
            Decimal::ZERO
        };
        
        SmartOrderRoute {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            side: "BUY".to_string(),
            quantity: total_quantity,
            routes,
            total_price: total_cost,
            average_price,
            price_impact: Decimal::ZERO,
            estimated_slippage: Decimal::new(5, 3),
            gas_cost: None,
            execution_time_ms: 100,
            exchanges_used,
            is_optimal: true,
        }
    }
    
    fn calculate_optimal_route_for_order(
        symbol: &str,
        market_type: &str,
        side: &str,
        quantity: Decimal,
        exchange_data: &HashMap<String, EnhancedOrderBook>
    ) -> SmartOrderRoute {
        // More sophisticated routing for specific orders
        let mut routes = Vec::new();
        let mut remaining_quantity = quantity;
        let mut total_cost = Decimal::ZERO;
        let mut exchanges_used = Vec::new();
        
        // Route through exchanges with best liquidity
        let mut sorted_exchanges: Vec<_> = exchange_data.iter().collect();
        sorted_exchanges.sort_by(|a, b| {
            let a_liquidity = a.1.total_bid_volume + a.1.total_ask_volume;
            let b_liquidity = b.1.total_bid_volume + b.1.total_ask_volume;
            b_liquidity.cmp(&a_liquidity)
        });
        
        for (exchange, book) in sorted_exchanges {
            if remaining_quantity <= Decimal::ZERO {
                break;
            }
            
            let order_book = if side == "BUY" { &book.asks } else { &book.bids };
            let mut remaining_for_exchange = remaining_quantity;
            
            for level in order_book {
                if remaining_for_exchange <= Decimal::ZERO {
                    break;
                }
                
                let quantity_to_trade = remaining_for_exchange.min(level.quantity);
                let cost = quantity_to_trade * level.price;
                
                routes.push(RouteStep {
                    exchange: exchange.clone(),
                    market_type: market_type.to_string(),
                    quantity: quantity_to_trade,
                    price: level.price,
                    fee: cost * Decimal::new(1, 3), // 0.1% fee
                    is_dex: level.is_from_dex,
                    pool_address: level.pool_address.clone(),
                    estimated_slippage: Decimal::new(5, 3), // 0.5%
                });
                
                total_cost += cost;
                remaining_for_exchange -= quantity_to_trade;
                remaining_quantity -= quantity_to_trade;
            }
            
            exchanges_used.push(exchange.clone());
        }
        
        let average_price = if quantity > Decimal::ZERO {
            total_cost / quantity
        } else {
            Decimal::ZERO
        };
        
        SmartOrderRoute {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            side: side.to_string(),
            quantity,
            routes,
            total_price: total_cost,
            average_price,
            price_impact: Decimal::ZERO,
            estimated_slippage: Decimal::new(5, 3),
            gas_cost: None,
            execution_time_ms: 100,
            exchanges_used,
            is_optimal: remaining_quantity <= Decimal::ZERO,
        }
    }
}

// Application state
#[derive(Clone)]
pub struct EnhancedAppState {
    pub aggregator: Arc<EnhancedLiquidityAggregator>,
}

// API handlers
pub async fn get_enhanced_order_book(
    Path((symbol, market_type)): Path<(String, String)>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<EnhancedOrderBook>, StatusCode> {
    match state.aggregator.get_aggregated_order_book(&symbol, &market_type).await {
        Ok(order_book) => Ok(Json(order_book)),
        Err(_) => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn get_enhanced_liquidity_metrics(
    Path((symbol, market_type)): Path<(String, String)>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<LiquidityMetrics>, StatusCode> {
    match state.aggregator.get_liquidity_metrics(&symbol, &market_type).await {
        Ok(metrics) => Ok(Json(metrics)),
        Err(_) => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn get_market_depth(
    Path((symbol, market_type)): Path<(String, String)>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<MarketDepth>, StatusCode> {
    match state.aggregator.get_market_depth(&symbol, &market_type).await {
        Ok(depth) => Ok(Json(depth)),
        Err(_) => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn get_best_liquidity_route(
    Path((symbol, market_type)): Path<(String, String)>,
    Query(params): Query<HashMap<String, String>>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<SmartOrderRoute>, StatusCode> {
    let side = params.get("side").unwrap_or(&"BUY".to_string()).clone();
    let quantity = params.get("quantity")
        .and_then(|q| q.parse::<Decimal>().ok())
        .unwrap_or(Decimal::new(1, 0));
    
    match state.aggregator.get_best_liquidity_route(&symbol, &market_type, &side, quantity).await {
        Ok(route) => Ok(Json(route)),
        Err(_) => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn get_arbitrage_opportunities(
    State(state): State<EnhancedAppState>,
) -> Result<Json<Vec<CrossExchangeArbitrage>>, StatusCode> {
    match state.aggregator.get_arbitrage_opportunities().await {
        Ok(opportunities) => Ok(Json(opportunities)),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn get_smart_routes(
    State(state): State<EnhancedAppState>,
) -> Result<Json<HashMap<String, SmartOrderRoute>>, StatusCode> {
    match state.aggregator.get_smart_routes().await {
        Ok(routes) => Ok(Json(routes)),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

pub async fn get_futures_market(
    Path(symbol): Path<String>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<FuturesMarket>, StatusCode> {
    match state.aggregator.connectors.get("binance") {
        Some(connector) => {
            match connector.get_futures_market(&symbol).await {
                Ok(market) => Ok(Json(market)),
                Err(_) => Err(StatusCode::NOT_FOUND),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn get_options_market(
    Path(symbol): Path<String>,
    State(state): State<EnhancedAppState>,
) -> Result<Json<OptionsMarket>, StatusCode> {
    match state.aggregator.connectors.get("binance") {
        Some(connector) => {
            match connector.get_options_market(&symbol).await {
                Ok(market) => Ok(Json(market)),
                Err(_) => Err(StatusCode::NOT_FOUND),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

pub async fn health_check() -> Json<Value> {
    Json(json!({
        "status": "healthy",
        "timestamp": Utc::now().to_rfc3339(),
        "service": "enhanced-liquidity-aggregator",
        "version": "2.0.0",
        "features": [
            "multi-exchange-liquidity",
            "cross-market-support",
            "smart-order-routing",
            "arbitrage-detection",
            "real-time-aggregation"
        ]
    }))
}

// Main function
#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::init();
    
    let config = EnhancedConfig::from_env();
    let aggregator = Arc::new(EnhancedLiquidityAggregator::new(&config).await?);
    
    // Define symbols by market type for comprehensive coverage
    let mut symbols_by_market = HashMap::new();
    
    // Spot market symbols
    symbols_by_market.insert("spot".to_string(), vec![
        "BTCUSDT".to_string(),
        "ETHUSDT".to_string(),
        "BNBUSDT".to_string(),
        "ADAUSDT".to_string(),
        "DOTUSDT".to_string(),
        "XRPUSDT".to_string(),
        "LTCUSDT".to_string(),
        "LINKUSDT".to_string(),
        "BCHUSDT".to_string(),
        "XLMUSDT".to_string(),
        "UNIUSDT".to_string(),
        "ATOMUSDT".to_string(),
        "VETUSDT".to_string(),
        "FILUSDT".to_string(),
        "TRXUSDT".to_string(),
        "ETCUSDT".to_string(),
        "XMRUSDT".to_string(),
        "ALGOUSDT".to_string(),
        "DASHUSDT".to_string(),
        "ZECUSDT".to_string(),
    ]);
    
    // Futures market symbols
    symbols_by_market.insert("futures".to_string(), vec![
        "BTCUSDT".to_string(),
        "ETHUSDT".to_string(),
        "BNBUSDT".to_string(),
        "ADAUSDT".to_string(),
        "DOTUSDT".to_string(),
        "XRPUSDT".to_string(),
        "LTCUSDT".to_string(),
        "LINKUSDT".to_string(),
        "BCHUSDT".to_string(),
        "XLMUSDT".to_string(),
    ]);
    
    // Margin market symbols
    symbols_by_market.insert("margin".to_string(), vec![
        "BTCUSDT".to_string(),
        "ETHUSDT".to_string(),
        "BNBUSDT".to_string(),
        "ADAUSDT".to_string(),
        "DOTUSDT".to_string(),
    ]);
    
    // ETF market symbols
    symbols_by_market.insert("etf".to_string(), vec![
        "BTCUPUSDT".to_string(),
        "BTCDOWNUSDT".to_string(),
        "ETHUPUSDT".to_string(),
        "ETHDOWNUSDT".to_string(),
        "BNBUPUSDT".to_string(),
        "BNBDOWNUSDT".to_string(),
    ]);
    
    info!("Starting enhanced liquidity aggregation for {} market types", symbols_by_market.len());
    aggregator.start_aggregation(symbols_by_market).await?;
    
    let app_state = EnhancedAppState { aggregator };
    
    // Build enhanced API router
    let app = Router::new()
        // Enhanced liquidity endpoints
        .route("/api/v2/orderbook/:symbol/:market_type", get(get_enhanced_order_book))
        .route("/api/v2/liquidity/:symbol/:market_type", get(get_enhanced_liquidity_metrics))
        .route("/api/v2/depth/:symbol/:market_type", get(get_market_depth))
        .route("/api/v2/route/:symbol/:market_type", get(get_best_liquidity_route))
        .route("/api/v2/arbitrage", get(get_arbitrage_opportunities))
        .route("/api/v2/routes", get(get_smart_routes))
        
        // Market-specific endpoints
        .route("/api/v2/futures/:symbol", get(get_futures_market))
        .route("/api/v2/options/:symbol", get(get_options_market))
        .route("/api/v2/margin/:symbol", get(get_margin_market))
        .route("/api/v2/etf/:symbol", get(get_etf_market))
        
        // Health check
        .route("/health", get(health_check))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive())
        )
        .with_state(app_state);
    
    info!("Starting Enhanced TigerEx Multi-Exchange Liquidity Aggregator on port 8089");
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8089").await?;
    axum::serve(listener, app).await?;
    
    Ok(())
}