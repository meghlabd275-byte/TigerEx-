# TigerEx Comprehensive API Documentation

## Overview

This document provides comprehensive API documentation for the TigerEx cryptocurrency exchange platform, including all trading types, admin controls, and security features.

## Table of Contents

1. [Authentication](#authentication)
2. [Trading APIs](#trading-apis)
3. [Admin APIs](#admin-apis)
4. [User Management](#user-management)
5. [Security APIs](#security-apis)
6. [WebSocket APIs](#websocket-apis)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

## Authentication

### JWT Authentication

All API requests (except public endpoints) require JWT authentication.

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password",
  "totp_code": "123456"  // Required if 2FA is enabled
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user123",
    "role": "verified_user",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 900
  }
}
```

### API Key Authentication

For programmatic access, API keys can be used with HMAC signature authentication.

#### Generate API Key

```http
POST /api/v1/user/api-keys
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Trading Bot",
  "permissions": ["trade_spot", "trade_futures", "read_balance"],
  "ip_whitelist": ["192.168.1.100"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "api_key": "tigerex_abc123def456...",
    "api_secret": "xyz789uvw456...",
    "permissions": ["trade_spot", "trade_futures", "read_balance"]
  }
}
```

#### Using API Keys

Include the following headers:
```http
X-API-Key: tigerex_abc123def456...
X-API-Signature: <hmac_sha256_signature>
X-API-Timestamp: <unix_timestamp>
```

## Trading APIs

### Spot Trading

#### Get Market Data

```http
GET /api/v1/spot/ticker
```

**Response:**
```json
{
  "success": true,
  "data": {
    "BTC/USDT": {
      "symbol": "BTC/USDT",
      "price": "45000.50",
      "change_24h": "2.5",
      "volume_24h": "1234567890",
      "high_24h": "46000.00",
      "low_24h": "44000.00"
    }
  }
}
```

#### Place Order

```http
POST /api/v1/spot/order
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "quantity": "0.1",
  "price": "44000.00",
  "time_in_force": "GTC"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order_id": "order_123456",
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "limit",
    "quantity": "0.1",
    "price": "44000.00",
    "status": "open",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Cancel Order

```http
DELETE /api/v1/spot/order/{order_id}
Authorization: Bearer <access_token>
```

#### Get Order History

```http
GET /api/v1/spot/orders?symbol=BTC/USDT&status=completed&limit=50&offset=0
Authorization: Bearer <access_token>
```

### Futures Trading

#### Get Futures Market Data

```http
GET /api/v1/futures/ticker
```

**Response:**
```json
{
  "success": true,
  "data": {
    "BTCUSDT_PERPETUAL": {
      "symbol": "BTCUSDT_PERPETUAL",
      "mark_price": "45000.50",
      "index_price": "45000.00",
      "funding_rate": "0.0001",
      "next_funding_time": "2024-01-01T16:00:00Z",
      "open_interest": "1000000",
      "volume_24h": "5000000000"
    }
  }
}
```

#### Place Futures Order

```http
POST /api/v1/futures/order
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "BTCUSDT_PERPETUAL",
  "side": "buy",
  "type": "limit",
  "quantity": "1",
  "price": "44000.00",
  "leverage": "10",
  "margin_type": "isolated",
  "reduce_only": false
}
```

#### Set Leverage

```http
POST /api/v1/futures/leverage
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "BTCUSDT_PERPETUAL",
  "leverage": "20"
}
```

#### Get Position Information

```http
GET /api/v1/futures/positions
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTCUSDT_PERPETUAL",
      "position_side": "long",
      "size": "1.5",
      "entry_price": "44500.00",
      "mark_price": "45000.50",
      "unrealized_pnl": "82.50",
      "percentage_pnl": "0.18",
      "leverage": "10",
      "margin": "6675.00",
      "liquidation_price": "40000.00"
    }
  ]
}
```

### Margin Trading

#### Get Margin Account

```http
GET /api/v1/margin/account
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user123",
    "borrowed": {
      "BTC": "0.5",
      "USDT": "10000"
    },
    "interest": {
      "BTC": "0.001",
      "USDT": "10.5"
    },
    "net_asset": "50000.00",
    "margin_ratio": "0.15"
  }
}
```

#### Borrow Asset

```http
POST /api/v1/margin/borrow
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "asset": "USDT",
  "amount": "1000"
}
```

#### Repay Asset

```http
POST /api/v1/margin/repay
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "asset": "USDT",
  "amount": "1000"
}
```

### Grid Trading

#### Create Grid Bot

```http
POST /api/v1/grid/bot
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "upper_price": "50000.00",
  "lower_price": "40000.00",
  "grid_count": 20,
  "investment_amount": "10000",
  "mode": "arithmetic"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "bot_id": "grid_bot_123",
    "symbol": "BTC/USDT",
    "status": "running",
    "upper_price": "50000.00",
    "lower_price": "40000.00",
    "grid_count": 20,
    "investment_amount": "10000",
    "current_profit": "125.50",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Get Grid Bots

```http
GET /api/v1/grid/bots
Authorization: Bearer <access_token>
```

#### Stop Grid Bot

```http
POST /api/v1/grid/bot/{bot_id}/stop
Authorization: Bearer <access_token>
```

### Copy Trading

#### Get Master Traders

```http
GET /api/v1/copy/masters
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "master_id": "master_123",
      "nickname": "ProTrader",
      "followers": 1250,
      "total_profit": "15.5",
      "profit_30d": "2.3",
      "max_drawdown": "5.2",
      "copy_fee": "0.1"
    }
  ]
}
```

#### Follow Master Trader

```http
POST /api/v1/copy/follow
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "master_id": "master_123",
  "copy_amount": "1000",
  "max_position_size": "5000",
  "stop_loss": "10"
}
```

#### Get Copy Positions

```http
GET /api/v1/copy/positions
Authorization: Bearer <access_token>
```

### Options Trading

#### Get Options Chain

```http
GET /api/v1/options/chain?underlying=BTC&expiry=2024-01-31
```

**Response:**
```json
{
  "success": true,
  "data": {
    "underlying": "BTC",
    "expiry": "2024-01-31",
    "spots": [
      {
        "strike": "45000",
        "call": {
          "bid": "1250.50",
          "ask": "1255.00",
          "iv": "0.65"
        },
        "put": {
          "bid": "980.25",
          "ask": "985.00",
          "iv": "0.63"
        }
      }
    ]
  }
}
```

#### Buy Option

```http
POST /api/v1/options/buy
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "underlying": "BTC",
  "expiry": "2024-01-31",
  "strike": "45000",
  "type": "call",
  "quantity": "1",
  "price": "1255.00"
}
```

#### Get Options Positions

```http
GET /api/v1/options/positions
Authorization: Bearer <access_token>
```

## Admin APIs

### Trading Control

#### Get System Overview

```http
GET /api/v1/admin/trading/overview
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trading_types": {
      "spot": {
        "status": "active",
        "enabled": true,
        "volume_24h": "1250000000",
        "orders_24h": 45000,
        "paused_symbols": []
      },
      "futures": {
        "status": "active",
        "enabled": true,
        "volume_24h": "2500000000",
        "orders_24h": 67000,
        "paused_symbols": ["DOGE/USDT"]
      }
    },
    "summary": {
      "total_trading_types": 7,
      "active_trading_types": 6,
      "paused_trading_types": 1
    }
  }
}
```

#### Control Trading System

```http
POST /api/v1/admin/trading/control
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "action": "pause",
  "trading_type": "spot",
  "symbol": "BTC/USDT",
  "reason": "Market volatility"
}
```

#### Get Trading Configuration

```http
GET /api/v1/admin/trading/config/{trading_type}
Authorization: Bearer <admin_access_token>
```

#### Update Trading Configuration

```http
PUT /api/v1/admin/trading/config/{trading_type}
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "enabled": true,
  "max_leverage": 20.0,
  "max_position_size": 1000000.0,
  "circuit_breaker_threshold": 0.1
}
```

### Contract Management

#### Create Contract

```http
POST /api/v1/admin/trading/contracts
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "contract_id": "BTCUSDT_PERPETUAL_V2",
  "trading_type": "future_perpetual",
  "symbol": "BTCUSDT_PERPETUAL",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "leverage_limit": 125.0,
  "funding_rate": 0.0001,
  "tick_size": 0.01
}
```

#### Get Contracts

```http
GET /api/v1/admin/trading/contracts?trading_type=future_perpetual&status=active
Authorization: Bearer <admin_access_token>
```

#### Update Contract

```http
PUT /api/v1/admin/trading/contracts/{contract_id}
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "status": "paused",
  "leverage_limit": 100.0
}
```

#### Delete Contract

```http
DELETE /api/v1/admin/trading/contracts/{contract_id}
Authorization: Bearer <admin_access_token>
```

### User Management

#### Get User Limits

```http
GET /api/v1/admin/trading/users/{user_id}/limits
Authorization: Bearer <admin_access_token>
```

#### Set User Limits

```http
POST /api/v1/admin/trading/users/{user_id}/limits
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "trading_type": "futures",
  "max_leverage": 10.0,
  "max_position_size": 500000.0,
  "daily_volume_limit": 5000000.0
}
```

#### Get User Positions

```http
GET /api/v1/admin/trading/users/{user_id}/positions
Authorization: Bearer <admin_access_token>
```

#### Close All User Positions

```http
POST /api/v1/admin/trading/users/{user_id}/close-all-positions
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "trading_type": "futures",
  "reason": "Risk management"
}
```

### Order Management

#### Get All Orders

```http
GET /api/v1/admin/trading/orders?trading_type=spot&status=open&limit=100
Authorization: Bearer <admin_access_token>
```

#### Cancel Order (Admin)

```http
DELETE /api/v1/admin/trading/orders/{order_id}
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "reason": "Suspicious activity detected"
}
```

#### Cancel All Orders

```http
POST /api/v1/admin/trading/orders/cancel-all
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "trading_type": "spot",
  "symbol": "BTC/USDT",
  "reason": "Emergency market halt"
}
```

### Risk Management

#### Get Risk Metrics

```http
GET /api/v1/admin/trading/risk/metrics?trading_type=futures
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trading_type": "futures",
    "metrics": {
      "total_exposure": "500000000",
      "open_interest": "1000000000",
      "insurance_fund_balance": "50000000",
      "margin_ratio": 0.12,
      "leverage_ratio": 8.5,
      "liquidation_risk": "medium"
    }
  }
}
```

#### Trigger Circuit Breaker

```http
POST /api/v1/admin/trading/risk/circuit-breaker
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "trading_type": "futures",
  "reason": "Extreme market volatility",
  "duration_minutes": 60
}
```

### Audit and Analytics

#### Get Audit Log

```http
GET /api/v1/admin/trading/audit/log?limit=100&action_type=pause_trading
Authorization: Bearer <admin_access_token>
```

#### Get Analytics Overview

```http
GET /api/v1/admin/trading/analytics/overview?trading_type=all&period_hours=24
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-02T00:00:00Z",
      "hours": 24
    },
    "overview": {
      "total_volume": "12500000000",
      "total_trades": 125000,
      "active_users": 45000,
      "total_orders": 250000,
      "trading_fee_collected": "12500000"
    },
    "by_trading_type": {
      "spot": {"volume": "1250000000", "trades": 45000},
      "futures": {"volume": "7500000000", "trades": 60000}
    }
  }
}
```

## Security APIs

### Two-Factor Authentication

#### Enable 2FA

```http
POST /api/v1/user/2fa/enable
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "backup_codes": ["12345678", "87654321", ...]
  }
}
```

#### Verify 2FA

```http
POST /api/v1/user/2fa/verify
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "code": "123456"
}
```

### Password Security

#### Change Password

```http
POST /api/v1/user/password/change
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

#### Check Password Strength

```http
POST /api/v1/user/password/strength
Content-Type: application/json

{
  "password": "test_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "score": 4,
    "strength": "strong",
    "errors": []
  }
}
```

### Session Management

#### Get Active Sessions

```http
GET /api/v1/user/sessions
Authorization: Bearer <access_token>
```

#### Revoke Session

```http
DELETE /api/v1/user/sessions/{session_id}
Authorization: Bearer <access_token>
```

## WebSocket APIs

### Market Data WebSocket

Connect to: `wss://api.tigerex.com/ws/market`

#### Subscribe to Ticker

```json
{
  "method": "subscribe",
  "params": {
    "channel": "ticker",
    "symbol": "BTC/USDT"
  },
  "id": 1
}
```

#### Subscribe to Order Book

```json
{
  "method": "subscribe",
  "params": {
    "channel": "orderbook",
    "symbol": "BTC/USDT",
    "depth": 20
  },
  "id": 2
}
```

#### Subscribe to Trades

```json
{
  "method": "subscribe",
  "params": {
    "channel": "trades",
    "symbol": "BTC/USDT"
  },
  "id": 3
}
```

### User Data WebSocket

Connect to: `wss://api.tigerex.com/ws/user`

#### Authentication

```json
{
  "method": "login",
  "params": {
    "token": "jwt_access_token"
  },
  "id": 1
}
```

#### Subscribe to Orders

```json
{
  "method": "subscribe",
  "params": {
    "channel": "orders"
  },
  "id": 2
}
```

#### Subscribe to Balances

```json
{
  "method": "subscribe",
  "params": {
    "channel": "balances"
  },
  "id": 3
}
```

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_ORDER",
    "message": "Order size is below minimum",
    "details": {
      "minimum_size": "0.001",
      "provided_size": "0.0001"
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_CREDENTIALS | Invalid username or password |
| INSUFFICIENT_BALANCE | Not enough balance for operation |
| INVALID_ORDER | Order parameters are invalid |
| RATE_LIMIT_EXCEEDED | API rate limit exceeded |
| PERMISSION_DENIED | User lacks required permission |
| MAINTENANCE_MODE | System is under maintenance |
| MARKET_CLOSED | Market is currently closed |
| LIQUIDATION_RISK | Position is at risk of liquidation |
| INVALID_SYMBOL | Trading symbol does not exist |

### HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limiting

### Rate Limits by Endpoint

| Endpoint | Limit | Window |
|----------|-------|--------|
| Public market data | 100 requests/min | 1 minute |
| Authenticated trading | 100 requests/min | 1 minute |
| Admin operations | 60 requests/min | 1 minute |
| API key requests | 1000 requests/min | 1 minute |

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

### Official SDKs

- **Python**: `pip install tigerex-python`
- **JavaScript**: `npm install tigerex-js`
- **Go**: `go get github.com/tigerex/go-sdk`
- **Java**: Available on Maven Central

### Example Usage

#### Python SDK

```python
from tigerex import TigerExClient

client = TigerExClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Place order
order = client.place_order(
    symbol="BTC/USDT",
    side="buy",
    type="limit",
    quantity=0.1,
    price=44000
)

print(order)
```

#### JavaScript SDK

```javascript
const { TigerExClient } = require('tigerex-js');

const client = new TigerExClient({
  apiKey: 'your_api_key',
  apiSecret: 'your_api_secret'
});

// Place order
client.placeOrder({
  symbol: 'BTC/USDT',
  side: 'buy',
  type: 'limit',
  quantity: 0.1,
  price: 44000
}).then(order => {
  console.log(order);
});
```

## Support

- **API Documentation**: https://docs.tigerex.com
- **Status Page**: https://status.tigerex.com
- **Developer Community**: https://community.tigerex.com
- **Support Email**: api-support@tigerex.com

## Changelog

### v4.0.0 (2024-01-01)
- Added comprehensive admin controls
- Implemented all trading types
- Enhanced security features
- Multi-platform support
- WebSocket real-time data
- Advanced risk management