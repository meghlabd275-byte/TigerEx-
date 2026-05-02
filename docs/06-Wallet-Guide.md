# TigerEx Wallet Complete Guide

## Table of Contents
1. Creating Wallets
2. Managing Wallets
3. Depositing Crypto
4. Withdrawing Crypto
5. Sending Crypto
6. Security Features
7. Multi-Chain Networks
8. Troubleshooting

---

## 1. Creating Wallets

### Create Custodial Wallet

Custodial wallets are managed by TigerEx - easy to use with built-in recovery.

**Step 1:** Login to your account

**Step 2:** Go to Wallet → Create Wallet

**Step 3:** Select Network
```
Supported Networks:
- Ethereum (ETH)
- BNB Smart Chain (BNB)
- Polygon (MATIC)
- Arbitrum (ARB)
- Avalanche (AVAX)
- TigerEx (TIG)
```

**Step 4:** Select Type → Custodial

**Step 5:** Click Create

**API Example:**
```python
import requests

BASE_URL = "http://localhost:6000"

# Create custodial wallet
response = requests.post(
    f"{BASE_URL}/wallet/create/custodial",
    json={
        "user_id": "user123",
        "chain": "ethereum"
    }
)

wallet = response.json()
print(f"Address: {wallet['address']}")
print(f"Wallet ID: {wallet['wallet_id']}")
```

### Create Non-Custodial Wallet

Non-custodial wallets give you full control of your private keys.

**Step 1:** Go to Wallet → Create Wallet

**Step 2:** Select Network

**Step 3:** Select Type → Non-Custodial

**Step 4:** Save your private key securely

**API Example:**
```python
# Create non-custodial wallet
response = requests.post(
    f"{BASE_URL}/wallet/create/non-custodial",
    json={
        "user_id": "user123",
        "chain": "ethereum"
    }
)

wallet = response.json()
# IMPORTANT: Save this address securely
print(f"Address: {wallet['address']}")
```

---

## 2. Managing Wallets

### View All Wallets

**Dashboard View:**
```
My Wallets:
├─ Ethereum Custodial - 0x742d...B5B5 [Active]
├─ BSC Custodial - 0x8AC7...9A0 [Active]
└─ Polygon Non-Custodial - 0x0d50...E2b1 [Active]
```

**API:**
```python
# Get all user wallets
response = requests.get(f"{BASE_URL}/wallet/list/user123")
wallets = response.json()

for wallet in wallets:
    print(f"Chain: {wallet['chain']}")
    print(f"Address: {wallet['address']}")
    print(f"Type: {wallet['type']}")
```

### Check Balance

**UI:** Click wallet → View Balance

**API:**
```python
# Get wallet balance
response = requests.get(f"{BASE_URL}/wallet/balance/CUST_ABC123")
balance = response.json()

for asset, data in balance['balances'].items():
    print(f"{asset}: {data['balance']}")
```

---

## 3. Depositing Crypto

### Find Deposit Address

1. Go to Wallet
2. Select network
3. Click Deposit
4. Copy address or scan QR

### Deposit Process

**Ethereum/ERC-20:**
```
1. Copy your deposit address
2. Send tokens to this address
3. Wait for 12 block confirmations
4. Balance updates automatically
```

**BSC (BNB):**
```
1. Copy your BNB deposit address
2. Send BNB to address
3. Wait for 15 confirmations
4. Balance credited
```

**Polygon:**
```
1. Copy MATIC deposit address
2. Send MATIC tokens
3. Wait for ~5 minutes
4. Balance updates
```

**API Example:**
```python
# Simulate deposit (in production, webhook from blockchain)
response = requests.post(
    f"{BASE_URL}/wallet/deposit",
    json={
        "wallet_id": "CUST_ABC123",
        "asset": "ETH",
        "amount": 1.0,
        "tx_hash": "0x..."
    }
)
```

---

## 4. Withdrawing Crypto

### Withdrawal Process

1. Go to Wallet
2. Select wallet
3. Click Withdraw
4. Enter destination address
5. Enter amount
6. Confirm with 2FA

### Daily Limits

| KYC Level | Daily Limit |
|-----------|------------|
| Unverified | $100 |
| Level 1 | $1,000 |
| Level 2 | $10,000 |
| Level 3+ | $100,000+ |

### Withdrawal Fees

| Network | Fee |
|---------|-----|
| ETH | 0.005 ETH |
| BNB | 0.005 BNB |
| MATIC | 5 MATIC |
| AVAX | 0.025 AVAX |

**API Example:**
```python
# Withdraw crypto
response = requests.post(
    f"{BASE_URL}/wallet/withdraw",
    json={
        "wallet_id": "CUST_ABC123",
        "to_address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0",
        "asset": "ETH",
        "amount": 0.5
    }
)
```

---

## 5. Sending Crypto

### Send Process

1. Select wallet
2. Click Send
3. Enter recipient address
4. Enter amount
5. Set gas price (optional)
6. Confirm

### Transaction Speed

| Gas Price | Speed | Cost |
|-----------|-------|-------|
| Slow | 10+ min | Low |
| Normal | 3-5 min | Medium |
| Fast | < 1 min | High |

**API Example:**
```python
# Send from non-custodial wallet
response = requests.post(
    f"{BASE_URL}/wallet/send",
    json={
        "wallet_id": "NONCUST_ABC123",
        "to_address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0",
        "amount": 0.1,
        "asset": "ETH"
    }
)

tx = response.json()
print(f"Transaction Hash: {tx['tx_hash']}")
```

### Cancel Pending Transaction

If transaction stuck:
1. Go to Transaction Details
2. Click "Speed Up" or "Cancel"
3. Sign new transaction with higher gas

---

## 6. Security Features

### Enable Two-Factor Authentication

1. Go to Security Settings
2. Click "Enable 2FA"
3. Scan QR with authenticator app
4. Enter verification code
5. Save backup codes

**Supported Apps:**
- Google Authenticator
- Authy
- 1Password

### Device Management

View authorized devices:
1. Security Settings
2. Active Sessions
3. Revoke suspicious devices

### Withdrawal Confirmations

| Amount | Requirements |
|--------|-------------|
| < $100 | Password |
| < $1,000 | Password + 2FA |
| < $10,000 | Password + 2FA + Email |
| > $10,000 | All above + Phone |

---

## 7. Multi-Chain Networks

### Supported Networks

**EVM Chains:**

| Network | Chain ID | Symbol | Explorer |
|---------|----------|--------|----------|
| Ethereum | 1 | ETH | etherscan.io |
| BSC | 56 | BNB | bscscan.com |
| Polygon | 137 | MATIC | polygonscan.com |
| Arbitrum | 42161 | ETH | arbiscan.io |
| Avalanche | 43114 | AVAX | snowtrace.io |
| TigerEx | 9999 | TIG | - |

**Non-EVM Chains:**

| Network | Symbol |
|---------|--------|
| Solana | SOL |
| TON | TON |
| NEAR | NEAR |
| Aptos | APT |
| Sui | SUI |
| Cosmos | ATOM |

### Switch Networks

1. Click network selector (top right)
2. Select desired chain
3. Wallet automatically updates

---

## 8. Troubleshooting

### Transaction Stuck

**Solutions:**
- Wait for network confirmations
- Try "Speed Up" option
- Contact support if >24 hours

### Balance Not Updating

**Solutions:**
- Wait for block confirmations
- Refresh page
- Clear cache

### Wrong Network

**Solutions:**
- Cannot reverse transactions
- Contact support immediately
- Provide transaction hash

### Cannot Withdraw

**Possible reasons:**
- Pending deposits not confirmed
- Below minimum withdrawal
- Exceeded daily limit
- 2FA not enabled

### API Code Examples

#### Full Wallet Integration

```python
import requests

class TigerExWallet:
    def __init__(self, base_url="http://localhost:6000"):
        self.base = base_url
    
    def create_wallet(self, user_id, chain, is_custodial=True):
        endpoint = "/wallet/create/custodial" if is_custodial else "/wallet/create/non-custodial"
        resp = requests.post(f"{self.base}{endpoint}", json={
            "user_id": user_id, "chain": chain
        })
        return resp.json()
    
    def get_balance(self, wallet_id):
        resp = requests.get(f"{self.base}/wallet/balance/{wallet_id}")
        return resp.json()
    
    def deposit(self, wallet_id, asset, amount):
        resp = requests.post(f"{self.base}/wallet/deposit", json={
            "wallet_id": wallet_id, "asset": asset, "amount": amount
        })
        return resp.json()
    
    def withdraw(self, wallet_id, to_address, asset, amount):
        resp = requests.post(f"{self.base}/wallet/withdraw", json={
            "wallet_id": wallet_id, "to_address": to_address,
            "asset": asset, "amount": amount
        })
        return resp.json()
    
    def get_chains(self):
        resp = requests.get(f"{self.base}/wallet/chains")
        return resp.json()

# Usage
wallet = TigerExWallet()
wallets = wallet.create_wallet("user123", "ethereum")
balance = wallet.get_balance("CUST_ABC123")
```

---

### Contact Support

- Email: support@tigerex.com
- Telegram: @TigerExSupport
- In-app chat