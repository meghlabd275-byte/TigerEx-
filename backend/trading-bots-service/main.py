from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
from enum import Enum
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis
from collections import defaultdict
import numpy as np
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trading Bots Service", version="3.0.00.0")

# Include admin router
app.include_router(admin_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/trading_bots"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup for real-time data
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, bot_id: str):
        await websocket.accept()
        self.active_connections[bot_id] = websocket
        logger.info(f"WebSocket connected for bot {bot_id}")

    def disconnect(self, bot_id: str):
        if bot_id in self.active_connections:
            del self.active_connections[bot_id]
            logger.info(f"WebSocket disconnected for bot {bot_id}")

    async def send_update(self, bot_id: str, message: dict):
        if bot_id in self.active_connections:
            try:
                await self.active_connections[bot_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending update to bot {bot_id}: {e}")
                self.disconnect(bot_id)

    async def broadcast(self, message: dict):
        for bot_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to bot {bot_id}: {e}")

manager = ConnectionManager()

# Database Models
class BotDB(Base):
    __tablename__ = "bots"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    bot_type = Column(String, nullable=False)
    trading_pair = Column(String, nullable=False)
    status = Column(String, default="stopped")
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)

class BotPerformanceDB(Base):
    __tablename__ = "bot_performance"
    
    id = Column(String, primary_key=True)
    bot_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)

class BotTradeDB(Base):
    __tablename__ = "bot_trades"
    
    id = Column(String, primary_key=True)
    bot_id = Column(String, nullable=False, index=True)
    trade_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    profit_loss = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")

class BotRiskMetricsDB(Base):
    __tablename__ = "bot_risk_metrics"
    
    id = Column(String, primary_key=True)
    bot_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    position_size = Column(Float, default=0.0)
    leverage = Column(Float, default=1.0)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_score = Column(Float, default=0.0)
    exposure = Column(Float, default=0.0)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enums
class BotType(str, Enum):
    GRID = "grid"
    DCA = "dca"
    MARTINGALE = "martingale"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"

class BotStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"

# Pydantic Models
class BotCreate(BaseModel):
    name: str
    bot_type: BotType
    trading_pair: str
    config: Dict[str, Any]

class BotResponse(BaseModel):
    id: str
    user_id: str
    name: str
    bot_type: str
    trading_pair: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

class PerformanceMetrics(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit: float
    total_loss: float
    net_profit: float
    roi: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float

# Bot Execution Logic
class TradingBot:
    def __init__(self, bot_id: str, user_id: str, bot_type: str, trading_pair: str, config: Dict, db: Session):
        self.bot_id = bot_id
        self.user_id = user_id
        self.bot_type = bot_type
        self.trading_pair = trading_pair
        self.config = config
        self.db = db
        self.is_running = False
        self.performance_data = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "total_loss": 0.0
        }

    async def start(self):
        self.is_running = True
        logger.info(f"Starting bot {self.bot_id} of type {self.bot_type}")
        
        bot = self.db.query(BotDB).filter(BotDB.id == self.bot_id).first()
        if bot:
            bot.status = "running"
            bot.started_at = datetime.utcnow()
            self.db.commit()
        
        if self.bot_type == "grid":
            await self.run_grid_bot()
        elif self.bot_type == "dca":
            await self.run_dca_bot()
        elif self.bot_type == "martingale":
            await self.run_martingale_bot()
        elif self.bot_type == "arbitrage":
            await self.run_arbitrage_bot()
        elif self.bot_type == "market_making":
            await self.run_market_making_bot()

    async def stop(self):
        self.is_running = False
        logger.info(f"Stopping bot {self.bot_id}")
        
        bot = self.db.query(BotDB).filter(BotDB.id == self.bot_id).first()
        if bot:
            bot.status = "stopped"
            bot.stopped_at = datetime.utcnow()
            self.db.commit()

    async def run_grid_bot(self):
        grid_levels = self.config.get("grid_levels", 10)
        price_low = self.config.get("price_range_low", 30000)
        price_high = self.config.get("price_range_high", 50000)
        
        while self.is_running:
            try:
                current_price = random.uniform(price_low, price_high)
                await manager.send_update(self.bot_id, {
                    "type": "grid_update",
                    "current_price": current_price,
                    "performance": self.performance_data
                })
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error in grid bot: {e}")
                await asyncio.sleep(5)

    async def run_dca_bot(self):
        while self.is_running:
            await asyncio.sleep(10)

    async def run_martingale_bot(self):
        while self.is_running:
            await asyncio.sleep(10)

    async def run_arbitrage_bot(self):
        while self.is_running:
            await asyncio.sleep(10)

    async def run_market_making_bot(self):
        while self.is_running:
            await asyncio.sleep(10)

active_bots: Dict[str, TradingBot] = {}

# API Endpoints
@app.post("/bots", response_model=BotResponse)
async def create_bot(bot: BotCreate, user_id: str = "user123", db: Session = Depends(get_db)):
    bot_id = str(uuid.uuid4())
    db_bot = BotDB(
        id=bot_id,
        user_id=user_id,
        name=bot.name,
        bot_type=bot.bot_type,
        trading_pair=bot.trading_pair,
        status="stopped",
        config=bot.config,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    
    return BotResponse(
        id=db_bot.id,
        user_id=db_bot.user_id,
        name=db_bot.name,
        bot_type=db_bot.bot_type,
        trading_pair=db_bot.trading_pair,
        status=db_bot.status,
        config=db_bot.config,
        created_at=db_bot.created_at,
        updated_at=db_bot.updated_at
    )

@app.get("/bots", response_model=List[BotResponse])
async def list_bots(user_id: str = "user123", db: Session = Depends(get_db)):
    bots = db.query(BotDB).filter(BotDB.user_id == user_id).all()
    return [BotResponse(
        id=bot.id,
        user_id=bot.user_id,
        name=bot.name,
        bot_type=bot.bot_type,
        trading_pair=bot.trading_pair,
        status=bot.status,
        config=bot.config,
        created_at=bot.created_at,
        updated_at=bot.updated_at
    ) for bot in bots]

@app.post("/bots/{bot_id}/start")
async def start_bot(bot_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    bot = db.query(BotDB).filter(BotDB.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    trading_bot = TradingBot(bot.id, bot.user_id, bot.bot_type, bot.trading_pair, bot.config, db)
    active_bots[bot_id] = trading_bot
    background_tasks.add_task(trading_bot.start)
    
    return {"message": "Bot started", "bot_id": bot_id}

@app.post("/bots/{bot_id}/stop")
async def stop_bot(bot_id: str):
    if bot_id not in active_bots:
        raise HTTPException(status_code=400, detail="Bot not running")
    await active_bots[bot_id].stop()
    del active_bots[bot_id]
    return {"message": "Bot stopped", "bot_id": bot_id}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "active_bots": len(active_bots)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)