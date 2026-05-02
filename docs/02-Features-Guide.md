# TigerEx - Complete Feature Documentation

## Table of Features

### 1. Trading Features

#### 1.1 Spot Trading

Spot trading is the core feature of TigerEx, allowing users to buy and sell cryptocurrencies instantly at market prices or set limit orders at desired prices.

**Supported Pairs:**
- BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT
- MATIC/USDT, AVAX/USDT, ARB/USDT, LINK/USDT
- TIG/USDC, BTC/USDC, ETH/USDC

**Order Types:**

1. **Market Order** - Executes immediately at best available price
```python
# Example: Buy 0.5 BTC at market price
order = {
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "market",
    "quantity": 0.5
}
```

2. **Limit Order** - Set your desired price
```python
order = {
    "symbol": "ETH/USDT",
    "side": "buy",
    "type": "limit", 
    "price": 2500.00,
    "quantity": 2.0,
    "time_in_force": "GTC"  # Good Till Cancel
}
```

3. **Stop-Loss Order** - Auto-sell when price drops
```python
order = {
    "symbol": "BTC/USDT", 
    "side": "sell",
    "type": "stop_loss",
    "stop_price": 42000,
    "quantity": 0.5
}
```

**Time-in-Force Options:**
- **GTC** (Good Till Cancel) - Order stays until filled or cancelled
- **IOC** (Immediate or Cancel) - Fill immediately or cancel
- **FOK** (Fill or Kill) - Fill completely or cancel

---

#### 1.2 Margin Trading

Trade with leverage up to 10x.

**Features:**
- Cross margin (use all collateral)
- Isolated margin (per position)
- Auto-deleverage system
- Liquidation warnings at 130%

**Leverage Levels:**
```python
leverage = 1   # No leverage
leverage = 2   # 2x
leverage = 5   # 5x  
leverage = 10  # 10x max
```

**Open Position:**
```python
# Open long position with 5x leverage
position = {
    "symbol": "BTC/USDT",
    "side": "long",
    "leverage": 5,
    "amount": 0.5,  # Your collateral: 0.1 BTC
    "entry_price": 45000
}
```

**Liquidation Price Calculation:**
```python
liquidation_price = entry_price * (1 - 1/leverage + 0.10)
# For 5x at 45000: 45000 * (0.9 + 0.10) = 45000
```

---

#### 1.3 Futures Trading

Perpetual futures with no expiration.

**Features:**
- Mark price (averages across exchanges)
- Index price (spot median)
- Funding rate (every 8 hours)
- Settlement in USDT

**Contract Specifications:**
```python
contract = {
    "symbol": "BTC-PERPETUAL",
    "underlying": "BTC/USDT",
    "tick_size": 0.5,
    "lot_size": 0.001,
    "max_order": 100,  # BTC
    "funding_rate": 0.0001  # 0.01%
}
```

---

#### 1.4 Staking

Earn rewards by holding tokens.

**Supported Assets:**
| Asset | APY | Min Stake |
|-------|-----|-----------|
| TIG | 12% | 10 |
| ETH | 5% | 0.1 |
| BNB | 8% | 0.01 |
| SOL | 7% | 1 |

**Stake Tokens:**
```python
# Stake TIG tokens
stake = {
    "asset": "TIG",
    "amount": 1000,
    "duration": 30  # days, 0 = flexible
}

# Response
{
    "stake_id": "STK_001",
    "rewards_apr": 0.12,
    "next_claim": "2024-06-01"
}
```

---

#### 1.5 Lending/Borrowing

Supply collateral and borrow against it.

**Parameters:**
- Collateral ratio: 130%
- Liquidation: 120%
- Variable interest rates

**Supply Assets:**
```python
# Supply ETH as collateral
supply = {
    "asset": "ETH",
    "amount": 10
}
```

**Borrow:**
```python
# Borrow USDT against collateral
borrow = {
    "asset": "USDT", 
    "amount": 5000,
    "collateral_asset": "ETH"
}
```

---

### 2. Wallet Features

#### 2.1 Custodial Wallets

Managed by TigerEx - easy to use, recovery available.

**Create:**
```python
# Create custodial wallet
wallet = {
    "user_id": "user123",
    "chain": "ethereum"
}

# Response
{
    "wallet_id": "CUST_ABC123",
    "address": "0x742d35Cc6634C0532925a3b8D0D2C8D3D5A5B5B5",
    "type": "custodial",
    "status": "active"
}
```

**Features:**
- Fast transactions
- Easy backup
- Customer support
- Built-in 2FA

---

#### 2.2 Non-Custodial Wallets

You control private keys - full ownership.

**Create:**
```python
# Create non-custodial
wallet = {
    "user_id": "user123", 
    "chain": "ethereum",
    "type": "non_custodial"
}
```

**Import Existing:**
```python
# Import wallet with private key
import_data = {
    "user_id": "user123",
    "private_key": "0x...",  # Your private key
    "chain": "ethereum"
}
```

**Security:**
- Private key stored encrypted on device
- Hardware wallet compatible
- Sign transactions locally

---

#### 2.3 Multi-Chain Support

**EVM Chains:**
- Ethereum (ETH)
- BNB Smart Chain (BNB)
- Polygon (MATIC)
- Arbitrum (ETH)
- Avalanche (AVAX)
- TigerEx (TIG)

**Non-EVM Chains:**
- Solana (SOL)
- TON (TON)
- NEAR (NEAR)
- Aptos (APT)
- Sui (SUI)
- Cosmos (ATOM)

---

### 3. Security Features

#### 3.1 Account Security

**Password Requirements:**
- Minimum 12 characters
- 1 uppercase, 1 lowercase, 1 number, 1 special
- No common passwords

**2FA Setup:**
```python
# Enable TOTP
response = requests.post("/security/2fa/enable")
{
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_uri": "otpauth://totp/TigerEx:user?secret=JBSWY3DPEHPK3PXP"
}
```

**Biometric:**
```python
# Enable biometric login
{
    "type": "fingerprint" | "face_id",
    "enabled": True
}
```

---

#### 3.2 Withdrawal Security

**Daily Limits by Level:**
| Level | Daily Limit | 2FA Required |
|-------|------------|---------------|
| Unverified | $100 | No |
| KYC 1 | $1,000 | Yes |
| KYC 2 | $10,000 | Yes + Email |
| KYC 3 | $100,000 | Yes + Email + Phone |

**Withdrawal Process:**
1. Enter amount and address
2. Confirm with password
3. Enter 2FA code
4. Email verification (high value)
5. Phone verification (very high)

---

### 4. API Trading

#### 4.1 REST API

**Base URL:** `https://api.tigerex.com/v1`

**Authentication:**
```python
# Get token
auth = requests.post("/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})

token = auth.json()["access_token"]

# Use token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Place order
order = requests.post(
    "/engine/order",
    json={
        "symbol": "BTC/USDT",
        "side": "buy", 
        "price": 45000,
        "quantity": 0.1
    },
    headers=headers
)
```

---

#### 4.2 WebSocket API

**Connection:**
```python
import websocket
import json

ws = websocket.create_connection(
    "wss://api.tigerex.com/ws"
)

# Subscribe to ticker
subscribe = {
    "action": "subscribe", 
    "channel": "ticker",
    "symbol": "BTC/USDT"
}

ws.send(json.dumps(subscribe))

# Receive updates
while True:
    result = ws.recv()
    print(result)
```

**Channels:**
- `ticker` - Price updates
- `orderbook` - Order book changes
- `trades` - Trade executions
- `orders` - Your orders

---

### 5. Fees

#### 5.1 Trading Fees

| Volume (30d) | Maker | Taker |
|---------------|------|-------|
| < $10,000 | 0.10% | 0.20% |
| $10,000+ | 0.08% | 0.18% |
| $100,000+ | 0.05% | 0.15% |
| $1,000,000+ | 0.03% | 0.10% |
| $10,000,000+ | 0.00% | 0.08% |

---

#### 5.2 Withdrawal Fees

| Network | Fee |
|---------|-----|
| BTC | 0.0005 BTC |
| ETH | 0.005 ETH |
| USDT (ERC20) | 5 USDT |
| USDT (TRC20) | 1 USDT |
| BNB | 0.005 BNB |
| MATIC | 5 MATIC |

---

### 6. Integration Examples

#### 6.1 Python Trading Bot

```python
import requests
import time

BASE_URL = "https://api.tigerex.com/v1"
TOKEN = "your_token_here"

def get_price(symbol):
    response = requests.get(
        f"{BASE_URL}/price/ticker/{symbol}",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

def place_order(symbol, side, quantity):
    response = requests.post(
        f"{BASE_URL}/engine/order",
        json={
            "symbol": symbol,
            "side": side,
            "type": "market",
            "quantity": quantity
        },
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

# Simple trading bot
def trading_bot():
    while True:
        price = get_price("BTC/USDT")
        
        # Buy if price drops 5%
        if price['change_24h'] < -5:
            order = place_order("BTC/USDT", "buy", 0.01)
            print(f"Bought: {order}")
        
        # Sell if price rises 5%
        elif price['change_24h'] > 5:
            order = place_order("BTC/USDT", "sell", 0.01)
            print(f"Sold: {order}")
        
        time.sleep(60)  # Check every minute

# Run bot
trading_bot()
```

---

#### 6.2 TradingView Alerts

```python
# TradingView webhook handler
from flask import Flask, request
import requests

app = Flask(__name__)

WEBHOOK_SECRET = "your_secret"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Verify signature
    if data.get('secret') != WEBHOOK_SECRET:
        return "Unauthorized", 401
    
    # Get alert price
    price = float(data.get('alert', {}).get('price', 0))
    
    # Execute trade via API
    if price > 0:
        response = requests.post(
            "https://api.tigerex.com/v1/engine/order",
            json={
                "symbol": "BTC/USDT",
                "side": "buy",
                "type": "limit",
                "price": price,
                "quantity": 0.01
            }
        )
    
    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)
```

---

### 7. Troubleshooting

#### Common Issues

**Order Not Filled:**
- Price not reaching limit
- Too small volume
- Market conditions

**Withdrawal Pending:**
- Network congestion
- Low gas price
- Wait for confirmations

**2FA Not Working:**
- Time sync issue
- Use backup codes
- Contact support

**API Errors:**
```python
# Handle errors
response = requests.post(url, json=data)
if response.status_code != 200:
    error = response.json()
    print(f"Error {error['code']}: {error['message']}")
```

---

### 8. Contact Support

- **Email:** support@tigerex.com
- **Telegram:** @TigerExSupport
- **In-App:** Chat with us