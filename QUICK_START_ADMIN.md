# TigerEx Admin Features - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- PostgreSQL database running
- Redis running

### Step 1: Run Database Migrations (1 minute)

```bash
# Navigate to database directory
cd backend/database

# Run the new migrations
psql -U postgres -d tigerex -f migrations/2025_03_03_000035_create_liquidity_and_virtual_assets.sql
psql -U postgres -d tigerex -f migrations/2025_03_03_000036_insert_default_virtual_reserves.sql
```

### Step 2: Start Services (2 minutes)

```bash
# Start Virtual Liquidity Service
cd backend/virtual-liquidity-service
pip install -r requirements.txt
python src/main.py &

# Start Comprehensive Admin Service
cd ../comprehensive-admin-service
pip install -r requirements.txt
python src/main.py &
```

### Step 3: Verify Services (1 minute)

```bash
# Check Virtual Liquidity Service
curl http://localhost:8150/health

# Check Comprehensive Admin Service
curl http://localhost:8160/health

# Get virtual reserves
curl http://localhost:8150/api/reserves

# Get analytics overview
curl http://localhost:8160/api/admin/analytics/overview
```

## 🎯 Common Admin Tasks

### Task 1: List a New Token (30 seconds)

```bash
curl -X POST http://localhost:8160/api/admin/tokens/list \
  -H "Content-Type: application/json" \
  -d '{
    "token_symbol": "TIGER",
    "token_name": "Tiger Token",
    "token_standard": "ERC20",
    "blockchain_id": "ETH_MAINNET",
    "contract_address": "0x1234567890123456789012345678901234567890",
    "decimals": 18,
    "total_supply": "1000000000",
    "description": "TigerEx native token",
    "website": "https://tigerex.com",
    "logo_url": "https://tigerex.com/logo.png",
    "auto_create_liquidity_pool": true,
    "initial_liquidity_usdt": "1000000"
  }'
```

### Task 2: Create a Trading Pair (30 seconds)

```bash
curl -X POST http://localhost:8160/api/admin/trading-pairs \
  -H "Content-Type: application/json" \
  -d '{
    "base_asset": "TIGER",
    "quote_asset": "USDT",
    "trading_type": "spot",
    "min_order_size": "1",
    "min_price": "0.01",
    "price_precision": 4,
    "quantity_precision": 2,
    "maker_fee": "0.001",
    "taker_fee": "0.001",
    "auto_provide_liquidity": true,
    "virtual_liquidity_percentage": "0.7"
  }'
```

### Task 3: Integrate a New Blockchain (1 minute)

```bash
# EVM Blockchain (e.g., Base)
curl -X POST http://localhost:8160/api/admin/blockchains/evm \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Base",
    "symbol": "BASE",
    "blockchain_type": "evm",
    "network_type": "mainnet",
    "chain_id": 8453,
    "rpc_url": "https://mainnet.base.org",
    "explorer_url": "https://basescan.org",
    "consensus_mechanism": "Optimistic Rollup",
    "block_time": 2,
    "native_currency": "ETH"
  }'

# Non-EVM Blockchain (e.g., TON)
curl -X POST http://localhost:8160/api/admin/blockchains/non-evm \
  -H "Content-Type: application/json" \
  -d '{
    "name": "The Open Network",
    "symbol": "TON",
    "blockchain_type": "ton",
    "api_endpoint": "https://toncenter.com/api/v2",
    "explorer_url": "https://tonscan.org",
    "native_currency": "TON",
    "supports_smart_contracts": true
  }'
```

### Task 4: Create an IOU Token (1 minute)

```bash
curl -X POST http://localhost:8160/api/admin/tokens/list \
  -H "Content-Type: application/json" \
  -d '{
    "token_symbol": "LAUNCH",
    "token_name": "Launch Token",
    "token_standard": "ERC20",
    "blockchain_id": "ETH_MAINNET",
    "decimals": 18,
    "total_supply": "10000000",
    "description": "Pre-launch IOU token",
    "is_iou": true,
    "auto_create_liquidity_pool": true,
    "initial_liquidity_usdt": "500000"
  }'
```

### Task 5: Create a Liquidity Pool (30 seconds)

```bash
curl -X POST http://localhost:8160/api/admin/liquidity-pools \
  -H "Content-Type: application/json" \
  -d '{
    "base_asset": "TIGER",
    "quote_asset": "ETH",
    "initial_base_amount": "1000000",
    "initial_quote_amount": "500",
    "virtual_base_percentage": "0.7",
    "virtual_quote_percentage": "0.7",
    "fee_rate": "0.003",
    "is_public": true
  }'
```

### Task 6: Adjust Virtual Reserves (30 seconds)

```bash
curl -X POST http://localhost:8160/api/admin/virtual-reserves/adjust \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "USDT",
    "adjustment_amount": "10000000",
    "adjustment_type": "add",
    "reason": "Increased trading volume"
  }'
```

## 📊 Monitoring & Analytics

### Get Complete Overview

```bash
curl http://localhost:8160/api/admin/analytics/overview | jq
```

### Get Virtual Reserves Status

```bash
curl http://localhost:8150/api/reserves | jq
```

### Get Liquidity Pools

```bash
curl http://localhost:8150/api/pools | jq
```

### Get IOU Tokens

```bash
curl http://localhost:8150/api/iou-tokens | jq
```

### Get All Blockchains

```bash
curl http://localhost:8160/api/admin/blockchains | jq
```

### Get All Trading Pairs

```bash
curl http://localhost:8160/api/admin/trading-pairs | jq
```

## 🎨 Pre-configured Resources

### Virtual Reserves (Ready to Use)
- ✅ USDT: $100M (20% backed)
- ✅ USDC: $100M (20% backed)
- ✅ ETH: 50K (15% backed)
- ✅ BTC: 2K (15% backed)
- ✅ BNB: 100K (10% backed)
- ✅ MATIC: 10M (10% backed)
- ✅ AVAX: 500K (10% backed)
- ✅ SOL: 500K (10% backed)
- ✅ DAI: $50M (20% backed)
- ✅ BUSD: $50M (20% backed)

### Supported Blockchains (Pre-configured)
- ✅ Ethereum Mainnet
- ✅ Binance Smart Chain
- ✅ Polygon
- ✅ Arbitrum One
- ✅ Optimism
- ✅ Avalanche C-Chain
- ✅ Fantom Opera
- ✅ Solana
- ✅ TigerChain (Custom)

### Example Liquidity Pools (Pre-configured)
- ✅ TIGER/USDT (70% virtual liquidity)
- ✅ TIGER/ETH (70% virtual liquidity)
- ✅ TIGER/BTC (70% virtual liquidity)

### Example IOU Tokens (Pre-configured)
- ✅ NEWTOKEN-IOU (with USDT pool, 90% virtual)
- ✅ LAUNCH-IOU (with USDT pool, 90% virtual)

## 🔧 Troubleshooting

### Service Not Starting

```bash
# Check if ports are available
lsof -i :8150
lsof -i :8160

# Check logs
tail -f logs/virtual-liquidity-service.log
tail -f logs/comprehensive-admin-service.log
```

### Database Connection Issues

```bash
# Test database connection
psql -U postgres -d tigerex -c "SELECT COUNT(*) FROM virtual_asset_reserves;"

# Check if migrations ran
psql -U postgres -d tigerex -c "\dt"
```

### Cannot Create Liquidity Pool

```bash
# Check virtual reserves
curl http://localhost:8150/api/reserves

# Check if reserve has enough available liquidity
curl http://localhost:8150/api/reserves/VUSDT_RESERVE_001
```

## 📚 API Documentation

Once services are running, access interactive API documentation:

- Virtual Liquidity Service: http://localhost:8150/docs
- Comprehensive Admin Service: http://localhost:8160/docs

## 🎯 What You Can Do Now

✅ List any token/coin on the exchange
✅ Create trading pairs for all trading types
✅ Integrate any EVM blockchain
✅ Integrate custom Web3 blockchains (Pi, TON, etc.)
✅ Create liquidity pools with virtual liquidity
✅ Manage virtual asset reserves
✅ Create and manage IOU tokens
✅ Monitor all exchange metrics
✅ Automatic liquidity provision
✅ Automatic reserve rebalancing

## 🚀 Production Deployment

For production deployment, see:
- `ADMIN_FEATURES_IMPLEMENTATION.md` - Complete implementation guide
- `DEPLOYMENT_GUIDE.md` - Production deployment guide
- `docker-compose.yml` - Docker configuration

## 💡 Tips

1. **Always check virtual reserves** before creating large liquidity pools
2. **Monitor utilization rates** to prevent reserve depletion
3. **Use auto-rebalancing** for hands-off reserve management
4. **Set appropriate backing ratios** based on risk tolerance
5. **Enable IOU conversion** only when real tokens are available
6. **Test on testnet** before mainnet integration
7. **Monitor admin activity logs** for audit trails

## 📞 Support

Need help? Check:
- API Documentation: `/docs` endpoint
- Implementation Guide: `ADMIN_FEATURES_IMPLEMENTATION.md`
- Database Schema: `backend/database/migrations/`
- Service Logs: Check console output or log files

---

**Ready to manage your exchange like a pro! 🎉**