# TigerEx Technical Specification

## Overview

TigerEx is a comprehensive cryptocurrency exchange platform featuring multi-chain support for both EVM and Non-EVM blockchains, with real-time price synchronization, production-grade trading engine, and secure wallet management.

---

## Architecture

### Service Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  /frontend/complete/platform.html                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                         │
│                      Port 5000                       │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Production  │  │   Price     │  │   Service   │
│   Engine     │  │    Sync    │  │    Mesh    │
│   Port 5300  │  │  Port 5200  │  │  Port 5100  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│               External APIs                           │
│  Binance, Coinbase, Kraken, KuCoin, Bybit, OKX    │
│  CoinGecko, Etherscan, RPC Nodes                 │
└─────────────────────────────────────────────────────────┘
```

---

## Core Services

### 1. Production Trading Engine

**File:** `/backend/production-engine/engine.py`
**Port:** 5300

#### Features:

- **Write-Ahead Log (WAL)**
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
  - Audit trail

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
GET  /engine/health          - Engine status
POST /engine/order           - Place order
GET  /engine/order/<id>      - Get order
PUT  /engine/order/<id>      - Update order
DELETE /engine/order/<id>   - Cancel order
GET  /engine/orders          - List orders
GET  /engine/book/<symbol>  - Order book depth
GET  /engine/trades         - Trade history
GET  /engine/balance/<user> - Account balance
POST /engine/deposit        - Deposit funds
POST /engine/withdraw      - Withdraw funds
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
  - Cache layer (Redis)

#### Supported Pairs:

```
BTC/USDT, ETH/USDT, BNB/USDT, TIG/USDC
SOL/USDT, MATIC/USDT, AVAX/USDT, ARB/USDT
```

#### API Endpoints:

```
GET  /price/health              - Service status
GET  /price/ticker/<symbol>   - Current price
GET  /price/tickers           - All prices
GET  /price/volume/<symbol>   - Trading volume
GET  /price/spread/<symbol>   - Bid/ask spread
GET  /price/history/<symbol>  - Price history
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
  - Transaction history

- **Non-Custodial Wallets**
  - User-controlled keys
  - Import existing wallets
  - Sign messages
  - Raw transaction support

- **Multi-Chain Support**

EVM Chains:
- Ethereum (chain_id: 1)
- BSC (chain_id: 56)
- Polygon (chain_id: 137)
- Arbitrum (chain_id: 42161)
- Avalanche (chain_id: 43114)
- TigerEx (chain_id: 9999)

Non-EVM Chains:
- Solana
- TON
- NEAR
- Aptos
- Sui
- Cosmos

#### API Endpoints:

```
POST /wallet/create/custodial     - Create custodial wallet
POST /wallet/create/non-custodial - Create non-custodial
POST /wallet/import              - Import wallet
GET  /wallet/list/<user_id>       - List user wallets
GET  /wallet/balance/<wallet_id> - Get balance
POST /wallet/deposit            - Process deposit
POST /wallet/withdraw          - Process withdrawal
POST /wallet/send              - Send transaction
GET  /wallet/transactions/<id>  - Transaction history
POST /wallet/sign              - Sign message
GET  /wallet/chains            - Supported chains
GET  /wallet/tokens/<chain>     - Token list
```

---

### 4. Custom Exchange

**File:** `/custom-exchange/backend/exchange.py`
**Port:** 5900

#### Features:

- **CEX Features**
  - Order book trading
  - Market/Limit orders
  - Stop-loss orders (planned)

- **DEX Features**
  - AMM liquidity pools
  - Swap quotes
  - Liquidity provision

- **Hybrid Mode**
  - Both CEX + DEX
  - Unified order books

#### API Endpoints:

```
GET  /exchange/health           - Status
POST /exchange/account       - Create account
POST /exchange/deposit      - Deposit
POST /exchange/withdraw   - Withdraw
POST /exchange/order      - Place order
DELETE /exchange/order/<id> - Cancel order
GET  /exchange/balance/<user> - Balance
GET  /exchange/book/<pair>  - Order book
GET  /exchange/orders      - Open orders
GET  /exchange/trades      - Trade history
GET  /exchange/ticker/<pair> - Price ticker
GET  /exchange/pairs      - Trading pairs
POST /exchange/liquidity/add  - Add liquidity
```

---

### 5. Custom Blockchain

**File:** `/custom-blockchain/blockchain_node.py`
**Port:** 5800

#### Features:

- **Chain Types**
  - EVM-compatible (TigerEx EVM, chain_id: 9999)
  - Native chain (TigerEx Native, chain_id: 10000)
  - Hybrid chain (TigerEx Hybrid, chain_id: 10001)

- **Consensus Mechanisms**
  - Proof of Authority (PoA)
  - Proof of Stake (PoS)

- **Smart Contract Support**
  - ERC-20 tokens
  - ERC-721 NFTs
  - Custom contracts

#### API Endpoints:

```
GET  /blockchain/health            - Status
POST /blockchain/account       - Create account
GET  /blockchain/account/<addr> - Account info
GET  /blockchain/balance/<addr> - Balance
GET  /blockchain/nonce/<addr>  - Nonce
POST /blockchain/send           - Send transaction
POST /blockchain/deploy         - Deploy contract
POST /blockchain/call          - Call contract
GET  /blockchain/block/<num>   - Block data
GET  /blockchain/latest_block - Latest block
GET  /blockchain/tx/<hash>    - Transaction
GET  /blockchain/logs          - Event logs
GET  /blockchain/code/<addr>   - Contract code
POST /blockchain/stake         - Stake tokens
GET  /blockchain/validators   - Validators
GET  /blockchain/stats        - Chain stats
```

---

### 6. Block Explorer

**File:** `/custom-explorer/index.html`

#### Features:

- Block search
- Transaction lookup
- Address lookup
- Chain statistics
- Real-time data

---

### 7. Frontend Platform

**File:** `/frontend/complete/platform.html`

#### Features:

- Dashboard
- Exchange trading
- Wallet management
- Blockchain explorer
- Liquidity provision
- Order management
- Trade history
- Network switching

---

## Security Features

### Authentication:
- Email verification (SendGrid)
- SMS verification (Twilio)
- TOTP 2FA (pyotp)
- Biometric support

### Wallet Security:
- Encrypted key storage
- Hardware wallet support
- Multi-sig transactions

### Trading Security:
- Order size limits
- Position limits
- Auto-liquidation
- Rate limiting

---

## Database Schema

### PostgreSQL Tables:

```sql
users              - User accounts
accounts          - Trading accounts
orders            - Open orders
trades             - Executed trades
ledger           - Transaction ledger
wallets           - Wallet addresses
transactions     - Blockchain transactions
deposits          - Deposit records
withdrawals       - Withdrawal records
```

### Redis Keys:

```
price:BTC/USDT    - Current price
orderbook:ETH    - Order book cache
wallet:balance    - User balances
session:token    - Auth tokens
```

---

## Deployment

### Environment Variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tigerex

# Redis  
REDIS_URL=redis://localhost:6379

# External APIs
BINANCE_API_KEY=
COINGECKO_API_KEY=
ETHERSCAN_API_KEY=
SENDGRID_API_KEY=
TWILIO_SID=
TWILIO_TOKEN=

# Wallet
PRIVATE_KEY_ENCRYPTION_KEY=

# Server
PORT=5000
```

### Docker Services:

```yaml
version: '3.8'
services:
  production-engine:
    build: ./backend/production-engine
    ports:
      - "5300:5300"
  
  price-sync:
    build: ./backend/price-sync
    ports:
      - "5200:5200"
  
  wallet:
    build: ./custom-wallet/backend
    ports:
      - "6000:6000"
  
  exchange:
    build: ./custom-exchange/backend
    ports:
      - "5900:5900"
  
  blockchain:
    build: ./custom-blockchain
    ports:
      - "5800:5800"
```

---

## API Rate Limits

| Endpoint | Limit |
|----------|-------|
| Price queries | 100/min |
| Order placement | 50/min |
| Wallet ops | 30/min |
| Withdrawals | 10/min |

---

## Version History

- v1.0.0 (2024-05-02) - Initial release
  - Production Engine
  - Multi-chain Wallet
  - CEX+DEX Exchange
  - Custom Blockchain

---

## License

Proprietary - All rights reserved

---

## Contact

support@tigerex.com