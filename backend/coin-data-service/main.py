#!/usr/bin/env python3
"""
TigerEx Coin Data API Service
Dynamically serves coin, network, and trading pair data with caching
Production-ready with rate limiting and Redis caching
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import aiohttp
import redis.asyncio as redis
from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
app = FastAPI(
    title="TigerEx Coin Data API",
    description="API for coins, networks, and trading pairs",
    version="2.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'coin-data'))
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '1000'))  # requests per minute

# Global state
_redis: Optional[redis.Redis] = None
_cache: Dict[str, Any] = {}


# ==================== DATA MODELS ====================

class Network(BaseModel):
    id: int
    name: str
    symbol: str
    chain_id: str
    type: str
    rpc_url: Optional[str] = None
    explorer_url: Optional[str] = None
    color: str
    status: str
    confirmations: int = 1
    min_deposit: float = 0


class Coin(BaseModel):
    id: int
    name: str
    symbol: str
    type: str
    status: str
    is_listed: bool
    decimals: int = 18
    contract_address: Optional[str] = None
    networks: List[int] = []
    description: Optional[str] = None


class TradingPair(BaseModel):
    id: int
    base_coin_id: int
    quote_coin_id: int
    pair_symbol: str
    status: str
    is_active: bool
    maker_fee: float
    taker_fee: float
    min_trade_amount: float
    price_precision: int
    quantity_precision: int


class TickerData(BaseModel):
    pair_symbol: str
    last_price: float
    price_change_24h: float
    price_change_pct_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float


# ==================== DATA LOADING ====================

async def load_coin_data() -> Dict[str, Any]:
    """Load coin data from JSON configuration."""
    cache_key = "coin_data"
    
    # Try Redis first
    if _redis:
        try:
            cached = await _redis.get(cache_key)
            if cached:
                logger.info("Loaded coin data from Redis")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
    
    # Fallback to memory
    if cache_key in _cache:
        logger.info("Loaded coin data from memory")
        return _cache[cache_key]
    
    # Load from file
    data_file = os.path.join(DATA_DIR, 'data.json')
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                content = f.read()
                # Replace template vars
                for key in os.environ:
                    if key.startswith(('BTC_', 'ETH_', 'BSC_', 'SOL_', 'MATIC_', 'AVAX_', 'ARB_', 'OP_', 'TRX_')):
                        content = content.replace(f"${{{key}}", os.environ.get(key, ''))
                
                data = json.loads(content)
                
                # Cache it
                _cache[cache_key] = data
                if _redis:
                    await _redis.setex(cache_key, CACHE_TTL, json.dumps(data))
                
                logger.info(f"Loaded coin data from {data_file}")
                return data
        except Exception as e:
            logger.error(f"Failed to load coin data: {e}")
    
    # Return embedded defaults
    return _get_default_data()


def _get_default_data() -> Dict[str, Any]:
    """Get default coin data (embedded)."""
    return {
        "networks": [
            {"id": 1, "name": "Bitcoin", "symbol": "BTC", "chain_id": "1", "type": "main", 
             "rpc_url": None, "explorer_url": "https://blockstream.info", "color": "#F7931A", 
             "status": "active", "confirmations": 1, "min_deposit": 0.0001},
            {"id": 2, "name": "Ethereum", "symbol": "ETH", "chain_id": "1", "type": "erc20",
             "rpc_url": None, "explorer_url": "https://etherscan.io", "color": "#627EEA",
             "status": "active", "confirmations": 12, "min_deposit": 0.001},
            {"id": 3, "name": "BNB Smart Chain", "symbol": "BSC", "chain_id": "56", "type": "bep20",
             "rpc_url": None, "explorer_url": "https://bscscan.com", "color": "#F0B90B",
             "status": "active", "confirmations": 15, "min_deposit": 0.001},
            {"id": 4, "name": "Solana", "symbol": "SOL", "chain_id": "main", "type": "spl",
             "rpc_url": None, "explorer_url": "https://solscan.io", "color": "#00D4A1",
             "status": "active", "confirmations": 1, "min_deposit": 0.01},
            {"id": 5, "name": "Tether USD", "symbol": "USDT", "chain_id": "main", "type": "erc20",
             "rpc_url": None, "explorer_url": "https://etherscan.io", "color": "#26A17A",
             "status": "active", "confirmations": 12, "min_deposit": 10},
        ],
        "coins": [
            {"id": 1, "name": "Bitcoin", "symbol": "BTC", "type": "coin", "status": "active",
             "is_listed": True, "decimals": 8, "networks": [1], "description": "Bitcoin"},
            {"id": 2, "name": "Ethereum", "symbol": "ETH", "type": "token", "status": "active",
             "is_listed": True, "decimals": 18, "networks": [2], "description": "Ethereum"},
            {"id": 3, "name": "BNB", "symbol": "BNB", "type": "token", "status": "active",
             "is_listed": True, "decimals": 18, "networks": [3], "description": "BNB"},
            {"id": 4, "name": "Solana", "symbol": "SOL", "type": "coin", "status": "active",
             "is_listed": True, "decimals": 9, "networks": [4], "description": "Solana"},
            {"id": 5, "name": "Tether USD", "symbol": "USDT", "type": "token", "status": "active",
             "is_listed": True, "decimals": 6, "networks": [2], "description": "USDT"},
        ],
        "trading_pairs": [
            {"id": 1, "base_coin_id": 1, "quote_coin_id": 5, "pair_symbol": "BTC/USDT",
             "status": "active", "is_active": True, "maker_fee": 0.001, "taker_fee": 0.001,
             "min_trade_amount": 0.0001, "price_precision": 2, "quantity_precision": 6},
            {"id": 2, "base_coin_id": 2, "quote_coin_id": 5, "pair_symbol": "ETH/USDT",
             "status": "active", "is_active": True, "maker_fee": 0.001, "taker_fee": 0.001,
             "min_trade_amount": 0.001, "price_precision": 2, "quantity_precision": 6},
            {"id": 3, "base_coin_id": 3, "quote_coin_id": 5, "pair_symbol": "BNB/USDT",
             "status": "active", "is_active": True, "maker_fee": 0.001, "taker_fee": 0.001,
             "min_trade_amount": 0.001, "price_precision": 2, "quantity_precision": 4},
            {"id": 4, "base_coin_id": 4, "quote_coin_id": 5, "pair_symbol": "SOL/USDT",
             "status": "active", "is_active": True, "maker_fee": 0.001, "taker_fee": 0.001,
             "min_trade_amount": 0.01, "price_precision": 2, "quantity_precision": 4},
        ]
    }


# ==================== REDIS CONNECTION ====================

async def get_redis() -> Optional[redis.Redis]:
    """Get Redis connection."""
    global _redis
    if _redis is None:
        try:
            _redis = redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await _redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            _redis = None
    return _redis


# ==================== RATE LIMITING ====================

rate_limits: Dict[str, List[datetime]] = {}


async def check_rate_limit(client_id: str) -> bool:
    """Check rate limit for client."""
    now = datetime.utcnow()
    minute_ago = now - timedelta(minutes=1)
    
    if client_id not in rate_limits:
        rate_limits[client_id] = []
    
    # Clean old entries
    rate_limits[client_id] = [
        t for t in rate_limits[client_id] if t > minute_ago
    ]
    
    if len(rate_limits[client_id]) >= RATE_LIMIT:
        return False
    
    rate_limits[client_id].append(now)
    return True


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API root."""
    return {
        "name": "TigerEx Coin Data API",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/networks")
async def get_networks(
    status: Optional[str] = Query(None, description="Filter by status"),
) -> Dict[str, Any]:
    """Get all blockchain networks."""
    data = await load_coin_data()
    networks = data.get("networks", [])
    
    if status:
        networks = [n for n in networks if n.get("status") == status]
    
    return {
        "success": True,
        "data": networks,
        "count": len(networks)
    }


@app.get("/api/v1/networks/{symbol}")
async def get_network(symbol: str) -> Dict[str, Any]:
    """Get network by symbol."""
    data = await load_coin_data()
    networks = data.get("networks", [])
    
    for n in networks:
        if n.get("symbol", "").upper() == symbol.upper():
            return {"success": True, "data": n}
    
    raise HTTPException(status_code=404, detail="Network not found")


@app.get("/api/v1/coins")
async def get_coins(
    status: Optional[str] = Query(None, description="Filter by status"),
    is_listed: Optional[bool] = Query(None, description="Filter by listed status"),
) -> Dict[str, Any]:
    """Get all coins/tokens."""
    data = await load_coin_data()
    coins = data.get("coins", [])
    
    if status:
        coins = [c for c in coins if c.get("status") == status]
    
    if is_listed is not None:
        coins = [c for c in coins if c.get("is_listed") == is_listed]
    
    return {
        "success": True,
        "data": coins,
        "count": len(coins)
    }


@app.get("/api/v1/coins/{symbol}")
async def get_coin(symbol: str) -> Dict[str, Any]:
    """Get coin by symbol."""
    data = await load_coin_data()
    coins = data.get("coins", [])
    
    for c in coins:
        if c.get("symbol", "").upper() == symbol.upper():
            return {"success": True, "data": c}
    
    raise HTTPException(status_code=404, detail="Coin not found")


@app.get("/api/v1/pairs")
async def get_pairs(
    status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active"),
) -> Dict[str, Any]:
    """Get all trading pairs."""
    data = await load_coin_data()
    pairs = data.get("trading_pairs", [])
    
    if status:
        pairs = [p for p in pairs if p.get("status") == status]
    
    if is_active is not None:
        pairs = [p for p in pairs if p.get("is_active") == is_active]
    
    return {
        "success": True,
        "data": pairs,
        "count": len(pairs)
    }


@app.get("/api/v1/pairs/{symbol}")
async def get_pair(symbol: str) -> Dict[str, Any]:
    """Get trading pair by symbol."""
    data = await load_coin_data()
    pairs = data.get("trading_pairs", [])
    
    for p in pairs:
        if p.get("pair_symbol", "").upper() == symbol.upper():
            return {"success": True, "data": p}
    
    raise HTTPException(status_code=404, detail="Trading pair not found")


@app.get("/api/v1/ticker")
async def get_ticker(
    symbol: Optional[str] = Query(None, description="Trading pair symbol"),
) -> Dict[str, Any]:
    """Get ticker data for trading pairs."""
    # In production, this would fetch from market data service
    # Using embedded mock data for demonstration
    tickers = {
        "BTC/USDT": {
            "pair_symbol": "BTC/USDT",
            "last_price": 42547.32,
            "price_change_24h": 1045.67,
            "price_change_pct_24h": 2.45,
            "high_24h": 43100.00,
            "low_24h": 41500.00,
            "volume_24h": 28450000000,
            "quote_volume_24h": 0,
        },
        "ETH/USDT": {
            "pair_symbol": "ETH/USDT",
            "last_price": 2256.78,
            "price_change_24h": 68.45,
            "price_change_pct_24h": 3.12,
            "high_24h": 2300.00,
            "low_24h": 2180.00,
            "volume_24h": 15200000000,
            "quote_volume_24h": 0,
        },
        "BNB/USDT": {
            "pair_symbol": "BNB/USDT",
            "last_price": 324.56,
            "price_change_24h": -3.95,
            "price_change_pct_24h": -1.20,
            "high_24h": 330.00,
            "low_24h": 320.00,
            "volume_24h": 1800000000,
            "quote_volume_24h": 0,
        },
        "SOL/USDT": {
            "pair_symbol": "SOL/USDT",
            "last_price": 98.45,
            "price_change_24h": 5.28,
            "price_change_pct_24h": 5.67,
            "high_24h": 102.00,
            "low_24h": 92.00,
            "volume_24h": 850000000,
            "quote_volume_24h": 0,
        }
    }
    
    if symbol:
        if symbol.upper() in tickers:
            return {"success": True, "data": tickers[symbol.upper()]}
        raise HTTPException(status_code=404, detail="Ticker not found")
    
    return {
        "success": True,
        "data": list(tickers.values()),
        "count": len(tickers)
    }


@app.get("/api/v1/search")
async def search(q: str = Query(..., min_length=1)) -> Dict[str, Any]:
    """Search coins and pairs."""
    data = await load_coin_data()
    q_upper = q.upper()
    
    results = []
    
    # Search coins
    for c in data.get("coins", []):
        if (q_upper in c.get("symbol", "").upper() or 
            q_upper in c.get("name", "").upper()):
            results.append({"type": "coin", "data": c})
    
    # Search pairs
    for p in data.get("trading_pairs", []):
        if q_upper in p.get("pair_symbol", "").upper():
            results.append({"type": "pair", "data": p})
    
    return {
        "success": True,
        "data": results,
        "count": len(results)
    }


# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_id = request.client.host
    
    if not await check_rate_limit(client_id):
        return JSONResponse(
            status_code=429,
            content={"success": False, "error": "Rate limit exceeded"}
        )
    
    return await call_next(request)


# ==================== LIFECYCLE ====================

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("Starting TigerEx Coin Data API...")
    await get_redis()


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger.info("Shutting down...")
    if _redis:
        await _redis.close()


# ==================== MAIN ====================

if __name__ == "__main__":
    port = int(os.getenv('PORT', '8080'))
    uvicorn.run(app, host="0.0.0.0", port=port)