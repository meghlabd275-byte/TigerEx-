# TigerEx Trading Complete Guide

## Table of Contents
1. Getting Started
2. Trading Interface
3. Order Types
4. Trading Pairs
5. Fees
6. Trading Strategies
7. API Trading
8. Troubleshooting

---

## 1. Getting Started

### Prerequisites

1. **Create Account** - Register at tigerex.com
2. **Verify Email** - Click verification link
3. **Enable 2FA** - Security Settings → Enable 2FA
4. **Deposit Funds** - Go to Wallet → Deposit

### Account Tiers

| Tier | Daily Limit | Features |
|------|------------|----------|
| Unverified | $100 | Basic |
| Level 1 | $1,000 | Higher limits |
| Level 2 | $10,000 | All features |
| Level 3+ | $100,000+ | VIP |

---

## 2. Trading Interface

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  BTC/USDT │ $45,000 │ +2.5% │ Vol: $125M │
├─────────────────────────────────────────────────────────┤
│  Order Book        │  Trading Form      │  My Orders  │
│  Bids    Asks      │  [Buy] [Sell]      │             │
│  44,990  45,010   │  Price: [      ]   │  Order 1   │
│  44,985  45,015   │  Amount: [      ]  │  Order 2   │
│  44,980  45,020   │  Total: $         │             │
│                    │  [Place Order]     │             │
└─────────────────────────────────────────────────────────┘
```

### Using the Interface

1. **Select Pair** - Click dropdown, choose trading pair
2. **Choose Side** - Click Buy (green) or Sell (red)
3. **Enter Price** - For limit orders
4. **Enter Amount** - Quantity to trade
5. **Review Total** - Price × Amount
6. **Place Order** - Click button to submit

---

## 3. Order Types

### Market Orders

Buy or sell immediately at best available price.

```python
# Example: Buy 0.5 BTC at market
order = {
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "market",
    "quantity": 0.5
}
```

**When to use:**
- Need immediate execution
- Don't care about price slippage
- Small orders in liquid markets

### Limit Orders

Set your desired price.

```python
# Example: Buy ETH at $2,500
order = {
    "symbol": "ETH/USDT",
    "side": "buy",
    "type": "limit",
    "price": 2500.00,
    "quantity": 2.0,
    "time_in_force": "GTC"
}
```

**Time-in-Force:**
- **GTC** - Good Till Cancel (default)
- **IOC** - Immediate or Cancel
- **FOK** - Fill or Kill

**When to use:**
- Want specific price
- Patient trading
- Larger orders

### Stop-Loss Orders

Auto-sell when price drops to stop price.

```python
order = {
    "symbol": "BTC/USDT",
    "side": "sell",
    "type": "stop_loss",
    "stop_price": 42000,
    "quantity": 0.5
}
```

**When to use:**
- Limit losses
- Protect profits
- Risk management

### OCO Orders

One-Cancels-Other - place two orders, one cancels the other.

```python
# If price reaches sell target, buy order cancels
# If price drops to stop, sell order triggers
order = {
    "type": "oco",
    "orders": [
        {"side": "buy", "price": 44000, "quantity": 1},
        {"side": "sell", "stop_price": 42000, "quantity": 1}
    ]
}
```

---

## 4. Trading Pairs

### Available Pairs

**USDT Pairs (Most Liquid):**
- BTC/USDT - Bitcoin
- ETH/USDT - Ethereum
- BNB/USDT - BNB
- SOL/USDT - Solana
- MATIC/USDT - Polygon
- AVAX/USDT - Avalanche
- ARB/USDT - Arbitrum

**USDC Pairs:**
- TIG/USDC - TigerEx Token
- BTC/USDC - Bitcoin
- ETH/USDC - Ethereum

### Selecting Pairs

1. Click pair dropdown
2. Search or scroll
3. Click desired pair
4. Interface updates

---

## 5. Fees

### Trading Fees

| Volume (30-day) | Maker | Taker |
|-----------------|-------|-------|
| < $10,000 | 0.10% | 0.20% |
| $10,000+ | 0.08% | 0.18% |
| $100,000+ | 0.05% | 0.15% |
| $1M+ | 0.03% | 0.10% |
| $10M+ | 0.00% | 0.08% |

### Fee Calculation

```python
# Example: Buy $10,000 worth
amount = 10000
taker_fee = 0.002  # 0.2%
fee = amount * taker_fee  # $20

# Net cost: $10,020
```

### Withdrawal Fees

| Asset | Fee |
|-------|-----|
| BTC | 0.0005 BTC |
| ETH | 0.005 ETH |
| USDT | 1 USDT |
| BNB | 0.005 BNB |

---

## 6. Trading Strategies

### Day Trading

Open and close positions within same day.

**Strategy:**
- Monitor charts all day
- Small price movements
- Quick decisions
- Strict stop-loss

**Tips:**
- Use 1-5% stop-loss
- Risk only 1-2% per trade
- Set daily profit target

### Swing Trading

Hold positions for days to weeks.

**Strategy:**
- Identify trends
- Hold through volatility
- Weekly chart analysis

**Tips:**
- Use daily/4hr charts
- Wider stop-loss (5-10%)
- Lower trade frequency

### Scalping

Many small trades, small profits.

**Strategy:**
- Very small profits per trade
- High volume
- Automated tools

**Tips:**
- Must have low fees
- Fast execution critical
- Manage slippage

### Position Sizing

```python
# Risk only 2% per trade
portfolio = 10000
risk_percent = 0.02
risk_amount = portfolio * risk_percent  # $200

# If stop-loss is 5%, position size:
stop_loss_percent = 0.05
position_size = risk_amount / stop_loss_percent  # $4,000
```

---

## 7. API Trading

### REST API Example

```python
import requests
import time

BASE_URL = "https://api.tigerex.com/v1"

# Get access token
auth = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})
token = auth.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Get price
price = requests.get(
    f"{BASE_URL}/price/ticker/BTC/USDT",
    headers=headers
).json()
print(f"BTC: ${price['last']}")

# Place order
order = requests.post(
    f"{BASE_URL}/engine/order",
    headers=headers,
    json={
        "symbol": "BTC/USDT",
        "side": "buy",
        "type": "limit",
        "price": 44000,
        "quantity": 0.1
    }
).json()
print(f"Order: {order['order_id']}")
```

### WebSocket Example

```python
import websocket
import json

ws = websocket.create_connection("wss://api.tigerex.com/ws")

# Subscribe to ticker
subscribe = {
    "action": "subscribe",
    "channel": "ticker",
    "symbol": "BTC/USDT"
}
ws.send(json.dumps(subscribe))

# Listen for updates
while True:
    data = json.loads(ws.recv())
    print(data)
```

### Trading Bot Example

```python
import requests
import time

BASE_URL = "https://api.tigerex.com/v1"
TOKEN = "your_token"

def get_price(symbol):
    r = requests.get(f"{BASE_URL}/price/ticker/{symbol}")
    return r.json()['last']

def place_order(symbol, side, quantity, price=None):
    order = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "type": "market" if not price else "limit"
    }
    if price:
        order["price"] = price
    
    r = requests.post(
        f"{BASE_URL}/engine/order",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json=order
    )
    return r.json()

def trading_bot():
    while True:
        try:
            price = get_price("BTC/USDT")
            
            # Simple strategy: buy if price drops 5%
            if price < 42500:  # Example threshold
                result = place_order("BTC/USDT", "buy", 0.01)
                print(f"Bought: {result}")
            
            elif price > 47500:
                result = place_order("BTC/USDT", "sell", 0.01)
                print(f"Sold: {result}")
        
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(60)  # Check every minute

trading_bot()
```

---

## 8. Troubleshooting

### Order Not Filled

**Causes:**
- Limit price not reached
- Insufficient liquidity
- Market closed

**Solutions:**
- Adjust limit price
- Place market order
- Check order status

### Insufficient Balance

**Solutions:**
- Deposit more funds
- Reduce order size
- Cancel open orders to free balance

### Price Slippage

**Causes:**
- Large order
- Low liquidity
- Volatile market

**Solutions:**
- Split into smaller orders
- Use limit orders
- Wait for better liquidity

### API Errors

```python
# Handle errors gracefully
response = requests.post(url, json=data)

if response.status_code != 200:
    error = response.json()
    print(f"Error {error['error']['code']}: {error['error']['message']}")
    
    # Common codes:
    # 400 - Bad request
    # 401 - Unauthorized  
    # 429 - Rate limited
    # 500 - Server error
```

---

## Quick Reference

### Order Types
- **Market** - Immediate at best price
- **Limit** - At your price
- **Stop-Loss** - Auto-sell at price

### Keyboard Shortcuts
- B - Buy panel
- S - Sell panel
- Esc - Close modal

### Order Status
- open - Waiting to fill
- partially_filled - Some filled
- filled - Completely filled
- cancelled - Cancelled
- rejected - Rejected