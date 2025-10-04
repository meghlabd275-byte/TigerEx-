"""
DeFi Staking Service - TigerEx Exchange
Port: 8056

Provides DeFi protocol staking functionality:
- Multi-protocol integration
- Yield farming
- Liquidity mining
- Auto-compounding
- Risk assessment
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import redis
import logging
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "postgresql://user:password@localhost:5432/tigerex_defi_staking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# FastAPI app
app = FastAPI(title="DeFi Staking Service", version="1.0.0")

# Include admin router
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class DeFiProtocol(Base):
    __tablename__ = "defi_protocols"
    
    id = Column(Integer, primary_key=True, index=True)
    protocol_name = Column(String, unique=True, index=True)
    protocol_type = Column(String)  # lending, farming, staking, liquidity
    chain = Column(String)
    contract_address = Column(String)
    token_symbol = Column(String)
    apy = Column(Numeric(5, 2))
    tvl = Column(Numeric(20, 2))
    risk_level = Column(String)  # low, medium, high
    is_active = Column(Boolean, default=True)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StakingPosition(Base):
    __tablename__ = "staking_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    protocol_id = Column(Integer, index=True)
    protocol_name = Column(String)
    asset_symbol = Column(String)
    staked_amount = Column(Numeric(20, 8))
    reward_amount = Column(Numeric(20, 8), default=Decimal('0'))
    apy_at_stake = Column(Numeric(5, 2))
    start_time = Column(DateTime, default=datetime.utcnow)
    last_compound = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    auto_compound = Column(Boolean, default=True)
    parameters = Column(JSON)

class YieldFarming(Base):
    __tablename__ = "yield_farming"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    protocol_name = Column(String)
    pool_name = Column(String)
    lp_tokens = Column(Numeric(20, 8))
    reward_tokens = Column(Numeric(20, 8), default=Decimal('0'))
    apy = Column(Numeric(5, 2))
    impermanent_loss = Column(Numeric(5, 4), default=Decimal('0'))
    start_time = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class LiquidityMining(Base):
    __tablename__ = "liquidity_mining"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    protocol_name = Column(String)
    token_symbol = Column(String)
    amount = Column(Numeric(20, 8))
    rewards_per_day = Column(Numeric(20, 8))
    total_rewards = Column(Numeric(20, 8), default=Decimal('0'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)

class AutoCompound(Base):
    __tablename__ = "auto_compound"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    protocol_name = Column(String)
    position_id = Column(Integer)
    compound_frequency = Column(String)  # daily, weekly, monthly
    last_compound = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    protocol_name = Column(String, unique=True, index=True)
    smart_contract_risk = Column(Integer)  # 1-10
    liquidity_risk = Column(Integer)  # 1-10
    governance_risk = Column(Integer)  # 1-10
    market_risk = Column(Integer)  # 1-10
    overall_risk = Column(Integer)  # 1-10
    last_updated = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ProtocolCreate(BaseModel):
    protocol_name: str
    protocol_type: str = Field(..., regex="^(lending|farming|staking|liquidity)$")
    chain: str
    contract_address: str
    token_symbol: str
    apy: Decimal = Field(..., ge=Decimal('0'))
    tvl: Decimal = Field(..., ge=Decimal('0'))
    risk_level: str = Field(..., regex="^(low|medium|high)$")
    parameters: Optional[Dict[str, Any]] = {}

class StakingCreate(BaseModel):
    user_id: str
    protocol_name: str
    asset_symbol: str
    amount: Decimal = Field(..., gt=Decimal('0'))
    auto_compound: bool = True

class YieldFarmingCreate(BaseModel):
    user_id: str
    protocol_name: str
    pool_name: str
    lp_tokens: Decimal = Field(..., gt=Decimal('0'))
    apy: Decimal = Field(..., gt=Decimal('0'))

class LiquidityMiningCreate(BaseModel):
    user_id: str
    protocol_name: str
    token_symbol: str
    amount: Decimal = Field(..., gt=Decimal('0'))
    rewards_per_day: Decimal = Field(..., gt=Decimal('0'))
    duration_days: int = Field(..., ge=1)

class AutoCompoundCreate(BaseModel):
    user_id: str
    protocol_name: str
    position_id: int
    compound_frequency: str = Field(..., regex="^(daily|weekly|monthly)$")

# Database initialization
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_protocol_data(protocol_name: str) -> Dict[str, Any]:
    """Get protocol data from external APIs"""
    try:
        # Mock data - in production use DeFi Llama, DeBank, etc.
        protocols = {
            "aave": {
                "apy": Decimal('3.5'),
                "tvl": Decimal('1500000000'),
                "risk_level": "medium",
                "chain": "ethereum"
            },
            "compound": {
                "apy": Decimal('2.8'),
                "tvl": Decimal('800000000'),
                "risk_level": "medium",
                "chain": "ethereum"
            },
            "maker": {
                "apy": Decimal('4.2'),
                "tvl": Decimal('1200000000'),
                "risk_level": "low",
                "chain": "ethereum"
            },
            "uniswap": {
                "apy": Decimal('15.5'),
                "tvl": Decimal('5000000000'),
                "risk_level": "high",
                "chain": "ethereum"
            },
            "curve": {
                "apy": Decimal('8.2'),
                "tvl": Decimal('3000000000'),
                "risk_level": "medium",
                "chain": "ethereum"
            },
            "sushiswap": {
                "apy": Decimal('12.8'),
                "tvl": Decimal('1000000000'),
                "risk_level": "high",
                "chain": "ethereum"
            }
        }
        
        return protocols.get(protocol_name.lower(), {})
    except Exception as e:
        logger.error(f"Error getting protocol data: {e}")
        return {}

async def calculate_impermanent_loss(
    price_ratio: float,
    initial_ratio: float = 1.0
) -> float:
    """Calculate impermanent loss for liquidity provision"""
    try:
        # IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
        il = 2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1
        return max(il, 0)  # Return absolute value
    except Exception as e:
        logger.error(f"Error calculating impermanent loss: {e}")
        return 0.0

async def get_token_price(token_symbol: str) -> Decimal:
    """Get token price from external APIs"""
    try:
        # Mock prices - in production use CoinGecko, CoinMarketCap
        prices = {
            "eth": Decimal('2500'),
            "btc": Decimal('45000'),
            "usdc": Decimal('1'),
            "usdt": Decimal('1'),
            "dai": Decimal('1'),
            "wbtc": Decimal('45000'),
            "aave": Decimal('85'),
            "comp": Decimal('55'),
            "uni": Decimal('6.5'),
            "crv": Decimal('0.45'),
            "sushi": Decimal('1.2')
        }
        
        return prices.get(token_symbol.lower(), Decimal('0'))
    except Exception as e:
        logger.error(f"Error getting token price: {e}")
        return Decimal('0')

async def compound_rewards(
    user_id: str,
    protocol_name: str,
    position_id: int,
    db: Session
) -> Dict[str, Any]:
    """Compound staking rewards"""
    try:
        # Get position
        position = db.query(StakingPosition).filter(
            StakingPosition.id == position_id,
            StakingPosition.user_id == user_id,
            StakingPosition.protocol_name == protocol_name,
            StakingPosition.is_active == True
        ).first()
        
        if not position:
            return {"error": "Position not found"}
        
        # Calculate rewards
        rewards = position.reward_amount
        
        if rewards > 0:
            # Compound rewards
            position.staked_amount += rewards
            position.reward_amount = Decimal('0')
            position.last_compound = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "compounded_amount": str(rewards),
                "new_staked_amount": str(position.staked_amount)
            }
        
        return {"success": True, "message": "No rewards to compound"}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

# API Endpoints
@app.post("/api/v1/protocols", response_model=Dict[str, Any])
async def create_protocol(
    protocol: ProtocolCreate,
    db: Session = Depends(get_db)
):
    """Create a new DeFi protocol"""
    try:
        db_protocol = DeFiProtocol(
            protocol_name=protocol.protocol_name,
            protocol_type=protocol.protocol_type,
            chain=protocol.chain,
            contract_address=protocol.contract_address,
            token_symbol=protocol.token_symbol,
            apy=protocol.apy,
            tvl=protocol.tvl,
            risk_level=protocol.risk_level,
            parameters=protocol.parameters or {}
        )
        db.add(db_protocol)
        db.commit()
        db.refresh(db_protocol)
        
        return {"success": True, "protocol_id": db_protocol.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/protocols")
async def get_protocols(
    protocol_type: Optional[str] = None,
    chain: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get DeFi protocols with filtering"""
    query = db.query(DeFiProtocol).filter(DeFiProtocol.is_active == True)
    
    if protocol_type:
        query = query.filter(DeFiProtocol.protocol_type == protocol_type)
    if chain:
        query = query.filter(DeFiProtocol.chain == chain)
    if risk_level:
        query = query.filter(DeFiProtocol.risk_level == risk_level)
    
    protocols = query.all()
    
    return {
        "protocols": [
            {
                "protocol_name": p.protocol_name,
                "protocol_type": p.protocol_type,
                "chain": p.chain,
                "token_symbol": p.token_symbol,
                "apy": float(p.apy),
                "tvl": float(p.tvl),
                "risk_level": p.risk_level,
                "parameters": p.parameters
            }
            for p in protocols
        ]
    }

@app.post("/api/v1/staking", response_model=Dict[str, Any])
async def create_staking_position(
    staking: StakingCreate,
    db: Session = Depends(get_db)
):
    """Create a new staking position"""
    try:
        # Get protocol data
        protocol = db.query(DeFiProtocol).filter(
            DeFiProtocol.protocol_name == staking.protocol_name,
            DeFiProtocol.is_active == True
        ).first()
        
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        # Create staking position
        position = StakingPosition(
            user_id=staking.user_id,
            protocol_id=protocol.id,
            protocol_name=staking.protocol_name,
            asset_symbol=staking.asset_symbol,
            staked_amount=staking.amount,
            apy_at_stake=protocol.apy,
            auto_compound=staking.auto_compound
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        
        return {
            "success": True,
            "position_id": position.id,
            "protocol": staking.protocol_name,
            "amount": str(staking.amount)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/yield-farming", response_model=Dict[str, Any])
async def create_yield_farming(
    farming: YieldFarmingCreate,
    db: Session = Depends(get_db)
):
    """Create a new yield farming position"""
    try:
        # Calculate impermanent loss
        impermanent_loss = await calculate_impermanent_loss(1.0)
        
        farming_position = YieldFarming(
            user_id=farming.user_id,
            protocol_name=farming.protocol_name,
            pool_name=farming.pool_name,
            lp_tokens=farming.lp_tokens,
            apy=farming.apy,
            impermanent_loss=Decimal(str(impermanent_loss))
        )
        db.add(farming_position)
        db.commit()
        db.refresh(farming_position)
        
        return {
            "success": True,
            "position_id": farming_position.id,
            "impermanent_loss": impermanent_loss
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/liquidity-mining", response_model=Dict[str, Any])
async def create_liquidity_mining(
    mining: LiquidityMiningCreate,
    db: Session = Depends(get_db)
):
    """Create a new liquidity mining position"""
    try:
        end_time = datetime.utcnow() + timedelta(days=mining.duration_days)
        
        mining_position = LiquidityMining(
            user_id=mining.user_id,
            protocol_name=mining.protocol_name,
            token_symbol=mining.token_symbol,
            amount=mining.amount,
            rewards_per_day=mining.rewards_per_day,
            end_time=end_time
        )
        db.add(mining_position)
        db.commit()
        db.refresh(mining_position)
        
        return {
            "success": True,
            "position_id": mining_position.id,
            "end_time": end_time.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/positions/{user_id}")
async def get_user_positions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's staking positions"""
    positions = db.query(StakingPosition).filter(
        StakingPosition.user_id == user_id,
        StakingPosition.is_active == True
    ).all()
    
    return {
        "positions": [
            {
                "id": p.id,
                "protocol_name": p.protocol_name,
                "asset_symbol": p.asset_symbol,
                "staked_amount": str(p.staked_amount),
                "reward_amount": str(p.reward_amount),
                "apy": float(p.apy_at_stake),
                "start_time": p.start_time.isoformat(),
                "auto_compound": p.auto_compound
            }
            for p in positions
        ]
    }

@app.get("/api/v1/performance/{user_id}")
async def get_user_performance(user_id: str, db: Session = Depends(get_db)):
    """Get user's DeFi staking performance"""
    try:
        # Get all positions
        positions = db.query(StakingPosition).filter(
            StakingPosition.user_id == user_id,
            StakingPosition.is_active == True
        ).all()
        
        total_staked = Decimal('0')
        total_rewards = Decimal('0')
        
        for position in positions:
            total_staked += position.staked_amount
            total_rewards += position.reward_amount
        
        # Get yield farming positions
        farming_positions = db.query(YieldFarming).filter(
            YieldFarming.user_id == user_id,
            YieldFarming.is_active == True
        ).all()
        
        farming_value = Decimal('0')
        farming_rewards = Decimal('0')
        
        for farming in farming_positions:
            farming_value += farming.lp_tokens
            farming_rewards += farming.reward_tokens
        
        # Get liquidity mining positions
        mining_positions = db.query(LiquidityMining).filter(
            LiquidityMining.user_id == user_id,
            LiquidityMining.is_active == True
        ).all()
        
        mining_value = Decimal('0')
        mining_rewards = Decimal('0')
        
        for mining in mining_positions:
            mining_value += mining.amount
            mining_rewards += mining.total_rewards
        
        # Calculate total portfolio value
        total_value = total_staked + farming_value + mining_value
        total_return = total_rewards + farming_rewards + mining_rewards
        
        return {
            "total_staked": str(total_staked),
            "total_rewards": str(total_rewards),
            "total_return": str(total_return),
            "total_value": str(total_value),
            "positions": len(positions),
            "farming_positions": len(farming_positions),
            "mining_positions": len(mining_positions),
            "return_percentage": float((total_return / total_value * 100)) if total_value > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/apy/{protocol_name}")
async def get_protocol_apy(protocol_name: str, db: Session = Depends(get_db)):
    """Get current APY for a protocol"""
    protocol = db.query(DeFiProtocol).filter(
        DeFiProtocol.protocol_name == protocol_name,
        DeFiProtocol.is_active == True
    ).first()
    
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    return {
        "protocol_name": protocol.protocol_name,
        "apy": float(protocol.apy),
        "tvl": float(protocol.tvl),
        "risk_level": protocol.risk_level,
        "last_updated": protocol.updated_at.isoformat()
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(reward_calculator())
    asyncio.create_task(auto_compound_scheduler())

async def reward_calculator():
    """Background task to calculate staking rewards"""
    while True:
        try:
            db = SessionLocal()
            active_positions = db.query(StakingPosition).filter(
                StakingPosition.is_active == True
            ).all()
            
            for position in active_positions:
                # Calculate daily rewards
                daily_rate = position.apy_at_stake / Decimal('365') / Decimal('100')
                daily_reward = position.staked_amount * daily_rate
                
                # Add to reward balance
                position.reward_amount += daily_reward
                position.updated_at = datetime.utcnow()
            
            db.commit()
            db.close()
            await asyncio.sleep(86400)  # Daily
            
        except Exception as e:
            logger.error(f"Error in reward calculator: {e}")
            await asyncio.sleep(3600)

async def auto_compound_scheduler():
    """Background task for auto-compounding"""
    while True:
        try:
            db = SessionLocal()
            auto_compound_positions = db.query(StakingPosition).filter(
                StakingPosition.auto_compound == True,
                StakingPosition.is_active == True
            ).all()
            
            for position in auto_compound_positions:
                # Check if rewards > 1% of staked amount
                if position.reward_amount > position.staked_amount * Decimal('0.01'):
                    # Compound rewards
                    position.staked_amount += position.reward_amount
                    position.reward_amount = Decimal('0')
                    position.last_compound = datetime.utcnow()
            
            db.commit()
            db.close()
            await asyncio.sleep(3600)  # Hourly
            
        except Exception as e:
            logger.error(f"Error in auto compound scheduler: {e}")
            await asyncio.sleep(3600)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "defi-staking-service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8056)