# TigerEx 2FA Reset Verification

Production-ready 2FA verification system with multi-factor authentication.

## Directory Structure

```
2fa-reset-verification/
├── index.html              # Main 2FA reset UI
├── assets/
│   ├── css/
│   │   └── responsive.css
│   └── js/
│       ├── auth-guard.js   # Auth guards
│       └── 2fa-client.js # API client (v2.0)
└── 2fa-reset-verification-service/
    ├── main.py           # Verification API
    └── requirements.txt
```

## Features

- **Email verification** - OTP sent to email
- **Phone verification** - OTP sent to phone  
- **Face verification** - Liveness detection
- **Rate limiting** - Prevents brute force
- **Audit logging** - Tracks all attempts

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/verification/start` | POST | Start session |
| `/api/v1/verification/email/send` | POST | Send email code |
| `/api/v1/verification/email/verify` | POST | Verify email code |
| `/api/v1/verification/phone/send` | POST | Send phone code |
| `/api/v1/verification/phone/verify` | POST | Verify phone code |
| `/api/v1/verification/face/init` | POST | Init face check |
| `/api/v1/verification/face/verify` | POST | Verify face |
| `/api/v1/verification/status` | GET | Get verification status |

## Installation

```bash
# Backend
cd 2fa-reset-verification-service
pip install -r requirements.txt
python main.py

# Frontend - open index.html in browser
```

## Security

- Codes hashed with PBKDF2
- Rate limiting (10/min, 30/hour)
- Session timeout (30 min)
- Audit logging## TigerEx Wallet API Multi-chain Decentralized Wallet

- **24-word BIP39 seed phrase**
- **Ethereum address** (0x...40 hex)
- **Multi-chain**: ETH, BTC, TRX, BNB
- **User ownership**: USER_OWNS

### Create Wallet
```python
create_wallet()  # Python
createWallet()  # JavaScript
CreateWallet()   // Go
create_wallet()  // Rust
```
