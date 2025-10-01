"""
TigerEx VIP Program Service
Manages VIP tiers, benefits, and rewards for users
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import os

app = FastAPI(
    title="TigerEx VIP Program Service",
    description="VIP tier management and benefits system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VIP Tier Enum
class VIPTier(str, Enum):
    REGULAR = "regular"
    VIP1 = "vip1"
    VIP2 = "vip2"
    VIP3 = "vip3"
    VIP4 = "vip4"
    VIP5 = "vip5"
    VIP6 = "vip6"
    VIP7 = "vip7"
    VIP8 = "vip8"
    VIP9 = "vip9"

# VIP Tier Configuration
VIP_TIERS = {
    VIPTier.REGULAR: {
        "name": "Regular",
        "trading_volume_30d": 0,
        "tiger_balance": 0,
        "maker_fee": 0.10,
        "taker_fee": 0.10,
        "withdrawal_fee_discount": 0,
        "benefits": [
            "Basic trading features",
            "Standard customer support"
        ]
    },
    VIPTier.VIP1: {
        "name": "VIP 1",
        "trading_volume_30d": 50000,
        "tiger_balance": 1000,
        "maker_fee": 0.09,
        "taker_fee": 0.09,
        "withdrawal_fee_discount": 5,
        "benefits": [
            "5% withdrawal fee discount",
            "Priority customer support",
            "Access to VIP trading signals"
        ]
    },
    VIPTier.VIP2: {
        "name": "VIP 2",
        "trading_volume_30d": 200000,
        "tiger_balance": 5000,
        "maker_fee": 0.08,
        "taker_fee": 0.08,
        "withdrawal_fee_discount": 10,
        "benefits": [
            "10% withdrawal fee discount",
            "Dedicated account manager",
            "Advanced trading tools",
            "Monthly market reports"
        ]
    },
    VIPTier.VIP3: {
        "name": "VIP 3",
        "trading_volume_30d": 500000,
        "tiger_balance": 10000,
        "maker_fee": 0.07,
        "taker_fee": 0.07,
        "withdrawal_fee_discount": 15,
        "benefits": [
            "15% withdrawal fee discount",
            "24/7 priority support",
            "Exclusive trading competitions",
            "API rate limit increase",
            "Early access to new features"
        ]
    },
    VIPTier.VIP4: {
        "name": "VIP 4",
        "trading_volume_30d": 1000000,
        "tiger_balance": 25000,
        "maker_fee": 0.06,
        "taker_fee": 0.06,
        "withdrawal_fee_discount": 20,
        "benefits": [
            "20% withdrawal fee discount",
            "Dedicated VIP support team",
            "Exclusive airdrops",
            "Higher API limits",
            "VIP lounge access",
            "Quarterly portfolio review"
        ]
    },
    VIPTier.VIP5: {
        "name": "VIP 5",
        "trading_volume_30d": 5000000,
        "tiger_balance": 50000,
        "maker_fee": 0.05,
        "taker_fee": 0.05,
        "withdrawal_fee_discount": 25,
        "benefits": [
            "25% withdrawal fee discount",
            "Personal relationship manager",
            "Exclusive events invitation",
            "Premium research reports",
            "OTC trading desk access",
            "Custom trading solutions"
        ]
    },
    VIPTier.VIP6: {
        "name": "VIP 6",
        "trading_volume_30d": 10000000,
        "tiger_balance": 100000,
        "maker_fee": 0.04,
        "taker_fee": 0.04,
        "withdrawal_fee_discount": 30,
        "benefits": [
            "30% withdrawal fee discount",
            "Institutional-grade services",
            "Customized trading strategies",
            "Direct market maker access",
            "Exclusive partnership opportunities",
            "Annual VIP summit invitation"
        ]
    },
    VIPTier.VIP7: {
        "name": "VIP 7",
        "trading_volume_30d": 25000000,
        "tiger_balance": 250000,
        "maker_fee": 0.03,
        "taker_fee": 0.03,
        "withdrawal_fee_discount": 40,
        "benefits": [
            "40% withdrawal fee discount",
            "White-glove service",
            "Dedicated trading infrastructure",
            "Custom API solutions",
            "Exclusive token sale access",
            "Board advisory opportunities"
        ]
    },
    VIPTier.VIP8: {
        "name": "VIP 8",
        "trading_volume_30d": 50000000,
        "tiger_balance": 500000,
        "maker_fee": 0.02,
        "taker_fee": 0.02,
        "withdrawal_fee_discount": 50,
        "benefits": [
            "50% withdrawal fee discount",
            "Institutional prime services",
            "Dedicated infrastructure",
            "Custom liquidity solutions",
            "Strategic partnership opportunities",
            "Revenue sharing programs"
        ]
    },
    VIPTier.VIP9: {
        "name": "VIP 9",
        "trading_volume_30d": 100000000,
        "tiger_balance": 1000000,
        "maker_fee": 0.01,
        "taker_fee": 0.01,
        "withdrawal_fee_discount": 75,
        "benefits": [
            "75% withdrawal fee discount",
            "Ultimate VIP experience",
            "Bespoke trading solutions",
            "Direct exchange integration",
            "Equity participation opportunities",
            "Global VIP network access",
            "Lifetime VIP status"
        ]
    }
}

# Models
class VIPStatus(BaseModel):
    user_id: str
    tier: VIPTier
    trading_volume_30d: float
    tiger_balance: float
    maker_fee: float
    taker_fee: float
    withdrawal_fee_discount: float
    benefits: List[str]
    next_tier: Optional[VIPTier] = None
    next_tier_requirements: Optional[Dict] = None
    tier_expiry: Optional[datetime] = None

class VIPBenefit(BaseModel):
    benefit_id: str
    name: str
    description: str
    tier_required: VIPTier
    active: bool = True

class VIPReward(BaseModel):
    reward_id: str
    user_id: str
    reward_type: str
    amount: float
    description: str
    claimed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TradingVolumeUpdate(BaseModel):
    user_id: str
    volume: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TigerBalanceUpdate(BaseModel):
    user_id: str
    balance: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# In-memory storage (replace with database in production)
user_vip_status = {}
vip_rewards = {}
trading_volumes = {}
tiger_balances = {}

# Helper Functions
def calculate_vip_tier(trading_volume_30d: float, tiger_balance: float) -> VIPTier:
    """Calculate VIP tier based on trading volume and TIGER balance"""
    current_tier = VIPTier.REGULAR
    
    for tier, config in reversed(list(VIP_TIERS.items())):
        if (trading_volume_30d >= config["trading_volume_30d"] and 
            tiger_balance >= config["tiger_balance"]):
            current_tier = tier
            break
    
    return current_tier

def get_next_tier(current_tier: VIPTier) -> Optional[VIPTier]:
    """Get the next VIP tier"""
    tiers = list(VIP_TIERS.keys())
    try:
        current_index = tiers.index(current_tier)
        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
    except ValueError:
        pass
    return None

def get_tier_requirements(tier: VIPTier) -> Dict:
    """Get requirements for a specific tier"""
    config = VIP_TIERS.get(tier, {})
    return {
        "trading_volume_30d": config.get("trading_volume_30d", 0),
        "tiger_balance": config.get("tiger_balance", 0)
    }

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vip-program-service"}

@app.get("/api/vip/tiers")
async def get_vip_tiers():
    """Get all VIP tier configurations"""
    return {
        "tiers": VIP_TIERS,
        "total_tiers": len(VIP_TIERS)
    }

@app.get("/api/vip/status/{user_id}", response_model=VIPStatus)
async def get_vip_status(user_id: str):
    """Get VIP status for a user"""
    
    # Get user's trading volume and TIGER balance
    trading_volume = trading_volumes.get(user_id, 0)
    tiger_balance = tiger_balances.get(user_id, 0)
    
    # Calculate tier
    tier = calculate_vip_tier(trading_volume, tiger_balance)
    tier_config = VIP_TIERS[tier]
    
    # Get next tier info
    next_tier = get_next_tier(tier)
    next_tier_requirements = None
    if next_tier:
        next_tier_requirements = get_tier_requirements(next_tier)
    
    status = VIPStatus(
        user_id=user_id,
        tier=tier,
        trading_volume_30d=trading_volume,
        tiger_balance=tiger_balance,
        maker_fee=tier_config["maker_fee"],
        taker_fee=tier_config["taker_fee"],
        withdrawal_fee_discount=tier_config["withdrawal_fee_discount"],
        benefits=tier_config["benefits"],
        next_tier=next_tier,
        next_tier_requirements=next_tier_requirements,
        tier_expiry=datetime.utcnow() + timedelta(days=30)
    )
    
    user_vip_status[user_id] = status
    return status

@app.post("/api/vip/trading-volume")
async def update_trading_volume(update: TradingVolumeUpdate):
    """Update user's 30-day trading volume"""
    trading_volumes[update.user_id] = update.volume
    
    # Recalculate VIP tier
    tiger_balance = tiger_balances.get(update.user_id, 0)
    new_tier = calculate_vip_tier(update.volume, tiger_balance)
    
    return {
        "user_id": update.user_id,
        "trading_volume_30d": update.volume,
        "new_tier": new_tier,
        "updated_at": update.timestamp
    }

@app.post("/api/vip/tiger-balance")
async def update_tiger_balance(update: TigerBalanceUpdate):
    """Update user's TIGER token balance"""
    tiger_balances[update.user_id] = update.balance
    
    # Recalculate VIP tier
    trading_volume = trading_volumes.get(update.user_id, 0)
    new_tier = calculate_vip_tier(trading_volume, update.balance)
    
    return {
        "user_id": update.user_id,
        "tiger_balance": update.balance,
        "new_tier": new_tier,
        "updated_at": update.timestamp
    }

@app.get("/api/vip/benefits/{tier}")
async def get_tier_benefits(tier: VIPTier):
    """Get benefits for a specific VIP tier"""
    if tier not in VIP_TIERS:
        raise HTTPException(status_code=404, detail="VIP tier not found")
    
    return {
        "tier": tier,
        "config": VIP_TIERS[tier]
    }

@app.get("/api/vip/fees/{user_id}")
async def get_user_fees(user_id: str):
    """Get trading fees for a user based on VIP tier"""
    
    trading_volume = trading_volumes.get(user_id, 0)
    tiger_balance = tiger_balances.get(user_id, 0)
    tier = calculate_vip_tier(trading_volume, tiger_balance)
    tier_config = VIP_TIERS[tier]
    
    return {
        "user_id": user_id,
        "tier": tier,
        "maker_fee": tier_config["maker_fee"],
        "taker_fee": tier_config["taker_fee"],
        "withdrawal_fee_discount": tier_config["withdrawal_fee_discount"]
    }

@app.post("/api/vip/rewards")
async def create_vip_reward(reward: VIPReward):
    """Create a VIP reward for a user"""
    if reward.user_id not in vip_rewards:
        vip_rewards[reward.user_id] = []
    
    vip_rewards[reward.user_id].append(reward)
    
    return {
        "message": "VIP reward created successfully",
        "reward": reward
    }

@app.get("/api/vip/rewards/{user_id}")
async def get_user_rewards(user_id: str):
    """Get all rewards for a user"""
    rewards = vip_rewards.get(user_id, [])
    
    return {
        "user_id": user_id,
        "total_rewards": len(rewards),
        "unclaimed_rewards": len([r for r in rewards if not r.claimed]),
        "rewards": rewards
    }

@app.post("/api/vip/rewards/{reward_id}/claim")
async def claim_reward(reward_id: str, user_id: str):
    """Claim a VIP reward"""
    user_rewards = vip_rewards.get(user_id, [])
    
    for reward in user_rewards:
        if reward.reward_id == reward_id:
            if reward.claimed:
                raise HTTPException(status_code=400, detail="Reward already claimed")
            
            reward.claimed = True
            return {
                "message": "Reward claimed successfully",
                "reward": reward
            }
    
    raise HTTPException(status_code=404, detail="Reward not found")

@app.get("/api/vip/leaderboard")
async def get_vip_leaderboard(limit: int = 100):
    """Get VIP leaderboard based on trading volume"""
    
    leaderboard = []
    for user_id, volume in trading_volumes.items():
        tiger_balance = tiger_balances.get(user_id, 0)
        tier = calculate_vip_tier(volume, tiger_balance)
        
        leaderboard.append({
            "user_id": user_id,
            "trading_volume_30d": volume,
            "tiger_balance": tiger_balance,
            "tier": tier
        })
    
    # Sort by trading volume
    leaderboard.sort(key=lambda x: x["trading_volume_30d"], reverse=True)
    
    return {
        "leaderboard": leaderboard[:limit],
        "total_users": len(leaderboard)
    }

@app.get("/api/vip/statistics")
async def get_vip_statistics():
    """Get VIP program statistics"""
    
    tier_distribution = {}
    for tier in VIP_TIERS.keys():
        tier_distribution[tier] = 0
    
    for user_id, volume in trading_volumes.items():
        tiger_balance = tiger_balances.get(user_id, 0)
        tier = calculate_vip_tier(volume, tiger_balance)
        tier_distribution[tier] += 1
    
    total_trading_volume = sum(trading_volumes.values())
    total_tiger_staked = sum(tiger_balances.values())
    
    return {
        "total_vip_users": len(trading_volumes),
        "tier_distribution": tier_distribution,
        "total_trading_volume_30d": total_trading_volume,
        "total_tiger_staked": total_tiger_staked,
        "total_rewards_distributed": sum(len(rewards) for rewards in vip_rewards.values())
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)