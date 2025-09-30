"""
TigerEx Institutional Services Admin Panel
Manages institutional clients, OTC trading, and custody services
Port: 8120
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_institutional"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ClientTier(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    VIP = "vip"

class ClientStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"

class InstitutionalClient(Base):
    __tablename__ = "institutional_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    legal_entity = Column(String)
    registration_number = Column(String)
    country = Column(String)
    tier = Column(String, default="standard")
    status = Column(String, default="pending")
    
    # Contact info
    primary_contact_name = Column(String)
    primary_contact_email = Column(String)
    primary_contact_phone = Column(String)
    
    # Trading limits
    daily_trading_limit = Column(Float, default=0.0)
    monthly_trading_limit = Column(Float, default=0.0)
    otc_min_trade_size = Column(Float, default=100000.0)
    
    # Fees
    trading_fee_percentage = Column(Float, default=0.1)
    custody_fee_percentage = Column(Float, default=0.05)
    
    # Stats
    total_trading_volume = Column(Float, default=0.0)
    total_custody_aum = Column(Float, default=0.0)
    total_otc_trades = Column(Integer, default=0)
    
    # Verification
    kyc_verified = Column(Boolean, default=False)
    aml_verified = Column(Boolean, default=False)
    
    onboarded_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class OTCTrade(Base):
    __tablename__ = "otc_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, index=True)
    trade_type = Column(String)  # buy, sell
    base_currency = Column(String)
    quote_currency = Column(String)
    amount = Column(Float)
    price = Column(Float)
    total_value = Column(Float)
    status = Column(String, default="pending")
    settlement_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class CustodyAccount(Base):
    __tablename__ = "custody_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, index=True)
    account_number = Column(String, unique=True, index=True)
    account_type = Column(String)  # hot, cold, warm
    total_value_usd = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

class InstitutionalClientCreate(BaseModel):
    company_name: str
    legal_entity: str
    registration_number: str
    country: str
    tier: ClientTier = ClientTier.STANDARD
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: str
    daily_trading_limit: float = Field(ge=0, default=0.0)
    monthly_trading_limit: float = Field(ge=0, default=0.0)
    otc_min_trade_size: float = Field(ge=0, default=100000.0)
    trading_fee_percentage: float = Field(ge=0, le=1, default=0.1)
    custody_fee_percentage: float = Field(ge=0, le=1, default=0.05)
    metadata: Optional[Dict[str, Any]] = None

class InstitutionalClientUpdate(BaseModel):
    tier: Optional[ClientTier] = None
    status: Optional[ClientStatus] = None
    daily_trading_limit: Optional[float] = None
    monthly_trading_limit: Optional[float] = None
    trading_fee_percentage: Optional[float] = None
    custody_fee_percentage: Optional[float] = None
    kyc_verified: Optional[bool] = None
    aml_verified: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="TigerEx Institutional Services Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/admin/clients", status_code=201)
async def create_client(client: InstitutionalClientCreate, db: Session = Depends(get_db)):
    """Create a new institutional client"""
    try:
        existing = db.query(InstitutionalClient).filter(
            InstitutionalClient.company_name == client.company_name
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Client already exists")
        
        db_client = InstitutionalClient(**client.dict())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        logger.info(f"Created institutional client: {client.company_name}")
        return db_client
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/clients")
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    tier: Optional[ClientTier] = None,
    status: Optional[ClientStatus] = None,
    kyc_verified: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all institutional clients"""
    try:
        query = db.query(InstitutionalClient)
        
        if tier:
            query = query.filter(InstitutionalClient.tier == tier)
        if status:
            query = query.filter(InstitutionalClient.status == status)
        if kyc_verified is not None:
            query = query.filter(InstitutionalClient.kyc_verified == kyc_verified)
        
        total = query.count()
        clients = query.order_by(InstitutionalClient.total_trading_volume.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "clients": clients}
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/clients/{client_id}")
async def update_client(
    client_id: int,
    client_update: InstitutionalClientUpdate,
    db: Session = Depends(get_db)
):
    """Update an institutional client"""
    try:
        client = db.query(InstitutionalClient).filter(InstitutionalClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        update_data = client_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        client.last_active = datetime.utcnow()
        db.commit()
        db.refresh(client)
        
        logger.info(f"Updated client: {client_id}")
        return client
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating client: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get institutional services analytics"""
    try:
        total_clients = db.query(InstitutionalClient).count()
        active_clients = db.query(InstitutionalClient).filter(
            InstitutionalClient.status == "active"
        ).count()
        total_trading_volume = db.query(InstitutionalClient).with_entities(
            db.func.sum(InstitutionalClient.total_trading_volume)
        ).scalar() or 0.0
        total_custody_aum = db.query(InstitutionalClient).with_entities(
            db.func.sum(InstitutionalClient.total_custody_aum)
        ).scalar() or 0.0
        total_otc_trades = db.query(OTCTrade).count()
        
        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_trading_volume": total_trading_volume,
            "total_custody_aum": total_custody_aum,
            "total_otc_trades": total_otc_trades
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "institutional-services-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8120)