# TigerEx Security Guide

## Overview

TigerEx implements comprehensive security measures to protect user funds and data.

---

## 1. Account Security

### Password Requirements

```python
# Password validation rules
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_BLOCKLIST = [
    "password", "123456", "qwerty", "admin", "tigerex"
]
```

### Two-Factor Authentication (2FA)

```python
import pyotp

# Generate TOTP secret
def generate_2fa_secret():
    return pyotp.random_base32()

# Verify code
def verify_2fa(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

# Get provisioning URI for QR code
def get_2fa_qr_uri(secret, user_email):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=user_email,
        issuer_name="TigerEx"
    )
```

### Biometric Authentication

```python
# Supported types
BIOMETRIC_TYPES = ["fingerprint", "face_id", "iris"]

# Store biometric hash (never raw data)
def store_biometric(user_id, biometric_type, biometric_hash):
    db.execute("""
        INSERT INTO user_biometrics (user_id, type, hash)
        VALUES (?, ?, ?)
    """, [user_id, biometric_type, biometric_hash])
```

---

## 2. Wallet Security

### Private Key Encryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

# Generate key from password
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Encrypt private key
def encrypt_private_key(private_key: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(private_key.encode())
    return base64.b64encode(salt + encrypted).decode()

# Decrypt private key
def decrypt_private_key(encrypted_data: str, password: str) -> str:
    data = base64.b64decode(encrypted_data)
    salt, encrypted = data[:16], data[16:]
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
```

### Transaction Signing

```python
# Sign transaction locally (non-custodial)
from eth_account import Account

def sign_transaction(private_key: str, tx_params: dict):
    account = Account.from_key(private_key)
    
    signed = account.sign_transaction({
        'nonce': tx_params['nonce'],
        'gasPrice': tx_params['gas_price'],
        'gas': tx_params['gas_limit'],
        'to': tx_params['to_address'],
        'value': tx_params['value'],
        'data': tx_params.get('data', '0x'),
        'chainId': tx_params['chain_id']
    })
    
    return signed.rawTransaction.hex()
```

---

## 3. API Security

### Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# Rate limits by endpoint
@app.route('/engine/order')
@limiter.limit("50 per minute")
def place_order():
    pass

@app.route('/wallet/send')
@limiter.limit("10 per minute")
def send_transaction():
    pass
```

### Request Signing

```python
import hmac
import hashlib
import time

def sign_request(secret: str, method: str, path: str, body: str = ""):
    timestamp = str(int(time.time()))
    message = timestamp + method + path + body
    
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'X-Timestamp': timestamp,
        'X-Signature': signature
    }
```

### IP Whitelist

```python
# Allow only whitelisted IPs
@app.middleware
async def check_ip_whitelist(request, handler):
    client_ip = request.headers.get('X-Real-IP')
    
    allowed_ips = get_user_allowed_ips(request.user_id)
    
    if client_ip not in allowed_ips:
        raise HTTPException(403, "IP not whitelisted")
    
    return await handler(request)
```

---

## 4. Withdrawal Security

### Multi-Sig Approval

```python
# Withdrawal requires multiple approvals
APPROVAL_THRESHOLDS = {
    1000: 1,   # $1000+ needs 1 approval
    10000: 2,  # $10,000+ needs 2 approvals
    100000: 3  # $100,000+ needs 3 approvals
}

def require_approvals(amount_usd: float) -> int:
    for threshold, approvals in sorted(APPROVAL_THRESHOLDS.items()):
        if amount_usd >= threshold:
            return approvals
    return 1
```

### Delay Period

```python
# Withdrawal delay for security
WITHDRAWAL_DELAY = {
    'level_0': 48 * 3600,  # 48 hours
    'level_1': 24 * 3600,  # 24 hours
    'level_2': 12 * 3600,  # 12 hours
    'level_3': 0           # No delay
}
```

---

## 5. Fraud Detection

### Transaction Monitoring

```python
# Flag suspicious transactions
SUSPICIOUS_PATTERNS = {
    'new_device': 0.3,
    'unusual_location': 0.3,
    'rapid_transactions': 0.5,
    'large_amount': 0.7,
    'multiple_destinations': 0.5
}

def calculate_risk_score(transaction: dict) -> float:
    score = 0.0
    
    if is_new_device(transaction['user_id'], transaction['device_id']):
        score += SUSPICIOUS_PATTERNS['new_device']
    
    if is_unusual_location(transaction['user_id'], transaction['ip']):
        score += SUSPICIOUS_PATTERNS['unusual_location']
    
    if count_transactions_1h(transaction['user_id']) > 10:
        score += SUSPICIOUS_PATTERNS['rapid_transactions']
    
    if transaction['amount'] > get_user_avg_transaction(transaction['user_id']) * 10:
        score += SUSPICIOUS_PATTERNS['large_amount']
    
    return score
```

### Auto-Lock Rules

```python
# Auto-lock triggers
AUTO_LOCK_RULES = {
    'failed_login_attempts': 5,
    'failed_2fa_attempts': 10,
    'suspicious_activity_score': 0.8,
    'withdrawal_to_blacklisted_address': 1.0
}
```

---

## 6. Data Protection

### Encryption at Rest

```python
# Database field encryption
from sqlalchemy.types import TypeDecorator, String
import json

class EncryptedValue(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_value(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_value(value)
        return value

# Usage
class User(Base):
    email = Column(EncryptedValue, nullable=False)
    phone = Column(EncryptedValue)
```

### Encryption in Transit

```python
# Always use HTTPS
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# HSTS headers
@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response
```

---

## 7. Audit Logging

### Log All Actions

```python
import logging
from datetime import datetime

# Create audit logger
audit_logger = logging.getLogger('audit')

def log_action(user_id: str, action: str, details: dict, ip: str):
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details,
        'ip_address': ip,
        'user_agent': get_user_agent()
    }
    
    audit_logger.info(json.dumps(event))
    
    # Store in database
    db.execute("""
        INSERT INTO audit_log (user_id, action, details, ip, created_at)
        VALUES (?, ?, ?, ?, NOW())
    """, [user_id, action, json.dumps(details), ip])
```

### Audit Events

```python
# Log these events
AUDIT_EVENTS = [
    'login',
    'logout',
    'password_change',
    '2fa_enable',
    '2fa_disable',
    'withdrawal_request',
    'withdrawal_approve',
    'api_key_create',
    'api_key_delete',
    'settings_change',
    'kyc_submit',
    'kyc_approve'
]
```

---

## 8. Compliance

### KYC Levels

```python
KYC_LEVELS = {
    0: {
        'name': 'Unverified',
        'daily_withdrawal': 100,
        'trading_limit': 100
    },
    1: {
        'name': 'Level 1',
        'daily_withdrawal': 1000,
        'trading_limit': 10000,
        'requirements': ['email', 'phone']
    },
    2: {
        'name': 'Level 2',
        'daily_withdrawal': 10000,
        'trading_limit': 100000,
        'requirements': ['email', 'phone', 'id_document']
    },
    3: {
        'name': 'Level 3',
        'daily_withdrawal': 100000,
        'trading_limit': 1000000,
        'requirements': ['email', 'phone', 'id_document', 'address_proof']
    }
}
```

### AML Screening

```python
# Check against sanctions lists
SANCTION_LISTS = ['OFAC', 'EU', 'UN', 'UK']

def check_sanctions(address: str) -> bool:
    for list_name in SANCTION_LISTS:
        if is_in_sanctions_list(address, list_name):
            return True
    return False

# Report large transactions
CTR_THRESHOLD = 10000  # $10,000

def check_ctr_required(transaction_amount: float) -> bool:
    return transaction_amount >= CTR_THRESHOLD
```

---

## 9. Incident Response

### Emergency Contacts

```
Security Emergency: security@tigerex.com
Phone: +1 (555) 123-4567
Telegram: @TigerExSecurity
```

### Response Procedure

1. **Detect** - Automated alerts
2. **Escalate** - Notify security team
3. **Contain** - Isolate affected systems
4. **Eradicate** - Remove threat
5. **Recover** - Restore operations
6. **Review** - Document lessons learned

### Backup Procedures

```bash
# Database backup
pg_dump -U tigerex tigerex > backup_$(date +%Y%m%d).sql

# Redis backup
redis-cli SAVE

# Files backup
tar -czf backup_files_$(date +%Y%m%d).tar.gz /data
```