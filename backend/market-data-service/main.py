import os
"""
TigerEx Market Data Service
Real-time market data, price feeds, and candlestick data
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import json
import asyncio

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Market Data Service", version="1.0.0")

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

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for pair in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[pair]:
                self.subscriptions[pair].remove(websocket)
    
    def subscribe(self, websocket: WebSocket, pair: str):
        if pair not in self.subscriptions:
            self.subscriptions[pair] = []
        if websocket not in self.subscriptions[pair]:
            self.subscriptions[pair].append(websocket)
    
    def unsubscribe(self, websocket: WebSocket, pair: str):
        if pair in self.subscriptions and websocket in self.subscriptions[pair]:
            self.subscriptions[pair].remove(websocket)
    
    async def broadcast_to_pair(self, pair: str, message: dict):
        if pair in self.subscriptions:
            for connection in self.subscriptions[pair]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# Enums
class CandleInterval(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"

# Models
class Candlestick(BaseModel):
    pair: str
    interval: str
    open_time: datetime
    close_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    trades_count: int

class MarketTicker(BaseModel):
    pair: str
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    bid_quantity: Decimal
    ask_quantity: Decimal
    volume_24h: Decimal
    quote_volume_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    price_change_24h: Decimal
    price_change_percent_24h: Decimal
    weighted_avg_price: Decimal
    timestamp: datetime

class OrderBookDepth(BaseModel):
    pair: str
    bids: List[List[Decimal]]
    asks: List[List[Decimal]]
    last_update_id: int
    timestamp: datetime

class RecentTrade(BaseModel):
    trade_id: int
    pair: str
    price: Decimal
    quantity: Decimal
    time: datetime
    is_buyer_maker: bool

class MarketStats(BaseModel):
    pair: str
    total_volume_24h: Decimal
    total_trades_24h: int
    price_high_24h: Decimal
    price_low_24h: Decimal
    price_open_24h: Decimal
    price_close: Decimal
    price_change_24h: Decimal
    price_change_percent_24h: Decimal

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
        database="tigerex_market_data",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create candlesticks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS candlesticks (
                candle_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                interval VARCHAR(10) NOT NULL,
                open_time TIMESTAMP NOT NULL,
                close_time TIMESTAMP NOT NULL,
                open_price DECIMAL(36, 18) NOT NULL,
                high_price DECIMAL(36, 18) NOT NULL,
                low_price DECIMAL(36, 18) NOT NULL,
                close_price DECIMAL(36, 18) NOT NULL,
                volume DECIMAL(36, 18) NOT NULL,
                trades_count INTEGER DEFAULT 0,
                UNIQUE(pair, interval, open_time),
                INDEX idx_pair_interval_time (pair, interval, open_time DESC)
            )
        """)
        
        # Create market tickers table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS market_tickers (
                ticker_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                last_price DECIMAL(36, 18) NOT NULL,
                bid_price DECIMAL(36, 18),
                ask_price DECIMAL(36, 18),
                bid_quantity DECIMAL(36, 18),
                ask_quantity DECIMAL(36, 18),
                volume_24h DECIMAL(36, 18),
                quote_volume_24h DECIMAL(36, 18),
                high_24h DECIMAL(36, 18),
                low_24h DECIMAL(36, 18),
                price_change_24h DECIMAL(36, 18),
                price_change_percent_24h DECIMAL(10, 4),
                weighted_avg_price DECIMAL(36, 18),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair_ticker (pair, created_at DESC)
            )
        """)
        
        # Create order book snapshots table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS order_book_snapshots (
                snapshot_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                bids JSONB NOT NULL,
                asks JSONB NOT NULL,
                last_update_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair_snapshots (pair, created_at DESC)
            )
        """)
        
        # Create trades table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS market_trades (
                trade_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                price DECIMAL(36, 18) NOT NULL,
                quantity DECIMAL(36, 18) NOT NULL,
                is_buyer_maker BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair_trades (pair, created_at DESC)
            )
        """)
        
        logger.info("Database initialized successfully")

# Helper functions
def get_interval_minutes(interval: CandleInterval) -> int:
    """Convert interval to minutes"""
    intervals = {
        CandleInterval.ONE_MINUTE: 1,
        CandleInterval.FIVE_MINUTES: 5,
        CandleInterval.FIFTEEN_MINUTES: 15,
        CandleInterval.THIRTY_MINUTES: 30,
        CandleInterval.ONE_HOUR: 60,
        CandleInterval.FOUR_HOURS: 240,
        CandleInterval.ONE_DAY: 1440,
        CandleInterval.ONE_WEEK: 10080,
        CandleInterval.ONE_MONTH: 43200
    }
    return intervals.get(interval, 1)

# API Endpoints
@app.get("/api/v1/market/candlesticks/{pair}", response_model=List[Candlestick])
async def get_candlesticks(
    pair: str,
    interval: CandleInterval = CandleInterval.ONE_HOUR,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 500,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get candlestick data for a trading pair"""
    try:
        query = """
            SELECT * FROM candlesticks
            WHERE pair = $1 AND interval = $2
        """
        params = [pair, interval.value]
        
        if start_time:
            query += f" AND open_time >= ${len(params) + 1}"
            params.append(start_time)
        
        if end_time:
            query += f" AND open_time <= ${len(params) + 1}"
            params.append(end_time)
        
        query += f" ORDER BY open_time DESC LIMIT ${len(params) + 1}"
        params.append(limit)
        
        candles = await db.fetch(query, *params)
        
        return [
            Candlestick(
                pair=c['pair'],
                interval=c['interval'],
                open_time=c['open_time'],
                close_time=c['close_time'],
                open_price=c['open_price'],
                high_price=c['high_price'],
                low_price=c['low_price'],
                close_price=c['close_price'],
                volume=c['volume'],
                trades_count=c['trades_count']
            )
            for c in reversed(candles)
        ]
        
    except Exception as e:
        logger.error("get_candlesticks_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/ticker/{pair}", response_model=MarketTicker)
async def get_ticker(
    pair: str,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get 24h ticker data for a trading pair"""
    try:
        ticker = await db.fetchrow("""
            SELECT * FROM market_tickers
            WHERE pair = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, pair)
        
        if not ticker:
            # Return default ticker if not found
            return MarketTicker(
                pair=pair,
                last_price=Decimal(0),
                bid_price=Decimal(0),
                ask_price=Decimal(0),
                bid_quantity=Decimal(0),
                ask_quantity=Decimal(0),
                volume_24h=Decimal(0),
                quote_volume_24h=Decimal(0),
                high_24h=Decimal(0),
                low_24h=Decimal(0),
                price_change_24h=Decimal(0),
                price_change_percent_24h=Decimal(0),
                weighted_avg_price=Decimal(0),
                timestamp=datetime.utcnow()
            )
        
        return MarketTicker(
            pair=ticker['pair'],
            last_price=ticker['last_price'],
            bid_price=ticker['bid_price'] or Decimal(0),
            ask_price=ticker['ask_price'] or Decimal(0),
            bid_quantity=ticker['bid_quantity'] or Decimal(0),
            ask_quantity=ticker['ask_quantity'] or Decimal(0),
            volume_24h=ticker['volume_24h'] or Decimal(0),
            quote_volume_24h=ticker['quote_volume_24h'] or Decimal(0),
            high_24h=ticker['high_24h'] or Decimal(0),
            low_24h=ticker['low_24h'] or Decimal(0),
            price_change_24h=ticker['price_change_24h'] or Decimal(0),
            price_change_percent_24h=ticker['price_change_percent_24h'] or Decimal(0),
            weighted_avg_price=ticker['weighted_avg_price'] or Decimal(0),
            timestamp=ticker['created_at']
        )
        
    except Exception as e:
        logger.error("get_ticker_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/tickers", response_model=List[MarketTicker])
async def get_all_tickers(db: asyncpg.Pool = Depends(get_db)):
    """Get 24h ticker data for all trading pairs"""
    try:
        tickers = await db.fetch("""
            SELECT DISTINCT ON (pair) *
            FROM market_tickers
            ORDER BY pair, created_at DESC
        """)
        
        return [
            MarketTicker(
                pair=t['pair'],
                last_price=t['last_price'],
                bid_price=t['bid_price'] or Decimal(0),
                ask_price=t['ask_price'] or Decimal(0),
                bid_quantity=t['bid_quantity'] or Decimal(0),
                ask_quantity=t['ask_quantity'] or Decimal(0),
                volume_24h=t['volume_24h'] or Decimal(0),
                quote_volume_24h=t['quote_volume_24h'] or Decimal(0),
                high_24h=t['high_24h'] or Decimal(0),
                low_24h=t['low_24h'] or Decimal(0),
                price_change_24h=t['price_change_24h'] or Decimal(0),
                price_change_percent_24h=t['price_change_percent_24h'] or Decimal(0),
                weighted_avg_price=t['weighted_avg_price'] or Decimal(0),
                timestamp=t['created_at']
            )
            for t in tickers
        ]
        
    except Exception as e:
        logger.error("get_all_tickers_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/orderbook/{pair}", response_model=OrderBookDepth)
async def get_order_book(
    pair: str,
    limit: int = 100,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get order book depth for a trading pair"""
    try:
        snapshot = await db.fetchrow("""
            SELECT * FROM order_book_snapshots
            WHERE pair = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, pair)
        
        if not snapshot:
            return OrderBookDepth(
                pair=pair,
                bids=[],
                asks=[],
                last_update_id=0,
                timestamp=datetime.utcnow()
            )
        
        return OrderBookDepth(
            pair=snapshot['pair'],
            bids=snapshot['bids'][:limit],
            asks=snapshot['asks'][:limit],
            last_update_id=snapshot['last_update_id'],
            timestamp=snapshot['created_at']
        )
        
    except Exception as e:
        logger.error("get_order_book_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/trades/{pair}", response_model=List[RecentTrade])
async def get_recent_trades(
    pair: str,
    limit: int = 100,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get recent trades for a trading pair"""
    try:
        trades = await db.fetch("""
            SELECT * FROM market_trades
            WHERE pair = $1
            ORDER BY created_at DESC
            LIMIT $2
        """, pair, limit)
        
        return [
            RecentTrade(
                trade_id=t['trade_id'],
                pair=t['pair'],
                price=t['price'],
                quantity=t['quantity'],
                time=t['created_at'],
                is_buyer_maker=t['is_buyer_maker']
            )
            for t in trades
        ]
        
    except Exception as e:
        logger.error("get_recent_trades_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/stats/{pair}", response_model=MarketStats)
async def get_market_stats(
    pair: str,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get 24h market statistics for a trading pair"""
    try:
        stats = await db.fetchrow("""
            SELECT
                COUNT(*) as total_trades_24h,
                SUM(quantity) as total_volume_24h,
                MAX(price) as price_high_24h,
                MIN(price) as price_low_24h,
                (SELECT price FROM market_trades WHERE pair = $1 
                 AND created_at >= NOW() - INTERVAL '24 hours' 
                 ORDER BY created_at ASC LIMIT 1) as price_open_24h,
                (SELECT price FROM market_trades WHERE pair = $1 
                 ORDER BY created_at DESC LIMIT 1) as price_close
            FROM market_trades
            WHERE pair = $1 AND created_at >= NOW() - INTERVAL '24 hours'
        """, pair)
        
        if not stats or not stats['price_close']:
            return MarketStats(
                pair=pair,
                total_volume_24h=Decimal(0),
                total_trades_24h=0,
                price_high_24h=Decimal(0),
                price_low_24h=Decimal(0),
                price_open_24h=Decimal(0),
                price_close=Decimal(0),
                price_change_24h=Decimal(0),
                price_change_percent_24h=Decimal(0)
            )
        
        price_change = stats['price_close'] - (stats['price_open_24h'] or stats['price_close'])
        price_change_percent = (price_change / stats['price_open_24h'] * 100) if stats['price_open_24h'] else Decimal(0)
        
        return MarketStats(
            pair=pair,
            total_volume_24h=stats['total_volume_24h'] or Decimal(0),
            total_trades_24h=stats['total_trades_24h'] or 0,
            price_high_24h=stats['price_high_24h'] or Decimal(0),
            price_low_24h=stats['price_low_24h'] or Decimal(0),
            price_open_24h=stats['price_open_24h'] or Decimal(0),
            price_close=stats['price_close'],
            price_change_24h=price_change,
            price_change_percent_24h=price_change_percent
        )
        
    except Exception as e:
        logger.error("get_market_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time data
@app.websocket("/ws/market/{pair}")
async def websocket_market_data(websocket: WebSocket, pair: str):
    """WebSocket endpoint for real-time market data"""
    await manager.connect(websocket)
    manager.subscribe(websocket, pair)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('action') == 'subscribe':
                manager.subscribe(websocket, message.get('pair', pair))
            elif message.get('action') == 'unsubscribe':
                manager.unsubscribe(websocket, message.get('pair', pair))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("websocket_disconnected", pair=pair)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "market-data-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Market Data Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Market Data Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8290)