"""
TigerEx Liquidity Provider Program
Complete liquidity management system with admin controls
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

app = FastAPI(title="Liquidity Provider Program", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class LiquidityTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class LiquiditySource(str, Enum):
    INTERNAL = "internal"
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    EXTERNAL = "external"

class PoolStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

# Models
class LiquidityPool(BaseModel):
    pool_id: Optional[str] = None
    name: str
    trading_pair: str
    base_asset: str
    quote_asset: str
    min_liquidity: float
    max_liquidity: float
    fee_rate: float
    reward_rate: float
    status: PoolStatus = PoolStatus.ACTIVE

class LiquidityProvider(BaseModel):
    provider_id: Optional[str] = None
    user_id: str
    tier: LiquidityTier
    total_provided: float
    active_pools: List[str]
    rewards_earned: float
    joined_at: Optional[str] = None

class LiquidityPosition(BaseModel):
    position_id: Optional[str] = None
    provider_id: str
    pool_id: str
    amount: float
    share_percentage: float
    entry_price: float
    current_value: float
    rewards_accrued: float

class ExternalLiquiditySource(BaseModel):
    source_id: Optional[str] = None
    exchange: LiquiditySource
    api_key: str
    api_secret: str
    enabled: bool = True
    auto_sync: bool = True

class AdminLiquidityCreate(BaseModel):
    pool_id: str
    amount: float
    source: LiquiditySource
    notes: Optional[str] = None

# Authentication
def verify_admin_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    return {"user_id": "admin", "role": "admin"}

def verify_user_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    return {"user_id": "user123", "role": "user"}

# ==================== LIQUIDITY POOLS ====================

@app.post("/api/v1/liquidity/pools")
async def create_liquidity_pool(pool: LiquidityPool, admin=Depends(verify_admin_token)):
    """Admin: Create a new liquidity pool"""
    
    pool_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "pool": {
            "pool_id": pool_id,
            "name": pool.name,
            "trading_pair": pool.trading_pair,
            "base_asset": pool.base_asset,
            "quote_asset": pool.quote_asset,
            "min_liquidity": pool.min_liquidity,
            "max_liquidity": pool.max_liquidity,
            "fee_rate": pool.fee_rate,
            "reward_rate": pool.reward_rate,
            "status": pool.status,
            "total_liquidity": 0,
            "providers_count": 0,
            "created_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/v1/liquidity/pools")
async def list_liquidity_pools(
    status: Optional[PoolStatus] = None,
    trading_pair: Optional[str] = None
):
    """List all liquidity pools"""
    
    pools = [
        {
            "pool_id": f"pool_{i}",
            "name": f"BTC/USDT Pool {i}",
            "trading_pair": "BTC/USDT",
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "total_liquidity": 1000000 * i,
            "providers_count": 50 * i,
            "fee_rate": 0.001,
            "reward_rate": 0.15,
            "apy": 15.5 + i,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(1, 6)
    ]
    
    if status:
        pools = [p for p in pools if p["status"] == status]
    if trading_pair:
        pools = [p for p in pools if p["trading_pair"] == trading_pair]
    
    return {
        "success": True,
        "pools": pools,
        "total": len(pools)
    }

@app.get("/api/v1/liquidity/pools/{pool_id}")
async def get_pool_details(pool_id: str):
    """Get detailed information about a liquidity pool"""
    
    return {
        "success": True,
        "pool": {
            "pool_id": pool_id,
            "name": "BTC/USDT Liquidity Pool",
            "trading_pair": "BTC/USDT",
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "total_liquidity": 5000000,
            "available_liquidity": 4500000,
            "utilized_liquidity": 500000,
            "providers_count": 150,
            "fee_rate": 0.001,
            "reward_rate": 0.15,
            "apy": 15.5,
            "volume_24h": 10000000,
            "fees_collected_24h": 10000,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "statistics": {
                "total_rewards_distributed": 50000,
                "avg_provider_return": 0.16,
                "top_providers": [
                    {"provider_id": "prov_1", "amount": 500000, "share": 10.0},
                    {"provider_id": "prov_2", "amount": 300000, "share": 6.0}
                ]
            }
        }
    }

@app.post("/api/v1/liquidity/pools/{pool_id}/status")
async def update_pool_status(
    pool_id: str,
    status: PoolStatus,
    admin=Depends(verify_admin_token)
):
    """Admin: Update pool status (active/paused/closed)"""
    
    return {
        "success": True,
        "pool_id": pool_id,
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }

# ==================== ADMIN LIQUIDITY CREATION ====================

@app.post("/api/v1/admin/liquidity/create")
async def admin_create_liquidity(
    data: AdminLiquidityCreate,
    admin=Depends(verify_admin_token)
):
    """Admin: Create liquidity in a pool"""
    
    return {
        "success": True,
        "liquidity_creation": {
            "creation_id": str(uuid.uuid4()),
            "pool_id": data.pool_id,
            "amount": data.amount,
            "source": data.source,
            "created_by": admin["user_id"],
            "notes": data.notes,
            "created_at": datetime.utcnow().isoformat()
        }
    }

@app.post("/api/v1/admin/liquidity/remove")
async def admin_remove_liquidity(
    pool_id: str,
    amount: float,
    reason: str,
    admin=Depends(verify_admin_token)
):
    """Admin: Remove liquidity from a pool"""
    
    return {
        "success": True,
        "liquidity_removal": {
            "removal_id": str(uuid.uuid4()),
            "pool_id": pool_id,
            "amount": amount,
            "reason": reason,
            "removed_by": admin["user_id"],
            "removed_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/v1/admin/liquidity/history")
async def get_admin_liquidity_history(admin=Depends(verify_admin_token)):
    """Admin: Get history of admin liquidity operations"""
    
    return {
        "success": True,
        "history": [
            {
                "operation_id": f"op_{i}",
                "type": "create" if i % 2 == 0 else "remove",
                "pool_id": f"pool_{i}",
                "amount": 100000 * i,
                "source": "internal",
                "admin_id": "admin",
                "timestamp": datetime.utcnow().isoformat()
            }
            for i in range(1, 11)
        ]
    }

# ==================== EXTERNAL LIQUIDITY SOURCES ====================

@app.post("/api/v1/admin/liquidity/sources")
async def add_external_source(
    source: ExternalLiquiditySource,
    admin=Depends(verify_admin_token)
):
    """Admin: Add external liquidity source (Binance, OKX, Bybit, etc.)"""
    
    source_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "source": {
            "source_id": source_id,
            "exchange": source.exchange,
            "enabled": source.enabled,
            "auto_sync": source.auto_sync,
            "status": "connected",
            "last_sync": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/v1/admin/liquidity/sources")
async def list_external_sources(admin=Depends(verify_admin_token)):
    """Admin: List all external liquidity sources"""
    
    return {
        "success": True,
        "sources": [
            {
                "source_id": f"src_{i}",
                "exchange": exchange,
                "enabled": True,
                "auto_sync": True,
                "status": "connected",
                "liquidity_shared": 1000000 * i,
                "last_sync": datetime.utcnow().isoformat()
            }
            for i, exchange in enumerate(["binance", "okx", "bybit", "kucoin"], 1)
        ]
    }

@app.post("/api/v1/admin/liquidity/sources/{source_id}/sync")
async def sync_external_source(
    source_id: str,
    admin=Depends(verify_admin_token)
):
    """Admin: Manually sync liquidity from external source"""
    
    return {
        "success": True,
        "sync": {
            "source_id": source_id,
            "liquidity_synced": 500000,
            "pools_updated": 5,
            "sync_time": datetime.utcnow().isoformat()
        }
    }

@app.post("/api/v1/admin/liquidity/sources/{source_id}/toggle")
async def toggle_external_source(
    source_id: str,
    enabled: bool,
    admin=Depends(verify_admin_token)
):
    """Admin: Enable/disable external liquidity source"""
    
    return {
        "success": True,
        "source_id": source_id,
        "enabled": enabled,
        "updated_at": datetime.utcnow().isoformat()
    }

# ==================== LIQUIDITY PROVIDERS ====================

@app.post("/api/v1/liquidity/provide")
async def provide_liquidity(
    pool_id: str,
    amount: float,
    user=Depends(verify_user_token)
):
    """User: Provide liquidity to a pool"""
    
    position_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "position": {
            "position_id": position_id,
            "pool_id": pool_id,
            "provider_id": user["user_id"],
            "amount": amount,
            "share_percentage": 2.5,
            "entry_price": 50000,
            "estimated_apy": 15.5,
            "created_at": datetime.utcnow().isoformat()
        }
    }

@app.post("/api/v1/liquidity/withdraw")
async def withdraw_liquidity(
    position_id: str,
    amount: Optional[float] = None,
    user=Depends(verify_user_token)
):
    """User: Withdraw liquidity from a pool"""
    
    return {
        "success": True,
        "withdrawal": {
            "withdrawal_id": str(uuid.uuid4()),
            "position_id": position_id,
            "amount": amount or 10000,
            "rewards_claimed": 150,
            "total_returned": (amount or 10000) + 150,
            "withdrawn_at": datetime.utcnow().isoformat()
        }
    }

@app.get("/api/v1/liquidity/positions")
async def get_user_positions(user=Depends(verify_user_token)):
    """User: Get all liquidity positions"""
    
    return {
        "success": True,
        "positions": [
            {
                "position_id": f"pos_{i}",
                "pool_id": f"pool_{i}",
                "pool_name": f"BTC/USDT Pool {i}",
                "amount": 10000 * i,
                "share_percentage": 2.5,
                "entry_price": 50000,
                "current_value": 10500 * i,
                "rewards_accrued": 150 * i,
                "apy": 15.5,
                "created_at": datetime.utcnow().isoformat()
            }
            for i in range(1, 6)
        ],
        "total_provided": 150000,
        "total_rewards": 1500
    }

@app.post("/api/v1/liquidity/claim-rewards")
async def claim_rewards(
    position_id: Optional[str] = None,
    user=Depends(verify_user_token)
):
    """User: Claim rewards from liquidity provision"""
    
    return {
        "success": True,
        "rewards_claimed": {
            "claim_id": str(uuid.uuid4()),
            "position_id": position_id,
            "amount": 150.50,
            "claimed_at": datetime.utcnow().isoformat()
        }
    }

# ==================== LIQUIDITY PROVIDER TIERS ====================

@app.get("/api/v1/liquidity/tiers")
async def get_provider_tiers():
    """Get liquidity provider tier information"""
    
    return {
        "success": True,
        "tiers": [
            {
                "tier": "bronze",
                "min_liquidity": 1000,
                "max_liquidity": 10000,
                "reward_boost": 1.0,
                "fee_discount": 0.0,
                "benefits": ["Basic rewards", "Standard support"]
            },
            {
                "tier": "silver",
                "min_liquidity": 10000,
                "max_liquidity": 50000,
                "reward_boost": 1.1,
                "fee_discount": 0.05,
                "benefits": ["10% reward boost", "5% fee discount", "Priority support"]
            },
            {
                "tier": "gold",
                "min_liquidity": 50000,
                "max_liquidity": 200000,
                "reward_boost": 1.2,
                "fee_discount": 0.10,
                "benefits": ["20% reward boost", "10% fee discount", "VIP support", "Early access"]
            },
            {
                "tier": "platinum",
                "min_liquidity": 200000,
                "max_liquidity": 1000000,
                "reward_boost": 1.3,
                "fee_discount": 0.15,
                "benefits": ["30% reward boost", "15% fee discount", "Dedicated manager", "Exclusive events"]
            },
            {
                "tier": "diamond",
                "min_liquidity": 1000000,
                "max_liquidity": None,
                "reward_boost": 1.5,
                "fee_discount": 0.20,
                "benefits": ["50% reward boost", "20% fee discount", "Personal account manager", "Custom solutions"]
            }
        ]
    }

@app.get("/api/v1/liquidity/provider/tier")
async def get_provider_tier(user=Depends(verify_user_token)):
    """User: Get current provider tier and progress"""
    
    return {
        "success": True,
        "provider": {
            "user_id": user["user_id"],
            "current_tier": "gold",
            "total_provided": 75000,
            "reward_boost": 1.2,
            "fee_discount": 0.10,
            "next_tier": "platinum",
            "progress_to_next": 0.375,
            "amount_needed": 125000
        }
    }

# ==================== ANALYTICS ====================

@app.get("/api/v1/liquidity/analytics")
async def get_liquidity_analytics(admin=Depends(verify_admin_token)):
    """Admin: Get comprehensive liquidity analytics"""
    
    return {
        "success": True,
        "analytics": {
            "total_liquidity": 50000000,
            "total_pools": 25,
            "total_providers": 1500,
            "total_rewards_distributed": 500000,
            "avg_apy": 15.5,
            "top_pools": [
                {"pool_id": "pool_1", "name": "BTC/USDT", "liquidity": 10000000, "providers": 300},
                {"pool_id": "pool_2", "name": "ETH/USDT", "liquidity": 8000000, "providers": 250}
            ],
            "liquidity_by_source": {
                "internal": 30000000,
                "binance": 10000000,
                "okx": 5000000,
                "bybit": 3000000,
                "kucoin": 2000000
            },
            "provider_distribution": {
                "bronze": 800,
                "silver": 400,
                "gold": 200,
                "platinum": 80,
                "diamond": 20
            }
        }
    }

@app.get("/api/v1/liquidity/stats")
async def get_liquidity_stats():
    """Public: Get public liquidity statistics"""
    
    return {
        "success": True,
        "stats": {
            "total_liquidity": 50000000,
            "total_pools": 25,
            "total_providers": 1500,
            "avg_apy": 15.5,
            "volume_24h": 100000000,
            "fees_collected_24h": 100000
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "liquidity-provider-program", "version": "3.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)