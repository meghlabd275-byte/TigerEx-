"""
TigerEx Unified API Server - Complete
================================
All systems connected
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
app = FastAPI(title=f"{EXCHANGE_NAME} API", version=VERSION, description="Complete TigerEx Trading Platform")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ============= IN-MEMORY STORAGE =============
class TigerExStorage:
    def __init__(self):
        self.users = {"USR_demo": {"id": "USR_demo", "email": "demo@tigerex.com", "balances": {"USDT": 10000, "BTC": 0.5, "ETH": 2.0}}}
        self.orders = {}
        self.bots = {}
        self.pairs = {}
        self._initialize()
    
    def _initialize(self):
        prices = {"BTC/USDT": 67500, "ETH/USDT": 3450, "BNB/USDT": 595, "SOL/USDT": 148, "XRP/USDT": 0.52, "DOGE/USDT": 0.085, "ADA/USDT": 0.45, "AVAX/USDT": 35, "DOT/USDT": 7.5, "MATIC/USDT": 0.72, "LINK/USDT": 14.5, "LTC/USDT": 85}
        for symbol, price in prices.items():
            base, quote = symbol.split("/")
            self.pairs[symbol] = {"symbol": symbol, "base_asset": base, "quote_asset": quote, "price": price}

storage = TigerExStorage()

# ============= MODELS =============
class RegisterRequest(BaseModel): email: str; password: str; phone: str = ""; referral_code: str = ""
class LoginRequest(BaseModel): email: str; password: str
class OrderRequest(BaseModel): symbol: str; side: str; order_type: str; quantity: float; price: float = 0
class BotRequest(BaseModel): name: str; strategy: str; symbol: str; config: Dict[str, Any] = {}
class PairRequest(BaseModel): symbol: str; base: str; quote: str

# ============= LIFESPAN ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"✅ {EXCHANGE_NAME} v{VERSION} started")
    # Initialize pair manager
    from pairs_manager import TradingPairManager
    global pair_manager
    pair_manager = TradingPairManager()
    logger.info("✅ Trading Pairs Manager initialized")
    yield
    logger.info(f"⏹️ {EXCHANGE_NAME} stopped")

app.router.lifespan_context = lifespan

# ============ CORE ENDPOINTS ============
@app.get("/health")
async def health(): return {"status": "ok", "exchange": EXCHANGE_NAME, "version": VERSION}

@app.get("/api/exchange/info")
async def exchange_info(): return {"exchange_name": EXCHANGE_NAME, "version": VERSION, "status": "operational", "maker_fee": 0.0005, "taker_fee": 0.001}

@app.post("/api/auth/register")
async def register(r: RegisterRequest):
    user_id = f"USR_{uuid.uuid4().hex[:8]}"
    storage.users[user_id] = {"id": user_id, "email": r.email, "balances": {"USDT": 10000}}
    return {"success": True, "user_id": user_id}

@app.post("/api/auth/login")
async def login(r: LoginRequest): return {"success": True, "user_id": "USR_demo", "token": "token_USR_demo"}

# ============ TRADING PAIRS ============
@app.get("/api/trading/pairs")
async def get_trading_pairs(): return list(storage.pairs.values())

@app.get("/api/trading/tickers")
async def get_tickers(): return [{"symbol": s, "price": p["price"], "change": random.uniform(-5, 5)} for s, p in storage.pairs.items()]

@app.get("/api/trading/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 20):
    pair = storage.pairs.get(symbol) or storage.pairs.get(symbol.replace("_", "/"))
    if not pair: raise HTTPException(404, "Symbol not found")
    mid = pair["price"]
    bids = [[mid - i*mid*0.0002, round(random.uniform(0.1, 5), 4)] for i in range(1, limit+1)]
    asks = [[mid + i*mid*0.0002, round(random.uniform(0.1, 5), 4)] for i in range(1, limit+1)]
    return {"symbol": symbol, "bids": bids, "asks": asks}

@app.post("/api/trading/orders")
async def create_order(o: OrderRequest):
    order_id = f"ORD_{uuid.uuid4().hex[:8]}"
    storage.orders[order_id] = {"id": order_id, "symbol": o.symbol, "side": o.side, "qty": o.quantity, "price": o.price, "status": "filled"}
    return {"success": True, "order_id": order_id, "status": "filled"}

@app.get("/api/trading/orders/open")
async def get_open_orders(): return [o for o in storage.orders.values() if o.get("status") == "open"]

# ============ WALLET ============
@app.get("/api/wallet/balance")
async def get_balance(): return storage.users.get("USR_demo", {}).get("balances", {})

# ============ TRADING BOTS ============
@app.get("/api/bots")
async def get_bots(): return [{"id": b["id"], "name": b["name"], "status": b["status"]} for b in storage.bots.values()]

@app.post("/api/bots")
async def create_bot(b: BotRequest):
    bot_id = f"BOT_{uuid.uuid4().hex[:8]}"
    storage.bots[bot_id] = {"id": bot_id, "name": b.name, "strategy": b.strategy, "symbol": b.symbol, "status": "paused"}
    return {"success": True, "bot_id": bot_id}

@app.post("/api/bots/{bot_id}/start")
async def start_bot(bot_id: str):
    if bot_id not in storage.bots: raise HTTPException(404, "Bot not found")
    storage.bots[bot_id]["status"] = "active"
    return {"success": True, "status": "active"}

@app.post("/api/bots/{bot_id}/stop")
async def stop_bot(bot_id: str):
    if bot_id not in storage.bots: raise HTTPException(404, "Bot not found")
    storage.bots[bot_id]["status"] = "paused"
    return {"success": True, "status": "paused"}

@app.delete("/api/bots/{bot_id}")
async def delete_bot(bot_id: str):
    if bot_id in storage.bots: del storage.bots[bot_id]
    return {"success": True}

# ============ PEERS ============
peers_storage = {}

@app.get("/api/peers")
async def get_peers(): return [{"id": p["id"], "name": p["name"], "status": p["status"]} for p in peers_storage.values()]

@app.post("/api/peers")
async def add_peer(name: str, url: str):
    peer_id = f"PEER_{uuid.uuid4().hex[:8]}"
    peers_storage[peer_id] = {"id": peer_id, "name": name, "url": url, "status": "connected"}
    return {"success": True, "peer_id": peer_id}

@app.delete("/api/peers/{peer_id}")
async def remove_peer(peer_id: str):
    if peer_id in peers_storage: del peers_storage[peer_id]
    return {"success": True}

# ============ EXTERNAL API ============
@app.post("/api/external/register")
async def register_external(name: str, permissions: List[str]):
    api_key = f"TX_{uuid.uuid4().hex[:16]}"
    return {"success": True, "api_key": api_key, "permissions": permissions}

# ============ ADMIN ============
@app.get("/api/admin/stats")
async def admin_stats(): return {"exchange": EXCHANGE_NAME, "version": VERSION, "users": len(storage.users), "orders": len(storage.orders)}

# ============ TRADING PAIRS MANAGER ============
pair_manager = None

def get_pair_manager():
    global pair_manager
    if pair_manager is None:
        from pairs_manager import TradingPairManager
        pair_manager = TradingPairManager()
    return pair_manager

@app.get("/api/trading-pairs")
async def get_pairs(status: str = ""):
    m = get_pair_manager()
    return await m.get_pairs(status)

@app.get("/api/trading-pairs/{symbol}")
async def get_pair(symbol: str):
    m = get_pair_manager()
    return await m.get_pair(symbol)

# ============ TOKENS ============
@app.get("/api/tokens")
async def get_tokens():
    m = get_pair_manager()
    return await m.get_tokens()

@app.get("/api/tokens/{token_id}")
async def get_token(token_id: str):
    m = get_pair_manager()
    return await m.get_token(token_id)

# ============ BLOCKCHAINS ============
@app.get("/api/blockchains")
async def get_blockchains():
    m = get_pair_manager()
    return await m.get_blockchains()

@app.get("/api/blockchains/{chain_id}")
async def get_blockchain(chain_id: str):
    m = get_pair_manager()
    return await m.get_blockchain(chain_id)

@app.get("/api/blockchains/{chain_id}/deposits")
async def get_deposits(chain_id: str):
    m = get_pair_manager()
    return await m.get_blockchain_deposits(chain_id)

# ============ LIQUIDITY ============
@app.get("/api/liquidity/pools")
async def get_pools():
    m = get_pair_manager()
    return await m.get_pools()

@app.get("/api/liquidity/pools/{pair_id}")
async def get_pool(pair_id: str):
    m = get_pair_manager()
    return await m.get_pool(pair_id)

@app.post("/api/liquidity/add")
async def add_liquidity(pair_id: str, amount_a: float, amount_b: float):
    m = get_pair_manager()
    return await m.add_liquidity(pair_id, amount_a, amount_b)

@app.get("/api/liquidity/stats")
async def liquidity_stats():
    m = get_pair_manager()
    return await m.get_stats()

@app.get("/api/markets/data")
async def markets_data():
    m = get_pair_manager()
    return await m.get_markets_data()

# ============ MARKET MAKER ============
mm_engine = None

def get_mm_engine():
    global mm_engine
    if mm_engine is None:
        from market_maker import MarketMakerEngine
        mm_engine = MarketMakerEngine()
    return mm_engine

@app.on_event("startup")
async def startup_mm():
    global mm_engine
    m = get_mm_engine()
    await m.start()

@app.get("/api/market-maker/stats")
async def mm_stats():
    e = get_mm_engine()
    return await e.get_stats()

@app.get("/api/market-maker")
async def get_mms():
    e = get_mm_engine()
    return await e.get_all_market_makers()

@app.post("/api/market-maker")
async def create_mm(name: str, strategy: str = "all", symbols: List[str] = None):
    e = get_mm_engine()
    return await e.create_market_maker("USR_demo", name, strategy, symbols or [])

@app.get("/api/market-maker/{mm_id}")
async def get_mm(mm_id: str):
    e = get_mm_engine()
    return await e.get_market_maker(mm_id)

@app.post("/api/market-maker/{mm_id}/start")
async def start_mm(mm_id: str):
    e = get_mm_engine()
    return await e.start_market_maker(mm_id)

@app.post("/api/market-maker/{mm_id}/stop")
async def stop_mm(mm_id: str):
    e = get_mm_engine()
    return await e.stop_market_maker(mm_id)

@app.delete("/api/market-maker/{mm_id}")
async def delete_mm(mm_id: str):
    e = get_mm_engine()
    return await e.delete_market_maker(mm_id)

@app.get("/api/market-maker/orderbook/{symbol}")
async def mm_orderbook(symbol: str):
    e = get_mm_engine()
    return await e.get_orderbook(symbol)

# ============= MINING SERVICE =============
mining_service = None

def get_mining_service():
    global mining_service
    if mining_service is None:
        from mining_service import MiningService
        mining_service = MiningService()
    return mining_service

@app.get("/api/mining/stats")
async def mining_stats():
    m = get_mining_service()
    return await m.get_stats()

@app.get("/api/mining")
async def get_all_mining():
    m = get_mining_service()
    return await m.get_all_data()

# Stake Pools
@app.get("/api/mining/stake-pools")
async def get_stake_pools(status: str = ""):
    m = get_mining_service()
    return await m.get_stake_pools(status)

@app.get("/api/mining/stake-pools/{pool_id}")
async def get_stake_pool(pool_id: str):
    m = get_mining_service()
    return await m.get_stake_pool(pool_id)

@app.post("/api/mining/stake")
async def stake_tokens(pool_id: str, user_id: str, amount: float):
    m = get_mining_service()
    return await m.stake(pool_id, user_id, amount)

@app.post("/api/mining/unstake")
async def unstake_tokens(position_id: str):
    m = get_mining_service()
    return await m.unstake(position_id)

@app.get("/api/mining/stake-positions")
async def get_stake_positions(user_id: str = ""):
    m = get_mining_service()
    return await m.get_stake_positions(user_id)

# Yield Farms
@app.get("/api/mining/yield-farms")
async def get_yield_farms():
    m = get_mining_service()
    return await m.get_yield_farms()

@app.get("/api/mining/yield-farms/{farm_id}")
async def get_yield_farm(farm_id: str):
    m = get_mining_service()
    return await m.get_yield_farm(farm_id)

@app.post("/api/mining/yield-add")
async def add_yield_liquidity(farm_id: str, user_id: str, amount_a: float, amount_b: float):
    m = get_mining_service()
    return await m.add_yield_liquidity(farm_id, user_id, amount_a, amount_b)

# Validators
@app.get("/api/mining/validators")
async def get_validators(chain: str = ""):
    m = get_mining_service()
    return await m.get_validators(chain)

@app.get("/api/mining/validators/{validator_id}")
async def get_validator(validator_id: str):
    m = get_mining_service()
    return await m.get_validator(validator_id)

@app.post("/api/mining/delegate")
async def delegate_to_validator(validator_id: str, user_id: str, amount: float):
    m = get_mining_service()
    return await m.delegate_to_validator(validator_id, user_id, amount)

# Cloud Miners
@app.get("/api/mining/cloud-miners")
async def get_cloud_miners():
    m = get_mining_service()
    return await m.get_cloud_miners()

@app.get("/api/mining/cloud-miners/{miner_id}")
async def get_cloud_miner(miner_id: str):
    m = get_mining_service()
    return await m.get_cloud_miner(miner_id)

@app.post("/api/mining/cloud-purchase")
async def purchase_hashrate(miner_id: str, user_id: str, gh_s: float):
    m = get_mining_service()
    return await m.purchase_hashrate(miner_id, user_id, gh_s)

# ============ RUN ============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")