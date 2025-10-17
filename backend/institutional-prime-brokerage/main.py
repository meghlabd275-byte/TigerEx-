#!/usr/bin/env python3
"""
Institutional Prime Brokerage Service
Complete institutional trading services with prime brokerage, custody, and OTC desk
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
from decimal import Decimal
import numpy as np

# FastAPI app
app = FastAPI(
    title="TigerEx Institutional Prime Brokerage",
    description="Complete institutional trading services with prime brokerage, custody, and OTC desk",
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

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_institutional")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class InstitutionalClient(Base):
    __tablename__ = "institutional_clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Client information
    company_name = Column(String, nullable=False)
    legal_entity_type = Column(String, nullable=False)  # corporation, fund, bank, etc.
    registration_number = Column(String, unique=True)
    jurisdiction = Column(String, nullable=False)
    
    # Contact information
    primary_contact_name = Column(String, nullable=False)
    primary_contact_email = Column(String, nullable=False)
    primary_contact_phone = Column(String)
    
    # Account details
    account_type = Column(String, default="prime_brokerage")  # prime_brokerage, custody, otc
    tier = Column(String, default="standard")  # standard, premium, elite
    status = Column(String, default="pending")  # pending, active, suspended, closed
    
    # Financial information
    aum = Column(Float, default=0.0)  # Assets Under Management
    credit_limit = Column(Float, default=0.0)
    margin_requirement = Column(Float, default=0.2)  # 20% default
    
    # Risk management
    risk_profile = Column(String, default="medium")  # low, medium, high
    max_position_size = Column(Float, default=1000000.0)
    max_daily_volume = Column(Float, default=10000000.0)
    
    # Compliance
    kyc_status = Column(String, default="pending")  # pending, approved, rejected
    aml_status = Column(String, default="pending")
    compliance_documents = Column(JSON)
    
    # Services
    enabled_services = Column(JSON, default=list)  # List of enabled services
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PrimeBrokerageAccount(Base):
    __tablename__ = "prime_brokerage_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # Account details
    account_number = Column(String, unique=True, nullable=False)
    base_currency = Column(String, default="USD")
    
    # Balances
    cash_balance = Column(Float, default=0.0)
    margin_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    
    # Credit facilities
    credit_line = Column(Float, default=0.0)
    used_credit = Column(Float, default=0.0)
    available_credit = Column(Float, default=0.0)
    
    # Risk metrics
    portfolio_value = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    margin_utilization = Column(Float, default=0.0)
    
    # Performance
    total_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OTCTrade(Base):
    __tablename__ = "otc_trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # Trade details
    trade_type = Column(String, nullable=False)  # spot, forward, swap, option
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Execution details
    execution_method = Column(String, default="rfs")  # rfs, streaming, algo
    settlement_date = Column(DateTime)
    settlement_method = Column(String, default="dvp")  # dvp, fop, cash
    
    # Counterparty
    counterparty = Column(String, default="tigerex")
    
    # Status
    status = Column(String, default="pending")  # pending, executed, settled, cancelled
    
    # Fees and costs
    commission = Column(Float, default=0.0)
    spread = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Risk
    var_impact = Column(Float, default=0.0)
    credit_impact = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    settled_at = Column(DateTime)

class CustodyHolding(Base):
    __tablename__ = "custody_holdings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # Asset details
    asset_type = Column(String, nullable=False)  # crypto, fiat, security
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    
    # Custody details
    custody_type = Column(String, default="segregated")  # segregated, omnibus
    storage_method = Column(String, default="cold")  # cold, hot, warm
    
    # Valuation
    market_value = Column(Float, default=0.0)
    cost_basis = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    
    # Security
    wallet_address = Column(String)
    multisig_threshold = Column(Integer, default=3)
    insurance_coverage = Column(Float, default=0.0)
    
    # Restrictions
    is_restricted = Column(Boolean, default=False)
    restriction_reason = Column(String)
    
    last_updated = Column(DateTime, default=datetime.utcnow)

class RFQRequest(Base):
    __tablename__ = "rfq_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # RFQ details
    instrument = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    
    # Timing
    valid_until = Column(DateTime, nullable=False)
    settlement_date = Column(DateTime)
    
    # Requirements
    min_quantity = Column(Float)
    max_quantity = Column(Float)
    price_type = Column(String, default="market")  # market, limit, stop
    limit_price = Column(Float)
    
    # Status
    status = Column(String, default="active")  # active, filled, expired, cancelled
    
    # Responses
    best_bid = Column(Float)
    best_offer = Column(Float)
    response_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class PrimeBrokerageReport(Base):
    __tablename__ = "prime_brokerage_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # Report details
    report_type = Column(String, nullable=False)  # daily, weekly, monthly, custom
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    
    # Content
    report_data = Column(JSON)
    
    # Delivery
    delivery_method = Column(String, default="email")  # email, api, portal
    delivered_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CreditFacility(Base):
    __tablename__ = "credit_facilities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, nullable=False)
    
    # Facility details
    facility_type = Column(String, nullable=False)  # revolving, term, repo
    currency = Column(String, default="USD")
    limit_amount = Column(Float, nullable=False)
    
    # Terms
    interest_rate = Column(Float, nullable=False)
    margin_rate = Column(Float, default=0.0)
    maturity_date = Column(DateTime)
    
    # Collateral
    collateral_requirement = Column(Float, default=1.0)  # 100% default
    eligible_collateral = Column(JSON)
    
    # Usage
    outstanding_amount = Column(Float, default=0.0)
    available_amount = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="active")  # active, suspended, expired
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class InstitutionalClientCreate(BaseModel):
    company_name: str
    legal_entity_type: str
    registration_number: str
    jurisdiction: str
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: Optional[str] = None
    account_type: str = "prime_brokerage"
    aum: float = 0.0

class OTCTradeRequest(BaseModel):
    client_id: str
    trade_type: str
    symbol: str
    side: str
    quantity: float
    price: Optional[float] = None
    execution_method: str = "rfs"
    settlement_date: Optional[datetime] = None

class RFQCreate(BaseModel):
    client_id: str
    instrument: str
    side: str
    quantity: float
    valid_until: datetime
    settlement_date: Optional[datetime] = None
    price_type: str = "market"
    limit_price: Optional[float] = None

class CustodyTransfer(BaseModel):
    client_id: str
    asset_type: str
    symbol: str
    quantity: float
    transfer_type: str  # deposit, withdrawal
    destination_address: Optional[str] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

def calculate_portfolio_metrics(client_id: str, db: Session) -> Dict[str, float]:
    """Calculate comprehensive portfolio metrics"""
    # Get holdings
    holdings = db.query(CustodyHolding).filter(CustodyHolding.client_id == client_id).all()
    
    if not holdings:
        return {
            "total_value": 0.0,
            "total_pnl": 0.0,
            "asset_allocation": {},
            "concentration_risk": 0.0
        }
    
    total_value = sum(holding.market_value for holding in holdings)
    total_pnl = sum(holding.unrealized_pnl for holding in holdings)
    
    # Asset allocation
    asset_allocation = {}
    for holding in holdings:
        if holding.asset_type not in asset_allocation:
            asset_allocation[holding.asset_type] = 0.0
        asset_allocation[holding.asset_type] += holding.market_value
    
    # Convert to percentages
    if total_value > 0:
        asset_allocation = {k: (v / total_value) * 100 for k, v in asset_allocation.items()}
    
    # Concentration risk (largest single position as % of portfolio)
    concentration_risk = max((holding.market_value / total_value) * 100 for holding in holdings) if total_value > 0 else 0
    
    return {
        "total_value": total_value,
        "total_pnl": total_pnl,
        "asset_allocation": asset_allocation,
        "concentration_risk": concentration_risk
    }

def calculate_risk_metrics(client_id: str, db: Session) -> Dict[str, float]:
    """Calculate risk metrics for client"""
    # Mock risk calculations - integrate with actual risk engine
    return {
        "var_1d": np.random.uniform(50000, 200000),
        "var_10d": np.random.uniform(150000, 600000),
        "expected_shortfall": np.random.uniform(75000, 300000),
        "beta": np.random.uniform(0.8, 1.2),
        "correlation": np.random.uniform(0.3, 0.8),
        "volatility": np.random.uniform(0.15, 0.35)
    }

def generate_account_number() -> str:
    """Generate unique account number"""
    return f"PB{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

async def execute_otc_trade(trade: OTCTrade, db: Session) -> Dict[str, Any]:
    """Execute OTC trade"""
    try:
        # Mock execution logic
        execution_price = trade.price * (1 + np.random.uniform(-0.001, 0.001))  # Small price improvement/slippage
        
        # Update trade
        trade.status = "executed"
        trade.executed_at = datetime.utcnow()
        trade.price = execution_price
        
        # Calculate costs
        notional = trade.quantity * execution_price
        trade.commission = notional * 0.001  # 0.1% commission
        trade.spread = abs(execution_price - trade.price) * trade.quantity
        trade.total_cost = trade.commission + trade.spread
        
        db.commit()
        
        return {
            "status": "executed",
            "execution_price": execution_price,
            "total_cost": trade.total_cost,
            "execution_time": trade.executed_at
        }
    except Exception as e:
        logger.error(f"Error executing OTC trade: {e}")
        trade.status = "failed"
        db.commit()
        raise

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "institutional-prime-brokerage"}

# Client management
@app.post("/clients")
async def create_institutional_client(
    client: InstitutionalClientCreate,
    db: Session = Depends(get_db)
):
    """Create new institutional client"""
    # Check if client already exists
    existing = db.query(InstitutionalClient).filter(
        InstitutionalClient.registration_number == client.registration_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Client already exists")
    
    # Create client
    db_client = InstitutionalClient(
        **client.dict(),
        enabled_services=["prime_brokerage", "custody", "otc", "reporting"]
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Create prime brokerage account
    account_number = generate_account_number()
    pb_account = PrimeBrokerageAccount(
        client_id=db_client.id,
        account_number=account_number,
        credit_line=client.aum * 0.5,  # 50% of AUM as initial credit line
        available_credit=client.aum * 0.5
    )
    db.add(pb_account)
    db.commit()
    
    return {
        "client": db_client,
        "account": pb_account
    }

@app.get("/clients/{client_id}")
async def get_client(client_id: str, db: Session = Depends(get_db)):
    """Get client details"""
    client = db.query(InstitutionalClient).filter(InstitutionalClient.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get associated accounts
    accounts = db.query(PrimeBrokerageAccount).filter(
        PrimeBrokerageAccount.client_id == client_id
    ).all()
    
    # Calculate portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(client_id, db)
    risk_metrics = calculate_risk_metrics(client_id, db)
    
    return {
        "client": client,
        "accounts": accounts,
        "portfolio_metrics": portfolio_metrics,
        "risk_metrics": risk_metrics
    }

@app.get("/clients")
async def get_clients(
    status: Optional[str] = None,
    tier: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get institutional clients"""
    query = db.query(InstitutionalClient)
    
    if status:
        query = query.filter(InstitutionalClient.status == status)
    if tier:
        query = query.filter(InstitutionalClient.tier == tier)
    
    clients = query.offset(skip).limit(limit).all()
    return clients

# Prime brokerage accounts
@app.get("/accounts/{client_id}")
async def get_client_accounts(client_id: str, db: Session = Depends(get_db)):
    """Get client's prime brokerage accounts"""
    accounts = db.query(PrimeBrokerageAccount).filter(
        PrimeBrokerageAccount.client_id == client_id
    ).all()
    
    return accounts

@app.get("/accounts/{account_id}/positions")
async def get_account_positions(account_id: str, db: Session = Depends(get_db)):
    """Get account positions"""
    account = db.query(PrimeBrokerageAccount).filter(
        PrimeBrokerageAccount.id == account_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get custody holdings for this client
    holdings = db.query(CustodyHolding).filter(
        CustodyHolding.client_id == account.client_id
    ).all()
    
    return holdings

# OTC Trading
@app.post("/otc/trade")
async def create_otc_trade(
    trade_request: OTCTradeRequest,
    db: Session = Depends(get_db)
):
    """Create OTC trade"""
    # Validate client
    client = db.query(InstitutionalClient).filter(
        InstitutionalClient.id == trade_request.client_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if "otc" not in client.enabled_services:
        raise HTTPException(status_code=403, detail="OTC trading not enabled for client")
    
    # Create trade
    db_trade = OTCTrade(
        **trade_request.dict(),
        settlement_date=trade_request.settlement_date or datetime.utcnow() + timedelta(days=2)
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    # Execute trade if price is provided
    if trade_request.price:
        execution_result = await execute_otc_trade(db_trade, db)
        return {
            "trade": db_trade,
            "execution": execution_result
        }
    
    return {"trade": db_trade}

@app.get("/otc/trades/{client_id}")
async def get_otc_trades(
    client_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get client's OTC trades"""
    query = db.query(OTCTrade).filter(OTCTrade.client_id == client_id)
    
    if status:
        query = query.filter(OTCTrade.status == status)
    
    trades = query.order_by(OTCTrade.created_at.desc()).limit(limit).all()
    return trades

# RFQ System
@app.post("/rfq")
async def create_rfq(rfq: RFQCreate, db: Session = Depends(get_db)):
    """Create RFQ request"""
    db_rfq = RFQRequest(
        **rfq.dict(),
        expires_at=rfq.valid_until
    )
    db.add(db_rfq)
    db.commit()
    db.refresh(db_rfq)
    
    # Mock market maker responses
    await asyncio.sleep(1)  # Simulate response time
    
    # Generate mock quotes
    base_price = np.random.uniform(100, 1000)
    spread = base_price * 0.001  # 0.1% spread
    
    db_rfq.best_bid = base_price - spread/2
    db_rfq.best_offer = base_price + spread/2
    db_rfq.response_count = np.random.randint(3, 8)
    
    db.commit()
    
    return db_rfq

@app.get("/rfq/{rfq_id}")
async def get_rfq(rfq_id: str, db: Session = Depends(get_db)):
    """Get RFQ details"""
    rfq = db.query(RFQRequest).filter(RFQRequest.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    return rfq

@app.post("/rfq/{rfq_id}/accept")
async def accept_rfq_quote(
    rfq_id: str,
    side: str,  # bid or offer
    db: Session = Depends(get_db)
):
    """Accept RFQ quote and create trade"""
    rfq = db.query(RFQRequest).filter(RFQRequest.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    if rfq.status != "active":
        raise HTTPException(status_code=400, detail="RFQ not active")
    
    if datetime.utcnow() > rfq.expires_at:
        raise HTTPException(status_code=400, detail="RFQ expired")
    
    # Create trade from RFQ
    price = rfq.best_bid if side == "bid" else rfq.best_offer
    trade_side = "sell" if side == "bid" else "buy"
    
    trade = OTCTrade(
        client_id=rfq.client_id,
        trade_type="spot",
        symbol=rfq.instrument,
        side=trade_side,
        quantity=rfq.quantity,
        price=price,
        execution_method="rfq"
    )
    
    db.add(trade)
    
    # Update RFQ status
    rfq.status = "filled"
    
    db.commit()
    
    # Execute trade
    execution_result = await execute_otc_trade(trade, db)
    
    return {
        "rfq": rfq,
        "trade": trade,
        "execution": execution_result
    }

# Custody Services
@app.post("/custody/transfer")
async def custody_transfer(
    transfer: CustodyTransfer,
    db: Session = Depends(get_db)
):
    """Process custody transfer"""
    client = db.query(InstitutionalClient).filter(
        InstitutionalClient.id == transfer.client_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if "custody" not in client.enabled_services:
        raise HTTPException(status_code=403, detail="Custody services not enabled")
    
    # Get or create holding
    holding = db.query(CustodyHolding).filter(
        CustodyHolding.client_id == transfer.client_id,
        CustodyHolding.symbol == transfer.symbol
    ).first()
    
    if transfer.transfer_type == "deposit":
        if holding:
            holding.quantity += transfer.quantity
        else:
            holding = CustodyHolding(
                client_id=transfer.client_id,
                asset_type=transfer.asset_type,
                symbol=transfer.symbol,
                quantity=transfer.quantity,
                market_value=transfer.quantity * 100,  # Mock price
                wallet_address=f"0x{uuid.uuid4().hex[:40]}"
            )
            db.add(holding)
    
    elif transfer.transfer_type == "withdrawal":
        if not holding or holding.quantity < transfer.quantity:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        holding.quantity -= transfer.quantity
        
        if holding.quantity == 0:
            db.delete(holding)
    
    db.commit()
    
    return {
        "status": "completed",
        "transfer_type": transfer.transfer_type,
        "quantity": transfer.quantity,
        "remaining_balance": holding.quantity if holding else 0
    }

@app.get("/custody/holdings/{client_id}")
async def get_custody_holdings(client_id: str, db: Session = Depends(get_db)):
    """Get client's custody holdings"""
    holdings = db.query(CustodyHolding).filter(
        CustodyHolding.client_id == client_id
    ).all()
    
    # Calculate total values
    total_value = sum(holding.market_value for holding in holdings)
    total_pnl = sum(holding.unrealized_pnl for holding in holdings)
    
    return {
        "holdings": holdings,
        "summary": {
            "total_positions": len(holdings),
            "total_value": total_value,
            "total_pnl": total_pnl
        }
    }

# Credit Facilities
@app.post("/credit/facility")
async def create_credit_facility(
    client_id: str,
    facility_type: str,
    currency: str,
    limit_amount: float,
    interest_rate: float,
    maturity_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Create credit facility"""
    client = db.query(InstitutionalClient).filter(
        InstitutionalClient.id == client_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    facility = CreditFacility(
        client_id=client_id,
        facility_type=facility_type,
        currency=currency,
        limit_amount=limit_amount,
        interest_rate=interest_rate,
        available_amount=limit_amount,
        maturity_date=maturity_date or datetime.utcnow() + timedelta(days=365),
        eligible_collateral=["BTC", "ETH", "USDT", "USDC"],
        expires_at=maturity_date or datetime.utcnow() + timedelta(days=365)
    )
    
    db.add(facility)
    db.commit()
    db.refresh(facility)
    
    return facility

@app.get("/credit/facilities/{client_id}")
async def get_credit_facilities(client_id: str, db: Session = Depends(get_db)):
    """Get client's credit facilities"""
    facilities = db.query(CreditFacility).filter(
        CreditFacility.client_id == client_id
    ).all()
    
    return facilities

# Reporting
@app.post("/reports/generate")
async def generate_report(
    client_id: str,
    report_type: str,
    period_start: datetime,
    period_end: datetime,
    db: Session = Depends(get_db)
):
    """Generate client report"""
    client = db.query(InstitutionalClient).filter(
        InstitutionalClient.id == client_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate report data
    report_data = {
        "client_info": {
            "name": client.company_name,
            "account_number": "PB123456789",  # Mock
            "report_period": f"{period_start.date()} to {period_end.date()}"
        },
        "portfolio_summary": calculate_portfolio_metrics(client_id, db),
        "risk_metrics": calculate_risk_metrics(client_id, db),
        "transactions": [],  # Would include actual transaction data
        "performance": {
            "total_return": np.random.uniform(-5, 15),
            "benchmark_return": np.random.uniform(-3, 12),
            "alpha": np.random.uniform(-2, 3),
            "tracking_error": np.random.uniform(1, 5)
        }
    }
    
    # Save report
    report = PrimeBrokerageReport(
        client_id=client_id,
        report_type=report_type,
        report_period_start=period_start,
        report_period_end=period_end,
        report_data=report_data,
        delivered_at=datetime.utcnow()
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report

@app.get("/reports/{client_id}")
async def get_client_reports(
    client_id: str,
    report_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get client reports"""
    query = db.query(PrimeBrokerageReport).filter(
        PrimeBrokerageReport.client_id == client_id
    )
    
    if report_type:
        query = query.filter(PrimeBrokerageReport.report_type == report_type)
    
    reports = query.order_by(PrimeBrokerageReport.created_at.desc()).limit(limit).all()
    return reports

# Analytics
@app.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get institutional services analytics overview"""
    # Client metrics
    total_clients = db.query(InstitutionalClient).count()
    active_clients = db.query(InstitutionalClient).filter(
        InstitutionalClient.status == "active"
    ).count()
    
    # AUM metrics
    clients = db.query(InstitutionalClient).all()
    total_aum = sum(client.aum for client in clients)
    
    # Trade metrics
    total_otc_trades = db.query(OTCTrade).count()
    otc_volume_30d = db.query(OTCTrade).filter(
        OTCTrade.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Holdings metrics
    total_holdings = db.query(CustodyHolding).count()
    custody_holdings = db.query(CustodyHolding).all()
    total_custody_value = sum(holding.market_value for holding in custody_holdings)
    
    return {
        "clients": {
            "total": total_clients,
            "active": active_clients,
            "activation_rate": (active_clients / total_clients * 100) if total_clients > 0 else 0
        },
        "aum": {
            "total": total_aum,
            "average_per_client": total_aum / total_clients if total_clients > 0 else 0
        },
        "trading": {
            "total_otc_trades": total_otc_trades,
            "otc_volume_30d": otc_volume_30d
        },
        "custody": {
            "total_positions": total_holdings,
            "total_value": total_custody_value
        }
    }

@app.get("/analytics/client/{client_id}")
async def get_client_analytics(client_id: str, db: Session = Depends(get_db)):
    """Get detailed client analytics"""
    client = db.query(InstitutionalClient).filter(
        InstitutionalClient.id == client_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Trading activity
    trades_30d = db.query(OTCTrade).filter(
        OTCTrade.client_id == client_id,
        OTCTrade.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(client_id, db)
    risk_metrics = calculate_risk_metrics(client_id, db)
    
    # Credit utilization
    credit_facilities = db.query(CreditFacility).filter(
        CreditFacility.client_id == client_id
    ).all()
    
    total_credit_limit = sum(facility.limit_amount for facility in credit_facilities)
    total_credit_used = sum(facility.outstanding_amount for facility in credit_facilities)
    credit_utilization = (total_credit_used / total_credit_limit * 100) if total_credit_limit > 0 else 0
    
    return {
        "client": client,
        "trading_activity": {
            "trades_30d": trades_30d,
            "avg_trade_size": portfolio_metrics["total_value"] / trades_30d if trades_30d > 0 else 0
        },
        "portfolio": portfolio_metrics,
        "risk": risk_metrics,
        "credit": {
            "total_limit": total_credit_limit,
            "total_used": total_credit_used,
            "utilization_percentage": credit_utilization,
            "available": total_credit_limit - total_credit_used
        }
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Institutional Prime Brokerage service started")
    
    # Start background tasks
    asyncio.create_task(periodic_risk_monitoring())
    asyncio.create_task(periodic_reporting())

async def periodic_risk_monitoring():
    """Monitor client risk metrics"""
    while True:
        try:
            db = SessionLocal()
            
            # Get active clients
            clients = db.query(InstitutionalClient).filter(
                InstitutionalClient.status == "active"
            ).all()
            
            for client in clients:
                # Calculate risk metrics
                risk_metrics = calculate_risk_metrics(client.id, db)
                
                # Check risk limits
                if risk_metrics["var_1d"] > client.max_position_size * 0.1:  # 10% of max position
                    logger.warning(f"High VaR detected for client {client.id}")
                    # Send alert
            
            db.close()
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Error in risk monitoring: {e}")
            await asyncio.sleep(300)

async def periodic_reporting():
    """Generate periodic reports"""
    while True:
        try:
            db = SessionLocal()
            
            # Generate daily reports for clients
            clients = db.query(InstitutionalClient).filter(
                InstitutionalClient.status == "active"
            ).all()
            
            for client in clients:
                if "reporting" in client.enabled_services:
                    # Generate daily report
                    period_end = datetime.utcnow()
                    period_start = period_end - timedelta(days=1)
                    
                    # This would generate and send the actual report
                    logger.info(f"Generated daily report for client {client.id}")
            
            db.close()
            await asyncio.sleep(86400)  # Generate daily
            
        except Exception as e:
            logger.error(f"Error in periodic reporting: {e}")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)