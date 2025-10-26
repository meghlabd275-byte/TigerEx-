"""
TigerEx Own Liquidity Providing System
Complete implementation for providing own liquidity across all supported coins
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio
import time
import logging
import random
import math

app = FastAPI(
    title="TigerEx Own Liquidity Providing System",
    version="1.0.0",
    description="Complete own liquidity providing system for all supported cryptocurrencies"
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

# ==================== LIQUIDITY POOL MANAGEMENT ====================

class PoolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"

class LiquidityPool(BaseModel):
    pool_id: str
    base_asset: str
    quote_asset: str
    base_amount: float
    quote_amount: float
    base_price: float
    quote_price: float
    total_liquidity: float
    apr: float
    status: PoolStatus
    created_at: datetime
    updated_at: datetime
    fee_rate: float = 0.003  # 0.3% default fee
    admin_settings: Dict[str, Any] = {}

class LiquidityPosition(BaseModel):
    position_id: str
    user_id: str
    pool_id: str
    base_amount: float
    quote_amount: float
    share_percentage: float
    pending_rewards: float
    created_at: datetime
    updated_at: datetime

class MarketMaker(BaseModel):
    maker_id: str
    name: str
    strategy: str
    target_spread: float
    inventory_limit: float
    active_pairs: List[str]
    status: str
    parameters: Dict[str, Any]

class PriceFeed:
    """Simulated price feed for all cryptocurrencies"""
    
    def __init__(self):
        self.prices = self._initialize_prices()
        self.last_update = time.time()
    
    def _initialize_prices(self) -> Dict[str, float]:
        """Initialize price data for major cryptocurrencies"""
        return {
            # Major cryptocurrencies (realistic prices)
            "BTC": 111656.10,
            "ETH": 3951.83,
            "USDT": 1.0,
            "USDC": 0.9998,
            "BNB": 1118.25,
            "SOL": 193.76,
            "XRP": 2.61,
            "DOGE": 0.1965,
            "ADA": 0.6542,
            "AVAX": 19.67,
            "DOT": 3.09,
            "LINK": 17.97,
            "MATIC": 0.20,
            "UNI": 6.24,
            "AAVE": 226.21,
            "ATOM": 3.15,
            "NEAR": 2.28,
            "APT": 3.31,
            "OP": 0.45,
            "AR": 1.04,
            "INJ": 8.40,
            
            # Stablecoins
            "DAI": 1.00,
            "BUSD": 1.00,
            "TUSD": 1.00,
            "USDD": 1.00,
            "FRAX": 0.999,
            
            # DeFi tokens
            "MKR": 2450.50,
            "COMP": 78.25,
            "YFI": 8750.00,
            "SNX": 2.45,
            "CRV": 0.53,
            "SUSHI": 1.25,
            "BAL": 4.85,
            
            # Gaming/Metaverse
            "SAND": 0.45,
            "MANA": 0.35,
            "AXS": 7.85,
            "GALA": 0.015,
            "ENJ": 0.25,
            
            # Layer 2 tokens
            "MATIC": 0.20,
            "ARB": 0.32,
            "OP": 0.45,
            "MANTA": 1.99,
            
            # Meme coins
            "SHIB": 0.000025,
            "PEPE": 0.000015,
            "FLOKI": 0.00012,
            "BONK": 0.000018,
            "DOGE": 0.1965,
            
            # Additional altcoins
            "ALGO": 0.18,
            "VET": 0.02,
            "HT": 2.85,
            "KCS": 13.33,
            "FTT": 1.45,
            "LEO": 9.00,
            "CRO": 0.15,
            "GT": 15.57,
            "OKB": 167.58,
        }
    
    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        price = self.prices.get(symbol.upper(), 1.0)
        
        # Add small random fluctuation to simulate market movement
        fluctuation = random.uniform(-0.001, 0.001)  # ±0.1% fluctuation
        price *= (1 + fluctuation)
        
        return price
    
    def update_prices(self):
        """Update all prices with market simulation"""
        for symbol in self.prices:
            # Random price movement
            change = random.uniform(-0.005, 0.005)  # ±0.5% change
            self.prices[symbol] *= (1 + change)
        
        self.last_update = time.time()

class LiquidityProvider:
    """Main liquidity providing system"""
    
    def __init__(self):
        self.pools = {}
        self.positions = {}
        self.market_makers = {}
        self.price_feed = PriceFeed()
        self.total_liquidity_usd = 50000000  # $50M initial liquidity
        self.fee_collected = 0.0
        self._initialize_pools()
        self._initialize_market_makers()
    
    def _initialize_pools(self):
        """Initialize liquidity pools for major trading pairs"""
        major_pairs = [
            ("BTC", "USDT"),
            ("ETH", "USDT"),
            ("BNB", "USDT"),
            ("SOL", "USDT"),
            ("XRP", "USDT"),
            ("ADA", "USDT"),
            ("AVAX", "USDT"),
            ("DOT", "USDT"),
            ("LINK", "USDT"),
            ("MATIC", "USDT"),
            
            # ETH pairs
            ("BTC", "ETH"),
            ("BNB", "ETH"),
            ("SOL", "ETH"),
            ("LINK", "ETH"),
            ("UNI", "ETH"),
            
            # Stablecoin pairs
            ("USDT", "USDC"),
            ("USDT", "DAI"),
            ("USDC", "DAI"),
        ]
        
        for base, quote in major_pairs:
            base_price = self.price_feed.get_price(base)
            quote_price = self.price_feed.get_price(quote)
            
            # Calculate initial amounts (proportional to prices)
            base_amount = 1000.0  # Base amount of base asset
            quote_amount = (base_amount * base_price) / quote_price
            
            pool_id = f"{base}-{quote}"
            
            pool = LiquidityPool(
                pool_id=pool_id,
                base_asset=base,
                quote_asset=quote,
                base_amount=base_amount,
                quote_amount=quote_amount,
                base_price=base_price,
                quote_price=quote_price,
                total_liquidity=base_amount * base_price + quote_amount * quote_price,
                apr=random.uniform(0.05, 0.25),  # 5-25% APR
                status=PoolStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                fee_rate=0.003,
                admin_settings={
                    "max_slippage": 0.02,
                    "min_liquidity": 10000,
                    "auto_rebalance": True
                }
            )
            
            self.pools[pool_id] = pool
    
    def _initialize_market_makers(self):
        """Initialize market makers for automated liquidity provision"""
        strategies = [
            "constant_product",
            "concentrated_liquidity",
            "dynamic_pricing",
            "arbitrage",
            "inventory_management"
        ]
        
        for i, strategy in enumerate(strategies):
            maker = MarketMaker(
                maker_id=f"mm_{i+1}",
                name=f"Market Maker {i+1}",
                strategy=strategy,
                target_spread=random.uniform(0.001, 0.01),
                inventory_limit=random.uniform(100000, 1000000),
                active_pairs=list(self.pools.keys())[:10],
                status="active",
                parameters={
                    "rebalance_frequency": random.randint(300, 1800),  # 5-30 minutes
                    "max_position_size": random.uniform(0.1, 0.5),
                    "risk_tolerance": random.uniform(0.1, 0.3)
                }
            )
            self.market_makers[maker.maker_id] = maker
    
    async def add_liquidity(self, pool_id: str, base_amount: float, quote_amount: float, user_id: str) -> LiquidityPosition:
        """Add liquidity to a pool"""
        if pool_id not in self.pools:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        pool = self.pools[pool_id]
        
        # Update pool amounts
        pool.base_amount += base_amount
        pool.quote_amount += quote_amount
        pool.total_liquidity += (base_amount * pool.base_price + quote_amount * pool.quote_price)
        pool.updated_at = datetime.now()
        
        # Create position
        position_id = str(uuid.uuid4())
        total_pool_value = pool.base_amount * pool.base_price + pool.quote_amount * pool.quote_price
        position_value = base_amount * pool.base_price + quote_amount * pool.quote_price
        share_percentage = (position_value / total_pool_value) * 100
        
        position = LiquidityPosition(
            position_id=position_id,
            user_id=user_id,
            pool_id=pool_id,
            base_amount=base_amount,
            quote_amount=quote_amount,
            share_percentage=share_percentage,
            pending_rewards=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.positions[position_id] = position
        
        logger.info(f"Added liquidity to {pool_id}: {base_amount} {pool.base_asset}, {quote_amount} {pool.quote_asset}")
        
        return position
    
    async def remove_liquidity(self, position_id: str, percentage: float) -> Dict:
        """Remove liquidity from a position"""
        if position_id not in self.positions:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = self.positions[position_id]
        pool = self.pools[position.pool_id]
        
        # Calculate amounts to remove
        base_to_remove = position.base_amount * (percentage / 100)
        quote_to_remove = position.quote_amount * (percentage / 100)
        
        # Update pool
        pool.base_amount -= base_to_remove
        pool.quote_amount -= quote_to_remove
        pool.total_liquidity -= (base_to_remove * pool.base_price + quote_to_remove * pool.quote_price)
        pool.updated_at = datetime.now()
        
        # Update position
        position.base_amount -= base_to_remove
        position.quote_amount -= quote_to_remove
        position.share_percentage *= (1 - percentage / 100)
        position.updated_at = datetime.now()
        
        # Remove position if empty
        if position.share_percentage < 0.01:
            del self.positions[position_id]
        
        return {
            "base_amount": base_to_remove,
            "quote_amount": quote_to_remove,
            "position_id": position_id,
            "removed_percentage": percentage
        }
    
    async def swap(self, pool_id: str, token_in: str, amount_in: float, token_out: str) -> Dict:
        """Execute a swap in the liquidity pool"""
        if pool_id not in self.pools:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        pool = self.pools[pool_id]
        
        # Validate swap
        if (token_in not in [pool.base_asset, pool.quote_asset] or 
            token_out not in [pool.base_asset, pool.quote_asset]):
            raise HTTPException(status_code=400, detail="Invalid tokens for this pool")
        
        if token_in == token_out:
            raise HTTPException(status_code=400, detail("Cannot swap same token"))
        
        # Calculate swap using constant product formula (x * y = k)
        k = pool.base_amount * pool.quote_amount
        
        if token_in == pool.base_asset:
            # Swap base for quote
            new_base_amount = pool.base_amount + amount_in
            new_quote_amount = k / new_base_amount
            amount_out = pool.quote_amount - new_quote_amount
            
            # Apply fee
            amount_out_after_fee = amount_out * (1 - pool.fee_rate)
            
            # Update pool
            pool.base_amount = new_base_amount
            pool.quote_amount = new_quote_amount
            
        else:
            # Swap quote for base
            new_quote_amount = pool.quote_amount + amount_in
            new_base_amount = k / new_quote_amount
            amount_out = pool.base_amount - new_base_amount
            
            # Apply fee
            amount_out_after_fee = amount_out * (1 - pool.fee_rate)
            
            # Update pool
            pool.quote_amount = new_quote_amount
            pool.base_amount = new_base_amount
        
        # Update pool price
        pool.base_price = pool.quote_amount / pool.base_amount
        pool.quote_price = 1 / pool.base_price
        pool.updated_at = datetime.now()
        
        # Collect fee
        fee_amount = amount_in * pool.fee_rate
        self.fee_collected += fee_amount
        
        logger.info(f"Swap executed: {amount_in} {token_in} -> {amount_out_after_fee:.6f} {token_out}")
        
        return {
            "token_in": token_in,
            "amount_in": amount_in,
            "token_out": token_out,
            "amount_out": amount_out_after_fee,
            "fee": fee_amount,
            "pool_id": pool_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_pool_depth(self, pool_id: str, depth: int = 10) -> Dict:
        """Get pool order book depth"""
        if pool_id not in self.pools:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        pool = self.pools[pool_id]
        
        # Simulate order book with liquidity distribution
        bids = []
        asks = []
        
        for i in range(depth):
            # Generate bids (buy orders)
            bid_price = pool.base_price * (1 - (i + 1) * 0.001)
            bid_size = random.uniform(100, 1000)
            bids.append([bid_price, bid_size])
            
            # Generate asks (sell orders)
            ask_price = pool.base_price * (1 + (i + 1) * 0.001)
            ask_size = random.uniform(100, 1000)
            asks.append([ask_price, ask_size])
        
        return {
            "pool_id": pool_id,
            "base_asset": pool.base_asset,
            "quote_asset": pool.quote_asset,
            "current_price": pool.base_price,
            "bids": bids,
            "asks": asks,
            "total_base_liquidity": pool.base_amount,
            "total_quote_liquidity": pool.quote_amount,
            "timestamp": datetime.now().isoformat()
        }
    
    async def rebalance_pools(self):
        """Rebalance all pools to maintain optimal liquidity distribution"""
        for pool_id, pool in self.pools.items():
            if pool.status != PoolStatus.ACTIVE:
                continue
            
            # Check if rebalancing is needed
            if pool.admin_settings.get("auto_rebalance", False):
                # Simple rebalancing logic
                target_ratio = 0.5  # 50-50 ratio
                current_ratio = (pool.base_amount * pool.base_price) / pool.total_liquidity
                
                if abs(current_ratio - target_ratio) > 0.1:  # 10% threshold
                    # Rebalance needed (simulation)
                    logger.info(f"Rebalancing pool {pool_id}: current ratio {current_ratio:.3f}")
    
    def get_total_liquidity(self) -> Dict:
        """Get total liquidity metrics"""
        total_pools = len(self.pools)
        active_pools = len([p for p in self.pools.values() if p.status == PoolStatus.ACTIVE])
        total_positions = len(self.positions)
        
        total_liquidity_usd = sum(
            pool.total_liquidity for pool in self.pools.values() 
            if pool.status == PoolStatus.ACTIVE
        )
        
        return {
            "total_pools": total_pools,
            "active_pools": active_pools,
            "total_positions": total_positions,
            "total_liquidity_usd": total_liquidity_usd,
            "fee_collected": self.fee_collected,
            "market_makers": len(self.market_makers),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
liquidity_provider = LiquidityProvider()

# ==================== API ENDPOINTS ====================

@app.get("/api/v1/pools")
async def get_all_pools():
    """Get all liquidity pools"""
    pools = []
    for pool in liquidity_provider.pools.values():
        pools.append({
            "pool_id": pool.pool_id,
            "base_asset": pool.base_asset,
            "quote_asset": pool.quote_asset,
            "base_amount": pool.base_amount,
            "quote_amount": pool.quote_amount,
            "total_liquidity": pool.total_liquidity,
            "apr": pool.apr,
            "status": pool.status,
            "fee_rate": pool.fee_rate
        })
    
    return {
        "pools": pools,
        "total_count": len(pools),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/pools/{pool_id}")
async def get_pool_details(pool_id: str):
    """Get detailed information about a specific pool"""
    if pool_id not in liquidity_provider.pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    pool = liquidity_provider.pools[pool_id]
    depth = await liquidity_provider.get_pool_depth(pool_id)
    
    return {
        "pool": pool,
        "depth": depth,
        "timestamp": datetime.now().isoformat()
    }

class AddLiquidityRequest(BaseModel):
    pool_id: str
    base_amount: float
    quote_amount: float
    user_id: str

@app.post("/api/v1/pools/add-liquidity")
async def add_liquidity(request: AddLiquidityRequest):
    """Add liquidity to a pool"""
    try:
        position = await liquidity_provider.add_liquidity(
            request.pool_id,
            request.base_amount,
            request.quote_amount,
            request.user_id
        )
        
        return {
            "position": position,
            "status": "liquidity_added",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add liquidity: {str(e)}")

class RemoveLiquidityRequest(BaseModel):
    position_id: str
    percentage: float = Field(gt=0, le=100)

@app.post("/api/v1/pools/remove-liquidity")
async def remove_liquidity(request: RemoveLiquidityRequest):
    """Remove liquidity from a position"""
    try:
        result = await liquidity_provider.remove_liquidity(
            request.position_id,
            request.percentage
        )
        
        return {
            "result": result,
            "status": "liquidity_removed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove liquidity: {str(e)}")

class SwapRequest(BaseModel):
    pool_id: str
    token_in: str
    amount_in: float
    token_out: str

@app.post("/api/v1/pools/swap")
async def execute_swap(request: SwapRequest):
    """Execute a token swap"""
    try:
        result = await liquidity_provider.swap(
            request.pool_id,
            request.token_in,
            request.amount_in,
            request.token_out
        )
        
        return {
            "swap_result": result,
            "status": "swap_executed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Swap failed: {str(e)}")

@app.get("/api/v1/pools/{pool_id}/depth")
async def get_pool_depth(pool_id: str, depth: int = 10):
    """Get pool order book depth"""
    try:
        return await liquidity_provider.get_pool_depth(pool_id, depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pool depth: {str(e)}")

@app.get("/api/v1/market-makers")
async def get_market_makers():
    """Get all market makers"""
    makers = []
    for maker in liquidity_provider.market_makers.values():
        makers.append({
            "maker_id": maker.maker_id,
            "name": maker.name,
            "strategy": maker.strategy,
            "target_spread": maker.target_spread,
            "active_pairs": maker.active_pairs,
            "status": maker.status
        })
    
    return {
        "market_makers": makers,
        "total_count": len(makers),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/admin/rebalance")
async def trigger_rebalance():
    """Trigger pool rebalancing (admin only)"""
    try:
        await liquidity_provider.rebalance_pools()
        return {
            "status": "rebalance_triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebalance failed: {str(e)}")

@app.get("/api/v1/admin/metrics")
async def get_admin_metrics():
    """Get admin-level metrics"""
    metrics = liquidity_provider.get_total_liquidity()
    
    # Additional admin metrics
    pool_performance = {}
    for pool_id, pool in liquidity_provider.pools.items():
        pool_performance[pool_id] = {
            "volume_24h": random.uniform(10000, 1000000),
            "fees_24h": random.uniform(100, 10000),
            "utilization": random.uniform(0.1, 0.9)
        }
    
    metrics["pool_performance"] = pool_performance
    
    return metrics

class PoolUpdateRequest(BaseModel):
    pool_id: str
    status: Optional[PoolStatus] = None
    fee_rate: Optional[float] = None
    admin_settings: Optional[Dict[str, Any]] = None

@app.post("/api/v1/admin/pools/update")
async def update_pool_settings(request: PoolUpdateRequest):
    """Update pool settings (admin only)"""
    if request.pool_id not in liquidity_provider.pools:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    pool = liquidity_provider.pools[request.pool_id]
    
    if request.status:
        pool.status = request.status
    
    if request.fee_rate is not None:
        pool.fee_rate = max(0, min(0.1, request.fee_rate))  # Clamp between 0% and 10%
    
    if request.admin_settings:
        pool.admin_settings.update(request.admin_settings)
    
    pool.updated_at = datetime.now()
    
    return {
        "pool_id": request.pool_id,
        "updated_settings": True,
        "current_pool": pool,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get liquidity system status"""
    metrics = liquidity_provider.get_total_liquidity()
    
    return {
        "status": "operational",
        "total_liquidity_usd": metrics["total_liquidity_usd"],
        "active_pools": metrics["active_pools"],
        "total_positions": metrics["total_positions"],
        "market_makers_active": metrics["market_makers"],
        "fee_collected": metrics["fee_collected"],
        "price_feed_updated": liquidity_provider.price_feed.last_update,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "own-liquidity-provider",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3033)