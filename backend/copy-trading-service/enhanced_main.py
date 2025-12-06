"""
TigerEx Enhanced Copy Trading Service v9.0.0
Combines best features from Bybit and Bitget copy trading platforms
Professional social trading with advanced analytics and performance tracking
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
import time
import math
from decimal import Decimal
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Enhanced Copy Trading Service v9.0.0",
    description="Professional social trading platform with advanced analytics and performance tracking",
    version="9.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ==================== ENUMS AND MODELS ====================

class TraderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    FEATURED = "featured"

class CopyTradingStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

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

@dataclass
class TradingStats:
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit: Decimal
    total_loss: Decimal
    max_drawdown: Decimal
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    avg_win: Decimal
    avg_loss: Decimal
    profit_factor: float
    avg_holding_time: timedelta
    volatility: float

@dataclass
class CopyTrader:
    id: str
    username: str
    display_name: str
    avatar_url: str
    bio: str
    status: TraderStatus
    verified: bool
    featured: bool
    risk_level: RiskLevel
    min_copy_amount: Decimal
    max_copy_amount: Decimal
    subscription_fee: Decimal
    profit_sharing: Decimal
    trading_stats: TradingStats
    followers_count: int
    total_copied_amount: Decimal
    created_at: datetime
    last_active: datetime
    tags: List[str]

@dataclass
class CopyTrade:
    id: str
    trader_id: str
    follower_id: str
    original_order_id: str
    copied_order_id: str
    symbol: str
    side: str
    original_quantity: Decimal
    copied_quantity: Decimal
    original_price: Decimal
    copied_price: Decimal
    profit_loss: Decimal
    fee: Decimal
    status: CopyTradingStatus
    created_at: datetime
    closed_at: Optional[datetime]

@dataclass
class CopyPosition:
    id: str
    trader_id: str
    follower_id: str
    symbol: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    percentage_pnl: float
    leverage: int
    margin: Decimal
    status: CopyTradingStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class Follower:
    id: str
    user_id: str
    trader_id: str
    copy_amount: Decimal
    auto_copy: bool
    copy_percentage: float
    max_positions: int
    risk_multiplier: float
    stop_loss_percentage: float
    take_profit_percentage: float
    status: CopyTradingStatus
    total_invested: Decimal
    total_return: Decimal
    created_at: datetime
    last_copied: Optional[datetime]

# ==================== PYDANTIC MODELS ====================

class TraderProfile(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=100)
    bio: str = Field(..., max_length=500)
    risk_level: RiskLevel
    min_copy_amount: Decimal = Field(..., gt=0)
    max_copy_amount: Decimal = Field(..., gt=0)
    subscription_fee: Decimal = Field(..., ge=0)
    profit_sharing: Decimal = Field(..., ge=0, le=100)
    tags: List[str] = []

class CopySettings(BaseModel):
    trader_id: str
    copy_amount: Decimal = Field(..., gt=0)
    auto_copy: bool = True
    copy_percentage: float = Field(100.0, ge=1, le=100)
    max_positions: int = Field(10, ge=1, le=50)
    risk_multiplier: float = Field(1.0, ge=0.1, le=5.0)
    stop_loss_percentage: float = Field(None, ge=0.1, le=50)
    take_profit_percentage: float = Field(None, ge=0.1, le=100)

class SearchTradersRequest(BaseModel):
    search_query: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    min_followers: Optional[int] = None
    min_profit: Optional[float] = None
    sort_by: SortBy = SortBy.PROFIT
    sort_order: str = Field("desc", regex="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class TraderStatsResponse(BaseModel):
    trader_id: str
    username: str
    display_name: str
    avatar_url: str
    verified: bool
    featured: bool
    followers_count: int
    total_copied_amount: str
    trading_stats: Dict[str, Any]
    performance_chart: List[Dict[str, Any]]
    recent_trades: List[Dict[str, Any]]
    risk_metrics: Dict[str, Any]

# ==================== COPY TRADING ENGINE ====================

class EnhancedCopyTradingEngine:
    def __init__(self):
        self.traders: Dict[str, CopyTrader] = {}
        self.followers: Dict[str, List[Follower]] = defaultdict(list)
        self.copy_trades: List[CopyTrade] = []
        self.copy_positions: Dict[str, List[CopyPosition]] = defaultdict(list)
        self.websockets: List[WebSocket] = []
        
        # Performance metrics
        self.metrics = {
            'total_traders': 0,
            'active_traders': 0,
            'total_followers': 0,
            'total_copied_amount': Decimal('0'),
            'total_trades_copied': 0,
            'total_profit_shared': Decimal('0'),
            'top_trader_daily_profit': Decimal('0')
        }
        
        # Initialize sample traders
        self._initialize_sample_traders()
        
        # Start background tasks
        asyncio.create_task(self._performance_updater())
        asyncio.create_task(self._leaderboard_updater())
        asyncio.create_task(self._risk_monitor())
    
    def _initialize_sample_traders(self):
        """Initialize sample traders for demonstration"""
        sample_traders = [
            {
                "username": "tiger_master",
                "display_name": "Tiger Master Trader",
                "bio": "Professional trader with 10+ years experience. Specializing in BTC/ETH derivatives.",
                "risk_level": RiskLevel.MODERATE,
                "min_copy_amount": Decimal('100'),
                "max_copy_amount": Decimal('100000'),
                "subscription_fee": Decimal('0'),
                "profit_sharing": Decimal('10'),
                "tags": ["btc", "eth", "derivatives", "technical_analysis"]
            },
            {
                "username": "crypto_queen",
                "display_name": "Crypto Queen",
                "bio": "DeFi enthusiast and yield farming expert. High-risk, high-reward strategies.",
                "risk_level": RiskLevel.AGGRESSIVE,
                "min_copy_amount": Decimal('500'),
                "max_copy_amount": Decimal('50000'),
                "subscription_fee": Decimal('50'),
                "profit_sharing": Decimal('15'),
                "tags": ["defi", "yield_farming", "altcoins", "high_risk"]
            },
            {
                "username": "steady_gains",
                "display_name": "Steady Gains Pro",
                "bio": "Conservative trader focused on steady gains and capital preservation.",
                "risk_level": RiskLevel.CONSERVATIVE,
                "min_copy_amount": Decimal('50'),
                "max_copy_amount": Decimal('200000'),
                "subscription_fee": Decimal('25'),
                "profit_sharing": Decimal('8'),
                "tags": ["conservative", "stable_coins", "low_risk", "long_term"]
            },
            {
                "username": "whale_hunter",
                "display_name": "Whale Hunter",
                "bio": "Institutional trader sharing large cap strategies and market insights.",
                "risk_level": RiskLevel.HIGH_RISK,
                "min_copy_amount": Decimal('1000'),
                "max_copy_amount": Decimal('1000000'),
                "subscription_fee": Decimal('100'),
                "profit_sharing": Decimal('20'),
                "tags": ["institutional", "large_cap", "market_making", "arbitrage"]
            }
        ]
        
        for i, trader_data in enumerate(sample_traders):
            trader_id = f"trader_{i+1:03d}"
            
            # Generate realistic trading stats
            total_trades = 500 + (i * 100)
            win_rate = 0.55 + (i * 0.05)
            winning_trades = int(total_trades * win_rate)
            losing_trades = total_trades - winning_trades
            
            avg_win = Decimal('150') + (i * 50)
            avg_loss = Decimal('80') + (i * 20)
            total_profit = avg_win * winning_trades
            total_loss = avg_loss * losing_trades
            net_profit = total_profit - total_loss
            
            stats = TradingStats(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                total_profit=total_profit,
                total_loss=total_loss,
                max_drawdown=Decimal('15.5') - (i * 2),
                sharpe_ratio=1.5 + (i * 0.3),
                sortino_ratio=2.1 + (i * 0.4),
                win_rate=win_rate * 100,
                avg_win=avg_win,
                avg_loss=avg_loss,
                profit_factor=float(total_profit / total_loss) if total_loss > 0 else 0,
                avg_holding_time=timedelta(hours=4 + i),
                volatility=0.15 + (i * 0.05)
            )
            
            trader = CopyTrader(
                id=trader_id,
                username=trader_data["username"],
                display_name=trader_data["display_name"],
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={trader_id}",
                bio=trader_data["bio"],
                status=TraderStatus.ACTIVE,
                verified=True if i < 3 else False,
                featured=True if i < 2 else False,
                risk_level=trader_data["risk_level"],
                min_copy_amount=trader_data["min_copy_amount"],
                max_copy_amount=trader_data["max_copy_amount"],
                subscription_fee=trader_data["subscription_fee"],
                profit_sharing=trader_data["profit_sharing"],
                trading_stats=stats,
                followers_count=150 + (i * 75),
                total_copied_amount=Decimal('500000') + (i * 250000),
                created_at=datetime.now() - timedelta(days=365 - i*30),
                last_active=datetime.now() - timedelta(hours=i),
                tags=trader_data["tags"]
            )
            
            self.traders[trader_id] = trader
            self.metrics['total_traders'] += 1
            self.metrics['active_traders'] += 1
    
    async def get_trader_leaderboard(
        self,
        search_request: SearchTradersRequest
    ) -> List[CopyTrader]:
        """Get trader leaderboard with filtering and sorting"""
        # Filter traders
        filtered_traders = list(self.traders.values())
        
        if search_request.search_query:
            query = search_request.search_query.lower()
            filtered_traders = [
                t for t in filtered_traders
                if query in t.username.lower() or 
                   query in t.display_name.lower() or 
                   query in t.bio.lower() or
                   any(query in tag.lower() for tag in t.tags)
            ]
        
        if search_request.risk_level:
            filtered_traders = [t for t in filtered_traders if t.risk_level == search_request.risk_level]
        
        if search_request.min_followers:
            filtered_traders = [t for t in filtered_traders if t.followers_count >= search_request.min_followers]
        
        if search_request.min_profit:
            filtered_traders = [
                t for t in filtered_traders 
                if float(t.trading_stats.total_profit - t.trading_stats.total_loss) >= search_request.min_profit
            ]
        
        # Sort traders
        sort_key_map = {
            SortBy.PROFIT: lambda t: float(t.trading_stats.total_profit - t.trading_stats.total_loss),
            SortBy.FOLLOWERS: lambda t: t.followers_count,
            SortBy.WIN_RATE: lambda t: t.trading_stats.win_rate,
            SortBy.SHARPE_RATIO: lambda t: t.trading_stats.sharpe_ratio,
            SortBy.RECENT_PERFORMANCE: lambda t: t.followers_count  # Simplified
        }
        
        reverse = search_request.sort_order == "desc"
        filtered_traders.sort(
            key=sort_key_map[search_request.sort_by],
            reverse=reverse
        )
        
        # Paginate
        start = (search_request.page - 1) * search_request.limit
        end = start + search_request.limit
        
        return filtered_traders[start:end]
    
    async def get_trader_details(self, trader_id: str) -> Optional[TraderStatsResponse]:
        """Get detailed trader statistics and performance"""
        trader = self.traders.get(trader_id)
        if not trader:
            return None
        
        # Generate performance chart data
        performance_chart = []
        base_value = 10000
        for i in range(30):  # 30 days
            daily_return = (hash(f"{trader_id}_{i}") % 200 - 100) / 10000  # -1% to +1%
            base_value *= (1 + daily_return)
            performance_chart.append({
                "date": (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d"),
                "value": round(base_value, 2),
                "return": round((base_value - 10000) / 100, 2)
            })
        
        # Generate recent trades
        recent_trades = []
        for i in range(10):
            profit = (hash(f"{trader_id}_trade_{i}") % 400 - 200) / 100  # -200 to +200
            recent_trades.append({
                "symbol": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"][i % 4],
                "side": "buy" if i % 2 == 0 else "sell",
                "profit": str(profit),
                "profit_percentage": round(profit / 1000 * 100, 2),
                "time": (datetime.now() - timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M")
            })
        
        # Risk metrics
        risk_metrics = {
            "var_95": round(trader.trading_stats.volatility * 1.65 * 100, 2),
            "max_drawdown": str(trader.trading_stats.max_drawdown),
            "sharpe_ratio": trader.trading_stats.sharpe_ratio,
            "sortino_ratio": trader.trading_stats.sortino_ratio,
            "volatility": round(trader.trading_stats.volatility * 100, 2),
            "beta": round(1.2 + (hash(trader_id) % 100) / 200, 2),
            "alpha": round(trader.trading_stats.sharpe_ratio * 2, 2)
        }
        
        return TraderStatsResponse(
            trader_id=trader.id,
            username=trader.username,
            display_name=trader.display_name,
            avatar_url=trader.avatar_url,
            verified=trader.verified,
            featured=trader.featured,
            followers_count=trader.followers_count,
            total_copied_amount=str(trader.total_copied_amount),
            trading_stats={
                "total_trades": trader.trading_stats.total_trades,
                "winning_trades": trader.trading_stats.winning_trades,
                "losing_trades": trader.trading_stats.losing_trades,
                "win_rate": trader.trading_stats.win_rate,
                "total_profit": str(trader.trading_stats.total_profit),
                "total_loss": str(trader.trading_stats.total_loss),
                "net_profit": str(trader.trading_stats.total_profit - trader.trading_stats.total_loss),
                "avg_win": str(trader.trading_stats.avg_win),
                "avg_loss": str(trader.trading_stats.avg_loss),
                "profit_factor": trader.trading_stats.profit_factor,
                "max_drawdown": str(trader.trading_stats.max_drawdown),
                "sharpe_ratio": trader.trading_stats.sharpe_ratio,
                "sortino_ratio": trader.trading_stats.sortino_ratio
            },
            performance_chart=performance_chart,
            recent_trades=recent_trades,
            risk_metrics=risk_metrics
        )
    
    async def start_copy_trading(self, user_id: str, settings: CopySettings) -> Follower:
        """Start copy trading a trader"""
        trader = self.traders.get(settings.trader_id)
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        if settings.copy_amount < trader.min_copy_amount:
            raise HTTPException(status_code=400, detail="Copy amount below minimum")
        
        if settings.copy_amount > trader.max_copy_amount:
            raise HTTPException(status_code=400, detail="Copy amount above maximum")
        
        follower_id = f"follower_{uuid.uuid4().hex[:8]}"
        
        follower = Follower(
            id=follower_id,
            user_id=user_id,
            trader_id=settings.trader_id,
            copy_amount=settings.copy_amount,
            auto_copy=settings.auto_copy,
            copy_percentage=settings.copy_percentage,
            max_positions=settings.max_positions,
            risk_multiplier=settings.risk_multiplier,
            stop_loss_percentage=settings.stop_loss_percentage,
            take_profit_percentage=settings.take_profit_percentage,
            status=CopyTradingStatus.ACTIVE,
            total_invested=settings.copy_amount,
            total_return=Decimal('0'),
            created_at=datetime.now(),
            last_copied=datetime.now()
        )
        
        self.followers[settings.trader_id].append(follower)
        
        # Update trader metrics
        trader.followers_count += 1
        trader.total_copied_amount += settings.copy_amount
        
        self.metrics['total_followers'] += 1
        self.metrics['total_copied_amount'] += settings.copy_amount
        
        logger.info(f"User {user_id} started copying trader {settings.trader_id}")
        return follower
    
    async def stop_copy_trading(self, follower_id: str, user_id: str) -> bool:
        """Stop copy trading"""
        # Find and remove follower
        for trader_id, followers in self.followers.items():
            for i, follower in enumerate(followers):
                if follower.id == follower_id and follower.user_id == user_id:
                    follower.status = CopyTradingStatus.STOPPED
                    
                    # Update trader metrics
                    trader = self.traders.get(trader_id)
                    if trader:
                        trader.followers_count -= 1
                        trader.total_copied_amount -= follower.copy_amount
                    
                    return True
        
        return False
    
    async def execute_copy_trade(self, original_order: Dict[str, Any]) -> List[CopyTrade]:
        """Execute copy trades for all followers of a trader"""
        trader_id = original_order.get("trader_id")
        if not trader_id:
            return []
        
        followers = self.followers.get(trader_id, [])
        active_followers = [f for f in followers if f.status == CopyTradingStatus.ACTIVE and f.auto_copy]
        
        copy_trades = []
        for follower in active_followers:
            try:
                # Calculate copy position size
                original_quantity = Decimal(str(original_order.get("quantity", 0)))
                copy_quantity = original_quantity * (follower.copy_percentage / 100)
                copy_quantity *= follower.risk_multiplier
                
                # Apply position limits
                max_position_size = follower.copy_amount / Decimal(str(original_order.get("price", 1)))
                if copy_quantity * Decimal(str(original_order.get("price", 1))) > max_position_size:
                    copy_quantity = max_position_size
                
                # Create copy trade
                copy_trade = CopyTrade(
                    id=f"copy_trade_{uuid.uuid4().hex[:8]}",
                    trader_id=trader_id,
                    follower_id=follower.user_id,
                    original_order_id=original_order.get("order_id"),
                    copied_order_id=f"copy_{uuid.uuid4().hex[:8]}",
                    symbol=original_order.get("symbol"),
                    side=original_order.get("side"),
                    original_quantity=original_quantity,
                    copied_quantity=copy_quantity,
                    original_price=Decimal(str(original_order.get("price", 0))),
                    copied_price=Decimal(str(original_order.get("price", 0))),
                    profit_loss=Decimal('0'),
                    fee=copy_quantity * Decimal(str(original_order.get("price", 0))) * Decimal('0.001'),
                    status=CopyTradingStatus.ACTIVE,
                    created_at=datetime.now()
                )
                
                copy_trades.append(copy_trade)
                self.copy_trades.append(copy_trade)
                
                # Update follower metrics
                follower.last_copied = datetime.now()
                
            except Exception as e:
                logger.error(f"Error executing copy trade for follower {follower.id}: {e}")
        
        if copy_trades:
            self.metrics['total_trades_copied'] += len(copy_trades)
        
        return copy_trades
    
    async def _performance_updater(self):
        """Background task to update performance metrics"""
        while True:
            try:
                for trader in self.traders.values():
                    # Simulate performance updates
                    if trader.status == TraderStatus.ACTIVE:
                        # Update last active time
                        trader.last_active = datetime.now()
                        
                        # Random performance update
                        if hash(f"{trader.id}_{int(time.time())}") % 10 == 0:
                            profit_change = (hash(trader.id) % 200 - 100) / 100
                            trader.trading_stats.total_profit += Decimal(str(profit_change))
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in performance updater: {e}")
                await asyncio.sleep(60)
    
    async def _leaderboard_updater(self):
        """Background task to update leaderboard rankings"""
        while True:
            try:
                # Calculate daily top performer
                if self.traders:
                    top_trader = max(
                        self.traders.values(),
                        key=lambda t: float(t.trading_stats.total_profit - t.trading_stats.total_loss)
                    )
                    daily_profit = top_trader.trading_stats.total_profit - top_trader.trading_stats.total_loss
                    self.metrics['top_trader_daily_profit'] = daily_profit
                
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Error in leaderboard updater: {e}")
                await asyncio.sleep(300)
    
    async def _risk_monitor(self):
        """Background task to monitor risk levels"""
        while True:
            try:
                for trader in self.traders.values():
                    # Check drawdown limits
                    if trader.trading_stats.max_drawdown > Decimal('25'):
                        if trader.status != TraderStatus.SUSPENDED:
                            logger.warning(f"Trader {trader.username} suspended due to high drawdown")
                            trader.status = TraderStatus.SUSPENDED
                    elif trader.status == TraderStatus.SUSPENDED and trader.trading_stats.max_drawdown < Decimal('20'):
                        trader.status = TraderStatus.ACTIVE
                
                await asyncio.sleep(600)  # Check every 10 minutes
            except Exception as e:
                logger.error(f"Error in risk monitor: {e}")
                await asyncio.sleep(600)

# Initialize copy trading engine
copy_trading_engine = EnhancedCopyTradingEngine()

# ==================== API ENDPOINTS ====================

@app.get("/traders/leaderboard")
async def get_trader_leaderboard(
    search_query: Optional[str] = None,
    risk_level: Optional[RiskLevel] = None,
    min_followers: Optional[int] = None,
    min_profit: Optional[float] = None,
    sort_by: SortBy = SortBy.PROFIT,
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 20
):
    """Get trader leaderboard with filtering and sorting"""
    search_request = SearchTradersRequest(
        search_query=search_query,
        risk_level=risk_level,
        min_followers=min_followers,
        min_profit=min_profit,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    
    traders = await copy_trading_engine.get_trader_leaderboard(search_request)
    
    return {
        "traders": [
            {
                "id": trader.id,
                "username": trader.username,
                "display_name": trader.display_name,
                "avatar_url": trader.avatar_url,
                "bio": trader.bio,
                "verified": trader.verified,
                "featured": trader.featured,
                "risk_level": trader.risk_level.value,
                "followers_count": trader.followers_count,
                "total_copied_amount": str(trader.total_copied_amount),
                "subscription_fee": str(trader.subscription_fee),
                "profit_sharing": trader.profit_sharing,
                "tags": trader.tags,
                "trading_stats": {
                    "total_trades": trader.trading_stats.total_trades,
                    "win_rate": trader.trading_stats.win_rate,
                    "net_profit": str(trader.trading_stats.total_profit - trader.trading_stats.total_loss),
                    "sharpe_ratio": trader.trading_stats.sharpe_ratio,
                    "max_drawdown": str(trader.trading_stats.max_drawdown)
                }
            }
            for trader in traders
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(copy_trading_engine.traders)
        }
    }

@app.get("/traders/{trader_id}", response_model=TraderStatsResponse)
async def get_trader_details(trader_id: str):
    """Get detailed trader statistics and performance"""
    trader_details = await copy_trading_engine.get_trader_details(trader_id)
    if not trader_details:
        raise HTTPException(status_code=404, detail="Trader not found")
    return trader_details

@app.post("/copy/start")
async def start_copy_trading(
    settings: CopySettings,
    credentials: str = Depends(security)
):
    """Start copy trading a trader"""
    user_id = "user_123"  # Extract from JWT in production
    
    try:
        follower = await copy_trading_engine.start_copy_trading(user_id, settings)
        return {
            "status": "success",
            "follower_id": follower.id,
            "message": f"Successfully started copying {settings.trader_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/copy/stop/{follower_id}")
async def stop_copy_trading(
    follower_id: str,
    credentials: str = Depends(security)
):
    """Stop copy trading"""
    user_id = "user_123"  # Extract from JWT in production
    
    success = await copy_trading_engine.stop_copy_trading(follower_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Copy trading relationship not found")
    
    return {"status": "success", "message": "Copy trading stopped successfully"}

@app.get("/copy/positions")
async def get_copy_positions(
    credentials: str = Depends(security)
):
    """Get current copy trading positions"""
    user_id = "user_123"  # Extract from JWT in production
    
    positions = []
    for trader_id, pos_list in copy_trading_engine.copy_positions.items():
        for position in pos_list:
            if position.follower_id == user_id:
                positions.append({
                    "id": position.id,
                    "trader_id": position.trader_id,
                    "symbol": position.symbol,
                    "side": position.side,
                    "quantity": str(position.quantity),
                    "entry_price": str(position.entry_price),
                    "current_price": str(position.current_price),
                    "unrealized_pnl": str(position.unrealized_pnl),
                    "percentage_pnl": position.percentage_pnl,
                    "leverage": position.leverage,
                    "created_at": position.created_at
                })
    
    return {"positions": positions}

@app.get("/copy/history")
async def get_copy_history(
    credentials: str = Depends(security),
    limit: int = 50
):
    """Get copy trading history"""
    user_id = "user_123"  # Extract from JWT in production
    
    user_trades = [
        trade for trade in copy_trading_engine.copy_trades
        if trade.follower_id == user_id
    ]
    
    user_trades.sort(key=lambda t: t.created_at, reverse=True)
    
    return {
        "trades": [
            {
                "id": trade.id,
                "trader_id": trade.trader_id,
                "symbol": trade.symbol,
                "side": trade.side,
                "original_quantity": str(trade.original_quantity),
                "copied_quantity": str(trade.copied_quantity),
                "original_price": str(trade.original_price),
                "copied_price": str(trade.copied_price),
                "profit_loss": str(trade.profit_loss),
                "fee": str(trade.fee),
                "status": trade.status.value,
                "created_at": trade.created_at,
                "closed_at": trade.closed_at
            }
            for trade in user_trades[:limit]
        ]
    }

@app.get("/metrics")
async def get_copy_trading_metrics():
    """Get copy trading platform metrics"""
    return {
        "total_traders": copy_trading_engine.metrics['total_traders'],
        "active_traders": copy_trading_engine.metrics['active_traders'],
        "total_followers": copy_trading_engine.metrics['total_followers'],
        "total_copied_amount": str(copy_trading_engine.metrics['total_copied_amount']),
        "total_trades_copied": copy_trading_engine.metrics['total_trades_copied'],
        "total_profit_shared": str(copy_trading_engine.metrics['total_profit_shared']),
        "top_trader_daily_profit": str(copy_trading_engine.metrics['top_trader_daily_profit'])
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    copy_trading_engine.websockets.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        copy_trading_engine.websockets.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced-copy-trading-service",
        "version": "9.0.0",
        "timestamp": datetime.now().isoformat(),
        "metrics": copy_trading_engine.metrics
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_main:app",
        host="0.0.0.0",
        port=3003,
        reload=True,
        log_level="info"
    )