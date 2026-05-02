# TigerEx API Complete Reference

## Authentication

### Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600,
  "user_id": "user123"
}
```

### Refresh Token

```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Register

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "trader123"
}
```

---

## Engine API

### Place Order

```bash
POST /engine/order
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user123",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "price": 45000.00,
  "quantity": 0.5,
  "time_in_force": "GTC"
}
```

**Response:**
```json
{
  "order_id": "ORD_ABC123DEF",
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "price": 45000.00,
  "quantity": 0.5,
  "filled": 0.0,
  "status": "open",
  "created_at": "2024-05-02T10:00:00Z"
}
```

### Get Order

```bash
GET /engine/order/ORD_ABC123DEF
Authorization: Bearer <token>
```

**Response:**
```json
{
  "order_id": "ORD_ABC123DEF",
  "symbol": "BTC/USDT",
  "side": "buy",
  "price": 45000.00,
  "quantity": 0.5,
  "filled": 0.5,
  "status": "filled",
  "created_at": "2024-05-02T10:00:00Z",
  "updated_at": "2024-05-02T10:01:30Z"
}
```

### Cancel Order

```bash
DELETE /engine/order/ORD_ABC123DEF
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "order_id": "ORD_ABC123DEF",
  "status": "cancelled"
}
```

### List Orders

```bash
GET /engine/orders?user_id=user123&status=open&symbol=BTC/USDT
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "order_id": "ORD_ABC123DEF",
    "symbol": "BTC/USDT",
    "side": "buy",
    "price": 45000.00,
    "quantity": 0.5,
    "filled": 0.0,
    "status": "open"
  }
]
```

### Order Book

```bash
GET /engine/book/BTC/USDT?levels=10
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "bids": [
    [44990.00, 2.5],
    [44985.00, 1.8],
    [44980.00, 3.2],
    [44975.00, 0.5],
    [44970.00, 2.1]
  ],
  "asks": [
    [45010.00, 1.5],
    [45015.00, 2.0],
    [45020.00, 4.5],
    [45025.00, 1.2],
    [45030.00, 3.0]
  ]
}
```

### Get Balance

```bash
GET /engine/balance/user123
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "user123",
  "account_id": "ACC_001",
  "balances": {
    "USDT": {
      "available": 50000.00,
      "locked": 5000.00
    },
    "BTC": {
      "available": 1.5,
      "locked": 0.25
    }
  }
}
```

### Deposit

```bash
POST /engine/deposit
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user123",
  "asset": "USDT",
  "amount": 10000.00,
  "tx_hash": "0x1234567890abcdef"
}
```

**Response:**
```json
{
  "deposit_id": "DEP_ABC123",
  "user_id": "user123",
  "asset": "USDT",
  "amount": 10000.00,
  "status": "confirmed",
  "confirmed_at": "2024-05-02T10:05:00Z"
}
```

### Withdraw

```bash
POST /engine/withdraw
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user123",
  "asset": "USDT",
  "amount": 5000.00,
  "to_address": "0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5"
}
```

**Response:**
```json
{
  "withdrawal_id": "WDR_ABC123",
  "user_id": "user123",
  "asset": "USDT",
  "amount": 5000.00,
  "fee": 5.00,
  "to_address": "0x742d...",
  "status": "pending"
}
```

---

## Price API

### Get Ticker

```bash
GET /price/ticker/BTC/USDT
```

**Response:**
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

### Get All Tickers

```bash
GET /price/tickers
```

**Response:**
```json
{
  "BTC/USDT": {
    "last": 45000.00,
    "change_24h": 2.5
  },
  "ETH/USDT": {
    "last": 2800.00,
    "change_24h": 1.8
  }
}
```

### Price History

```bash
GET /price/history/BTC/USDT?interval=1h&limit=24
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2024-05-02T10:00:00Z",
      "open": 44900.00,
      "high": 45100.00,
      "low": 44850.00,
      "close": 45000.00,
      "volume": 1250.5
    }
  ]
}
```

---

## Wallet API

### Create Custodial Wallet

```bash
POST /wallet/create/custodial
Content-Type: application/json

{
  "user_id": "user123",
  "chain": "ethereum"
}
```

**Response:**
```json
{
  "wallet_id": "CUST_ABC123",
  "address": "0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5",
  "chain": "ethereum",
  "type": "custodial",
  "status": "active",
  "created_at": "2024-05-02T10:00:00Z"
}
```

### Create Non-Custodial Wallet

```bash
POST /wallet/create/non-custodial
Content-Type: application/json

{
  "user_id": "user123",
  "chain": "ethereum"
}
```

**Response:**
```json
{
  "wallet_id": "NONCUST_ABC123",
  "address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0",
  "chain": "ethereum",
  "type": "non_custodial",
  "status": "active",
  "created_at": "2024-05-02T10:00:00Z"
}
```

### Import Wallet

```bash
POST /wallet/import
Content-Type: application/json

{
  "user_id": "user123",
  "private_key": "0xabcdef123456...",
  "chain": "ethereum"
}
```

### Get Wallets

```bash
GET /wallet/list/user123
```

**Response:**
```json
[
  {
    "wallet_id": "CUST_ABC123",
    "address": "0x742d...",
    "chain": "ethereum",
    "type": "custodial"
  },
  {
    "wallet_id": "NONCUST_DEF456",
    "address": "0x8AC7...",
    "chain": "bsc",
    "type": "non_custodial"
  }
]
```

### Get Balance

```bash
GET /wallet/balance/CUST_ABC123
```

**Response:**
```json
{
  "wallet_id": "CUST_ABC123",
  "address": "0x742d...",
  "chain": "ethereum",
  "balances": {
    "ETH": {
      "balance": 1.25,
      "on_chain": true
    },
    "USDC": {
      "balance": 5000.00,
      "usd_value": 5000.00
    }
  }
}
```

### Send Transaction

```bash
POST /wallet/send
Content-Type: application/json

{
  "wallet_id": "NONCUST_ABC123",
  "to_address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0",
  "amount": 0.5,
  "asset": "ETH"
}
```

**Response:**
```json
{
  "tx_hash": "0x1234567890abcdef...",
  "from": "0x742d...",
  "to": "0x8AC7...",
  "amount": 0.5,
  "asset": "ETH",
  "status": "signed_ready_to_broadcast"
}
```

### Sign Message

```bash
POST /wallet/sign
Content-Type: application/json

{
  "wallet_id": "NONCUST_ABC123",
  "message": "Hello TigerEx"
}
```

**Response:**
```json
{
  "wallet_id": "NONCUST_ABC123",
  "message": "Hello TigerEx",
  "signature": "0xabcdef123456...",
  "address": "0x742d..."
}
```

### List Chains

```bash
GET /wallet/chains
```

**Response:**
```json
[
  {"id": "ethereum", "name": "Ethereum", "type": "evm", "chain_id": 1},
  {"id": "bsc", "name": "BNB Chain", "type": "evm", "chain_id": 56},
  {"id": "polygon", "name": "Polygon", "type": "evm", "chain_id": 137},
  {"id": "arbitrum", "name": "Arbitrum", "type": "evm", "chain_id": 42161},
  {"id": "solana", "name": "Solana", "type": "non_evm", "symbol": "SOL"}
]
```

---

## Exchange API

### Create Account

```bash
POST /exchange/account
Content-Type: application/json

{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "account_id": "EXC_ABC123",
  "user_id": "user123",
  "status": "active"
}
```

### Place Order

```bash
POST /exchange/order
Content-Type: application/json

{
  "user_id": "user123",
  "pair": "TIG/USDC",
  "side": "buy",
  "type": "limit",
  "price": 2.50,
  "quantity": 100
}
```

**Response:**
```json
{
  "order_id": "ORD_TIG001",
  "pair": "TIG/USDC",
  "side": "buy",
  "price": 2.50,
  "quantity": 100,
  "status": "open"
}
```

### Get Order Book

```bash
GET /exchange/book/TIG:USDC
```

**Response:**
```json
{
  "pair": "TIG:USDC",
  "bids": [
    [2.48, 1000],
    [2.47, 500],
    [2.46, 250]
  ],
  "asks": [
    [2.52, 800],
    [2.53, 1200],
    [2.54, 500]
  ]
}
```

### Add Liquidity

```bash
POST /exchange/liquidity/add
Content-Type: application/json

{
  "user_id": "user123",
  "pair": "TIG/USDC",
  "amount_a": 1000,
  "amount_b": 2500
}
```

**Response:**
```json
{
  "liquidity_id": "LIQ_ABC123",
  "pair": "TIG/USDC",
  "token_a": "TIG",
  "amount_a": 1000,
  "token_b": "USDC",
  "amount_b": 2500,
  "shares": 1000,
  "timestamp": "2024-05-02T10:00:00Z"
}
```

---

## Blockchain API

### Create Account

```bash
POST /blockchain/account
Content-Type: application/json

{
  "private_key": "0x..."
}
```

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5",
  "private_key_hash": "..."
}
```

### Get Balance

```bash
GET /blockchain/balance/0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5
```

**Response:**
```json
{
  "address": "0x742d...",
  "balance": "1000000000000000000",
  "balance_eth": 1.0
}
```

### Send Transaction

```bash
POST /blockchain/send
Content-Type: application/json

{
  "from": "0x742d...",
  "to": "0x8AC7...",
  "value": 1000000000000000000,
  "gas_price": 20000000000
}
```

**Response:**
```json
{
  "tx_hash": "0x1234567890abcdef...",
  "status": "pending"
}
```

### Get Block

```bash
GET /blockchain/block/12345
```

**Response:**
```json
{
  "number": 12345,
  "hash": "0xabcdef123456...",
  "parentHash": "0x123456abcdef...",
  "timestamp": "2024-05-02T10:00:00Z",
  "transactions": [],
  "gasUsed": 500000,
  "gasLimit": 30000000
}
```

### Get Transaction

```bash
GET /blockchain/tx/0x1234567890abcdef...
```

**Response:**
```json
{
  "hash": "0x1234567890abcdef...",
  "from": "0x742d...",
  "to": "0x8AC7...",
  "value": "1000000000000000000",
  "gas": 21000,
  "status": "confirmed",
  "block": 12345
}
```

---

## Error Codes

| Code | Message |
|------|---------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 429 | Rate Limited - Too many requests |
| 500 | Internal Error - Server error |
| 503 | Service Unavailable - Service down |

**Error Response Format:**
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

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /engine/order | 50/min |
| /wallet/send | 10/min |
| /price/* | 100/min |
| /exchange/order | 30/min |

---

## WebSocket

### Connect

```
wss://api.tigerex.com/ws
```

### Subscribe

```json
{
  "action": "subscribe",
  "channel": "ticker",
  "symbol": "BTC/USDT"
}
```

### Messages

```json
{
  "channel": "ticker",
  "data": {
    "symbol": "BTC/USDT",
    "last": 45000.00,
    "bid": 44990.00,
    "ask": 45010.00,
    "change_24h": 2.5,
    "volume_24h": 125000.00
  }
}
```

### Channels

- `ticker` - Real-time price updates
- `orderbook` - Order book changes (depth)
- `trades` - Trade executions
- `orders` - User's orders