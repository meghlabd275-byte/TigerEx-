import os
"""
TigerEx Analytics Dashboard Service
Comprehensive analytics and metrics for admin dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Analytics Dashboard Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Models
class PlatformMetrics(BaseModel):
    total_users: int
    active_users_24h: int
    active_users_7d: int
    active_users_30d: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    total_trading_volume_24h: Decimal
    total_trading_volume_7d: Decimal
    total_trading_volume_30d: Decimal
    total_deposits_24h: Decimal
    total_withdrawals_24h: Decimal
    pending_kyc_applications: int
    pending_withdrawals: int
    total_open_orders: int

class TradingMetrics(BaseModel):
    pair: str
    volume_24h: Decimal
    trades_count_24h: int
    price_change_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    last_price: Decimal

class UserGrowthMetrics(BaseModel):
    date: str
    new_users: int
    total_users: int
    active_users: int

class RevenueMetrics(BaseModel):
    date: str
    trading_fees: Decimal
    withdrawal_fees: Decimal
    total_revenue: Decimal

class TopTrader(BaseModel):
    user_id: int
    username: Optional[str]
    trading_volume: Decimal
    trades_count: int
    profit_loss: Optional[Decimal]

# Database functions
async def get_db():
    return db_pool

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="tigerex",
        password="tigerex_secure_password",
        database="tigerex_analytics",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create analytics aggregation tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                metric_id SERIAL PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                total_users INTEGER,
                new_users INTEGER,
                active_users INTEGER,
                trading_volume DECIMAL(36, 18),
                trades_count INTEGER,
                deposits_count INTEGER,
                deposits_volume DECIMAL(36, 18),
                withdrawals_count INTEGER,
                withdrawals_volume DECIMAL(36, 18),
                trading_fees DECIMAL(36, 18),
                withdrawal_fees DECIMAL(36, 18),
                total_revenue DECIMAL(36, 18),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_date (date)
            )
        """)
        
        # Create trading pair metrics
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_pair_metrics (
                metric_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                volume DECIMAL(36, 18),
                trades_count INTEGER,
                high_price DECIMAL(36, 18),
                low_price DECIMAL(36, 18),
                open_price DECIMAL(36, 18),
                close_price DECIMAL(36, 18),
                INDEX idx_pair_timestamp (pair, timestamp DESC)
            )
        """)
        
        # Create user activity metrics
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_metrics (
                metric_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                login_count INTEGER DEFAULT 0,
                trades_count INTEGER DEFAULT 0,
                trading_volume DECIMAL(36, 18) DEFAULT 0,
                deposits_count INTEGER DEFAULT 0,
                withdrawals_count INTEGER DEFAULT 0,
                UNIQUE(user_id, date),
                INDEX idx_user_date (user_id, date DESC)
            )
        """)
        
        logger.info("Database initialized successfully")

# API Endpoints
@app.get("/api/v1/analytics/platform/overview", response_model=PlatformMetrics)
async def get_platform_overview(db: asyncpg.Pool = Depends(get_db)):
    """Get overall platform metrics"""
    try:
        # This would query multiple databases in production
        # For now, returning mock data structure
        
        metrics = PlatformMetrics(
            total_users=50000,
            active_users_24h=5000,
            active_users_7d=15000,
            active_users_30d=35000,
            new_users_today=150,
            new_users_this_week=1200,
            new_users_this_month=5500,
            total_trading_volume_24h=Decimal("15000000.00"),
            total_trading_volume_7d=Decimal("95000000.00"),
            total_trading_volume_30d=Decimal("450000000.00"),
            total_deposits_24h=Decimal("2500000.00"),
            total_withdrawals_24h=Decimal("1800000.00"),
            pending_kyc_applications=45,
            pending_withdrawals=23,
            total_open_orders=1250
        )
        
        logger.info("platform_overview_retrieved")
        return metrics
        
    except Exception as e:
        logger.error("get_platform_overview_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/trading/pairs", response_model=List[TradingMetrics])
async def get_trading_pairs_metrics(
    limit: int = Query(20, le=100),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get trading metrics for all pairs"""
    try:
        # Mock data - in production, this would query actual trading data
        pairs = [
            TradingMetrics(
                pair="BTC/USDT",
                volume_24h=Decimal("5000000.00"),
                trades_count_24h=15000,
                price_change_24h=Decimal("2.5"),
                high_24h=Decimal("45000.00"),
                low_24h=Decimal("43500.00"),
                last_price=Decimal("44800.00")
            ),
            TradingMetrics(
                pair="ETH/USDT",
                volume_24h=Decimal("3500000.00"),
                trades_count_24h=12000,
                price_change_24h=Decimal("3.2"),
                high_24h=Decimal("2450.00"),
                low_24h=Decimal("2380.00"),
                last_price=Decimal("2425.00")
            ),
            TradingMetrics(
                pair="BNB/USDT",
                volume_24h=Decimal("1200000.00"),
                trades_count_24h=8000,
                price_change_24h=Decimal("-1.5"),
                high_24h=Decimal("315.00"),
                low_24h=Decimal("305.00"),
                last_price=Decimal("308.50")
            )
        ]
        
        return pairs[:limit]
        
    except Exception as e:
        logger.error("get_trading_pairs_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/users/growth", response_model=List[UserGrowthMetrics])
async def get_user_growth(
    days: int = Query(30, le=365),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user growth metrics"""
    try:
        metrics = []
        base_date = datetime.utcnow().date()
        
        # Mock data - in production, query actual user data
        for i in range(days):
            date = base_date - timedelta(days=i)
            metrics.append(UserGrowthMetrics(
                date=date.isoformat(),
                new_users=100 + (i * 5),
                total_users=50000 - (i * 100),
                active_users=5000 - (i * 50)
            ))
        
        return list(reversed(metrics))
        
    except Exception as e:
        logger.error("get_user_growth_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/revenue", response_model=List[RevenueMetrics])
async def get_revenue_metrics(
    days: int = Query(30, le=365),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get revenue metrics"""
    try:
        metrics = []
        base_date = datetime.utcnow().date()
        
        # Mock data - in production, query actual fee data
        for i in range(days):
            date = base_date - timedelta(days=i)
            trading_fees = Decimal("15000.00") + Decimal(i * 100)
            withdrawal_fees = Decimal("2500.00") + Decimal(i * 20)
            
            metrics.append(RevenueMetrics(
                date=date.isoformat(),
                trading_fees=trading_fees,
                withdrawal_fees=withdrawal_fees,
                total_revenue=trading_fees + withdrawal_fees
            ))
        
        return list(reversed(metrics))
        
    except Exception as e:
        logger.error("get_revenue_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/users/top-traders", response_model=List[TopTrader])
async def get_top_traders(
    limit: int = Query(10, le=100),
    period: str = Query("24h", regex="^(24h|7d|30d)$"),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get top traders by volume"""
    try:
        # Mock data - in production, query actual trading data
        traders = [
            TopTrader(
                user_id=1001,
                username="trader_pro",
                trading_volume=Decimal("500000.00"),
                trades_count=1250,
                profit_loss=Decimal("15000.00")
            ),
            TopTrader(
                user_id=1002,
                username="crypto_whale",
                trading_volume=Decimal("450000.00"),
                trades_count=980,
                profit_loss=Decimal("12500.00")
            ),
            TopTrader(
                user_id=1003,
                username="day_trader",
                trading_volume=Decimal("380000.00"),
                trades_count=2100,
                profit_loss=Decimal("8500.00")
            )
        ]
        
        return traders[:limit]
        
    except Exception as e:
        logger.error("get_top_traders_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/trading/volume")
async def get_trading_volume_breakdown(
    period: str = Query("24h", regex="^(24h|7d|30d)$"),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get trading volume breakdown by currency"""
    try:
        # Mock data
        breakdown = {
            "BTC": {"volume": "5000000.00", "percentage": 33.3},
            "ETH": {"volume": "3500000.00", "percentage": 23.3},
            "BNB": {"volume": "1200000.00", "percentage": 8.0},
            "USDT": {"volume": "5300000.00", "percentage": 35.4}
        }
        
        return breakdown
        
    except Exception as e:
        logger.error("get_volume_breakdown_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/deposits-withdrawals")
async def get_deposits_withdrawals_stats(
    days: int = Query(7, le=90),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get deposits and withdrawals statistics"""
    try:
        stats = []
        base_date = datetime.utcnow().date()
        
        for i in range(days):
            date = base_date - timedelta(days=i)
            stats.append({
                "date": date.isoformat(),
                "deposits_count": 150 + (i * 5),
                "deposits_volume": str(Decimal("2500000.00") + Decimal(i * 10000)),
                "withdrawals_count": 120 + (i * 3),
                "withdrawals_volume": str(Decimal("1800000.00") + Decimal(i * 8000))
            })
        
        return list(reversed(stats))
        
    except Exception as e:
        logger.error("get_deposits_withdrawals_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/kyc/stats")
async def get_kyc_statistics(db: asyncpg.Pool = Depends(get_db)):
    """Get KYC statistics"""
    try:
        stats = {
            "total_applications": 5000,
            "pending": 45,
            "approved": 4500,
            "rejected": 455,
            "level_0": 500,
            "level_1": 2000,
            "level_2": 1800,
            "level_3": 700,
            "avg_processing_time_hours": 24,
            "applications_today": 25,
            "applications_this_week": 180,
            "applications_this_month": 750
        }
        
        return stats
        
    except Exception as e:
        logger.error("get_kyc_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/security/events")
async def get_security_events(
    days: int = Query(7, le=90),
    severity: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get security events statistics"""
    try:
        events = {
            "total_events": 150,
            "critical": 5,
            "high": 15,
            "medium": 50,
            "low": 80,
            "resolved": 120,
            "unresolved": 30,
            "recent_events": [
                {
                    "event_type": "suspicious_login",
                    "severity": "high",
                    "count": 8,
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "event_type": "multiple_failed_logins",
                    "severity": "medium",
                    "count": 25,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        return events
        
    except Exception as e:
        logger.error("get_security_events_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/system/health")
async def get_system_health(db: asyncpg.Pool = Depends(get_db)):
    """Get system health metrics"""
    try:
        health = {
            "status": "healthy",
            "services": {
                "auth_service": {"status": "up", "response_time_ms": 45},
                "trading_engine": {"status": "up", "response_time_ms": 120},
                "wallet_service": {"status": "up", "response_time_ms": 80},
                "kyc_service": {"status": "up", "response_time_ms": 95},
                "notification_service": {"status": "up", "response_time_ms": 60}
            },
            "database": {
                "status": "healthy",
                "connections": 25,
                "max_connections": 100,
                "query_time_avg_ms": 15
            },
            "api": {
                "requests_per_minute": 1500,
                "avg_response_time_ms": 85,
                "error_rate": 0.5
            }
        }
        
        return health
        
    except Exception as e:
        logger.error("get_system_health_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analytics/aggregate/daily")
async def aggregate_daily_metrics(
    date: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Aggregate daily metrics (scheduled job)"""
    try:
        target_date = datetime.fromisoformat(date).date() if date else datetime.utcnow().date()
        
        # In production, this would aggregate data from various sources
        await db.execute("""
            INSERT INTO daily_metrics (
                date, total_users, new_users, active_users,
                trading_volume, trades_count, deposits_count,
                deposits_volume, withdrawals_count, withdrawals_volume,
                trading_fees, withdrawal_fees, total_revenue
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (date) DO UPDATE SET
                total_users = $2,
                new_users = $3,
                active_users = $4,
                trading_volume = $5,
                trades_count = $6,
                deposits_count = $7,
                deposits_volume = $8,
                withdrawals_count = $9,
                withdrawals_volume = $10,
                trading_fees = $11,
                withdrawal_fees = $12,
                total_revenue = $13
        """, target_date, 50000, 150, 5000, Decimal("15000000"),
            25000, 150, Decimal("2500000"), 120, Decimal("1800000"),
            Decimal("15000"), Decimal("2500"), Decimal("17500"))
        
        logger.info("daily_metrics_aggregated", date=target_date.isoformat())
        return {"message": "Daily metrics aggregated successfully", "date": target_date.isoformat()}
        
    except Exception as e:
        logger.error("aggregate_daily_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics-dashboard-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Analytics Dashboard Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Analytics Dashboard Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8260)