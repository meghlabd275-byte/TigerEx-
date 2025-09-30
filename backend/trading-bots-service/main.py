"""
TigerEx Trading Bots Service
Automated trading bots including Grid, DCA, Martingale, Arbitrage, and Market Making
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Enum as SQLEnum, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import aioredis
import asyncpg
import numpy as np
import pandas as pd
from decimal import Decimal
import ccxt.async_support as ccxt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TigerEx Trading Bots Service",
    description="Automated trading bots with multiple strategies",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/tigerex")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    TRADING_ENGINE_URL = os.getenv("TRADING_ENGINE_URL", "http://localhost:8081")
    MARKET_DATA_URL = os.getenv("MARKET_DATA_URL", "http://localhost:8106")

config = Config()

# Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class BotType(str, Enum):
    GRID = "grid"
    DCA = "dca"
    MARTINGALE = "martingale"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    SMART_REBALANCE = "smart_rebalance"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"

class BotStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

# Database Models
class TradingBot(Base):
    __tablename__ = "trading_bots"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    bot_type = Column(SQLEnum(BotType), nullable=False)
    name = Column(String(255))
    symbol = Column(String(20), nullable=False)
    config = Column(JSON)
    status = Column(SQLEnum(BotStatus), default=BotStatus.CREATED)
    total_profit = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    started_at = Column(DateTime)
    stopped_at = Column(DateTime)

class BotTrade(Base):
    __tablename__ = "bot_trades"
    
    id = Column(BigInteger, primary_key=True, index=True)
    bot_id = Column(BigInteger, nullable=False, index=True)
    order_id = Column(BigInteger)
    symbol = Column(String(20), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    profit_loss = Column(Float, default=0.0)
    fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class BotPerformance(Base):
    __tablename__ = "bot_performance"
    
    id = Column(BigInteger, primary_key=True, index=True)
    bot_id = Column(BigInteger, nullable=False, index=True)
    timestamp = Column(DateTime, default=func.now())
    total_value = Column(Float)
    profit_loss = Column(Float)
    roi = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class BotConfig(BaseModel):
    # Grid Bot Config
    grid_levels: Optional[int] = 10
    price_range_low: Optional[float] = None
    price_range_high: Optional[float] = None
    investment_amount: Optional[float] = None
    
    # DCA Bot Config
    dca_interval: Optional[str] = "1h"  # 1h, 4h, 1d, 1w
    dca_amount: Optional[float] = None
    target_profit: Optional[float] = None
    
    # Martingale Bot Config
    initial_amount: Optional[float] = None
    multiplier: Optional[float] = 2.0
    max_orders: Optional[int] = 5
    
    # Arbitrage Bot Config
    exchanges: Optional[List[str]] = []
    min_profit_percentage: Optional[float] = 0.5
    
    # Market Making Bot Config
    spread_percentage: Optional[float] = 0.2
    order_amount: Optional[float] = None
    max_position: Optional[float] = None
    
    # Common Config
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    max_daily_loss: Optional[float] = None
    trailing_stop: Optional[float] = None

class CreateBotRequest(BaseModel):
    bot_type: BotType
    name: str
    symbol: str
    config: BotConfig

class BotResponse(BaseModel):
    id: int
    user_id: int
    bot_type: BotType
    name: str
    symbol: str
    config: Dict
    status: BotStatus
    total_profit: float
    total_trades: int
    win_rate: float
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]

class BotPerformanceResponse(BaseModel):
    bot_id: int
    total_value: float
    profit_loss: float
    roi: float
    sharpe_ratio: float
    max_drawdown: float
    trades: List[Dict]
    performance_history: List[Dict]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis connection
redis_client = None

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = await aioredis.create_redis_pool(config.REDIS_URL)
    logger.info("Trading Bots Service started")

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        redis_client.close()
        await redis_client.wait_closed()
    logger.info("Trading Bots Service stopped")

# Bot Strategy Implementations
class GridTradingBot:
    """Grid Trading Bot Strategy"""
    
    def __init__(self, bot_id: int, config: BotConfig, symbol: str):
        self.bot_id = bot_id
        self.config = config
        self.symbol = symbol
        self.grid_levels = config.grid_levels
        self.price_low = config.price_range_low
        self.price_high = config.price_range_high
        self.investment = config.investment_amount
        self.orders = []
        
    async def initialize(self):
        """Initialize grid levels and place orders"""
        price_step = (self.price_high - self.price_low) / self.grid_levels
        amount_per_grid = self.investment / self.grid_levels
        
        # Create buy and sell orders at each grid level
        for i in range(self.grid_levels):
            buy_price = self.price_low + (i * price_step)
            sell_price = buy_price + price_step
            
            # Place buy order
            buy_order = {
                "price": buy_price,
                "amount": amount_per_grid / buy_price,
                "side": "buy",
                "status": "pending"
            }
            
            # Place sell order
            sell_order = {
                "price": sell_price,
                "amount": amount_per_grid / buy_price,
                "side": "sell",
                "status": "pending"
            }
            
            self.orders.extend([buy_order, sell_order])
        
        return self.orders
    
    async def execute(self, current_price: float):
        """Execute grid trading logic"""
        executed_orders = []
        
        for order in self.orders:
            if order["status"] == "pending":
                if order["side"] == "buy" and current_price <= order["price"]:
                    # Execute buy order
                    order["status"] = "filled"
                    executed_orders.append(order)
                elif order["side"] == "sell" and current_price >= order["price"]:
                    # Execute sell order
                    order["status"] = "filled"
                    executed_orders.append(order)
        
        return executed_orders

class DCABot:
    """Dollar-Cost Averaging Bot Strategy"""
    
    def __init__(self, bot_id: int, config: BotConfig, symbol: str):
        self.bot_id = bot_id
        self.config = config
        self.symbol = symbol
        self.interval = config.dca_interval
        self.amount = config.dca_amount
        self.target_profit = config.target_profit
        self.total_invested = 0
        self.total_quantity = 0
        self.last_buy_time = None
        
    async def should_buy(self) -> bool:
        """Check if it's time to buy"""
        if self.last_buy_time is None:
            return True
        
        interval_map = {
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1)
        }
        
        time_since_last_buy = datetime.now() - self.last_buy_time
        return time_since_last_buy >= interval_map.get(self.interval, timedelta(hours=1))
    
    async def execute(self, current_price: float):
        """Execute DCA strategy"""
        if await self.should_buy():
            quantity = self.amount / current_price
            self.total_invested += self.amount
            self.total_quantity += quantity
            self.last_buy_time = datetime.now()
            
            avg_price = self.total_invested / self.total_quantity
            current_value = self.total_quantity * current_price
            profit_percentage = ((current_value - self.total_invested) / self.total_invested) * 100
            
            # Check if target profit reached
            if self.target_profit and profit_percentage >= self.target_profit:
                return {
                    "action": "sell_all",
                    "quantity": self.total_quantity,
                    "profit": current_value - self.total_invested
                }
            
            return {
                "action": "buy",
                "price": current_price,
                "quantity": quantity,
                "amount": self.amount
            }
        
        return None

class MartingaleBot:
    """Martingale Trading Bot Strategy"""
    
    def __init__(self, bot_id: int, config: BotConfig, symbol: str):
        self.bot_id = bot_id
        self.config = config
        self.symbol = symbol
        self.initial_amount = config.initial_amount
        self.multiplier = config.multiplier
        self.max_orders = config.max_orders
        self.current_order = 0
        self.current_amount = self.initial_amount
        self.positions = []
        
    async def execute(self, current_price: float, last_trade_result: str):
        """Execute Martingale strategy"""
        if last_trade_result == "loss" and self.current_order < self.max_orders:
            # Double the bet after loss
            self.current_amount *= self.multiplier
            self.current_order += 1
        elif last_trade_result == "win":
            # Reset to initial amount after win
            self.current_amount = self.initial_amount
            self.current_order = 0
        
        if self.current_order < self.max_orders:
            return {
                "action": "buy",
                "price": current_price,
                "amount": self.current_amount,
                "order_number": self.current_order
            }
        
        return None

class ArbitrageBot:
    """Arbitrage Trading Bot Strategy"""
    
    def __init__(self, bot_id: int, config: BotConfig, symbol: str):
        self.bot_id = bot_id
        self.config = config
        self.symbol = symbol
        self.exchanges = config.exchanges
        self.min_profit = config.min_profit_percentage
        
    async def find_arbitrage_opportunity(self, prices: Dict[str, float]):
        """Find arbitrage opportunities across exchanges"""
        if len(prices) < 2:
            return None
        
        min_exchange = min(prices, key=prices.get)
        max_exchange = max(prices, key=prices.get)
        
        min_price = prices[min_exchange]
        max_price = prices[max_exchange]
        
        profit_percentage = ((max_price - min_price) / min_price) * 100
        
        if profit_percentage >= self.min_profit:
            return {
                "buy_exchange": min_exchange,
                "sell_exchange": max_exchange,
                "buy_price": min_price,
                "sell_price": max_price,
                "profit_percentage": profit_percentage
            }
        
        return None

class MarketMakingBot:
    """Market Making Bot Strategy"""
    
    def __init__(self, bot_id: int, config: BotConfig, symbol: str):
        self.bot_id = bot_id
        self.config = config
        self.symbol = symbol
        self.spread = config.spread_percentage
        self.order_amount = config.order_amount
        self.max_position = config.max_position
        self.current_position = 0
        
    async def execute(self, current_price: float, order_book: Dict):
        """Execute market making strategy"""
        buy_price = current_price * (1 - self.spread / 100)
        sell_price = current_price * (1 + self.spread / 100)
        
        orders = []
        
        # Place buy order if not at max position
        if self.current_position < self.max_position:
            orders.append({
                "side": "buy",
                "price": buy_price,
                "amount": self.order_amount
            })
        
        # Place sell order if have position
        if self.current_position > 0:
            orders.append({
                "side": "sell",
                "price": sell_price,
                "amount": self.order_amount
            })
        
        return orders

# Bot Manager
class BotManager:
    """Manages all trading bots"""
    
    def __init__(self):
        self.active_bots: Dict[int, Any] = {}
        self.bot_tasks: Dict[int, asyncio.Task] = {}
    
    async def start_bot(self, bot_id: int, bot_type: BotType, config: BotConfig, symbol: str, db: Session):
        """Start a trading bot"""
        if bot_id in self.active_bots:
            raise HTTPException(status_code=400, detail="Bot already running")
        
        # Create bot instance based on type
        if bot_type == BotType.GRID:
            bot = GridTradingBot(bot_id, config, symbol)
        elif bot_type == BotType.DCA:
            bot = DCABot(bot_id, config, symbol)
        elif bot_type == BotType.MARTINGALE:
            bot = MartingaleBot(bot_id, config, symbol)
        elif bot_type == BotType.ARBITRAGE:
            bot = ArbitrageBot(bot_id, config, symbol)
        elif bot_type == BotType.MARKET_MAKING:
            bot = MarketMakingBot(bot_id, config, symbol)
        else:
            raise HTTPException(status_code=400, detail="Unsupported bot type")
        
        self.active_bots[bot_id] = bot
        
        # Start bot execution task
        task = asyncio.create_task(self._run_bot(bot_id, bot, db))
        self.bot_tasks[bot_id] = task
        
        # Update bot status
        db_bot = db.query(TradingBot).filter(TradingBot.id == bot_id).first()
        db_bot.status = BotStatus.RUNNING
        db_bot.started_at = datetime.now()
        db.commit()
        
        logger.info(f"Started bot {bot_id} of type {bot_type}")
    
    async def stop_bot(self, bot_id: int, db: Session):
        """Stop a trading bot"""
        if bot_id not in self.active_bots:
            raise HTTPException(status_code=404, detail="Bot not found or not running")
        
        # Cancel bot task
        if bot_id in self.bot_tasks:
            self.bot_tasks[bot_id].cancel()
            del self.bot_tasks[bot_id]
        
        # Remove from active bots
        del self.active_bots[bot_id]
        
        # Update bot status
        db_bot = db.query(TradingBot).filter(TradingBot.id == bot_id).first()
        db_bot.status = BotStatus.STOPPED
        db_bot.stopped_at = datetime.now()
        db.commit()
        
        logger.info(f"Stopped bot {bot_id}")
    
    async def _run_bot(self, bot_id: int, bot: Any, db: Session):
        """Run bot execution loop"""
        try:
            while True:
                # Get current market price
                # This would call the market data service
                current_price = await self._get_current_price(bot.symbol)
                
                # Execute bot strategy
                if isinstance(bot, GridTradingBot):
                    orders = await bot.execute(current_price)
                    # Process orders
                elif isinstance(bot, DCABot):
                    result = await bot.execute(current_price)
                    # Process result
                elif isinstance(bot, MartingaleBot):
                    result = await bot.execute(current_price, "win")  # Placeholder
                    # Process result
                elif isinstance(bot, MarketMakingBot):
                    orders = await bot.execute(current_price, {})
                    # Process orders
                
                # Update bot performance
                await self._update_performance(bot_id, db)
                
                # Sleep before next iteration
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info(f"Bot {bot_id} execution cancelled")
        except Exception as e:
            logger.error(f"Error in bot {bot_id}: {str(e)}")
            db_bot = db.query(TradingBot).filter(TradingBot.id == bot_id).first()
            db_bot.status = BotStatus.ERROR
            db.commit()
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        # This would call the market data service
        # Placeholder implementation
        return 50000.0
    
    async def _update_performance(self, bot_id: int, db: Session):
        """Update bot performance metrics"""
        # Calculate and store performance metrics
        pass

# Initialize bot manager
bot_manager = BotManager()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "trading-bots-service",
        "version": "1.0.0"
    }

@app.post("/api/v1/bots/create", response_model=BotResponse)
async def create_bot(
    request: CreateBotRequest,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Create a new trading bot"""
    try:
        # Create bot in database
        db_bot = TradingBot(
            user_id=user_id,
            bot_type=request.bot_type,
            name=request.name,
            symbol=request.symbol,
            config=request.config.dict(),
            status=BotStatus.CREATED
        )
        
        db.add(db_bot)
        db.commit()
        db.refresh(db_bot)
        
        logger.info(f"Created bot {db_bot.id} for user {user_id}")
        
        return BotResponse(
            id=db_bot.id,
            user_id=db_bot.user_id,
            bot_type=db_bot.bot_type,
            name=db_bot.name,
            symbol=db_bot.symbol,
            config=db_bot.config,
            status=db_bot.status,
            total_profit=db_bot.total_profit,
            total_trades=db_bot.total_trades,
            win_rate=db_bot.win_rate,
            created_at=db_bot.created_at,
            started_at=db_bot.started_at,
            stopped_at=db_bot.stopped_at
        )
        
    except Exception as e:
        logger.error(f"Error creating bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/bots/list")
async def list_bots(
    user_id: int = 1,  # TODO: Get from auth
    status: Optional[BotStatus] = None,
    db: Session = Depends(get_db)
):
    """List all bots for a user"""
    query = db.query(TradingBot).filter(TradingBot.user_id == user_id)
    
    if status:
        query = query.filter(TradingBot.status == status)
    
    bots = query.all()
    
    return {
        "bots": [
            BotResponse(
                id=bot.id,
                user_id=bot.user_id,
                bot_type=bot.bot_type,
                name=bot.name,
                symbol=bot.symbol,
                config=bot.config,
                status=bot.status,
                total_profit=bot.total_profit,
                total_trades=bot.total_trades,
                win_rate=bot.win_rate,
                created_at=bot.created_at,
                started_at=bot.started_at,
                stopped_at=bot.stopped_at
            )
            for bot in bots
        ]
    }

@app.get("/api/v1/bots/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Get bot details"""
    bot = db.query(TradingBot).filter(
        TradingBot.id == bot_id,
        TradingBot.user_id == user_id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return BotResponse(
        id=bot.id,
        user_id=bot.user_id,
        bot_type=bot.bot_type,
        name=bot.name,
        symbol=bot.symbol,
        config=bot.config,
        status=bot.status,
        total_profit=bot.total_profit,
        total_trades=bot.total_trades,
        win_rate=bot.win_rate,
        created_at=bot.created_at,
        started_at=bot.started_at,
        stopped_at=bot.stopped_at
    )

@app.post("/api/v1/bots/{bot_id}/start")
async def start_bot(
    bot_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Start a trading bot"""
    bot = db.query(TradingBot).filter(
        TradingBot.id == bot_id,
        TradingBot.user_id == user_id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    if bot.status == BotStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    # Start bot
    config = BotConfig(**bot.config)
    await bot_manager.start_bot(bot_id, bot.bot_type, config, bot.symbol, db)
    
    return {"message": "Bot started successfully", "bot_id": bot_id}

@app.post("/api/v1/bots/{bot_id}/stop")
async def stop_bot(
    bot_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Stop a trading bot"""
    bot = db.query(TradingBot).filter(
        TradingBot.id == bot_id,
        TradingBot.user_id == user_id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Stop bot
    await bot_manager.stop_bot(bot_id, db)
    
    return {"message": "Bot stopped successfully", "bot_id": bot_id}

@app.delete("/api/v1/bots/{bot_id}")
async def delete_bot(
    bot_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Delete a trading bot"""
    bot = db.query(TradingBot).filter(
        TradingBot.id == bot_id,
        TradingBot.user_id == user_id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Stop bot if running
    if bot.status == BotStatus.RUNNING:
        await bot_manager.stop_bot(bot_id, db)
    
    # Delete bot
    db.delete(bot)
    db.commit()
    
    return {"message": "Bot deleted successfully", "bot_id": bot_id}

@app.get("/api/v1/bots/{bot_id}/performance", response_model=BotPerformanceResponse)
async def get_bot_performance(
    bot_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: Session = Depends(get_db)
):
    """Get bot performance metrics"""
    bot = db.query(TradingBot).filter(
        TradingBot.id == bot_id,
        TradingBot.user_id == user_id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Get trades
    trades = db.query(BotTrade).filter(BotTrade.bot_id == bot_id).all()
    
    # Get performance history
    performance = db.query(BotPerformance).filter(
        BotPerformance.bot_id == bot_id
    ).order_by(BotPerformance.timestamp.desc()).limit(100).all()
    
    # Calculate metrics
    total_value = sum(trade.quantity * trade.price for trade in trades)
    profit_loss = bot.total_profit
    roi = (profit_loss / total_value * 100) if total_value > 0 else 0
    
    return BotPerformanceResponse(
        bot_id=bot_id,
        total_value=total_value,
        profit_loss=profit_loss,
        roi=roi,
        sharpe_ratio=0.0,  # TODO: Calculate
        max_drawdown=0.0,  # TODO: Calculate
        trades=[
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "price": trade.price,
                "quantity": trade.quantity,
                "profit_loss": trade.profit_loss,
                "created_at": trade.created_at.isoformat()
            }
            for trade in trades
        ],
        performance_history=[
            {
                "timestamp": perf.timestamp.isoformat(),
                "total_value": perf.total_value,
                "profit_loss": perf.profit_loss,
                "roi": perf.roi
            }
            for perf in performance
        ]
    )

@app.get("/api/v1/bots/types")
async def get_bot_types():
    """Get available bot types and their descriptions"""
    return {
        "bot_types": [
            {
                "type": "grid",
                "name": "Grid Trading Bot",
                "description": "Places buy and sell orders at regular intervals in a price range",
                "parameters": ["grid_levels", "price_range_low", "price_range_high", "investment_amount"]
            },
            {
                "type": "dca",
                "name": "DCA Bot",
                "description": "Dollar-cost averaging strategy that buys at regular intervals",
                "parameters": ["dca_interval", "dca_amount", "target_profit"]
            },
            {
                "type": "martingale",
                "name": "Martingale Bot",
                "description": "Doubles position size after losses to recover",
                "parameters": ["initial_amount", "multiplier", "max_orders"]
            },
            {
                "type": "arbitrage",
                "name": "Arbitrage Bot",
                "description": "Exploits price differences across exchanges",
                "parameters": ["exchanges", "min_profit_percentage"]
            },
            {
                "type": "market_making",
                "name": "Market Making Bot",
                "description": "Provides liquidity by placing buy and sell orders",
                "parameters": ["spread_percentage", "order_amount", "max_position"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8110)