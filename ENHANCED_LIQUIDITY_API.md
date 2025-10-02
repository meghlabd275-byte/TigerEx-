# 🌊 TigerEx Enhanced Liquidity Aggregator API Documentation

## Overview

The Enhanced Liquidity Aggregator provides comprehensive multi-exchange liquidity data across all market types (spot, futures, margin, ETF, options, derivatives) with real-time aggregation, smart order routing, and arbitrage detection capabilities.

## Base URL
```
https://api.tigerex.com/v2
```

## Authentication
Most endpoints require API key authentication via header:
```
Authorization: Bearer YOUR_API_KEY
```

## Market Types Supported
- **spot**: Spot trading markets
- **futures**: Futures and perpetual contracts
- **margin**: Margin/isolated margin trading
- **etf**: ETF and leveraged tokens
- **options**: Options contracts
- **derivatives**: All derivative products

## Exchanges Integrated
- Binance (Spot, Futures, Margin, ETF, Options)
- OKX (Spot, Futures, Margin, Options)
- Bybit (Spot, Futures, Options)
- KuCoin (Spot, Futures, Margin)
- MEXC (Spot, Futures)
- BitMart (Spot, Futures, Margin)
- CoinW (Spot, Futures)
- Bitget (Spot, Futures)

---

## 📊 Core Liquidity Endpoints

### Get Aggregated Order Book
Get real-time aggregated order book across all exchanges for a specific symbol and market type.

**Endpoint:** `GET /orderbook/{symbol}/{market_type}`

**Parameters:**
- `symbol` (string): Trading pair symbol (e.g., "BTCUSDT")
- `market_type` (string): Market type (spot, futures, margin, etc.)

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "market_type": "spot",
  "exchange": "aggregated",
  "bids": [
    {
      "price": "50000.00",
      "quantity": "1.5",
      "timestamp": "2024-01-01T12:00:00Z",
      "exchange": "binance",
      "is_from_dex": false,
      "pool_address": null
    }
  ],
  "asks": [
    {
      "price": "50001.00",
      "quantity": "2.0",
      "timestamp": "2024-01-01T12:00:00Z",
      "exchange": "okx",
      "is_from_dex": false,
      "pool_address": null
    }
  ],
  "best_bid": "50000.00",
  "best_ask": "50001.00",
  "spread": "1.00",
  "spread_bps": "2.00",
  "total_bid_volume": "150.5",
  "total_ask_volume": "200.3",
  "timestamp": "2024-01-01T12:00:00Z",
  "latency_ms": 45,
  "is_stale": false
}
```

### Get Liquidity Metrics
Get comprehensive liquidity metrics for a specific symbol and market type.

**Endpoint:** `GET /liquidity/{symbol}/{market_type}`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "market_type": "spot",
  "total_liquidity_usd": "15000000.00",
  "bid_liquidity_usd": "7000000.00",
  "ask_liquidity_usd": "8000000.00",
  "spread_bps": "2.00",
  "depth_1_percent": "500000.00",
  "depth_5_percent": "2500000.00",
  "volume_24h": "1500000000.00",
  "price_impact_1k": "0.05",
  "price_impact_10k": "0.25",
  "price_impact_100k": "1.20",
  "sources": {
    "binance": {
      "exchange": "binance",
      "liquidity_usd": "8000000.00",
      "volume_24h": "800000000.00",
      "spread_bps": "1.80",
      "uptime_percentage": "99.00",
      "latency_ms": 45,
      "market_types": ["spot", "futures", "margin"]
    },
    "okx": {
      "exchange": "okx",
      "liquidity_usd": "4000000.00",
      "volume_24h": "400000000.00",
      "spread_bps": "2.20",
      "uptime_percentage": "99.00",
      "latency_ms": 60,
      "market_types": ["spot", "futures", "margin", "options"]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Get Market Depth
Get detailed market depth analysis at different price levels.

**Endpoint:** `GET /depth/{symbol}/{market_type}`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "market_type": "spot",
  "depth_levels": [
    {
      "percentage": 1.0,
      "bid_depth": "100000.00",
      "ask_depth": "120000.00",
      "total_depth": "220000.00",
      "price_range": ["49500.00", "50500.00"]
    },
    {
      "percentage": 2.0,
      "bid_depth": "250000.00",
      "ask_depth": "280000.00",
      "total_depth": "530000.00",
      "price_range": ["49000.00", "51000.00"]
    }
  ],
  "total_depth_usd": "750000.00",
  "average_price": "50000.00",
  "price_impact": "0.30",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Get Best Liquidity Route
Get the optimal routing for executing an order across multiple exchanges.

**Endpoint:** `GET /route/{symbol}/{market_type}?side=BUY&quantity=1.5`

**Parameters:**
- `side` (string): Order side (BUY/SELL)
- `quantity` (decimal): Order quantity

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "market_type": "spot",
  "side": "BUY",
  "quantity": "1.5",
  "routes": [
    {
      "exchange": "binance",
      "market_type": "spot",
      "quantity": "0.8",
      "price": "50000.00",
      "fee": "40.00",
      "is_dex": false,
      "pool_address": null,
      "estimated_slippage": "0.005"
    },
    {
      "exchange": "okx",
      "market_type": "spot",
      "quantity": "0.7",
      "price": "50001.00",
      "fee": "35.00",
      "is_dex": false,
      "pool_address": null,
      "estimated_slippage": "0.005"
    }
  ],
  "total_price": "75000.50",
  "average_price": "50000.33",
  "price_impact": "0.15",
  "estimated_slippage": "0.005",
  "gas_cost": null,
  "execution_time_ms": 150,
  "exchanges_used": ["binance", "okx"],
  "is_optimal": true
}
```

---

## 🔄 Arbitrage Detection

### Get Arbitrage Opportunities
Get real-time arbitrage opportunities across exchanges.

**Endpoint:** `GET /arbitrage`

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "BTCUSDT",
    "market_type": "spot",
    "buy_exchange": "binance",
    "sell_exchange": "okx",
    "buy_price": "50000.00",
    "sell_price": "50100.00",
    "profit_percentage": "0.20",
    "profit_usd": "150.00",
    "max_quantity": "1.5",
    "confidence_score": "85.00",
    "execution_time_ms": 100,
    "gas_cost": "25.00",
    "net_profit": "125.00",
    "timestamp": "2024-01-01T12:00:00Z"
  }
]
```

---

## 🧠 Smart Order Routing

### Get Smart Routes
Get all available smart order routes.

**Endpoint:** `GET /routes`

**Response:**
```json
{
  "BTCUSDT:spot": {
    "symbol": "BTCUSDT",
    "market_type": "spot",
    "side": "BUY",
    "quantity": "1.0",
    "routes": [...],
    "total_price": "50000.00",
    "average_price": "50000.00",
    "price_impact": "0.10",
    "estimated_slippage": "0.005",
    "exchanges_used": ["binance", "okx"],
    "is_optimal": true
  }
}
```

---

## 📈 Market-Specific Endpoints

### Get Futures Market Data
Get detailed futures market information.

**Endpoint:** `GET /futures/{symbol}`

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "contract_type": "perpetual",
  "underlying": "BTC",
  "settlement_currency": "USDT",
  "contract_size": "1",
  "tick_size": "0.01",
  "maker_fee_rate": "0.0002",
  "taker_fee_rate": "0.0004",
  "funding_rate": "0.0001",
  "next_funding_time": "2024-01-01T16:00:00Z",
  "open_interest": "150000.5",
  "volume_24h": "2500000000.00",
  "price_change_24h": "500.00",
  "high_24h": "51000.00",
  "low_24h": "49500.00"
}
```

### Get Options Market Data
Get detailed options market information.

**Endpoint:** `GET /options/{symbol}`

**Response:**
```json
{
  "symbol": "BTC-50000-C",
  "underlying": "BTC",
  "option_type": "CALL",
  "strike_price": "50000.00",
  "expiry_date": "2024-01-15T08:00:00Z",
  "settlement_currency": "USDT",
  "contract_size": "1",
  "tick_size": "0.01",
  "implied_volatility": "0.45",
  "delta": "0.52",
  "gamma": "0.0001",
  "theta": "-0.02",
  "vega": "0.18",
  "open_interest": "1500.5",
  "volume_24h": "250.3"
}
```

---

## ⚡ WebSocket Real-time Data

### Subscribe to Real-time Market Data
WebSocket endpoint for real-time market data updates.

**WebSocket URL:** `wss://api.tigerex.com/v2/ws`

**Subscribe Message:**
```json
{
  "op": "subscribe",
  "args": [
    {
      "channel": "orderbook",
      "symbol": "BTCUSDT",
      "market_type": "spot"
    }
  ]
}
```

**Update Message:**
```json
{
  "channel": "orderbook",
  "data": {
    "symbol": "BTCUSDT",
    "market_type": "spot",
    "bids": [...],
    "asks": [...],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

---

## 🔧 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Invalid symbol provided",
    "details": "Symbol must be in format BASEQUOTE (e.g., BTCUSDT)"
  }
}
```

### Common Error Codes
- `INVALID_SYMBOL`: Invalid trading pair symbol
- `UNSUPPORTED_MARKET_TYPE`: Market type not supported
- `EXCHANGE_UNAVAILABLE`: Exchange temporarily unavailable
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `INSUFFICIENT_LIQUIDITY`: Not enough liquidity for requested quantity

---

## 📊 Performance Metrics

### Latency Targets
- **Order Book Updates**: < 100ms
- **Liquidity Metrics**: < 200ms
- **Smart Route Calculation**: < 500ms
- **Arbitrage Detection**: < 1s

### Throughput
- **Order Book Requests**: 10,000+ per second
- **Liquidity Metrics**: 5,000+ per second
- **Route Calculations**: 1,000+ per second

### Availability
- **Uptime Target**: 99.9%
- **Failover Time**: < 5 seconds
- **Data Freshness**: < 100ms

---

## 🔒 Security Features

### Rate Limiting
- **Standard**: 100 requests per second per API key
- **Premium**: 500 requests per second per API key
- **Enterprise**: 2000+ requests per second per API key

### Authentication
- API key authentication required
- Request signing for sensitive operations
- IP whitelisting available
- SSL/TLS encryption for all communications

### Data Protection
- No storage of API credentials
- Encrypted data transmission
- Secure WebSocket connections
- Audit logging for all requests

---

## 🚀 Deployment

### Docker Deployment
```bash
docker run -d \
  -p 8089:8089 \
  -e BINANCE_API_KEY=your_key \
  -e OKX_API_KEY=your_key \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  tigerex/enhanced-liquidity-aggregator:latest
```

### Environment Variables
```bash
# Exchange API Keys
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET=your_binance_secret
OKX_API_KEY=your_okx_key
OKX_SECRET=your_okx_secret
OKX_PASSPHRASE=your_okx_passphrase

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/tigerex
REDIS_URL=redis://host:6379

# Performance Settings
UPDATE_INTERVAL_MS=100
ORDER_BOOK_DEPTH=100
MAX_LATENCY_MS=500
```

---

## 📚 Additional Resources

### SDKs and Libraries
- **JavaScript/TypeScript**: `@tigerex/liquidity-sdk`
- **Python**: `tigerex-liquidity`
- **Rust**: `tigerex-liquidity-rs`
- **Go**: `github.com/tigerex/liquidity-go`

### Examples and Tutorials
- [Quick Start Guide](https://docs.tigerex.com/liquidity/quickstart)
- [Advanced Usage](https://docs.tigerex.com/liquidity/advanced)
- [Integration Examples](https://github.com/tigerex/liquidity-examples)

### Support
- **Documentation**: https://docs.tigerex.com/liquidity
- **GitHub Issues**: https://github.com/tigerex/TigerEx-/issues
- **Community**: https://discord.gg/tigerex
- **Email**: support@tigerex.com

---

**Last Updated:** October 2, 2025  
**API Version:** 2.0.0  
**Status:** Production Ready 🚀