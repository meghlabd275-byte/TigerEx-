# TigerEx Platform - Production Deployment Guide

## Quick Start

### 1. Prerequisites
- Docker 24.0+
- Docker Compose 2.20+
- PostgreSQL 14+
- Redis 7+
- Nginx 1.24+

### 2. Clone & Configure
```bash
git clone https://github.com/tigerex/platform.git
cd platform
cp .env.example .env
# Edit .env with your configuration
```

### 3. Deploy
```bash
docker-compose up -d
```

### 4. Verify
```bash
# Check all services
for port in {8115..8125}; do
  curl http://localhost:$port/health
done
```

## Service Ports
- 8115: Alpha Market Admin
- 8116: Copy Trading Admin
- 8117: DEX Integration Admin
- 8118: Liquidity Aggregator Admin
- 8119: NFT Marketplace Admin
- 8120: Institutional Services Admin
- 8121: Lending & Borrowing Admin
- 8122: Payment Gateway Admin
- 8123: Payment Gateway Service
- 8124: Advanced Trading Service
- 8125: DeFi Enhancements Service

For complete deployment guide, see DEPLOYMENT_GUIDE.md