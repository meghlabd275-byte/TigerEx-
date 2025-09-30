from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Staking Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/staking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class StakingProductDB(Base):
    __tablename__ = "staking_products"
    
    id = Column(String, primary_key=True)
    asset = Column(String, nullable=False)
    product_type = Column(String, nullable=False)  # flexible, locked
    duration_days = Column(Integer, nullable=True)
    apy = Column(Float, nullable=False)
    min_amount = Column(Float, default=0.0)
    max_amount = Column(Float, nullable=True)
    total_staked = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StakingPositionDB(Base):
    __tablename__ = "staking_positions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    asset = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    apy = Column(Float, nullable=False)
    product_type = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active, completed, cancelled
    total_rewards = Column(Float, default=0.0)
    last_reward_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class StakingRewardDB(Base):
    __tablename__ = "staking_rewards"
    
    id = Column(String, primary_key=True)
    position_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    asset = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    reward_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, distributed

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class ProductType(str, Enum):
    FLEXIBLE = "flexible"
    LOCKED = "locked"

class StakingProductCreate(BaseModel):
    asset: str
    product_type: ProductType
    duration_days: Optional[int] = None
    apy: float = Field(gt=0, le=100)
    min_amount: float = Field(ge=0)
    max_amount: Optional[float] = None

class StakingProductResponse(BaseModel):
    id: str
    asset: str
    product_type: str
    duration_days: Optional[int]
    apy: float
    min_amount: float
    max_amount: Optional[float]
    total_staked: float
    is_active: bool
    created_at: datetime

class StakeRequest(BaseModel):
    product_id: str
    amount: float = Field(gt=0)

class StakingPositionResponse(BaseModel):
    id: str
    user_id: str
    product_id: str
    asset: str
    amount: float
    apy: float
    product_type: str
    duration_days: Optional[int]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    total_rewards: float
    estimated_daily_reward: float

class RewardResponse(BaseModel):
    id: str
    position_id: str
    user_id: str
    asset: str
    amount: float
    reward_date: datetime
    status: str

# Reward calculation background task
async def calculate_and_distribute_rewards(db: Session):
    """Background task to calculate and distribute staking rewards"""
    while True:
        try:
            # Get all active positions
            positions = db.query(StakingPositionDB).filter(
                StakingPositionDB.status == "active"
            ).all()
            
            for position in positions:
                # Calculate daily reward
                daily_reward = (position.amount * position.apy / 100) / 365
                
                # Check if 24 hours passed since last reward
                time_since_last = datetime.utcnow() - position.last_reward_date
                if time_since_last >= timedelta(hours=24):
                    # Create reward record
                    reward_id = str(uuid.uuid4())
                    reward = StakingRewardDB(
                        id=reward_id,
                        position_id=position.id,
                        user_id=position.user_id,
                        asset=position.asset,
                        amount=daily_reward,
                        reward_date=datetime.utcnow(),
                        status="distributed"
                    )
                    
                    db.add(reward)
                    
                    # Update position
                    position.total_rewards += daily_reward
                    position.last_reward_date = datetime.utcnow()
                    
                    # Check if locked staking period ended
                    if position.product_type == "locked" and position.end_date:
                        if datetime.utcnow() >= position.end_date:
                            position.status = "completed"
                    
                    db.commit()
                    logger.info(f"Distributed reward {daily_reward} {position.asset} to position {position.id}")
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Error in reward distribution: {e}")
            await asyncio.sleep(60)

# API Endpoints
@app.post("/products", response_model=StakingProductResponse)
async def create_product(product: StakingProductCreate, db: Session = Depends(get_db)):
    """Create a staking product"""
    product_id = str(uuid.uuid4())
    
    db_product = StakingProductDB(
        id=product_id,
        asset=product.asset,
        product_type=product.product_type,
        duration_days=product.duration_days,
        apy=product.apy,
        min_amount=product.min_amount,
        max_amount=product.max_amount,
        created_at=datetime.utcnow()
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return StakingProductResponse(
        id=db_product.id,
        asset=db_product.asset,
        product_type=db_product.product_type,
        duration_days=db_product.duration_days,
        apy=db_product.apy,
        min_amount=db_product.min_amount,
        max_amount=db_product.max_amount,
        total_staked=db_product.total_staked,
        is_active=db_product.is_active,
        created_at=db_product.created_at
    )

@app.get("/products", response_model=List[StakingProductResponse])
async def list_products(asset: Optional[str] = None, product_type: Optional[str] = None, db: Session = Depends(get_db)):
    """List all staking products"""
    query = db.query(StakingProductDB).filter(StakingProductDB.is_active == True)
    
    if asset:
        query = query.filter(StakingProductDB.asset == asset)
    if product_type:
        query = query.filter(StakingProductDB.product_type == product_type)
    
    products = query.all()
    
    return [StakingProductResponse(
        id=p.id,
        asset=p.asset,
        product_type=p.product_type,
        duration_days=p.duration_days,
        apy=p.apy,
        min_amount=p.min_amount,
        max_amount=p.max_amount,
        total_staked=p.total_staked,
        is_active=p.is_active,
        created_at=p.created_at
    ) for p in products]

@app.post("/stake", response_model=StakingPositionResponse)
async def stake_asset(stake: StakeRequest, user_id: str = "user123", db: Session = Depends(get_db)):
    """Stake assets"""
    product = db.query(StakingProductDB).filter(StakingProductDB.id == stake.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not product.is_active:
        raise HTTPException(status_code=400, detail="Product is not active")
    
    if stake.amount < product.min_amount:
        raise HTTPException(status_code=400, detail=f"Minimum stake amount is {product.min_amount}")
    
    if product.max_amount and stake.amount > product.max_amount:
        raise HTTPException(status_code=400, detail=f"Maximum stake amount is {product.max_amount}")
    
    position_id = str(uuid.uuid4())
    
    # Calculate end date for locked staking
    end_date = None
    if product.product_type == "locked" and product.duration_days:
        end_date = datetime.utcnow() + timedelta(days=product.duration_days)
    
    position = StakingPositionDB(
        id=position_id,
        user_id=user_id,
        product_id=product.id,
        asset=product.asset,
        amount=stake.amount,
        apy=product.apy,
        product_type=product.product_type,
        duration_days=product.duration_days,
        start_date=datetime.utcnow(),
        end_date=end_date,
        status="active",
        created_at=datetime.utcnow()
    )
    
    db.add(position)
    
    # Update product total staked
    product.total_staked += stake.amount
    
    db.commit()
    db.refresh(position)
    
    daily_reward = (stake.amount * product.apy / 100) / 365
    
    return StakingPositionResponse(
        id=position.id,
        user_id=position.user_id,
        product_id=position.product_id,
        asset=position.asset,
        amount=position.amount,
        apy=position.apy,
        product_type=position.product_type,
        duration_days=position.duration_days,
        start_date=position.start_date,
        end_date=position.end_date,
        status=position.status,
        total_rewards=position.total_rewards,
        estimated_daily_reward=daily_reward
    )

@app.post("/unstake/{position_id}")
async def unstake_asset(position_id: str, user_id: str = "user123", db: Session = Depends(get_db)):
    """Unstake assets"""
    position = db.query(StakingPositionDB).filter(
        StakingPositionDB.id == position_id,
        StakingPositionDB.user_id == user_id
    ).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if position.status != "active":
        raise HTTPException(status_code=400, detail="Position is not active")
    
    # Check if locked period ended
    if position.product_type == "locked" and position.end_date:
        if datetime.utcnow() < position.end_date:
            raise HTTPException(status_code=400, detail="Locked period has not ended")
    
    # Update position status
    position.status = "completed"
    
    # Update product total staked
    product = db.query(StakingProductDB).filter(StakingProductDB.id == position.product_id).first()
    if product:
        product.total_staked -= position.amount
    
    db.commit()
    
    return {
        "message": "Unstaked successfully",
        "position_id": position_id,
        "amount": position.amount,
        "total_rewards": position.total_rewards
    }

@app.get("/positions", response_model=List[StakingPositionResponse])
async def list_positions(user_id: str = "user123", status: Optional[str] = None, db: Session = Depends(get_db)):
    """List user staking positions"""
    query = db.query(StakingPositionDB).filter(StakingPositionDB.user_id == user_id)
    
    if status:
        query = query.filter(StakingPositionDB.status == status)
    
    positions = query.all()
    
    return [StakingPositionResponse(
        id=pos.id,
        user_id=pos.user_id,
        product_id=pos.product_id,
        asset=pos.asset,
        amount=pos.amount,
        apy=pos.apy,
        product_type=pos.product_type,
        duration_days=pos.duration_days,
        start_date=pos.start_date,
        end_date=pos.end_date,
        status=pos.status,
        total_rewards=pos.total_rewards,
        estimated_daily_reward=(pos.amount * pos.apy / 100) / 365
    ) for pos in positions]

@app.get("/rewards", response_model=List[RewardResponse])
async def list_rewards(user_id: str = "user123", db: Session = Depends(get_db)):
    """List user staking rewards"""
    rewards = db.query(StakingRewardDB).filter(
        StakingRewardDB.user_id == user_id
    ).order_by(StakingRewardDB.reward_date.desc()).all()
    
    return [RewardResponse(
        id=r.id,
        position_id=r.position_id,
        user_id=r.user_id,
        asset=r.asset,
        amount=r.amount,
        reward_date=r.reward_date,
        status=r.status
    ) for r in rewards]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "staking"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)