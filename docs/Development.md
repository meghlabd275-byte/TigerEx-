# TigerEx Development Guide

## Project Structure

```
TigerEx-/
├── backend/
│   ├── production-engine/      # Trading engine
│   ├── price-sync/         # Price feeds
│   ├── service-mesh/       # Service communication
│   └── ...
├── custom-wallet/
│   └── backend/           # Wallet service
├── custom-exchange/
│   └── backend/           # Exchange
├── custom-blockchain/     # Custom blockchain
├── frontend/
│   └── complete/          # UI platform
├── docs/                  # Documentation
└── server/               # Main server
```

---

## Development Setup

### Local Environment

```bash
# Clone
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export PYTHONPATH=$PWD:$PYTHONPATH

# Run tests
pytest tests/ -v

# Start development server
python server/app.py
```

---

## Adding New Features

### Service Template

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

class NewService:
    def __init__(self):
        self.data = {}
    
    def process(self, data):
        # Your logic here
        return {"result": "success"}

# Initialize
service = NewService()

# Routes
@app.route('/service/endpoint', methods=['POST'])
def endpoint():
    data = request.get_json()
    result = service.process(data)
    return jsonify(result)

# Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Database Integration

```python
import psycopg2
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    try:
        yield conn
    finally:
        conn.close()

# Usage
with get_db() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        result = cur.fetchall()
```

### Redis Cache

```python
import redis
import json

r = redis.from_url(os.environ['REDIS_URL'])

def cache_get(key):
    data = r.get(key)
    return json.loads(data) if data else None

def cache_set(key, value, ttl=300):
    r.setex(key, ttl, json.dumps(value))

# Usage
def get_price(symbol):
    # Try cache first
    cached = cache_get(f"price:{symbol}")
    if cached:
        return cached
    
    # Fetch from API
    price = fetch_price(symbol)
    
    # Cache result
    cache_set(f"price:{symbol}", price, ttl=5)
    
    return price
```

---

## Testing

### Unit Tests

```python
import pytest

def test_orderMatching():
    engine = OrderMatchingEngine()
    
    # Add orders
    buy_order = Order(
        symbol="BTC/USDT",
        side="buy",
        price=45000,
        quantity=1
    )
    
    sell_order = Order(
        symbol="BTC/USDT",
        side="sell", 
        price=45000,
        quantity=1
    )
    
    # Match
    trades = engine.match(buy_order, sell_order)
    
    # Assert
    assert len(trades) == 1
    assert trades[0].price == 45000

def test_walletCreation():
    wallet_service = WalletService()
    
    # Create wallet
    wallet = wallet_service.create_custodial_wallet("user1", "ethereum")
    
    # Assert
    assert wallet['address'].startswith('0x')
    assert wallet['type'] == 'custodial'
```

### Integration Tests

```python
import requests

BASE_URL = "http://localhost:5300"

def test_health():
    response = requests.get(f"{BASE_URL}/engine/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_orderFlow():
    # Login
    token = login("testuser", "testpass")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Place order
    order_data = {
        "symbol": "BTC/USDT",
        "side": "buy",
        "price": 45000,
        "quantity": 0.1
    }
    
    response = requests.post(
        f"{BASE_URL}/engine/order",
        json=order_data,
        headers=headers
    )
    
    assert response.status_code == 200
    assert 'order_id' in response.json()
```

---

## Code Style

### Python

Follow PEP 8 with:
- 4 spaces indentation
- Maximum line length: 100
- Docstrings: Google style
- Type hints where applicable

```python
def process_order(order_id: str, user_id: str) -> Optional[Order]:
    """Process a trading order.
    
    Args:
        order_id: Unique order identifier
        user_id: User placing the order
    
    Returns:
        Processed order or None if not found
    
    Raises:
        ValueError: If order is invalid
    """
    # Implementation
    pass
```

### JavaScript

```javascript
// Use ES6+ features
const processOrder = async (orderId) => {
    try {
        const response = await fetch(`/api/orders/${orderId}`);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
};

// Arrow functions
const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
};
```

---

## Git Workflow

### Branch Naming

```
feature/feature-name
bugfix/bug-description
hotfix/urgent-fix
refactor/section-name
docs/documentation
```

### Commit Messages

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(wallet): add multi-chain support

- Added Ethereum, BSC, Polygon support
- Updated wallet creation flow
- Added RPC endpoint configuration

Closes #123
```

---

## Deployment

### Build Process

```bash
# Build Docker image
docker build -t tigerex/backend:latest ./backend

# Push to registry
docker push tigerex/backend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Kubernetes Config

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: production-engine
  template:
    spec:
      containers:
      - name: engine
        image: tigerex/backend:latest
        ports:
        - containerPort: 5300
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tigerex-secrets
              key: database-url
```

---

## Monitoring

### Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
ORDER_COUNT = Counter('orders_total', 'Total orders placed')
TRADE_VOLUME = Histogram('trade_volume_usd', 'Trade volume in USD')
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Order placed: {order_id}")
logger.warning(f"Low balance: {user_id}")
logger.error(f"Trade failed: {error}")
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|------|----------|
| Import error | Check PYTHONPATH |
| Database connection | Verify DATABASE_URL |
| Redis connection | Check REDIS_URL |
| Port in use | Kill existing process or use different port |
| API not responding | Check service logs |

### Debug Mode

```bash
# Enable debug
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG

# Run with debug
python -m flask run --debug
```

---

## Performance Optimization

### Caching Strategy

1. **Redis for frequent queries**
   - Prices (5s TTL)
   - Order book (1s TTL)
   - User balances (30s TTL)

2. **Database indexing**
   - Primary keys
   - Foreign keys
   - Composite indexes for queries

### Async Processing

```python
import asyncio

async def process_batch(orders):
    # Process orders concurrently
    tasks = [process_order(o) for o in orders]
    results = await asyncio.gather(*tasks)
    return results
```