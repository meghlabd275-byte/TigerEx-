# TigerEx Unified Exchange Service

## Overview

The TigerEx Unified Exchange Service provides a comprehensive, unified API interface for interacting with all major cryptocurrency exchanges. This service implements complete feature parity with Binance, Bitfinex, OKX, Bybit, KuCoin, Bitget, MEXC, BitMart, and CoinW.

## Features

### 1. Unified Fetchers (`unified_exchange_fetchers.py`)
- **Market Data**: Order books, trades, klines, tickers, and more
- **Account Data**: Balances, positions, orders, and trade history
- **Wallet Data**: Deposits, withdrawals, transfers, and addresses

### 2. Unified User Operations (`unified_user_operations.py`)
- **Trading**: Place, cancel, modify orders across all exchanges
- **Order Types**: LIMIT, MARKET, STOP_LOSS, TAKE_PROFIT
- **Wallet Management**: Deposits, withdrawals, transfers
- **Advanced Features**: Margin trading, futures, options

### 3. Unified Admin Operations (`unified_admin_operations.py`)
- **User Management**: Create, manage, and monitor sub-accounts
- **API Key Management**: Create, modify, delete API keys
- **Security**: IP restrictions, permissions, access control
- **System Management**: Status monitoring, configuration

## Supported Exchanges

| Exchange | Fetchers | User Ops | Admin Ops | Status |
|----------|----------|----------|-----------|--------|
| Binance | ✅ | ✅ | ✅ | Complete |
| Bitfinex | ✅ | ✅ | ✅ | Complete |
| OKX | ✅ | ✅ | ✅ | Complete |
| Bybit | ✅ | ✅ | ✅ | Complete |
| KuCoin | ✅ | ✅ | ✅ | Complete |
| Bitget | ✅ | ✅ | ✅ | Complete |
| MEXC | ✅ | ✅ | ✅ | Complete |
| BitMart | ✅ | ✅ | ✅ | Complete |
| CoinW | ✅ | ✅ | ✅ | Complete |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Fetcher Example

```python
import asyncio
from unified_exchange_fetchers import UnifiedExchangeFetcher, BinanceFetcher

async def main():
    unified = UnifiedExchangeFetcher()
    
    async with BinanceFetcher() as binance:
        unified.add_exchange("binance", binance)
        
        # Get order book
        order_book = await unified.get_order_book("binance", "BTCUSDT", 10)
        print(f"Order Book: {order_book}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Trading Example

```python
import asyncio
from unified_user_operations import (
    UnifiedUserOperations, 
    BinanceUserOperations,
    OrderSide, 
    OrderType
)

async def main():
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    
    unified = UnifiedUserOperations()
    
    async with BinanceUserOperations(api_key, api_secret) as binance_ops:
        unified.add_exchange("binance", binance_ops)
        
        # Place a limit order
        result = await unified.place_order(
            "binance",
            "BTCUSDT",
            OrderSide.BUY,
            OrderType.LIMIT,
            0.001,
            50000.0
        )
        print(f"Order placed: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Admin Operations Example

```python
import asyncio
from unified_admin_operations import (
    UnifiedAdminOperations,
    BinanceAdminOperations
)

async def main():
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    
    unified = UnifiedAdminOperations()
    
    async with BinanceAdminOperations(api_key, api_secret) as binance_admin:
        unified.add_exchange("binance", binance_admin)
        
        # Create sub-account
        sub_account = await unified.create_sub_account(
            "binance",
            "subaccount@example.com"
        )
        print(f"Sub-account created: {sub_account}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Coverage

### Fetchers (150+ endpoints)
- Market data: 40+ endpoints
- Account data: 60+ endpoints
- Wallet data: 50+ endpoints

### User Operations (100+ endpoints)
- Trading: 50+ endpoints
- Wallet: 30+ endpoints
- Margin/Futures: 20+ endpoints

### Admin Operations (80+ endpoints)
- User management: 30+ endpoints
- System management: 25+ endpoints
- Security: 25+ endpoints

## Performance

- **Async/Await**: All operations are asynchronous for maximum performance
- **Connection Pooling**: Efficient HTTP connection management
- **Rate Limiting**: Built-in rate limit handling per exchange
- **Error Handling**: Comprehensive error handling and retry logic

## Security

- **API Key Encryption**: All API keys are encrypted at rest
- **Signature Generation**: Proper HMAC-SHA256 signature for all authenticated requests
- **IP Whitelisting**: Support for IP restrictions
- **Permission Management**: Granular API key permissions

## License

Copyright © 2025 TigerEx. All rights reserved.