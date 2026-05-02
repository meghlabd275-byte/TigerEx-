# TigerEx Troubleshooting Guide

## Common Issues and Solutions

---

## API Issues

### 1. Connection Refused

**Symptom:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Cause:** Service not running on specified port

**Solution:**
```bash
# Check which process is using the port
lsof -i :5300

# Start the service if not running
python backend/production-engine/engine.py &
```

---

### 2. Authentication Failed

**Symptom:**
```
{"error": "Unauthorized", "code": 401}
```

**Cause:** Invalid or expired token

**Solution:**
```python
# Refresh token
response = requests.post('/auth/refresh', json={
    'refresh_token': refresh_token
})

# Or login again
response = requests.post('/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
```

---

### 3. Rate Limited

**Symptom:**
```
{"error": "Rate limit exceeded", "code": 429}
```

**Cause:** Too many requests

**Solution:**
```python
# Implement rate limiting
import time
import requests

def request_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code != 429:
                return response
        except:
            pass
        time.sleep(2 ** i)  # Exponential backoff
    return None
```

---

### 4. Invalid Order Parameters

**Symptom:**
```
{"error": "Invalid price", "code": 400}
```

**Cause:** Invalid order data

**Solution:**
```python
# Validate order before sending
ORDER_LIMITS = {
    'BTC/USDT': {'min': 0.001, 'max': 100},
    'ETH/USDT': {'min': 0.01, 'max': 1000}
}

def validate_order(symbol, price, quantity):
    limits = ORDER_LIMITS.get(symbol)
    if not limits:
        raise ValueError(f"Unsupported symbol: {symbol}")
    if price <= 0:
        raise ValueError("Price must be positive")
    if quantity < limits['min'] or quantity > limits['max']:
        raise ValueError(f"Quantity must be between {limits['min']} and {limits['max']}")
    return True
```

---

## Database Issues

### 1. Connection Failed

**Symptom:**
```
psycopg2.OperationalError: could not connect to server
```

**Cause:** PostgreSQL not running or incorrect credentials

**Solution:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql

# Check connection
psql -h localhost -U tigerex -d tigerex

# Verify .env file
cat .env | grep DATABASE
```

---

### 2. Query Timeout

**Symptom:** Request hangs indefinitely

**Cause:** Missing database index or large table

**Solution:**
```sql
-- Add index
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);

-- Optimize query
SELECT * FROM orders 
WHERE user_id = 'user123' 
AND created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC
LIMIT 100;
```

---

## Wallet Issues

### 1. Balance Not Updating

**Symptom:** Balance shows 0 after deposit

**Cause:** Blockchain not confirmed or cache issue

**Solution:**
```python
# Check on-chain balance
balance = fetch_onchain_balance(chain, address)

# Wait for confirmations
# ETH: 12+ confirmations
# BSC: 15+ confirmations

# Force refresh
clear_balance_cache(wallet_id)
```

---

### 2. Transaction Pending Too Long

**Symptom:** Transaction shows "pending" for hours

**Cause:** Low gas price or network congestion

**Solution:**
```python
# Check current gas price
gas_price = get_current_gas_price(chain)

# Speed up transaction
speed_up_transaction(tx_hash, gas_price * 1.5)

# Or cancel and resend
cancel_transaction(tx_hash)
resend_with_higher_gas(tx_hash)
```

---

### 3. Wallet Import Failed

**Symptom:** Invalid private key error

**Cause:** Wrong format or checksum

**Solution:**
```python
# Validate private key format
def validate_private_key(key):
    if key.startswith('0x'):
        key = key[2:]
    
    # Check length (64 chars for private key)
    if len(key) != 64:
        raise ValueError("Invalid private key length")
    
    # Validate hex
    try:
        int(key, 16)
    except:
        raise ValueError("Invalid private key: not valid hex")
    
    return True
```

---

## Trading Issues

### 1. Order Not Filling

**Symptom:** Order stays open indefinitely

**Cause:** Price not reaching order price

**Solution:**
```python
# Check order book
book = get_order_book('BTC/USDT')

# Place market order instead
place_order(symbol, 'buy', type='market', quantity=0.1)

# Or modify order price
modify_order(order_id, new_price=current_price + 0.01)
```

---

### 2. Insufficient Balance

**Symptom:**
```
{"error": "Insufficient balance", "code": 400}
```

**Cause:** Not enough funds

**Solution:**
```python
# Check current balance
balance = get_balance(user_id, 'USDT')

# Calculate max order
max_quantity = balance.available / order_price

# Reduce order size
place_order(symbol, 'buy', quantity=max_quantity)
```

---

### 3. Slippage Too High

**Symptom:** Order fills at worse price

**Cause:** Large order in thin market

**Solution:**
```python
# Split into smaller orders
def split_order(order_id, num_splits=10):
    original_order = get_order(order_id)
    split_size = original_order.quantity / num_splits
    
    for i in range(num_splits):
        place_order(
            symbol=original_order.symbol,
            side=original_order.side,
            price=original_order.price,
            quantity=split_size
        )
    
    cancel_order(order_id)
```

---

## Frontend Issues

### 1. Page Not Loading

**Symptom:** White screen or error

**Cause:** JavaScript error or missing file

**Solution:**
```bash
# Check browser console (F12)

# Clear cache
# Ctrl+Shift+R (hard refresh)

# Check network tab for 404 errors

# Verify file exists
ls -la frontend/complete/platform.html
```

---

### 2. API Calls Not Working

**Symptom:** "Network error" in console

**Cause:** CORS or API endpoint issue

**Solution:**
```javascript
// Enable CORS on backend
app.config['CORS_ORIGINS'] = ['*']

// Or use correct base URL
const API_BASE = 'http://localhost:5300';

// Check proxy configuration
// nginx.conf should proxy to correct port
```

---

## Performance Issues

### 1. Slow Response Time

**Symptom:** API responds in >1 second

**Cause:** No caching or poor query

**Solution:**
```python
# Enable Redis caching
import redis
r = redis.from_url('redis://localhost:6379')

def getCachedPrice(symbol):
    # Try cache
    cached = r.get(f'price:{symbol}')
    if cached:
        return json.loads(cached)
    
    # Fetch and cache
    price = fetchPrice(symbol)
    r.setex(f'price:{symbol}', 5, json.dumps(price))
    return price
```

---

### 2. High Memory Usage

**Symptom:** Server uses >80% RAM

**Cause:** Memory leak or large data loads

**Solution:**
```python
# Limit data in memory
MAX_ORDERS_IN_MEM = 10000
MAX_TRADES_PER_SYMBOL = 1000

# Use pagination
def get_orders(page=1, limit=100):
    offset = (page - 1) * limit
    return db.query(f"SELECT * FROM orders LIMIT {limit} OFFSET {offset}")
```

---

## Deployment Issues

### 1. Docker Container Fails

**Symptom:** Container exits immediately

**Solution:**
```bash
# Check logs
docker logs container_id

# Build with debug
docker build --no-cache -t tigerex:test .

# Run interactively
docker run -it tigerex:test /bin/bash
```

---

### 2. Service Not Registering

**Symptom:** Service mesh not working

**Solution:**
```bash
# Check service health
curl http://localhost:5300/engine/health

# Check Redis service registry
redis-cli KEYS "service:*"

# Restart service
docker-compose restart service
```

---

## Emergency Procedures

### Complete System Reset

```bash
# Stop all services
pkill -f "engine.py"

# Clear Redis
redis-cli FLUSHALL

# Clear database (careful!)
# psql -c "TRUNCATE orders, trades, ledger;"

# Restart services
./start_services.sh
```

### Rollback to Previous Version

```bash
# Check git log
git log --oneline -10

# Checkout previous commit
git checkout PREVIOUS_COMMIT

# Rebuild and restart
docker-compose build
docker-compose up -d
```

---

## Getting Help

### Logs Required

When reporting issues, include:

1. Error message
2. Request/response details
3. Relevant logs
4. Steps to reproduce

### Contact

- Email: support@tigerex.com
- Telegram: @TigerExSupport
- Discord: TigerEx#1234

---

## Diagnostic Commands

```bash
# System status
curl http://localhost:5300/engine/health
curl http://localhost:5200/price/health
curl http://localhost:6000/wallet/health

# Database
psql -c "SELECT count(*) FROM orders;"

# Redis
redis-cli INFO
redis-cli DBSIZE

# Docker
docker ps
docker stats

# System
free -h
df -h
top -b -n 1
```