# TigerEx Custom Exchange

CEX + DEX Hybrid Exchange with order matching engine.

## Files

```
custom-exchange/
├── backend/
│   └── exchange.py    # Exchange backend with matching
└── frontend/
    └── exchange.html # Trading UI
```

## Features

**Matching Engine (v2.0):**
- Price-time priority matching
- Limit orders (buy/sell)
- Partial fills
- Order book depth
- Spread calculation

**Trading:**
- Order placement with validation
- Balance checking
- Order cancellation
- Trade history

**Security:**
- Rate limiting (100 req/min)
- Input validation
- Order value limits

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/account` | POST | Create account |
| `/deposit` | POST | Deposit funds |
| `/withdraw` | POST | Withdraw funds |
| `/order` | POST | Place order |
| `/order/<id>` | DELETE | Cancel order |
| `/balance/<uid>` | GET | Get balance |
| `/book/<pair>` | GET | Order book |
| `/trades/<pair>` | GET | Trade history |
| `/config` | GET | Exchange config |

## Usage

```bash
# Run backend
cd backend
pip install flask
python exchange.py

# Open frontend
# frontend/exchange.html in browser
```

## Configuration

```python
CONFIG = {
    "fee_maker": 0.001,      # 0.1%
    "fee_taker": 0.002,      # 0.2%
    "min_order_value": 1.0,
    "max_order_value": 1_000_000
}
```