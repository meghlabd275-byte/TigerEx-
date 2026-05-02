# TigerEx API Reference

## Base URLs

| Environment | URL |
|-------------|-----|
| Production | https://api.tigerex.com |
| Staging | https://staging-api.tigerex.com |
| Development | http://localhost:5000 |

---

## Authentication

### Headers

All authenticated requests require:

```
Authorization: Bearer <access_token>
Content-Type: application/json
X-User-ID: <user_id>
X-Timestamp: <unix_timestamp>
X-Signature: <signature>
```

### Getting Access Token

```bash
curl -X POST https://api.tigerex.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

---

## Production Engine API

### Base: `/engine`

#### Health Check

```bash
GET /engine/health
```

Response:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": "86400",
  "orders": 1250,
  "trades": 8540
}
```

#### Place Order

```bash
POST /engine/order
{
  "user_id": "user_123",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "price": 45000.00,
  "quantity": 0.5,
  "time_in_force": "GTC"
}
```

Response:

```json
{
  "order_id": "ORD_ABC123DEF",
  "symbol": "BTC/USDT",
  "side": "buy",
  "price": 45000.00,
  "quantity": 0.5,
  "filled": 0.0,
  "status": "open",
  "created_at": "2024-05-02T10:00:00Z"
}
```

#### Get Order

```bash
GET /engine/order/ORD_ABC123DEF
```

#### Cancel Order

```bash
DELETE /engine/order/ORD_ABC123DEF
```

#### Get Order Book

```bash
GET /engine/book/BTC/USDT?levels=10
```

Response:

```json
{
  "symbol": "BTC/USDT",
  "bids": [
    [44990.00, 2.5],
    [44985.00, 1.8],
    [44980.00, 3.2]
  ],
  "asks": [
    [45010.00, 1.5],
    [45015.00, 2.0],
    [45020.00, 4.5]
  ]
}
```

#### Get Trades

```bash
GET /engine/trades?symbol=BTC/USDT&limit=50
```

#### Get Balance

```bash
GET /engine/balance/user_123
```

Response:

```json
{
  "user_id": "user_123",
  "account_id": "ACC_001",
  "balances": {
    "USDT": {"available": 50000.00, "locked": 5000.00},
    "BTC": {"available": 1.5, "locked": 0.25}
  }
}
```

#### Deposit

```bash
POST /engine/deposit
{
  "user_id": "user_123",
  "asset": "USDT",
  "amount": 10000.00,
  "tx_hash": "0x..."
}
```

#### Withdraw

```bash
POST /engine/withdraw
{
  "user_id": "user_123",
  "asset": "USDT",
  "amount": 5000.00,
  "to_address": "0x..."
}
```

---

## Price Sync API

### Base: `/price`

#### Get Ticker

```bash
GET /price/ticker/BTC/USDT
```

Response:

```json
{
  "symbol": "BTC/USDT",
  "last": 45000.00,
  "bid": 44990.00,
  "ask": 45010.00,
  "volume_24h": 125000.00,
  "change_24h": 2.5,
  "high_24h": 45500.00,
  "low_24h": 44200.00,
  "updated_at": "2024-05-02T10:00:00Z"
}
```

#### Get All Tickers

```bash
GET /price/tickers
```

#### Get Price History

```bash
GET /price/history/BTC/USDT?interval=1h&limit=24
```

---

## Wallet API

### Base: `/wallet`

#### Create Custodial Wallet

```bash
POST /wallet/create/custodial
{
  "user_id": "user_123",
  "chain": "ethereum"
}
```

Response:

```json
{
  "wallet_id": "CUST_ABC123",
  "address": "0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5",
  "chain": "ethereum",
  "type": "custodial",
  "status": "active"
}
```

#### Create Non-Custodial Wallet

```bash
POST /wallet/create/non-custodial
{
  "user_id": "user_123",
  "chain": "ethereum"
}
```

#### Import Wallet

```bash
POST /wallet/import
{
  "user_id": "user_123",
  "private_key": "0x...",
  "chain": "ethereum"
}
```

#### Get Wallets

```bash
GET /wallet/list/user_123
```

#### Get Balance

```bash
GET /wallet/balance/CUST_ABC123
```

Response:

```json
{
  "wallet_id": "CUST_ABC123",
  "address": "0x...",
  "chain": "ethereum",
  "balances": {
    "ETH": {"balance": 1.25, "on_chain": true},
    "USDC": {"balance": 5000.00, "usd_value": 5000.00}
  }
}
```

#### Send Transaction

```bash
POST /wallet/send
{
  "wallet_id": "NONCUST_ABC123",
  "to_address": "0x...",
  "amount": 0.5,
  "asset": "ETH"
}
```

#### Sign Message

```bash
POST /wallet/sign
{
  "wallet_id": "NONCUST_ABC123",
  "message": "Hello TigerEx"
}
```

---

## Exchange API

### Base: `/exchange`

#### Create Account

```bash
POST /exchange/account
{
  "user_id": "user_123"
}
```

#### Place Order

```bash
POST /exchange/order
{
  "user_id": "user_123",
  "pair": "TIG/USDC",
  "side": "buy",
  "type": "limit",
  "price": 2.50,
  "quantity": 100
}
```

#### Get Order Book

```bash
GET /exchange/book/TIG:USDC
```

---

## Blockchain API

### Base: `/blockchain`

#### Create Account

```bash
POST /blockchain/account
{
  "private_key": "0x..."
}
```

#### Get Balance

```bash
GET /blockchain/balance/0x...
```

#### Send Transaction

```bash
POST /blockchain/send
{
  "from": "0x...",
  "to": "0x...",
  "value": 1000000000000000000,
  "gas_price": 20000000000
}
```

#### Deploy Contract

```bash
POST /blockchain/deploy
{
  "sender": "0x...",
  "code": "0x60806040..."
}
```

#### Get Block

```bash
GET /blockchain/block/12345
```

#### Get Transaction

```bash
GET /blockchain/tx/0x...
```

---

## Error Codes

| Code | Message |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Error |
| 503 | Service Unavailable |

### Error Response

```json
{
  "error": {
    "code": 400,
    "message": "Invalid order parameters",
    "details": {
      "field": "price",
      "reason": "must be positive"
    }
  }
}
```

---

## WebSocket API

### Endpoints

| Channel | URL |
|---------|-----|
| Order Book | wss://api.tigerex.com/ws/book |
| Trades | wss://api.tigerex.com/ws/trades |
| Ticker | wss://api.tigerex.com/ws/ticker |

### Subscribe

```json
{
  "action": "subscribe",
  "channel": "ticker",
  "symbol": "BTC/USDT"
}
```

### Message Format

```json
{
  "channel": "ticker",
  "data": {
    "symbol": "BTC/USDT",
    "last": 45000.00,
    "change": 2.5
  }
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /engine/order | 50/min |
| /wallet/send | 10/min |
| /price/* | 100/min |

---

## Versioning

API version is specified in the URL:

```
/v1/engine/order
/v1/price/ticker
```

Current version: v1