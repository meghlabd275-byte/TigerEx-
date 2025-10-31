"""
Orbit Exchange Service - Custom Exchange Implementation
Complete custom exchange with full functionality
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import aiohttp
import asyncio
import hashlib
import hmac
import base64
import json
import logging

app = FastAPI(title="Orbit Exchange Service", version="1.0.0")
security = HTTPBearer()

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TradingPair(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    min_order_size: float
    max_order_size: float
    price_precision: int
    quantity_precision: int
    trading_fee: float
    status: str

class Order(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    order_type: OrderType
    order_side: OrderSide
    quantity: float
    price: Optional[float]
    filled_quantity: float
    remaining_quantity: float
    average_price: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    stop_price: Optional[float] = None

class Trade(BaseModel):
    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float
    created_at: datetime

class Balance(BaseModel):
    user_id: str
    currency: str
    available: float
    frozen: float
    total: float

class OrbitExchange:
    def __init__(self):
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.order_books: Dict[str, Dict] = {}
        self.balances: Dict[str, Dict[str, Balance]] = {}
        
        self.initialize_trading_pairs()
        self.initialize_order_books()
    
    def initialize_trading_pairs(self):
        """Initialize trading pairs"""
        pairs = [
            TradingPair(
                symbol="BTC/USDT",
                base_currency="BTC",
                quote_currency="USDT",
                min_order_size=0.001,
                max_order_size=1000,
                price_precision=2,
                quantity_precision=8,
                trading_fee=0.001,
                status="active"
            ),
            TradingPair(
                symbol="ETH/USDT",
                base_currency="ETH",
                quote_currency="USDT",
                min_order_size=0.01,
                max_order_size=10000,
                price_precision=2,
                quantity_precision=8,
                trading_fee=0.001,
                status="active"
            ),
            TradingPair(
                symbol="ETH/BTC",
                base_currency="ETH",
                quote_currency="BTC",
                min_order_size=0.001,
                max_order_size=100,
                price_precision=5,
                quantity_precision=8,
                trading_fee=0.002,
                status="active"
            ),
            TradingPair(
                symbol="BNB/USDT",
                base_currency="BNB",
                quote_currency="USDT",
                min_order_size=0.1,
                max_order_size=50000,
                price_precision=2,
                quantity_precision=8,
                trading_fee=0.001,
                status="active"
            ),
            TradingPair(
                symbol="ADA/USDT",
                base_currency="ADA",
                quote_currency="USDT",
                min_order_size=1,
                max_order_size=1000000,
                price_precision=4,
                quantity_precision=2,
                trading_fee=0.001,
                status="active"
            )
        ]
        
        for pair in pairs:
            self.trading_pairs[pair.symbol] = pair
    
    def initialize_order_books(self):
        """Initialize order books with some depth"""
        for symbol in self.trading_pairs.keys():
            self.order_books[symbol] = {
                "bids": [],
                "asks": []
            }
            
            # Add some initial liquidity
            if symbol == "BTC/USDT":
                base_price = 45000.0
            elif symbol == "ETH/USDT":
                base_price = 3000.0
            elif symbol == "ETH/BTC":
                base_price = 0.067
            elif symbol == "BNB/USDT":
                base_price = 300.0
            elif symbol == "ADA/USDT":
                base_price = 1.5
            else:
                base_price = 1.0
            
            # Generate mock order book
            for i in range(50):
                # Bids
                bid_price = base_price * (1 - (i + 1) * 0.001)
                bid_qty = 1.0 + i * 0.1
                self.order_books[symbol]["bids"].append([bid_price, bid_qty])
                
                # Asks
                ask_price = base_price * (1 + (i + 1) * 0.001)
                ask_qty = 1.0 + i * 0.1
                self.order_books[symbol]["asks"].append([ask_price, ask_qty])
            
            # Sort order book
            self.order_books[symbol]["bids"].sort(key=lambda x: x[0], reverse=True)
            self.order_books[symbol]["asks"].sort(key=lambda x: x[0])
    
    def match_order(self, order: Order) -> List[Trade]:
        """Match order against order book"""
        trades = []
        symbol = order.symbol
        order_book = self.order_books[symbol]
        
        if order.order_side == OrderSide.BUY:
            # Match against asks
            i = 0
            while i < len(order_book["asks"]) and order.remaining_quantity > 0:
                ask_price, ask_qty = order_book["asks"][i]
                
                if (order.order_type == OrderType.MARKET) or \
                   (order.order_type == OrderType.LIMIT and order.price >= ask_price):
                    
                    trade_qty = min(order.remaining_quantity, ask_qty)
                    trade_price = ask_price
                    
                    # Create trade
                    trade = Trade(
                        trade_id=f"trade_{int(datetime.utcnow().timestamp())}_{len(self.trades)}",
                        order_id=order.order_id,
                        symbol=symbol,
                        side=OrderSide.BUY,
                        quantity=trade_qty,
                        price=trade_price,
                        fee=trade_qty * trade_price * self.trading_pairs[symbol].trading_fee,
                        created_at=datetime.utcnow()
                    )
                    trades.append(trade)
                    
                    # Update order
                    order.filled_quantity += trade_qty
                    order.remaining_quantity -= trade_qty
                    
                    if order.filled_quantity > 0:
                        order.average_price = (
                            (order.average_price * (order.filled_quantity - trade_qty) + trade_price * trade_qty) /
                            order.filled_quantity
                        )
                    
                    # Update order book
                    if ask_qty > trade_qty:
                        order_book["asks"][i][1] -= trade_qty
                    else:
                        del order_book["asks"][i]
                        i -= 1
                else:
                    break
                
                i += 1
        else:
            # Match against bids
            i = 0
            while i < len(order_book["bids"]) and order.remaining_quantity > 0:
                bid_price, bid_qty = order_book["bids"][i]
                
                if (order.order_type == OrderType.MARKET) or \
                   (order.order_type == OrderType.LIMIT and order.price <= bid_price):
                    
                    trade_qty = min(order.remaining_quantity, bid_qty)
                    trade_price = bid_price
                    
                    # Create trade
                    trade = Trade(
                        trade_id=f"trade_{int(datetime.utcnow().timestamp())}_{len(self.trades)}",
                        order_id=order.order_id,
                        symbol=symbol,
                        side=OrderSide.SELL,
                        quantity=trade_qty,
                        price=trade_price,
                        fee=trade_qty * trade_price * self.trading_pairs[symbol].trading_fee,
                        created_at=datetime.utcnow()
                    )
                    trades.append(trade)
                    
                    # Update order
                    order.filled_quantity += trade_qty
                    order.remaining_quantity -= trade_qty
                    
                    if order.filled_quantity > 0:
                        order.average_price = (
                            (order.average_price * (order.filled_quantity - trade_qty) + trade_price * trade_qty) /
                            order.filled_quantity
                        )
                    
                    # Update order book
                    if bid_qty > trade_qty:
                        order_book["bids"][i][1] -= trade_qty
                    else:
                        del order_book["bids"][i]
                        i -= 1
                else:
                    break
                
                i += 1
        
        # Add remaining quantity to order book if not fully filled
        if order.remaining_quantity > 0 and order.order_type == OrderType.LIMIT:
            if order.order_side == OrderSide.BUY:
                # Insert into bids
                self.insert_into_order_book(order_book["bids"], [order.price, order.remaining_quantity], True)
            else:
                # Insert into asks
                self.insert_into_order_book(order_book["asks"], [order.price, order.remaining_quantity], False)
        
        # Update order status
        if order.remaining_quantity == 0:
            order.status = OrderStatus.FILLED
        elif order.filled_quantity > 0:
            order.status = OrderStatus.PARTIALLY_FILLED
        elif order.order_type == OrderType.LIMIT:
            order.status = OrderStatus.OPEN
        
        order.updated_at = datetime.utcnow()
        
        return trades
    
    def insert_into_order_book(self, book: List[List[float]], order_level: List[float], is_bid: bool):
        """Insert order level into order book"""
        price, qty = order_level
        
        # Find insertion point
        insertion_index = 0
        if is_bid:
            # Bids - sort descending
            for i, (book_price, _) in enumerate(book):
                if price > book_price:
                    insertion_index = i
                    break
            else:
                insertion_index = len(book)
        else:
            # Asks - sort ascending
            for i, (book_price, _) in enumerate(book):
                if price < book_price:
                    insertion_index = i
                    break
            else:
                insertion_index = len(book)
        
        book.insert(insertion_index, [price, qty])

orbit_exchange = OrbitExchange()

@app.get("/")
async def root():
    return {
        "service": "Orbit Exchange Service",
        "status": "operational",
        "trading_pairs": len(orbit_exchange.trading_pairs)
    }

@app.get("/trading-pairs")
async def get_trading_pairs():
    """Get all trading pairs"""
    return {"trading_pairs": list(orbit_exchange.trading_pairs.values())}

@app.get("/trading-pairs/{symbol}")
async def get_trading_pair(symbol: str):
    """Get specific trading pair"""
    pair = orbit_exchange.trading_pairs.get(symbol)
    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    return {"trading_pair": pair}

@app.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 100):
    """Get order book for symbol"""
    if symbol not in orbit_exchange.trading_pairs:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    order_book = orbit_exchange.order_books[symbol]
    
    bids = order_book["bids"][:limit]
    asks = order_book["asks"][:limit]
    
    return {
        "symbol": symbol,
        "bids": bids,
        "asks": asks,
        "timestamp": datetime.utcnow()
    }

@app.post("/orders")
async def create_order(
    symbol: str,
    order_type: OrderType,
    order_side: OrderSide,
    quantity: float,
    price: Optional[float] = None,
    user_id: str = "demo_user"
):
    """Create new order"""
    try:
        pair = orbit_exchange.trading_pairs.get(symbol)
        if not pair:
            raise HTTPException(status_code=404, detail="Trading pair not found")
        
        if quantity < pair.min_order_size:
            raise HTTPException(status_code=400, detail="Quantity below minimum")
        
        if quantity > pair.max_order_size:
            raise HTTPException(status_code=400, detail="Quantity above maximum")
        
        if order_type == OrderType.LIMIT and not price:
            raise HTTPException(status_code=400, detail="Price required for limit orders")
        
        order_id = f"order_{int(datetime.utcnow().timestamp())}_{len(orbit_exchange.orders)}"
        
        order = Order(
            order_id=order_id,
            user_id=user_id,
            symbol=symbol,
            order_type=order_type,
            order_side=order_side,
            quantity=quantity,
            price=price,
            filled_quantity=0.0,
            remaining_quantity=quantity,
            average_price=0.0,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Match order
        trades = orbit_exchange.match_order(order)
        
        # Store order and trades
        orbit_exchange.orders[order_id] = order
        orbit_exchange.trades.extend(trades)
        
        return {
            "order_id": order_id,
            "status": order.status.value,
            "filled_quantity": order.filled_quantity,
            "remaining_quantity": order.remaining_quantity,
            "average_price": order.average_price,
            "trades": len(trades),
            "message": "Order created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    order = orbit_exchange.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order}

@app.get("/orders/user/{user_id}")
async def get_user_orders(user_id: str, status: Optional[OrderStatus] = None, limit: int = 100):
    """Get user orders"""
    user_orders = [
        order for order in orbit_exchange.orders.values()
        if order.user_id == user_id
    ]
    
    if status:
        user_orders = [order for order in user_orders if order.status == status]
    
    # Sort by creation time and limit
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    user_orders = user_orders[:limit]
    
    return {"orders": user_orders}

@app.get("/trades/{symbol}")
async def get_trades(symbol: str, limit: int = 100):
    """Get recent trades for symbol"""
    symbol_trades = [
        trade for trade in orbit_exchange.trades
        if trade.symbol == symbol
    ]
    
    # Sort by creation time and limit
    symbol_trades.sort(key=lambda x: x.created_at, reverse=True)
    symbol_trades = symbol_trades[:limit]
    
    return {"trades": symbol_trades}

@app.get("/trades/user/{user_id}")
async def get_user_trades(user_id: str, limit: int = 100):
    """Get user trades"""
    user_trades = []
    
    for trade in orbit_exchange.trades:
        order = orbit_exchange.orders.get(trade.order_id)
        if order and order.user_id == user_id:
            user_trades.append(trade)
    
    # Sort by creation time and limit
    user_trades.sort(key=lambda x: x.created_at, reverse=True)
    user_trades = user_trades[:limit]
    
    return {"trades": user_trades}

@app.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker information"""
    if symbol not in orbit_exchange.trading_pairs:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    order_book = orbit_exchange.order_books[symbol]
    
    best_bid = order_book["bids"][0][0] if order_book["bids"] else 0
    best_ask = order_book["asks"][0][0] if order_book["asks"] else 0
    
    # Calculate 24h stats (mock)
    last_price = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else 0
    price_change = last_price * 0.02  # Mock 2% change
    price_change_percent = (price_change / last_price * 100) if last_price > 0 else 0
    
    return {
        "symbol": symbol,
        "last": last_price,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "price_change": price_change,
        "price_change_percent": price_change_percent,
        "high": last_price * 1.05,  # Mock high
        "low": last_price * 0.95,   # Mock low
        "volume": 1000000.0,        # Mock volume
        "timestamp": datetime.utcnow()
    }

@app.get("/stats/exchange")
async def get_exchange_stats():
    """Get exchange statistics"""
    total_orders = len(orbit_exchange.orders)
    total_trades = len(orbit_exchange.trades)
    
    # Count orders by status
    order_status_counts = {}
    for status in OrderStatus:
        order_status_counts[status.value] = len([
            order for order in orbit_exchange.orders.values()
            if order.status == status
        ])
    
    # Calculate total volume
    total_volume = 0
    for trade in orbit_exchange.trades:
        total_volume += trade.quantity * trade.price
    
    return {
        "total_orders": total_orders,
        "total_trades": total_trades,
        "total_volume": total_volume,
        "order_status_counts": order_status_counts,
        "active_pairs": len(orbit_exchange.trading_pairs),
        "timestamp": datetime.utcnow()
    }

@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel order"""
    order = orbit_exchange.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot cancel filled or cancelled order")
    
    # Remove from order book if still there
    symbol = order.symbol
    order_book = orbit_exchange.order_books[symbol]
    
    if order.order_side == OrderSide.BUY and order.order_type == OrderType.LIMIT:
        # Remove from bids
        for i, (price, qty) in enumerate(order_book["bids"]):
            if price == order.price and qty >= order.remaining_quantity:
                if qty > order.remaining_quantity:
                    order_book["bids"][i][1] -= order.remaining_quantity
                else:
                    del order_book["bids"][i]
                break
    elif order.order_side == OrderSide.SELL and order.order_type == OrderType.LIMIT:
        # Remove from asks
        for i, (price, qty) in enumerate(order_book["asks"]):
            if price == order.price and qty >= order.remaining_quantity:
                if qty > order.remaining_quantity:
                    order_book["asks"][i][1] -= order.remaining_quantity
                else:
                    del order_book["asks"][i]
                break
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    
    return {
        "order_id": order_id,
        "status": "cancelled",
        "message": "Order cancelled successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)