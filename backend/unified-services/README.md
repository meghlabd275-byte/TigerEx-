# TigerEx Unified Services

This directory contains unified services that implement all features from major exchanges.

## Services

1. **Unified Data Fetcher Service** (`unified_fetcher_service.py`)
   - All market data fetchers
   - Futures data
   - Options data
   - Margin data
   - Staking/Earn data

2. **Complete User Operations Service** (`complete_user_operations.py`)
   - Account management
   - Trading operations
   - Margin trading
   - Futures trading
   - Wallet operations
   - Staking/Earn
   - Convert
   - Copy trading
   - Trading bots

3. **Complete Admin Operations Service** (`complete_admin_operations.py`)
   - User management
   - KYC management
   - Trading management
   - Market management
   - Liquidity management
   - Risk management
   - Financial management
   - System configuration
   - Analytics & reporting
   - Notifications
   - Compliance

## Running the Services

### Using Docker

```bash
docker build -t tigerex-unified-services .
docker run -p 8000:8000 tigerex-unified-services
```

### Using Python

```bash
pip install -r requirements.txt

# Run fetcher service
python unified_fetcher_service.py

# Run user operations service
python complete_user_operations.py

# Run admin operations service
python complete_admin_operations.py
```

## API Documentation

Once running, visit:
- Fetcher Service: http://localhost:8000/docs
- User Operations: http://localhost:8001/docs
- Admin Operations: http://localhost:8002/docs

## Integration

These services can be integrated with the existing TigerEx infrastructure through the API gateway.
