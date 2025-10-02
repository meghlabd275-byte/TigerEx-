/*
Enhanced OKX Exchange Connector
Supports all market types: spot, futures, margin, options
*/

use crate::*;
use reqwest::Client;
use serde_json::Value;
use hmac::{Hmac, Mac};
use sha2::Sha256;
use base64::{Engine as _, engine::general_purpose};
use chrono::Utc;

type HmacSha256 = Hmac<Sha256>;

pub struct EnhancedOKXConnector {
    client: Client,
    api_key: Option<String>,
    secret: Option<String>,
    passphrase: Option<String>,
    testnet: bool,
}

impl EnhancedOKXConnector {
    pub fn new(api_key: Option<String>, secret: Option<String>, passphrase: Option<String>, testnet: bool) -> Self {
        Self {
            client: Client::new(),
            api_key,
            secret,
            passphrase,
            testnet,
        }
    }
    
    fn get_base_url(&self) -> String {
        if self.testnet {
            "https://www.okx.com".to_string()
        } else {
            "https://www.okx.com".to_string()
        }
    }
    
    fn generate_signature(&self, method: &str, path: &str, timestamp: &str, body: &str) -> Result<String> {
        if let (Some(secret), Some(passphrase)) = (&self.secret, &self.passphrase) {
            let message = format!("{}{}{}{}", timestamp, method, path, body);
            let mut mac = HmacSha256::new_from_slice(secret.as_bytes())?;
            mac.update(message.as_bytes());
            let result = mac.finalize();
            let signature = general_purpose::STANDARD.encode(result.into_bytes());
            Ok(signature)
        } else {
            Err(anyhow!("Missing API credentials for OKX"))
        }
    }
    
    async fn make_request(&self, method: &str, endpoint: &str, params: Option<Value>) -> Result<Value> {
        let timestamp = Utc::now().to_rfc3339();
        let url = format!("{}{}", self.get_base_url(), endpoint);
        
        let mut request = self.client.request(
            method.parse().unwrap(),
            &url
        );
        
        // Add API credentials if available
        if let Some(api_key) = &self.api_key {
            request = request.header("OK-ACCESS-KEY", api_key);
        }
        
        if let (Some(secret), Some(passphrase)) = (&self.secret, &self.passphrase) {
            let body = params.as_ref().map(|p| p.to_string()).unwrap_or_default();
            let signature = self.generate_signature(method, endpoint, &timestamp, &body)?;
            
            request = request
                .header("OK-ACCESS-SIGN", signature)
                .header("OK-ACCESS-TIMESTAMP", timestamp)
                .header("OK-ACCESS-PASSPHRASE", passphrase);
        }
        
        if let Some(params) = params {
            if method == "GET" {
                for (key, value) in params.as_object().unwrap() {
                    request = request.query(&[(key, value)]);
                }
            } else {
                request = request.json(&params);
            }
        }
        
        let response = request.send().await?;
        let data: Value = response.json().await?;
        
        if let Some(code) = data["code"].as_str() {
            if code != "0" {
                return Err(anyhow!("OKX API error: {}", data["msg"].as_str().unwrap_or("Unknown error")));
            }
        }
        
        Ok(data)
    }
}

#[async_trait]
impl EnhancedExchangeConnector for EnhancedOKXConnector {
    async fn get_order_book(&self, symbol: &str, market_type: &str) -> Result<EnhancedOrderBook> {
        let endpoint = match market_type {
            "spot" => format!("/api/v5/market/books?instId={}&sz=100", symbol),
            "futures" => format!("/api/v5/market/books?instId={}-SWAP&sz=100", symbol),
            "margin" => format!("/api/v5/margin/isolated/order-book?instId={}&sz=100", symbol),
            "options" => format!("/api/v5/public/option-ticker?instId={}", symbol),
            _ => return Err(anyhow!("Unsupported market type: {}", market_type)),
        };
        
        let data = self.make_request("GET", &endpoint, None).await?;
        
        let mut bids = Vec::new();
        let mut asks = Vec::new();
        
        if let Some(result) = data["data"].as_array() {
            if let Some(book) = result.first() {
                if let Some(bid_array) = book["bids"].as_array() {
                    for bid in bid_array {
                        if let (Some(price), Some(qty)) = (bid[0].as_str(), bid[1].as_str()) {
                            bids.push(OrderBookLevel {
                                price: price.parse()?,
                                quantity: qty.parse()?,
                                timestamp: Utc::now(),
                                exchange: "okx".to_string(),
                                is_from_dex: false,
                                pool_address: None,
                            });
                        }
                    }
                }
                
                if let Some(ask_array) = book["asks"].as_array() {
                    for ask in ask_array {
                        if let (Some(price), Some(qty)) = (ask[0].as_str(), ask[1].as_str()) {
                            asks.push(OrderBookLevel {
                                price: price.parse()?,
                                quantity: qty.parse()?,
                                timestamp: Utc::now(),
                                exchange: "okx".to_string(),
                                is_from_dex: false,
                                pool_address: None,
                            });
                        }
                    }
                }
            }
        }
        
        let best_bid = bids.first().map(|b| b.price);
        let best_ask = asks.first().map(|a| a.price);
        let spread = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some(ask - bid),
            _ => None,
        };
        
        let spread_bps = match (best_bid, best_ask) {
            (Some(bid), Some(ask)) => Some((ask - bid) / bid * Decimal::new(10000, 0)),
            _ => None,
        };
        
        Ok(EnhancedOrderBook {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            exchange: "okx".to_string(),
            bids,
            asks,
            best_bid,
            best_ask,
            spread,
            spread_bps,
            total_bid_volume: bids.iter().map(|b| b.quantity).sum(),
            total_ask_volume: asks.iter().map(|a| a.quantity).sum(),
            timestamp: Utc::now(),
            latency_ms: 60,
            is_stale: false,
        })
    }
    
    async fn get_liquidity_metrics(&self, symbol: &str, market_type: &str) -> Result<LiquidityMetrics> {
        let order_book = self.get_order_book(symbol, market_type).await?;
        
        let depth_1_percent = self.calculate_depth_at_percentage(&order_book, Decimal::new(1, 2));
        let depth_5_percent = self.calculate_depth_at_percentage(&order_book, Decimal::new(5, 2));
        let price_impact_1k = self.calculate_price_impact(&order_book, Decimal::new(1000, 0));
        let price_impact_10k = self.calculate_price_impact(&order_book, Decimal::new(10000, 0));
        let price_impact_100k = self.calculate_price_impact(&order_book, Decimal::new(100000, 0));
        
        let volume_24h = self.get_24h_volume(symbol, market_type).await?;
        
        let mut sources = HashMap::new();
        sources.insert("okx".to_string(), ExchangeLiquidityMetrics {
            exchange: "okx".to_string(),
            liquidity_usd: (order_book.total_bid_volume + order_book.total_ask_volume) * 
                          order_book.best_bid.unwrap_or_default(),
            volume_24h,
            spread_bps: order_book.spread_bps.unwrap_or_default(),
            uptime_percentage: Decimal::new(99, 2),
            latency_ms: 60,
            market_types: vec!["spot".to_string(), "futures".to_string(), "margin".to_string(), "options".to_string()],
        });
        
        Ok(LiquidityMetrics {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            total_liquidity_usd: (order_book.total_bid_volume + order_book.total_ask_volume) * 
                                order_book.best_bid.unwrap_or_default(),
            bid_liquidity_usd: order_book.total_bid_volume * order_book.best_bid.unwrap_or_default(),
            ask_liquidity_usd: order_book.total_ask_volume * order_book.best_ask.unwrap_or_default(),
            spread_bps: order_book.spread_bps.unwrap_or_default(),
            depth_1_percent,
            depth_5_percent,
            volume_24h,
            price_impact_1k,
            price_impact_10k,
            price_impact_100k,
            sources,
            timestamp: Utc::now(),
        })
    }
    
    async fn get_market_depth(&self, symbol: &str, market_type: &str) -> Result<MarketDepth> {
        let order_book = self.get_order_book(symbol, market_type).await?;
        
        let depth_levels = vec![
            self.calculate_depth_level(&order_book, Decimal::new(1, 2)),   // 1%
            self.calculate_depth_level(&order_book, Decimal::new(2, 2)),   // 2%
            self.calculate_depth_level(&order_book, Decimal::new(5, 2)),   // 5%
            self.calculate_depth_level(&order_book, Decimal::new(10, 2)),  // 10%
        ];
        
        let total_depth_usd = depth_levels.iter().map(|d| d.total_depth).sum();
        let average_price = order_book.best_bid.unwrap_or_default() + order_book.best_ask.unwrap_or_default() / Decimal::new(2, 0);
        let price_impact = self.calculate_price_impact(&order_book, Decimal::new(10000, 0));
        
        Ok(MarketDepth {
            symbol: symbol.to_string(),
            market_type: market_type.to_string(),
            depth_levels,
            total_depth_usd,
            average_price,
            price_impact,
            timestamp: Utc::now(),
        })
    }
    
    async fn get_futures_market(&self, symbol: &str) -> Result<FuturesMarket> {
        let endpoint = format!("/api/v5/public/futures-ticker?instId={}-SWAP", symbol);
        let data = self.make_request("GET", &endpoint, None).await?;
        
        if let Some(result) = data["data"].as_array() {
            if let Some(ticker) = result.first() {
                return Ok(FuturesMarket {
                    symbol: symbol.to_string(),
                    contract_type: "perpetual".to_string(),
                    underlying: symbol.replace("USDT", ""),
                    settlement_currency: "USDT".to_string(),
                    contract_size: Decimal::new(1, 0),
                    tick_size: Decimal::new(1, 2),
                    maker_fee_rate: Decimal::new(2, 4),
                    taker_fee_rate: Decimal::new(5, 4),
                    funding_rate: ticker["fundingRate"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    next_funding_time: DateTime::parse_from_rfc3339(ticker["nextFundingTime"].as_str().unwrap_or("2024-01-01T00:00:00Z")).unwrap_or(Utc::now()),
                    open_interest: ticker["oi"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    volume_24h: ticker["vol24h"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    price_change_24h: ticker["pxChange24h"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    high_24h: ticker["high24h"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    low_24h: ticker["low24h"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                });
            }
        }
        
        Err(anyhow!("Failed to get futures market data from OKX"))
    }
    
    async fn get_options_market(&self, symbol: &str) -> Result<OptionsMarket> {
        let endpoint = format!("/api/v5/public/opt-ticker?instId={}", symbol);
        let data = self.make_request("GET", &endpoint, None).await?;
        
        if let Some(result) = data["data"].as_array() {
            if let Some(ticker) = result.first() {
                return Ok(OptionsMarket {
                    symbol: symbol.to_string(),
                    underlying: ticker["uly"].as_str().unwrap_or("").to_string(),
                    option_type: if symbol.contains("C") { "CALL".to_string() } else { "PUT".to_string() },
                    strike_price: ticker["strike"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    expiry_date: DateTime::parse_from_rfc3339(ticker["expTime"].as_str().unwrap_or("2024-01-01T00:00:00Z")).unwrap_or(Utc::now()),
                    settlement_currency: "USDT".to_string(),
                    contract_size: Decimal::new(1, 0),
                    tick_size: Decimal::new(1, 2),
                    implied_volatility: ticker["vol"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    delta: ticker["delta"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    gamma: ticker["gamma"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    theta: ticker["theta"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    vega: ticker["vega"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    open_interest: ticker["oi"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                    volume_24h: ticker["vol24h"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                });
            }
        }
        
        Err(anyhow!("Failed to get options market data from OKX"))
    }
    
    async fn get_margin_market(&self, symbol: &str) -> Result<MarginMarket> {
        let endpoint = format!("/api/v5/margin/isolated-marginData?instId={}", symbol);
        let data = self.make_request("GET", &endpoint, None).await?;
        
        if let Some(result) = data["data"].as_array() {
            if let Some(margin_data) = result.first() {
                return Ok(MarginMarket {
                    symbol: symbol.to_string(),
                    base_currency: symbol.replace("USDT", ""),
                    quote_currency: "USDT".to_string(),
                    max_leverage: margin_data["maxLever"].as_str().unwrap_or("10").parse().unwrap_or(Decimal::new(10, 0)),
                    isolated_margin_available: true,
                    cross_margin_available: true,
                    margin_call_ratio: margin_data["mrCall"].as_str().unwrap_or("1.25").parse().unwrap_or(Decimal::new(125, 2)),
                    liquidation_ratio: margin_data["mrLiq"].as_str().unwrap_or("1.10").parse().unwrap_or(Decimal::new(110, 2)),
                    daily_interest_rate: margin_data["interestRate"].as_str().unwrap_or("0.0001").parse().unwrap_or(Decimal::new(1, 4)),
                    borrow_limit: margin_data["maxLoan"].as_str().unwrap_or("100000").parse().unwrap_or(Decimal::new(100000, 0)),
                    total_borrowed: margin_data["usedLoan"].as_str().unwrap_or("0").parse().unwrap_or(Decimal::ZERO),
                });
            }
        }
        
        Err(anyhow!("Failed to get margin market data from OKX"))
    }
    
    async fn get_etf_market(&self, symbol: &str) -> Result<ETFMarket> {
        // OKX doesn't have traditional ETFs, but has index products
        // This would be implemented based on their index product API
        Err(anyhow!("ETF markets not directly supported on OKX"))
    }
    
    async fn get_supported_markets(&self) -> Result<Vec<MarketType>> {
        Ok(vec![
            MarketType {
                market_type: "spot".to_string(),
                is_enabled: true,
                api_endpoints: vec![
                    "/api/v5/market".to_string(),
                ],
            },
            MarketType {
                market_type: "futures".to_string(),
                is_enabled: true,
                api_endpoints: vec![
                    "/api/v5/public".to_string(),
                ],
            },
            MarketType {
                market_type: "margin".to_string(),
                is_enabled: true,
                api_endpoints: vec![
                    "/api/v5/margin".to_string(),
                ],
            },
            MarketType {
                market_type: "options".to_string(),
                is_enabled: true,
                api_endpoints: vec![
                    "/api/v5/public".to_string(),
                ],
            },
        ])
    }
    
    async fn get_24h_volume(&self, symbol: &str, market_type: &str) -> Result<Decimal> {
        let endpoint = match market_type {
            "spot" => format!("/api/v5/market/ticker?instId={}", symbol),
            "futures" => format!("/api/v5/public/futures-ticker?instId={}-SWAP", symbol),
            _ => return Err(anyhow!("Unsupported market type for volume: {}", market_type)),
        };
        
        let data = self.make_request("GET", &endpoint, None).await?;
        
        if let Some(result) = data["data"].as_array() {
            if let Some(ticker) = result.first() {
                if let Some(volume) = ticker["volCcy24h"].as_str() {
                    return Ok(volume.parse()?);
                }
            }
        }
        
        Ok(Decimal::ZERO)
    }
    
    async fn get_ticker(&self, symbol: &str, market_type: &str) -> Result<Value> {
        let endpoint = match market_type {
            "spot" => format!("/api/v5/market/ticker?instId={}", symbol),
            "futures" => format!("/api/v5/public/futures-ticker?instId={}-SWAP", symbol),
            _ => return Err(anyhow!("Unsupported market type for ticker: {}", market_type)),
        };
        
        self.make_request("GET", &endpoint, None).await
    }
    
    async fn subscribe_market_data(&self, symbols: Vec<String>, market_types: Vec<String>) -> Result<()> {
        // WebSocket subscription implementation
        let ws_url = if self.testnet {
            "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
        } else {
            "wss://ws.okx.com:8443/ws/v5/public"
        };
        
        let (ws_stream, _) = connect_async(ws_url).await?;
        let (mut write, mut read) = ws_stream.split();
        
        // Subscribe to market data for all symbols and market types
        for market_type in &market_types {
            for symbol in &symbols {
                let subscribe_msg = json!({
                    "op": "subscribe",
                    "args": [{
                        "channel": "books",
                        "instId": match market_type.as_str() {
                            "futures" => format!("{}-SWAP", symbol),
                            "options" => format!("{}-{}", symbol, if symbol.contains("C") { "C" } else { "P" }),
                            _ => symbol.clone(),
                        }
                    }]
                });
                
                write.send(Message::Text(subscribe_msg.to_string())).await?;
            }
        }
        
        // Handle incoming messages
        tokio::spawn(async move {
            while let Some(msg) = read.next().await {
                match msg {
                    Ok(Message::Text(text)) => {
                        if let Ok(data) = serde_json::from_str::<Value>(&text) {
                            debug!("Received OKX market data update: {:?}", data);
                            // Process the market data update
                        }
                    }
                    Ok(Message::Close(_)) => break,
                    Err(e) => {
                        error!("OKX WebSocket error: {}", e);
                        break;
                    }
                    _ => {}
                }
            }
        });
        
        Ok(())
    }
    
    // Helper methods
    fn calculate_depth_at_percentage(&self, order_book: &EnhancedOrderBook, percentage: Decimal) -> Decimal {
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
    
    fn calculate_price_impact(&self, order_book: &EnhancedOrderBook, trade_size_usd: Decimal) -> Decimal {
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
    
    fn calculate_depth_level(&self, order_book: &EnhancedOrderBook, percentage: Decimal) -> DepthLevel {
        let mid_price = match (order_book.best_bid, order_book.best_ask) {
            (Some(bid), Some(ask)) => (bid + ask) / Decimal::new(2, 0),
            _ => return DepthLevel {
                percentage,
                bid_depth: Decimal::ZERO,
                ask_depth: Decimal::ZERO,
                total_depth: Decimal::ZERO,
                price_range: (Decimal::ZERO, Decimal::ZERO),
            },
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
        
        DepthLevel {
            percentage,
            bid_depth,
            ask_depth,
            total_depth: bid_depth + ask_depth,
            price_range: (lower_bound, upper_bound),
        }
    }
}