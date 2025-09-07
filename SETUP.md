# TigerEx Setup Guide

This guide will help you set up and run the TigerEx cryptocurrency exchange platform on your local machine or server.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 50GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Required Software

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Node.js**: Version 18.0+
- **npm**: Version 9.0+
- **Git**: Latest version

### Optional Tools

- **Go**: Version 1.19+ (for backend development)
- **Rust**: Version 1.65+ (for trading engine)
- **Python**: Version 3.9+ (for analytics and scripts)
- **PostgreSQL Client**: For database management
- **Redis CLI**: For cache management

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/meghla121/TigerEx.git
cd TigerEx
```

### 2. Environment Setup

```bash
# Copy environment configuration
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

### 3. Install Dependencies

```bash
# Install all project dependencies
npm run install:all
```

### 4. Start the Platform

```bash
# For development environment
./scripts/deploy.sh development

# For staging environment
./scripts/deploy.sh staging

# For production environment
./scripts/deploy.sh production
```

### 5. Access the Platform

- **Web Application**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3100
- **Landing Pages**: http://localhost:3200
- **API Gateway**: http://localhost:8080

## 🔧 Detailed Setup

### Environment Configuration

Edit the `.env` file to configure your environment:

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
MONGO_PASSWORD=your_mongo_password

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key
REFRESH_TOKEN_SECRET=your_refresh_token_secret

# API Keys
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# Blockchain Configuration
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_infura_key
BITCOIN_RPC_URL=your_bitcoin_rpc_url

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_email_password
```

### Manual Service Setup

If you prefer to set up services manually:

#### 1. Database Setup

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run database migrations
npm run migrate

# Seed initial data (development only)
npm run seed
```

#### 2. Cache and Message Queue

```bash
# Start Redis and message queues
docker-compose up -d redis kafka rabbitmq
```

#### 3. Backend Services

```bash
# Start all backend services
docker-compose up -d \
  auth-service \
  trading-engine \
  wallet-service \
  kyc-service \
  notification-service \
  analytics-service \
  admin-service \
  blockchain-service \
  p2p-service \
  copy-trading-service
```

#### 4. Frontend Services

```bash
# Start frontend applications
docker-compose up -d \
  web-app \
  admin-dashboard \
  landing-pages
```

#### 5. API Gateway

```bash
# Start Nginx API gateway
docker-compose up -d nginx
```

## 🏗️ Development Setup

### Backend Development

#### Go Services (Auth, Wallet, Blockchain)

```bash
cd backend/auth-service
go mod download
go run main.go
```

#### C++ Trading Engine

```bash
cd backend/trading-engine
mkdir build && cd build
cmake ..
make
./TigerExTradingEngine
```

#### Python Services (KYC, Analytics)

```bash
cd backend/kyc-service
pip install -r requirements.txt
python main.py
```

#### Node.js Services (Notification, Admin)

```bash
cd backend/notification-service
npm install
npm run dev
```

### Frontend Development

#### Web Application (Next.js)

```bash
cd frontend/web-app
npm install
npm run dev
```

#### Admin Dashboard (React)

```bash
cd frontend/admin-dashboard
npm install
npm start
```

### Mobile Development

#### Android App

```bash
cd mobile/android
./gradlew assembleDebug
```

#### iOS App

```bash
cd mobile/ios
pod install
open TigerEx.xcworkspace
```

### Blockchain Development

#### Smart Contracts

```bash
cd blockchain/smart-contracts
npm install
npx hardhat compile
npx hardhat test
```

## 🧪 Testing

### Run All Tests

```bash
npm test
```

### Backend Tests

```bash
npm run test:backend
```

### Frontend Tests

```bash
npm run test:frontend
```

### Integration Tests

```bash
npm run test:integration
```

### Load Testing

```bash
npm run test:load
```

## 📊 Monitoring and Logging

### Access Monitoring Tools

- **Grafana**: http://localhost:3300 (admin/admin123)
- **Prometheus**: http://localhost:9090

### View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f auth-service
docker-compose logs -f trading-engine
```

### Health Checks

```bash
# Check service health
curl http://localhost:8080/health

# Check individual services
curl http://localhost:3001/health  # Auth service
curl http://localhost:3002/health  # Trading engine
curl http://localhost:3003/health  # Wallet service
```

## 🔒 Security Setup

### SSL Certificates (Production)

```bash
# Generate self-signed certificate (for testing)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/tigerex.key \
  -out ssl/tigerex.crt

# For production, use Let's Encrypt or commercial certificates
```

### Firewall Configuration

```bash
# Allow necessary ports
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8080  # API Gateway
sudo ufw enable
```

### Database Security

```bash
# Secure PostgreSQL
docker-compose exec postgres psql -U tigerex -c "ALTER USER tigerex PASSWORD 'new_secure_password';"

# Secure Redis
docker-compose exec redis redis-cli CONFIG SET requirepass "new_redis_password"
```

## 🚀 Production Deployment

### Server Requirements

- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 500GB+ SSD
- **Network**: 1Gbps+ connection
- **OS**: Ubuntu 20.04 LTS

### Production Setup

```bash
# Clone repository
git clone https://github.com/meghla121/TigerEx.git
cd TigerEx

# Set production environment
cp .env.production .env
nano .env

# Deploy to production
./scripts/deploy.sh production
```

### Load Balancer Setup (Optional)

```bash
# Install HAProxy
sudo apt install haproxy

# Configure load balancer
sudo nano /etc/haproxy/haproxy.cfg

# Restart HAProxy
sudo systemctl restart haproxy
```

### Database Backup

```bash
# Automated backup script
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/TigerEx/scripts/backup-database.sh
```

## 🛠️ Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check port usage
sudo netstat -tulpn | grep :3000

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:3000)
```

#### Docker Issues

```bash
# Clean Docker system
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U tigerex

# Reset database
docker-compose down
docker volume rm tigerex_postgres_data
docker-compose up -d postgres
npm run migrate
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory
```

### Service-Specific Issues

#### Trading Engine Not Starting

```bash
# Check C++ dependencies
cd backend/trading-engine
ldd build/TigerExTradingEngine

# Rebuild trading engine
make clean && make
```

#### Frontend Build Failures

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### WebSocket Connection Issues

```bash
# Check Nginx WebSocket configuration
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

## 📚 Additional Resources

### Documentation

- [API Documentation](./docs/api.md)
- [Database Schema](./docs/database.md)
- [Architecture Guide](./docs/architecture.md)
- [Security Guide](./docs/security.md)

### Development Tools

- [Postman Collection](./docs/postman-collection.json)
- [Database Migrations](./scripts/migrations/)
- [Test Data](./scripts/test-data/)

### Community

- [GitHub Issues](https://github.com/meghla121/TigerEx/issues)
- [Discord Server](https://discord.gg/tigerex)
- [Telegram Group](https://t.me/tigerex)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or need help:

1. Check the [troubleshooting section](#troubleshooting)
2. Search [existing issues](https://github.com/meghla121/TigerEx/issues)
3. Create a [new issue](https://github.com/meghla121/TigerEx/issues/new)
4. Contact support: support@tigerex.com

---

**Happy Trading! 🐅**
