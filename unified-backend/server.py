"""
TigerEx Unified API Server
=====================
Complete TigerEx Trading Platform API
Version: 9.0.0
"""

import os
import sys
import random
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional as TypingOptional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= CONFIGURATION =============
VERSION = "9.0.0"
EXCHANGE_NAME = "TigerEx"

# ============= FASTAPI APP =============
app = FastAPI(
    title=f"{EXCHANGE_NAME} API",
    version=VERSION,
    description="Complete TigerEx Trading Platform API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= IN-MEMORY STORAGE =============
class TigerExStorage:
    def __init__(self):
        self.users: Dict = {}
        self.orders: Dict = {}
        self.bots: Dict = {}
        self.peers: Dict = {}
        self._initialize_data()
    
    def _initialize_data(self):
        # Demo user
        self.users["USR_demo"] = {
            "id": "USR_demo",
            "email": "demo@tigerex.com",
            "balances": {"USDT": 10000.0, "BTC": 0.5, "ETH": 2.0}
        }
        
        # Trading pairs
        self.pairs = {}
        base_prices = {
            "BTC/USDT": 67500.0, "ETH/USDT": 3450.0, "BNB/USDT": 595.0,
            "SOL/USDT": 148.0, "XRP/USDT": 0.52, "DOGE/USDT": 0.085,
            "ADA/USDT": 0.45, "AVAX/USDT": 35.0, "DOT/USDT": 7.50,
            "MATIC/USDT": 0.72, "LINK/USDT": 14.50, "LTC/USDT": 85.0,
        }
        for symbol, price in base_prices.items():
            base, quote = symbol.split("/")
            self.pairs[symbol] = {
                "symbol": symbol,
                "base_asset": base,
                "quote_asset": quote,
                "min_quantity": 0.01,
                "price_precision": 2
            }
        
        # Price oracle (own prices)
        self.prices = {symbol: price for symbol, price in base_prices.items()}

storage = TigerExStorage()

# ============= PYDANTIC MODELS =============
class RegisterRequest(BaseModel):
    email: str
    password: str
    phone: TypingOptional[str] = ""
    referral_code: TypingOptional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class OrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: TypingOptional[float] = 0

class BotRequest(BaseModel):
    name: str
    strategy: str
    symbol: str
    config: Dict[str, Any] = {}

class PeerRequest(BaseModel):
    name: str
    url: str
    api_key: str
    api_secret: str

class ExternalRequest(BaseModel):
    name: str
    permissions: List[str]

# ============= LIFESPAN =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"✅ {EXCHANGE_NAME} v{VERSION} started")
    
    # Initialize Market Maker
    global mm_engine
    from market_maker import MarketMakerEngine
    mm_engine = MarketMakerEngine()
    await mm_engine.start()
    logger.info("✅ Market Maker Engine initialized")
    
    yield
    logger.info(f"⏹️ {EXCHANGE_NAME} stopped")

app.router.lifespan_context = lifespan

# ============= HEALTH =============
@app.get("/health")
async def health_check():
    return {"status": "ok", "exchange": EXCHANGE_NAME, "version": VERSION, "timestamp": datetime.now().isoformat()}

# ============= EXCHANGE INFO =============
@app.get("/api/exchange/info")
async def get_exchange_info():
    return {"exchange_name": EXCHANGE_NAME, "version": VERSION, "exchange_id": "TIGEREX-2026", "status": "operational", "maker_fee": 0.0005, "taker_fee": 0.001}

# ============= AUTH =============
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    user_id = f"USR_{uuid.uuid4().hex[:8]}"
    storage.users[user_id] = {"id": user_id, "email": request.email, "balances": {"USDT": 10000.0}}
    return {"success": True, "user_id": user_id, "email": request.email}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    return {"success": True, "user_id": "USR_demo", "token": f"token_USR_demo"}

# ============= TRADING =============
@app.get("/api/trading/pairs")
async def get_trading_pairs():
    return list(storage.pairs.values())

@app.get("/api/trading/tickers")
async def get_tickers():
    return [{"symbol": s, "price": p, "change_percent_24h": random.uniform(-5, 5)} for s, p in storage.prices.items()]

@app.get("/api/trading/ticker/{symbol}")
async def get_ticker(symbol: str):
    if symbol not in storage.prices:
        raise HTTPException(status_code=404, detail="Symbol not found")
    price = storage.prices[symbol]
    spread = price * 0.0005
    return {"symbol": symbol, "price": price, "bid": price-spread, "ask": price+spread, "spread": spread, "volume_24h": random.uniform(100000, 1000000)}

@app.get("/api/trading/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 20):
    if symbol not in storage.prices:
        raise HTTPException(status_code=404, detail="Symbol not found")
    mid = storage.prices[symbol]
    bids = [[mid - i*mid*0.0002, round(random.uniform(0.1, 5), 4)] for i in range(1, limit+1)]
    asks = [[mid + i*mid*0.0002, round(random.uniform(0.1, 5), 4)] for i in range(1, limit+1)]
    return {"symbol": symbol, "bids": bids, "asks": asks}

@app.post("/api/trading/orders")
async def create_order(order: OrderRequest):
    order_id = f"ORD_{uuid.uuid4().hex[:8]}"
    storage.orders[order_id] = {
        "id": order_id, "symbol": order.symbol, "side": order.side,
        "type": order.order_type, "quantity": order.quantity,
        "price": order.price or storage.prices.get(order.symbol, 0),
        "status": "filled", "created_at": datetime.now().isoformat()
    }
    return {"success": True, "order_id": order_id, "status": "filled"}

@app.get("/api/trading/orders/open")
async def get_open_orders():
    return [o for o in storage.orders.values() if o.get("status") == "open"]

# ============= WALLET =============
@app.get("/api/wallet/balance")
async def get_balance():
    return storage.users.get("USR_demo", {}).get("balances", {})

# ============= BOTS =============
@app.get("/api/bots")
async def get_bots():
    return [{"id": b["id"], "name": b["name"], "strategy": b["strategy"], "status": b["status"], "symbol": b["symbol"]} for b in storage.bots.values()]

@app.post("/api/bots")
async def create_bot(bot: BotRequest):
    bot_id = f"BOT_{uuid.uuid4().hex[:8]}"
    storage.bots[bot_id] = {"id": bot_id, "user_id": "USR_demo", "name": bot.name, "strategy": bot.strategy, "symbol": bot.symbol, "config": bot.config, "status": "paused"}
    return {"success": True, "bot_id": bot_id}

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str):
    if bot_id not in storage.bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    storage.bots[bot_id]["status"] = "active"
    return {"success": True, "status": "active"}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str):
    if bot_id not in storage.bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    storage.bots[bot_id]["status"] = "paused"
    return {"success": True, "status": "paused"}

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str):
    if bot_id in storage.bots:
        del storage.bots[bot_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Bot not found")

# ============= PEERS =============
@app.get("/api/peers")
async def get_peers():
    return [{"id": p["id"], "name": p["name"], "status": p["status"]} for p in storage.peers.values()]

@app.post("/api/peers")
async def add_peer(peer: PeerRequest):
    peer_id = f"PEER_{uuid.uuid4().hex[:8]}"
    storage.peers[peer_id] = {"id": peer_id, "name": peer.name, "url": peer.url, "status": "connected"}
    return {"success": True, "peer_id": peer_id}

@app.delete("/api/peers/{peer_id}")
async def remove_peer(peer_id: str):
    if peer_id in storage.peers:
        del storage.peers[peer_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Peer not found")

@app.post("/api/peers/sync")
async def sync_peers():
    return {"success": True, "peers_synced": len(storage.peers)}

# ============= EXTERNAL =============
@app.post("/api/external/register")
async def register_external(request: ExternalRequest):
    api_key = f"TX_{uuid.uuid4().hex[:16]}"
    api_secret = uuid.uuid4().hex
    return {"success": True, "api_key": api_key, "api_secret": api_secret, "permissions": request.permissions}

# ============= ADMIN =============
@app.get("/api/admin/stats")
async def get_admin_stats():
    return {"exchange_name": EXCHANGE_NAME, "version": VERSION, "total_users": len(storage.users), "total_orders": len(storage.orders), "active_bots": len([b for b in storage.bots.values() if b.get("status") == "active"])}

# ============= MARKET MAKER =============
mm_engine = None

def get_mm_engine():
    global mm_engine
    if mm_engine is None:
        from market_maker import MarketMakerEngine
        mm_engine = MarketMakerEngine()
    return mm_engine

@app.get("/api/market-maker/stats")
async def get_mm_stats():
    engine = get_mm_engine()
    return await engine.get_stats()

@app.get("/api/market-maker")
async def get_mms(owner_id: str = ""):
    engine = get_mm_engine()
    return await engine.get_all_market_makers(owner_id)

@app.post("/api/market-maker")
async def create_mm(
    name: str,
    strategy: str = "all",
    symbols: List[str] = None,
    owner_id: str = "USR_demo"
):
    engine = get_mm_engine()
    return await engine.create_market_maker(owner_id, name, strategy, symbols or [])

@app.get("/api/market-maker/{mm_id}")
async def get_mm(mm_id: str):
    engine = get_mm_engine()
    return await engine.get_market_maker(mm_id)

@app.post("/api/market-maker/{mm_id}/start")
async def start_mm(mm_id: str):
    engine = get_mm_engine()
    return await engine.start_market_maker(mm_id)

@app.post("/api/market-maker/{mm_id}/stop")
async def stop_mm(mm_id: str):
    engine = get_mm_engine()
    return await engine.stop_market_maker(mm_id)

@app.delete("/api/market-maker/{mm_id}")
async def delete_mm(mm_id: str):
    engine = get_mm_engine()
    return await engine.delete_market_maker(mm_id)

@app.get("/api/market-maker/orderbook/{symbol}")
async def get_mm_orderbook(symbol: str, limit: int = 20):
    engine = get_mm_engine()
    return await engine.get_orderbook(symbol, limit)

@app.post("/api/market-maker/{mm_id}/arbitrage")
async def execute_arbitrage(mm_id: str):
    engine = get_mm_engine()
    return await engine.execute_arbitrage(mm_id)

@app.post("/api/market-maker/{mm_id}/liquidity")
async def provide_liquidity(mm_id: str, symbol: str, amount: float):
    engine = get_mm_engine()
    return await engine.provide_liquidity(mm_id, symbol, amount)

@app.post("/api/market-maker/{mm_id}/stabilize")
async def stabilize_price(mm_id: str, symbol: str, target_price: float):
    engine = get_mm_engine()
    return await engine.stabilize_price(mm_id, symbol, target_price)

# ============= RUN =============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
