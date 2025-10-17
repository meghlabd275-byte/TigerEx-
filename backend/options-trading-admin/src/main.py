/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx Options Trading Admin Panel Service
Comprehensive admin panel for managing options contracts, Greeks monitoring, and risk management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum
import math

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, String, DECIMAL, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis
import numpy as np
from scipy.stats import norm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Options Trading Admin Panel",
    description="Admin panel for options contract management and risk monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql://postgres:password@localhost/tigerex_options_admin"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Enums
class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class OptionStyle(str, Enum):
    EUROPEAN = "european"
    AMERICAN = "american"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    SETTLED = "settled"

# Database Models
class OptionsContractDB(Base):
    __tablename__ = "options_contracts"
    
    id = Column(String, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    underlying_asset = Column(String, nullable=False)
    option_type = Column(String, nullable=False)  # call, put
    option_style = Column(String, nullable=False)  # european, american
    strike_price = Column(DECIMAL(20, 8), nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    contract_size = Column(DECIMAL(20, 8), default=1.0)
    premium = Column(DECIMAL(20, 8), default=0.0)
    open_interest = Column(Integer, default=0)
    volume_24h = Column(DECIMAL(30, 8), default=0.0)
    implied_volatility = Column(DECIMAL(10, 4), default=0.0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GreeksDataDB(Base):
    __tablename__ = "greeks_data"
    
    id = Column(String, primary_key=True)
    contract_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    delta = Column(DECIMAL(10, 6))
    gamma = Column(DECIMAL(10, 6))
    theta = Column(DECIMAL(10, 6))
    vega = Column(DECIMAL(10, 6))
    rho = Column(DECIMAL(10, 6))
    underlying_price = Column(DECIMAL(20, 8))
    created_at = Column(DateTime, default=datetime.utcnow)

class OptionsPositionDB(Base):
    __tablename__ = "options_positions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    contract_id = Column(String, nullable=False)
    position_type = Column(String, nullable=False)  # long, short
    quantity = Column(DECIMAL(20, 8), nullable=False)
    entry_price = Column(DECIMAL(20, 8), nullable=False)
    current_price = Column(DECIMAL(20, 8), default=0.0)
    unrealized_pnl = Column(DECIMAL(20, 8), default=0.0)
    margin_required = Column(DECIMAL(20, 8), default=0.0)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)

class VolatilitySurfaceDB(Base):
    __tablename__ = "volatility_surface"
    
    id = Column(String, primary_key=True)
    underlying_asset = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strike_price = Column(DECIMAL(20, 8), nullable=False)
    days_to_expiry = Column(Integer, nullable=False)
    implied_volatility = Column(DECIMAL(10, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SettlementHistoryDB(Base):
    __tablename__ = "settlement_history"
    
    id = Column(String, primary_key=True)
    contract_id = Column(String, nullable=False)
    settlement_date = Column(DateTime, default=datetime.utcnow)
    settlement_price = Column(DECIMAL(20, 8), nullable=False)
    total_contracts = Column(Integer, default=0)
    total_payout = Column(DECIMAL(30, 8), default=0.0)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Greeks Calculation Functions
def calculate_d1(S, K, T, r, sigma):
    """Calculate d1 for Black-Scholes"""
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def calculate_d2(S, K, T, r, sigma):
    """Calculate d2 for Black-Scholes"""
    return calculate_d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

def calculate_delta(S, K, T, r, sigma, option_type):
    """Calculate Delta"""
    d1 = calculate_d1(S, K, T, r, sigma)
    if option_type == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

def calculate_gamma(S, K, T, r, sigma):
    """Calculate Gamma"""
    d1 = calculate_d1(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

def calculate_theta(S, K, T, r, sigma, option_type):
    """Calculate Theta"""
    d1 = calculate_d1(S, K, T, r, sigma)
    d2 = calculate_d2(S, K, T, r, sigma)
    
    if option_type == "call":
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
    else:
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
    
    return theta / 365  # Daily theta

def calculate_vega(S, K, T, r, sigma):
    """Calculate Vega"""
    d1 = calculate_d1(S, K, T, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change in volatility

def calculate_rho(S, K, T, r, sigma, option_type):
    """Calculate Rho"""
    d2 = calculate_d2(S, K, T, r, sigma)
    
    if option_type == "call":
        return K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        return -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

# Pydantic Models
class OptionsContractCreate(BaseModel):
    symbol: str
    underlying_asset: str
    option_type: OptionType
    option_style: OptionStyle
    strike_price: Decimal
    expiry_date: datetime
    contract_size: Decimal = Decimal("1.0")
    premium: Decimal = Decimal("0.0")

class OptionsContractUpdate(BaseModel):
    premium: Optional[Decimal]
    implied_volatility: Optional[Decimal]
    status: Optional[ContractStatus]

class OptionsContractResponse(BaseModel):
    id: str
    symbol: str
    underlying_asset: str
    option_type: str
    option_style: str
    strike_price: Decimal
    expiry_date: datetime
    contract_size: Decimal
    premium: Decimal
    open_interest: int
    volume_24h: Decimal
    implied_volatility: Decimal
    status: str
    created_at: datetime

class GreeksResponse(BaseModel):
    contract_id: str
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    vega: Decimal
    rho: Decimal
    underlying_price: Decimal
    timestamp: datetime

class OptionsStatistics(BaseModel):
    total_contracts: int
    active_contracts: int
    total_open_interest: int
    total_volume_24h: Decimal
    total_premium_collected: Decimal
    pending_settlements: int

# API Endpoints

@app.post("/admin/options/contracts", response_model=OptionsContractResponse)
async def create_options_contract(
    contract: OptionsContractCreate,
    db: Session = Depends(get_db)
):
    """Create a new options contract"""
    import uuid
    
    # Check if symbol already exists
    existing = db.query(OptionsContractDB).filter(
        OptionsContractDB.symbol == contract.symbol
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract symbol already exists")
    
    # Validate expiry date
    if contract.expiry_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Expiry date must be in the future")
    
    contract_id = str(uuid.uuid4())
    db_contract = OptionsContractDB(
        id=contract_id,
        symbol=contract.symbol,
        underlying_asset=contract.underlying_asset,
        option_type=contract.option_type,
        option_style=contract.option_style,
        strike_price=contract.strike_price,
        expiry_date=contract.expiry_date,
        contract_size=contract.contract_size,
        premium=contract.premium,
        status="active",
        created_at=datetime.utcnow()
    )
    
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    logger.info(f"Created options contract: {contract.symbol}")
    
    return OptionsContractResponse(
        id=db_contract.id,
        symbol=db_contract.symbol,
        underlying_asset=db_contract.underlying_asset,
        option_type=db_contract.option_type,
        option_style=db_contract.option_style,
        strike_price=db_contract.strike_price,
        expiry_date=db_contract.expiry_date,
        contract_size=db_contract.contract_size,
        premium=db_contract.premium,
        open_interest=db_contract.open_interest,
        volume_24h=db_contract.volume_24h,
        implied_volatility=db_contract.implied_volatility,
        status=db_contract.status,
        created_at=db_contract.created_at
    )

@app.get("/admin/options/contracts", response_model=List[OptionsContractResponse])
async def list_options_contracts(
    underlying_asset: Optional[str] = None,
    option_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all options contracts"""
    query = db.query(OptionsContractDB)
    
    if underlying_asset:
        query = query.filter(OptionsContractDB.underlying_asset == underlying_asset)
    if option_type:
        query = query.filter(OptionsContractDB.option_type == option_type)
    if status:
        query = query.filter(OptionsContractDB.status == status)
    
    contracts = query.offset(skip).limit(limit).all()
    
    return [OptionsContractResponse(
        id=c.id,
        symbol=c.symbol,
        underlying_asset=c.underlying_asset,
        option_type=c.option_type,
        option_style=c.option_style,
        strike_price=c.strike_price,
        expiry_date=c.expiry_date,
        contract_size=c.contract_size,
        premium=c.premium,
        open_interest=c.open_interest,
        volume_24h=c.volume_24h,
        implied_volatility=c.implied_volatility,
        status=c.status,
        created_at=c.created_at
    ) for c in contracts]

@app.get("/admin/options/greeks/{contract_id}", response_model=GreeksResponse)
async def get_contract_greeks(
    contract_id: str,
    underlying_price: float,
    risk_free_rate: float = 0.05,
    db: Session = Depends(get_db)
):
    """Calculate and return Greeks for a contract"""
    import uuid
    
    contract = db.query(OptionsContractDB).filter(
        OptionsContractDB.id == contract_id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Calculate time to expiry in years
    T = (contract.expiry_date - datetime.utcnow()).total_seconds() / (365.25 * 24 * 3600)
    if T <= 0:
        raise HTTPException(status_code=400, detail="Contract has expired")
    
    S = underlying_price
    K = float(contract.strike_price)
    r = risk_free_rate
    sigma = float(contract.implied_volatility) if contract.implied_volatility > 0 else 0.3
    
    # Calculate Greeks
    delta = calculate_delta(S, K, T, r, sigma, contract.option_type)
    gamma = calculate_gamma(S, K, T, r, sigma)
    theta = calculate_theta(S, K, T, r, sigma, contract.option_type)
    vega = calculate_vega(S, K, T, r, sigma)
    rho = calculate_rho(S, K, T, r, sigma, contract.option_type)
    
    # Store Greeks in database
    greeks_id = str(uuid.uuid4())
    greeks_data = GreeksDataDB(
        id=greeks_id,
        contract_id=contract_id,
        timestamp=datetime.utcnow(),
        delta=Decimal(str(delta)),
        gamma=Decimal(str(gamma)),
        theta=Decimal(str(theta)),
        vega=Decimal(str(vega)),
        rho=Decimal(str(rho)),
        underlying_price=Decimal(str(underlying_price)),
        created_at=datetime.utcnow()
    )
    
    db.add(greeks_data)
    db.commit()
    
    return GreeksResponse(
        contract_id=contract_id,
        delta=Decimal(str(delta)),
        gamma=Decimal(str(gamma)),
        theta=Decimal(str(theta)),
        vega=Decimal(str(vega)),
        rho=Decimal(str(rho)),
        underlying_price=Decimal(str(underlying_price)),
        timestamp=datetime.utcnow()
    )

@app.get("/admin/options/statistics", response_model=OptionsStatistics)
async def get_options_statistics(db: Session = Depends(get_db)):
    """Get options platform statistics"""
    total_contracts = db.query(OptionsContractDB).count()
    active_contracts = db.query(OptionsContractDB).filter(
        OptionsContractDB.status == "active"
    ).count()
    
    # Calculate total open interest
    contracts = db.query(OptionsContractDB).filter(
        OptionsContractDB.status == "active"
    ).all()
    total_open_interest = sum(c.open_interest for c in contracts)
    
    # Calculate 24h volume
    total_volume_24h = sum(c.volume_24h for c in contracts)
    
    # Calculate total premium collected
    total_premium = sum(c.premium * c.open_interest for c in contracts)
    
    # Count pending settlements
    pending_settlements = db.query(SettlementHistoryDB).filter(
        SettlementHistoryDB.status == "pending"
    ).count()
    
    return OptionsStatistics(
        total_contracts=total_contracts,
        active_contracts=active_contracts,
        total_open_interest=total_open_interest,
        total_volume_24h=Decimal(str(total_volume_24h)),
        total_premium_collected=Decimal(str(total_premium)),
        pending_settlements=pending_settlements
    )

@app.post("/admin/options/settle/{contract_id}")
async def settle_contract(
    contract_id: str,
    settlement_price: Decimal,
    db: Session = Depends(get_db)
):
    """Settle an expired options contract"""
    import uuid
    
    contract = db.query(OptionsContractDB).filter(
        OptionsContractDB.id == contract_id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if contract.expiry_date > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Contract has not expired yet")
    
    # Calculate total payout
    if contract.option_type == "call":
        payout_per_contract = max(0, settlement_price - contract.strike_price)
    else:  # put
        payout_per_contract = max(0, contract.strike_price - settlement_price)
    
    total_payout = payout_per_contract * contract.open_interest * contract.contract_size
    
    # Create settlement record
    settlement_id = str(uuid.uuid4())
    settlement = SettlementHistoryDB(
        id=settlement_id,
        contract_id=contract_id,
        settlement_date=datetime.utcnow(),
        settlement_price=settlement_price,
        total_contracts=contract.open_interest,
        total_payout=total_payout,
        status="completed",
        created_at=datetime.utcnow()
    )
    
    db.add(settlement)
    
    # Update contract status
    contract.status = "settled"
    contract.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Settled contract: {contract.symbol}, Total payout: {total_payout}")
    
    return {
        "message": "Contract settled successfully",
        "settlement_id": settlement_id,
        "total_payout": float(total_payout)
    }

@app.get("/admin/options/volatility-surface/{underlying_asset}")
async def get_volatility_surface(
    underlying_asset: str,
    db: Session = Depends(get_db)
):
    """Get volatility surface for an underlying asset"""
    surface_data = db.query(VolatilitySurfaceDB).filter(
        VolatilitySurfaceDB.underlying_asset == underlying_asset
    ).order_by(
        VolatilitySurfaceDB.days_to_expiry,
        VolatilitySurfaceDB.strike_price
    ).all()
    
    return [{
        "strike_price": float(data.strike_price),
        "days_to_expiry": data.days_to_expiry,
        "implied_volatility": float(data.implied_volatility),
        "timestamp": data.timestamp.isoformat()
    } for data in surface_data]

@app.get("/admin/options/positions")
async def list_options_positions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all options positions"""
    query = db.query(OptionsPositionDB)
    
    if status:
        query = query.filter(OptionsPositionDB.status == status)
    
    positions = query.order_by(OptionsPositionDB.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": pos.id,
        "user_id": pos.user_id,
        "contract_id": pos.contract_id,
        "position_type": pos.position_type,
        "quantity": float(pos.quantity),
        "entry_price": float(pos.entry_price),
        "current_price": float(pos.current_price),
        "unrealized_pnl": float(pos.unrealized_pnl),
        "margin_required": float(pos.margin_required),
        "status": pos.status,
        "created_at": pos.created_at.isoformat()
    } for pos in positions]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "options-trading-admin"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8114)