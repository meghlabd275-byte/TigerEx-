# TigerEx Features Guide

## Core Features

### 1. Spot Trading

Available trading pairs:

```
TIG/USDC, ETH/USDT, BTC/USDT, BNB/USDT
SOL/USDT, MATIC/USDT, AVAX/USDT, ARB/USDT
```

#### Features:
- Market orders
- Limit orders
- Stop-loss orders
- OCO (One-Cancels-Other)
- Time-in-force: GTC, IOC, FOK

#### Trading Interface

```python
# Example: Place limit order
order = {
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "limit",
    "price": 45000.00,
    "quantity": 0.5,
    "time_in_force": "GTC"
}

POST /engine/order
```

---

### 2. Margin Trading

#### Features:
- Leverage: 1x to 10x
- Cross margin
- Isolated margin
- Auto-deleverage
- Liquidation warnings

```python
# Open margin position
position = {
    "symbol": "BTC/USDT",
    "side": "long",
    "leverage": 5,
    "amount": 0.5
}

POST /engine/margin/open
```

---

### 3. Futures Trading

#### Features:
- Perpetual futures
- Quarterly futures
- Funding rate
- Mark price
- Index price
- Settlement: USDT

---

### 4. Options Trading

#### Features:
- Call options
- Put options
- American style
- Multiple expirations
- Strike prices

---

### 5. Staking

#### Supported Assets:

| Asset | APY | Lock Period |
|-------|-----|-------------|
| TIG | 12% | Flexible |
| ETH | 5% | Flexible |
| BNB | 8% | Flexible |
| SOL | 7% | Flexible |

```bash
# Stake tokens
POST /staking/stake
{
  "asset": "TIG",
  "amount": 1000
}
```

---

### 6. Lending/Borrowing

#### Features:
- Supply collateral
- Borrow assets
- Variable interest rates
- Collateral ratio: 130%
- Liquidation threshold: 120%

```python
# Supply collateral
POST /lending/supply
{
  "asset": "ETH",
  "amount": 10
}

# Borrow
POST /lending/borrow
{
  "asset": "USDT",
  "amount": 5000
}
```

---

### 7. Launchpad

#### Features:
- New token sales
- Tiered allocation
- FCFS (First-Come-First-Served)
- Guaranteed allocation

#### Tiers:

| Tier | TIG Holdings | Allocation |
|------|--------------|------------|
| Bronze | 100 | $10 |
| Silver | 1,000 | $100 |
| Gold | 10,000 | $1,000 |
| Platinum | 100,000 | $10,000 |

---

### 8. Liquidity Pools

#### Supported DEXs:

- Uniswap V2/V3
- PancakeSwap
- SushiSwap
- QuickSwap

#### Features:
- Add liquidity
- Remove liquidity
- LP rewards
- Impermanent loss protection

---

### 9. NFT Marketplace

#### Features:
- Buy/Sell NFTs
- Mint NFTs
- NFT auctions
- Collection browsing
- Floor price tracking

---

### 10. P2P Trading

#### Features:
- Local fiat payments
- Escrow protection
- Multiple payment methods
- Instant trade

---

### 11. Payment Gateway

#### Features:
- Crypto payments
- Fiat on/off ramp
- Card payments
- Payment links

---

### 12. Analytics

#### Dashboard Features:

```
Portfolio Value    $12,500.00
24h P&L         +$250.00 (+2.05%)
30d P&L         +$1,200.00 (+10.6%)
Total Trades    156
Win Rate        65%
```

---

### 13. Copy Trading

#### Features:
- Follow top traders
- Auto-copy positions
- Performance tracking
- Leaderboard

---

### 14. API Trading

#### Features:
- REST API
- WebSocket API
- Python SDK
- Rate limits by tier

---

### 15. Mobile App

#### Features:
- iOS & Android
- Biometric login
- Push notifications
- Price alerts

---

### 16. Card

#### Debit Card Features:
- Crypto spending
- 2% cashback
- No annual fee
- Global acceptance

---

### 17. Earn Products

| Product | APY | Features |
|---------|-----|----------|
| Flexible | Variable | Withdraw anytime |
| Fixed | 5-12% | Lock period |
| Dual | 15-25% | 2 assets |

---

### 18. Cloud Mining

#### Features:
- Cloud hashrate
- Daily payouts
- Multiple contracts

---

## Supported Countries

TigerEx is available in 150+ countries.

### Restricted Countries:
- United States (limited)
- China
- North Korea
- Iran
- Cuba
- Syria

---

## Fee Schedule

### Maker/Taker Fees

| Volume (30d) | Maker | Taker |
|---------------|-------|-------|
| < $10,000 | 0.10% | 0.20% |
| $10,000+ | 0.08% | 0.18% |
| $100,000+ | 0.05% | 0.15% |
| $1,000,000+ | 0.03% | 0.10% |
| $10,000,000+ | 0.00% | 0.08% |

### Withdrawal Fees

| Network | Fee |
|---------|-----|
| BTC | 0.0005 |
| ETH | 0.005 |
| USDT (TRC20) | 1 |
| USDC | 1 |

---

## Limits

| Feature | Daily Limit |
|---------|------------|
| Deposit | $1,000,000 |
| Withdrawal | $100,000 |
| Trading | $10,000,000 |
| API | Varies |