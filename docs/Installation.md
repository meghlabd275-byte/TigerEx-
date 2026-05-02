# TigerEx Installation Guide

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Storage | 100 GB SSD | 500 GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software Requirements

- **OS:** Ubuntu 22.04 LTS / Debian 11
- **Python:** 3.10+
- **PostgreSQL:** 14+
- **Redis:** 6+
- **Docker:** 24+ (optional)

### Required Packages

```bash
# Install system packages
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv postgresql redis-server nginx git

# Install Python packages
pip3 install flask flask-cors requests pyjwt pyotp python-dotenv
pip3 install psycopg2-binary redis
pip3 install ccxt aiohttp
```

---

## Installation Methods

### Method 1: Manual Installation

#### 1. Clone Repository

```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit `.env`:

```bash
# Database
DATABASE_URL=postgresql://tigerex:tigerex123@localhost:5432/tigerex

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
BINANCE_API_KEY=your_key
COINGECKO_API_KEY=your_key
ETHERSCAN_API_KEY=your_key

# Server
PORT=5000
SECRET_KEY=your_secret_key
```

#### 4. Initialize Database

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE tigerex;
CREATE USER tigerex WITH PASSWORD 'tigerex123';
GRANT ALL PRIVILEGES ON DATABASE tigerex TO tigerex;

# Run migrations
python scripts/migrate.py
```

#### 5. Start Services

```bash
# Production Engine (port 5300)
python backend/production-engine/engine.py &

# Price Sync (port 5200)
python backend/price-sync/price_feed.py &

# Wallet Service (port 6000)
python custom-wallet/backend/wallet_service.py &

# Exchange (port 5900)
python custom-exchange/backend/exchange.py &

# Blockchain (port 5800)
python custom-blockchain/blockchain_node.py &
```

#### 6. Start Frontend

```bash
# Option 1: Static file
# Open frontend/complete/platform.html in browser

# Option 2: Development server
cd frontend
python -m http.server 8080
```

---

### Method 2: Docker Installation

#### 1. Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: tigerex
      POSTGRES_USER: tigerex
      POSTGRES_PASSWORD: tigerex123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  production-engine:
    build: ./backend/production-engine
    ports:
      - "5300:5300"
    depends_on:
      - postgres
      - redis

  price-sync:
    build: ./backend/price-sync
    ports:
      - "5200:5200"

  wallet:
    build: ./custom-wallet/backend
    ports:
      - "6000:6000"

  exchange:
    build: ./custom-exchange/backend
    ports:
      - "5900:5900"

  blockchain:
    build: ./custom-blockchain
    ports:
      - "5800:5800"

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - production-engine
      - wallet
      - exchange

volumes:
  postgres_data:
```

#### 2. Start Services

```bash
docker-compose up -d
```

---

## Configuration

### Production Engine

File: `backend/production-engine/engine.py`

```python
# Key settings
FEE_MAKER = 0.001    # 0.1%
FEE_TAKER = 0.002     # 0.2%
MAX_ORDER_SIZE = 1000000
MAX_LEVERAGE = 10
LIQUIDATION_THRESHOLD = 0.025
```

### Price Sync

File: `backend/price-sync/price_feed.py`

```python
# Exchange API keys (set in environment)
# BINANCE_API_KEY
# COINGECKO_API_KEY
```

### Wallet

File: `custom-wallet/backend/wallet_service.py`

```python
# Supported chains configured
CHAINS = {
    "ethereum": {...},
    "bsc": {...},
    ...
}
```

---

## SSL/TLS Setup

### Using Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx

sudo certbot --nginx -d api.tigerex.com
```

### Manual Certificate

```bash
# Generate self-signed (for testing)
openssl req -x509 -newkey rsa:4096 -key key.pem -out cert.pem -days 365
```

---

## Nginx Configuration

File: `nginx.conf`

```nginx
upstream production_engine {
    server localhost:5300;
}

upstream price_sync {
    server localhost:5200;
}

upstream wallet {
    server localhost:6000;
}

upstream exchange {
    server localhost:5900;
}

server {
    listen 443 ssl http2;
    server_name api.tigerex.com;
    
    ssl_certificate /etc/letsencrypt/live/tigerex.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tigerex.com/privkey.pem;
    
    location /engine {
        proxy_pass http://production_engine;
    }
    
    location /price {
        proxy_pass http://price_sync;
    }
    
    location /wallet {
        proxy_pass http://wallet;
    }
    
    location /exchange {
        proxy_pass http://exchange;
    }
}
```

---

## Monitoring

### Health Checks

```bash
# Production Engine
curl http://localhost:5300/engine/health

# Price Sync
curl http://localhost:5200/price/health

# Wallet
curl http://localhost:6000/wallet/health
```

### Logs

```bash
# View logs
tail -f /var/log/tigerex/production-engine.log
tail -f /var/log/tigerex/price-sync.log
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup
pg_dump -U tigerex tigerex > backup_$(date +%Y%m%d).sql

# Restore
psql -U tigerex tigerex < backup_20240502.sql
```

### Redis Backup

```bash
# Save RDB
redis-cli SAVE

# Backup file
cp /var/lib/redis/dump.rdb backup_dump.rdb
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check service is running on correct port |
| Database error | Verify DATABASE_URL in .env |
| Redis error | Check REDIS_URL and firewall |
| API rate limit | Wait and retry, or add API key |
| SSL error | Regenerate certificates |

### Logs Location

```
/var/log/tigerex/     - Application logs
/var/log/nginx/        - Web server logs
/var/log/postgresql/ - Database logs
```

---

## Uninstall

```bash
# Stop all services
pkill -f "engine.py"
pkill -f "price_feed.py"
pkill -f "wallet_service.py"

# Remove database
sudo -u postgres psql -c "DROP DATABASE tigerex;"

# Remove files
rm -rf ~/tigerex
```