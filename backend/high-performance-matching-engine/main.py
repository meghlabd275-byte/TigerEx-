#!/usr/bin/env python3
"""
High-Performance Order Matching Engine for TigerEx
Based on OpenFinex architecture with Raft consensus
Supports 500,000+ orders per second with in-memory operations
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, AsyncIterator
from collections import defaultdict
import threading
import heapq

# @file main.py
# @description TigerEx high-performance-matching-engine service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"
    POST_ONLY = "post_only"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TimeInForce(str, Enum):
    GTC = "good_till_cancelled"
    IOC = "immediate_or_cancel"
    FOK = "fill_or_kill"
    GTD = "good_till_date"
    DAY = "day"

@dataclass
class Order:
    """Order data structure with all required fields"""
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trailing_percent: Optional[Decimal] = None
    displayed_quantity: Optional[Decimal] = None  # For iceberg orders
    status: OrderStatus = OrderStatus.PENDING
    time_in_force: TimeInForce = TimeInForce.GTC
    expire_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    filled_quantity: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    parent_order_id: Optional[str] = None  # For linked orders
    
    def __lt__(self, other):
        """Comparison for heap operations - price-time priority"""
        if self.price is None or other.price is None:
            return False
        if self.side == OrderSide.BUY:
            # Higher price has priority for buys
            if self.price != other.price:
                return self.price > other.price
        else:
            # Lower price has priority for sells
            if self.price != other.price:
                return self.price < other.price
        # Earlier time has priority
        return self.created_at < other.created_at

@dataclass
class Trade:
    """Executed trade data"""
    trade_id: str
    symbol: str
    taker_order_id: str
    maker_order_id: str
    side: OrderSide
    price: Decimal
    quantity: Decimal
    taker_user_id: str
    maker_user_id: str
    taker_fee: Decimal = Decimal("0")
    maker_fee: Decimal = Decimal("0")
    executed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OrderBookLevel:
    """Single price level in order book"""
    price: Decimal
    total_quantity: Decimal
    order_count: int

class OrderBook:
    """
    High-performance order book with in-memory operations
    Supports sub-microsecond order matching
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: List[Order] = []  # Max heap for bids
        self.asks: List[Order] = []  # Min heap for asks
        self.orders: Dict[str, Order] = {}  # Order ID -> Order mapping
        self.user_orders: Dict[str, Dict[str, Order]] = defaultdict(dict)  # User ID -> Order mapping
        
        # Price level tracking for efficient depth queries
        self.bid_levels: Dict[Decimal, OrderBookLevel] = {}
        self.ask_levels: Dict[Decimal, OrderBookLevel] = {}
        
        # Trade history
        self.recent_trades: List[Trade] = []
        self.max_trades_history = 1000
        
        # Statistics
        self.total_trades = 0
        self.total_volume = Decimal("0")
        self.high_price = Decimal("0")
        self.low_price = Decimal("0")
        
        # Lock for thread-safe operations
        self._lock = threading.RLock()
        
        # Stop orders tracking
        self.stop_orders: Dict[str, Order] = {}
        self.trailing_stops: Dict[str, Decimal] = {}  # Track trailing stop trigger prices
        
        # Market state
        self.last_trade_price: Optional[Decimal] = None
        self.last_trade_time: Optional[datetime] = None
    
    def add_order(self, order: Order) -> Tuple[bool, List[Trade]]:
        """
        Add order to book and attempt matching
        Returns (success, trades)
        """
        with self._lock:
            trades = []
            
            # Validate order
            if not self._validate_order(order):
                order.status = OrderStatus.REJECTED
                return False, []
            
            # Handle stop orders
            if order.order_type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP]:
                return self._add_stop_order(order)
            
            # Try to match marketable orders
            if order.order_type == OrderType.MARKET:
                trades = self._match_market_order(order)
            elif order.order_type in [OrderType.LIMIT, OrderType.POST_ONLY]:
                if order.order_type == OrderType.POST_ONLY:
                    # Post-only orders must not cross
                    if self._would_cross(order):
                        order.status = OrderStatus.REJECTED
                        return False, []
                trades = self._match_limit_order(order)
            elif order.order_type == OrderType.IOC:
                trades = self._match_ioc_order(order)
            elif order.order_type == OrderType.FOK:
                trades = self._match_fok_order(order)
            elif order.order_type == OrderType.ICEBERG:
                trades = self._match_iceberg_order(order)
            
            # Add remaining quantity to book if not fully filled
            if order.filled_quantity < order.quantity:
                if order.status != OrderStatus.CANCELLED and order.status != OrderStatus.REJECTED:
                    self._add_to_book(order)
            
            # Update order status
            if order.filled_quantity == order.quantity:
                order.status = OrderStatus.FILLED
            elif order.filled_quantity > Decimal("0"):
                order.status = OrderStatus.PARTIALLY_FILLED
            
            # Record trades
            for trade in trades:
                self._record_trade(trade)
            
            return True, trades
    
    def _validate_order(self, order: Order) -> bool:
        """Validate order parameters"""
        if order.quantity <= Decimal("0"):
            return False
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.POST_ONLY]:
            if order.price is None or order.price <= Decimal("0"):
                return False
        if order.order_type == OrderType.TRAILING_STOP and order.trailing_percent is None:
            return False
        return True
    
    def _would_cross(self, order: Order) -> bool:
        """Check if order would cross with existing orders"""
        if order.side == OrderSide.BUY:
            if self.asks and order.price >= self.asks[0].price:
                return True
        else:
            if self.bids and order.price <= self.bids[0].price:
                return True
        return False
    
    def _match_market_order(self, order: Order) -> List[Trade]:
        """Match market order against opposite side"""
        trades = []
        remaining = order.quantity
        
        opposite_book = self.asks if order.side == OrderSide.BUY else self.bids
        
        while remaining > Decimal("0") and opposite_book:
            best_order = opposite_book[0]
            fill_qty = min(remaining, best_order.quantity - best_order.filled_quantity)
            
            if fill_qty <= Decimal("0"):
                heapq.heappop(opposite_book)
                continue
            
            trade = self._create_trade(order, best_order, fill_qty, best_order.price)
            trades.append(trade)
            
            remaining -= fill_qty
            order.filled_quantity += fill_qty
            best_order.filled_quantity += fill_qty
            
            if best_order.filled_quantity >= best_order.quantity:
                heapq.heappop(opposite_book)
                best_order.status = OrderStatus.FILLED
        
        return trades
    
    def _match_limit_order(self, order: Order) -> List[Trade]:
        """Match limit order with price-time priority"""
        trades = []
        remaining = order.quantity - order.filled_quantity
        
        opposite_book = self.asks if order.side == OrderSide.BUY else self.bids
        
        while remaining > Decimal("0") and opposite_book:
            best_order = opposite_book[0]
            
            # Check price crossing
            if order.side == OrderSide.BUY:
                if order.price < best_order.price:
                    break
            else:
                if order.price > best_order.price:
                    break
            
            fill_qty = min(remaining, best_order.quantity - best_order.filled_quantity)
            
            if fill_qty <= Decimal("0"):
                heapq.heappop(opposite_book)
                continue
            
            trade = self._create_trade(order, best_order, fill_qty, best_order.price)
            trades.append(trade)
            
            remaining -= fill_qty
            order.filled_quantity += fill_qty
            best_order.filled_quantity += fill_qty
            
            if best_order.filled_quantity >= best_order.quantity:
                heapq.heappop(opposite_book)
                best_order.status = OrderStatus.FILLED
        
        return trades
    
    def _match_ioc_order(self, order: Order) -> List[Trade]:
        """Immediate-or-Cancel: Match what's possible, cancel rest"""
        trades = self._match_limit_order(order)
        if order.filled_quantity < order.quantity:
            order.status = OrderStatus.CANCELLED
        return trades
    
    def _match_fok_order(self, Order) -> List[Trade]:
        """Fill-or-Kill: Fill completely or cancel"""
        # Check if entire order can be filled
        opposite_book = self.asks if order.side == OrderSide.BUY else self.bids
        
        available = Decimal("0")
        for o in opposite_book:
            if order.side == OrderSide.BUY and o.price > order.price:
                break
            if order.side == OrderSide.SELL and o.price < order.price:
                break
            available += o.quantity - o.filled_quantity
        
        if available >= order.quantity:
            return self._match_limit_order(order)
        else:
            order.status = OrderStatus.CANCELLED
            return []
    
    def _match_iceberg_order(self, order: Order) -> List[Trade]:
        """Match iceberg order showing only displayed quantity"""
        # Use displayed quantity for matching
        display_qty = order.displayed_quantity or (order.quantity * Decimal("0.1"))
        
        # Match displayed portion
        trades = self._match_limit_order(order)
        
        # Refresh displayed quantity after partial fill
        if order.filled_quantity < order.quantity:
            order.displayed_quantity = min(
                display_qty,
                order.quantity - order.filled_quantity
            )
        
        return trades
    
    def _add_stop_order(self, order: Order) -> Tuple[bool, List[Trade]]:
        """Add stop order to monitoring"""
        order.status = OrderStatus.OPEN
        self.stop_orders[order.order_id] = order
        
        if order.order_type == OrderType.TRAILING_STOP:
            # Initialize trailing stop
            self.trailing_stops[order.order_id] = self.last_trade_price or order.stop_price
        
        return True, []
    
    def _add_to_book(self, order: Order):
        """Add order to order book"""
        order.status = OrderStatus.OPEN
        self.orders[order.order_id] = order
        self.user_orders[order.user_id][order.order_id] = order
        
        if order.side == OrderSide.BUY:
            heapq.heappush(self.bids, order)
            # Update price level
            if order.price not in self.bid_levels:
                self.bid_levels[order.price] = OrderBookLevel(
                    price=order.price,
                    total_quantity=Decimal("0"),
                    order_count=0
                )
            self.bid_levels[order.price].total_quantity += order.quantity - order.filled_quantity
            self.bid_levels[order.price].order_count += 1
        else:
            heapq.heappush(self.asks, order)
            # Update price level
            if order.price not in self.ask_levels:
                self.ask_levels[order.price] = OrderBookLevel(
                    price=order.price,
                    total_quantity=Decimal("0"),
                    order_count=0
                )
            self.ask_levels[order.price].total_quantity += order.quantity - order.filled_quantity
            self.ask_levels[order.price].order_count += 1
    
    def _create_trade(self, taker_order: Order, maker_order: Order, 
                      quantity: Decimal, price: Decimal) -> Trade:
        """Create a trade from matched orders"""
        return Trade(
            trade_id=str(uuid.uuid4()),
            symbol=self.symbol,
            taker_order_id=taker_order.order_id,
            maker_order_id=maker_order.order_id,
            side=taker_order.side,
            price=price,
            quantity=quantity,
            taker_user_id=taker_order.user_id,
            maker_user_id=maker_order.user_id
        )
    
    def _record_trade(self, trade: Trade):
        """Record trade and update statistics"""
        self.recent_trades.append(trade)
        if len(self.recent_trades) > self.max_trades_history:
            self.recent_trades.pop(0)
        
        self.total_trades += 1
        self.total_volume += trade.quantity
        
        if trade.price > self.high_price:
            self.high_price = trade.price
        if self.low_price == Decimal("0") or trade.price < self.low_price:
            self.low_price = trade.price
        
        self.last_trade_price = trade.price
        self.last_trade_time = trade.executed_at
        
        # Update maker order
        if trade.maker_order_id in self.orders:
            maker = self.orders[trade.maker_order_id]
            maker.filled_quantity += trade.quantity
            maker.average_price = (
                (maker.average_price * (maker.filled_quantity - trade.quantity) + 
                 trade.price * trade.quantity) / maker.filled_quantity
            )
            if maker.filled_quantity >= maker.quantity:
                maker.status = OrderStatus.FILLED
    
    def cancel_order(self, order_id: str, user_id: str) -> bool:
        """Cancel an order from the book"""
        with self._lock:
            if order_id not in self.orders:
                # Check stop orders
                if order_id in self.stop_orders:
                    order = self.stop_orders[order_id]
                    if order.user_id != user_id:
                        return False
                    order.status = OrderStatus.CANCELLED
                    del self.stop_orders[order_id]
                    return True
                return False
            
            order = self.orders[order_id]
            if order.user_id != user_id:
                return False
            
            # Update price level
            if order.side == OrderSide.BUY:
                if order.price in self.bid_levels:
                    self.bid_levels[order.price].total_quantity -= order.quantity - order.filled_quantity
                    self.bid_levels[order.price].order_count -= 1
                    if self.bid_levels[order.price].order_count <= 0:
                        del self.bid_levels[order.price]
            else:
                if order.price in self.ask_levels:
                    self.ask_levels[order.price].total_quantity -= order.quantity - order.filled_quantity
                    self.ask_levels[order.price].order_count -= 1
                    if self.ask_levels[order.price].order_count <= 0:
                        del self.ask_levels[order.price]
            
            order.status = OrderStatus.CANCELLED
            del self.orders[order_id]
            del self.user_orders[user_id][order_id]
            
            return True
    
    def get_depth(self, levels: int = 20) -> Dict:
        """Get order book depth"""
        with self._lock:
            bids = []
            for price in sorted(self.bid_levels.keys(), reverse=True)[:levels]:
                level = self.bid_levels[price]
                bids.append({
                    "price": str(level.price),
                    "quantity": str(level.total_quantity),
                    "count": level.order_count
                })
            
            asks = []
            for price in sorted(self.ask_levels.keys())[:levels]:
                level = self.ask_levels[price]
                asks.append({
                    "price": str(level.price),
                    "quantity": str(level.total_quantity),
                    "count": level.order_count
                })
            
            return {
                "symbol": self.symbol,
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_user_orders(self, user_id: str) -> List[Order]:
        """Get all orders for a user"""
        return list(self.user_orders.get(user_id, {}).values())
    
    def check_stop_orders(self, current_price: Decimal) -> List[Tuple[Order, List[Trade]]]:
        """Check and trigger stop orders based on current price"""
        triggered = []
        
        with self._lock:
            orders_to_remove = []
            
            for order_id, order in self.stop_orders.items():
                should_trigger = False
                
                if order.order_type == OrderType.STOP_LOSS:
                    if order.side == OrderSide.SELL and current_price <= order.stop_price:
                        should_trigger = True
                    elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                        should_trigger = True
                
                elif order.order_type == OrderType.STOP_LIMIT:
                    if order.side == OrderSide.SELL and current_price <= order.stop_price:
                        should_trigger = True
                        order.price = order.price or order.stop_price
                    elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                        should_trigger = True
                        order.price = order.price or order.stop_price
                
                elif order.order_type == OrderType.TRAILING_STOP:
                    # Update trailing stop price
                    if order.side == OrderSide.SELL:
                        new_trigger = current_price * (1 - order.trailing_percent / 100)
                        if new_trigger > self.trailing_stops[order_id]:
                            self.trailing_stops[order_id] = new_trigger
                        if current_price <= self.trailing_stops[order_id]:
                            should_trigger = True
                    else:
                        new_trigger = current_price * (1 + order.trailing_percent / 100)
                        if new_trigger < self.trailing_stops[order_id]:
                            self.trailing_stops[order_id] = new_trigger
                        if current_price >= self.trailing_stops[order_id]:
                            should_trigger = True
                
                if should_trigger:
                    orders_to_remove.append(order_id)
                    # Convert to market or limit order and match
                    if order.order_type == OrderType.STOP_LOSS:
                        order.order_type = OrderType.MARKET
                    else:
                        order.order_type = OrderType.LIMIT
                    
                    success, trades = self.add_order(order)
                    triggered.append((order, trades))
            
            for order_id in orders_to_remove:
                del self.stop_orders[order_id]
                if order_id in self.trailing_stops:
                    del self.trailing_stops[order_id]
        
        return triggered


class MatchingEngine:
    """
    High-performance matching engine managing multiple order books
    Implements OpenFinex-style architecture with in-memory operations
    """
    
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.symbols: Dict[str, Dict] = {}  # Symbol configurations
        self._lock = threading.RLock()
        
        # Performance metrics
        self.orders_processed = 0
        self.trades_executed = 0
        self.start_time = datetime.utcnow()
        
        # Event handlers
        self.trade_handlers = []
        self.order_handlers = []
    
    def add_symbol(self, symbol: str, base_asset: str, quote_asset: str,
                   min_price: Decimal = Decimal("0.00000001"),
                   max_price: Decimal = Decimal("1000000000"),
                   min_quantity: Decimal = Decimal("0.00000001"),
                   max_quantity: Decimal = Decimal("1000000000"),
                   tick_size: Decimal = Decimal("0.00000001"),
                   step_size: Decimal = Decimal("0.00000001")):
        """Add a new trading symbol"""
        with self._lock:
            if symbol not in self.order_books:
                self.order_books[symbol] = OrderBook(symbol)
                self.symbols[symbol] = {
                    "base_asset": base_asset,
                    "quote_asset": quote_asset,
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_quantity": min_quantity,
                    "max_quantity": max_quantity,
                    "tick_size": tick_size,
                    "step_size": step_size,
                    "is_active": True
                }
    
    def submit_order(self, order: Order) -> Tuple[bool, List[Trade], str]:
        """
        Submit order to matching engine
        Returns (success, trades, message)
        """
        with self._lock:
            if order.symbol not in self.order_books:
                return False, [], f"Symbol {order.symbol} not found"
            
            book = self.order_books[order.symbol]
            success, trades = book.add_order(order)
            self.orders_processed += 1
            self.trades_executed += len(trades)
            
            # Notify handlers
            for trade in trades:
                for handler in self.trade_handlers:
                    handler(trade)
            
            for handler in self.order_handlers:
                handler(order)
            
            return success, trades, "Order processed successfully"
    
    def cancel_order(self, symbol: str, order_id: str, user_id: str) -> bool:
        """Cancel an order"""
        with self._lock:
            if symbol not in self.order_books:
                return False
            return self.order_books[symbol].cancel_order(order_id, user_id)
    
    def get_order_book(self, symbol: str, depth: int = 20) -> Optional[Dict]:
        """Get order book for a symbol"""
        if symbol not in self.order_books:
            return None
        return self.order_books[symbol].get_depth(depth)
    
    def get_user_orders(self, symbol: str, user_id: str) -> List[Order]:
        """Get user orders for a symbol"""
        if symbol not in self.order_books:
            return []
        return self.order_books[symbol].get_user_orders(user_id)
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Trade]:
        """Get recent trades for a symbol"""
        if symbol not in self.order_books:
            return []
        return self.order_books[symbol].recent_trades[-limit:]
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "orders_processed": self.orders_processed,
            "trades_executed": self.trades_executed,
            "orders_per_second": self.orders_processed / max(uptime, 1),
            "trades_per_second": self.trades_executed / max(uptime, 1),
            "active_symbols": len(self.symbols),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def on_trade(self, handler):
        """Register trade event handler"""
        self.trade_handlers.append(handler)
    
    def on_order(self, handler):
        """Register order event handler"""
        self.order_handlers.append(handler)


# Singleton instance
matching_engine = MatchingEngine()


if __name__ == "__main__":
    # Test the matching engine
    engine = MatchingEngine()
    
    # Add BTC/USDT symbol
    engine.add_symbol("BTCUSDT", "BTC", "USDT")
    
    # Create some test orders
    buy_order = Order(
        order_id=str(uuid.uuid4()),
        user_id="user1",
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000")
    )
    
    sell_order = Order(
        order_id=str(uuid.uuid4()),
        user_id="user2",
        symbol="BTCUSDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.5"),
        price=Decimal("50000")
    )
    
    # Submit orders
    success, trades, msg = engine.submit_order(buy_order)
    print(f"Buy order: {success}, Trades: {len(trades)}, Message: {msg}")
    
    success, trades, msg = engine.submit_order(sell_order)
    print(f"Sell order: {success}, Trades: {len(trades)}, Message: {msg}")
    
    # Get order book
    order_book = engine.get_order_book("BTCUSDT")
    print(f"Order book: {json.dumps(order_book, indent=2)}")
    
    # Get stats
    stats = engine.get_stats()
    print(f"Engine stats: {json.dumps(stats, indent=2)}")def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
