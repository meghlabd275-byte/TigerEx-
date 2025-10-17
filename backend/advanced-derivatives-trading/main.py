#!/usr/bin/env python3
"""
Advanced Derivatives Trading Service
Exotic options, structured products, and advanced derivatives trading
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
import scipy.stats as stats
from scipy.optimize import minimize_scalar
import math

# FastAPI app
app = FastAPI(
    title="TigerEx Advanced Derivatives Trading",
    description="Exotic options, structured products, and advanced derivatives trading",
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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_derivatives")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class DerivativeProduct(Base):
    __tablename__ = "derivative_products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Product details
    product_type = Column(String, nullable=False)  # option, future, swap, structured_product
    product_subtype = Column(String, nullable=False)  # vanilla, barrier, asian, digital, etc.
    underlying_asset = Column(String, nullable=False)
    
    # Contract specifications
    contract_size = Column(Float, default=1.0)
    tick_size = Column(Float, default=0.01)
    min_quantity = Column(Float, default=1.0)
    max_quantity = Column(Float, default=1000000.0)
    
    # Trading details
    is_active = Column(Boolean, default=True)
    trading_hours = Column(JSON)
    settlement_method = Column(String, default="cash")  # cash, physical
    
    # Risk parameters
    initial_margin = Column(Float, default=0.1)
    maintenance_margin = Column(Float, default=0.05)
    max_leverage = Column(Float, default=10.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OptionContract(Base):
    __tablename__ = "option_contracts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic option details
    underlying = Column(String, nullable=False)
    option_type = Column(String, nullable=False)  # call, put
    style = Column(String, default="european")  # european, american, bermudan
    
    # Strike and expiry
    strike_price = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    
    # Exotic option parameters
    barrier_type = Column(String)  # up_and_in, up_and_out, down_and_in, down_and_out
    barrier_level = Column(Float)
    
    # Asian option parameters
    averaging_type = Column(String)  # arithmetic, geometric
    observation_dates = Column(JSON)
    
    # Digital option parameters
    payout_amount = Column(Float)
    
    # Pricing parameters
    current_price = Column(Float, default=0.0)
    implied_volatility = Column(Float, default=0.2)
    delta = Column(Float, default=0.0)
    gamma = Column(Float, default=0.0)
    theta = Column(Float, default=0.0)
    vega = Column(Float, default=0.0)
    rho = Column(Float, default=0.0)
    
    # Market data
    bid_price = Column(Float, default=0.0)
    ask_price = Column(Float, default=0.0)
    last_price = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)
    open_interest = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StructuredProduct(Base):
    __tablename__ = "structured_products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Product details
    product_name = Column(String, nullable=False)
    product_type = Column(String, nullable=False)  # autocall, reverse_convertible, barrier_reverse_convertible
    underlying_assets = Column(JSON, nullable=False)  # List of underlying assets
    
    # Terms
    issue_date = Column(DateTime, nullable=False)
    maturity_date = Column(DateTime, nullable=False)
    notional_amount = Column(Float, nullable=False)
    
    # Payoff structure
    coupon_rate = Column(Float, default=0.0)
    coupon_frequency = Column(String, default="quarterly")  # monthly, quarterly, semi_annual, annual
    barrier_level = Column(Float)
    knock_in_level = Column(Float)
    autocall_level = Column(Float)
    
    # Protection and participation
    capital_protection = Column(Float, default=0.0)  # 0-1, 1 = 100% protected
    participation_rate = Column(Float, default=1.0)
    
    # Pricing
    current_value = Column(Float, default=0.0)
    accrued_coupon = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="active")  # active, knocked_in, autocalled, matured
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DerivativeTrade(Base):
    __tablename__ = "derivative_trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Trade details
    product_id = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Order details
    order_type = Column(String, default="market")  # market, limit, stop
    time_in_force = Column(String, default="gtc")  # gtc, ioc, fok
    
    # Execution
    fill_price = Column(Float)
    fill_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    
    # Risk and margin
    initial_margin_required = Column(Float, default=0.0)
    maintenance_margin = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="pending")  # pending, filled, partially_filled, cancelled, expired
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime)
    expires_at = Column(DateTime)

class RiskMetrics(Base):
    __tablename__ = "risk_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Portfolio metrics
    portfolio_value = Column(Float, default=0.0)
    total_margin_used = Column(Float, default=0.0)
    available_margin = Column(Float, default=0.0)
    
    # Risk measures
    portfolio_delta = Column(Float, default=0.0)
    portfolio_gamma = Column(Float, default=0.0)
    portfolio_theta = Column(Float, default=0.0)
    portfolio_vega = Column(Float, default=0.0)
    portfolio_rho = Column(Float, default=0.0)
    
    # VaR calculations
    var_1d = Column(Float, default=0.0)
    var_10d = Column(Float, default=0.0)
    expected_shortfall = Column(Float, default=0.0)
    
    # Stress test results
    stress_test_results = Column(JSON)
    
    calculated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class OptionContractCreate(BaseModel):
    underlying: str
    option_type: str
    style: str = "european"
    strike_price: float
    expiry_date: datetime
    barrier_type: Optional[str] = None
    barrier_level: Optional[float] = None
    averaging_type: Optional[str] = None
    payout_amount: Optional[float] = None

class StructuredProductCreate(BaseModel):
    product_name: str
    product_type: str
    underlying_assets: List[str]
    issue_date: datetime
    maturity_date: datetime
    notional_amount: float
    coupon_rate: float = 0.0
    coupon_frequency: str = "quarterly"
    barrier_level: Optional[float] = None
    knock_in_level: Optional[float] = None
    autocall_level: Optional[float] = None
    capital_protection: float = 0.0
    participation_rate: float = 1.0

class DerivativeTradeCreate(BaseModel):
    product_id: str
    product_type: str
    side: str
    quantity: float
    price: Optional[float] = None
    order_type: str = "market"
    time_in_force: str = "gtc"

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

class OptionPricer:
    """Advanced option pricing models"""
    
    @staticmethod
    def black_scholes(S, K, T, r, sigma, option_type="call"):
        """Black-Scholes option pricing"""
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if option_type == "call":
            price = S*stats.norm.cdf(d1) - K*np.exp(-r*T)*stats.norm.cdf(d2)
        else:
            price = K*np.exp(-r*T)*stats.norm.cdf(-d2) - S*stats.norm.cdf(-d1)
        
        return price
    
    @staticmethod
    def barrier_option(S, K, T, r, sigma, barrier, barrier_type, option_type="call"):
        """Barrier option pricing using Monte Carlo"""
        n_simulations = 100000
        n_steps = 252  # Daily steps
        dt = T / n_steps
        
        payoffs = []
        
        for _ in range(n_simulations):
            path = [S]
            barrier_hit = False
            
            for _ in range(n_steps):
                dW = np.random.normal(0, np.sqrt(dt))
                S_next = path[-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*dW)
                path.append(S_next)
                
                # Check barrier condition
                if barrier_type == "up_and_out" and S_next >= barrier:
                    barrier_hit = True
                    break
                elif barrier_type == "down_and_out" and S_next <= barrier:
                    barrier_hit = True
                    break
                elif barrier_type == "up_and_in" and S_next >= barrier:
                    barrier_hit = True
                elif barrier_type == "down_and_in" and S_next <= barrier:
                    barrier_hit = True
            
            # Calculate payoff
            final_price = path[-1]
            
            if barrier_type in ["up_and_out", "down_and_out"]:
                if not barrier_hit:
                    if option_type == "call":
                        payoff = max(final_price - K, 0)
                    else:
                        payoff = max(K - final_price, 0)
                else:
                    payoff = 0
            else:  # knock-in options
                if barrier_hit:
                    if option_type == "call":
                        payoff = max(final_price - K, 0)
                    else:
                        payoff = max(K - final_price, 0)
                else:
                    payoff = 0
            
            payoffs.append(payoff)
        
        return np.exp(-r*T) * np.mean(payoffs)
    
    @staticmethod
    def asian_option(S, K, T, r, sigma, averaging_type="arithmetic", option_type="call"):
        """Asian option pricing using Monte Carlo"""
        n_simulations = 100000
        n_steps = 252
        dt = T / n_steps
        
        payoffs = []
        
        for _ in range(n_simulations):
            path = [S]
            
            for _ in range(n_steps):
                dW = np.random.normal(0, np.sqrt(dt))
                S_next = path[-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*dW)
                path.append(S_next)
            
            # Calculate average
            if averaging_type == "arithmetic":
                avg_price = np.mean(path)
            else:  # geometric
                avg_price = np.exp(np.mean(np.log(path)))
            
            # Calculate payoff
            if option_type == "call":
                payoff = max(avg_price - K, 0)
            else:
                payoff = max(K - avg_price, 0)
            
            payoffs.append(payoff)
        
        return np.exp(-r*T) * np.mean(payoffs)
    
    @staticmethod
    def digital_option(S, K, T, r, sigma, payout, option_type="call"):
        """Digital/Binary option pricing"""
        d2 = (np.log(S/K) + (r - 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        
        if option_type == "call":
            price = payout * np.exp(-r*T) * stats.norm.cdf(d2)
        else:
            price = payout * np.exp(-r*T) * stats.norm.cdf(-d2)
        
        return price

class Greeks:
    """Option Greeks calculations"""
    
    @staticmethod
    def calculate_greeks(S, K, T, r, sigma, option_type="call"):
        """Calculate all Greeks for vanilla options"""
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        # Delta
        if option_type == "call":
            delta = stats.norm.cdf(d1)
        else:
            delta = stats.norm.cdf(d1) - 1
        
        # Gamma
        gamma = stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # Theta
        if option_type == "call":
            theta = (-S * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    - r * K * np.exp(-r*T) * stats.norm.cdf(d2)) / 365
        else:
            theta = (-S * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    + r * K * np.exp(-r*T) * stats.norm.cdf(-d2)) / 365
        
        # Vega
        vega = S * stats.norm.pdf(d1) * np.sqrt(T) / 100
        
        # Rho
        if option_type == "call":
            rho = K * T * np.exp(-r*T) * stats.norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r*T) * stats.norm.cdf(-d2) / 100
        
        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho
        }

def calculate_option_price(option: OptionContract, spot_price: float, risk_free_rate: float = 0.05) -> Dict[str, float]:
    """Calculate option price and Greeks"""
    S = spot_price
    K = option.strike_price
    T = (option.expiry_date - datetime.utcnow()).total_seconds() / (365.25 * 24 * 3600)
    r = risk_free_rate
    sigma = option.implied_volatility
    
    if T <= 0:
        return {"price": 0.0, "delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
    
    # Price calculation based on option type
    if option.barrier_type:
        # Barrier option
        price = OptionPricer.barrier_option(S, K, T, r, sigma, option.barrier_level, option.barrier_type, option.option_type)
        greeks = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}  # Simplified
    elif option.averaging_type:
        # Asian option
        price = OptionPricer.asian_option(S, K, T, r, sigma, option.averaging_type, option.option_type)
        greeks = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}  # Simplified
    elif option.payout_amount:
        # Digital option
        price = OptionPricer.digital_option(S, K, T, r, sigma, option.payout_amount, option.option_type)
        greeks = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}  # Simplified
    else:
        # Vanilla option
        price = OptionPricer.black_scholes(S, K, T, r, sigma, option.option_type)
        greeks = Greeks.calculate_greeks(S, K, T, r, sigma, option.option_type)
    
    return {
        "price": price,
        **greeks
    }

def calculate_structured_product_value(product: StructuredProduct, underlying_prices: Dict[str, float]) -> float:
    """Calculate structured product value"""
    # Simplified structured product valuation
    # In practice, this would involve complex Monte Carlo simulations
    
    if product.product_type == "autocall":
        # Autocall note valuation
        worst_performance = min(
            underlying_prices[asset] / 100  # Assuming 100 is initial price
            for asset in product.underlying_assets
        )
        
        if worst_performance >= product.autocall_level:
            # Autocall triggered
            return product.notional_amount * (1 + product.coupon_rate)
        elif worst_performance >= product.barrier_level:
            # No autocall, but above barrier
            return product.notional_amount * (1 + product.accrued_coupon / product.notional_amount)
        else:
            # Below barrier
            return product.notional_amount * (product.capital_protection + 
                                           (1 - product.capital_protection) * worst_performance * product.participation_rate)
    
    elif product.product_type == "reverse_convertible":
        # Reverse convertible note
        worst_performance = min(
            underlying_prices[asset] / 100
            for asset in product.underlying_assets
        )
        
        if worst_performance >= product.barrier_level:
            return product.notional_amount * (1 + product.coupon_rate)
        else:
            return product.notional_amount * worst_performance
    
    return product.current_value

def calculate_portfolio_risk(user_id: str, db: Session) -> Dict[str, float]:
    """Calculate portfolio risk metrics"""
    # Get user's derivative positions
    trades = db.query(DerivativeTrade).filter(
        DerivativeTrade.user_id == user_id,
        DerivativeTrade.status.in_(["filled", "partially_filled"])
    ).all()
    
    if not trades:
        return {
            "portfolio_delta": 0.0,
            "portfolio_gamma": 0.0,
            "portfolio_theta": 0.0,
            "portfolio_vega": 0.0,
            "portfolio_rho": 0.0,
            "var_1d": 0.0,
            "var_10d": 0.0
        }
    
    # Aggregate Greeks
    total_delta = sum(trade.quantity * 0.5 for trade in trades)  # Mock calculation
    total_gamma = sum(trade.quantity * 0.1 for trade in trades)
    total_theta = sum(trade.quantity * -0.05 for trade in trades)
    total_vega = sum(trade.quantity * 0.2 for trade in trades)
    total_rho = sum(trade.quantity * 0.1 for trade in trades)
    
    # VaR calculation (simplified)
    portfolio_value = sum(trade.quantity * trade.fill_price for trade in trades if trade.fill_price)
    var_1d = portfolio_value * 0.02  # 2% VaR
    var_10d = var_1d * np.sqrt(10)
    
    return {
        "portfolio_delta": total_delta,
        "portfolio_gamma": total_gamma,
        "portfolio_theta": total_theta,
        "portfolio_vega": total_vega,
        "portfolio_rho": total_rho,
        "var_1d": var_1d,
        "var_10d": var_10d
    }

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "advanced-derivatives-trading"}

# Option contracts
@app.post("/options")
async def create_option_contract(
    option: OptionContractCreate,
    db: Session = Depends(get_db)
):
    """Create new option contract"""
    db_option = OptionContract(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    
    # Calculate initial pricing
    spot_price = 100.0  # Mock spot price
    pricing = calculate_option_price(db_option, spot_price)
    
    db_option.current_price = pricing["price"]
    db_option.delta = pricing["delta"]
    db_option.gamma = pricing["gamma"]
    db_option.theta = pricing["theta"]
    db_option.vega = pricing["vega"]
    db_option.rho = pricing["rho"]
    
    db.commit()
    
    return db_option

@app.get("/options")
async def get_option_contracts(
    underlying: Optional[str] = None,
    option_type: Optional[str] = None,
    style: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get option contracts"""
    query = db.query(OptionContract)
    
    if underlying:
        query = query.filter(OptionContract.underlying == underlying)
    if option_type:
        query = query.filter(OptionContract.option_type == option_type)
    if style:
        query = query.filter(OptionContract.style == style)
    
    options = query.offset(skip).limit(limit).all()
    return options

@app.get("/options/{option_id}")
async def get_option_contract(option_id: str, db: Session = Depends(get_db)):
    """Get option contract details"""
    option = db.query(OptionContract).filter(OptionContract.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option contract not found")
    
    return option

@app.get("/options/{option_id}/pricing")
async def get_option_pricing(
    option_id: str,
    spot_price: float,
    volatility: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get option pricing and Greeks"""
    option = db.query(OptionContract).filter(OptionContract.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Option contract not found")
    
    # Use provided volatility or current implied volatility
    if volatility:
        option.implied_volatility = volatility
    
    pricing = calculate_option_price(option, spot_price)
    
    return {
        "option_id": option_id,
        "spot_price": spot_price,
        "pricing": pricing,
        "time_to_expiry": (option.expiry_date - datetime.utcnow()).total_seconds() / (365.25 * 24 * 3600)
    }

# Structured products
@app.post("/structured-products")
async def create_structured_product(
    product: StructuredProductCreate,
    db: Session = Depends(get_db)
):
    """Create structured product"""
    db_product = StructuredProduct(**product.dict())
    db_product.current_value = product.notional_amount  # Initial value
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

@app.get("/structured-products")
async def get_structured_products(
    product_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get structured products"""
    query = db.query(StructuredProduct)
    
    if product_type:
        query = query.filter(StructuredProduct.product_type == product_type)
    if status:
        query = query.filter(StructuredProduct.status == status)
    
    products = query.offset(skip).limit(limit).all()
    return products

@app.get("/structured-products/{product_id}")
async def get_structured_product(product_id: str, db: Session = Depends(get_db)):
    """Get structured product details"""
    product = db.query(StructuredProduct).filter(StructuredProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Structured product not found")
    
    return product

@app.get("/structured-products/{product_id}/valuation")
async def get_structured_product_valuation(
    product_id: str,
    underlying_prices: Dict[str, float],
    db: Session = Depends(get_db)
):
    """Get structured product valuation"""
    product = db.query(StructuredProduct).filter(StructuredProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Structured product not found")
    
    current_value = calculate_structured_product_value(product, underlying_prices)
    
    return {
        "product_id": product_id,
        "current_value": current_value,
        "notional_amount": product.notional_amount,
        "pnl": current_value - product.notional_amount,
        "pnl_percentage": ((current_value - product.notional_amount) / product.notional_amount) * 100,
        "underlying_prices": underlying_prices
    }

# Trading
@app.post("/trades")
async def create_derivative_trade(
    user_id: str,
    trade: DerivativeTradeCreate,
    db: Session = Depends(get_db)
):
    """Create derivative trade"""
    # Get product details
    if trade.product_type == "option":
        product = db.query(OptionContract).filter(OptionContract.id == trade.product_id).first()
    elif trade.product_type == "structured_product":
        product = db.query(StructuredProduct).filter(StructuredProduct.id == trade.product_id).first()
    else:
        product = db.query(DerivativeProduct).filter(DerivativeProduct.id == trade.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create trade
    db_trade = DerivativeTrade(
        user_id=user_id,
        **trade.dict(),
        remaining_quantity=trade.quantity
    )
    
    # Calculate margin requirements
    if hasattr(product, 'current_price'):
        notional_value = trade.quantity * product.current_price
    else:
        notional_value = trade.quantity * (trade.price or 100.0)
    
    db_trade.initial_margin_required = notional_value * 0.1  # 10% margin
    db_trade.maintenance_margin = notional_value * 0.05  # 5% maintenance
    
    # Mock execution for market orders
    if trade.order_type == "market":
        db_trade.fill_price = trade.price or (product.current_price if hasattr(product, 'current_price') else 100.0)
        db_trade.fill_quantity = trade.quantity
        db_trade.remaining_quantity = 0.0
        db_trade.status = "filled"
        db_trade.filled_at = datetime.utcnow()
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    return db_trade

@app.get("/trades/{user_id}")
async def get_user_trades(
    user_id: str,
    product_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's derivative trades"""
    query = db.query(DerivativeTrade).filter(DerivativeTrade.user_id == user_id)
    
    if product_type:
        query = query.filter(DerivativeTrade.product_type == product_type)
    if status:
        query = query.filter(DerivativeTrade.status == status)
    
    trades = query.order_by(DerivativeTrade.created_at.desc()).limit(limit).all()
    return trades

# Risk management
@app.get("/risk/{user_id}")
async def get_user_risk_metrics(user_id: str, db: Session = Depends(get_db)):
    """Get user's risk metrics"""
    risk_metrics = calculate_portfolio_risk(user_id, db)
    
    # Save to database
    db_risk = RiskMetrics(
        user_id=user_id,
        **risk_metrics
    )
    db.add(db_risk)
    db.commit()
    
    return risk_metrics

@app.get("/risk/{user_id}/stress-test")
async def perform_stress_test(
    user_id: str,
    scenarios: Dict[str, float],  # {"spot_shock": -0.2, "vol_shock": 0.5}
    db: Session = Depends(get_db)
):
    """Perform portfolio stress test"""
    # Get user positions
    trades = db.query(DerivativeTrade).filter(
        DerivativeTrade.user_id == user_id,
        DerivativeTrade.status.in_(["filled", "partially_filled"])
    ).all()
    
    if not trades:
        return {"message": "No positions found", "stress_results": {}}
    
    # Calculate stress test results
    base_portfolio_value = sum(trade.quantity * (trade.fill_price or 100) for trade in trades)
    
    stress_results = {}
    for scenario_name, shock in scenarios.items():
        if scenario_name == "spot_shock":
            # Simulate spot price shock
            stressed_value = base_portfolio_value * (1 + shock * 0.5)  # Simplified delta approximation
        elif scenario_name == "vol_shock":
            # Simulate volatility shock
            stressed_value = base_portfolio_value * (1 + shock * 0.1)  # Simplified vega approximation
        else:
            stressed_value = base_portfolio_value
        
        stress_results[scenario_name] = {
            "shock": shock,
            "portfolio_value": stressed_value,
            "pnl": stressed_value - base_portfolio_value,
            "pnl_percentage": ((stressed_value - base_portfolio_value) / base_portfolio_value) * 100
        }
    
    return {
        "base_portfolio_value": base_portfolio_value,
        "stress_results": stress_results
    }

# Market data and analytics
@app.get("/market-data/volatility-surface/{underlying}")
async def get_volatility_surface(underlying: str, db: Session = Depends(get_db)):
    """Get implied volatility surface"""
    # Get all options for the underlying
    options = db.query(OptionContract).filter(
        OptionContract.underlying == underlying
    ).all()
    
    if not options:
        raise HTTPException(status_code=404, detail="No options found for underlying")
    
    # Build volatility surface
    surface_data = []
    for option in options:
        time_to_expiry = (option.expiry_date - datetime.utcnow()).total_seconds() / (365.25 * 24 * 3600)
        if time_to_expiry > 0:
            surface_data.append({
                "strike": option.strike_price,
                "expiry": time_to_expiry,
                "implied_vol": option.implied_volatility,
                "option_type": option.option_type
            })
    
    return {
        "underlying": underlying,
        "surface_data": surface_data,
        "data_points": len(surface_data)
    }

@app.get("/analytics/option-flow")
async def get_option_flow_analysis(
    underlying: Optional[str] = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get option flow analysis"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DerivativeTrade).filter(
        DerivativeTrade.product_type == "option",
        DerivativeTrade.created_at >= start_date
    )
    
    if underlying:
        # Filter by underlying (would need to join with OptionContract)
        pass
    
    trades = query.all()
    
    # Analyze option flow
    call_volume = sum(trade.quantity for trade in trades if "call" in str(trade.product_id))
    put_volume = sum(trade.quantity for trade in trades if "put" in str(trade.product_id))
    
    call_value = sum(trade.quantity * (trade.fill_price or 0) for trade in trades if "call" in str(trade.product_id))
    put_value = sum(trade.quantity * (trade.fill_price or 0) for trade in trades if "put" in str(trade.product_id))
    
    return {
        "period_days": days,
        "total_trades": len(trades),
        "call_put_ratio": call_volume / put_volume if put_volume > 0 else float('inf'),
        "call_volume": call_volume,
        "put_volume": put_volume,
        "call_value": call_value,
        "put_value": put_value,
        "net_gamma": call_volume * 0.1 - put_volume * 0.1,  # Simplified
        "net_delta": call_volume * 0.5 - put_volume * (-0.5)  # Simplified
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Advanced Derivatives Trading service started")
    
    # Start background tasks
    asyncio.create_task(periodic_option_pricing_update())
    asyncio.create_task(periodic_risk_monitoring())

async def periodic_option_pricing_update():
    """Update option pricing periodically"""
    while True:
        try:
            db = SessionLocal()
            
            # Get all active options
            options = db.query(OptionContract).all()
            
            for option in options:
                # Mock spot price update
                spot_price = 100 * (1 + np.random.normal(0, 0.01))
                
                # Update pricing
                pricing = calculate_option_price(option, spot_price)
                
                option.current_price = pricing["price"]
                option.delta = pricing["delta"]
                option.gamma = pricing["gamma"]
                option.theta = pricing["theta"]
                option.vega = pricing["vega"]
                option.rho = pricing["rho"]
            
            db.commit()
            db.close()
            
            await asyncio.sleep(60)  # Update every minute
            
        except Exception as e:
            logger.error(f"Error updating option pricing: {e}")
            await asyncio.sleep(30)

async def periodic_risk_monitoring():
    """Monitor portfolio risks"""
    while True:
        try:
            db = SessionLocal()
            
            # Get all users with active positions
            user_ids = db.query(DerivativeTrade.user_id).filter(
                DerivativeTrade.status.in_(["filled", "partially_filled"])
            ).distinct().all()
            
            for (user_id,) in user_ids:
                risk_metrics = calculate_portfolio_risk(user_id, db)
                
                # Check risk limits
                if risk_metrics["var_1d"] > 100000:  # $100k VaR limit
                    logger.warning(f"High VaR detected for user {user_id}: ${risk_metrics['var_1d']:,.2f}")
                
                # Save risk metrics
                db_risk = RiskMetrics(
                    user_id=user_id,
                    **risk_metrics
                )
                db.add(db_risk)
            
            db.commit()
            db.close()
            
            await asyncio.sleep(300)  # Monitor every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in risk monitoring: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)