#!/usr/bin/env python3

"""
TigerEx Unified Exchange Fetchers
Complete implementation of all fetcher endpoints for all major exchanges
Enhanced with additional exchanges and comprehensive functionality
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

class BybitFetcher(BaseExchangeFetcher):
    """Bybit exchange fetcher implementation"""
    
    BASE_URL = "https://api.bybit.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/v5/market/orderbook"
        params = {"category": "spot", "symbol": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('result', {})
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/v5/market/recent-trade"
        params = {"category": "spot", "symbol": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('result', {}).get('list', [])
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/v5/market/kline"
        params = {"category": "spot", "symbol": symbol, "interval": interval, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('result', {}).get('list', [])
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        url = f"{self.BASE_URL}/v5/market/tickers"
        params = {"category": "spot"}
        if symbol:
            params["symbol"] = symbol
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('result', {})
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/v5/account/wallet-balance"
        headers = {"X-BAPI-API-KEY": self.api_key}
        async with self.session.get(url, headers=headers) as response:
            data = await response.json()
            return data.get('result', {})

class OKXFetcher(BaseExchangeFetcher):
    """OKX exchange fetcher implementation"""
    
    BASE_URL = "https://www.okx.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/api/v5/market/books"
        params = {"instId": symbol, "sz": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [{}])[0] if data.get('data') else {}
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/api/v5/market/trades"
        params = {"instId": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/api/v5/market/candles"
        params = {"instId": symbol, "bar": interval, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        url = f"{self.BASE_URL}/api/v5/market/ticker"
        params = {"instType": "SPOT"}
        if symbol:
            params["instId"] = symbol
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [{}])[0] if data.get('data') else {}
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/api/v5/account/balance"
        headers = {"OK-ACCESS-KEY": self.api_key}
        async with self.session.get(url, headers=headers) as response:
            data = await response.json()
            return data.get('data', [{}])[0] if data.get('data') else {}

class KuCoinFetcher(BaseExchangeFetcher):
    """KuCoin exchange fetcher implementation"""
    
    BASE_URL = "https://api.kucoin.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/api/v1/market/orderbook/level2"
        params = {"symbol": symbol}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', {})
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/api/v1/market/histories"
        params = {"symbol": symbol, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/api/v1/market/candles"
        params = {"symbol": symbol, "type": interval, "limit": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        if symbol:
            url = f"{self.BASE_URL}/api/v1/market/stats"
            params = {"symbol": symbol}
        else:
            url = f"{self.BASE_URL}/api/v1/market/allTickers"
            params = {}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', {})
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/api/v1/accounts"
        headers = {"KC-API-KEY": self.api_key}
        async with self.session.get(url, headers=headers) as response:
            data = await response.json()
            return data.get('data', {})

class HuobiFetcher(BaseExchangeFetcher):
    """Huobi exchange fetcher implementation"""
    
    BASE_URL = "https://api.huobi.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/market/depth"
        params = {"symbol": symbol.lower(), "type": "step0", "depth": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/market/history/trade"
        params = {"symbol": symbol.lower(), "size": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/market/history/kline"
        params = {"symbol": symbol.lower(), "period": interval, "size": limit}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        if symbol:
            url = f"{self.BASE_URL}/market/detail/merged"
            params = {"symbol": symbol.lower()}
        else:
            url = f"{self.BASE_URL}/market/tickers"
            params = {}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/v1/account/accounts"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(url, headers=headers) as response:
            data = await response.json()
            return data.get('data', {})

class KrakenFetcher(BaseExchangeFetcher):
    """Kraken exchange fetcher implementation"""
    
    BASE_URL = "https://api.kraken.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/0/public/Depth"
        params = {"pair": symbol, "count": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/0/public/Trades"
        params = {"pair": symbol, "count": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        url = f"{self.BASE_URL}/0/public/OHLC"
        params = {"pair": symbol, "interval": interval, "count": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        if symbol:
            url = f"{self.BASE_URL}/0/public/Ticker"
            params = {"pair": symbol}
        else:
            url = f"{self.BASE_URL}/0/public/Ticker"
            params = {}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/0/private/Balance"
        headers = {"API-Key": self.api_key}
        async with self.session.post(url, headers=headers) as response:
            return await response.json()

class CoinbaseFetcher(BaseExchangeFetcher):
    """Coinbase exchange fetcher implementation"""
    
    BASE_URL = "https://api.pro.coinbase.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/products/{symbol}/book"
        params = {"level": 2}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/products/{symbol}/trades"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        # Map intervals to Coinbase granularity
        granularity_map = {
            '1m': 60, '5m': 300, '15m': 900, '1h': 3600,
            '6h': 21600, '1d': 86400
        }
        granularity = granularity_map.get(interval, 3600)
        
        url = f"{self.BASE_URL}/products/{symbol}/candles"
        params = {"granularity": granularity}
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            # Coinbase returns data in reverse order
            return list(reversed(data[-limit:])) if len(data) > limit else list(reversed(data))
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        if symbol:
            url = f"{self.BASE_URL}/products/{symbol}/ticker"
        else:
            url = f"{self.BASE_URL}/products"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/accounts"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

class GeminiFetcher(BaseExchangeFetcher):
    """Gemini exchange fetcher implementation"""
    
    BASE_URL = "https://api.gemini.com"
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book depth"""
        url = f"{self.BASE_URL}/v1/book/{symbol}"
        params = {"limit_bids": limit, "limit_asks": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades"""
        url = f"{self.BASE_URL}/v1/trades/{symbol}"
        params = {"limit_trades": limit}
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get kline/candlestick data"""
        # Map intervals to Gemini timeframes
        timeframe_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h',
            '1d': '1d'
        }
        timeframe = timeframe_map.get(interval, '1h')
        
        url = f"{self.BASE_URL}/v2/candles/{symbol}/{timeframe}"
        async with self.session.get(url) as response:
            data = await response.json()
            return data[-limit:] if len(data) > limit else data
    
    async def get_ticker_24hr(self, symbol: str = None) -> Dict:
        """Get 24hr ticker statistics"""
        if symbol:
            url = f"{self.BASE_URL}/v1/pubticker/{symbol}"
        else:
            url = f"{self.BASE_URL}/v1/symbols"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def get_account_balance(self) -> Dict:
        """Get account information"""
        url = f"{self.BASE_URL}/v1/balances"
        headers = {"X-GEMINI-APIKEY": self.api_key}
        async with self.session.get(url, headers=headers) as response:
            return await response.json()

class UnifiedExchangeFetcher:
    """Unified fetcher that routes requests to appropriate exchange"""
    
    def __init__(self):
        self.fetchers = {}
        self.supported_exchanges = {
            'binance': BinanceFetcher,
            'bybit': BybitFetcher,
            'okx': OKXFetcher,
            'kucoin': KuCoinFetcher,
            'huobi': HuobiFetcher,
            'kraken': KrakenFetcher,
            'coinbase': CoinbaseFetcher,
            'gemini': GeminiFetcher
        }
    
    def add_exchange(self, exchange_name: str, fetcher: BaseExchangeFetcher):
        """Add an exchange fetcher"""
        self.fetchers[exchange_name.lower()] = fetcher
    
    def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges"""
        return list(self.supported_exchanges.keys())
    
    async def get_order_book(self, exchange: str, symbol: str, limit: int = 100) -> Dict:
        """Get order book from specified exchange"""
        fetcher_class = self.supported_exchanges.get(exchange.lower())
        if not fetcher_class:
            raise ValueError(f"Exchange {exchange} not supported")
        
        async with fetcher_class() as fetcher:
            return await fetcher.get_order_book(symbol, limit)
    
    async def get_recent_trades(self, exchange: str, symbol: str, limit: int = 500) -> List[Dict]:
        """Get recent trades from specified exchange"""
        fetcher_class = self.supported_exchanges.get(exchange.lower())
        if not fetcher_class:
            raise ValueError(f"Exchange {exchange} not supported")
        
        async with fetcher_class() as fetcher:
            return await fetcher.get_recent_trades(symbol, limit)
    
    async def get_klines(self, exchange: str, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """Get klines from specified exchange"""
        fetcher_class = self.supported_exchanges.get(exchange.lower())
        if not fetcher_class:
            raise ValueError(f"Exchange {exchange} not supported")
        
        async with fetcher_class() as fetcher:
            return await fetcher.get_klines(symbol, interval, limit)
    
    async def get_ticker_24hr(self, exchange: str, symbol: str = None) -> Dict:
        """Get 24hr ticker from specified exchange"""
        fetcher_class = self.supported_exchanges.get(exchange.lower())
        if not fetcher_class:
            raise ValueError(f"Exchange {exchange} not supported")
        
        async with fetcher_class() as fetcher:
            return await fetcher.get_ticker_24hr(symbol)
    
    async def get_account_balance(self, exchange: str, api_key: str, api_secret: str) -> Dict:
        """Get account balance from specified exchange"""
        fetcher_class = self.supported_exchanges.get(exchange.lower())
        if not fetcher_class:
            raise ValueError(f"Exchange {exchange} not supported")
        
        async with fetcher_class(api_key, api_secret) as fetcher:
            return await fetcher.get_account_balance()
    
    async def compare_tickers(self, symbol: str, exchanges: List[str] = None) -> Dict:
        """Compare ticker data across multiple exchanges"""
        if not exchanges:
            exchanges = self.get_supported_exchanges()
        
        comparison = {}
        for exchange in exchanges:
            try:
                ticker_data = await self.get_ticker_24hr(exchange, symbol)
                comparison[exchange] = ticker_data
            except Exception as e:
                comparison[exchange] = {'error': str(e)}
        
        return comparison

# Example usage
async def main():
    """Example usage of unified fetcher"""
    unified = UnifiedExchangeFetcher()
    
    # Compare BTC/USDT across multiple exchanges
    symbol = "BTCUSDT"
    exchanges = ['binance', 'bybit', 'okx']
    
    comparison = await unified.compare_tickers(symbol, exchanges)
    print(f"Ticker comparison for {symbol}:")
    for exchange, data in comparison.items():
        print(f"{exchange}: {data}")

if __name__ == "__main__":
    asyncio.run(main())