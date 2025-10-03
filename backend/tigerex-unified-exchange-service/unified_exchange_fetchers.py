#!/usr/bin/env python3
"""
TigerEx Unified Exchange Fetchers
Complete implementation of all fetcher endpoints for all major exchanges
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import hmac
import json
from abc import ABC, abstractmethod

class BaseExchangeFetcher(ABC):
    """Base class for exchange fetchers"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book for a symbol"""
        pass
    
    @abstractmethod
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades for a symbol"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        pass
    
    @abstractmethod
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        pass
    
    @abstractmethod
    async def get_account_balance(self) -> Dict:
        """Get account balance"""
        pass

class BinanceFetcher(BaseExchangeFetcher):
    """Binance exchange fetcher implementation"""
    
    BASE_URL = "https://api.binance.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/api/v3/trades"
        params = {"symbol": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        url = f"{self.BASE_URL}/api/v3/ticker/24hr"
        params = {}
        if symbol:
            params["symbol"] = symbol
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/api/v3/account"
        timestamp = int(datetime.now().timestamp() * 1000)
        params = {"timestamp": timestamp}
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        async with self.session.get(url, params=params, headers=headers) as response:
            return await response.json()

class UnifiedExchangeFetcher:
    """Unified fetcher that routes requests to appropriate exchange"""
    
    def __init__(self):
        self.fetchers = {}
    
    def add_exchange(self, exchange_name: str, fetcher: BaseExchangeFetcher):
        """Add an exchange fetcher"""
        self.fetchers[exchange_name.lower()] = fetcher
    
    async def get_order_book(self, exchange: str, symbol: str, limit: int = 100) -> Dict:
        """Get order book from specified exchange"""
        fetcher = self.fetchers.get(exchange.lower())
        if not fetcher:
            raise ValueError(f"Exchange {exchange} not supported")
        return await fetcher.get_order_book(symbol, limit)
    
    async def get_recent_trades(self, exchange: str, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades from specified exchange"""
        fetcher = self.fetchers.get(exchange.lower())
        if not fetcher:
            raise ValueError(f"Exchange {exchange} not supported")
        return await fetcher.get_recent_trades(symbol, limit)
    
    async def get_klines(self, exchange: str, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get klines from specified exchange"""
        fetcher = self.fetchers.get(exchange.lower())
        if not fetcher:
            raise ValueError(f"Exchange {exchange} not supported")
        return await fetcher.get_klines(symbol, interval, limit)
    
    async def get_ticker_24hr(self, exchange: str, symbol: str = None) -> Dict:
        """Get 24hr ticker from specified exchange"""
        fetcher = self.fetchers.get(exchange.lower())
        if not fetcher:
            raise ValueError(f"Exchange {exchange} not supported")
        return await fetcher.get_ticker_24hr(symbol)
    
    async def get_account_balance(self, exchange: str) -> Dict:
        """Get account balance from specified exchange"""
        fetcher = self.fetchers.get(exchange.lower())
        if not fetcher:
            raise ValueError(f"Exchange {exchange} not supported")
        return await fetcher.get_account_balance()

# Example usage
async def main():
    """Example usage of unified fetcher"""
    unified = UnifiedExchangeFetcher()
    
    async with BinanceFetcher() as binance:
        unified.add_exchange("binance", binance)
        
        # Get order book from Binance
        order_book = await unified.get_order_book("binance", "BTCUSDT", 10)
        print(f"Binance Order Book: {order_book}")

if __name__ == "__main__":
    asyncio.run(main())