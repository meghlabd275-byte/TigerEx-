# 🚀 TigerEx Hex Quick Start Guide

Get TigerEx Hex up and running in minutes with this comprehensive quick start guide.

## 📋 Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Node.js** 18+ (for development)
- **Python** 3.11+ (for development)
- **Git** for version control

## ⚡ Quick Deployment

### 1. Clone Repository
```bash
git clone https://github.com/meghlabd275-byte/TigerEx-.git
cd TigerEx-
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### 3. Deploy with One Command
```bash
# For development
./deploy.sh development

# For production
./deploy.sh production
```

### 4. Access Your Exchange
- **Frontend**: http://localhost:3000
- **Hex Trading API**: http://localhost:8000
- **DEX Integration API**: http://localhost:8001
- **Admin Dashboard**: http://localhost:3001

## 🔧 Manual Setup (Advanced)

### Backend Services
```bash
# Start infrastructure
docker-compose up -d postgres redis rabbitmq

# Start Hex Trading Engine
cd backend/hex-trading-engine
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Start DEX Integration Service
cd ../dex-integration-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Mobile App
```bash
cd mobile-app
npm install
npm run start
```

## 🌟 Key Features

### Hex Trading
- **Smart Order Routing**: Automatically finds best prices across CEX and DEX
- **Real-time Price Comparison**: See CEX vs DEX prices instantly
- **Cross-chain Support**: Trade across 5+ blockchain networks
- **Unified Liquidity**: Access both centralized and decentralized liquidity

### Supported Networks
- **Ethereum** (Uniswap V3, SushiSwap)
- **Binance Smart Chain** (PancakeSwap)
- **Polygon** (QuickSwap)
- **Arbitrum** (Layer 2 scaling)
- **Avalanche** (Trader Joe)

### Trading Features
- Market and limit orders
- Stop-loss and take-profit
- Slippage protection
- Gas optimization
- Portfolio management

## 📊 Monitoring

Access monitoring dashboards:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002

## 🔒 Security

TigerEx Hex includes enterprise-grade security:
- Multi-validator cross-chain bridge
- Rate limiting and DDoS protection
- Encrypted communications
- Audit trails and monitoring

## 📱 Mobile Trading

Full trading capabilities on mobile:
- Native React Native app
- Real-time price feeds
- Portfolio tracking
- Push notifications

## 🛠️ Development

### API Documentation
- Hex Trading API: http://localhost:8000/docs
- DEX Integration API: http://localhost:8001/docs

### Testing
```bash
# Run backend tests
cd backend/hex-trading-engine
pytest

# Run frontend tests
cd frontend
npm test

# Run integration tests
docker-compose -f docker-compose.test.yml up
```

## 🆘 Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check logs
docker-compose logs -f

# Restart services
docker-compose restart
```

**Database connection issues:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Port conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Stop conflicting services
sudo systemctl stop apache2
```

## 📞 Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/meghlabd275-byte/TigerEx-/issues)
- **Discord**: [TigerEx Community](https://discord.gg/tigerex)

## 🚀 What's Next?

1. **Configure your trading pairs** in the admin dashboard
2. **Set up blockchain RPC endpoints** for better performance
3. **Enable monitoring** with Prometheus and Grafana
4. **Deploy to production** with proper SSL certificates
5. **Scale horizontally** with load balancers

---

**Welcome to the future of hybrid trading with TigerEx Hex!** 🐅⚡