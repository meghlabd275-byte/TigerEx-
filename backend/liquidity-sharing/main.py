"""
TigerEx Liquidity Sharing System
Complete implementation for sharing liquidity from major exchanges
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import hmac
import urllib.parse
from dataclasses import dataclass
from enum import Enum

class ExchangeType(Enum):
    BINANCE = "binance"
    OKX = "okx"
    HUOBI = "huobi"
    KRAKEN = "kraken"
    GEMINI = "gemini"
    COINBASE = "coinbase"

@dataclass
class LiquiditySource:
    exchange: ExchangeType
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    sandbox: bool = False
    enabled: bool = True

@dataclass
class OrderBook:
    exchange: str
    symbol: str
    bids: List[tuple]
    asks: List[tuple]
    timestamp: datetime

@dataclass
class Ticker:
    exchange: str
    symbol: str
    price: float
    volume: float
    change: float
    timestamp: datetime

class LiquidityAggregator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.liquidity_sources: Dict[ExchangeType, LiquiditySource] = {}
        self.order_books: Dict[str, OrderBook] = {}
        self.tickers: Dict[str, Ticker] = {}
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def add_liquidity_source(self, source: LiquiditySource):
        """Add a liquidity source"""
        self.liquidity_sources[source.exchange] = source
        self.logger.info(f"Added liquidity source: {source.exchange.value}")

    async def get_binance_orderbook(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """Get orderbook from Binance"""
        source = self.liquidity_sources.get(ExchangeType.BINANCE)
        if not source or not source.enabled:
            return None

        base_url = "https://api.binance.com" if not source.sandbox else "https://testnet.binance.vision"
        endpoint = "/api/v3/depth"
        
        params = {
            "symbol": symbol.upper(),
            "limit": limit
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return OrderBook(
                        exchange="binance",
                        symbol=symbol,
                        bids=[(float(bid[0]), float(bid[1])) for bid in data["bids"]],
                        asks=[(float(ask[0]), float(ask[1])) for ask in data["asks"]],
                        timestamp=datetime.now()
                    )
        except Exception as e:
            self.logger.error(f"Error fetching Binance orderbook: {e}")
        return None

    async def get_okx_orderbook(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """Get orderbook from OKX"""
        source = self.liquidity_sources.get(ExchangeType.OKX)
        if not source or not source.enabled:
            return None

        base_url = "https://www.okx.com" if not source.sandbox else "https://www.okx.com/api/v5"
        endpoint = "/api/v5/market/books"
        
        params = {
            "instId": symbol.replace("-", "-"),
            "sz": str(limit)
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "0" and data.get("data"):
                        book_data = data["data"][0]
                        bids = [(float(bid[0]), float(bid[1])) for bid in book_data["bids"]]
                        asks = [(float(ask[0]), float(ask[1])) for ask in book_data["asks"]]
                        
                        return OrderBook(
                            exchange="okx",
                            symbol=symbol,
                            bids=bids,
                            asks=asks,
                            timestamp=datetime.now()
                        )
        except Exception as e:
            self.logger.error(f"Error fetching OKX orderbook: {e}")
        return None

    async def get_huobi_orderbook(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """Get orderbook from Huobi"""
        source = self.liquidity_sources.get(ExchangeType.HUOBI)
        if not source or not source.enabled:
            return None

        base_url = "https://api.huobi.pro" if not source.sandbox else "https://api.huobi.pro"
        endpoint = "/market/depth"
        
        params = {
            "symbol": symbol.lower().replace("-", ""),
            "depth": str(limit),
            "type": "step0"
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "tick" in data:
                        return OrderBook(
                            exchange="huobi",
                            symbol=symbol,
                            bids=[(float(bid[0]), float(bid[1])) for bid in data["tick"]["bids"]],
                            asks=[(float(ask[0]), float(ask[1])) for ask in data["tick"]["asks"]],
                            timestamp=datetime.fromtimestamp(data["tick"]["ts"] / 1000)
                        )
        except Exception as e:
            self.logger.error(f"Error fetching Huobi orderbook: {e}")
        return None

    async def get_kraken_orderbook(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """Get orderbook from Kraken"""
        source = self.liquidity_sources.get(ExchangeType.KRAKEN)
        if not source or not source.enabled:
            return None

        base_url = "https://api.kraken.com"
        endpoint = "/0/public/Depth"
        
        params = {
            "pair": symbol,
            "count": str(limit)
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("error") == [] and "result" in data:
                        result = data["result"]
                        # Get the first pair key as Kraken returns with actual pair name
                        pair_key = list(result.keys())[0]
                        if pair_key != "last":
                            book_data = result[pair_key]
                            return OrderBook(
                                exchange="kraken",
                                symbol=symbol,
                                bids=[(float(bid[0]), float(bid[1])) for bid in book_data["bids"]],
                                asks=[(float(ask[0]), float(ask[1])) for ask in book_data["asks"]],
                                timestamp=datetime.now()
                            )
        except Exception as e:
            self.logger.error(f"Error fetching Kraken orderbook: {e}")
        return None

    async def get_gemini_orderbook(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """Get orderbook from Gemini"""
        source = self.liquidity_sources.get(ExchangeType.GEMINI)
        if not source or not source.enabled:
            return None

        base_url = "https://api.gemini.com" if not source.sandbox else "https://api.sandbox.gemini.com"
        endpoint = f"/v1/book/{symbol.upper()}"
        
        params = {
            "limit_bids": limit,
            "limit_asks": limit
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return OrderBook(
                        exchange="gemini",
                        symbol=symbol,
                        bids=[(float(bid["price"]), float(bid["amount"])) for bid in data["bids"]],
                        asks=[(float(ask["price"]), float(ask["amount"])) for ask in data["asks"]],
                        timestamp=datetime.now()
                    )
        except Exception as e:
            self.logger.error(f"Error fetching Gemini orderbook: {e}")
        return None

    async def get_coinbase_orderbook(self, symbol: str, limit: int = 2) -> Optional[OrderBook]:
        """Get orderbook from Coinbase"""
        source = self.liquidity_sources.get(ExchangeType.COINBASE)
        if not source or not source.enabled:
            return None

        base_url = "https://api.exchange.coinbase.com" if not source.sandbox else "https://api-public.sandbox.exchange.coinbase.com"
        endpoint = f"/products/{symbol.upper()}/book"
        
        params = {
            "level": str(limit)
        }
        
        try:
            async with self.session.get(f"{base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return OrderBook(
                        exchange="coinbase",
                        symbol=symbol,
                        bids=[(float(bid[0]), float(bid[1])) for bid in data["bids"]],
                        asks=[(float(ask[0]), float(ask[1])) for ask in data["asks"]],
                        timestamp=datetime.now()
                    )
        except Exception as e:
            self.logger.error(f"Error fetching Coinbase orderbook: {e}")
        return None

    async def get_aggregated_orderbook(self, symbol: str) -> Dict[str, Any]:
        """Get aggregated orderbook from all enabled exchanges"""
        tasks = []
        
        # Add all exchange orderbook tasks
        tasks.append(self.get_binance_orderbook(symbol))
        tasks.append(self.get_okx_orderbook(symbol))
        tasks.append(self.get_huobi_orderbook(symbol))
        tasks.append(self.get_kraken_orderbook(symbol))
        tasks.append(self.get_gemini_orderbook(symbol))
        tasks.append(self.get_coinbase_orderbook(symbol))
        
        # Execute all tasks concurrently
        orderbooks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid orderbooks
        valid_orderbooks = [ob for ob in orderbooks if isinstance(ob, OrderBook)]
        
        # Aggregate orderbooks
        aggregated_bids = {}
        aggregated_asks = {}
        total_volume = 0
        
        for ob in valid_orderbooks:
            # Aggregate bids
            for price, amount in ob.bids:
                if price in aggregated_bids:
                    aggregated_bids[price] += amount
                else:
                    aggregated_bids[price] = amount
                    
            # Aggregate asks
            for price, amount in ob.asks:
                if price in aggregated_asks:
                    aggregated_asks[price] += amount
                else:
                    aggregated_asks[price] = amount
            
            # Calculate total volume
            total_volume += sum(amount for _, amount in ob.bids[:10]) + sum(amount for _, amount in ob.asks[:10])
        
        # Sort and convert to lists
        sorted_bids = sorted(aggregated_bids.items(), key=lambda x: x[0], reverse=True)[:100]
        sorted_asks = sorted(aggregated_asks.items(), key=lambda x: x[0])[:100]
        
        return {
            "symbol": symbol,
            "bids": sorted_bids,
            "asks": sorted_asks,
            "total_volume": total_volume,
            "sources": [ob.exchange for ob in valid_orderbooks],
            "timestamp": datetime.now().isoformat()
        }

    async def get_best_prices(self, symbol: str) -> Dict[str, Any]:
        """Get best bid/ask prices across all exchanges"""
        aggregated = await self.get_aggregated_orderbook(symbol)
        
        if not aggregated["bids"] or not aggregated["asks"]:
            return {}
        
        best_bid = aggregated["bids"][0]  # Highest bid
        best_ask = aggregated["asks"][0]  # Lowest ask
        
        return {
            "symbol": symbol,
            "best_bid": {"price": best_bid[0], "amount": best_bid[1]},
            "best_ask": {"price": best_ask[0], "amount": best_ask[1]},
            "spread": best_ask[0] - best_bid[0],
            "spread_percentage": ((best_ask[0] - best_bid[0]) / best_bid[0]) * 100,
            "timestamp": aggregated["timestamp"]
        }

    async def route_order(self, symbol: str, side: str, amount: float, order_type: str = "market") -> Dict[str, Any]:
        """Route order to best available liquidity"""
        if order_type.lower() == "market":
            # For market orders, find the best execution across exchanges
            aggregated = await self.get_aggregated_orderbook(symbol)
            
            if side.lower() == "buy":
                # Execute against asks (buy orders)
                remaining_amount = amount
                executions = []
                total_cost = 0
                
                for price, available_amount in aggregated["asks"]:
                    if remaining_amount <= 0:
                        break
                    
                    execute_amount = min(remaining_amount, available_amount)
                    total_cost += price * execute_amount
                    executions.append({
                        "price": price,
                        "amount": execute_amount,
                        "exchange": "aggregated"
                    })
                    remaining_amount -= execute_amount
                
                avg_price = total_cost / amount if amount > 0 else 0
                
                return {
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "order_type": order_type,
                    "executions": executions,
                    "average_price": avg_price,
                    "total_cost": total_cost,
                    "status": "filled" if remaining_amount <= 0 else "partial"
                }
            
            elif side.lower() == "sell":
                # Execute against bids (sell orders)
                remaining_amount = amount
                executions = []
                total_revenue = 0
                
                for price, available_amount in aggregated["bids"]:
                    if remaining_amount <= 0:
                        break
                    
                    execute_amount = min(remaining_amount, available_amount)
                    total_revenue += price * execute_amount
                    executions.append({
                        "price": price,
                        "amount": execute_amount,
                        "exchange": "aggregated"
                    })
                    remaining_amount -= execute_amount
                
                avg_price = total_revenue / amount if amount > 0 else 0
                
                return {
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "order_type": order_type,
                    "executions": executions,
                    "average_price": avg_price,
                    "total_revenue": total_revenue,
                    "status": "filled" if remaining_amount <= 0 else "partial"
                }
        
        return {"error": "Unsupported order type"}

    async def get_liquidity_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get liquidity metrics for a symbol"""
        aggregated = await self.get_aggregated_orderbook(symbol)
        
        if not aggregated["bids"] or not aggregated["asks"]:
            return {}
        
        # Calculate various liquidity metrics
        total_bid_volume = sum(amount for _, amount in aggregated["bids"])
        total_ask_volume = sum(amount for _, amount in aggregated["asks"])
        
        # Depth at different levels
        depth_1_percent = self._calculate_depth(aggregated, 0.01)
        depth_5_percent = self._calculate_depth(aggregated, 0.05)
        
        # Spread metrics
        best_bid = aggregated["bids"][0][0]
        best_ask = aggregated["asks"][0][0]
        spread = best_ask - best_bid
        spread_percentage = (spread / best_bid) * 100
        
        return {
            "symbol": symbol,
            "total_bid_volume": total_bid_volume,
            "total_ask_volume": total_ask_volume,
            "total_volume": total_bid_volume + total_ask_volume,
            "depth_1_percent": depth_1_percent,
            "depth_5_percent": depth_5_percent,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "spread_percentage": spread_percentage,
            "sources_count": len(aggregated["sources"]),
            "timestamp": aggregated["timestamp"]
        }

    def _calculate_depth(self, aggregated: Dict, percentage: float) -> Dict[str, float]:
        """Calculate depth within a certain percentage of mid price"""
        if not aggregated["bids"] or not aggregated["asks"]:
            return {"bid_depth": 0, "ask_depth": 0}
        
        mid_price = (aggregated["bids"][0][0] + aggregated["asks"][0][0]) / 2
        bid_range = mid_price * (1 - percentage)
        ask_range = mid_price * (1 + percentage)
        
        bid_depth = sum(amount for price, amount in aggregated["bids"] if price >= bid_range)
        ask_depth = sum(amount for price, amount in aggregated["asks"] if price <= ask_range)
        
        return {"bid_depth": bid_depth, "ask_depth": ask_depth}

# Initialize and configure the liquidity sharing system
async def initialize_liquidity_system():
    """Initialize the liquidity sharing system with default configurations"""
    aggregator = LiquidityAggregator()
    
    # Add default liquidity sources (these should be configured with actual API keys)
    exchanges_config = [
        LiquiditySource(
            exchange=ExchangeType.BINANCE,
            api_key="YOUR_BINANCE_API_KEY",
            api_secret="YOUR_BINANCE_SECRET",
            sandbox=True
        ),
        LiquiditySource(
            exchange=ExchangeType.OKX,
            api_key="YOUR_OKX_API_KEY",
            api_secret="YOUR_OKX_SECRET",
            passphrase="YOUR_OKX_PASSPHRASE",
            sandbox=True
        ),
        LiquiditySource(
            exchange=ExchangeType.HUOBI,
            api_key="YOUR_HUOBI_API_KEY",
            api_secret="YOUR_HUOBI_SECRET",
            sandbox=True
        ),
        LiquiditySource(
            exchange=ExchangeType.KRAKEN,
            api_key="YOUR_KRAKEN_API_KEY",
            api_secret="YOUR_KRAKEN_SECRET",
            sandbox=True
        ),
        LiquiditySource(
            exchange=ExchangeType.GEMINI,
            api_key="YOUR_GEMINI_API_KEY",
            api_secret="YOUR_GEMINI_SECRET",
            sandbox=True
        ),
        LiquiditySource(
            exchange=ExchangeType.COINBASE,
            api_key="YOUR_COINBASE_API_KEY",
            api_secret="YOUR_COINBASE_SECRET",
            passphrase="YOUR_COINBASE_PASSPHRASE",
            sandbox=True
        )
    ]
    
    for config in exchanges_config:
        aggregator.add_liquidity_source(config)
    
    return aggregator

# FastAPI endpoints for the liquidity sharing system
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List

app = FastAPI(title="TigerEx Liquidity Sharing API", version="1.0.0")
security = HTTPBearer()

class OrderRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    amount: float
    order_type: str = "market"

class LiquidityMetricsResponse(BaseModel):
    symbol: str
    total_bid_volume: float
    total_ask_volume: float
    total_volume: float
    depth_1_percent: dict
    depth_5_percent: dict
    best_bid: float
    best_ask: float
    spread: float
    spread_percentage: float
    sources_count: int
    timestamp: str

# Global liquidity aggregator
liquidity_aggregator = None

@app.on_event("startup")
async def startup_event():
    global liquidity_aggregator
    liquidity_aggregator = await initialize_liquidity_system()

@app.get("/api/v1/liquidity/orderbook/{symbol}")
async def get_orderbook(symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get aggregated orderbook for a symbol"""
    if not liquidity_aggregator:
        raise HTTPException(status_code=500, detail="Liquidity system not initialized")
    
    try:
        async with liquidity_aggregator:
            orderbook = await liquidity_aggregator.get_aggregated_orderbook(symbol)
            return orderbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/liquidity/best-prices/{symbol}")
async def get_best_prices(symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get best bid/ask prices across all exchanges"""
    if not liquidity_aggregator:
        raise HTTPException(status_code=500, detail="Liquidity system not initialized")
    
    try:
        async with liquidity_aggregator:
            prices = await liquidity_aggregator.get_best_prices(symbol)
            return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/liquidity/route-order")
async def route_order(order: OrderRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route order to best available liquidity"""
    if not liquidity_aggregator:
        raise HTTPException(status_code=500, detail="Liquidity system not initialized")
    
    try:
        async with liquidity_aggregator:
            result = await liquidity_aggregator.route_order(
                order.symbol, 
                order.side, 
                order.amount, 
                order.order_type
            )
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/liquidity/metrics/{symbol}", response_model=LiquidityMetricsResponse)
async def get_liquidity_metrics(symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get liquidity metrics for a symbol"""
    if not liquidity_aggregator:
        raise HTTPException(status_code=500, detail="Liquidity system not initialized")
    
    try:
        async with liquidity_aggregator:
            metrics = await liquidity_aggregator.get_liquidity_metrics(symbol)
            return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/liquidity/sources")
async def get_liquidity_sources(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get list of configured liquidity sources"""
    if not liquidity_aggregator:
        raise HTTPException(status_code=500, detail="Liquidity system not initialized")
    
    sources = []
    for exchange_type, source in liquidity_aggregator.liquidity_sources.items():
        sources.append({
            "exchange": exchange_type.value,
            "enabled": source.enabled,
            "sandbox": source.sandbox
        })
    
    return {"sources": sources}

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8001)