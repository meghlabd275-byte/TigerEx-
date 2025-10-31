"""
Complete Own Liquidity Providing System
Automated Market Makers, Yield Generation, Dynamic Pricing, Multi-Asset Support
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
import math

app = FastAPI(title="Complete Own Liquidity System", version="1.0.0")
security = HTTPBearer()

class PoolType(str, Enum):
    STANDARD = "standard"
    WEIGHTED = "weighted"
    STABLE = "stable"
    METAPOOL = "metapool"
    GAMIFIED = "gamified"
    CONCENTRATED = "concentrated"

class MarketMakingStrategy(str, Enum):
    STATIC_SPREAD = "static_spread"
    DYNAMIC_SPREAD = "dynamic_spread"
    INVENTORY_BALANCE = "inventory_balance"
    PING_PONG = "ping_pong"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"

class LiquidityPool(BaseModel):
    pool_id: str
    token_a: str
    token_b: str
    pool_type: PoolType
    total_liquidity: float
    reserve_a: float
    reserve_b: float
    apr: float
    fee_tier: float
    created_at: datetime
    last_updated: datetime
    is_active: bool

class LiquidityPosition(BaseModel):
    position_id: str
    user_id: str
    pool_id: str
    liquidity_amount: float
    token_a_amount: float
    token_b_amount: float
    rewards_earned: float
    created_at: datetime
    last_updated: datetime

class MarketMaker(BaseModel):
    mm_id: str
    pool_id: str
    strategy: MarketMakingStrategy
    base_spread: float
    min_order_size: float
    max_order_size: float
    inventory_target: float
    is_active: bool
    parameters: Dict[str, Any]

class YieldFarm(BaseModel):
    farm_id: str
    pool_id: str
    reward_token: str
    reward_rate: float
    total_rewards: float
    lock_period: int
    multiplier: float
    created_at: datetime

class RebalanceRequest(BaseModel):
    pool_id: str
    target_ratio_a: float
    target_ratio_b: float
    max_slippage: float

class CompleteLiquiditySystem:
    def __init__(self):
        self.pools: Dict[str, LiquidityPool] = {}
        self.positions: Dict[str, LiquidityPosition] = {}
        self.market_makers: Dict[str, MarketMaker] = {}
        self.yield_farms: Dict[str, YieldFarm] = {}
        self.price_feeds: Dict[str, float] = {}
        self.volatility_feeds: Dict[str, float] = {}
        
        self.fee_tiers = {
            PoolType.STANDARD: 0.003,      # 0.3%
            PoolType.WEIGHTED: 0.002,      # 0.2%
            PoolType.STABLE: 0.0005,       # 0.05%
            PoolType.METAPOOL: 0.001,      # 0.1%
            PoolType.GAMIFIED: 0.005,      # 0.5%
            PoolType.CONCENTRATED: 0.0001  # 0.01%
        }
        
        self.initialize_default_pools()
        self.start_background_tasks()
    
    def initialize_default_pools(self):
        """Initialize default liquidity pools"""
        default_pools = [
            ("BTC", "USDT", PoolType.STANDARD),
            ("ETH", "USDT", PoolType.STANDARD),
            ("ETH", "BTC", PoolType.WEIGHTED),
            ("USDC", "USDT", PoolType.STABLE),
            ("BNB", "USDT", PoolType.CONCENTRATED),
            ("ADA", "USDT", PoolType.STANDARD),
            ("SOL", "USDT", PoolType.STANDARD),
            ("MATIC", "USDT", PoolType.CONCENTRATED),
        ]
        
        for token_a, token_b, pool_type in default_pools:
            self.create_pool(token_a, token_b, pool_type)
    
    def create_pool(self, token_a: str, token_b: str, pool_type: PoolType) -> str:
        """Create new liquidity pool"""
        pool_id = f"{token_a}_{token_b}_{pool_type.value}"
        
        if pool_id in self.pools:
            return pool_id
        
        # Get initial prices (mock data)
        price_a = self.get_token_price(token_a)
        price_b = self.get_token_price(token_b)
        
        # Calculate initial reserves (10,000 USD worth)
        initial_value = 10000.0
        initial_reserve_a = initial_value / price_a
        initial_reserve_b = initial_value / price_b
        
        pool = LiquidityPool(
            pool_id=pool_id,
            token_a=token_a,
            token_b=token_b,
            pool_type=pool_type,
            total_liquidity=0.0,
            reserve_a=initial_reserve_a,
            reserve_b=initial_reserve_b,
            apr=0.0,
            fee_tier=self.fee_tiers[pool_type],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            is_active=True
        )
        
        self.pools[pool_id] = pool
        
        # Create yield farm for the pool
        self.create_yield_farm(pool_id)
        
        return pool_id
    
    def create_yield_farm(self, pool_id: str):
        """Create yield farm for pool"""
        farm_id = f"farm_{pool_id}"
        
        # Calculate reward rate based on pool type and APR
        pool = self.pools[pool_id]
        base_apr = {
            PoolType.STANDARD: 0.10,      # 10%
            PoolType.WEIGHTED: 0.08,      # 8%
            PoolType.STABLE: 0.05,        # 5%
            PoolType.METAPOOL: 0.12,      # 12%
            PoolType.GAMIFIED: 0.15,      # 15%
            PoolType.CONCENTRATED: 0.20   # 20%
        }
        
        pool.apr = base_apr[pool.pool_type]
        
        farm = YieldFarm(
            farm_id=farm_id,
            pool_id=pool_id,
            reward_token=pool.token_a,  # Reward in token_a
            reward_rate=pool.total_liquidity * pool.apr / 365 / 24 / 3600,  # per second
            total_rewards=0.0,
            lock_period=0,  # No lock period by default
            multiplier=1.0,
            created_at=datetime.utcnow()
        )
        
        self.yield_farms[farm_id] = farm
    
    def get_token_price(self, token: str) -> float:
        """Get token price (mock data)"""
        mock_prices = {
            "BTC": 45000.0,
            "ETH": 3000.0,
            "USDT": 1.0,
            "USDC": 1.0,
            "BNB": 300.0,
            "ADA": 1.5,
            "SOL": 120.0,
            "MATIC": 1.8,
            "DOT": 25.0,
            "AVAX": 35.0
        }
        
        return mock_prices.get(token, 1.0)
    
    def calculate_k(self, reserve_a: float, reserve_b: float) -> float:
        """Calculate constant product k = x * y"""
        return reserve_a * reserve_b
    
    def calculate_output_amount(self, amount_in: float, reserve_in: float, reserve_out: float, fee: float) -> float:
        """Calculate output amount using constant product formula"""
        amount_in_with_fee = amount_in * (1 - fee)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        return numerator / denominator
    
    def add_liquidity(self, pool_id: str, amount_a: float, amount_b: float, user_id: str) -> str:
        """Add liquidity to pool"""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError("Pool not found")
        
        # Maintain pool ratio
        if pool.reserve_a > 0 and pool.reserve_b > 0:
            optimal_b = (amount_a * pool.reserve_b) / pool.reserve_a
            if optimal_b > amount_b:
                # Adjust amount_a
                amount_a = (amount_b * pool.reserve_a) / pool.reserve_b
            else:
                # Use amount_b
                amount_b = optimal_b
        
        # Update pool reserves
        pool.reserve_a += amount_a
        pool.reserve_b += amount_b
        pool.total_liquidity += math.sqrt(pool.reserve_a * pool.reserve_b)
        pool.last_updated = datetime.utcnow()
        
        # Create position
        position_id = f"pos_{user_id}_{pool_id}_{int(datetime.utcnow().timestamp())}"
        position = LiquidityPosition(
            position_id=position_id,
            user_id=user_id,
            pool_id=pool_id,
            liquidity_amount=math.sqrt(pool.reserve_a * pool.reserve_b),
            token_a_amount=amount_a,
            token_b_amount=amount_b,
            rewards_earned=0.0,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        self.positions[position_id] = position
        
        # Update yield farm
        self.update_yield_farm(pool_id)
        
        return position_id
    
    def remove_liquidity(self, position_id: str, liquidity_amount: float) -> Dict[str, float]:
        """Remove liquidity from position"""
        position = self.positions.get(position_id)
        if not position:
            raise ValueError("Position not found")
        
        if liquidity_amount > position.liquidity_amount:
            raise ValueError("Insufficient liquidity")
        
        pool = self.pools[position.pool_id]
        
        # Calculate token amounts to return
        ratio = liquidity_amount / position.liquidity_amount
        token_a_out = position.token_a_amount * ratio
        token_b_out = position.token_b_amount * ratio
        
        # Update pool
        pool.reserve_a -= token_a_out
        pool.reserve_b -= token_b_out
        pool.total_liquidity -= liquidity_amount
        pool.last_updated = datetime.utcnow()
        
        # Update position
        position.liquidity_amount -= liquidity_amount
        position.token_a_amount -= token_a_out
        position.token_b_amount -= token_b_out
        position.last_updated = datetime.utcnow()
        
        # Update yield farm
        self.update_yield_farm(position.pool_id)
        
        return {
            "token_a": token_a_out,
            "token_b": token_b_out,
            "liquidity_removed": liquidity_amount
        }
    
    def swap(self, pool_id: str, token_in: str, amount_in: float) -> float:
        """Execute swap in pool"""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError("Pool not found")
        
        if token_in not in [pool.token_a, pool.token_b]:
            raise ValueError("Invalid token for pool")
        
        # Determine input/output reserves
        if token_in == pool.token_a:
            reserve_in = pool.reserve_a
            reserve_out = pool.reserve_b
        else:
            reserve_in = pool.reserve_b
            reserve_out = pool.reserve_a
        
        # Calculate output
        amount_out = self.calculate_output_amount(amount_in, reserve_in, reserve_out, pool.fee_tier)
        
        # Update pool reserves
        if token_in == pool.token_a:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
        else:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out
        
        pool.last_updated = datetime.utcnow()
        
        return amount_out
    
    def create_market_maker(self, pool_id: str, strategy: MarketMakingStrategy, parameters: Dict[str, Any]) -> str:
        """Create market maker for pool"""
        mm_id = f"mm_{pool_id}_{strategy.value}_{int(datetime.utcnow().timestamp())}"
        
        market_maker = MarketMaker(
            mm_id=mm_id,
            pool_id=pool_id,
            strategy=strategy,
            base_spread=0.001,  # 0.1%
            min_order_size=0.01,
            max_order_size=10.0,
            inventory_target=0.5,  # 50% in each token
            is_active=True,
            parameters=parameters
        )
        
        self.market_makers[mm_id] = market_maker
        return mm_id
    
    def update_yield_farm(self, pool_id: str):
        """Update yield farm rates"""
        farm = None
        for f in self.yield_farms.values():
            if f.pool_id == pool_id:
                farm = f
                break
        
        if not farm:
            return
        
        pool = self.pools[pool_id]
        farm.reward_rate = pool.total_liquidity * pool.apr / 365 / 24 / 3600
    
    def rebalance_pool(self, pool_id: str, target_ratio_a: float, target_ratio_b: float, max_slippage: float) -> bool:
        """Rebalance pool to target ratios"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False
        
        total_value = pool.reserve_a * self.get_token_price(pool.token_a) + pool.reserve_b * self.get_token_price(pool.token_b)
        target_value_a = total_value * target_ratio_a
        target_value_b = total_value * target_ratio_b
        
        current_value_a = pool.reserve_a * self.get_token_price(pool.token_a)
        current_value_b = pool.reserve_b * self.get_token_price(pool.token_b)
        
        # Calculate required trades
        if current_value_a > target_value_a:
            # Sell token_a for token_b
            sell_amount = (current_value_a - target_value_a) / self.get_token_price(pool.token_a)
            
            # Check slippage
            estimated_out = self.calculate_output_amount(sell_amount, pool.reserve_a, pool.reserve_b, pool.fee_tier)
            slippage = abs(estimated_out - target_value_b / self.get_token_price(pool.token_b)) / estimated_out
            
            if slippage <= max_slippage:
                self.swap(pool_id, pool.token_a, sell_amount)
                return True
        else:
            # Buy token_a with token_b
            buy_value = target_value_a - current_value_a
            buy_amount = buy_value / self.get_token_price(pool.token_a)
            
            # Check slippage
            estimated_in = self.calculate_output_amount_inverse(buy_amount, pool.reserve_b, pool.reserve_a, pool.fee_tier)
            slippage = abs(estimated_in - current_value_b / self.get_token_price(pool.token_b)) / estimated_in
            
            if slippage <= max_slippage:
                self.swap(pool_id, pool.token_b, estimated_in)
                return True
        
        return False
    
    def calculate_output_amount_inverse(self, amount_out: float, reserve_in: float, reserve_out: float, fee: float) -> float:
        """Calculate required input amount for desired output"""
        numerator = reserve_in * amount_out
        denominator = (reserve_out - amount_out) * (1 - fee)
        return numerator / denominator
    
    def start_background_tasks(self):
        """Start background tasks for market making and yield distribution"""
        asyncio.create_task(self.market_making_loop())
        asyncio.create_task(self.yield_distribution_loop())
        asyncio.create_task(self.price_update_loop())
    
    async def market_making_loop(self):
        """Background task for market making"""
        while True:
            try:
                for mm in self.market_makers.values():
                    if mm.is_active:
                        self.execute_market_making_strategy(mm)
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                print(f"Market making error: {e}")
                await asyncio.sleep(5)
    
    async def yield_distribution_loop(self):
        """Background task for yield distribution"""
        while True:
            try:
                for farm in self.yield_farms.values():
                    self.distribute_yield(farm)
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                print(f"Yield distribution error: {e}")
                await asyncio.sleep(300)
    
    async def price_update_loop(self):
        """Background task for price updates"""
        while True:
            try:
                self.update_price_feeds()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Price update error: {e}")
                await asyncio.sleep(60)
    
    def execute_market_making_strategy(self, mm: MarketMaker):
        """Execute market making strategy"""
        pool = self.pools.get(mm.pool_id)
        if not pool:
            return
        
        current_price = self.get_token_price(pool.token_a) / self.get_token_price(pool.token_b)
        volatility = self.volatility_feeds.get(mm.pool_id, 0.01)
        
        if mm.strategy == MarketMakingStrategy.DYNAMIC_SPREAD:
            # Adjust spread based on volatility
            spread = mm.base_spread * (1 + volatility * 10)
            
            # Place orders around current price
            bid_price = current_price * (1 - spread)
            ask_price = current_price * (1 + spread)
            
            # Update order book (mock implementation)
            pass
        
        elif mm.strategy == MarketMakingStrategy.INVENTORY_BALANCE:
            # Balance inventory based on current holdings
            inventory_ratio = pool.reserve_a * self.get_token_price(pool.token_a) / (
                pool.reserve_a * self.get_token_price(pool.token_a) + pool.reserve_b * self.get_token_price(pool.token_b)
            )
            
            # Adjust spread to rebalance
            if inventory_ratio > mm.inventory_target:
                # Too much of token_a, lower bid
                pass
            else:
                # Too little of token_a, raise ask
                pass
    
    def distribute_yield(self, farm: YieldFarm):
        """Distribute yield to liquidity providers"""
        pool = self.pools[farm.pool_id]
        
        # Calculate rewards for this period
        time_delta = 60  # 1 minute
        rewards_to_distribute = farm.reward_rate * time_delta
        
        # Distribute to positions proportional to liquidity
        total_liquidity = sum(pos.liquidity_amount for pos in self.positions.values() if pos.pool_id == farm.pool_id)
        
        if total_liquidity > 0:
            for position in self.positions.values():
                if position.pool_id == farm.pool_id:
                    position.rewards_earned += rewards_to_distribute * (position.liquidity_amount / total_liquidity)
                    position.last_updated = datetime.utcnow()
    
    def update_price_feeds(self):
        """Update price and volatility feeds"""
        # Mock price updates with small random changes
        for pool in self.pools.values():
            price_a = self.get_token_price(pool.token_a)
            price_b = self.get_token_price(pool.token_b)
            
            # Add small random movement
            import random
            price_a *= (1 + random.uniform(-0.001, 0.001))
            price_b *= (1 + random.uniform(-0.001, 0.001))
            
            self.price_feeds[f"{pool.token_a}_{pool.token_b}"] = price_a / price_b
            self.volatility_feeds[pool.pool_id] = random.uniform(0.005, 0.02)  # 0.5% - 2% volatility

liquidity_system = CompleteLiquiditySystem()

@app.get("/")
async def root():
    return {
        "service": "Complete Own Liquidity System",
        "pool_types": [pool_type.value for pool_type in PoolType],
        "strategies": [strategy.value for strategy in MarketMakingStrategy],
        "status": "operational"
    }

@app.get("/pools")
async def get_pools():
    """Get all liquidity pools"""
    return {"pools": list(liquidity_system.pools.values())}

@app.post("/pools/create")
async def create_pool(token_a: str, token_b: str, pool_type: PoolType):
    """Create new liquidity pool"""
    try:
        pool_id = liquidity_system.create_pool(token_a, token_b, pool_type)
        return {"pool_id": pool_id, "message": "Pool created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pools/{pool_id}")
async def get_pool(pool_id: str):
    """Get specific pool information"""
    pool = liquidity_system.pools.get(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return {"pool": pool}

@app.post("/pools/{pool_id}/add-liquidity")
async def add_liquidity(pool_id: str, amount_a: float, amount_b: float, user_id: str):
    """Add liquidity to pool"""
    try:
        position_id = liquidity_system.add_liquidity(pool_id, amount_a, amount_b, user_id)
        return {"position_id": position_id, "message": "Liquidity added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/positions/{position_id}/remove-liquidity")
async def remove_liquidity(position_id: str, liquidity_amount: float):
    """Remove liquidity from position"""
    try:
        result = liquidity_system.remove_liquidity(position_id, liquidity_amount)
        return {"result": result, "message": "Liquidity removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pools/{pool_id}/swap")
async def swap(pool_id: str, token_in: str, amount_in: float):
    """Execute swap in pool"""
    try:
        amount_out = liquidity_system.swap(pool_id, token_in, amount_in)
        return {"amount_out": amount_out, "message": "Swap executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/market-makers/create")
async def create_market_maker(pool_id: str, strategy: MarketMakingStrategy, parameters: Dict[str, Any]):
    """Create market maker"""
    try:
        mm_id = liquidity_system.create_market_maker(pool_id, strategy, parameters)
        return {"mm_id": mm_id, "message": "Market maker created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-makers")
async def get_market_makers():
    """Get all market makers"""
    return {"market_makers": list(liquidity_system.market_makers.values())}

@app.post("/pools/{pool_id}/rebalance")
async def rebalance_pool(pool_id: str, request: RebalanceRequest):
    """Rebalance pool"""
    try:
        success = liquidity_system.rebalance_pool(
            pool_id, 
            request.target_ratio_a, 
            request.target_ratio_b, 
            request.max_slippage
        )
        return {"success": success, "message": "Rebalance completed" if success else "Rebalance failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yield-farms")
async def get_yield_farms():
    """Get all yield farms"""
    return {"yield_farms": list(liquidity_system.yield_farms.values())}

@app.get("/positions/{user_id}")
async def get_user_positions(user_id: str):
    """Get user positions"""
    user_positions = [
        pos for pos in liquidity_system.positions.values()
        if pos.user_id == user_id
    ]
    return {"positions": user_positions}

@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get system analytics overview"""
    total_liquidity = sum(pool.total_liquidity for pool in liquidity_system.pools.values())
    total_volume = 0  # Would track actual volume
    total_positions = len(liquidity_system.positions)
    active_pools = len([p for p in liquidity_system.pools.values() if p.is_active])
    
    return {
        "total_liquidity": total_liquidity,
        "total_volume": total_volume,
        "total_positions": total_positions,
        "active_pools": active_pools,
        "total_pools": len(liquidity_system.pools),
        "active_market_makers": len([mm for mm in liquidity_system.market_makers.values() if mm.is_active])
    }

@app.get("/analytics/{pool_id}")
async def get_pool_analytics(pool_id: str):
    """Get detailed analytics for pool"""
    pool = liquidity_system.pools.get(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    # Calculate pool statistics
    positions_in_pool = [pos for pos in liquidity_system.positions.values() if pos.pool_id == pool_id]
    
    return {
        "pool_id": pool_id,
        "total_liquidity": pool.total_liquidity,
        "reserve_a": pool.reserve_a,
        "reserve_b": pool.reserve_b,
        "apr": pool.apr,
        "fee_tier": pool.fee_tier,
        "number_of_positions": len(positions_in_pool),
        "total_rewards_earned": sum(pos.rewards_earned for pos in positions_in_pool),
        "utilization": (pool.reserve_a + pool.reserve_b) / (pool.total_liquidity * 2) if pool.total_liquidity > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)