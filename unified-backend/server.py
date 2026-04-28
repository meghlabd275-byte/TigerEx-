"""
TigerEx Unified API Server
=====================
Connects frontend to backend with all features
Version: 9.0.0

This server connects:
- Frontend to Backend
- All trading features
- AI Trading Bots
- External API
- All services
"""

import asyncio
import uvicorn
import os
import sys
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

# Import TigerEx Core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tigerex_core_engine import TigerExCoreEngine

# ============= CONFIGURATION =============
VERSION = "9.0.0"
EXCHANGE_NAME = "TigerEx"

# ============= FASTAPI APP =============
app = FastAPI(
    title=f"{EXCHANGE_NAME} API",
    version=VERSION,
    description="Complete TigerEx Trading Platform API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= MODELS =============
class RegisterRequest(BaseModel):
    email: str
    password: str
    phone: Optional[str] = ""
    referral_code: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class OrderRequest(BaseModel):
    symbol: str
    side: str  # buy or sell
    order_type: str  # market or limit
    quantity: float
    price: Optional[float] = 0

class BotRequest(BaseModel):
    name: str
    strategy: str  # grid, dca, momentum, etc.
    symbol: str
    config: Dict[str, Any]

class PeerRequest(BaseModel):
    name: str
    url: str
    api_key: str
    api_secret: str

class ExternalRequest(BaseModel):
    name: str
    permissions: List[str]

# ============= CORE ENGINE =============
engine = TigerExCoreEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    await engine.start()
    logger.info(f"✅ {EXCHANGE_NAME} v{VERSION} started")
    yield
    await engine.stop()
    logger.info(f"⏹️ {EXCHANGE_NAME} stopped")

app.router.lifespan_context = lifespan

# ============= HEALTH =============
@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "ok",
        "exchange": EXCHANGE_NAME,
        "version": VERSION,
        "timestamp": datetime.now().isoformat()
    }

# ============= EXCHANGE INFO =============
@app.get("/api/exchange/info")
async def get_exchange_info():
    """Get exchange information"""
    return {
        "exchange_name": EXCHANGE_NAME,
        "version": VERSION,
        "exchange_id": "TIGEREX-2026",
        "status": "operational",
        "maker_fee": 0.0005,
        "taker_fee": 0.001,
    }

# ============= AUTHENTICATION =============
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """User registration"""
    user_id = f"USR-{datetime.now().timestamp()}"
    
    # Create user in engine
    engine.users[user_id] = type('User', (), {
        'id': user_id,
        'email': request.email,
        'balances': {'USDT': 10000.0},  # Demo balance
        'locked_balances': {},
    })()
    
    return {
        "success": True,
        "user_id": user_id,
        "email": request.email,
        "message": "Account created successfully"
    }

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login"""
    # Find user (demo)
    for user_id, user in engine.users.items():
        if hasattr(user, 'email') and user.email == request.email:
            return {
                "success": True,
                "user_id": user_id,
                "token": f"token_{user_id}"
            }
    
    # Demo user
    user_id = "USR_demo"
    return {
        "success": True,
        "user_id": user_id,
        "token": f"token_{user_id}"
    }

# ============= TRADING =============
@app.get("/api/trading/pairs")
async def get_trading_pairs():
    """Get all trading pairs"""
    return [
        {
            "symbol": symbol,
            "base_asset": pair.base_asset,
            "quote_asset": pair.quote_asset,
            "min_quantity": pair.min_quantity,
            "price_precision": pair.price_precision,
        }
        for symbol, pair in engine.pairs.items()
    ]

@app.get("/api/trading/tickers")
async def get_tickers():
    """Get all tickers from price oracle"""
    tickers = await engine.get_tickers()
    return tickers

@app.get("/api/trading/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get specific ticker"""
    oracle = await engine.get_price(symbol)
    if not oracle:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return {
        "symbol": oracle.symbol,
        "price": oracle.price,
        "bid": oracle.bid,
        "ask": oracle.ask,
        "spread": oracle.spread,
        "volume_24h": oracle.volume_24h,
    }

@app.get("/api/trading/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 20):
    """Get orderbook"""
    return await engine.get_orderbook(symbol, limit)

@app.post("/api/trading/orders")
async def create_order(order: OrderRequest):
    """Create order"""
    result = await engine.create_order(
        user_id="USR_demo",  # Would come from auth
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price or 0
    )
    return result

@app.delete("/api/trading/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel order"""
    return await engine.cancel_order(order_id, "USR_demo")

@app.get("/api/trading/orders/open")
async def get_open_orders():
    """Get open orders"""
    orders = [o for o in engine.orders.values() if o.status == "open"]
    return [
        {
            "id": o.id,
            "symbol": o.symbol,
            "side": o.side,
            "type": o.type,
            "quantity": o.quantity,
            "filled_quantity": o.filled_quantity,
            "price": o.price,
            "status": o.status,
        }
        for o in orders
    ]

# ============= WALLET =============
@app.get("/api/wallet/balance")
async def get_balance():
    """Get user balance"""
    user = engine.users.get("USR_demo", None)
    if not user:
        # Demo user with balances
        return {
            "USDT": {"available": 10000.0, "locked": 0.0},
            "BTC": {"available": 0.5, "locked": 0.0},
            "ETH": {"available": 2.0, "locked": 0.0},
        }
    return user.balances if hasattr(user, 'balances') else {}

@app.post("/api/wallet/deposit")
async def deposit(currency: str, amount: float):
    """Deposit funds"""
    user = engine.users.get("USR_demo")
    if user and hasattr(user, 'balances'):
        current = user.balances.get(currency, 0)
        user.balances[currency] = current + amount
    return {"success": True, "currency": currency, "amount": amount}

@app.post("/api/wallet/withdraw")
async def withdraw(currency: str, amount: float, address: str):
    """Withdraw funds"""
    user = engine.users.get("USR_demo")
    if user and hasattr(user, 'balances'):
        current = user.balances.get(currency, 0)
        if current < amount:
            return {"success": False, "error": "Insufficient balance"}
        user.balances[currency] = current - amount
    return {"success": True, "currency": currency, "amount": amount}

# ============= TRADING BOTS =============
@app.get("/api/bots")
async def get_bots():
    """Get user bots"""
    return [
        {
            "id": b.id,
            "name": b.name,
            "strategy": b.strategy,
            "status": b.status,
            "symbol": b.symbol,
            "total_pnl": b.total_pnl,
            "total_trades": b.total_trades,
        }
        for b in engine.bots.values()
    ]

@app.post("/api/bots")
async def create_bot(bot: BotRequest):
    """Create trading bot"""
    return await engine.create_bot(
        user_id="USR_demo",
        name=bot.name,
        strategy=bot.strategy,
        symbol=bot.symbol,
        config=bot.config
    )

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str):
    """Start bot"""
    return await engine.start_bot(bot_id)

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str):
    """Stop bot"""
    return await engine.stop_bot(bot_id)

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str):
    """Delete bot"""
    if bot_id in engine.bots:
        del engine.bots[bot_id]
        return {"success": True, "message": "Bot deleted"}
    return {"success": False, "error": "Bot not found"}

# ============= PEERING =============
@app.get("/api/peers")
async def get_peers():
    """Get connected peers"""
    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "latency_ms": p.latency_ms,
        }
        for p in engine.peers.values()
    ]

@app.post("/api/peers")
async def add_peer(peer: PeerRequest):
    """Add TigerEx peer"""
    return await engine.add_peer(
        name=peer.name,
        url=peer.url,
        api_key=peer.api_key,
        api_secret=peer.api_secret
    )

@app.delete("/api/peers/{peer_id}")
async def remove_peer(peer_id: str):
    """Remove peer"""
    return await engine.remove_peer(peer_id)

@app.post("/api/peers/sync")
async def sync_peers():
    """Sync with peers"""
    return await engine.sync_with_peers()

# ============= EXTERNAL API =============
@app.post("/api/external/register")
async def register_external(request: ExternalRequest):
    """Register external system"""
    return await engine.register_external(request.name, request.permissions)

# ============= ADMIN =============
@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get exchange statistics"""
    return await engine.get_stats()

# ============= RUN SERVER =============
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )