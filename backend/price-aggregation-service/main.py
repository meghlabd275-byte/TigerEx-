#!/usr/bin/env python3
"""
TigerEx Price Aggregation Service
Real-time price aggregation from major exchanges (Binance, Coinbase, Kraken, Bybit, etc.)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from admin.admin_routes import router as admin_router
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
import aiohttp
import aioredis
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import websockets
import hashlib

# @file main.py
# @author TigerEx Development Team
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Price Aggregation Service",
    description="Real-time price aggregation from major cryptocurrency exchanges",
    version="1.0.0"
)

app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exchange API endpoints
EXCHANGE_ENDPOINTS = {
    "binance": {
        "spot": "https://api.binance.com/api/v3/ticker/price",
        "futures": "https://fapi.binance.com/fapi/v1/ticker/price",
        "websocket": "wss://stream.binance.com:9443/ws"
    },
    "coinbase": {
        "spot": "https://api.coinbase.com/v2/prices",
        "websocket": "wss://ws-feed.exchange.coinbase.com"
    },
    "kraken": {
        "spot": "https://api.kraken.com/0/public/Ticker",
        "websocket": "wss://ws.kraken.com"
    },
    "bybit": {
        "spot": "https://api.bybit.com/v5/market/tickers",
        "linear": "https://api.bybit.com/v5/market/tickers?category=linear",
        "websocket": "wss://stream.bybit.com/v5/public/spot"
    },
    "kucoin": {
        "spot": "https://api.kucoin.com/api/v1/market/allTickers",
        "websocket": "wss://ws-api.kucoin.com"
    },
    "okx": {
        "spot": "https://www.okx.com/api/v5/market/tickers",
        "websocket": "wss://ws.okx.com:8443/ws/v5/public"
    },
    "huobi": {
        "spot": "https://api.huobi.pro/market/tickers",
        "websocket": "wss://api.huobi.pro/ws"
    },
    "bitget": {
        "spot": "https://api.bitget.com/api/v2/spot/tickers",
        "websocket": "wss://ws.bitget.com/v2/ws/spot/public"
    },
    "gate": {
        "spot": "https://api.gateio.ws/api/v4/spot/tickers",
        "websocket": "wss://api.gateio.ws/ws/v4/"
    },
    "bitfinex": {
        "spot": "https://api-pub.bitfinex.com/v2/tickers",
        "websocket": "wss://api-pub.bitfinex.com/ws/2"
    }
}

# Price cache
price_cache: Dict[str, Any] = {}
websocket_connections: List[WebSocket] = []

class PriceData(BaseModel):
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    exchange: str
    timestamp: datetime

class AggregatedPrice(BaseModel):
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    exchanges: List[str]
    best_bid: float
    best_ask: float
    spread: float
    timestamp: datetime

async def fetch_binance_prices() -> Dict[str, Any]:
    """Fetch prices from Binance"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["binance"]["spot"], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    for item in data:
                        symbol = item["symbol"]
                        if symbol.endswith("USDT"):
                            prices[symbol] = {
                                "price": float(item["price"]),
                                "exchange": "binance"
                            }
                    return prices
    except Exception as e:
        logger.error(f"Binance API error: {e}")
    return {}

async def fetch_coinbase_prices() -> Dict[str, Any]:
    """Fetch prices from Coinbase"""
    try:
        popular_pairs = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD", 
                        "DOGE-USD", "DOT-USD", "AVAX-USD", "LINK-USD", "MATIC-USD"]
        
        prices = {}
        async with aiohttp.ClientSession() as session:
            for pair in popular_pairs:
                try:
                    base, quote = pair.split("-")
                    symbol = f"{base}{quote}"
                    url = f"{EXCHANGE_ENDPOINTS['coinbase']['spot']}/{pair}/spot"
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices[symbol] = {
                                "price": float(data["data"]["amount"]),
                                "exchange": "coinbase"
                            }
                except:
                    continue
        return prices
    except Exception as e:
        logger.error(f"Coinbase API error: {e}")
    return {}

async def fetch_kraken_prices() -> Dict[str, Any]:
    """Fetch prices from Kraken"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["kraken"]["spot"], 
                                 params={"pair": "XXBTZUSD,XETHZUSD,XXRPZUSD,XSOLZUSD,XADAZUSD"},
                                 timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "result" in data:
                        for pair, info in data["result"].items():
                            base = pair.replace("X", "").replace("ZUSD", "USD")
                            prices[base] = {
                                "price": float(info["c"][0]),
                                "exchange": "kraken"
                            }
                    return prices
    except Exception as e:
        logger.error(f"Kraken API error: {e}")
    return {}

async def fetch_bybit_prices() -> Dict[str, Any]:
    """Fetch prices from Bybit"""
    try:
        headers = {"Referer": "https://www.bybit.com"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                EXCHANGE_ENDPOINTS["bybit"]["spot"],
                params={"category": "spot", "limit": 100},
                headers=headers,
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "result" in data and "list" in data["result"]:
                        for item in data["result"]["list"]:
                            symbol = item["symbol"]
                            prices[symbol] = {
                                "price": float(item["lastPrice"]),
                                "exchange": "bybit"
                            }
                    return prices
    except Exception as e:
        logger.error(f"Bybit API error: {e}")
    return {}

async def fetch_kucoin_prices() -> Dict[str, Any]:
    """Fetch prices from KuCoin"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["kucoin"]["spot"], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "data" in data and "ticker" in data["data"]:
                        for item in data["data"]["ticker"]:
                            symbol = item["symbol"]
                            prices[symbol] = {
                                "price": float(item["last"]),
                                "exchange": "kucoin"
                            }
                    return prices
    except Exception as e:
        logger.error(f"KuCoin API error: {e}")
    return {}

async def fetch_okx_prices() -> Dict[str, Any]:
    """Fetch prices from OKX"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                EXCHANGE_ENDPOINTS["okx"]["spot"],
                params={"instType": "SPOT"},
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "data" in data:
                        for item in data["data"]:
                            symbol = item["instId"]
                            prices[symbol] = {
                                "price": float(item["last"]),
                                "exchange": "okx"
                            }
                    return prices
    except Exception as e:
        logger.error(f"OKX API error: {e}")
    return {}

async def fetch_huobi_prices() -> Dict[str, Any]:
    """Fetch prices from Huobi"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["huobi"]["spot"], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "data" in data:
                        for item in data["data"]:
                            symbol = item["symbol"].upper()
                            if symbol.endswith("USDT"):
                                prices[symbol] = {
                                    "price": float(item["close"]),
                                    "exchange": "huobi"
                                }
                    return prices
    except Exception as e:
        logger.error(f"Huobi API error: {e}")
    return {}

async def fetch_bitget_prices() -> Dict[str, Any]:
    """Fetch prices from Bitget"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                EXCHANGE_ENDPOINTS["bitget"]["spot"],
                params={"limit": 100},
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    if "data" in data:
                        for item in data["data"]:
                            symbol = item["symbol"]
                            prices[symbol] = {
                                "price": float(item["last"]),
                                "exchange": "bitget"
                            }
                    return prices
    except Exception as e:
        logger.error(f"Bitget API error: {e}")
    return {}

async def fetch_gate_prices() -> Dict[str, Any]:
    """Fetch prices from Gate.io"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["gate"]["spot"], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    for item in data:
                        symbol = item["currency_pair"]
                        prices[symbol] = {
                            "price": float(item["last"]),
                            "exchange": "gate"
                        }
                    return prices
    except Exception as e:
        logger.error(f"Gate.io API error: {e}")
    return {}

async def fetch_bitfinex_prices() -> Dict[str, Any]:
    """Fetch prices from Bitfinex"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_ENDPOINTS["bitfinex"]["spot"], timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    for item in data:
                        if isinstance(item, list) and len(item) > 1:
                            symbol = item[0]
                            if symbol.startswith("t") and "USD" in symbol:
                                symbol = symbol.replace("t", "").replace("USD", "USDT")
                                prices[symbol] = {
                                    "price": float(item[1]) if item[1] else 0,
                                    "exchange": "bitfinex"
                                }
                    return prices
    except Exception as e:
        logger.error(f"Bitfinex API error: {e}")
    return {}

async def aggregate_all_prices() -> Dict[str, AggregatedPrice]:
    """Aggregate prices from all exchanges"""
    global price_cache
    
    all_prices = {}
    exchange_prices = {}
    
    # Fetch from all exchanges concurrently
    tasks = [
        fetch_binance_prices(),
        fetch_coinbase_prices(),
        fetch_kraken_prices(),
        fetch_bybit_prices(),
        fetch_kucoin_prices(),
        fetch_okx_prices(),
        fetch_huobi_prices(),
        fetch_bitget_prices(),
        fetch_gate_prices(),
        fetch_bitfinex_prices()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    exchange_names = ["binance", "coinbase", "kraken", "bybit", "kucoin", "okx", "huobi", "bitget", "gate", "bitfinex"]
    
    for exchange_name, prices in zip(exchange_names, results):
        if isinstance(prices, dict):
            exchange_prices[exchange_name] = prices
            for symbol, data in prices.items():
                if symbol not in all_prices:
                    all_prices[symbol] = {
                        "prices": [],
                        "volumes": [],
                        "exchanges": []
                    }
                all_prices[symbol]["prices"].append(data["price"])
                all_prices[symbol]["exchanges"].append(exchange_name)
    
    # Calculate aggregated prices
    aggregated = {}
    for symbol, data in all_prices.items():
        if data["prices"]:
            prices = data["prices"]
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            spread = max_price - min_price
            
            aggregated[symbol] = AggregatedPrice(
                symbol=symbol,
                price=round(avg_price, 8),
                change_24h=0,  # Would require historical data
                change_percent_24h=0,
                volume_24h=0,
                high_24h=max_price,
                low_24h=min_price,
                exchanges=data["exchanges"],
                best_bid=min_price,
                best_ask=max_price,
                spread=round(spread, 8),
                timestamp=datetime.utcnow()
            )
    
    price_cache = aggregated
    return aggregated

async def update_prices_periodically():
    """Update prices every 10 seconds"""
    while True:
        try:
            await aggregate_all_prices()
            
            # Broadcast to WebSocket clients
            if websocket_connections:
                message = json.dumps({
                    "type": "price_update",
                    "data": price_cache,
                    "timestamp": datetime.utcnow().isoformat()
                })
                for ws in websocket_connections:
                    try:
                        await ws.send_text(message)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Price update error: {e}")
        
        await asyncio.sleep(10)

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "price-aggregation"}

@app.get("/api/v1/prices")
async def get_all_prices():
    """Get all aggregated prices"""
    if not price_cache:
        await aggregate_all_prices()
    return {
        "success": True,
        "count": len(price_cache),
        "prices": price_cache,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/prices/{symbol}")
async def get_symbol_price(symbol: str):
    """Get price for specific symbol"""
    if not price_cache:
        await aggregate_all_prices()
    
    symbol = symbol.upper()
    
    # Try exact match first
    if symbol in price_cache:
        return {"success": True, "data": price_cache[symbol]}
    
    # Try with USDT suffix
    if not symbol.endswith("USDT"):
        symbol_with_usdt = f"{symbol}USDT"
        if symbol_with_usdt in price_cache:
            return {"success": True, "data": price_cache[symbol_with_usdt]}
    
    raise HTTPException(status_code=404, detail="Symbol not found")

@app.get("/api/v1/prices/{symbol}/compare")
async def compare_symbol_prices(symbol: str):
    """Compare prices across exchanges for a symbol"""
    if not price_cache:
        await aggregate_all_prices()
    
    symbol = symbol.upper()
    if not symbol.endswith("USDT"):
        symbol = f"{symbol}USDT"
    
    if symbol not in price_cache:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    return {
        "success": True,
        "symbol": symbol,
        "aggregated": price_cache[symbol],
        "exchanges": EXCHANGE_ENDPOINTS.keys()
    }

@app.get("/api/v1/exchanges")
async def get_exchanges():
    """Get list of supported exchanges"""
    return {
        "success": True,
        "exchanges": [
            {
                "name": name,
                "endpoints": endpoints,
                "status": "active" if name in ["binance", "coinbase", "kraken", "bybit", "kucoin", "okx", "huobi", "bitget", "gate", "bitfinex"] else "inactive"
            }
            for name, endpoints in EXCHANGE_ENDPOINTS.items()
        ]
    }

@app.get("/api/v1/trending")
async def get_trending_pairs(limit: int = 10):
    """Get trending pairs based on number of exchanges"""
    if not price_cache:
        await aggregate_all_prices()
    
    trending = sorted(
        price_cache.items(),
        key=lambda x: len(x[1].exchanges),
        reverse=True
    )[:limit]
    
    return {
        "success": True,
        "trending": [t[1] for t in trending]
    }

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial prices
        if not price_cache:
            await aggregate_all_prices()
        
        await websocket.send_json({
            "type": "initial",
            "data": price_cache,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    # Handle subscription to specific symbols
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbols": message.get("symbols", [])
                    })
                elif message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "keepalive"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

@app.on_event("startup")
async def startup():
    """Start background price updates"""
    asyncio.create_task(update_prices_periodically())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)