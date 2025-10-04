import os
"""
TigerEx Enhanced Trading Engine
High-performance order matching and trade execution
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import asyncio
from collections import defaultdict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Enhanced Trading Engine", version="1.0.0")

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

# In-memory order books (for high performance)
order_books: Dict[str, Dict] = defaultdict(lambda: {"bids": [], "asks": []})

# Enums
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TimeInForce(str, Enum):
    GTC = "gtc"  # Good Till Cancel
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill
    DAY = "day"  # Day order

# Models
class OrderRequest(BaseModel):
    user_id: int
    pair: str
    order_type: OrderType
    side: OrderSide
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    stop_price: Optional[Decimal] = Field(None, gt=0)
    time_in_force: TimeInForce = TimeInForce.GTC
    post_only: bool = False
    reduce_only: bool = False

class Order(BaseModel):
    order_id: int
    user_id: int
    pair: str
    order_type: str
    side: str
    quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal
    price: Optional[Decimal]
    average_price: Optional[Decimal]
    status: str
    time_in_force: str
    created_at: datetime
    updated_at: datetime

class Trade(BaseModel):
    trade_id: int
    order_id: int
    pair: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    fee_currency: str
    is_maker: bool
    created_at: datetime

class OrderBook(BaseModel):
    pair: str
    bids: List[List[Decimal]]  # [[price, quantity], ...]
    asks: List[List[Decimal]]  # [[price, quantity], ...]
    timestamp: datetime

class TickerData(BaseModel):
    pair: str
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    volume_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    price_change_24h: Decimal
    price_change_percent_24h: Decimal
    timestamp: datetime

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
        database="tigerex_trading",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create orders table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                pair VARCHAR(50) NOT NULL,
                order_type VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                quantity DECIMAL(36, 18) NOT NULL,
                filled_quantity DECIMAL(36, 18) DEFAULT 0,
                remaining_quantity DECIMAL(36, 18) NOT NULL,
                price DECIMAL(36, 18),
                stop_price DECIMAL(36, 18),
                average_price DECIMAL(36, 18),
                status VARCHAR(20) NOT NULL,
                time_in_force VARCHAR(10) NOT NULL,
                post_only BOOLEAN DEFAULT FALSE,
                reduce_only BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_orders (user_id, created_at DESC),
                INDEX idx_pair_status (pair, status),
                INDEX idx_status (status)
            )
        """)
        
        # Create trades table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                maker_order_id INTEGER,
                taker_order_id INTEGER,
                pair VARCHAR(50) NOT NULL,
                side VARCHAR(10) NOT NULL,
                quantity DECIMAL(36, 18) NOT NULL,
                price DECIMAL(36, 18) NOT NULL,
                fee DECIMAL(36, 18) NOT NULL,
                fee_currency VARCHAR(20) NOT NULL,
                is_maker BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_order_trades (order_id),
                INDEX idx_pair_trades (pair, created_at DESC)
            )
        """)
        
        # Create order book snapshots table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS order_book_snapshots (
                snapshot_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                bids JSONB NOT NULL,
                asks JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair_snapshots (pair, created_at DESC)
            )
        """)
        
        # Create ticker data table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ticker_data (
                ticker_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL,
                last_price DECIMAL(36, 18) NOT NULL,
                bid_price DECIMAL(36, 18),
                ask_price DECIMAL(36, 18),
                volume_24h DECIMAL(36, 18),
                high_24h DECIMAL(36, 18),
                low_24h DECIMAL(36, 18),
                price_change_24h DECIMAL(36, 18),
                price_change_percent_24h DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair_ticker (pair, created_at DESC)
            )
        """)
        
        # Create trading pairs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_pairs (
                pair_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL UNIQUE,
                base_currency VARCHAR(20) NOT NULL,
                quote_currency VARCHAR(20) NOT NULL,
                min_order_size DECIMAL(36, 18) NOT NULL,
                max_order_size DECIMAL(36, 18),
                price_precision INTEGER NOT NULL,
                quantity_precision INTEGER NOT NULL,
                maker_fee DECIMAL(10, 8) NOT NULL,
                taker_fee DECIMAL(10, 8) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair (pair)
            )
        """)
        
        # Insert default trading pairs
        await conn.execute("""
            INSERT INTO trading_pairs (
                pair, base_currency, quote_currency, min_order_size,
                price_precision, quantity_precision, maker_fee, taker_fee
            ) VALUES 
                ('BTC/USDT', 'BTC', 'USDT', 0.0001, 2, 8, 0.001, 0.001),
                ('ETH/USDT', 'ETH', 'USDT', 0.001, 2, 8, 0.001, 0.001),
                ('BNB/USDT', 'BNB', 'USDT', 0.01, 2, 8, 0.001, 0.001)
            ON CONFLICT (pair) DO NOTHING
        """)
        
        logger.info("Database initialized successfully")

# Order matching engine
class OrderMatchingEngine:
    """High-performance order matching engine"""
    
    @staticmethod
    async def match_order(order: Dict, db: asyncpg.Pool) -> List[Dict]:
        """Match an order against the order book"""
        pair = order['pair']
        side = order['side']
        trades = []
        
        # Get opposite side orders
        opposite_side = 'sell' if side == 'buy' else 'buy'
        
        # Get matching orders from database
        matching_orders = await db.fetch("""
            SELECT * FROM orders
            WHERE pair = $1 AND side = $2 AND status = 'open'
            AND remaining_quantity > 0
            ORDER BY 
                CASE WHEN $2 = 'sell' THEN price END ASC,
                CASE WHEN $2 = 'buy' THEN price END DESC,
                created_at ASC
        """, pair, opposite_side)
        
        remaining_qty = order['remaining_quantity']
        
        for match_order in matching_orders:
            if remaining_qty <= 0:
                break
            
            # Check price compatibility
            if side == 'buy':
                if order['order_type'] == 'limit' and match_order['price'] > order['price']:
                    continue
            else:
                if order['order_type'] == 'limit' and match_order['price'] < order['price']:
                    continue
            
            # Calculate trade quantity
            trade_qty = min(remaining_qty, match_order['remaining_quantity'])
            trade_price = match_order['price']
            
            # Calculate fees
            maker_fee = trade_qty * trade_price * Decimal('0.001')
            taker_fee = trade_qty * trade_price * Decimal('0.001')
            
            # Create trade record
            trade = {
                'order_id': order['order_id'],
                'maker_order_id': match_order['order_id'],
                'taker_order_id': order['order_id'],
                'pair': pair,
                'side': side,
                'quantity': trade_qty,
                'price': trade_price,
                'maker_fee': maker_fee,
                'taker_fee': taker_fee
            }
            
            trades.append(trade)
            remaining_qty -= trade_qty
            
            # Update matched order
            await db.execute("""
                UPDATE orders
                SET filled_quantity = filled_quantity + $2,
                    remaining_quantity = remaining_quantity - $2,
                    status = CASE 
                        WHEN remaining_quantity - $2 <= 0 THEN 'filled'
                        ELSE 'partially_filled'
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_id = $1
            """, match_order['order_id'], trade_qty)
        
        # Update original order
        await db.execute("""
            UPDATE orders
            SET filled_quantity = filled_quantity + $2,
                remaining_quantity = remaining_quantity - $2,
                status = CASE 
                    WHEN remaining_quantity - $2 <= 0 THEN 'filled'
                    WHEN filled_quantity > 0 THEN 'partially_filled'
                    ELSE status
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE order_id = $1
        """, order['order_id'], order['remaining_quantity'] - remaining_qty)
        
        return trades

# API Endpoints
@app.post("/api/v1/trading/order", response_model=Order)
async def place_order(
    request: OrderRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Pool = Depends(get_db)
):
    """Place a new order"""
    try:
        # Validate trading pair
        pair_info = await db.fetchrow("""
            SELECT * FROM trading_pairs WHERE pair = $1 AND is_active = TRUE
        """, request.pair)
        
        if not pair_info:
            raise HTTPException(status_code=400, detail="Invalid or inactive trading pair")
        
        # Validate order size
        if request.quantity < pair_info['min_order_size']:
            raise HTTPException(status_code=400, detail=f"Order size below minimum: {pair_info['min_order_size']}")
        
        if pair_info['max_order_size'] and request.quantity > pair_info['max_order_size']:
            raise HTTPException(status_code=400, detail=f"Order size above maximum: {pair_info['max_order_size']}")
        
        # Validate price for limit orders
        if request.order_type == OrderType.LIMIT and not request.price:
            raise HTTPException(status_code=400, detail="Price required for limit orders")
        
        # Create order
        order = await db.fetchrow("""
            INSERT INTO orders (
                user_id, pair, order_type, side, quantity, remaining_quantity,
                price, stop_price, status, time_in_force, post_only, reduce_only
            ) VALUES ($1, $2, $3, $4, $5, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *
        """, request.user_id, request.pair, request.order_type.value, request.side.value,
            request.quantity, request.price, request.stop_price, OrderStatus.OPEN.value,
            request.time_in_force.value, request.post_only, request.reduce_only)
        
        # Match order in background
        if request.order_type == OrderType.MARKET or request.order_type == OrderType.LIMIT:
            background_tasks.add_task(OrderMatchingEngine.match_order, dict(order), db)
        
        logger.info("order_placed",
                   order_id=order['order_id'],
                   user_id=request.user_id,
                   pair=request.pair,
                   side=request.side.value)
        
        return Order(
            order_id=order['order_id'],
            user_id=order['user_id'],
            pair=order['pair'],
            order_type=order['order_type'],
            side=order['side'],
            quantity=order['quantity'],
            filled_quantity=order['filled_quantity'],
            remaining_quantity=order['remaining_quantity'],
            price=order['price'],
            average_price=order['average_price'],
            status=order['status'],
            time_in_force=order['time_in_force'],
            created_at=order['created_at'],
            updated_at=order['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("place_order_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Order placement failed: {str(e)}")

@app.delete("/api/v1/trading/order/{order_id}")
async def cancel_order(
    order_id: int,
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Cancel an order"""
    try:
        # Verify order ownership
        order = await db.fetchrow("""
            SELECT * FROM orders WHERE order_id = $1 AND user_id = $2
        """, order_id, user_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order['status'] not in ['open', 'partially_filled']:
            raise HTTPException(status_code=400, detail="Order cannot be cancelled")
        
        # Cancel order
        await db.execute("""
            UPDATE orders
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE order_id = $1
        """, order_id)
        
        logger.info("order_cancelled", order_id=order_id, user_id=user_id)
        return {"message": "Order cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("cancel_order_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trading/orders/{user_id}", response_model=List[Order])
async def get_user_orders(
    user_id: int,
    pair: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user orders"""
    try:
        query = "SELECT * FROM orders WHERE user_id = $1"
        params = [user_id]
        
        if pair:
            query += " AND pair = $2"
            params.append(pair)
        
        if status:
            query += f" AND status = ${len(params) + 1}"
            params.append(status.value)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        orders = await db.fetch(query, *params)
        
        return [
            Order(
                order_id=o['order_id'],
                user_id=o['user_id'],
                pair=o['pair'],
                order_type=o['order_type'],
                side=o['side'],
                quantity=o['quantity'],
                filled_quantity=o['filled_quantity'],
                remaining_quantity=o['remaining_quantity'],
                price=o['price'],
                average_price=o['average_price'],
                status=o['status'],
                time_in_force=o['time_in_force'],
                created_at=o['created_at'],
                updated_at=o['updated_at']
            )
            for o in orders
        ]
        
    except Exception as e:
        logger.error("get_user_orders_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trading/orderbook/{pair}", response_model=OrderBook)
async def get_order_book(
    pair: str,
    depth: int = 20,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get order book for a trading pair"""
    try:
        # Get bids (buy orders)
        bids = await db.fetch("""
            SELECT price, SUM(remaining_quantity) as quantity
            FROM orders
            WHERE pair = $1 AND side = 'buy' AND status = 'open'
            GROUP BY price
            ORDER BY price DESC
            LIMIT $2
        """, pair, depth)
        
        # Get asks (sell orders)
        asks = await db.fetch("""
            SELECT price, SUM(remaining_quantity) as quantity
            FROM orders
            WHERE pair = $1 AND side = 'sell' AND status = 'open'
            GROUP BY price
            ORDER BY price ASC
            LIMIT $2
        """, pair, depth)
        
        return OrderBook(
            pair=pair,
            bids=[[b['price'], b['quantity']] for b in bids],
            asks=[[a['price'], a['quantity']] for a in asks],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("get_order_book_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trading/ticker/{pair}", response_model=TickerData)
async def get_ticker(
    pair: str,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get ticker data for a trading pair"""
    try:
        # Get latest trade
        last_trade = await db.fetchrow("""
            SELECT price FROM trades
            WHERE pair = $1
            ORDER BY created_at DESC
            LIMIT 1
        """, pair)
        
        # Get 24h statistics
        stats = await db.fetchrow("""
            SELECT
                MAX(price) as high_24h,
                MIN(price) as low_24h,
                SUM(quantity) as volume_24h
            FROM trades
            WHERE pair = $1 AND created_at >= NOW() - INTERVAL '24 hours'
        """, pair)
        
        # Get best bid and ask
        best_bid = await db.fetchval("""
            SELECT MAX(price) FROM orders
            WHERE pair = $1 AND side = 'buy' AND status = 'open'
        """, pair)
        
        best_ask = await db.fetchval("""
            SELECT MIN(price) FROM orders
            WHERE pair = $1 AND side = 'sell' AND status = 'open'
        """, pair)
        
        last_price = last_trade['price'] if last_trade else Decimal(0)
        
        return TickerData(
            pair=pair,
            last_price=last_price,
            bid_price=best_bid or Decimal(0),
            ask_price=best_ask or Decimal(0),
            volume_24h=stats['volume_24h'] or Decimal(0),
            high_24h=stats['high_24h'] or Decimal(0),
            low_24h=stats['low_24h'] or Decimal(0),
            price_change_24h=Decimal(0),
            price_change_percent_24h=Decimal(0),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("get_ticker_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trading/trades/{pair}", response_model=List[Trade])
async def get_recent_trades(
    pair: str,
    limit: int = 50,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get recent trades for a pair"""
    try:
        trades = await db.fetch("""
            SELECT * FROM trades
            WHERE pair = $1
            ORDER BY created_at DESC
            LIMIT $2
        """, pair, limit)
        
        return [
            Trade(
                trade_id=t['trade_id'],
                order_id=t['order_id'],
                pair=t['pair'],
                side=t['side'],
                quantity=t['quantity'],
                price=t['price'],
                fee=t['fee'],
                fee_currency=t['fee_currency'],
                is_maker=t['is_maker'],
                created_at=t['created_at']
            )
            for t in trades
        ]
        
    except Exception as e:
        logger.error("get_recent_trades_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "trading-engine-enhanced",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Enhanced Trading Engine started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Enhanced Trading Engine stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8280)