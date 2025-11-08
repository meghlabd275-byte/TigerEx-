# 📚 TigerEx Complete API Documentation v7.0.0

## Table of Contents
- [Authentication](#authentication)
- [Trading APIs](#trading-apis)
- [Admin APIs](#admin-apis)
- [Blockchain APIs](#blockchain-apis)
- [User Management](#user-management)
- [WebSocket Streams](#websocket-streams)

## 🔐 Authentication

### Login Endpoint
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@tigerex.com",
  "password": "secure_password",
  "2fa_code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "admin@tigerex.com",
    "role": "admin",
    "permissions": ["read", "write", "admin"]
  }
}
```

## 📈 Trading APIs

### Spot Trading

#### Create Trading Pair (Admin Only)
```http
POST /api/v1/admin/spot-trading/pairs/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "min_price": 40000,
  "max_price": 50000,
  "tick_size": 0.01,
  "step_size": 0.00001,
  "min_quantity": 0.001,
  "max_quantity": 1000,
  "leverage": 125,
  "maker_fee": 0.0005,
  "taker_fee": 0.001,
  "enable_margin": true,
  "enable_futures": true,
  "enable_options": true,
  "enable_grid": true,
  "enable_copy": true
}
```

**Response:**
```json
{
  "success": true,
  "pair_id": "pair_12345",
  "symbol": "BTC/USDT",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Pause Trading Pair (Admin Only)
```http
PUT /api/v1/admin/spot-trading/pairs/{pair_id}/pause
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Trading pair BTC/USDT paused successfully",
  "status": "paused"
}
```

#### Resume Trading Pair (Admin Only)
```http
PUT /api/v1/admin/spot-trading/pairs/{pair_id}/resume
Authorization: Bearer <admin_token>
```

#### Suspend Trading Pair (Admin Only)
```http
PUT /api/v1/admin/spot-trading/pairs/{pair_id}/suspend
Authorization: Bearer <admin_token>
```

#### Delete Trading Pair (Admin Only)
```http
DELETE /api/v1/admin/spot-trading/pairs/{pair_id}
Authorization: Bearer <admin_token>
```

#### Get All Trading Pairs
```http
GET /api/v1/spot-trading/pairs
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "pairs": [
    {
      "id": "pair_12345",
      "symbol": "BTC/USDT",
      "base_asset": "BTC",
      "quote_asset": "USDT",
      "status": "active",
      "price": 43250.50,
      "change_24h": 2.5,
      "volume_24h": 125000000,
      "leverage": 125,
      "features": {
        "margin": true,
        "futures": true,
        "options": true,
        "grid": true,
        "copy": true
      }
    }
  ]
}
```

### Futures Trading

#### Create Futures Contract (Admin Only)
```http
POST /api/v1/admin/futures-trading/contracts/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "symbol": "BTCUSDT-PERP",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "contract_type": "perpetual",
  "margin_mode": "cross",
  "multiplier": 1.0,
  "leverage": 125,
  "maintenance_margin_rate": 0.005,
  "initial_margin_rate": 0.01,
  "maker_fee": -0.0002,
  "taker_fee": 0.0004,
  "funding_rate": 0.0001,
  "funding_interval": 8,
  "price_band": 0.05,
  "max_order_value": 1000000,
  "max_position_value": 10000000
}
```

#### Get Futures Contracts
```http
GET /api/v1/futures-trading/contracts
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "contracts": [
    {
      "id": "contract_123",
      "symbol": "BTCUSDT-PERP",
      "contract_type": "perpetual",
      "margin_mode": "cross",
      "leverage": 125,
      "funding_rate": 0.0001,
      "open_interest": 250000000,
      "mark_price": 43245.25,
      "index_price": 43250.00,
      "next_funding_time": "2024-01-15T16:00:00Z",
      "status": "active"
    }
  ]
}
```

### Margin Trading

#### Create Margin Pair (Admin Only)
```http
POST /api/v1/admin/margin-trading/pairs/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "margin_mode": "cross",
  "initial_margin_ratio": 0.1,
  "maintenance_margin_ratio": 0.05,
  "max_leverage": 10,
  "borrowing_enabled": true,
  "max_borrow_amount": {"BTC": 100, "USDT": 1000000},
  "interest_rate": {"BTC": 0.02, "USDT": 0.05},
  "liquidation_threshold": 0.9,
  "force_liquidation_threshold": 0.95
}
```

### Options Trading

#### Create Options Contract (Admin Only)
```http
POST /api/v1/admin/options-trading/contracts/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "symbol": "BTC-250119-45000-C",
  "underlying_asset": "BTC",
  "option_type": "call",
  "exercise_style": "european",
  "strike_price": 45000,
  "expiration_date": "2025-01-19",
  "contract_size": 1.0,
  "settlement_type": "cash",
  "pricing_model": "black_scholes",
  "implied_volatility": 0.25,
  "max_open_interest": 1000000,
  "position_limit": 10000
}
```

### Grid Trading

#### Create Grid Bot
```http
POST /api/v1/grid-trading/bots/create
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "pair_symbol": "BTC/USDT",
  "grid_type": "arithmetic",
  "upper_price": 45000,
  "lower_price": 40000,
  "grid_count": 50,
  "total_investment": 10000,
  "profit_per_grid": 0.01,
  "stop_loss_price": 38000,
  "take_profit_price": 50000,
  "ai_optimized": true,
  "dynamic_adjustment": true
}
```

#### Pause Grid Bot (Admin Only)
```http
PUT /api/v1/admin/grid-trading/bots/{bot_id}/pause
Authorization: Bearer <admin_token>
```

#### Get Grid Bots
```http
GET /api/v1/grid-trading/bots
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "bots": [
    {
      "id": "bot_123",
      "pair_symbol": "BTC/USDT",
      "grid_type": "arithmetic",
      "status": "active",
      "total_investment": 10000,
      "current_profit": 450.50,
      "profit_percentage": 4.505,
      "win_rate": 68.5,
      "completed_grids": 125,
      "total_grids": 50,
      "running_time": "72h 35m",
      "ai_optimized": true,
      "risk_level": "medium"
    }
  ]
}
```

### Copy Trading

#### Add Master Trader (Admin Only)
```http
POST /api/v1/admin/copy-trading/masters/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "master_trader_id": "master_001",
  "min_copy_amount": 10,
  "max_copy_amount": 100000,
  "max_followers": 1000,
  "commission_rate": 0.1,
  "allowed_instruments": ["BTC/USDT", "ETH/USDT"],
  "risk_level": "moderate",
  "max_risk_per_trade": 0.02,
  "max_daily_loss": 0.05
}
```

#### Start Copy Trading
```http
POST /api/v1/copy-trading/start
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "master_trader_id": "master_001",
  "copy_mode": "percentage",
  "copy_amount": 1000,
  "copy_percentage": 10,
  "max_copy_per_trade": 1000,
  "max_total_copy": 10000,
  "stop_loss_enabled": true,
  "stop_loss_percentage": 0.1
}
```

#### Get Copy Traders
```http
GET /api/v1/copy-trading/traders
Authorization: Bearer <access_token>
```

## 🔗 Blockchain APIs

### Network Management

#### Add Blockchain Network (Admin Only)
```http
POST /api/v1/admin/blockchain/networks/add
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "network_id": "ethereum",
  "name": "Ethereum Mainnet",
  "chain_id": 1,
  "rpc_url": "https://mainnet.infura.io/v3/...",
  "ws_url": "wss://mainnet.infura.io/ws/v3/...",
  "block_explorer": "https://etherscan.io",
  "gas_token": "ETH",
  "block_time": 12,
  "confirmation_blocks": 12,
  "network_type": "EVM"
}
```

#### Get Blockchain Networks
```http
GET /api/v1/blockchain/networks
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "networks": [
    {
      "id": "ethereum",
      "name": "Ethereum Mainnet",
      "chain_id": 1,
      "status": "active",
      "current_block": 18543210,
      "gas_price": 25.5,
      "supported_tokens": ["ETH", "USDT", "USDC", "WBTC"],
      "network_type": "EVM"
    }
  ]
}
```

### Smart Contract Deployment

#### Deploy Token Contract
```http
POST /api/v1/admin/blockchain/contracts/deploy-token
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "network_id": "ethereum",
  "name": "My Token",
  "symbol": "MTK",
  "decimals": 18,
  "total_supply": "1000000000000000000000000",
  "token_type": "ERC20",
  "mintable": true,
  "burnable": true
}
```

**Response:**
```json
{
  "success": true,
  "contract_address": "0x1234567890123456789012345678901234567890",
  "transaction_hash": "0xabcdef...",
  "deployment_block": 18543210,
  "verified": true
}
```

## 💰 Financial System APIs

### IOU System

#### Create IOU Contract
```http
POST /api/v1/admin/iou/contracts/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "issuer_id": "issuer_001",
  "recipient_id": "recipient_001",
  "iou_type": "payment",
  "amount": 10000,
  "currency": "USDT",
  "maturity_date": "2024-02-15T00:00:00Z",
  "interest_rate": 0.05,
  "collateral_required": false,
  "auto_settlement": true,
  "early_settlement_allowed": true
}
```

#### Settle IOU Contract
```http
POST /api/v1/admin/iou/contracts/{iou_id}/settle
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "settlement_amount": 10000,
  "settlement_type": "full"
}
```

### Virtual Coins

#### Create Virtual Coin
```http
POST /api/v1/admin/virtual-coins/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "symbol": "VTIGER",
  "name": "Virtual Tiger Token",
  "coin_type": "utility",
  "total_supply": "1000000000000000000000000",
  "current_price": 1.25,
  "is_virtual": true,
  "trading_enabled": true,
  "mintable": true,
  "burnable": true,
  "decimals": 18
}
```

#### Add Trading Pair for Virtual Coin
```http
POST /api/v1/admin/virtual-coins/{coin_id}/trading-pairs/add
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "quote_asset": "USDT",
  "min_price": 1.00,
  "max_price": 2.00,
  "tick_size": 0.0001,
  "step_size": 0.01,
  "trading_enabled": true,
  "market_making_enabled": true
}
```

## 👥 User Management

### Get User Profile
```http
GET /api/v1/users/profile
Authorization: Bearer <access_token>
```

### Update User Settings
```http
PUT /api/v1/users/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "trading_preferences": {
    "default_leverage": 10,
    "risk_level": "moderate",
    "auto_confirm_orders": false
  },
  "notification_settings": {
    "email_alerts": true,
    "push_notifications": true,
    "price_alerts": true
  }
}
```

### Get User Portfolio
```http
GET /api/v1/users/portfolio
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "portfolio": {
    "total_value": 125000.50,
    "assets": [
      {
        "symbol": "BTC",
        "balance": 2.5,
        "value": 107562.50,
        "percentage": 86.0
      },
      {
        "symbol": "USDT",
        "balance": 17438.00,
        "value": 17438.00,
        "percentage": 14.0
      }
    ],
    "positions": [
      {
        "symbol": "BTCUSDT-PERP",
        "size": 1.5,
        "side": "long",
        "entry_price": 42000,
        "mark_price": 43245,
        "pnl": 1867.50,
        "leverage": 125
      }
    ]
  }
}
```

## 📊 WebSocket Streams

### Market Data Stream
```javascript
const ws = new WebSocket('wss://api.tigerex.com/ws');

// Subscribe to ticker updates
ws.send(JSON.stringify({
  "method": "subscribe",
  "params": {
    "channel": "ticker",
    "symbol": "BTC/USDT"
  }
}));

// Subscribe to orderbook updates
ws.send(JSON.stringify({
  "method": "subscribe",
  "params": {
    "channel": "orderbook",
    "symbol": "BTC/USDT",
    "depth": 20
  }
}));

// Subscribe to trades
ws.send(JSON.stringify({
  "method": "subscribe",
  "params": {
    "channel": "trades",
    "symbol": "BTC/USDT"
  }
}));
```

### User Data Stream
```javascript
// Authenticate for user data
ws.send(JSON.stringify({
  "method": "login",
  "params": {
    "access_token": "your_access_token"
  }
}));

// Subscribe to account updates
ws.send(JSON.stringify({
  "method": "subscribe",
  "params": {
    "channel": "account"
  }
}));

// Subscribe to order updates
ws.send(JSON.stringify({
  "method": "subscribe",
  "params": {
    "channel": "orders"
  }
}));
```

## 🔧 Error Codes

| Error Code | Description |
|------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Maintenance mode |

## 📝 Rate Limits

| Endpoint Type | Rate Limit | Time Window |
|---------------|------------|-------------|
| Public APIs | 100 requests | 1 minute |
| Private APIs | 60 requests | 1 minute |
| Trading APIs | 20 requests | 1 minute |
| Admin APIs | 30 requests | 1 minute |

## 🌐 SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @tigerex/api-client
```

### Python
```bash
pip install tigerex-python
```

### React Native
```bash
npm install @tigerex/react-native
```

## 📞 Support

For API support and documentation:
- 📧 Email: api-support@tigerex.com
- 💬 Discord: https://discord.gg/tigerex
- 📚 Documentation: https://docs.tigerex.com
- 🐛 Issues: https://github.com/tigerex/api-issues

---

**© 2024 TigerEx Enterprise Trading Platform v7.0.0**
*All rights reserved. Enterprise-grade cryptocurrency exchange platform.*