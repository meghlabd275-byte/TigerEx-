"""
TigerEx Complete Exchange Fetchers System
Comprehensive implementation of all major exchange fetchers with unique functionality
Includes Binance, OKX, Bybit, Coinbase, KuCoin, Bitfinex, Huobi, Gemini, MEXC, BitGet
"""

import asyncio
import aiohttp
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class BaseExchangeFetcher:
    """Base class for all exchange fetchers"""
    
    def __init__(self, exchange_name: str, api_key: str = None, api_secret: str = None, passphrase: str = None):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = self.get_base_url()
        self.session = None
    
    def get_base_url(self) -> str:
        raise NotImplementedError
    
    async def _create_session(self):
        """Create aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to exchange API"""
        await self._create_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, params=params, json=data, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API request failed: {response.status} - {await response.text()}")
                return await response.json()
        except Exception as e:
            logger.error(f"Request failed for {self.exchange_name}: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol"""
        raise NotImplementedError
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book data"""
        raise NotImplementedError
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades"""
        raise NotImplementedError
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs"""
        raise NotImplementedError
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        raise NotImplementedError
    
    async def get_24h_stats(self, symbol: str) -> Dict[str, Any]:
        """Get 24-hour statistics"""
        raise NotImplementedError
    
    async def get_server_time(self) -> int:
        """Get server time"""
        raise NotImplementedError

class BinanceFetcher(BaseExchangeFetcher):
    """Binance exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("binance", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.binance.com"
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate signature for authenticated requests"""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            # 24hr ticker
            ticker_url = "/api/v3/ticker/24hr"
            params = {"symbol": symbol.replace("/", "")}
            ticker_data = await self._make_request("GET", ticker_url, params)
            
            # Price ticker
            price_url = "/api/v3/ticker/price"
            price_data = await self._make_request("GET", price_url, params)
            
            # Book ticker
            book_url = "/api/v3/ticker/bookTicker"
            book_data = await self._make_request("GET", book_url, params)
            
            return {
                "symbol": ticker_data["symbol"],
                "price": float(price_data["price"]),
                "change_24h": float(ticker_data["priceChange"]),
                "change_percent_24h": float(ticker_data["priceChangePercent"]),
                "volume_24h": float(ticker_data["volume"]),
                "quote_volume_24h": float(ticker_data["quoteVolume"]),
                "high_24h": float(ticker_data["highPrice"]),
                "low_24h": float(ticker_data["lowPrice"]),
                "open_24h": float(ticker_data["openPrice"]),
                "close_24h": float(ticker_data["prevClosePrice"]),
                "bid_price": float(book_data["bidPrice"]),
                "bid_qty": float(book_data["bidQty"]),
                "ask_price": float(book_data["askPrice"]),
                "ask_qty": float(book_data["askQty"]),
                "count": int(ticker_data["count"])
            }
        except Exception as e:
            logger.error(f"Binance ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            url = "/api/v3/depth"
            params = {"symbol": symbol.replace("/", ""), "limit": min(limit, 5000)}
            data = await self._make_request("GET", url, params)
            
            return {
                "symbol": data["symbol"],
                "bids": [[float(price), float(qty)] for price, qty in data["bids"]],
                "asks": [[float(price), float(qty)] for price, qty in data["asks"]],
                "last_update_id": data["lastUpdateId"]
            }
        except Exception as e:
            logger.error(f"Binance orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            url = "/api/v3/trades"
            params = {"symbol": symbol.replace("/", ""), "limit": min(limit, 1000)}
            data = await self._make_request("GET", url, params)
            
            return [
                {
                    "id": trade["id"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["qty"]),
                    "time": trade["time"],
                    "is_buyer_maker": trade["isBuyerMaker"],
                    "is_best_match": trade["isBestMatch"]
                }
                for trade in data
            ]
        except Exception as e:
            logger.error(f"Binance trades error: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        try:
            url = "/api/v3/klines"
            params = {
                "symbol": symbol.replace("/", ""),
                "interval": interval,
                "limit": min(limit, 1000)
            }
            data = await self._make_request("GET", url, params)
            
            return [
                {
                    "open_time": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": k[6],
                    "quote_asset_volume": float(k[7]),
                    "number_of_trades": k[8],
                    "taker_buy_base_volume": float(k[9]),
                    "taker_buy_quote_volume": float(k[10]),
                }
                for k in data
            ]
        except Exception as e:
            logger.error(f"Binance klines error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/api/v3/exchangeInfo"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["baseAsset"],
                    "quote_asset": pair["quoteAsset"],
                    "status": pair["status"],
                    "base_asset_precision": pair["baseAssetPrecision"],
                    "quote_precision": pair["quotePrecision"],
                    "quote_asset_precision": pair["quoteAssetPrecision"],
                    "min_qty": float(pair["filters"][0]["minQty"]),
                    "max_qty": float(pair["filters"][1]["maxQty"]),
                    "step_size": float(pair["filters"][2]["stepSize"]),
                    "min_notional": float(pair["filters"][10]["minNotional"])
                }
                for pair in data["symbols"]
                if pair["status"] == "TRADING"
            ]
        except Exception as e:
            logger.error(f"Binance trading pairs error: {e}")
            raise

class OKXFetcher(BaseExchangeFetcher):
    """OKX exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        super().__init__("okx", api_key, api_secret, passphrase)
    
    def get_base_url(self) -> str:
        return "https://www.okx.com"
    
    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = "") -> str:
        """Generate signature for OKX API"""
        message = timestamp + method + endpoint + body
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            # Convert symbol format (BTC/USDT -> BTC-USDT)
            okx_symbol = symbol.replace("/", "-")
            url = "/api/v5/market/ticker"
            params = {"instId": okx_symbol}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "0" or not data.get("data"):
                raise Exception(f"OKX API error: {data}")
            
            ticker = data["data"][0]
            
            return {
                "symbol": ticker["instId"],
                "price": float(ticker["last"]),
                "change_24h": float(ticker["sodUtc8"]) if ticker["sodUtc8"] else 0,
                "change_percent_24h": float(ticker["changePercent24h"]) if ticker["changePercent24h"] else 0,
                "volume_24h": float(ticker["vol24h"]) if ticker["vol24h"] else 0,
                "quote_volume_24h": float(ticker["volCcy24h"]) if ticker["volCcy24h"] else 0,
                "high_24h": float(ticker["high24h"]) if ticker["high24h"] else 0,
                "low_24h": float(ticker["low24h"]) if ticker["low24h"] else 0,
                "open_24h": float(ticker["open24h"]) if ticker["open24h"] else 0,
                "bid_price": float(ticker["bidPx"]) if ticker["bidPx"] else 0,
                "bid_qty": float(ticker["bidSz"]) if ticker["bidSz"] else 0,
                "ask_price": float(ticker["askPx"]) if ticker["askPx"] else 0,
                "ask_qty": float(ticker["askSz"]) if ticker["askSz"] else 0,
                "sod_utc8": float(ticker["sodUtc8"]) if ticker["sodUtc8"] else 0
            }
        except Exception as e:
            logger.error(f"OKX ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            okx_symbol = symbol.replace("/", "-")
            url = "/api/v5/market/books"
            params = {"instId": okx_symbol, "sz": str(min(limit, 400))}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "0" or not data.get("data"):
                raise Exception(f"OKX API error: {data}")
            
            book = data["data"][0]
            
            return {
                "symbol": book["instId"],
                "bids": [[float(bid[0]), float(bid[1])] for bid in book["bids"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in book["asks"]],
                "ts": book["ts"]
            }
        except Exception as e:
            logger.error(f"OKX orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            okx_symbol = symbol.replace("/", "-")
            url = "/api/v5/market/trades"
            params = {"instId": okx_symbol, "limit": str(min(limit, 500))}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "0" or not data.get("data"):
                return []
            
            return [
                {
                    "id": trade["tradeId"],
                    "price": float(trade["px"]),
                    "quantity": float(trade["sz"]),
                    "time": int(trade["ts"]),
                    "side": trade["side"]
                }
                for trade in data["data"]
            ]
        except Exception as e:
            logger.error(f"OKX trades error: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        try:
            okx_symbol = symbol.replace("/", "-")
            url = "/api/v5/market/history-candles"
            params = {
                "instId": okx_symbol,
                "bar": interval,
                "limit": str(min(limit, 300))
            }
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "0" or not data.get("data"):
                return []
            
            return [
                {
                    "timestamp": int(k[0]),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "volume_currency": float(k[6]),
                    "volume_currency_quote": float(k[7])
                }
                for k in data["data"]
            ]
        except Exception as e:
            logger.error(f"OKX klines error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/api/v5/public/instruments"
            params = {"instType": "SPOT"}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "0" or not data.get("data"):
                return []
            
            return [
                {
                    "symbol": pair["instId"],
                    "base_asset": pair["baseCcy"],
                    "quote_asset": pair["quoteCcy"],
                    "status": " trading" if pair["state"] == "live" else pair["state"],
                    "min_size": float(pair["minSz"]),
                    "max_size": float(pair["maxSz"]),
                    "lot_size": float(pair["lotSz"]),
                    "tick_size": float(pair["tickSz"]),
                    "category": pair["category"]
                }
                for pair in data["data"]
                if pair["state"] == "live"
            ]
        except Exception as e:
            logger.error(f"OKX trading pairs error: {e}")
            raise

class BybitFetcher(BaseExchangeFetcher):
    """Bybit exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("bybit", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.bybit.com"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            url = "/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol.replace("/", "")}
            data = await self._make_request("GET", url, params)
            
            if data.get("retCode") != 0 or not data.get("result", {}).get("list"):
                raise Exception(f"Bybit API error: {data}")
            
            ticker = data["result"]["list"][0]
            
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["lastPrice"]),
                "change_24h": float(ticker["price1hPct"]) if ticker.get("price1hPct") else 0,
                "change_percent_24h": float(ticker["price24hPcnt"]) if ticker.get("price24hPcnt") else 0,
                "volume_24h": float(ticker["turnover24h"]) if ticker.get("turnover24h") else 0,
                "quote_volume_24h": float(ticker["volume24h"]) if ticker.get("volume24h") else 0,
                "high_24h": float(ticker["highPrice24h"]) if ticker.get("highPrice24h") else 0,
                "low_24h": float(ticker["lowPrice24h"]) if ticker.get("lowPrice24h") else 0,
                "open_24h": float(ticker["openPrice"]) if ticker.get("openPrice") else 0,
                "bid_price": float(ticker["bid1Price"]) if ticker.get("bid1Price") else 0,
                "bid_qty": float(ticker["bid1Size"]) if ticker.get("bid1Size") else 0,
                "ask_price": float(ticker["ask1Price"]) if ticker.get("ask1Price") else 0,
                "ask_qty": float(ticker["ask1Size"]) if ticker.get("ask1Size") else 0
            }
        except Exception as e:
            logger.error(f"Bybit ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            url = "/v5/market/orderbook"
            params = {"category": "spot", "symbol": symbol.replace("/", ""), "limit": str(min(limit, 500))}
            data = await self._make_request("GET", url, params)
            
            if data.get("retCode") != 0 or not data.get("result", {}).get("b"):
                raise Exception(f"Bybit API error: {data}")
            
            result = data["result"]
            
            return {
                "symbol": result["s"],
                "bids": [[float(bid[0]), float(bid[1])] for bid in result["b"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in result["a"]],
                "ts": result["ts"]
            }
        except Exception as e:
            logger.error(f"Bybit orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            url = "/v5/market/recent-trade"
            params = {"category": "spot", "symbol": symbol.replace("/", ""), "limit": str(min(limit, 60))}
            data = await self._make_request("GET", url, params)
            
            if data.get("retCode") != 0 or not data.get("result", {}).get("list"):
                return []
            
            return [
                {
                    "id": trade["id"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["size"]),
                    "time": int(trade["time"]),
                    "side": trade["side"]
                }
                for trade in data["result"]["list"]
            ]
        except Exception as e:
            logger.error(f"Bybit trades error: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        try:
            url = "/v5/market/kline"
            params = {
                "category": "spot",
                "symbol": symbol.replace("/", ""),
                "interval": interval,
                "limit": str(min(limit, 200))
            }
            data = await self._make_request("GET", url, params)
            
            if data.get("retCode") != 0 or not data.get("result", {}).get("list"):
                return []
            
            return [
                {
                    "timestamp": int(k[0]),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "turnover": float(k[6])
                }
                for k in data["result"]["list"]
            ]
        except Exception as e:
            logger.error(f"Bybit klines error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/v5/market/instruments-info"
            params = {"category": "spot"}
            data = await self._make_request("GET", url, params)
            
            if data.get("retCode") != 0 or not data.get("result", {}).get("list"):
                return []
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["baseCoin"],
                    "quote_asset": pair["quoteCoin"],
                    "status": pair["status"],
                    "min_trade_qty": float(pair["lotSizeFilter"]["minOrderQty"]),
                    "max_trade_qty": float(pair["lotSizeFilter"]["maxOrderQty"]),
                    "qty_step": float(pair["lotSizeFilter"]["qtyStep"]),
                    "min_price_precision": pair["priceFilter"]["tickSize"]
                }
                for pair in data["result"]["list"]
                if pair["status"] == "Trading"
            ]
        except Exception as e:
            logger.error(f"Bybit trading pairs error: {e}")
            raise

class CoinbaseFetcher(BaseExchangeFetcher):
    """Coinbase exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("coinbase", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.pro.coinbase.com"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            coinbase_symbol = symbol.replace("/", "-")
            url = f"/products/{coinbase_symbol}/ticker"
            data = await self._make_request("GET", url)
            
            # Get 24h stats
            stats_url = f"/products/{coinbase_symbol}/stats"
            stats_data = await self._make_request("GET", stats_url)
            
            return {
                "symbol": data["product_id"],
                "price": float(data["price"]),
                "change_24h": 0,  # Coinbase doesn't provide this directly
                "change_percent_24h": 0,
                "volume_24h": float(stats_data["volume"]),
                "quote_volume_24h": float(data.get("volume_24h", 0)),
                "high_24h": float(stats_data["high"]),
                "low_24h": float(stats_data["low"]),
                "open_24h": float(stats_data["open"]),
                "bid_price": float(data.get("bid", 0)),
                "ask_price": float(data.get("ask", 0)),
                "bid_qty": 0,
                "ask_qty": 0,
                "time": data["time"]
            }
        except Exception as e:
            logger.error(f"Coinbase ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            coinbase_symbol = symbol.replace("/", "-")
            url = f"/products/{coinbase_symbol}/book"
            params = {"level": 2 if limit > 50 else 1}
            data = await self._make_request("GET", url, params=params)
            
            return {
                "symbol": coinbase_symbol,
                "bids": [[float(bid[0]), float(bid[1])] for bid in data["bids"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in data["asks"]],
                "sequence": data["sequence"]
            }
        except Exception as e:
            logger.error(f"Coinbase orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            coinbase_symbol = symbol.replace("/", "-")
            url = f"/products/{coinbase_symbol}/trades"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "id": trade["trade_id"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["size"]),
                    "time": trade["time"],
                    "side": trade["side"]
                }
                for trade in data[:min(limit, 100)]
            ]
        except Exception as e:
            logger.error(f"Coinbase trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/products"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "symbol": pair["id"],
                    "base_asset": pair["base_currency"],
                    "quote_asset": pair["quote_currency"],
                    "status": "online" if pair["status"] == "online" else "offline",
                    "min_market_funds": float(pair["min_market_funds"]),
                    "max_market_funds": float(pair["max_market_funds"]),
                    "min_size": float(pair["base_min_size"]),
                    "max_size": float(pair["base_max_size"]),
                    "increment": float(pair["quote_increment"]),
                    "base_increment": float(pair["base_increment"])
                }
                for pair in data
                if pair["status"] == "online"
            ]
        except Exception as e:
            logger.error(f"Coinbase trading pairs error: {e}")
            raise

class KuCoinFetcher(BaseExchangeFetcher):
    """KuCoin exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        super().__init__("kucoin", api_key, api_secret, passphrase)
    
    def get_base_url(self) -> str:
        return "https://api.kucoin.com"
    
    def _generate_signature(self, endpoint: str, params: str = "", method: str = "GET") -> str:
        """Generate signature for KuCoin API"""
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method + endpoint + params
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            kucoin_symbol = symbol.replace("/", "-")
            url = f"/api/v1/market/orderbook/level1"
            params = {"symbol": kucoin_symbol}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "200000":
                raise Exception(f"KuCoin API error: {data}")
            
            ticker = data["data"]
            
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["price"]),
                "change_24h": 0,
                "change_percent_24h": float(ticker.get("changeRate", 0)),
                "volume_24h": 0,
                "quote_volume_24h": 0,
                "high_24h": 0,
                "low_24h": 0,
                "open_24h": 0,
                "bid_price": float(ticker.get("bestBid", 0)),
                "ask_price": float(ticker.get("bestAsk", 0)),
                "bid_qty": 0,
                "ask_qty": 0,
                "time": ticker["time"]
            }
        except Exception as e:
            logger.error(f"KuCoin ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            kucoin_symbol = symbol.replace("/", "-")
            url = "/api/v1/market/orderbook/level2_100"
            params = {"symbol": kucoin_symbol}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "200000":
                raise Exception(f"KuCoin API error: {data}")
            
            book = data["data"]
            
            return {
                "symbol": book["symbol"],
                "bids": [[float(bid[0]), float(bid[1])] for bid in book["bids"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in book["asks"]],
                "time": book["time"]
            }
        except Exception as e:
            logger.error(f"KuCoin orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            kucoin_symbol = symbol.replace("/", "-")
            url = "/api/v1/market/histories"
            params = {"symbol": kucoin_symbol}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "200000":
                return []
            
            return [
                {
                    "id": trade["tradeId"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["size"]),
                    "time": trade["time"],
                    "side": trade["side"]
                }
                for trade in data["data"][:min(limit, 1000)]
            ]
        except Exception as e:
            logger.error(f"KuCoin trades error: {e}")
            raise
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get candlestick data"""
        try:
            kucoin_symbol = symbol.replace("/", "-")
            url = "/api/v1/market/candles"
            params = {
                "symbol": kucoin_symbol,
                "type": interval,
                "limit": str(min(limit, 500))
            }
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "200000":
                return []
            
            return [
                {
                    "timestamp": int(k[0]),
                    "open": float(k[1]),
                    "close": float(k[2]),
                    "high": float(k[3]),
                    "low": float(k[4]),
                    "volume": float(k[5]),
                    "turnover": float(k[6])
                }
                for k in data["data"]
            ]
        except Exception as e:
            logger.error(f"KuCoin klines error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/api/v1/symbols"
            data = await self._make_request("GET", url)
            
            if data.get("code") != "200000":
                return []
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["baseCurrency"],
                    "quote_asset": pair["quoteCurrency"],
                    "status": "trading" if pair["enableTrading"] else "disabled",
                    "min_size": float(pair["baseMinSize"]),
                    "max_size": float(pair["baseMaxSize"]),
                    "quote_increment": float(pair["quoteIncrement"]),
                    "base_increment": float(pair["baseIncrement"]),
                    "fee_currency": pair["feeCurrency"]
                }
                for pair in data["data"]
                if pair["enableTrading"]
            ]
        except Exception as e:
            logger.error(f"KuCoin trading pairs error: {e}")
            raise

class BitfinexFetcher(BaseExchangeFetcher):
    """Bitfinex exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("bitfinex", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api-pub.bitfinex.com"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            bitfinex_symbol = f"t{symbol.replace('/', '')}"
            url = f"/v2/ticker/{bitfinex_symbol}"
            data = await self._make_request("GET", url)
            
            if len(data) < 10:
                raise Exception("Invalid ticker data")
            
            return {
                "symbol": bitfinex_symbol,
                "price": float(data[6]),
                "change_24h": float(data[4]),
                "change_percent_24h": float(data[5]),
                "volume_24h": float(data[7]),
                "quote_volume_24h": float(data[8]),
                "high_24h": float(data[8]),
                "low_24h": float(data[9]),
                "open_24h": float(data[6]) - float(data[4]),
                "bid_price": float(data[0]) if data[0] else 0,
                "ask_price": float(data[2]) if data[2] else 0,
                "bid_qty": float(data[1]) if data[1] else 0,
                "ask_qty": float(data[3]) if data[3] else 0,
                "time": data[1] if len(data) > 1 else 0
            }
        except Exception as e:
            logger.error(f"Bitfinex ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            bitfinex_symbol = f"t{symbol.replace('/', '')}"
            url = f"/v2/book/{bitfinex_symbol}/P0"
            params = {"len": str(min(limit, 100))}
            data = await self._make_request("GET", url, params)
            
            return {
                "symbol": bitfinex_symbol,
                "bids": [[float(bid[0]), float(bid[2])] for bid in data[0] if len(bid) >= 3],
                "asks": [[float(ask[0]), float(ask[2])] for ask in data[1] if len(ask) >= 3]
            }
        except Exception as e:
            logger.error(f"Bitfinex orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            bitfinex_symbol = f"t{symbol.replace('/', '')}"
            url = f"/v2/trades/{bitfinex_symbol}/hist"
            params = {"limit": str(min(limit, 100))}
            data = await self._make_request("GET", url, params)
            
            return [
                {
                    "id": trade[0],
                    "time": trade[1],
                    "price": float(trade[3]),
                    "quantity": float(trade[2]),
                    "side": "buy" if trade[2] > 0 else "sell"
                }
                for trade in data
            ]
        except Exception as e:
            logger.error(f"Bitfinex trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/v1/symbols_details"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "symbol": f"t{pair['pair']}",
                    "base_asset": pair["base_currency"],
                    "quote_asset": pair["quote_currency"],
                    "status": "trading" if pair["pair"] else "disabled",
                    "min_order_size": float(pair["minimum_order_size"]),
                    "max_order_size": float(pair["maximum_order_size"]),
                    "price_precision": pair["price_precision"],
                    "initial_margin": pair["initial_margin"]
                }
                for pair in data
            ]
        except Exception as e:
            logger.error(f"Bitfinex trading pairs error: {e}")
            raise

class HuobiFetcher(BaseExchangeFetcher):
    """Huobi exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("huobi", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.huobi.pro"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            huobi_symbol = symbol.lower().replace("/", "")
            url = "/market/detail/merged"
            params = {"symbol": huobi_symbol}
            data = await self._make_request("GET", url, params)
            
            if "status" in data and data["status"] != "ok":
                raise Exception(f"Huobi API error: {data}")
            
            tick = data["tick"]
            
            return {
                "symbol": symbol,
                "price": float(tick["close"]),
                "change_24h": float(tick["close"]) - float(tick["open"]),
                "change_percent_24h": ((float(tick["close"]) - float(tick["open"])) / float(tick["open"])) * 100,
                "volume_24h": float(tick["vol"]),
                "quote_volume_24h": float(tick["amount"]),
                "high_24h": float(tick["high"]),
                "low_24h": float(tick["low"]),
                "open_24h": float(tick["open"]),
                "bid_price": float(tick["bid"][0]) if tick["bid"] else 0,
                "bid_qty": float(tick["bid"][1]) if tick["bid"] else 0,
                "ask_price": float(tick["ask"][0]) if tick["ask"] else 0,
                "ask_qty": float(tick["ask"][1]) if tick["ask"] else 0,
                "time": data["ts"]
            }
        except Exception as e:
            logger.error(f"Huobi ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            huobi_symbol = symbol.lower().replace("/", "")
            url = "/market/depth"
            params = {"symbol": huobi_symbol, "type": "step0"}
            data = await self._make_request("GET", url, params)
            
            if "status" in data and data["status"] != "ok":
                raise Exception(f"Huobi API error: {data}")
            
            tick = data["tick"]
            
            return {
                "symbol": symbol,
                "bids": [[float(bid[0]), float(bid[1])] for bid in tick["bids"][:limit]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in tick["asks"][:limit]],
                "time": data["ts"]
            }
        except Exception as e:
            logger.error(f"Huobi orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            huobi_symbol = symbol.lower().replace("/", "")
            url = "/market/trade"
            params = {"symbol": huobi_symbol}
            data = await self._make_request("GET", url, params)
            
            if "status" in data and data["status"] != "ok":
                return []
            
            return [
                {
                    "id": trade["id"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["amount"]),
                    "time": trade["ts"],
                    "side": "buy" if trade["direction"] == "buy" else "sell"
                }
                for trade in data["tick"]["data"][:limit]
            ]
        except Exception as e:
            logger.error(f"Huobi trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/v1/common/symbols"
            data = await self._make_request("GET", url)
            
            if "status" in data and data["status"] != "ok":
                return []
            
            return [
                {
                    "symbol": f"{pair['base-currency'].upper()}/{pair['quote-currency'].upper()}",
                    "base_asset": pair["base-currency"].upper(),
                    "quote_asset": pair["quote-currency"].upper(),
                    "status": "trading" if pair["state"] == "online" else "disabled",
                    "min_amount": float(pair["min-order-amount"]),
                    "max_amount": float(pair["max-order-amount"]),
                    "min_value": float(pair["min-order-value"]),
                    "price_precision": pair["price-precision"],
                    "amount_precision": pair["amount-precision"]
                }
                for pair in data["data"]
                if pair["state"] == "online"
            ]
        except Exception as e:
            logger.error(f"Huobi trading pairs error: {e}")
            raise

class GeminiFetcher(BaseExchangeFetcher):
    """Gemini exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("gemini", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.gemini.com"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            gemini_symbol = symbol.lower().replace("/", "")
            url = f"/v1/pubticker/{gemini_symbol}"
            data = await self._make_request("GET", url)
            
            return {
                "symbol": data["symbol"],
                "price": float(data["last"]),
                "change_24h": float(data["change"]) if data.get("change") else 0,
                "change_percent_24h": float(data["changePercent"]) if data.get("changePercent") else 0,
                "volume_24h": 0,  # Gemini doesn't provide volume in ticker
                "quote_volume_24h": 0,
                "high_24h": float(data["high"]) if data.get("high") else 0,
                "low_24h": float(data["low"]) if data.get("low") else 0,
                "open_24h": 0,
                "bid_price": float(data["bid"]) if data.get("bid") else 0,
                "ask_price": float(data["ask"]) if data.get("ask") else 0,
                "bid_qty": 0,
                "ask_qty": 0,
                "time": data["volume"]["timestamp"] if data.get("volume") else data["timestamp"]
            }
        except Exception as e:
            logger.error(f"Gemini ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            gemini_symbol = symbol.lower().replace("/", "")
            url = f"/v1/book/{gemini_symbol}"
            params = {"limit_bids": limit, "limit_asks": limit}
            data = await self._make_request("GET", url, params)
            
            return {
                "symbol": data["symbol"],
                "bids": [[float(bid["price"]), float(bid["amount"])] for bid in data["bids"]],
                "asks": [[float(ask["price"]), float(ask["amount"])] for ask in data["asks"]]
            }
        except Exception as e:
            logger.error(f"Gemini orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            gemini_symbol = symbol.lower().replace("/", "")
            url = f"/v1/trades/{gemini_symbol}"
            params = {"limit_trades": limit}
            data = await self._make_request("GET", url, params)
            
            return [
                {
                    "id": trade["tid"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["amount"]),
                    "time": trade["timestampms"],
                    "side": trade["type"],
                    "exchange": trade["exchange"]
                }
                for trade in data
            ]
        except Exception as e:
            logger.error(f"Gemini trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/v1/symbols"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["base_currency"],
                    "quote_asset": pair["quote_currency"],
                    "status": "trading",
                    "min_order_size": float(pair["min_order_size"]),
                    "max_order_size": float(pair["max_order_size"]),
                    "quote_increment": float(pair["quote_increment"]),
                    "base_increment": float(pair["base_increment"])
                }
                for pair in data
            ]
        except Exception as e:
            logger.error(f"Gemini trading pairs error: {e}")
            raise

class MEXCFetcher(BaseExchangeFetcher):
    """MEXC exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__("mexc", api_key, api_secret)
    
    def get_base_url(self) -> str:
        return "https://api.mexc.com"
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            mexc_symbol = symbol.replace("/", "")
            url = "/api/v3/ticker/24hr"
            params = {"symbol": mexc_symbol}
            data = await self._make_request("GET", url, params)
            
            if not data or len(data) == 0:
                raise Exception("No ticker data available")
            
            ticker = data[0]
            
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["lastPrice"]),
                "change_24h": float(ticker["priceChange"]),
                "change_percent_24h": float(ticker["priceChangePercent"]),
                "volume_24h": float(ticker["volume"]),
                "quote_volume_24h": float(ticker["quoteVolume"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"]),
                "open_24h": float(ticker["openPrice"]),
                "bid_price": float(ticker["bidPrice"]) if ticker.get("bidPrice") else 0,
                "ask_price": float(ticker["askPrice"]) if ticker.get("askPrice") else 0,
                "bid_qty": 0,
                "ask_qty": 0,
                "count": int(ticker["count"])
            }
        except Exception as e:
            logger.error(f"MEXC ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            mexc_symbol = symbol.replace("/", "")
            url = "/api/v3/depth"
            params = {"symbol": mexc_symbol, "limit": str(min(limit, 5000))}
            data = await self._make_request("GET", url, params)
            
            return {
                "symbol": mexc_symbol,
                "bids": [[float(bid[0]), float(bid[1])] for bid in data["bids"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in data["asks"]],
                "last_update_id": data.get("lastUpdateId", 0)
            }
        except Exception as e:
            logger.error(f"MEXC orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            mexc_symbol = symbol.replace("/", "")
            url = "/api/v3/trades"
            params = {"symbol": mexc_symbol, "limit": str(min(limit, 1000))}
            data = await self._make_request("GET", url, params)
            
            return [
                {
                    "id": trade["id"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["qty"]),
                    "time": trade["time"],
                    "is_buyer_maker": trade["isBuyerMaker"],
                    "is_best_match": trade["isBestMatch"]
                }
                for trade in data
            ]
        except Exception as e:
            logger.error(f"MEXC trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/api/v3/exchangeInfo"
            data = await self._make_request("GET", url)
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["baseAsset"],
                    "quote_asset": pair["quoteAsset"],
                    "status": pair["status"],
                    "base_asset_precision": pair["baseAssetPrecision"],
                    "quote_precision": pair["quotePrecision"],
                    "min_qty": float(pair["filters"][0]["minQty"]),
                    "max_qty": float(pair["filters"][1]["maxQty"]),
                    "step_size": float(pair["filters"][2]["stepSize"])
                }
                for pair in data["symbols"]
                if pair["status"] == "TRADING"
            ]
        except Exception as e:
            logger.error(f"MEXC trading pairs error: {e}")
            raise

class BitGetFetcher(BaseExchangeFetcher):
    """BitGet exchange fetcher with complete functionality"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        super().__init__("bitget", api_key, api_secret, passphrase)
    
    def get_base_url(self) -> str:
        return "https://api.bitget.com"
    
    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = "") -> str:
        """Generate signature for BitGet API"""
        message = timestamp + method + endpoint + body
        return base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker with enhanced data"""
        try:
            bitget_symbol = symbol.replace("/", "")
            url = f"/api/v2/spot/market/tickers"
            params = {"symbol": bitget_symbol}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "00000" or not data.get("data"):
                raise Exception(f"BitGet API error: {data}")
            
            ticker = data["data"][0]
            
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["lastPr"]),
                "change_24h": float(ticker["changeUtc24h"]) if ticker.get("changeUtc24h") else 0,
                "change_percent_24h": float(ticker["changeUtc24hPercent"]) if ticker.get("changeUtc24hPercent") else 0,
                "volume_24h": float(ticker["baseVol24h"]) if ticker.get("baseVol24h") else 0,
                "quote_volume_24h": float(ticker["quoteVol24h"]) if ticker.get("quoteVol24h") else 0,
                "high_24h": float(ticker["high24h"]) if ticker.get("high24h") else 0,
                "low_24h": float(ticker["low24h"]) if ticker.get("low24h") else 0,
                "open_24h": 0,
                "bid_price": float(ticker["bidPr"]) if ticker.get("bidPr") else 0,
                "bid_qty": float(ticker["bidSz"]) if ticker.get("bidSz") else 0,
                "ask_price": float(ticker["askPr"]) if ticker.get("askPr") else 0,
                "ask_qty": float(ticker["askSz"]) if ticker.get("askSz") else 0
            }
        except Exception as e:
            logger.error(f"BitGet ticker error: {e}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get enhanced order book"""
        try:
            bitget_symbol = symbol.replace("/", "")
            url = f"/api/v2/spot/market/orderbook"
            params = {"symbol": bitget_symbol, "depth": str(min(limit, 200))}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "00000" or not data.get("data"):
                raise Exception(f"BitGet API error: {data}")
            
            book = data["data"]
            
            return {
                "symbol": bitget_symbol,
                "bids": [[float(bid[0]), float(bid[1])] for bid in book["bids"]],
                "asks": [[float(ask[0]), float(ask[1])] for ask in book["asks"]],
                "timestamp": book["timestamp"]
            }
        except Exception as e:
            logger.error(f"BitGet orderbook error: {e}")
            raise
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades with enhanced data"""
        try:
            bitget_symbol = symbol.replace("/", "")
            url = f"/api/v2/spot/market/fills"
            params = {"symbol": bitget_symbol, "limit": str(min(limit, 100))}
            data = await self._make_request("GET", url, params)
            
            if data.get("code") != "00000" or not data.get("data"):
                return []
            
            return [
                {
                    "id": trade["tradeId"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["size"]),
                    "time": trade["timestamp"],
                    "side": trade["side"]
                }
                for trade in data["data"]
            ]
        except Exception as e:
            logger.error(f"BitGet trades error: {e}")
            raise
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading pairs with detailed info"""
        try:
            url = "/api/v2/spot/market/symbols"
            data = await self._make_request("GET", url)
            
            if data.get("code") != "00000" or not data.get("data"):
                return []
            
            return [
                {
                    "symbol": pair["symbol"],
                    "base_asset": pair["baseCoin"],
                    "quote_asset": pair["quoteCoin"],
                    "status": "trading" if pair["status"] == "normal" else "disabled",
                    "min_size": float(pair["minTradeAmount"]),
                    "max_size": float(pair["maxTradeAmount"]),
                    "size_precision": pair["sizePrecision"],
                    "price_precision": pair["pricePrecision"]
                }
                for pair in data["data"]
                if pair["status"] == "normal"
            ]
        except Exception as e:
            logger.error(f"BitGet trading pairs error: {e}")
            raise

# Exchange Factory
class ExchangeFetcherFactory:
    """Factory for creating exchange fetchers"""
    
    _fetchers = {
        "binance": BinanceFetcher,
        "okx": OKXFetcher,
        "bybit": BybitFetcher,
        "coinbase": CoinbaseFetcher,
        "kucoin": KuCoinFetcher,
        "bitfinex": BitfinexFetcher,
        "huobi": HuobiFetcher,
        "gemini": GeminiFetcher,
        "mexc": MEXCFetcher,
        "bitget": BitGetFetcher
    }
    
    @classmethod
    def create_fetcher(cls, exchange: str, api_key: str = None, api_secret: str = None, passphrase: str = None) -> BaseExchangeFetcher:
        """Create exchange fetcher"""
        if exchange.lower() not in cls._fetchers:
            raise ValueError(f"Exchange {exchange} not supported")
        
        fetcher_class = cls._fetchers[exchange.lower()]
        
        if exchange.lower() in ["okx", "kucoin", "bitget"]:
            return fetcher_class(api_key, api_secret, passphrase)
        else:
            return fetcher_class(api_key, api_secret)
    
    @classmethod
    def get_supported_exchanges(cls) -> List[str]:
        """Get list of supported exchanges"""
        return list(cls._fetchers.keys())

# Unified Exchange Manager
class UnifiedExchangeManager:
    """Manager for all exchange fetchers with unified interface"""
    
    def __init__(self):
        self.fetchers = {}
        self.supported_exchanges = ExchangeFetcherFactory.get_supported_exchanges()
    
    def add_exchange(self, exchange: str, api_key: str = None, api_secret: str = None, passphrase: str = None):
        """Add exchange fetcher"""
        fetcher = ExchangeFetcherFactory.create_fetcher(exchange, api_key, api_secret, passphrase)
        self.fetchers[exchange] = fetcher
        return fetcher
    
    def get_exchange(self, exchange: str) -> BaseExchangeFetcher:
        """Get exchange fetcher"""
        if exchange not in self.fetchers:
            raise ValueError(f"Exchange {exchange} not added")
        return self.fetchers[exchange]
    
    async def get_all_tickers(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data from all exchanges"""
        results = {}
        tasks = []
        
        for exchange_name, fetcher in self.fetchers.items():
            task = self._safe_get_ticker(exchange_name, fetcher, symbol)
            tasks.append(task)
        
        ticker_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(ticker_results):
            exchange_name = list(self.fetchers.keys())[i]
            if isinstance(result, Exception):
                results[exchange_name] = {"error": str(result)}
            else:
                results[exchange_name] = result
        
        return results
    
    async def _safe_get_ticker(self, exchange_name: str, fetcher: BaseExchangeFetcher, symbol: str) -> Dict[str, Any]:
        """Safely get ticker with error handling"""
        try:
            return await fetcher.get_ticker(symbol)
        except Exception as e:
            logger.error(f"Error getting ticker from {exchange_name}: {e}")
            raise
    
    async def get_best_price(self, symbol: str) -> Dict[str, Any]:
        """Get best price across all exchanges"""
        tickers = await self.get_all_tickers(symbol)
        
        best_bid = None
        best_ask = None
        bid_exchange = None
        ask_exchange = None
        
        for exchange, ticker in tickers.items():
            if "error" in ticker:
                continue
            
            if ticker.get("bid_price", 0) > (best_bid or 0):
                best_bid = ticker["bid_price"]
                bid_exchange = exchange
            
            if ticker.get("ask_price", float('inf')) < (best_ask or float('inf')):
                best_ask = ticker["ask_price"]
                ask_exchange = exchange
        
        return {
            "symbol": symbol,
            "best_bid": best_bid,
            "best_bid_exchange": bid_exchange,
            "best_ask": best_ask,
            "best_ask_exchange": ask_exchange,
            "spread": (best_ask - best_bid) if best_bid and best_ask else None,
            "all_tickers": tickers
        }
    
    async def close_all(self):
        """Close all exchange sessions"""
        for fetcher in self.fetchers.values():
            await fetcher._close_session()

# Usage Example
async def main():
    """Example usage of unified exchange system"""
    manager = UnifiedExchangeManager()
    
    # Add all exchanges
    for exchange in manager.supported_exchanges:
        manager.add_exchange(exchange)
    
    # Get ticker from all exchanges
    tickers = await manager.get_all_tickers("BTC/USDT")
    print("All tickers:", json.dumps(tickers, indent=2))
    
    # Get best price
    best_price = await manager.get_best_price("BTC/USDT")
    print("Best price:", json.dumps(best_price, indent=2))
    
    # Close all sessions
    await manager.close_all()

if __name__ == "__main__":
    asyncio.run(main())