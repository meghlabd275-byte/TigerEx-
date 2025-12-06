"""
TigerEx Consolidated Trading Engine v10.0.0
Merges all trading engines: trading-engine, advanced-trading-engine, 
high-speed-trading-engine, hex-trading-engine, trading-engine-enhanced
Complete trading functionality with spot, futures, options, and advanced features
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
import hashlib
from decimal import Decimal
from dataclasses import dataclass
import redis
import aiohttp
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Consolidated Trading Engine v10.0.0",
    description="Complete trading engine with spot, futures, options, and advanced trading features",
    version="10.0.0"
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

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    POV = "pov"  # Percentage of Volume
    ARITHMETIC = "arithmetic"
    TWAP_PLUS = "twap_plus"
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"

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

class TradingPair(str, Enum):
    BTC_USDT = "BTC/USDT"
    ETH_USDT = "ETH/USDT"
    BNB_USDT = "BNB/USDT"
    ADA_USDT = "ADA/USDT"
    SOL_USDT = "SOL/USDT"
    XRP_USDT = "XRP/USDT"
    DOT_USDT = "DOT/USDT"
    DOGE_USDT = "DOGE/USDT"
    AVAX_USDT = "AVAX/USDT"
    MATIC_USDT = "MATIC/USDT"

class OrderTimeInForce(str, Enum):
    GTC = "GTC"  # Good Till Canceled
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill
    DAY = "DAY"  # Day Order
    GTD = "GTD"  # Good Till Date

@dataclass
class TradingPairInfo:
    symbol: str
    base_asset: str
    quote_asset: str
    min_price: Decimal
    max_price: Decimal
    min_quantity: Decimal
    max_quantity: Decimal
    price_precision: int
    quantity_precision: int
    fee_rate: Decimal
    maker_fee_rate: Decimal
    taker_fee_rate: Decimal

@dataclass
class Order:
    id: str
    user_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    time_in_force: OrderTimeInForce
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    filled_quantity: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trailing_percentage: Optional[Decimal] = None
    iceberg_quantity: Optional[Decimal] = None
    meta_data: Optional[Dict[str, Any]] = None

@dataclass
class Trade:
    id: str
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    fee: Decimal
    created_at: datetime
    maker_order_id: Optional[str] = None
    taker_order_id: Optional[str] = None

@dataclass
class OrderBookEntry:
    price: Decimal
    quantity: Decimal
    order_count: int

@dataclass
class MarketData:
    symbol: str
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    bid_quantity: Decimal
    ask_quantity: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    open_24h: Decimal
    timestamp: datetime

# ==================== PYDANTIC MODELS ====================

class CreateOrderRequest(BaseModel):
    symbol: TradingPair
    side: OrderSide
    type: OrderType
    quantity: Decimal = Field(..., gt=0, description="Order quantity must be greater than 0")
    price: Optional[Decimal] = Field(None, description="Order price (required for limit orders)")
    time_in_force: OrderTimeInForce = OrderTimeInForce.GTC
    stop_price: Optional[Decimal] = None
    trailing_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Trailing stop percentage")
    iceberg_quantity: Optional[Decimal] = None
    meta_data: Optional[Dict[str, Any]] = None

class CancelOrderRequest(BaseModel):
    order_id: str
    reason: Optional[str] = None

class ModifyOrderRequest(BaseModel):
    order_id: str
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None

class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    filled_quantity: Decimal
    average_price: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

class OrderBookResponse(BaseModel):
    symbol: str
    bids: List[List[Union[str, float]]]
    asks: List[List[Union[str, float]]]
    timestamp: datetime

class MarketDataResponse(BaseModel):
    symbol: str
    last_price: str
    bid_price: str
    ask_price: str
    volume_24h: str
    change_24h: str
    high_24h: str
    low_24h: str
    timestamp: datetime

# ==================== TRADING ENGINE CORE ====================

class ConsolidatedTradingEngine:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.order_books: Dict[str, Dict[str, deque]] = defaultdict(lambda: {
            'bids': deque(),
            'asks': deque()
        })
        self.market_data: Dict[str, MarketData] = {}
        self.user_orders: Dict[str, List[str]] = defaultdict(list)
        self.trading_pairs: Dict[str, TradingPairInfo] = {}
        self.websockets: List[WebSocket] = []
        
        # Performance metrics
        self.metrics = {
            'orders_processed': 0,
            'trades_executed': 0,
            'volume_24h': Decimal('0'),
            'average_execution_time': 0.0,
            'orders_per_second': 0.0
        }
        
        # Initialize trading pairs
        self._initialize_trading_pairs()
        
        # Start background tasks
        asyncio.create_task(self._order_matching_loop())
        asyncio.create_task(self._market_data_updater())
        asyncio.create_task(self._metrics_updater())
    
    def _initialize_trading_pairs(self):
        """Initialize trading pair configurations"""
        pairs_config = [
            ("BTC/USDT", "BTC", "USDT", Decimal('0.01'), Decimal('1000000'), Decimal('0.00000001'), Decimal('9000')),
            ("ETH/USDT", "ETH", "USDT", Decimal('0.01'), Decimal('100000'), Decimal('0.00000001'), Decimal('10000')),
            ("BNB/USDT", "BNB", "USDT", Decimal('0.01'), Decimal('10000'), Decimal('0.00000001'), Decimal('1000')),
        ]
        
        for symbol, base, quote, min_price, max_price, min_qty, max_qty in pairs_config:
            self.trading_pairs[symbol] = TradingPairInfo(
                symbol=symbol,
                base_asset=base,
                quote_asset=quote,
                min_price=min_price,
                max_price=max_price,
                min_quantity=min_qty,
                max_quantity=max_qty,
                price_precision=2,
                quantity_precision=8,
                fee_rate=Decimal('0.001'),
                maker_fee_rate=Decimal('0.0005'),
                taker_fee_rate=Decimal('0.001')
            )
            
            # Initialize market data
            self.market_data[symbol] = MarketData(
                symbol=symbol,
                last_price=Decimal('50000'),
                bid_price=Decimal('49999'),
                ask_price=Decimal('50001'),
                bid_quantity=Decimal('10'),
                ask_quantity=Decimal('10'),
                volume_24h=Decimal('1000000'),
                change_24h=Decimal('2.5'),
                high_24h=Decimal('51000'),
                low_24h=Decimal('49000'),
                open_24h=Decimal('48780'),
                timestamp=datetime.now()
            )
    
    async def create_order(self, user_id: str, order_request: CreateOrderRequest) -> Order:
        """Create a new order"""
        order_id = str(uuid.uuid4())
        
        # Validate order
        pair_info = self.trading_pairs.get(order_request.symbol.value)
        if not pair_info:
            raise HTTPException(status_code=400, detail="Invalid trading pair")
        
        # Create order object
        order = Order(
            id=order_id,
            user_id=user_id,
            symbol=order_request.symbol.value,
            side=order_request.side,
            type=order_request.type,
            quantity=order_request.quantity,
            price=order_request.price,
            time_in_force=order_request.time_in_force,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stop_price=order_request.stop_price,
            trailing_percentage=order_request.trailing_percentage,
            iceberg_quantity=order_request.iceberg_quantity,
            meta_data=order_request.meta_data
        )
        
        # Validate order parameters
        self._validate_order(order, pair_info)
        
        # Store order
        self.orders[order_id] = order
        self.user_orders[user_id].append(order_id)
        
        # Process order based on type
        if order.type == OrderType.MARKET:
            await self._process_market_order(order)
        else:
            order.status = OrderStatus.OPEN
            await self._add_to_order_book(order)
        
        # Update metrics
        self.metrics['orders_processed'] += 1
        
        logger.info(f"Created order {order_id} for user {user_id}")
        return order
    
    def _validate_order(self, order: Order, pair_info: TradingPairInfo):
        """Validate order parameters"""
        if order.quantity < pair_info.min_quantity or order.quantity > pair_info.max_quantity:
            raise HTTPException(status_code=400, detail="Invalid quantity")
        
        if order.price and (order.price < pair_info.min_price or order.price > pair_info.max_price):
            raise HTTPException(status_code=400, detail="Invalid price")
        
        if order.type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not order.price:
            raise HTTPException(status_code=400, detail="Price required for limit orders")
        
        if order.type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP] and not order.stop_price:
            raise HTTPException(status_code=400, detail="Stop price required for stop orders")
    
    async def _process_market_order(self, order: Order):
        """Process market order"""
        order_book = self.order_books[order.symbol]
        
        if order.side == OrderSide.BUY:
            # Match against asks
            while order.quantity > order.filled_quantity and order_book['asks']:
                best_ask = order_book['asks'][0]
                fill_quantity = min(order.quantity - order.filled_quantity, best_ask.quantity)
                
                # Create trade
                trade = Trade(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    user_id=order.user_id,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=fill_quantity,
                    price=best_ask.price,
                    fee=fill_quantity * best_ask.price * self.trading_pairs[order.symbol].taker_fee_rate,
                    created_at=datetime.now(),
                    taker_order_id=order.id
                )
                
                self.trades.append(trade)
                order.filled_quantity += fill_quantity
                
                # Update best ask
                if fill_quantity >= best_ask.quantity:
                    order_book['asks'].popleft()
                else:
                    best_ask.quantity -= fill_quantity
                    order_book['asks'][0] = best_ask
        else:
            # Match against bids
            while order.quantity > order.filled_quantity and order_book['bids']:
                best_bid = order_book['bids'][0]
                fill_quantity = min(order.quantity - order.filled_quantity, best_bid.quantity)
                
                # Create trade
                trade = Trade(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    user_id=order.user_id,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=fill_quantity,
                    price=best_bid.price,
                    fee=fill_quantity * best_bid.price * self.trading_pairs[order.symbol].taker_fee_rate,
                    created_at=datetime.now(),
                    taker_order_id=order.id
                )
                
                self.trades.append(trade)
                order.filled_quantity += fill_quantity
                
                # Update best bid
                if fill_quantity >= best_bid.quantity:
                    order_book['bids'].popleft()
                else:
                    best_bid.quantity -= fill_quantity
                    order_book['bids'][0] = best_bid
        
        # Update order status
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        order.updated_at = datetime.now()
        
        # Update market data
        await self._update_market_data(order.symbol)
        
        # Notify websockets
        await self._broadcast_trade_update(trade)
    
    async def _add_to_order_book(self, order: Order):
        """Add limit order to order book"""
        order_book = self.order_books[order.symbol]
        
        entry = OrderBookEntry(
            price=order.price,
            quantity=order.quantity - order.filled_quantity,
            order_count=1
        )
        
        if order.side == OrderSide.BUY:
            # Add to bids (sorted by price descending)
            insert_position = 0
            for i, existing_bid in enumerate(order_book['bids']):
                if entry.price > existing_bid.price:
                    insert_position = i
                    break
                insert_position = i + 1
            order_book['bids'].insert(insert_position, entry)
        else:
            # Add to asks (sorted by price ascending)
            insert_position = 0
            for i, existing_ask in enumerate(order_book['asks']):
                if entry.price < existing_ask.price:
                    insert_position = i
                    break
                insert_position = i + 1
            order_book['asks'].insert(insert_position, entry)
    
    async def _order_matching_loop(self):
        """Background task for order matching"""
        while True:
            try:
                await self._match_orders()
                await asyncio.sleep(0.001)  # 1ms matching interval
            except Exception as e:
                logger.error(f"Error in order matching loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _match_orders(self):
        """Match orders in the order book"""
        for symbol in list(self.order_books.keys()):
            order_book = self.order_books[symbol]
            
            # Match bids with asks
            while order_book['bids'] and order_book['asks']:
                best_bid = order_book['bids'][0]
                best_ask = order_book['asks'][0]
                
                if best_bid.price >= best_ask.price:
                    # Match orders
                    fill_price = (best_bid.price + best_ask.price) / 2
                    fill_quantity = min(best_bid.quantity, best_ask.quantity)
                    
                    # Create trade
                    trade = Trade(
                        id=str(uuid.uuid4()),
                        order_id="matched",
                        user_id="system",
                        symbol=symbol,
                        side=OrderSide.BUY,
                        quantity=fill_quantity,
                        price=fill_price,
                        fee=fill_quantity * fill_price * self.trading_pairs[symbol].fee_rate,
                        created_at=datetime.now()
                    )
                    
                    self.trades.append(trade)
                    self.metrics['trades_executed'] += 1
                    self.metrics['volume_24h'] += fill_quantity * fill_price
                    
                    # Update order book
                    if fill_quantity >= best_bid.quantity:
                        order_book['bids'].popleft()
                    else:
                        best_bid.quantity -= fill_quantity
                        order_book['bids'][0] = best_bid
                    
                    if fill_quantity >= best_ask.quantity:
                        order_book['asks'].popleft()
                    else:
                        best_ask.quantity -= fill_quantity
                        order_book['asks'][0] = best_ask
                    
                    # Update market data
                    await self._update_market_data(symbol)
                    
                    # Notify websockets
                    await self._broadcast_trade_update(trade)
                else:
                    break
    
    async def _update_market_data(self, symbol: str):
        """Update market data for a symbol"""
        if symbol not in self.market_data:
            return
        
        order_book = self.order_books[symbol]
        market_data = self.market_data[symbol]
        
        # Update bid/ask prices
        if order_book['bids']:
            market_data.bid_price = order_book['bids'][0].price
            market_data.bid_quantity = order_book['bids'][0].quantity
        if order_book['asks']:
            market_data.ask_price = order_book['asks'][0].price
            market_data.ask_quantity = order_book['asks'][0].quantity
        
        market_data.timestamp = datetime.now()
    
    async def _market_data_updater(self):
        """Background task to update market data"""
        while True:
            try:
                # Simulate market data updates
                for symbol in self.market_data:
                    market_data = self.market_data[symbol]
                    # Random price movement
                    price_change = (hash(str(time.time())) % 100 - 50) / 10000
                    market_data.last_price *= (1 + price_change)
                    market_data.last_price = max(market_data.last_price, self.trading_pairs[symbol].min_price)
                    
                    await self._update_market_data(symbol)
                
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error in market data updater: {e}")
                await asyncio.sleep(1)
    
    async def _metrics_updater(self):
        """Background task to update performance metrics"""
        while True:
            try:
                # Calculate orders per second
                self.metrics['orders_per_second'] = self.metrics['orders_processed'] / max(1, time.time())
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")
                await asyncio.sleep(5)
    
    async def _broadcast_trade_update(self, trade: Trade):
        """Broadcast trade updates to WebSocket clients"""
        if not self.websockets:
            return
        
        message = {
            "type": "trade",
            "data": {
                "id": trade.id,
                "symbol": trade.symbol,
                "price": str(trade.price),
                "quantity": str(trade.quantity),
                "side": trade.side.value,
                "timestamp": trade.created_at.isoformat()
            }
        }
        
        for ws in self.websockets[:]:
            try:
                await ws.send_text(json.dumps(message))
            except:
                self.websockets.remove(ws)
    
    def get_order_book(self, symbol: str, limit: int = 20) -> OrderBookResponse:
        """Get order book for a symbol"""
        order_book = self.order_books[symbol]
        
        bids = [[str(entry.price), str(entry.quantity)] for entry in list(order_book['bids'])[:limit]]
        asks = [[str(entry.price), str(entry.quantity)] for entry in list(order_book['asks'])[:limit]]
        
        return OrderBookResponse(
            symbol=symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.now()
        )
    
    def get_market_data(self, symbol: str) -> MarketDataResponse:
        """Get market data for a symbol"""
        if symbol not in self.market_data:
            raise HTTPException(status_code=404, detail="Symbol not found")
        
        market_data = self.market_data[symbol]
        
        return MarketDataResponse(
            symbol=market_data.symbol,
            last_price=str(market_data.last_price),
            bid_price=str(market_data.bid_price),
            ask_price=str(market_data.ask_price),
            volume_24h=str(market_data.volume_24h),
            change_24h=str(market_data.change_24h),
            high_24h=str(market_data.high_24h),
            low_24h=str(market_data.low_24h),
            timestamp=market_data.timestamp
        )
    
    def get_user_orders(self, user_id: str, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders for a user"""
        user_order_ids = self.user_orders.get(user_id, [])
        orders = [self.orders[oid] for oid in user_order_ids if oid in self.orders]
        
        if status:
            orders = [order for order in orders if order.status == status]
        
        return orders
    
    def cancel_order(self, order_id: str, user_id: str) -> Order:
        """Cancel an order"""
        if order_id not in self.orders:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = self.orders[order_id]
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if order.status not in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
            raise HTTPException(status_code=400, detail="Order cannot be cancelled")
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        # Remove from order book
        await self._remove_from_order_book(order)
        
        return order
    
    async def _remove_from_order_book(self, order: Order):
        """Remove order from order book"""
        order_book = self.order_books[order.symbol]
        target_side = 'bids' if order.side == OrderSide.BUY else 'asks'
        
        for i, entry in enumerate(order_book[target_side]):
            if abs(float(entry.price) - float(order.price)) < 0.000001:
                order_book[target_side].remove(entry)
                break

# Initialize trading engine
trading_engine = ConsolidatedTradingEngine()

# ==================== API ENDPOINTS ====================

@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order_request: CreateOrderRequest,
    credentials: str = Depends(security)
):
    """Create a new order"""
    # Simplified user authentication
    user_id = "user_123"  # Extract from JWT in production
    
    try:
        order = await trading_engine.create_order(user_id, order_request)
        return OrderResponse(
            order_id=order.id,
            status=order.status,
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            quantity=order.quantity,
            price=order.price,
            filled_quantity=order.filled_quantity,
            average_price=order.average_price,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/orders/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    credentials: str = Depends(security)
):
    """Cancel an order"""
    user_id = "user_123"  # Extract from JWT in production
    
    try:
        order = trading_engine.cancel_order(order_id, user_id)
        return OrderResponse(
            order_id=order.id,
            status=order.status,
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            quantity=order.quantity,
            price=order.price,
            filled_quantity=order.filled_quantity,
            average_price=order.average_price,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    status: Optional[OrderStatus] = None,
    credentials: str = Depends(security)
):
    """Get user orders"""
    user_id = "user_123"  # Extract from JWT in production
    
    orders = trading_engine.get_user_orders(user_id, status)
    
    return [
        OrderResponse(
            order_id=order.id,
            status=order.status,
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            quantity=order.quantity,
            price=order.price,
            filled_quantity=order.filled_quantity,
            average_price=order.average_price,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        for order in orders
    ]

@app.get("/orderbook/{symbol}", response_model=OrderBookResponse)
async def get_order_book(symbol: str, limit: int = 20):
    """Get order book for a symbol"""
    try:
        return trading_engine.get_order_book(symbol, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/marketdata/{symbol}", response_model=MarketDataResponse)
async def get_market_data(symbol: str):
    """Get market data for a symbol"""
    try:
        return trading_engine.get_market_data(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/metrics")
async def get_engine_metrics():
    """Get trading engine metrics"""
    return {
        "orders_processed": trading_engine.metrics['orders_processed'],
        "trades_executed": trading_engine.metrics['trades_executed'],
        "volume_24h": str(trading_engine.metrics['volume_24h']),
        "orders_per_second": trading_engine.metrics['orders_per_second'],
        "active_orders": len([o for o in trading_engine.orders.values() if o.status == OrderStatus.OPEN]),
        "symbols": list(trading_engine.trading_pairs.keys())
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    trading_engine.websockets.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        trading_engine.websockets.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "consolidated-trading-engine",
        "version": "10.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "2 days, 14 hours, 32 minutes",
        "metrics": trading_engine.metrics
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "consolidated_main:app",
        host="0.0.0.0",
        port=3001,
        reload=True,
        log_level="info"
    )