"""
TigerEx COMPLETE Liquidity Enhancement System
Integrates ALL major exchanges with comprehensive liquidity aggregation
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import aiohttp
import json
import hmac
import hashlib
import time
import logging

app = FastAPI(
    title="TigerEx COMPLETE Liquidity Enhancement",
    version="2.0.0",
    description="Complete liquidity integration with all major exchanges"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== EXCHANGE INTEGRATIONS ====================

class ExchangeType(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    HUOBI = "huobi"
    KRAKEN = "kraken"
    GEMINI = "gemini"
    COINBASE = "coinbase"
    ORBIT = "orbit"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    BITGET = "bitget"

class LiquidityPool(BaseModel):
    exchange: ExchangeType
    base_asset: str
    quote_asset: str
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    timestamp: datetime

class ExchangeConnector:
    """Base class for exchange connectors"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None
    
    async def connect(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def disconnect(self):
        if self.session:
            await self.session.close()
    
    async def get_orderbook(self, symbol: str) -> Dict:
        raise NotImplementedError

class BinanceConnector(ExchangeConnector):
    """Binance integration"""
    
    BASE_URL = "https://api.binance.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/api/v3/depth"
        params = {"symbol": symbol, "limit": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "bids": data.get("bids", []),
                    "asks": data.get("asks", []),
                    "timestamp": time.time()
                }
        except Exception as e:
            logger.error(f"Binance orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class OKXConnector(ExchangeConnector):
    """OKX integration"""
    
    BASE_URL = "https://www.okx.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/api/v5/market/books"
        params = {"instId": symbol, "sz": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("code") == "0":
                    book = data["data"][0] if data["data"] else {}
                    return {
                        "bids": book.get("bids", []),
                        "asks": book.get("asks", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"OKX orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class HuobiConnector(ExchangeConnector):
    """Huobi integration"""
    
    BASE_URL = "https://api.huobi.pro"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/market/depth"
        params = {"symbol": symbol.lower(), "type": "step0", "depth": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("status") == "ok":
                    tick = data.get("tick", {})
                    return {
                        "bids": tick.get("bids", []),
                        "asks": tick.get("asks", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"Huobi orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class KrakenConnector(ExchangeConnector):
    """Kraken integration"""
    
    BASE_URL = "https://api.kraken.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/0/public/Depth"
        params = {"pair": symbol, "count": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("error") == []:
                    result = data.get("result", {})
                    # Kraken returns pairs as keys
                    pair_data = list(result.values())[0] if result else {}
                    return {
                        "bids": pair_data.get("bids", []),
                        "asks": pair_data.get("asks", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"Kraken orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class GeminiConnector(ExchangeConnector):
    """Gemini integration"""
    
    BASE_URL = "https://api.gemini.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/v1/book/{symbol}"
        params = {"limit_bids": 100, "limit_asks": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "bids": [[str(bid["price"]), str(bid["amount"])] for bid in data.get("bids", [])],
                    "asks": [[str(ask["price"]), str(ask["amount"])] for ask in data.get("asks", [])],
                    "timestamp": time.time()
                }
        except Exception as e:
            logger.error(f"Gemini orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class CoinbaseConnector(ExchangeConnector):
    """Coinbase integration"""
    
    BASE_URL = "https://api.pro.coinbase.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/products/{symbol}/book"
        params = {"level": 2}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "bids": data.get("bids", []),
                    "asks": data.get("asks", []),
                    "timestamp": time.time()
                }
        except Exception as e:
            logger.error(f"Coinbase orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class OrbitConnector(ExchangeConnector):
    """Orbit integration (custom implementation)"""
    
    BASE_URL = "https://api.orbit.exchange"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/v1/depth"
        params = {"symbol": symbol, "limit": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "bids": data.get("bids", []),
                    "asks": data.get("asks", []),
                    "timestamp": time.time()
                }
        except Exception as e:
            logger.error(f"Orbit orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class BybitConnector(ExchangeConnector):
    """Bybit integration"""
    
    BASE_URL = "https://api.bybit.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/v5/market/orderbook"
        params = {"category": "spot", "symbol": symbol, "limit": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("retCode") == 0:
                    result = data.get("result", {})
                    return {
                        "bids": result.get("b", []),
                        "asks": result.get("a", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"Bybit orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class KuCoinConnector(ExchangeConnector):
    """KuCoin integration"""
    
    BASE_URL = "https://api.kucoin.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/api/v1/market/orderbook/level2_100"
        params = {"symbol": symbol}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("code") == "200000":
                    book_data = data.get("data", {})
                    return {
                        "bids": book_data.get("bids", []),
                        "asks": book_data.get("asks", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"KuCoin orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

class BitgetConnector(ExchangeConnector):
    """Bitget integration"""
    
    BASE_URL = "https://api.bitget.com"
    
    async def get_orderbook(self, symbol: str) -> Dict:
        await self.connect()
        url = f"{self.BASE_URL}/api/v2/spot/market/orderbook"
        params = {"symbol": symbol, "limit": 100}
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                if data.get("code") == "00000":
                    book_data = data.get("data", {})
                    return {
                        "bids": book_data.get("bids", []),
                        "asks": book_data.get("asks", []),
                        "timestamp": time.time()
                    }
        except Exception as e:
            logger.error(f"Bitget orderbook error: {e}")
            return {"bids": [], "asks": [], "timestamp": time.time()}

# ==================== LIQUIDITY AGGREGATOR ====================

class LiquidityAggregator:
    """Main liquidity aggregation system"""
    
    def __init__(self):
        self.connectors = {
            ExchangeType.BINANCE: BinanceConnector(),
            ExchangeType.OKX: OKXConnector(),
            ExchangeType.HUOBI: HuobiConnector(),
            ExchangeType.KRAKEN: KrakenConnector(),
            ExchangeType.GEMINI: GeminiConnector(),
            ExchangeType.COINBASE: CoinbaseConnector(),
            ExchangeType.ORBIT: OrbitConnector(),
            ExchangeType.BYBIT: BybitConnector(),
            ExchangeType.KUCOIN: KuCoinConnector(),
            ExchangeType.BITGET: BitgetConnector()
        }
        self.liquidity_pools = {}
    
    async def aggregate_liquidity(self, symbol: str, exchanges: List[ExchangeType] = None) -> Dict:
        """Aggregate liquidity from multiple exchanges"""
        if exchanges is None:
            exchanges = list(ExchangeType)
        
        aggregated_bids = []
        aggregated_asks = []
        total_liquidity = 0.0
        
        tasks = []
        for exchange in exchanges:
            if exchange in self.connectors:
                connector = self.connectors[exchange]
                task = self._get_exchange_liquidity(connector, exchange, symbol)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                exchange_name = result.get("exchange")
                bids = result.get("bids", [])
                asks = result.get("asks", [])
                
                # Process bids
                for bid in bids:
                    if len(bid) >= 2:
                        price = float(bid[0])
                        size = float(bid[1])
                        aggregated_bids.append({
                            "price": price,
                            "size": size,
                            "exchange": exchange_name
                        })
                        total_liquidity += price * size
                
                # Process asks
                for ask in asks:
                    if len(ask) >= 2:
                        price = float(ask[0])
                        size = float(ask[1])
                        aggregated_asks.append({
                            "price": price,
                            "size": size,
                            "exchange": exchange_name
                        })
                        total_liquidity += price * size
        
        # Sort bids (descending) and asks (ascending)
        aggregated_bids.sort(key=lambda x: x["price"], reverse=True)
        aggregated_asks.sort(key=lambda x: x["price"])
        
        return {
            "symbol": symbol,
            "bids": aggregated_bids[:100],  # Top 100 bids
            "asks": aggregated_asks[:100],  # Top 100 asks
            "total_liquidity": total_liquidity,
            "exchange_count": len(exchanges),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_exchange_liquidity(self, connector: ExchangeConnector, exchange: ExchangeType, symbol: str) -> Dict:
        """Get liquidity from a single exchange"""
        try:
            orderbook = await connector.get_orderbook(symbol)
            return {
                "exchange": exchange.value,
                "bids": orderbook.get("bids", []),
                "asks": orderbook.get("asks", []),
                "timestamp": orderbook.get("timestamp", time.time())
            }
        except Exception as e:
            logger.error(f"Error getting liquidity from {exchange.value}: {e}")
            return {"exchange": exchange.value, "bids": [], "asks": [], "timestamp": time.time()}

# Global aggregator instance
liquidity_aggregator = LiquidityAggregator()

# ==================== API ENDPOINTS ====================

@app.get("/api/v1/liquidity/aggregated/{symbol}")
async def get_aggregated_liquidity(symbol: str, exchanges: str = None):
    """Get aggregated liquidity from all exchanges"""
    exchange_list = None
    if exchanges:
        exchange_list = [ExchangeType(ex.strip()) for ex in exchanges.split(",")]
    
    result = await liquidity_aggregator.aggregate_liquidity(symbol, exchange_list)
    return result

@app.get("/api/v1/liquidity/exchanges")
async def get_supported_exchanges():
    """Get list of supported exchanges"""
    return {
        "exchanges": [exchange.value for exchange in ExchangeType],
        "total_count": len(ExchangeType)
    }

@app.get("/api/v1/liquidity/status")
async def get_liquidity_status():
    """Get liquidity system status"""
    return {
        "status": "operational",
        "connected_exchanges": len(liquidity_aggregator.connectors),
        "total_pools": len(liquidity_aggregator.liquidity_pools),
        "timestamp": datetime.now().isoformat()
    }

class LiquidityRequest(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    exchanges: List[ExchangeType] = []
    min_liquidity: Optional[float] = None

@app.post("/api/v1/liquidity/custom")
async def get_custom_liquidity(request: LiquidityRequest):
    """Get custom liquidity based on request parameters"""
    exchanges = request.exchanges if request.exchanges else list(ExchangeType)
    
    result = await liquidity_aggregator.aggregate_liquidity(request.symbol, exchanges)
    
    # Filter by minimum liquidity if specified
    if request.min_liquidity:
        filtered_bids = [bid for bid in result["bids"] if bid["price"] * bid["size"] >= request.min_liquidity]
        filtered_asks = [ask for ask in result["asks"] if ask["price"] * ask["size"] >= request.min_liquidity]
        result["bids"] = filtered_bids
        result["asks"] = filtered_asks
    
    return result

@app.get("/api/v1/liquidity/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "liquidity-enhancement",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3030)