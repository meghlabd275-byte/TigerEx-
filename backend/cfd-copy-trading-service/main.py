#!/usr/bin/env python3
"""
TigerEx CFD Copy Trading Service
Elite trader platform with CFD copy trading functionality
Based on Bitget/Bybit CFD Copy Trading systems
Port: 8191
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import jwt
import hashlib
import secrets
import uuid
import numpy as np
from collections import defaultdict

# @file main.py
# @description TigerEx cfd-copy-trading-service service
# @author TigerEx Development Team
# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"

# Global connections
db_pool = None
redis_client = None

security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class TraderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    FEATURED = "featured"
    ELITE = "elite"

class CopyTradingType(str, Enum):
    CFD = "cfd"
    FUTURES = "futures"
    SPOT = "spot"
    SPOT_COPY = "spot_copy"
    SIMULATED = "simulated"

class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    HIGH_RISK = "high_risk"

class SortBy(str, Enum):
    PROFIT = "profit"
    FOLLOWERS = "followers"
    WIN_RATE = "win_rate"
    SHARPE_RATIO = "sharpe_ratio"
    RECENT_PERFORMANCE = "recent_performance"
    ROI = "roi"
    AUM = "aum"

class CopyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TraderStats(BaseModel):
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit: Decimal = Decimal("0")
    total_loss: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    win_rate: float = 0.0
    avg_win: Decimal = Decimal("0")
    avg_loss: Decimal = Decimal("0")
    profit_factor: float = 0.0
    avg_holding_time_hours: float = 0.0
    volatility: float = 0.0
    roi: Decimal = Decimal("0")
    recent_roi_7d: Decimal = Decimal("0")
    recent_roi_30d: Decimal = Decimal("0")

class EliteTrader(BaseModel):
    trader_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    status: TraderStatus = TraderStatus.ACTIVE
    verified: bool = False
    featured: bool = False
    elite_trader: bool = False
    trading_type: CopyTradingType = CopyTradingType.CFD
    risk_level: RiskLevel = RiskLevel.MODERATE
    min_copy_amount: Decimal = Decimal("100")
    max_copy_amount: Decimal = Decimal("1000000")
    subscription_fee: Decimal = Decimal("0")
    profit_sharing: Decimal = Decimal("10")
    stats: TraderStats = TraderStats()
    followers_count: int = 0
    copiers_count: int = 0
    total_copied_amount: Decimal = Decimal("0")
    aum: Decimal = Decimal("0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    trading_instruments: List[str] = []

class CopySettings(BaseModel):
    trader_id: str
    copy_amount: Decimal = Field(..., gt=0)
    auto_copy: bool = True
    copy_percentage: float = Field(100.0, ge=1, le=100)
    max_positions: int = Field(10, ge=1, le=50)
    risk_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    stop_loss_percentage: Optional[float] = Field(None, ge=0.1, le=50)
    take_profit_percentage: Optional[float] = Field(None, ge=0.1, le=100)
    max_daily_loss: Optional[Decimal] = None
    copy_stop_loss: bool = True
    copy_take_profit: bool = True
    leverage_limit: Optional[int] = None

class SearchTradersRequest(BaseModel):
    search_query: Optional[str] = None
    trading_type: Optional[CopyTradingType] = None
    risk_level: Optional[RiskLevel] = None
    min_followers: Optional[int] = None
    min_profit: Optional[float] = None
    min_roi: Optional[float] = None
    sort_by: SortBy = SortBy.PROFIT
    sort_order: str = Field("desc", regex="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class CopyTradeRecord(BaseModel):
    record_id: str
    trader_id: str
    follower_id: str
    symbol: str
    side: PositionSide
    trader_entry_price: Decimal
    follower_entry_price: Decimal
    trader_exit_price: Optional[Decimal] = None
    follower_exit_price: Optional[Decimal] = None
    trader_lots: Decimal
    follower_lots: Decimal
    trader_pnl: Decimal = Decimal("0")
    follower_pnl: Decimal = Decimal("0")
    profit_share: Decimal = Decimal("0")
    status: CopyStatus = CopyStatus.ACTIVE
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

class FollowerStats(BaseModel):
    total_trades_copied: int = 0
    total_profit: Decimal = Decimal("0")
    total_fees_paid: Decimal = Decimal("0")
    active_copies: int = 0
    total_traders_followed: int = 0

# ============================================================================
# ELITE TRADER ENGINE
# ============================================================================

class CFDCopyTradingEngine:
    """CFD Copy Trading Engine with Elite Trader ranking"""
    
    def __init__(self):
        self.traders: Dict[str, EliteTrader] = {}
        self.followers: Dict[str, Dict[str, CopySettings]] = defaultdict(dict)  # user_id -> {trader_id -> settings}
        self.copy_records: List[CopyTradeRecord] = []
        self.trader_positions: Dict[str, List[Dict]] = defaultdict(list)
        self.follower_stats: Dict[str, FollowerStats] = {}
        self.leaderboard: List[Dict] = []
        
        self._initialize_sample_traders()
        self._start_background_tasks()
    
    def _initialize_sample_traders(self):
        """Initialize sample elite traders for demonstration"""
        
        sample_traders = [
            {
                "username": "tiger_elite",
                "display_name": "Tiger Elite Trader",
                "bio": "Professional CFD trader with 15+ years experience. Specializing in Forex and Gold trading with consistent returns.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.MODERATE,
                "stats": TraderStats(
                    total_trades=2500,
                    winning_trades=1650,
                    losing_trades=850,
                    total_profit=Decimal("2850000"),
                    total_loss=Decimal("1200000"),
                    win_rate=66.0,
                    roi=Decimal("1611.05"),
                    sharpe_ratio=2.15,
                    profit_factor=2.38
                ),
                "followers_count": 17102,
                "copiers_count": 5234,
                "aum": Decimal("24270.3"),
                "tags": ["forex", "gold", "technical", "medium_term"],
                "verified": True,
                "featured": True,
                "elite_trader": True
            },
            {
                "username": "forex_master",
                "display_name": "Forex Master Pro",
                "bio": "Institutional forex trader. Pure technical analysis with price action strategies. Low risk, consistent profits.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.CONSERVATIVE,
                "stats": TraderStats(
                    total_trades=5200,
                    winning_trades=3120,
                    losing_trades=2080,
                    total_profit=Decimal("1850000"),
                    total_loss=Decimal("950000"),
                    win_rate=60.0,
                    roi=Decimal("509.89"),
                    sharpe_ratio=1.85,
                    profit_factor=1.95
                ),
                "followers_count": 68104,
                "copiers_count": 12500,
                "aum": Decimal("1644.75"),
                "tags": ["forex", "conservative", "price_action", "long_term"],
                "verified": True,
                "featured": True,
                "elite_trader": True
            },
            {
                "username": "gold_hunter",
                "display_name": "Gold Hunter X",
                "bio": "Gold and metals specialist. High conviction trades with strict risk management. 10+ years in precious metals.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.AGGRESSIVE,
                "stats": TraderStats(
                    total_trades=1800,
                    winning_trades=1170,
                    losing_trades=630,
                    total_profit=Decimal("3200000"),
                    total_loss=Decimal("1450000"),
                    win_rate=65.0,
                    roi=Decimal("507.27"),
                    sharpe_ratio=2.05,
                    profit_factor=2.21
                ),
                "followers_count": 100,
                "copiers_count": 45,
                "aum": Decimal("1587.14"),
                "tags": ["gold", "silver", "metals", "swing_trading"],
                "verified": True,
                "featured": False,
                "elite_trader": True
            },
            {
                "username": "index_trader",
                "display_name": "Index Master",
                "bio": "S&P 500 and NASDAQ specialist. Day trading indices with precision entries and exits.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.MODERATE,
                "stats": TraderStats(
                    total_trades=8500,
                    winning_trades=5100,
                    losing_trades=3400,
                    total_profit=Decimal("4200000"),
                    total_loss=Decimal("2100000"),
                    win_rate=60.0,
                    roi=Decimal("385.45"),
                    sharpe_ratio=1.72,
                    profit_factor=2.0
                ),
                "followers_count": 45230,
                "copiers_count": 8900,
                "aum": Decimal("52840.50"),
                "tags": ["indices", "sp500", "nasdaq", "day_trading"],
                "verified": True,
                "featured": True,
                "elite_trader": True
            },
            {
                "username": "crypto_cfd_pro",
                "display_name": "Crypto CFD Pro",
                "bio": "Bitcoin and Ethereum CFD trader. Leveraging crypto volatility for consistent gains.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.HIGH_RISK,
                "stats": TraderStats(
                    total_trades=3200,
                    winning_trades=1760,
                    losing_trades=1440,
                    total_profit=Decimal("5800000"),
                    total_loss=Decimal("3200000"),
                    win_rate=55.0,
                    roi=Decimal("892.30"),
                    sharpe_ratio=1.55,
                    profit_factor=1.81
                ),
                "followers_count": 28500,
                "copiers_count": 6200,
                "aum": Decimal("35120.75"),
                "tags": ["crypto", "bitcoin", "ethereum", "leverage"],
                "verified": True,
                "featured": True,
                "elite_trader": True
            },
            {
                "username": "commodity_king",
                "display_name": "Commodity King",
                "bio": "Oil, gas, and agricultural commodities expert. Fundamental analysis combined with technical precision.",
                "trading_type": CopyTradingType.CFD,
                "risk_level": RiskLevel.AGGRESSIVE,
                "stats": TraderStats(
                    total_trades=2100,
                    winning_trades=1344,
                    losing_trades=756,
                    total_profit=Decimal("1950000"),
                    total_loss=Decimal("850000"),
                    win_rate=64.0,
                    roi=Decimal("425.67"),
                    sharpe_ratio=1.92,
                    profit_factor=2.29
                ),
                "followers_count": 15800,
                "copiers_count": 3200,
                "aum": Decimal("28450.00"),
                "tags": ["commodities", "oil", "gas", "fundamental"],
                "verified": True,
                "featured": False,
                "elite_trader": True
            }
        ]
        
        for i, trader_data in enumerate(sample_traders):
            trader_id = f"trader_{i+1:03d}"
            
            trader = EliteTrader(
                trader_id=trader_id,
                username=trader_data["username"],
                display_name=trader_data["display_name"],
                bio=trader_data["bio"],
                trading_type=trader_data["trading_type"],
                risk_level=trader_data["risk_level"],
                stats=trader_data["stats"],
                followers_count=trader_data["followers_count"],
                copiers_count=trader_data["copiers_count"],
                aum=trader_data["aum"],
                tags=trader_data["tags"],
                verified=trader_data.get("verified", False),
                featured=trader_data.get("featured", False),
                elite_trader=trader_data.get("elite_trader", False),
                min_copy_amount=Decimal("100"),
                max_copy_amount=Decimal("1000000"),
                subscription_fee=Decimal("0"),
                profit_sharing=Decimal("10")
            )
            
            self.traders[trader_id] = trader
        
        self._update_leaderboard()
    
    def _start_background_tasks(self):
        """Start background tasks"""
        asyncio.create_task(self._update_trader_stats())
        asyncio.create_task(self._update_leaderboard_task())
    
    async def _update_trader_stats(self):
        """Simulate trader stat updates"""
        while True:
            try:
                for trader_id, trader in self.traders.items():
                    # Simulate small changes
                    roi_change = np.random.uniform(-5, 10)
                    new_roi = trader.stats.roi + Decimal(str(roi_change))
                    trader.stats.roi = max(Decimal("0"), new_roi)
                    trader.last_active = datetime.utcnow()
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating trader stats: {e}")
                await asyncio.sleep(60)
    
    async def _update_leaderboard_task(self):
        """Update leaderboard periodically"""
        while True:
            try:
                self._update_leaderboard()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error updating leaderboard: {e}")
                await asyncio.sleep(30)
    
    def _update_leaderboard(self):
        """Update the leaderboard"""
        sorted_traders = sorted(
            self.traders.values(),
            key=lambda t: float(t.stats.roi),
            reverse=True
        )
        
        self.leaderboard = [
            {
                "rank": i + 1,
                "trader_id": trader.trader_id,
                "username": trader.username,
                "display_name": trader.display_name,
                "roi": str(trader.stats.roi),
                "win_rate": trader.stats.win_rate,
                "followers_count": trader.followers_count,
                "copiers_count": trader.copiers_count,
                "aum": str(trader.aum),
                "risk_level": trader.risk_level.value,
                "verified": trader.verified,
                "featured": trader.featured,
                "tags": trader.tags
            }
            for i, trader in enumerate(sorted_traders)
        ]
    
    async def search_traders(self, request: SearchTradersRequest) -> Dict[str, Any]:
        """Search and filter elite traders"""
        
        traders = list(self.traders.values())
        
        # Apply filters
        if request.search_query:
            query = request.search_query.lower()
            traders = [
                t for t in traders
                if query in t.username.lower() or
                   query in t.display_name.lower() or
                   any(query in tag.lower() for tag in t.tags)
            ]
        
        if request.trading_type:
            traders = [t for t in traders if t.trading_type == request.trading_type]
        
        if request.risk_level:
            traders = [t for t in traders if t.risk_level == request.risk_level]
        
        if request.min_followers:
            traders = [t for t in traders if t.followers_count >= request.min_followers]
        
        if request.min_profit:
            traders = [t for t in traders if float(t.stats.total_profit) >= request.min_profit]
        
        if request.min_roi:
            traders = [t for t in traders if float(t.stats.roi) >= request.min_roi]
        
        # Sort
        reverse = request.sort_order == "desc"
        if request.sort_by == SortBy.PROFIT:
            traders.sort(key=lambda t: float(t.stats.roi), reverse=reverse)
        elif request.sort_by == SortBy.FOLLOWERS:
            traders.sort(key=lambda t: t.followers_count, reverse=reverse)
        elif request.sort_by == SortBy.WIN_RATE:
            traders.sort(key=lambda t: t.stats.win_rate, reverse=reverse)
        elif request.sort_by == SortBy.AUM:
            traders.sort(key=lambda t: float(t.aum), reverse=reverse)
        elif request.sort_by == SortBy.ROI:
            traders.sort(key=lambda t: float(t.stats.roi), reverse=reverse)
        
        # Paginate
        total = len(traders)
        start = (request.page - 1) * request.limit
        end = start + request.limit
        paginated = traders[start:end]
        
        return {
            "success": True,
            "total": total,
            "page": request.page,
            "limit": request.limit,
            "traders": [
                {
                    "trader_id": t.trader_id,
                    "username": t.username,
                    "display_name": t.display_name,
                    "avatar_url": t.avatar_url,
                    "bio": t.bio,
                    "verified": t.verified,
                    "featured": t.featured,
                    "elite_trader": t.elite_trader,
                    "trading_type": t.trading_type.value,
                    "risk_level": t.risk_level.value,
                    "stats": {
                        "roi": str(t.stats.roi),
                        "win_rate": t.stats.win_rate,
                        "total_trades": t.stats.total_trades,
                        "profit_factor": t.stats.profit_factor,
                        "sharpe_ratio": t.stats.sharpe_ratio
                    },
                    "followers_count": t.followers_count,
                    "copiers_count": t.copiers_count,
                    "aum": str(t.aum),
                    "tags": t.tags,
                    "min_copy_amount": str(t.min_copy_amount),
                    "max_copy_amount": str(t.max_copy_amount),
                    "subscription_fee": str(t.subscription_fee),
                    "profit_sharing": str(t.profit_sharing)
                }
                for t in paginated
            ]
        }
    
    async def get_trader_details(self, trader_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed trader information"""
        
        if trader_id not in self.traders:
            return None
        
        trader = self.traders[trader_id]
        
        # Generate performance chart data
        performance_chart = self._generate_performance_chart(trader)
        
        # Generate recent trades
        recent_trades = self._generate_recent_trades(trader)
        
        return {
            "trader_id": trader.trader_id,
            "username": trader.username,
            "display_name": trader.display_name,
            "avatar_url": trader.avatar_url,
            "bio": trader.bio,
            "verified": trader.verified,
            "featured": trader.featured,
            "elite_trader": trader.elite_trader,
            "trading_type": trader.trading_type.value,
            "risk_level": trader.risk_level.value,
            "status": trader.status.value,
            "stats": {
                "roi": str(trader.stats.roi),
                "recent_roi_7d": str(trader.stats.recent_roi_7d),
                "recent_roi_30d": str(trader.stats.recent_roi_30d),
                "win_rate": trader.stats.win_rate,
                "total_trades": trader.stats.total_trades,
                "winning_trades": trader.stats.winning_trades,
                "losing_trades": trader.stats.losing_trades,
                "total_profit": str(trader.stats.total_profit),
                "total_loss": str(trader.stats.total_loss),
                "profit_factor": trader.stats.profit_factor,
                "sharpe_ratio": trader.stats.sharpe_ratio,
                "max_drawdown": str(trader.stats.max_drawdown),
                "avg_holding_time_hours": trader.stats.avg_holding_time_hours
            },
            "followers_count": trader.followers_count,
            "copiers_count": trader.copiers_count,
            "aum": str(trader.aum),
            "total_copied_amount": str(trader.total_copied_amount),
            "min_copy_amount": str(trader.min_copy_amount),
            "max_copy_amount": str(trader.max_copy_amount),
            "subscription_fee": str(trader.subscription_fee),
            "profit_sharing": str(trader.profit_sharing),
            "tags": trader.tags,
            "trading_instruments": trader.trading_instruments,
            "performance_chart": performance_chart,
            "recent_trades": recent_trades,
            "created_at": trader.created_at.isoformat(),
            "last_active": trader.last_active.isoformat()
        }
    
    def _generate_performance_chart(self, trader: EliteTrader) -> List[Dict]:
        """Generate performance chart data"""
        chart = []
        base_value = 1000
        roi = float(trader.stats.roi)
        
        for i in range(30):
            daily_change = np.random.uniform(-2, 3)
            base_value = base_value * (1 + daily_change / 100)
            chart.append({
                "date": (datetime.utcnow() - timedelta(days=29-i)).strftime("%Y-%m-%d"),
                "value": round(base_value, 2),
                "change_pct": round(daily_change, 2)
            })
        
        return chart
    
    def _generate_recent_trades(self, trader: EliteTrader) -> List[Dict]:
        """Generate recent trades for trader"""
        instruments = ["XAU/USD", "EUR/USD", "GBP/USD", "SPX500", "NAS100", "BTC/USD"]
        trades = []
        
        for i in range(10):
            is_win = np.random.random() < (trader.stats.win_rate / 100)
            pnl = np.random.uniform(100, 5000) * (1 if is_win else -1)
            
            trades.append({
                "trade_id": f"trade_{i+1}",
                "symbol": np.random.choice(instruments),
                "side": np.random.choice(["long", "short"]),
                "entry_price": round(np.random.uniform(1.05, 2350), 2),
                "exit_price": round(np.random.uniform(1.04, 2360), 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl / 1000 * 100, 2),
                "lots": round(np.random.uniform(0.1, 5.0), 2),
                "opened_at": (datetime.utcnow() - timedelta(hours=np.random.randint(1, 72))).isoformat(),
                "closed_at": datetime.utcnow().isoformat()
            })
        
        return trades
    
    async def start_copy(self, user_id: str, settings: CopySettings) -> Dict[str, Any]:
        """Start copying a trader"""
        
        if settings.trader_id not in self.traders:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        trader = self.traders[settings.trader_id]
        
        # Validate copy amount
        if settings.copy_amount < trader.min_copy_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum copy amount is {trader.min_copy_amount}"
            )
        
        if settings.copy_amount > trader.max_copy_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum copy amount is {trader.max_copy_amount}"
            )
        
        # Store copy settings
        self.followers[user_id][settings.trader_id] = settings
        
        # Update trader stats
        trader.followers_count += 1
        trader.copiers_count += 1
        trader.total_copied_amount += settings.copy_amount
        
        # Initialize follower stats if needed
        if user_id not in self.follower_stats:
            self.follower_stats[user_id] = FollowerStats()
        
        self.follower_stats[user_id].active_copies += 1
        self.follower_stats[user_id].total_traders_followed += 1
        
        return {
            "success": True,
            "message": f"Now copying {trader.display_name}",
            "copy_id": str(uuid.uuid4()),
            "trader_id": settings.trader_id,
            "copy_amount": str(settings.copy_amount),
            "settings": {
                "auto_copy": settings.auto_copy,
                "copy_percentage": settings.copy_percentage,
                "max_positions": settings.max_positions,
                "risk_multiplier": settings.risk_multiplier,
                "stop_loss_percentage": settings.stop_loss_percentage,
                "take_profit_percentage": settings.take_profit_percentage
            },
            "profit_sharing": str(trader.profit_sharing),
            "started_at": datetime.utcnow().isoformat()
        }
    
    async def stop_copy(self, user_id: str, trader_id: str, close_positions: bool = False) -> Dict[str, Any]:
        """Stop copying a trader"""
        
        if trader_id not in self.followers.get(user_id, {}):
            raise HTTPException(status_code=404, detail="Copy relationship not found")
        
        del self.followers[user_id][trader_id]
        
        if trader_id in self.traders:
            self.traders[trader_id].copiers_count = max(0, self.traders[trader_id].copiers_count - 1)
        
        if user_id in self.follower_stats:
            self.follower_stats[user_id].active_copies = max(0, self.follower_stats[user_id].active_copies - 1)
        
        return {
            "success": True,
            "message": "Stopped copying trader",
            "trader_id": trader_id,
            "positions_closed": close_positions,
            "stopped_at": datetime.utcnow().isoformat()
        }
    
    async def get_following_traders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get traders that user is following"""
        
        following = self.followers.get(user_id, {})
        
        result = []
        for trader_id, settings in following.items():
            if trader_id in self.traders:
                trader = self.traders[trader_id]
                result.append({
                    "trader_id": trader_id,
                    "username": trader.username,
                    "display_name": trader.display_name,
                    "copy_amount": str(settings.copy_amount),
                    "auto_copy": settings.auto_copy,
                    "profit_sharing": str(trader.profit_sharing),
                    "trader_roi": str(trader.stats.roi),
                    "status": "active"
                })
        
        return result
    
    async def get_copy_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get copy trading history for user"""
        
        # Generate sample history
        history = []
        for record in self.copy_records:
            if record.follower_id == user_id:
                history.append({
                    "record_id": record.record_id,
                    "trader_id": record.trader_id,
                    "symbol": record.symbol,
                    "side": record.side.value,
                    "trader_pnl": str(record.trader_pnl),
                    "follower_pnl": str(record.follower_pnl),
                    "profit_share": str(record.profit_share),
                    "status": record.status.value,
                    "opened_at": record.opened_at.isoformat(),
                    "closed_at": record.closed_at.isoformat() if record.closed_at else None
                })
        
        return history
    
    async def get_leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get current leaderboard"""
        return self.leaderboard[:limit]

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="TigerEx CFD Copy Trading Service",
    description="Elite trader platform with CFD copy trading functionality",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
copy_engine = CFDCopyTradingEngine()

# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "role": payload.get("role", "user")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "moderator"]:
            raise HTTPException(status_code=401, detail="Admin access required")
        
        return {"admin_id": admin_id, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# ELITE TRADER ENDPOINTS
# ============================================================================

@app.get("/api/copy-trading/cfd/traders")
async def search_traders(
    search_query: Optional[str] = None,
    trading_type: Optional[CopyTradingType] = None,
    risk_level: Optional[RiskLevel] = None,
    min_followers: Optional[int] = None,
    min_roi: Optional[float] = None,
    sort_by: SortBy = SortBy.ROI,
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20
):
    """Search elite CFD traders"""
    
    request = SearchTradersRequest(
        search_query=search_query,
        trading_type=trading_type,
        risk_level=risk_level,
        min_followers=min_followers,
        min_roi=min_roi,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    
    return await copy_engine.search_traders(request)

@app.get("/api/copy-trading/cfd/traders/{trader_id}")
async def get_trader_details(trader_id: str):
    """Get detailed trader information"""
    
    details = await copy_engine.get_trader_details(trader_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    return {"success": True, "trader": details}

@app.get("/api/copy-trading/cfd/leaderboard")
async def get_leaderboard(limit: int = 20):
    """Get elite trader leaderboard"""
    
    leaderboard = await copy_engine.get_leaderboard(limit)
    
    return {"success": True, "leaderboard": leaderboard}

# ============================================================================
# COPY TRADING ENDPOINTS
# ============================================================================

@app.post("/api/copy-trading/cfd/start")
async def start_copy_trading(
    settings: CopySettings,
    user: dict = Depends(get_current_user)
):
    """Start copying a trader"""
    
    return await copy_engine.start_copy(user["user_id"], settings)

@app.post("/api/copy-trading/cfd/stop/{trader_id}")
async def stop_copy_trading(
    trader_id: str,
    close_positions: bool = False,
    user: dict = Depends(get_current_user)
):
    """Stop copying a trader"""
    
    return await copy_engine.stop_copy(user["user_id"], trader_id, close_positions)

@app.get("/api/copy-trading/cfd/following")
async def get_following_traders(user: dict = Depends(get_current_user)):
    """Get traders user is following"""
    
    following = await copy_engine.get_following_traders(user["user_id"])
    
    return {"success": True, "following": following}

@app.get("/api/copy-trading/cfd/history")
async def get_copy_history(user: dict = Depends(get_current_user)):
    """Get copy trading history"""
    
    history = await copy_engine.get_copy_history(user["user_id"])
    
    return {"success": True, "history": history}

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/copy-trading/admin/traders/{trader_id}/verify")
async def verify_trader(
    trader_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Verify a trader (Admin only)"""
    
    if trader_id not in copy_engine.traders:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    copy_engine.traders[trader_id].verified = True
    
    return {
        "success": True,
        "message": f"Trader {trader_id} verified",
        "verified_by": admin["admin_id"],
        "verified_at": datetime.utcnow().isoformat()
    }

@app.post("/api/copy-trading/admin/traders/{trader_id}/feature")
async def feature_trader(
    trader_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Feature a trader (Admin only)"""
    
    if trader_id not in copy_engine.traders:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    copy_engine.traders[trader_id].featured = True
    
    return {
        "success": True,
        "message": f"Trader {trader_id} featured",
        "featured_by": admin["admin_id"],
        "featured_at": datetime.utcnow().isoformat()
    }

@app.post("/api/copy-trading/admin/traders/{trader_id}/suspend")
async def suspend_trader(
    trader_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Suspend a trader (Admin only)"""
    
    if trader_id not in copy_engine.traders:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    copy_engine.traders[trader_id].status = TraderStatus.SUSPENDED
    
    return {
        "success": True,
        "message": f"Trader {trader_id} suspended",
        "reason": reason,
        "suspended_by": admin["admin_id"],
        "suspended_at": datetime.utcnow().isoformat()
    }

@app.post("/api/copy-trading/admin/traders/{trader_id}/elite")
async def make_elite_trader(
    trader_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Make trader elite (Admin only)"""
    
    if trader_id not in copy_engine.traders:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    copy_engine.traders[trader_id].elite_trader = True
    
    return {
        "success": True,
        "message": f"Trader {trader_id} promoted to elite",
        "promoted_by": admin["admin_id"],
        "promoted_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cfd-copy-trading-service",
        "version": "2.0.0",
        "traders_count": len(copy_engine.traders),
        "leaderboard_entries": len(copy_engine.leaderboard)
    }

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL)
    logger.info("CFD Copy Trading Service started")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()
    logger.info("CFD Copy Trading Service stopped")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8191)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
