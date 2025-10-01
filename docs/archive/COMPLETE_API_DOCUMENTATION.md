# TigerEx Platform - Complete API Documentation

## Table of Contents
1. [Admin Panel APIs](#admin-panel-apis)
2. [Payment Gateway API](#payment-gateway-api)
3. [Advanced Trading API](#advanced-trading-api)
4. [DeFi Enhancements API](#defi-enhancements-api)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)

---

## Admin Panel APIs

### 1. Alpha Market Admin API (Port 8115)

#### Base URL
```
http://localhost:8115/api/admin
```

#### Endpoints

**Create Alpha Strategy**
```http
POST /strategies
Content-Type: application/json

{
  "name": "Momentum Strategy",
  "description": "High-frequency momentum trading",
  "strategy_type": "momentum",
  "provider_id": 1,
  "risk_level": "high",
  "min_investment": 1000.0,
  "performance_fee": 20.0,
  "management_fee": 2.0
}

Response: 201 Created
{
  "id": 1,
  "name": "Momentum Strategy",
  "status": "active",
  "created_at": "2025-01-15T10:00:00Z"
}
```

**List Alpha Strategies**
```http
GET /strategies?skip=0&limit=100&strategy_type=momentum

Response: 200 OK
{
  "total": 50,
  "strategies": [...]
}
```

---

### 2. Copy Trading Admin API (Port 8116)

**Create Master Trader**
```http
POST /traders
Content-Type: application/json

{
  "user_id": 123,
  "username": "crypto_master",
  "display_name": "Crypto Master",
  "bio": "10 years trading experience",
  "risk_level": "medium",
  "profit_sharing": 15.0,
  "min_copy_amount": 100.0,
  "max_followers": 1000
}

Response: 201 Created
```

---

## Payment Gateway API (Port 8123)

**Create Deposit**
```http
POST /deposits
Content-Type: application/json

{
  "user_id": 123,
  "provider": "stripe",
  "amount": 1000.0,
  "currency": "USD"
}

Response: 201 Created
{
  "transaction_id": "TXN-ABC123",
  "amount": 1000.0,
  "fee": 25.0,
  "net_amount": 975.0,
  "status": "pending",
  "payment_url": "https://checkout.stripe.com/..."
}
```

---

## Advanced Trading API (Port 8124)

**Create TWAP Order**
```http
POST /orders/twap
Content-Type: application/json

{
  "user_id": 123,
  "symbol": "BTC/USDT",
  "side": "buy",
  "total_quantity": 1.0,
  "duration_minutes": 60,
  "execution_strategy": "balanced"
}

Response: 201 Created
{
  "order_id": "TWAP-ABC123",
  "num_slices": 20,
  "slice_size": 0.05,
  "status": "active"
}
```

---

For complete API documentation, see the full documentation at https://docs.tigerex.com/api