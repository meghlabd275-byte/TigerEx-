# TigerEx KYC Verification

Identity verification module for TigerEx exchange.

## Files

```
kyc-verification/
├── index.html              # KYC verification UI
└── assets/
    └── css/
        └── responsive.css # Responsive styles
```

## Features

**5-Step Verification:**

1. **Document Type Selection**
   - Passport
   - Driver License
   - National ID
   - Other

2. **Front Document Upload**
   - Drag & drop
   - Image preview

3. **Back Document Upload**
   - Drag & drop
   - Image preview

4. **Selfie Verification**
   - Camera capture
   - Live video

5. **Verification Status**
   - Pending / Approved / Rejected

## Usage

Open `index.html` in browser to test.

## API Endpoints

The frontend expects these API endpoints:

- `POST /api/kyc/submit` - Submit documents
- `GET /api/kyc/status/:userId` - Get verification status
- `POST /api/kyc/verify-selfie` - Verify selfie match

## KYC Levels

| Level | Requirements |
|-------|-------------|
| 0 | None - Unverified |
| 1 | Email verified |
| 2 | Phone verified + ID |
| 3 | Full KYC + Selfie |

## Security

- Client-side image compression
- Secure camera capture
- Liveness detection placeholder## TigerEx Wallet API Multi-chain Decentralized Wallet

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
