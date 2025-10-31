"""
Advanced Liquidity System - Complete AMM and Liquidity Management
Automated Market Maker with multiple pool types and yield farming
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

app = FastAPI(title="Advanced Liquidity System", version="1.0.0")
security = HTTPBearer()

class PoolType(str, Enum):
    STANDARD = "standard"
    STABLE = "stable"
    WEIGHTED = "weighted"
    METAPOOL = "metapool"
    GAMIFIED = "gamified"
    CONCENTRATED = "concentrated"

class LiquidityPool(BaseModel):
    pool_id: str
    token_a: str
    token_b: str
    pool_type: PoolType
    total_liquidity: float
    token_a_reserve: float
    token_b_reserve: float
    apr: float
    fee_tier: float
    created_at: datetime

class LiquidityPosition(BaseModel):
    position_id: str
    user_address: str
    pool_id: str
    liquidity_amount: float
    token_a_amount: float
    token_b_amount: float
    rewards_earned: float
    created_at: datetime

class AddLiquidityRequest(BaseModel):
    pool_id: str
    user_address: str
    token_a_amount: float
    token_b_amount: float
    min_token_a: Optional[float] = None
    min_token_b: Optional[float] = None

class RemoveLiquidityRequest(BaseModel):
    pool_id: str
    user_address: str
    liquidity_amount: float
    min_token_a: Optional[float] = None
    min_token_b: Optional[float] = None

class SwapRequest(BaseModel):
    pool_id: str
    token_in: str
    token_out: str
    amount_in: float
    min_amount_out: float
    user_address: str

class FarmingReward(BaseModel):
    pool_id: str
    reward_token: str
    reward_rate: float
    total_rewards: float
    user_rewards: float
    lock_period: Optional[int] = None

class LiquidityEngine:
    def __init__(self):
        self.pools: Dict[str, LiquidityPool] = {}
        self.positions: Dict[str, LiquidityPosition] = {}
        self.farming_rewards: Dict[str, FarmingReward] = {}
        self.fee_rates = {
            PoolType.STANDARD: 0.003,  # 0.3%
            PoolType.STABLE: 0.0005,    # 0.05%
            PoolType.WEIGHTED: 0.002,   # 0.2%
            PoolType.METAPOOL: 0.001,   # 0.1%
            PoolType.GAMIFIED: 0.005,   # 0.5%
            PoolType.CONCENTRATED: 0.0001  # 0.01%
        }
    
    def calculate_k(self, token_a_reserve: float, token_b_reserve: float) -> float:
        """Calculate constant product k = x * y"""
        return token_a_reserve * token_b_reserve
    
    def calculate_output_amount(self, amount_in: float, reserve_in: float, reserve_out: float, fee: float) -> float:
        """Calculate output amount for swap using constant product formula"""
        amount_in_with_fee = amount_in * (1 - fee)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        return numerator / denominator
    
    def calculate_apr(self, pool_id: str) -> float:
        """Calculate APR for liquidity pool"""
        pool = self.pools.get(pool_id)
        if not pool:
            return 0.0
        
        # Simplified APR calculation
        daily_volume = pool.total_liquidity * 0.1  # Assume 10% daily volume
        daily_fees = daily_volume * pool.fee_tier
        yearly_fees = daily_fees * 365
        apr = (yearly_fees / pool.total_liquidity) * 100 if pool.total_liquidity > 0 else 0
        
        # Add farming rewards if available
        if pool_id in self.farming_rewards:
            reward = self.farming_rewards[pool_id]
            yearly_rewards = reward.reward_rate * 365
            apr += (yearly_rewards / pool.total_liquidity) * 100 if pool.total_liquidity > 0 else 0
        
        return apr
    
    def create_pool(self, token_a: str, token_b: str, pool_type: PoolType) -> str:
        """Create new liquidity pool"""
        pool_id = f"{token_a}_{token_b}_{pool_type.value}"
        
        if pool_id in self.pools:
            return pool_id
        
        pool = LiquidityPool(
            pool_id=pool_id,
            token_a=token_a,
            token_b=token_b,
            pool_type=pool_type,
            total_liquidity=0.0,
            token_a_reserve=0.0,
            token_b_reserve=0.0,
            apr=0.0,
            fee_tier=self.fee_rates[pool_type],
            created_at=datetime.utcnow()
        )
        
        self.pools[pool_id] = pool
        return pool_id

liquidity_engine = LiquidityEngine()

@app.get("/")
async def root():
    return {
        "service": "Advanced Liquidity System",
        "pool_types": [pool_type.value for pool_type in PoolType],
        "status": "operational"
    }

@app.post("/pools/create")
async def create_pool(token_a: str, token_b: str, pool_type: PoolType):
    """Create new liquidity pool"""
    try:
        pool_id = liquidity_engine.create_pool(token_a, token_b, pool_type)
        return {
            "pool_id": pool_id,
            "message": "Pool created successfully",
            "pool": liquidity_engine.pools[pool_id]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pools")
async def get_pools():
    """Get all liquidity pools"""
    return {"pools": list(liquidity_engine.pools.values())}

@app.get("/pools/{pool_id}")
async def get_pool(pool_id: str):
    """Get specific pool information"""
    pool = liquidity_engine.pools.get(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    # Update APR
    pool.apr = liquidity_engine.calculate_apr(pool_id)
    
    return {"pool": pool}

@app.post("/pools/{pool_id}/add-liquidity")
async def add_liquidity(pool_id: str, request: AddLiquidityRequest):
    """Add liquidity to pool"""
    try:
        pool = liquidity_engine.pools.get(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        # Calculate optimal token amounts based on current ratio
        if pool.token_a_reserve > 0 and pool.token_b_reserve > 0:
            # Maintain pool ratio
            optimal_token_b = (request.token_a_amount * pool.token_b_reserve) / pool.token_a_reserve
            if optimal_token_b < request.token_b_amount:
                # Adjust token_a amount
                request.token_a_amount = (request.token_b_amount * pool.token_a_reserve) / pool.token_b_reserve
            else:
                request.token_b_amount = optimal_token_b
        
        # Update pool reserves
        pool.token_a_reserve += request.token_a_amount
        pool.token_b_reserve += request.token_b_amount
        
        # Calculate liquidity tokens to mint (simplified)
        if pool.total_liquidity == 0:
            liquidity_tokens = (request.token_a_amount * request.token_b_amount) ** 0.5
        else:
            liquidity_tokens = min(
                (request.token_a_amount * pool.total_liquidity) / pool.token_a_reserve,
                (request.token_b_amount * pool.total_liquidity) / pool.token_b_reserve
            )
        
        pool.total_liquidity += liquidity_tokens
        
        # Create position
        position_id = f"{request.user_address}_{pool_id}_{int(datetime.utcnow().timestamp())}"
        position = LiquidityPosition(
            position_id=position_id,
            user_address=request.user_address,
            pool_id=pool_id,
            liquidity_amount=liquidity_tokens,
            token_a_amount=request.token_a_amount,
            token_b_amount=request.token_b_amount,
            rewards_earned=0.0,
            created_at=datetime.utcnow()
        )
        
        liquidity_engine.positions[position_id] = position
        
        return {
            "position_id": position_id,
            "liquidity_tokens": liquidity_tokens,
            "pool": pool,
            "message": "Liquidity added successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pools/{pool_id}/remove-liquidity")
async def remove_liquidity(pool_id: str, request: RemoveLiquidityRequest):
    """Remove liquidity from pool"""
    try:
        pool = liquidity_engine.pools.get(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        # Find user position
        user_positions = [
            pos for pos in liquidity_engine.positions.values()
            if pos.pool_id == pool_id and pos.user_address == request.user_address
        ]
        
        if not user_positions:
            raise HTTPException(status_code=404, detail="No liquidity position found")
        
        position = user_positions[0]  # Simplified - use first position
        
        if position.liquidity_amount < request.liquidity_amount:
            raise HTTPException(status_code=400, detail="Insufficient liquidity tokens")
        
        # Calculate token amounts to return
        token_a_out = (request.liquidity_amount * pool.token_a_reserve) / pool.total_liquidity
        token_b_out = (request.liquidity_amount * pool.token_b_reserve) / pool.total_liquidity
        
        # Check minimum amounts
        if request.min_token_a and token_a_out < request.min_token_a:
            raise HTTPException(status_code=400, detail="Token A output below minimum")
        if request.min_token_b and token_b_out < request.min_token_b:
            raise HTTPException(status_code=400, detail="Token B output below minimum")
        
        # Update pool
        pool.token_a_reserve -= token_a_out
        pool.token_b_reserve -= token_b_out
        pool.total_liquidity -= request.liquidity_amount
        
        # Update position
        position.liquidity_amount -= request.liquidity_amount
        
        return {
            "token_a_out": token_a_out,
            "token_b_out": token_b_out,
            "liquidity_tokens_removed": request.liquidity_amount,
            "remaining_liquidity": position.liquidity_amount,
            "message": "Liquidity removed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pools/{pool_id}/swap")
async def swap(pool_id: str, request: SwapRequest):
    """Execute token swap"""
    try:
        pool = liquidity_engine.pools.get(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        # Determine input/output reserves
        if request.token_in == pool.token_a:
            reserve_in = pool.token_a_reserve
            reserve_out = pool.token_b_reserve
        elif request.token_in == pool.token_b:
            reserve_in = pool.token_b_reserve
            reserve_out = pool.token_a_reserve
        else:
            raise HTTPException(status_code=400, detail="Invalid token for this pool")
        
        # Calculate output amount
        amount_out = liquidity_engine.calculate_output_amount(
            request.amount_in, reserve_in, reserve_out, pool.fee_tier
        )
        
        if amount_out < request.min_amount_out:
            raise HTTPException(status_code=400, detail="Insufficient output amount")
        
        # Update pool reserves
        if request.token_in == pool.token_a:
            pool.token_a_reserve += request.amount_in
            pool.token_b_reserve -= amount_out
        else:
            pool.token_b_reserve += request.amount_in
            pool.token_a_reserve -= amount_out
        
        return {
            "amount_in": request.amount_in,
            "amount_out": amount_out,
            "fee": request.amount_in * pool.fee_tier,
            "pool": pool,
            "message": "Swap executed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pools/{pool_id}/farming/setup")
async def setup_farming(pool_id: str, reward_token: str, reward_rate: float, lock_period: Optional[int] = None):
    """Setup farming rewards for pool"""
    try:
        pool = liquidity_engine.pools.get(pool_id)
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        farming = FarmingReward(
            pool_id=pool_id,
            reward_token=reward_token,
            reward_rate=reward_rate,
            total_rewards=0.0,
            user_rewards=0.0,
            lock_period=lock_period
        )
        
        liquidity_engine.farming_rewards[pool_id] = farming
        
        # Update pool APR
        pool.apr = liquidity_engine.calculate_apr(pool_id)
        
        return {
            "pool_id": pool_id,
            "reward_token": reward_token,
            "reward_rate": reward_rate,
            "lock_period": lock_period,
            "new_apr": pool.apr,
            "message": "Farming setup completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pools/{pool_id}/positions/{user_address}")
async def get_user_positions(pool_id: str, user_address: str):
    """Get user's liquidity positions in a pool"""
    positions = [
        pos for pos in liquidity_engine.positions.values()
        if pos.pool_id == pool_id and pos.user_address == user_address
    ]
    
    return {"positions": positions}

@app.get("/positions/{user_address}")
async def get_all_user_positions(user_address: str):
    """Get all user positions across all pools"""
    positions = [
        pos for pos in liquidity_engine.positions.values()
        if pos.user_address == user_address
    ]
    
    return {"positions": positions}

@app.get("/pools/{pool_id}/apr")
async def get_pool_apr(pool_id: str):
    """Get current APR for pool"""
    pool = liquidity_engine.pools.get(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    apr = liquidity_engine.calculate_apr(pool_id)
    return {"pool_id": pool_id, "apr": apr}

@app.get("/analytics/top-pools")
async def get_top_pools(limit: int = 10):
    """Get top pools by liquidity"""
    pools = sorted(
        liquidity_engine.pools.values(),
        key=lambda x: x.total_liquidity,
        reverse=True
    )[:limit]
    
    # Update APRs
    for pool in pools:
        pool.apr = liquidity_engine.calculate_apr(pool.pool_id)
    
    return {"top_pools": pools}

@app.get("/analytics/apr-stats")
async def get_apr_statistics():
    """Get APR statistics across all pools"""
    if not liquidity_engine.pools:
        return {"message": "No pools available"}
    
    aprs = []
    for pool in liquidity_engine.pools.values():
        apr = liquidity_engine.calculate_apr(pool.pool_id)
        aprs.append(apr)
    
    return {
        "total_pools": len(aprs),
        "average_apr": sum(aprs) / len(aprs),
        "highest_apr": max(aprs),
        "lowest_apr": min(aprs),
        "median_apr": sorted(aprs)[len(aprs) // 2]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)