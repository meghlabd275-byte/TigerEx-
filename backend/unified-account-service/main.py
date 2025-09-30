from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified Trading Account Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/unified_account"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class UnifiedAccountDB(Base):
    __tablename__ = "unified_accounts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    total_equity = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    margin_available = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    margin_level = Column(Float, default=0.0)
    account_mode = Column(String, default="single")  # single, portfolio, cross
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AccountPositionDB(Base):
    __tablename__ = "account_positions"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False)
    position_type = Column(String, nullable=False)  # spot, futures, margin
    side = Column(String, nullable=False)  # long, short
    size = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    leverage = Column(Float, default=1.0)
    liquidation_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AccountAssetDB(Base):
    __tablename__ = "account_assets"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False, index=True)
    asset = Column(String, nullable=False)
    total_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    locked_balance = Column(Float, default=0.0)
    usd_value = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class AccountMode(str, Enum):
    SINGLE = "single"
    PORTFOLIO = "portfolio"
    CROSS = "cross"

class UnifiedAccountCreate(BaseModel):
    user_id: str
    account_mode: AccountMode = AccountMode.SINGLE

class UnifiedAccountResponse(BaseModel):
    id: str
    user_id: str
    total_equity: float
    available_balance: float
    margin_used: float
    margin_available: float
    unrealized_pnl: float
    realized_pnl: float
    margin_level: float
    account_mode: str
    created_at: datetime
    updated_at: datetime

class PositionResponse(BaseModel):
    id: str
    account_id: str
    symbol: str
    position_type: str
    side: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    margin_used: float
    leverage: float
    liquidation_price: Optional[float]

class AssetResponse(BaseModel):
    id: str
    account_id: str
    asset: str
    total_balance: float
    available_balance: float
    locked_balance: float
    usd_value: float

# API Endpoints
@app.post("/accounts", response_model=UnifiedAccountResponse)
async def create_account(account: UnifiedAccountCreate, db: Session = Depends(get_db)):
    """Create a unified trading account"""
    existing = db.query(UnifiedAccountDB).filter(UnifiedAccountDB.user_id == account.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")
    
    account_id = str(uuid.uuid4())
    db_account = UnifiedAccountDB(
        id=account_id,
        user_id=account.user_id,
        account_mode=account.account_mode,
        created_at=datetime.utcnow()
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return UnifiedAccountResponse(
        id=db_account.id,
        user_id=db_account.user_id,
        total_equity=db_account.total_equity,
        available_balance=db_account.available_balance,
        margin_used=db_account.margin_used,
        margin_available=db_account.margin_available,
        unrealized_pnl=db_account.unrealized_pnl,
        realized_pnl=db_account.realized_pnl,
        margin_level=db_account.margin_level,
        account_mode=db_account.account_mode,
        created_at=db_account.created_at,
        updated_at=db_account.updated_at
    )

@app.get("/accounts/{user_id}", response_model=UnifiedAccountResponse)
async def get_account(user_id: str, db: Session = Depends(get_db)):
    """Get unified account details"""
    account = db.query(UnifiedAccountDB).filter(UnifiedAccountDB.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return UnifiedAccountResponse(
        id=account.id,
        user_id=account.user_id,
        total_equity=account.total_equity,
        available_balance=account.available_balance,
        margin_used=account.margin_used,
        margin_available=account.margin_available,
        unrealized_pnl=account.unrealized_pnl,
        realized_pnl=account.realized_pnl,
        margin_level=account.margin_level,
        account_mode=account.account_mode,
        created_at=account.created_at,
        updated_at=account.updated_at
    )

@app.get("/accounts/{user_id}/positions", response_model=List[PositionResponse])
async def get_positions(user_id: str, db: Session = Depends(get_db)):
    """Get all positions for unified account"""
    account = db.query(UnifiedAccountDB).filter(UnifiedAccountDB.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    positions = db.query(AccountPositionDB).filter(AccountPositionDB.account_id == account.id).all()
    
    return [PositionResponse(
        id=pos.id,
        account_id=pos.account_id,
        symbol=pos.symbol,
        position_type=pos.position_type,
        side=pos.side,
        size=pos.size,
        entry_price=pos.entry_price,
        current_price=pos.current_price,
        unrealized_pnl=pos.unrealized_pnl,
        margin_used=pos.margin_used,
        leverage=pos.leverage,
        liquidation_price=pos.liquidation_price
    ) for pos in positions]

@app.get("/accounts/{user_id}/assets", response_model=List[AssetResponse])
async def get_assets(user_id: str, db: Session = Depends(get_db)):
    """Get all assets in unified account"""
    account = db.query(UnifiedAccountDB).filter(UnifiedAccountDB.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    assets = db.query(AccountAssetDB).filter(AccountAssetDB.account_id == account.id).all()
    
    return [AssetResponse(
        id=asset.id,
        account_id=asset.account_id,
        asset=asset.asset,
        total_balance=asset.total_balance,
        available_balance=asset.available_balance,
        locked_balance=asset.locked_balance,
        usd_value=asset.usd_value
    ) for asset in assets]

@app.post("/accounts/{user_id}/mode")
async def change_account_mode(user_id: str, mode: AccountMode, db: Session = Depends(get_db)):
    """Change account mode"""
    account = db.query(UnifiedAccountDB).filter(UnifiedAccountDB.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.account_mode = mode
    account.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Account mode updated", "mode": mode}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "unified-account"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)