# 📚 TigerEx API Documentation

**Complete REST API Reference for TigerEx Trading Platform**

## 🌐 **API Overview**

- **Base URL**: `https://api.tigerex.com/v1`
- **Authentication**: JWT Bearer Tokens
- **Rate Limiting**: 1000 requests/minute per user
- **Data Format**: JSON
- **Status Codes**: Standard HTTP codes

**Last Updated**: November 14, 2024  
**Version**: v12.0.0

---

## 🔑 **Authentication**

### Generate API Token
```http
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
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "role": "trader"
    }
  }
}
```

### Use Token in Requests
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📊 **Market Data API**

### Get Market Overview
```http
GET /markets
```

**Response:**
```json
{
  "success": true,
  "data": {
    "markets": [
      {
        "symbol": "BTC/USDT",
        "name": "Bitcoin",
        "price": 67850.25,
        "change_24h": 1250.00,
        "change_percent_24h": 1.87,
        "volume_24h": 1250000000,
        "market_cap": 1320000000000,
        "high_24h": 68900.00,
        "low_24h": 66500.00,
        "is_positive": true,
        "sparkline": [66500, 66800, 67200, 66900, 67400, 67100, 67850]
      }
    ],
    "timestamp": "2024-11-14T10:30:00Z"
  }
}
```

### Get Specific Market Data
```http
GET /markets/{symbol}
```

**Parameters:**
- `symbol` (string): Trading pair symbol (e.g., BTC/USDT)

### Get Order Book
```http
GET /markets/{symbol}/orderbook
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTC/USDT",
    "bids": [
      {"price": 67845.50, "amount": 0.1254, "total": 8508.92},
      {"price": 67845.25, "amount": 0.2341, "total": 15879.16}
    ],
    "asks": [
      {"price": 67846.00, "amount": 0.2345, "total": 15908.37},
      {"price": 67846.25, "amount": 0.1234, "total": 8376.64}
    ],
    "timestamp": "2024-11-14T10:30:00Z"
  }
}
```

### Get Recent Trades
```http
GET /markets/{symbol}/trades
```

**Query Parameters:**
- `limit` (integer, optional): Number of trades to return (default: 50, max: 1000)

---

## 💼 **Trading API**

### Place Order
```http
POST /orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "side": "buy",
  "type": "limit",
  "amount": "0.01",
  "price": "67000.00",
  "leverage": "1"
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
    "amount": "0.01",
    "price": "67000.00",
    "status": "open",
    "created_at": "2024-11-14T10:30:00Z",
    "filled": "0.0000",
    "remaining": "0.0100"
  }
}
```

### Cancel Order
```http
DELETE /orders/{order_id}
Authorization: Bearer {token}
```

### Get Open Orders
```http
GET /orders?status=open
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (string): Order status (open, filled, canceled, partially_filled)
- `symbol` (string, optional): Filter by trading pair
- `limit` (integer, optional): Number of orders to return

### Get Order History
```http
GET /orders/history
Authorization: Bearer {token}
```

### Get Trade History
```http
GET /trades
Authorization: Bearer {token}
```

---

## 💳 **Portfolio API**

### Get Account Balance
```http
GET /account/balance
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "balances": [
      {
        "asset": "BTC",
        "free": "0.0523",
        "locked": "0.0000",
        "total": "0.0523",
        "usd_value": "3548.12"
      },
      {
        "asset": "USDT",
        "free": "10000.00",
        "locked": "500.00",
        "total": "10500.00",
        "usd_value": "10500.00"
      }
    ],
    "total_value_usd": "14048.12",
    "total_value_btc": "0.2070"
  }
}
```

### Get Portfolio Overview
```http
GET /account/portfolio
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_value": "14048.12",
    "today_pnl": "125.50",
    "today_pnl_percent": "0.90",
    "assets": [
      {
        "symbol": "BTC",
        "name": "Bitcoin",
        "balance": "0.0523",
        "usd_value": "3548.12",
        "today_pnl": "67.80",
        "today_pnl_percent": "1.95",
        "avg_price": "65000.00",
        "current_price": "67850.25"
      }
    ]
  }
}
```

### Get Transaction History
```http
GET /account/transactions
Authorization: Bearer {token}
```

**Query Parameters:**
- `type` (string): Transaction type (deposit, withdrawal, trade, fee)
- `limit` (integer): Number of transactions to return
- `offset` (integer): Pagination offset

---

## 🏛️ **Admin API**

> **Note**: Admin endpoints require admin role privileges

### Get Platform Statistics
```http
GET /admin/stats
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 15420,
    "active_traders": 3247,
    "total_volume_24h": "125400000",
    "revenue_24h": "42350",
    "pending_verifications": 23,
    "system_status": "operational",
    "uptime": "99.99"
  }
}
```

### Get User Management
```http
GET /admin/users
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `status` (string): Filter by user status
- `role` (string): Filter by user role
- `limit` (integer): Pagination limit

### Update User Status
```http
PUT /admin/users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "active",
  "role": "vip_trader",
  "kyc_status": "verified"
}
```

### Get Trading Configuration
```http
GET /admin/config/trading
Authorization: Bearer {admin_token}
```

### Update Trading Fees
```http
PUT /admin/config/fees
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "default_maker_fee": "0.10",
  "default_taker_fee": "0.10",
  "vip_tiers": [
    {
      "level": "VIP 1",
      "maker_fee": "0.08",
      "taker_fee": "0.10",
      "volume_threshold": "50"
    }
  ]
}
```

---

## 🔧 **System API**

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-11-14T10:30:00Z",
    "services": {
      "database": "healthy",
      "redis": "healthy",
      "api": "healthy"
    },
    "version": "v12.0.0",
    "uptime": "15d 8h 30m"
  }
}
```

### Get System Status
```http
GET /status
```

### Get API Limits
```http
GET /limits
Authorization: Bearer {token}
```

---

## 🔒 **Security API**

### Enable 2FA
```http
POST /security/2fa/enable
Authorization: Bearer {token}
Content-Type: application/json

{
  "password": "current_password"
}
```

### Verify 2FA
```http
POST /security/2fa/verify
Authorization: Bearer {token}
Content-Type: application/json

{
  "code": "123456"
}
```

### Get API Keys
```http
GET /security/api-keys
Authorization: Bearer {token}
```

### Create API Key
```http
POST /security/api-keys
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Trading Bot",
  "permissions": ["read", "trade"],
  "ip_whitelist": ["192.168.1.100"]
}
```

---

## 📈 **WebSocket API**

### Connect to WebSocket
```javascript
const ws = new WebSocket('wss://api.tigerex.com/ws');

// Authenticate
ws.send(JSON.stringify({
  type: 'auth',
  token: 'your_jwt_token'
}));

// Subscribe to market data
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'market',
  symbol: 'BTC/USDT'
}));
```

### WebSocket Channels

#### Market Data
```json
{
  "type": "subscribe",
  "channel": "market",
  "symbol": "BTC/USDT"
}
```

#### Order Book Updates
```json
{
  "type": "subscribe",
  "channel": "orderbook",
  "symbol": "BTC/USDT"
}
```

#### User Trades
```json
{
  "type": "subscribe",
  "channel": "trades"
}
```

#### Account Updates
```json
{
  "type": "subscribe",
  "channel": "account"
}
```

---

## 🚨 **Error Handling**

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_ORDER",
    "message": "Order amount is too small",
    "details": {
      "min_amount": "0.001",
      "provided_amount": "0.0005"
    }
  },
  "timestamp": "2024-11-14T10:30:00Z"
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `INVALID_ORDER` | 400 | Order validation failed |
| `INSUFFICIENT_BALANCE` | 400 | Not enough balance |
| `MARKET_CLOSED` | 400 | Market is not open |

---

## 📝 **Rate Limiting**

### Rate Limits by Endpoint
| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| `/markets/*` | 100 requests/minute | 1 minute |
| `/orders` | 50 requests/minute | 1 minute |
| `/account/*` | 30 requests/minute | 1 minute |
| `/admin/*` | 20 requests/minute | 1 minute |

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699998600
```

---

## 🔄 **Pagination**

### Pagination Parameters
- `limit` (integer): Number of items per page (default: 20, max: 100)
- `offset` (integer): Number of items to skip (default: 0)

### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 154,
      "has_more": true
    }
  }
}
```

---

## 🧪 **Testing the API**

### Using curl
```bash
# Health check
curl https://api.tigerex.com/health

# Get markets
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.tigerex.com/v1/markets

# Place order
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"symbol":"BTC/USDT","side":"buy","type":"market","amount":"0.01"}' \
     https://api.tigerex.com/v1/orders
```

### Using JavaScript
```javascript
// Fetch markets
const response = await fetch('https://api.tigerex.com/v1/markets');
const data = await response.json();

// Place order
const orderResponse = await fetch('https://api.tigerex.com/v1/orders', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symbol: 'BTC/USDT',
    side: 'buy',
    type: 'market',
    amount: '0.01'
  })
});
```

### Using Python
```python
import requests

# Get markets
response = requests.get('https://api.tigerex.com/v1/markets')
markets = response.json()

# Place order
headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}
order_data = {
    'symbol': 'BTC/USDT',
    'side': 'buy',
    'type': 'market',
    'amount': '0.01'
}
response = requests.post(
    'https://api.tigerex.com/v1/orders',
    headers=headers,
    json=order_data
)
```

---

## 🔧 **SDKs and Libraries**

### Official SDKs
- **Python**: `pip install tigerex-python`
- **JavaScript**: `npm install tigerex-js`
- **PHP**: `composer require tigerex/php`
- **Go**: `go get github.com/tigerex/go-sdk`

### Community Libraries
- **Rust**: Available on crates.io
- **C#**: Available on NuGet
- **Java**: Available on Maven Central

---

## 📞 **Support**

### Getting Help
- **Documentation**: https://docs.tigerex.com
- **API Status**: https://status.tigerex.com
- **Support Email**: api-support@tigerex.com
- **Developer Community**: https://community.tigerex.com
- **GitHub Issues**: https://github.com/meghlabd275-byte/TigerEx-/issues

### Reporting Issues
When reporting API issues, please include:
- Request URL and method
- Request headers and body
- Response received
- Timestamp of the request
- Your API key (truncated)

---

## 📋 **Changelog**

### v12.0.0 (November 2024)
- ✅ Added modern trading interface endpoints
- ✅ Enhanced portfolio management API
- ✅ Improved admin dashboard endpoints
- ✅ Added real-time WebSocket streams
- ✅ Enhanced security features

### v11.0.0 (October 2024)
- ✅ Multi-tenant API support
- ✅ Advanced analytics endpoints
- ✅ Enhanced user management
- ✅ Institutional trading features

### v10.0.0 (September 2024)
- ✅ Initial API release
- ✅ Basic trading functionality
- ✅ User authentication
- ✅ Market data endpoints

---

## 🏆 **Best Practices**

### Performance Tips
1. **Use WebSocket** for real-time data
2. **Batch requests** when possible
3. **Cache market data** locally
4. **Use appropriate rate limits**
5. **Handle errors gracefully**

### Security Recommendations
1. **Never expose API keys** in client-side code
2. **Use HTTPS** for all requests
3. **Validate all inputs** before sending
4. **Implement proper authentication**
5. **Monitor API usage** for anomalies

### Trading Guidelines
1. **Use limit orders** for better price control
2. **Set stop-loss** orders for risk management
3. **Check market depth** before large orders
4. **Monitor position sizes** carefully
5. **Keep API keys secure** and rotate regularly

---

## 🚀 **Getting Started**

1. **Create Account**: Sign up at https://tigerex.com
2. **Generate API Key**: Get API credentials from dashboard
3. **Test Connection**: Use health check endpoint
4. **Start Trading**: Place your first order via API
5. **Monitor**: Use WebSocket for real-time updates

---

**🎯 Ready to build amazing trading applications with TigerEx API!**

*API Version: v12.0.0 | Last Updated: November 14, 2024*