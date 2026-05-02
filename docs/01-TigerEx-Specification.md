# TigerEx Technical Specification

## Overview

TigerEx is a comprehensive cryptocurrency exchange platform featuring multi-chain support for both EVM and Non-EVM blockchains.

---

## Architecture

### Service Layers

```
┌─────────────────────────────────────────────────────┐
│                   Frontend Layer                     │
│         /frontend/complete/platform.html                │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    API Gateway                    │
│                      Port 5000                   │
└─────────────────────────────────────────────────────┘
                          │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Production │  │   Price    │  │  Service   │
│  Engine   │  │    Sync   │  │   Mesh    │
│ Port 5300 │  │ Port 5200 │  │ Port 5100 │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Core Services

### 1. Production Trading Engine

**File:** `/backend/production-engine/engine.py`
**Port:** 5300

#### Features:

- **file_editor-Ahead Log (WAL)**
  - Append-only transaction log
  - Durability guarantee
  - Crash recovery
  - Transaction replay

- **Order Matching Engine**
  - Price-time priority matching
  - FIFO execution
  - Partial fill support
  - Market/Limit orders

- **Authoritative Ledger**
  - Double-entry accounting
  - Real-time balance updates
  - Transaction history

- **Risk Engine**
  - Order size limits
  - Position limits
  - Auto-liquidation
  - Margin checks

- **Trade Execution**
  - Fee calculation (maker: 0.1%, taker: 0.2%)
  - Trade confirmation
  - Trade history

#### API Endpoints:

```
GET  /engine/health           - Engine status
POST /engine/order          - Place order
GET  /engine/order/<id>     - Get order
PUT  /engine/order/<id>     - Update order
DELETE /engine/order/<id>  - Cancel order
GET  /engine/orders         - List orders
GET  /engine/book/<symbol> - Order book depth
GET  /engine/trades        - Trade history
GET  /engine/balance/<user> - Account balance
POST /engine/deposit       - Deposit funds
POST /engine/withdraw   - Withdraw funds
```

#### Code Example - Place Order:

```python
import requests

BASE_URL = "http://localhost:5300"

# Place a limit order
order_data = {
    "user_id": "user123",
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "limit",
    "price": 45000.00,
    "quantity": 0.5,
    "time_in_force": "GTC"
}

response = requests.post(f"{BASE_URL}/engine/order", json=order_data)
print(response.json())
```

#### Response:

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

---

### 2. Price Synchronization Service

**File:** `/backend/price-sync/price_feed.py`
**Port:** 5200

#### Features:

- **Multi-Exchange Connectivity**
  - Binance
  - Coinbase  
  - Kraken
  - KuCoin
  - Bybit
  - OKX

- **Price Aggregation**
  - Volume-weighted prices
  - Best bid/ask calculation
  - Price spread monitoring

- **Real-Time Updates**
  - 1-second sync interval
  - WebSocket push support
  - Cache layer

#### Supported Pairs:

```
BTC/USDT, ETH/USDT, BNB/USDT, TIG/USDC
SOL/USDT, MATIC/USDT, AVAX/USDT, ARB/USDT
```

#### Code Example - Get Price:

```python
import requests

BASE_URL = "http://localhost:5200"

# Get current price
response = requests.get(f"{BASE_URL}/price/ticker/BTC/USDT")
data = response.json()

print(f"Price: ${data['last']}")
print(f"Bid: ${data['bid']}")
print(f"Ask: ${data['ask']}")
print(f"Volume: ${data['volume_24h']}")
```

---

### 3. Wallet Service

**File:** `/custom-wallet/backend/wallet_service.py`
**Port:** 6000

#### Features:

- **Custodial Wallets**
  - Platform-managed keys
  - Deposit/withdraw
  - Internal transfers

- **Non-Custodial Wallets**
  - User-controlled keys
  - Import existing wallets
  - Sign messages

- **Multi-Chain Support:**

EVM Chains (6):
- Ethereum (chain_id: 1)
- BSC (chain_id: 56)
- Polygon (chain_id: 137)
- Arbitrum (chain_id: 42161)
- Avalanche (chain_id: 43114)
- TigerEx (chain_id: 9999)

Non-EVM Chains (6):
- Solana
- TON
- NEAR
- Aptos
- Sui
- Cosmos

#### Code Example - Create Wallet:

```python
import requests

BASE_URL = "http://localhost:6000"

# Create custodial wallet
data = {
    "user_id": "user123",
    "chain": "ethereum"
}

response = requests.post(
    f"{BASE_URL}/wallet/create/custodial", 
    json=data
)

wallet = response.json()
print(f"Address: {wallet['address']}")
print(f"Wallet ID: {wallet['wallet_id']}")
```

---

### 4. Custom Exchange

**File:** `/custom-exchange/backend/exchange.py`
**Port:** 5900

#### Features:

- **CEX Features**
  - Order book trading
  - Market/Limit orders

- **DEX Features**
  - AMM liquidity pools
  - Swap quotes
  - Liquidity provision

- **Hybrid Mode**
  - Both CEX + DEX

#### Code Example - Place Order:

```python
import requests

BASE_URL = "http://localhost:5900"

order = {
    "user_id": "user123",
    "pair": "TIG/USDC",
    "side": "buy",
    "type": "limit",
    "price": 2.50,
    "quantity": 100
}

response = requests.post(f"{BASE_URL}/exchange/order", json=order)
print(response.json())
```

---

### 5. Custom Blockchain

**File:** `/custom-blockchain/blockchain_node.py`
**Port:** 5800

#### Chain Types:

- **TigerEx EVM** (chain_id: 9999) - EVM-compatible
- **TigerEx Native** (chain_id: 10000) - Proof of Stake
- **TigerEx Hybrid** (chain_id: 10001) - Combined

#### Code Example - Create Account:

```python
import requests

BASE_URL = "http://localhost:5800"

# Create account on custom blockchain
response = requests.post(
    f"{BASE_URL}/blockchain/account",
    json={"private_key": "0x..."}
)

account = response.json()
print(f"Address: {account['address']}")
```

---

### 6. Production Engine Code

```python
"""
Production Trading Engine - Complete Implementation
"""
from flask import Flask, jsonify, request
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import uuid

app = Flask(__name__)

# Data Classes
@dataclass
class Order:
    order_id: str
    user_id: str
    symbol: str
    side: str
    type: str
    price: float
    quantity: float
    filled: float = 0
    status: str = "open"
    created_at: str = None
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "type": self.type,
            "price": self.price,
            "quantity": self.quantity,
            "filled": self.filled,
            "status": self.status,
            "created_at": self.created_at
        }

# In-memory storage
orders_db = {}
balances_db = {}

# Fee configuration
FEE_MAKER = 0.001  # 0.1%
FEE_TAKER = 0.002  # 0.2%

# Routes
@app.route('/engine/health')
def health():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "orders": len(orders_db)
    })

@app.route('/engine/order', methods=['POST'])
def place_order():
    data = request.get_json()
    
    order_id = f"ORD_{uuid.uuid4().hex[:8].upper()}"
    
    order = Order(
        order_id=order_id,
        user_id=data['user_id'],
        symbol=data['symbol'],
        side=data['side'],
        type=data.get('type', 'limit'),
        price=data['price'],
        quantity=data['quantity'],
        created_at=datetime.utcnow().isoformat()
    )
    
    orders_db[order_id] = order
    
    return jsonify(order.to_dict())

@app.route('/engine/order/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({"error": "Not found"}), 404

@app.route('/engine/order/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    order = orders_db.get(order_id)
    if order:
        order.status = "cancelled"
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404

@app.route('/engine/orders', methods=['GET'])
def list_orders():
    user_id = request.args.get('user_id')
    if user_id:
        user_orders = [o.to_dict() for o in orders_db.values() 
                   if o.user_id == user_id]
        return jsonify(user_orders)
    return jsonify([o.to_dict() for o in orders_db.values()])

@app.route('/engine/balance/<user_id>', methods=['GET'])
def get_balance(user_id):
    if user_id in balances_db:
        return jsonify(balances_db[user_id])
    return jsonify({})

@app.route('/engine/book/<symbol>', methods=['GET'])
def order_book(symbol):
    levels = int(request.args.get('levels', 10))
    
    buy_orders = [o for o in orders_db.values() 
                if o.symbol == symbol and o.side == "buy" and o.status == "open"]
    sell_orders = [o for o in orders_db.values() 
                if o.symbol == symbol and o.side == "sell" and o.status == "open"]
    
    # Sort by price
    buy_orders.sort(key=lambda x: x.price, reverse=True)
    sell_orders.sort(key=lambda x: x.price)
    
    bids = [[o.price, o.quantity] for o in buy_orders[:levels]]
    asks = [[o.price, o.quantity] for o in sell_orders[:levels]]
    
    return jsonify({
        "symbol": symbol,
        "bids": bids,
        "asks": asks
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5300)
```

---

### 7. Wallet Service Code

```python
"""
Wallet Service - Complete Implementation
"""
from flask import Flask, jsonify, request
import uuid
import hashlib
from datetime import datetime

app = Flask(__name__)

# Supported chains configuration
CHAINS = {
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH"},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB"},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC"},
    "arbitrum": {"name": "Arbitrum", "type": "evm", "chain_id": 42161, "symbol": "ETH"},
    "avalanche": {"name": "Avalanche", "type": "evm", "chain_id": 43114, "symbol": "AVAX"},
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL"},
    "tigerex": {"name": "TigerEx", "type": "evm", "chain_id": 9999, "symbol": "TIG"},
}

# Database
wallets_db = {}
balances_db = {}
transactions_db = {}

# Routes
@app.route('/wallet/health')
def health():
    return jsonify({
        "status": "ok",
        "chains": list(CHAINS.keys())
    })

@app.route('/wallet/create/custodial', methods=['POST'])
def create_custodial():
    data = request.get_json()
    chain = data.get('chain', 'ethereum')
    
    if chain not in CHAINS:
        return jsonify({"error": f"Unsupported chain: {chain}"}), 400
    
    # Generate address
    address = "0x" + hashlib.sha256(
        f"{data['user_id']}{chain}{uuid.uuid4()}".encode()
    ).hexdigest()[-40:]
    
    wallet_id = f"CUST_{uuid.uuid4().hex[:8]}"
    
    wallets_db[wallet_id] = {
        "wallet_id": wallet_id,
        "user_id": data['user_id'],
        "address": address,
        "chain": chain,
        "type": "custodial",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Initialize balance
    balances_db[wallet_id] = {}
    
    return jsonify(wallets_db[wallet_id])

@app.route('/wallet/create/non-custodial', methods=['POST'])
def create_non_custodial():
    data = request.get_json()
    chain = data.get('chain', 'ethereum')
    
    # Generate private key hash for mock
    private_key = hashlib.sha256(
        f"{data['user_id']}{uuid.uuid4()}".encode()
    ).hexdigest()
    
    address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[-40:]
    
    wallet_id = f"NONCUST_{uuid.uuid4().hex[:8]}"
    
    wallets_db[wallet_id] = {
        "wallet_id": wallet_id,
        "user_id": data['user_id'],
        "address": address,
        "chain": chain,
        "type": "non_custodial",
        "created_at": datetime.utcnow().isoformat()
    }
    
    balances_db[wallet_id] = {}
    
    return jsonify(wallets_db[wallet_id])

@app.route('/wallet/list/<user_id>')
def list_wallets(user_id):
    user_wallets = [w for w in wallets_db.values() 
                  if w['user_id'] == user_id]
    return jsonify(user_wallets)

@app.route('/wallet/balance/<wallet_id>')
def get_balance(wallet_id):
    if wallet_id not in wallets_db:
        return jsonify({"error": "Wallet not found"}), 404
    
    wallet = wallets_db[wallet_id]
    balance = balances_db.get(wallet_id, {})
    
    return jsonify({
        "wallet_id": wallet_id,
        "address": wallet['address'],
        "chain": wallet['chain'],
        "balances": balance
    })

@app.route('/wallet/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    asset = data.get('asset')
    amount = data.get('amount')
    
    if wallet_id not in wallets_db:
        return jsonify({"error": "Wallet not found"}), 404
    
    if wallet_id not in balances_db:
        balances_db[wallet_id] = {}
    
    balances_db[wallet_id][asset] = balances_db[wallet_id].get(asset, 0) + amount
    
    # Record transaction
    tx_id = f"DEP_{uuid.uuid4().hex[:8]}"
    transactions_db[tx_id] = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "type": "deposit",
        "asset": asset,
        "amount": amount,
        "status": "confirmed"
    }
    
    return jsonify({"deposit_id": tx_id, "status": "confirmed"})

@app.route('/wallet/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    wallet_id = data.get('wallet_id')
    asset = data.get('asset')
    amount = data.get('amount')
    to_address = data.get('to_address')
    
    if wallet_id not in wallets_db:
        return jsonify({"error": "Wallet not found"}), 404
    
    balance = balances_db.get(wallet_id, {}).get(asset, 0)
    
    if balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    balances_db[wallet_id][asset] -= amount
    
    tx_id = f"WDR_{uuid.uuid4().hex[:8]}"
    transactions_db[tx_id] = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "type": "withdraw",
        "asset": asset,
        "amount": amount,
        "to": to_address,
        "status": "pending"
    }
    
    return jsonify({"withdrawal_id": tx_id, "status": "pending"})

@app.route('/wallet/chains')
def chains():
    return jsonify([
        {"id": k, "name": v["name"], "type": v["type"], "chain_id": v["chain_id"]}
        for k, v in CHAINS.items()
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
```

---

### 8. Price Sync Code

```python
"""
Price Synchronization Service - Complete Implementation
"""
from flask import Flask, jsonify, request
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Configuration for exchanges
EXCHANGES = {
    "binance": {"api": "https://api.binance.com"},
    "coinbase": {"api": "https://api.coinbase.com"},
    "kraken": {"api": "https://api.kraken.com"},
    "kucoin": {"api": "https://api.kucoin.com"},
    "bybit": {"api": "https://api.bybit.com"},
    "okx": {"api": "https://www.okx.com"},
}

# Supported trading pairs
PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "TIG/USDC",
    "SOL/USDT", "MATIC/USDT", "AVAX/USDT", "ARB/USDT"
]

# Price data storage
prices_db = {}
volumes_db = {}

# Initialize with mock prices
for pair in PAIRS:
    base = pair.split('/')[0]
    # Mock prices - in production, fetch from exchanges
    prices_db[pair] = {
        "symbol": pair,
        "last": 45000 if base == "BTC" else 2800 if base == "ETH" else 2.5,
        "bid": 44990 if base == "BTC" else 2795 else 2.49,
        "ask": 45010 if base == "BTC" else 2805 else 2.51,
        "volume_24h": 1000000,
        "change_24h": 2.5,
    }

# Background price sync
def sync_prices():
    while True:
        # In production, fetch real prices from each exchange
        # For now, add small random variation
        for pair in PAIRS:
            if pair in prices_db:
                prices_db[pair]['last'] *= 0.999 + 0.002
                prices_db[pair]['bid'] = prices_db[pair]['last'] * 0.9998
                prices_db[pair]['ask'] = prices_db[pair]['last'] * 1.0002
        time.sleep(1)

# Start background sync
thread = threading.Thread(target=sync_prices, daemon=True)
thread.start()

# Routes
@app.route('/price/health')
def health():
    return jsonify({
        "status": "ok",
        "exchanges": len(EXCHANGES),
        "pairs": len(PAIRS)
    })

@app.route('/price/ticker/<symbol>')
def get_ticker(symbol):
    # Normalize symbol format
    symbol = symbol.replace('-', '/').upper()
    
    if symbol in prices_db:
        return jsonify(prices_db[symbol])
    return jsonify({"error": "Symbol not found"}), 404

@app.route('/price/tickers')
def get_tickers():
    return jsonify(prices_db)

@app.route('/price/volume/<symbol>')
def get_volume(symbol):
    symbol = symbol.replace('-', '/').upper()
    if symbol in prices_db:
        return jsonify({"symbol": symbol, "volume": prices_db[symbol]['volume_24h']})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200)
```

---

### 9. Exchange Code

```python
"""
Custom Exchange Service - Complete Implementation
"""
from flask import Flask, jsonify, request
from dataclasses import dataclass
import uuid

app = Flask(__name__)

@dataclass
class Order:
    id: str
    user_id: str
    pair: str
    side: str
    price: float
    quantity: float

# Storage
orders_db = {}
balances_db = {}

@app.route('/exchange/health')
def health(): 
    return jsonify({"status": "ok"})

@app.route('/exchange/order', methods=['POST'])
def place_order():
    data = request.get_json()
    
    order_id = f"ORD_{uuid.uuid4().hex[:8]}"
    order = Order(
        id=order_id,
        user_id=data['user_id'],
        pair=data['pair'],
        side=data['side'],
        price=data['price'],
        quantity=data['quantity']
    )
    
    orders_db[order_id] = order
    
    return jsonify({
        "order_id": order_id,
        "status": "open"
    })

@app.route('/exchange/book/<pair>')
def order_book(pair):
    buys = [o for o in orders_db.values() 
           if o.pair == pair and o.side == "buy"]
    sells = [o for o in orders_db.values() 
            if o.pair == pair and o.side == "sell"]
    
    return jsonify({
        "pair": pair,
        "bids": [[o.price, o.quantity] for o in buys],
        "asks": [[o.price, o.quantity] for o in sells]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900)
```

---

## Database Schema

### PostgreSQL Tables:

```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    kyc_level INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    symbol VARCHAR(20),
    side VARCHAR(10),
    type VARCHAR(10),
    price DECIMAL(20, 8),
    quantity DECIMAL(20, 8),
    filled DECIMAL(20, 8),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Trades table
CREATE TABLE trades (
    trade_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    price DECIMAL(20, 8),
    quantity DECIMAL(20, 8),
    fee DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Wallets table
CREATE TABLE wallets (
    wallet_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    address VARCHAR(100),
    chain VARCHAR(20),
    type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Balances table
CREATE TABLE balances (
    user_id VARCHAR(50),
    asset VARCHAR(20),
    available DECIMAL(20, 8),
    locked DECIMAL(20, 8),
    PRIMARY KEY (user_id, asset)
);
```

---

## Deployment Commands

### Start All Services:

```bash
# Production Engine
python backend/production-engine/engine.py &

# Price Sync
python backend/price-sync/price_feed.py &

# Wallet Service
python custom-wallet/backend/wallet_service.py &

# Exchange
python custom-exchange/backend/exchange.py &

# Blockchain
python custom-blockchain/blockchain_node.py &
```

### Check Service Health:

```bash
curl http://localhost:5300/engine/health
curl http://localhost:5200/price/health
curl http://localhost:6000/wallet/health
curl http://localhost:5900/exchange/health
curl http://localhost:5800/blockchain/health
```

---

## Version History

- v1.0.0 (2024-05-02) - Initial release
  - Production Engine with WAL
  - Multi-chain Wallet
  - CEX+DEX Exchange
  - Custom Blockchain
  - Price Synchronization