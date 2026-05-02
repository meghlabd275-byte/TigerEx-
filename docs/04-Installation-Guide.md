# TigerEx Complete Installation Guide

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 100 GB SSD
- Network: 100 Mbps

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 500 GB SSD
- Network: 1 Gbps

### Software Requirements

- **OS:** Ubuntu 22.04 LTS / Debian 11
- **Python:** 3.10+
- **PostgreSQL:** 14+
- **Redis:** 6+
- **Docker:** 24+ (optional)

---

## Step 1: Install System Packages

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install database
sudo apt install -y postgresql postgresql-contrib redis-server

# Install web server
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install build tools
sudo apt install -y build-essential libssl-dev libffi-dev
```

---

## Step 2: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone TigerEx repository
git clone https://github.com/meghlabd275-byte/TigerEx-.git

# Navigate to project
cd TigerEx-
```

---

## Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify Python version
python --version
```

---

## Step 4: Install Python Dependencies

```bash
# Install required packages
pip install --upgrade pip

# Install Flask and extensions
pip install flask flask-cors flask-jwt-extended

# Install data processing
pip install requests pyjwt pyotp python-dotenv

# Install database
pip install psycopg2-binary sqlalchemy

# Install cache
pip install redis

# Install trading libraries
pip install ccxt aiohttp asyncio

# Install utilities
pip install pandas numpy
```

---

## Step 5: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit environment file
nano .env
```

**Add these variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://tigerex:tigerex123@localhost:5432/tigerex

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Keys (get from respective services)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

COINGECKO_API_KEY=your_coingecko_api_key

ETHERSCAN_API_KEY=your_etherscan_api_key

# Security
SECRET_KEY=your_very_long_random_secret_key
JWT_SECRET=your_jwt_secret

# Server Configuration
PORT=5000
DEBUG=False

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# External Services
EXTERNAL_RPC_ETH=https://eth.llamarpc.com
EXTERNAL_RPC_BSC=https://bsc.llamarpc.com
EXTERNAL_RPC_POLYGON=https://polygon.llamarpc.com
```

---

## Step 6: Setup Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE tigerex;

# Create user
CREATE USER tigerex WITH PASSWORD 'tigerex123';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tigerex TO tigerex;

# Exit
\q
```

**Create tables:**

```bash
# Create tables.sql file
cat > tables.sql << 'EOF'
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    kyc_level INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    type VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8),
    quantity DECIMAL(20, 8),
    filled DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    trade_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id),
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8),
    quantity DECIMAL(20, 8),
    fee DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    address VARCHAR(100) NOT NULL,
    chain VARCHAR(20) NOT NULL,
    wallet_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Balances table
CREATE TABLE IF NOT EXISTS balances (
    user_id VARCHAR(50),
    asset VARCHAR(20),
    available DECIMAL(20, 8) DEFAULT 0,
    locked DECIMAL(20, 8) DEFAULT 0,
    PRIMARY KEY (user_id, asset)
);

-- Indexes
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_symbol ON orders(symbol);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_trades_order ON trades(order_id);
CREATE INDEX idx_wallets_user ON wallets(user_id);
EOF

# Run SQL
psql -U tigerex -d tigerex -f tables.sql
```

---

## Step 7: Configure Redis

```bash
# Start Redis
sudo systemctl start redis-server

# Enable Redis on boot
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping

# Should return: PONG
```

---

## Step 8: Start Services

### Start Production Engine (Port 5300)

```bash
# Create service file
sudo tee /etc/systemd/system/tigerex-engine.service > /dev/null <<EOF
[Unit]
Description=TigerEx Production Engine
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=~/TigerEx-
ExecStart=/home/$USER/TigerEx-/venv/bin/python backend/production-engine/engine.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl start tigerex-engine
sudo systemctl enable tigerex-engine
```

### Start Price Sync (Port 5200)

```bash
# Create service
sudo tee /etc/systemd/system/tigerex-price.service > /dev/null <<EOF
[Unit]
Description=TigerEx Price Sync
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=~/TigerEx-
ExecStart=/home/$USER/TigerEx-/venv/bin/python backend/price-sync/price_feed.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start
sudo systemctl start tigerex-price
sudo systemctl enable tigerex-price
```

### Start Wallet Service (Port 6000)

```bash
# Create service
sudo tee /etc/systemd/system/tigerex-wallet.service > /dev/null <<EOF
[Unit]
Description=TigerEx Wallet Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=~/TigerEx-
ExecStart=/home/$USER/TigerEx-/venv/bin/python custom-wallet/backend/wallet_service.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start
sudo systemctl start tigerex-wallet
sudo systemctl enable tigerex-wallet
```

---

## Step 9: Verify Services

```bash
# Check all services
sudo systemctl status tigerex-engine
sudo systemctl status tigerex-price
sudo systemctl status tigerex-wallet

# Test endpoints
curl http://localhost:5300/engine/health
curl http://localhost:5200/price/health
curl http://localhost:6000/wallet/health

# Expected: {"status": "ok", ...}
```

---

## Step 10: Configure Nginx

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/tigerex
```

**Add configuration:**

```nginx
upstream engine {
    server localhost:5300;
}

upstream price {
    server localhost:5200;
}

upstream wallet {
    server localhost:6000;
}

upstream exchange {
    server localhost:5900;
}

server {
    listen 80;
    server_name api.tigerex.com;

    location /engine {
        proxy_pass http://engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /price {
        proxy_pass http://price;
        proxy_set_header Host $host;
    }

    location /wallet {
        proxy_pass http://wallet;
        proxy_set_header Host $host;
    }

    location /exchange {
        proxy_pass http://exchange;
        proxy_set_header Host $host;
    }
}
```

**Enable site:**

```bash
# Enable configuration
sudo ln -s /etc/nginx/sites-available/tigerex /etc/nginx/sites-enabled/

# Test nginx
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## Docker Installation (Alternative)

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Create docker-compose.yml

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

  engine:
    build: 
      context: .
      dockerfile: Dockerfile.engine
    ports:
      - "5300:5300"
    environment:
      - DATABASE_URL=postgresql://tigerex:tigerex123@postgres:5432/tigerex
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  price-sync:
    build:
      context: .
      dockerfile: Dockerfile.price
    ports:
      - "5200:5200"

  wallet:
    build:
      context: .
      dockerfile: Dockerfile.wallet
    ports:
      - "6000:6000"

volumes:
  postgres_data:
```

**Start Docker:**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

## Troubleshooting

### Check Logs

```bash
# View service logs
journalctl -u tigerex-engine -f
journalctl -u tigerex-price -f
journalctl -u tigerex-wallet -f

# View nginx logs
tail -f /var/log/nginx/error.log
```

### Common Issues

**Database connection error:**
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
psql -U tigerex -d tigerex -h localhost
```

**Redis connection error:**
```bash
# Check Redis
sudo systemctl status redis-server

# Test
redis-cli ping
```

**Port already in use:**
```bash
# Find process using port
sudo lsof -i :5300

# Kill process
sudo kill -9 <PID>
```

---

## Next Steps

1. **Configure SSL/TLS** - Set up Let's Encrypt
2. **Setup Monitoring** - Configure Prometheus/Grafana
3. **Configure Backups** - Set up automated backups
4. **Security Hardening** - Configure firewall, fail2ban