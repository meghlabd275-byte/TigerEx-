"""
TigerEx Alpha Market Admin Panel
Manages alpha trading strategies, signal providers, and performance tracking
Port: 8115
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_alpha_market"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class StrategyType(str, Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    TREND_FOLLOWING = "trend_following"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    PAIRS_TRADING = "pairs_trading"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

# Database Models
class AlphaStrategy(Base):
    __tablename__ = "alpha_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    strategy_type = Column(String)
    provider_id = Column(Integer)
    risk_level = Column(String)  # low, medium, high
    min_investment = Column(Float)
    performance_fee = Column(Float)
    management_fee = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    total_return = Column(Float)
    win_rate = Column(Float)
    avg_trade_duration = Column(Integer)  # in hours
    total_trades = Column(Integer)
    active_subscribers = Column(Integer, default=0)
    aum = Column(Float, default=0.0)  # Assets Under Management
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

class SignalProvider(Base):
    __tablename__ = "signal_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    company = Column(String)
    description = Column(Text)
    status = Column(String, default="active")
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    rating = Column(Float, default=0.0)
    total_strategies = Column(Integer, default=0)
    total_subscribers = Column(Integer, default=0)
    total_aum = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    avg_return = Column(Float, default=0.0)
    joined_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    kyc_verified = Column(Boolean, default=False)
    metadata = Column(JSON)

class TradingSignal(Base):
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, index=True)
    provider_id = Column(Integer, index=True)
    symbol = Column(String, index=True)
    signal_type = Column(String)
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_loss = Column(Float)
    confidence = Column(Float)  # 0-100
    timeframe = Column(String)  # 1h, 4h, 1d, etc.
    reasoning = Column(Text)
    status = Column(String, default="active")  # active, executed, expired, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    executed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, index=True)
    date = Column(DateTime, index=True)
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    total_trades = Column(Integer)
    profitable_trades = Column(Integer)
    avg_profit = Column(Float)
    avg_loss = Column(Float)
    aum = Column(Float)
    metadata = Column(JSON)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    strategy_id = Column(Integer, index=True)
    tier = Column(String)
    amount_invested = Column(Float)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    total_return = Column(Float, default=0.0)
    total_fees_paid = Column(Float, default=0.0)
    metadata = Column(JSON)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class AlphaStrategyCreate(BaseModel):
    name: str
    description: str
    strategy_type: StrategyType
    provider_id: int
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    min_investment: float = Field(gt=0)
    performance_fee: float = Field(ge=0, le=50)
    management_fee: float = Field(ge=0, le=10)
    metadata: Optional[Dict[str, Any]] = None

class AlphaStrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    min_investment: Optional[float] = None
    performance_fee: Optional[float] = None
    management_fee: Optional[float] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class SignalProviderCreate(BaseModel):
    name: str
    email: str
    company: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

class SignalProviderUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProviderStatus] = None
    verification_status: Optional[str] = None
    rating: Optional[float] = None
    kyc_verified: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class TradingSignalCreate(BaseModel):
    strategy_id: int
    provider_id: int
    symbol: str
    signal_type: SignalType
    entry_price: float = Field(gt=0)
    target_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    confidence: float = Field(ge=0, le=100)
    timeframe: str
    reasoning: str
    expires_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class SubscriptionCreate(BaseModel):
    user_id: int
    strategy_id: int
    tier: SubscriptionTier
    amount_invested: float = Field(gt=0)
    auto_renew: bool = True
    metadata: Optional[Dict[str, Any]] = None

# FastAPI app
app = FastAPI(
    title="TigerEx Alpha Market Admin API",
    description="Admin panel for managing alpha trading strategies and signal providers",
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

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ALPHA STRATEGY ENDPOINTS ====================

@app.post("/api/admin/strategies", status_code=201)
async def create_strategy(strategy: AlphaStrategyCreate, db: Session = Depends(get_db)):
    """Create a new alpha trading strategy"""
    try:
        # Check if strategy name already exists
        existing = db.query(AlphaStrategy).filter(AlphaStrategy.name == strategy.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Strategy name already exists")
        
        # Check if provider exists
        provider = db.query(SignalProvider).filter(SignalProvider.id == strategy.provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Signal provider not found")
        
        db_strategy = AlphaStrategy(**strategy.dict())
        db.add(db_strategy)
        
        # Update provider stats
        provider.total_strategies += 1
        
        db.commit()
        db.refresh(db_strategy)
        
        logger.info(f"Created alpha strategy: {strategy.name}")
        return db_strategy
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/strategies")
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    strategy_type: Optional[StrategyType] = None,
    provider_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all alpha strategies with filters"""
    try:
        query = db.query(AlphaStrategy)
        
        if strategy_type:
            query = query.filter(AlphaStrategy.strategy_type == strategy_type)
        if provider_id:
            query = query.filter(AlphaStrategy.provider_id == provider_id)
        if is_active is not None:
            query = query.filter(AlphaStrategy.is_active == is_active)
        
        total = query.count()
        strategies = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "strategies": strategies
        }
    except Exception as e:
        logger.error(f"Error fetching strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/strategies/{strategy_id}")
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get a specific alpha strategy"""
    strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@app.put("/api/admin/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy_update: AlphaStrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update an alpha strategy"""
    try:
        strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        update_data = strategy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        strategy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Updated strategy: {strategy_id}")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete an alpha strategy"""
    try:
        strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Check if strategy has active subscribers
        active_subs = db.query(Subscription).filter(
            Subscription.strategy_id == strategy_id,
            Subscription.is_active == True
        ).count()
        
        if active_subs > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete strategy with {active_subs} active subscribers"
            )
        
        db.delete(strategy)
        db.commit()
        
        logger.info(f"Deleted strategy: {strategy_id}")
        return {"message": "Strategy deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SIGNAL PROVIDER ENDPOINTS ====================

@app.post("/api/admin/providers", status_code=201)
async def create_provider(provider: SignalProviderCreate, db: Session = Depends(get_db)):
    """Create a new signal provider"""
    try:
        # Check if email already exists
        existing = db.query(SignalProvider).filter(SignalProvider.email == provider.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_provider = SignalProvider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        
        logger.info(f"Created signal provider: {provider.name}")
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
    status: Optional[ProviderStatus] = None,
    verification_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all signal providers with filters"""
    try:
        query = db.query(SignalProvider)
        
        if status:
            query = query.filter(SignalProvider.status == status)
        if verification_status:
            query = query.filter(SignalProvider.verification_status == verification_status)
        
        total = query.count()
        providers = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "providers": providers
        }
    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/providers/{provider_id}")
async def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get a specific signal provider"""
    provider = db.query(SignalProvider).filter(SignalProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.put("/api/admin/providers/{provider_id}")
async def update_provider(
    provider_id: int,
    provider_update: SignalProviderUpdate,
    db: Session = Depends(get_db)
):
    """Update a signal provider"""
    try:
        provider = db.query(SignalProvider).filter(SignalProvider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        update_data = provider_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        provider.last_active = datetime.utcnow()
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

@app.post("/api/admin/providers/{provider_id}/verify")
async def verify_provider(provider_id: int, db: Session = Depends(get_db)):
    """Verify a signal provider"""
    try:
        provider = db.query(SignalProvider).filter(SignalProvider.id == provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider.verification_status = "verified"
        provider.kyc_verified = True
        db.commit()
        
        logger.info(f"Verified provider: {provider_id}")
        return {"message": "Provider verified successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying provider: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRADING SIGNAL ENDPOINTS ====================

@app.post("/api/admin/signals", status_code=201)
async def create_signal(signal: TradingSignalCreate, db: Session = Depends(get_db)):
    """Create a new trading signal"""
    try:
        # Verify strategy and provider exist
        strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == signal.strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        provider = db.query(SignalProvider).filter(SignalProvider.id == signal.provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        db_signal = TradingSignal(**signal.dict())
        db.add(db_signal)
        db.commit()
        db.refresh(db_signal)
        
        logger.info(f"Created trading signal for {signal.symbol}")
        return db_signal
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating signal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/signals")
async def get_signals(
    skip: int = 0,
    limit: int = 100,
    strategy_id: Optional[int] = None,
    provider_id: Optional[int] = None,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all trading signals with filters"""
    try:
        query = db.query(TradingSignal)
        
        if strategy_id:
            query = query.filter(TradingSignal.strategy_id == strategy_id)
        if provider_id:
            query = query.filter(TradingSignal.provider_id == provider_id)
        if symbol:
            query = query.filter(TradingSignal.symbol == symbol)
        if status:
            query = query.filter(TradingSignal.status == status)
        
        total = query.count()
        signals = query.order_by(TradingSignal.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error fetching signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/signals/{signal_id}/status")
async def update_signal_status(
    signal_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update trading signal status"""
    try:
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        signal.status = status
        if status == "executed":
            signal.executed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Updated signal {signal_id} status to {status}")
        return {"message": "Signal status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating signal status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SUBSCRIPTION ENDPOINTS ====================

@app.post("/api/admin/subscriptions", status_code=201)
async def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create a new strategy subscription"""
    try:
        # Verify strategy exists
        strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == subscription.strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Check minimum investment
        if subscription.amount_invested < strategy.min_investment:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum investment is {strategy.min_investment}"
            )
        
        db_subscription = Subscription(**subscription.dict())
        db.add(db_subscription)
        
        # Update strategy stats
        strategy.active_subscribers += 1
        strategy.aum += subscription.amount_invested
        
        db.commit()
        db.refresh(db_subscription)
        
        logger.info(f"Created subscription for user {subscription.user_id}")
        return db_subscription
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/subscriptions")
async def get_subscriptions(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all subscriptions with filters"""
    try:
        query = db.query(Subscription)
        
        if user_id:
            query = query.filter(Subscription.user_id == user_id)
        if strategy_id:
            query = query.filter(Subscription.strategy_id == strategy_id)
        if is_active is not None:
            query = query.filter(Subscription.is_active == is_active)
        
        total = query.count()
        subscriptions = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "subscriptions": subscriptions
        }
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Cancel a subscription"""
    try:
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription.is_active = False
        subscription.end_date = datetime.utcnow()
        
        # Update strategy stats
        strategy = db.query(AlphaStrategy).filter(AlphaStrategy.id == subscription.strategy_id).first()
        if strategy:
            strategy.active_subscribers -= 1
            strategy.aum -= subscription.amount_invested
        
        db.commit()
        
        logger.info(f"Cancelled subscription: {subscription_id}")
        return {"message": "Subscription cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall alpha market analytics"""
    try:
        total_strategies = db.query(AlphaStrategy).count()
        active_strategies = db.query(AlphaStrategy).filter(AlphaStrategy.is_active == True).count()
        total_providers = db.query(SignalProvider).count()
        verified_providers = db.query(SignalProvider).filter(
            SignalProvider.verification_status == "verified"
        ).count()
        total_subscriptions = db.query(Subscription).filter(Subscription.is_active == True).count()
        total_aum = db.query(AlphaStrategy).with_entities(
            db.func.sum(AlphaStrategy.aum)
        ).scalar() or 0.0
        
        # Recent signals
        recent_signals = db.query(TradingSignal).filter(
            TradingSignal.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "total_strategies": total_strategies,
            "active_strategies": active_strategies,
            "total_providers": total_providers,
            "verified_providers": verified_providers,
            "total_subscriptions": total_subscriptions,
            "total_aum": total_aum,
            "recent_signals_7d": recent_signals
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/top-strategies")
async def get_top_strategies(limit: int = 10, db: Session = Depends(get_db)):
    """Get top performing strategies"""
    try:
        strategies = db.query(AlphaStrategy).filter(
            AlphaStrategy.is_active == True
        ).order_by(
            AlphaStrategy.total_return.desc()
        ).limit(limit).all()
        
        return strategies
    except Exception as e:
        logger.error(f"Error fetching top strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/top-providers")
async def get_top_providers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top signal providers"""
    try:
        providers = db.query(SignalProvider).filter(
            SignalProvider.status == "active"
        ).order_by(
            SignalProvider.total_aum.desc()
        ).limit(limit).all()
        
        return providers
    except Exception as e:
        logger.error(f"Error fetching top providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alpha-market-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8115)