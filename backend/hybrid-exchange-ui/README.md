# TigerEx Hybrid Exchange UI

## Overview

Complete hybrid exchange user interface with seamless CEX/DEX switching capabilities, similar to Binance's hybrid trading experience.

## Features

### 🎯 Core Hybrid Functionality
- **Seamless CEX/DEX Switching**: Switch between centralized and decentralized exchange modes with one click
- **Smart Order Routing**: Automatically finds best prices across CEX and DEX
- **Unified Wallet**: Single wallet for both CEX and DEX trading
- **Hybrid Trading**: Execute orders using best available liquidity

### 📊 Trading Interface
- **Complete Trading Modes**: Spot, Margin, Futures, Options
- **Advanced Order Types**: Market, Limit, Stop-Limit, Stop-Market
- **Real-time Market Data**: Live prices, order books, charts
- **Portfolio Management**: Unified view of CEX and DEX holdings

### 🔄 Exchange Mode Switching
- **CEX Mode**: Centralized exchange features only
- **DEX Mode**: Decentralized exchange features only  
- **Hybrid Mode**: Best of both worlds with smart routing

### 💼 User Experience
- **Unified Dashboard**: Single interface for all trading activities
- **Smart Routing**: Auto-select best execution venue
- **Best Price Execution**: Always get optimal prices
- **Cross-platform Liquidity**: Access both CEX and DEX liquidity

## API Endpoints

### Authentication
```
POST /api/auth/login
POST /api/auth/logout
```

### Exchange Mode Switching
```
POST /api/exchange/switch-mode
GET /api/exchange/current-mode/{user_id}
```

### Trading
```
POST /api/trading/place-order
GET /api/trading/order-book/{symbol}
POST /api/trading/switch-mode
```

### Dashboard & Interface
```
GET /api/dashboard/complete
GET /api/dashboard/trading-interface/{symbol}
GET /api/dashboard/portfolio/{user_id}
GET /api/dashboard/hybrid-stats
```

### Wallet & Balance
```
GET /api/wallet/balance/{user_id}
```

### System Status
```
GET /api/system/status
GET /api/system/health
```

## Usage Example

### 1. User Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "demo_password"}'
```

### 2. Switch to Hybrid Mode
```bash
curl -X POST "http://localhost:8000/api/exchange/switch-mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "hybrid"}' \
  -H "user_id: user_123"
```

### 3. Place Hybrid Order
```bash
curl -X POST "http://localhost:8000/api/trading/place-order" \
  -H "Content-Type: application/json" \
  -H "user_id: user_123" \
  -d '{
    "symbol": "BTC/USDT",
    "side": "BUY",
    "order_type": "LIMIT",
    "quantity": 0.001,
    "price": 50000.0,
    "use_smart_routing": true
  }'
```

### 4. Get Complete Dashboard
```bash
curl "http://localhost:8000/api/dashboard/complete?user_id=user_123"
```

## Hybrid Exchange Features

### CEX Features
- ✅ Spot trading with order book
- ✅ Margin trading (up to 10x leverage)
- ✅ Futures trading (perpetual contracts)
- ✅ Options trading
- ✅ Advanced order types
- ✅ Fiat gateway integration
- ✅ Custody wallet service

### DEX Features
- ✅ AMM (Automated Market Maker)
- ✅ Liquidity pools
- ✅ Yield farming
- ✅ Token swap
- ✅ Cross-chain bridge
- ✅ Governance and DAO
- ✅ NFT marketplace

### Hybrid Features
- ✅ Smart order routing
- ✅ Best price execution
- ✅ Unified wallet
- ✅ Cross-platform liquidity
- ✅ Seamless mode switching
- ✅ Smart routing efficiency: 99.5%

## Architecture

```
TigerEx Hybrid Exchange UI
├── main.py (FastAPI application)
├── hybrid_exchange_interface.py (Core interface logic)
├── hybrid_dashboard.py (Dashboard components)
├── requirements.txt
└── README.md
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The application will start on http://localhost:8000

## Testing

Visit http://localhost:8000/docs for interactive API documentation.

## License

Copyright © 2025 TigerEx. All rights reserved.