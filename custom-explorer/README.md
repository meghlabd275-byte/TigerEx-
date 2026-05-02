# TigerEx Custom Explorer

Blockchain explorer for TigerEx custom blockchain.

## Files

```
custom-explorer/
├── index.html              # Explorer UI
│
custom-explorer-service/
├── main.py              # Backend API
└── requirements.txt    # Dependencies
```

## Features

**Backend API:**
- Chain statistics
- Block data
- Transaction lookup
- Account/balance lookup
- Blockchain search
- Demo data generation

**Frontend:**
- Auto-detect API port
- Chain stats display
- Block browser
- Transaction search
- Address lookup

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/blockchain/stats` | GET | Chain stats |
| `/blockchain/latest_block` | GET | Latest block |
| `/blockchain/block/<num>` | GET | Block by number |
| `/blockchain/tx/<hash>` | GET | Transaction |
| `/blockchain/account/<addr>` | GET | Account |
| `/blockchain/balance/<addr>` | GET | Balance |
| `/blockchain/search?q=` | GET | Search |

## Usage

```bash
# Install dependencies
cd custom-explorer-service
pip install -r requirements.txt

# Run backend
python main.py

# Open frontend
# custom-explorer/index.html in browser
```

## Demo Data

The backend generates:
- 100 blocks
- ~2500 transactions
- 10 accounts

Chain ID: 5777