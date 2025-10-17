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
TigerEx Payment Gateway Admin Panel
Manages payment providers, transactions, and fiat on/off ramps
Port: 8122
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

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_payment_gateway"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProviderType(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    BNPL = "bnpl"  # Buy Now Pay Later

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class PaymentProvider(Base):
    __tablename__ = "payment_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    provider_type = Column(String)
    api_endpoint = Column(String)
    api_key_encrypted = Column(String)
    is_enabled = Column(Boolean, default=True)
    status = Column(String, default="active")
    
    # Supported features
    supports_deposits = Column(Boolean, default=True)
    supports_withdrawals = Column(Boolean, default=True)
    supports_refunds = Column(Boolean, default=True)
    
    # Limits
    min_transaction_amount = Column(Float, default=10.0)
    max_transaction_amount = Column(Float, default=50000.0)
    daily_limit = Column(Float, default=100000.0)
    
    # Fees
    deposit_fee_percentage = Column(Float, default=2.5)
    withdrawal_fee_percentage = Column(Float, default=1.0)
    fixed_fee = Column(Float, default=0.0)
    
    # Stats
    total_transactions = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    avg_processing_time = Column(Float, default=0.0)
    
    # Supported currencies and countries
    supported_currencies = Column(JSON)
    supported_countries = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    transaction_type = Column(String)  # deposit, withdrawal
    amount = Column(Float)
    currency = Column(String)
    fee = Column(Float)
    net_amount = Column(Float)
    status = Column(String, default="pending")
    payment_method = Column(String)
    external_transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class FiatOnRamp(Base):
    __tablename__ = "fiat_onramps"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    fiat_amount = Column(Float)
    fiat_currency = Column(String)
    crypto_amount = Column(Float)
    crypto_currency = Column(String)
    exchange_rate = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class FiatOffRamp(Base):
    __tablename__ = "fiat_offramps"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    crypto_amount = Column(Float)
    crypto_currency = Column(String)
    fiat_amount = Column(Float)
    fiat_currency = Column(String)
    exchange_rate = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

class PaymentProviderCreate(BaseModel):
    name: str
    provider_type: ProviderType
    api_endpoint: str
    api_key_encrypted: str
    supports_deposits: bool = True
    supports_withdrawals: bool = True
    supports_refunds: bool = True
    min_transaction_amount: float = Field(ge=0, default=10.0)
    max_transaction_amount: float = Field(ge=0, default=50000.0)
    daily_limit: float = Field(ge=0, default=100000.0)
    deposit_fee_percentage: float = Field(ge=0, le=10, default=2.5)
    withdrawal_fee_percentage: float = Field(ge=0, le=10, default=1.0)
    fixed_fee: float = Field(ge=0, default=0.0)
    supported_currencies: List[str] = []
    supported_countries: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

class PaymentProviderUpdate(BaseModel):
    api_endpoint: Optional[str] = None
    is_enabled: Optional[bool] = None
    status: Optional[ProviderStatus] = None
    min_transaction_amount: Optional[float] = None
    max_transaction_amount: Optional[float] = None
    daily_limit: Optional[float] = None
    deposit_fee_percentage: Optional[float] = None
    withdrawal_fee_percentage: Optional[float] = None
    fixed_fee: Optional[float] = None
    supported_currencies: Optional[List[str]] = None
    supported_countries: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="TigerEx Payment Gateway Admin API", version="1.0.0")

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

@app.post("/api/admin/providers", status_code=201)
async def create_provider(provider: PaymentProviderCreate, db: Session = Depends(get_db)):
    """Create a new payment provider"""
    try:
        existing = db.query(PaymentProvider).filter(PaymentProvider.name == provider.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Provider already exists")
        
        db_provider = PaymentProvider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        
        logger.info(f"Created payment provider: {provider.name}")
        return db_provider
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/providers")
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    provider_type: Optional[ProviderType] = None,
    is_enabled: Optional[bool] = None,
    status: Optional[ProviderStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all payment providers"""
    try:
        query = db.query(PaymentProvider)
        
        if provider_type:
            query = query.filter(PaymentProvider.provider_type == provider_type)
        if is_enabled is not None:
            query = query.filter(PaymentProvider.is_enabled == is_enabled)
        if status:
            query = query.filter(PaymentProvider.status == status)
        
        total = query.count()
        providers = query.order_by(PaymentProvider.total_volume.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "providers": providers}
    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/providers/{provider_id}")
async def update_provider(
    provider_id: int,
    provider_update: PaymentProviderUpdate,
    db: Session = Depends(get_db)
):
    """Update a payment provider"""
    try:
        provider = db.query(PaymentProvider).filter(PaymentProvider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        update_data = provider_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        provider.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(provider)
        
        logger.info(f"Updated provider: {provider_id}")
        return provider
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/transactions")
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    provider_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all payment transactions"""
    try:
        query = db.query(PaymentTransaction)
        
        if provider_id:
            query = query.filter(PaymentTransaction.provider_id == provider_id)
        if transaction_type:
            query = query.filter(PaymentTransaction.transaction_type == transaction_type)
        if status:
            query = query.filter(PaymentTransaction.status == status)
        
        total = query.count()
        transactions = query.order_by(PaymentTransaction.created_at.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "transactions": transactions}
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get payment gateway analytics"""
    try:
        total_providers = db.query(PaymentProvider).count()
        active_providers = db.query(PaymentProvider).filter(
            PaymentProvider.is_enabled == True,
            PaymentProvider.status == "active"
        ).count()
        total_transactions = db.query(PaymentTransaction).count()
        total_volume = db.query(PaymentProvider).with_entities(
            db.func.sum(PaymentProvider.total_volume)
        ).scalar() or 0.0
        avg_success_rate = db.query(PaymentProvider).filter(
            PaymentProvider.is_enabled == True
        ).with_entities(db.func.avg(PaymentProvider.success_rate)).scalar() or 0.0
        
        return {
            "total_providers": total_providers,
            "active_providers": active_providers,
            "total_transactions": total_transactions,
            "total_volume": total_volume,
            "avg_success_rate": avg_success_rate
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-gateway-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8122)