# TigerEx Trading Guide

## Table of Contents
1. Getting Started with Trading
2. Trading Interface
3. Order Types
4. Trading Pairs
5. Fees and Limits
6. Advanced Features
7. Trading Strategies
8. Risk Management

---

## 1. Getting Started with Trading

### Account Requirements

Before trading, complete these steps:

1. **Verify Email**
   - Check inbox for verification email
   - Click verification link

2. **Enable 2FA**
   - Go to Security Settings
   - Enable two-factor authentication

3. **Complete KYC (Optional)**
   - Level 1: Email + Phone
   - Level 2: ID verification

4. **Deposit Funds**
   - Go to Wallet
   - Deposit USDT or supported asset

### Account Tiers and Limits

| Tier | Daily Limit | Features |
|------|------------|----------|
| Unverified | $100 | Basic trading |
| Level 1 | $1,000 | Higher limits |
| Level 2 | $10,000 | All features |
| Level 3 | $100,000 | VIP support |

---

## 2. Trading Interface

### Main Interface

```
┌────────────────────────────────────────────────────────┐
│                    TigerEx Trading                   │
├────────────────────────────────────────────────────────┤
│  Pair: BTC/USDT │ $45,000 │ +2.5% │ Vol: $125M │
├─────────────────────────────────────────────────────────┤
│                    Order Book                       │
│  Bids                │ Asks                        │
│  44,990  │ 2.5   │ 45,010  │ 1.8              │
│  44,985  │ 1.8   │ 45,015  │ 2.0              │
│  44,980  │ 3.2   │ 45,020  │ 4.5              │
├─────────────────────────────────────────────────────────┤
│                 Your Orders                         │
│  [Buy] [Sell]                                   │
│  Price: [        ] Amount: [        ]               │
│  Total: $45,000                               │
│  [      Place Buy Order       ]                    │
└─────────────────────────────────────────────────────────┘
```

### Interface Features

- **Ticker:** Real-time price updates
- **Order Book:** Live buy/sell orders
- **My Orders:** Your open positions
- **Trade History:** Completed trades
- **Charts:** Price charts and indicators

---

## 3. Order Types

### Market Orders

Execute immediately at best available price.

```python
order = {
    "symbol": "BTC/USDT",
    "side": "buy",
    "type": "market",
    "quantity": 0.5
}
```

**Example:**
- Market price: $45,000
- Order executes at: $45,005 (slippage)
- Good for: Fast execution

### Limit Orders

Set your desired price.

```python
order = {
    "symbol": "BTC/USDT", 
    "side": "buy",
    "type": "limit",
    "price": 44000,
    "quantity": 0.5,
    "time_in_force": "GTC"
}
```

**Time-in-Force Options:**
- **GTC** - Good Till Cancel
- **IOC** - Immediate or Cancel
- **FOK** - Fill or Kill

### Stop-Loss Orders

Limit losses automatically.

```python
order = {
    "symbol": "BTC/USDT",
    "side": "sell",
    "type": "stop_loss",
    "stop_price": 43000,
    "quantity": 0.5
}
```

### OCO Orders

One-Cancels-Other

```
Buy at: $44,000
Sell at: $46,000

If buy executes → Sell order cancelled
If sell executes → Buy order cancelled
```

---

## 4. Trading Pairs

### Spot Pairs Available

**USDT Pairs:**
```
BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT
MATIC/USDT, AVAX/USDT, ARB/USDT, LINK/USDT
```

**USDC Pairs:**
```
TIG/USDC, BTC/USDC, ETH/USDC
```

### Trading Pair Codes

Each pair has:
- **Base:** The asset you're buying/selling
- **Quote:** The asset you're paying/receiving

BTC/USDT:
- Base: BTC
- Quote: USDT

---

## 5. Fees and Limits

### Fee Schedule

| 30-Day Volume | Maker Fee | Taker Fee |
|--------------|---------|----------|
| < $10,000 | 0.10% | 0.20% |
| $10,000+ | 0.08% | 0.18% |
| $100,000+ | 0.05% | 0.15% |
| $1,000,000+ | 0.03% | 0.10% |
| $10,000,000+ | 0.00% | 0.08% |

### Trading Limits

| Pair | Min Order | Max Order |
|------|----------|----------|
| BTC/USDT | 0.001 | 100 |
| ETH/USDT | 0.01 | 1000 |
| TIG/USDC | 1 | 100000 |

---

## 6. Advanced Features

### Margin Trading

Trade with leverage.

```
Leverage: 1x - 10x

Example:
- 1x: Use your $1,000 → Trade $1,000
- 5x: Use your $1,000 → Trade $5,000
- 10x: Use your $1,000 → Trade $10,000
```

### Stop-Loss and Take-Profit

```python
// Set stop-loss at 10% loss
stop_loss: price * 0.90

// Set take-profit at 20% gain  
take_profit: price * 1.20
```

### Trailing Stop

```
Trailing Distance: 2%

Entry: $45,000
Current: $46,000
Stop Updates: $46,000 * 0.98 = $45,080

When price drops to $45,080, order triggers
```

---

## 7. Trading Strategies

### Day Trading

Open and close positions within same day.

```
Strategy:
- Small price movements
- Use charts
- Set strict stop-loss
- Quick decisions
```

### Swing Trading

Hold positions for days/weeks.

```
Strategy:
- Price swings
- Trend following
- Weekly charts
- Lower stress
```

### scalping

Many small trades.

```
Strategy:
- Very small profits
- High volume
- Automated tools
- Low fees critical
```

---

## 8. Risk Management

### Position Sizing

```python
# Risk only 2% per trade
risk_amount = portfolio * 0.02

# If portfolio = $10,000
# Risk = $200 per trade
```

### Stop-Loss Rules

| Account Risk | Per Trade |
|------------|----------|
| Conservative | 1% |
| Moderate | 2% |
| Aggressive | 5% |

### Portfolio Allocation

```
Suggested:
- Max 10% in single position
- Max 20% in single sector
- Hold 10% in stablecoin
```

---

## Quick Reference

| Term | Definition |
|------|-----------|
| Bid | Buy price |
| Ask | Sell price |
| Spread | Ask - Bid |
| Volume | Trading amount |
| Liquidity | Ease of trading |
| Slippage | Price difference |

### Keyboard Shortcuts

- **B:** Buy panel
- **S:** Sell panel
- **Esc:** Close modal
- **Ctrl+Enter:** Submit order