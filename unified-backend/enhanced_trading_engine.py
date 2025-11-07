"""
TigerEx Enhanced Trading Engine
Complete trading functionality with advanced features
"""

import asyncio
import json
import decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_, func
import redis.asyncio as redis
import aiohttp
import numpy as np

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class Order:
    id: str
    user_id: int
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: decimal.Decimal
    price: Optional[decimal.Decimal] = None
    stop_price: Optional[decimal.Decimal] = None
    time_in_force: str = "GTC"
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: decimal.Decimal = decimal.Decimal('0')
    average_price: decimal.Decimal = decimal.Decimal('0')
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

class OrderBook:
    def __init__(self, symbol: str, redis_client: redis.Redis):
        self.symbol = symbol
        self.redis = redis_client
        self.bids_key = f"orderbook:{symbol}:bids"
        self.asks_key = f"orderbook:{symbol}:asks"
        
    async def add_order(self, order: Order):
        """Add order to orderbook"""
        if order.side == OrderSide.BUY:
            key = self.bids_key
            score = float(order.price) if order.price else 0
        else:
            key = self.asks_key
            score = float(order.price) if order.price else float('inf')
        
        order_data = {
            "id": order.id,
            "user_id": order.user_id,
            "quantity": float(order.quantity),
            "filled": float(order.filled_quantity),
            "type": order.type.value,
            "time_in_force": order.time_in_force,
            "created_at": order.created_at.isoformat() if order.created_at else datetime.utcnow().isoformat()
        }
        
        await self.redis.zadd(key, {json.dumps(order_data): score})
        
    async def remove_order(self, order_id: str, side: OrderSide):
        """Remove order from orderbook"""
        key = self.bids_key if side == OrderSide.BUY else self.asks_key
        
        # Get all orders and find the one to remove
        orders = await self.redis.zrange(key, 0, -1, withscores=True)
        for order_json, score in orders:
            order_data = json.loads(order_json)
            if order_data["id"] == order_id:
                await self.redis.zrem(key, order_json)
                break
                
    async def get_best_bid_ask(self) -> Tuple[Optional[float], Optional[float]]:
        """Get best bid and ask prices"""
        best_bid = await self.redis.zrevrange(self.bids_key, 0, 0, withscores=True)
        best_ask = await self.redis.zrange(self.asks_key, 0, 0, withscores=True)
        
        bid_price = float(best_bid[0][1]) if best_bid else None
        ask_price = float(best_ask[0][1]) if best_ask else None
        
        return bid_price, ask_price
    
    async def get_order_book_depth(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Get order book depth"""
        bids = await self.redis.zrevrange(self.bids_key, 0, limit - 1, withscores=True)
        asks = await self.redis.zrange(self.asks_key, 0, limit - 1, withscores=True)
        
        return {
            "bids": [{"price": float(score), **json.loads(order_json)} for order_json, score in bids],
            "asks": [{"price": float(score), **json.loads(order_json)} for order_json, score in asks]
        }

class MarketDataAggregator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.exchanges = ["binance", "okx", "huobi", "kraken", "coinbase"]
        
    async def aggregate_ticker_data(self, symbol: str) -> Dict[str, Any]:
        """Aggregate ticker data from multiple exchanges"""
        aggregated = {
            "symbol": symbol,
            "price": 0,
            "volume_24h": 0,
            "high_24h": 0,
            "low_24h": float('inf'),
            "change_24h": 0,
            "exchange_count": 0,
            "exchanges": {}
        }
        
        for exchange in self.exchanges:
            try:
                data = await self._get_exchange_ticker(exchange, symbol)
                if data:
                    aggregated["exchanges"][exchange] = data
                    aggregated["price"] += data["price"]
                    aggregated["volume_24h"] += data["volume_24h"]
                    aggregated["high_24h"] = max(aggregated["high_24h"], data["high_24h"])
                    aggregated["low_24h"] = min(aggregated["low_24h"], data["low_24h"])
                    aggregated["exchange_count"] += 1
            except Exception as e:
                logger.error(f"Failed to get data from {exchange}: {e}")
                continue
        
        # Calculate averages
        if aggregated["exchange_count"] > 0:
            aggregated["price"] /= aggregated["exchange_count"]
        else:
            aggregated["low_24h"] = 0
            
        return aggregated
    
    async def _get_exchange_ticker(self, exchange: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker data from specific exchange"""
        # This would integrate with actual exchange APIs
        # For now, return mock data
        base_price = 50000 if "BTC" in symbol else 1000
        return {
            "price": base_price * (1 + np.random.normal(0, 0.01)),
            "volume_24h": np.random.uniform(100, 1000),
            "high_24h": base_price * 1.05,
            "low_24h": base_price * 0.95
        }

class OrderMatcher:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.fee_structure = {
            "maker_fee": decimal.Decimal('0.001'),
            "taker_fee": decimal.Decimal('0.0012')
        }
        
    async def match_order(self, order: Order, orderbook: OrderBook) -> List[Dict[str, Any]]:
        """Match order against orderbook"""
        trades = []
        
        if order.side == OrderSide.BUY:
            trades = await self._match_buy_order(order, orderbook)
        else:
            trades = await self._match_sell_order(order, orderbook)
            
        return trades
    
    async def _match_buy_order(self, order: Order, orderbook: OrderBook) -> List[Dict[str, Any]]:
        """Match buy order with sell orders"""
        trades = []
        remaining_quantity = order.quantity - order.filled_quantity
        
        while remaining_quantity > 0:
            # Get best ask
            asks = await self.redis.zrange(orderbook.asks_key, 0, 0, withscores=True)
            if not asks:
                break
                
            best_ask_json, ask_price = asks[0]
            best_ask = json.loads(best_ask_json)
            
            # Check if price matches
            if order.type == OrderType.LIMIT and order.price and ask_price > float(order.price):
                break
                
            # Calculate trade quantity
            trade_quantity = min(remaining_quantity, decimal.Decimal(str(best_ask["quantity"])))
            
            # Execute trade
            trade = {
                "buy_order_id": order.id,
                "sell_order_id": best_ask["id"],
                "symbol": order.symbol,
                "quantity": float(trade_quantity),
                "price": ask_price,
                "total": float(trade_quantity * decimal.Decimal(str(ask_price))),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            trades.append(trade)
            remaining_quantity -= trade_quantity
            
            # Update orderbook
            if trade_quantity >= decimal.Decimal(str(best_ask["quantity"])):
                await self.redis.zrem(orderbook.asks_key, best_ask_json)
            else:
                # Partial fill - update the order
                best_ask["quantity"] -= float(trade_quantity)
                await self.redis.zrem(orderbook.asks_key, best_ask_json)
                await self.redis.zadd(orderbook.asks_key, {json.dumps(best_ask): ask_price})
        
        return trades
    
    async def _match_sell_order(self, order: Order, orderbook: OrderBook) -> List[Dict[str, Any]]:
        """Match sell order with buy orders"""
        trades = []
        remaining_quantity = order.quantity - order.filled_quantity
        
        while remaining_quantity > 0:
            # Get best bid
            bids = await self.redis.zrevrange(orderbook.bids_key, 0, 0, withscores=True)
            if not bids:
                break
                
            best_bid_json, bid_price = bids[0]
            best_bid = json.loads(best_bid_json)
            
            # Check if price matches
            if order.type == OrderType.LIMIT and order.price and bid_price < float(order.price):
                break
                
            # Calculate trade quantity
            trade_quantity = min(remaining_quantity, decimal.Decimal(str(best_bid["quantity"])))
            
            # Execute trade
            trade = {
                "buy_order_id": best_bid["id"],
                "sell_order_id": order.id,
                "symbol": order.symbol,
                "quantity": float(trade_quantity),
                "price": bid_price,
                "total": float(trade_quantity * decimal.Decimal(str(bid_price))),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            trades.append(trade)
            remaining_quantity -= trade_quantity
            
            # Update orderbook
            if trade_quantity >= decimal.Decimal(str(best_bid["quantity"])):
                await self.redis.zrem(orderbook.bids_key, best_bid_json)
            else:
                # Partial fill - update the order
                best_bid["quantity"] -= float(trade_quantity)
                await self.redis.zrem(orderbook.bids_key, best_bid_json)
                await self.redis.zadd(orderbook.bids_key, {json.dumps(best_bid): bid_price})
        
        return trades

class RiskManager:
    def __init__(self, redis_client: redis.Redis, db: Session):
        self.redis = redis_client
        self.db = db
        
    async def validate_order_risk(self, order: Order) -> Tuple[bool, str]:
        """Validate order against risk rules"""
        # Check account balance
        balance_ok, message = await self._check_account_balance(order)
        if not balance_ok:
            return False, message
        
        # Check position limits
        position_ok, position_message = await self._check_position_limits(order)
        if not position_ok:
            return False, position_message
        
        # Check daily trading limits
        daily_ok, daily_message = await self._check_daily_limits(order)
        if not daily_ok:
            return False, daily_message
        
        return True, "Order passes risk checks"
    
    async def _check_account_balance(self, order: Order) -> Tuple[bool, str]:
        """Check if user has sufficient balance"""
        # Get user's wallet balance
        balance_query = text("""
            SELECT balance FROM wallets 
            WHERE user_id = :user_id AND currency = :currency
        """)
        
        if order.side == OrderSide.BUY:
            # Check quote currency balance
            currency = order.symbol.split('/')[1] if '/' in order.symbol else 'USDT'
            required_balance = order.quantity * (order.price or 0)
        else:
            # Check base currency balance
            currency = order.symbol.split('/')[0] if '/' in order.symbol else order.symbol
            required_balance = order.quantity
        
        result = self.db.execute(balance_query, {
            "user_id": order.user_id,
            "currency": currency
        }).fetchone()
        
        if not result or result.balance < required_balance:
            return False, f"Insufficient {currency} balance"
        
        return True, "Sufficient balance"
    
    async def _check_position_limits(self, order: Order) -> Tuple[bool, str]:
        """Check position size limits"""
        # Get current position
        position_query = text("""
            SELECT COALESCE(SUM(CASE WHEN side = 'buy' THEN quantity ELSE -quantity END), 0) as net_position
            FROM orders 
            WHERE user_id = :user_id AND symbol = :symbol AND status IN ('open', 'partially_filled')
        """)
        
        result = self.db.execute(position_query, {
            "user_id": order.user_id,
            "symbol": order.symbol
        }).fetchone()
        
        current_position = abs(result.net_position or 0)
        new_position = current_position + order.quantity
        
        # Define position limits (could be configurable)
        max_position = decimal.Decimal('1000000')  # 1M base currency
        
        if new_position > max_position:
            return False, f"Position size exceeds maximum limit of {max_position}"
        
        return True, "Position within limits"
    
    async def _check_daily_limits(self, order: Order) -> Tuple[bool, str]:
        """Check daily trading volume limits"""
        today = datetime.utcnow().date()
        
        volume_query = text("""
            SELECT COALESCE(SUM(quantity * price), 0) as daily_volume
            FROM orders 
            WHERE user_id = :user_id AND DATE(created_at) = :today AND status = 'filled'
        """)
        
        result = self.db.execute(volume_query, {
            "user_id": order.user_id,
            "today": today
        }).fetchone()
        
        daily_volume = result.daily_volume or 0
        order_volume = order.quantity * (order.price or 0)
        new_total = daily_volume + order_volume
        
        # Define daily limits
        daily_limit = decimal.Decimal('10000000')  # 10M daily volume
        
        if new_total > daily_limit:
            return False, f"Daily trading volume exceeds limit of {daily_limit}"
        
        return True, "Daily volume within limits"

class TradingEngine:
    """Main trading engine"""
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.market_data = MarketDataAggregator(redis_client)
        self.order_matcher = OrderMatcher(redis_client)
        self.risk_manager = RiskManager(redis_client, db)
        self.orderbooks = {}
        
    async def initialize_engine(self):
        """Initialize trading engine"""
        logger.info("Initializing TigerEx Trading Engine")
        
        # Load trading pairs
        await self._load_trading_pairs()
        
        # Start order book synchronization
        asyncio.create_task(self._sync_orderbooks())
        
    async def _load_trading_pairs(self):
        """Load active trading pairs"""
        pairs_query = text("SELECT symbol FROM trading_pairs WHERE is_active = true")
        pairs = self.db.execute(pairs_query).fetchall()
        
        for pair in pairs:
            self.orderbooks[pair.symbol] = OrderBook(pair.symbol, self.redis)
            
    async def _sync_orderbooks(self):
        """Synchronize orderbooks with external exchanges"""
        while True:
            try:
                for symbol, orderbook in self.orderbooks.items():
                    # Get external liquidity and merge with internal orderbook
                    await self._merge_external_liquidity(symbol, orderbook)
                
                await asyncio.sleep(1)  # Sync every second
            except Exception as e:
                logger.error(f"Orderbook sync error: {e}")
                await asyncio.sleep(5)
    
    async def _merge_external_liquidity(self, symbol: str, orderbook: OrderBook):
        """Merge external exchange liquidity"""
        # This would integrate with multiple exchanges
        # For now, keep internal orderbook
        pass
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new order"""
        try:
            # Create order object
            order = Order(
                id=str(uuid.uuid4()),
                user_id=order_data["user_id"],
                symbol=order_data["symbol"],
                side=OrderSide(order_data["side"]),
                type=OrderType(order_data["type"]),
                quantity=decimal.Decimal(str(order_data["quantity"])),
                price=decimal.Decimal(str(order_data.get("price", 0))) if order_data.get("price") else None,
                stop_price=decimal.Decimal(str(order_data.get("stop_price", 0))) if order_data.get("stop_price") else None,
                time_in_force=order_data.get("time_in_force", "GTC"),
                created_at=datetime.utcnow(),
                metadata=order_data.get("metadata", {})
            )
            
            # Risk validation
            risk_ok, risk_message = await self.risk_manager.validate_order_risk(order)
            if not risk_ok:
                order.status = OrderStatus.REJECTED
                await self._save_order(order)
                return {"success": False, "message": risk_message, "order_id": order.id}
            
            # Add to orderbook
            if order.type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                order.status = OrderStatus.OPEN
                await self._save_order(order)
                
                if symbol in self.orderbooks:
                    await self.orderbooks[symbol].add_order(order)
                
                # Try to match
                if symbol in self.orderbooks:
                    trades = await self.order_matcher.match_order(order, self.orderbooks[symbol])
                    await self._execute_trades(trades)
                    
                    # Update order status
                    if order.filled_quantity >= order.quantity:
                        order.status = OrderStatus.FILLED
                    elif order.filled_quantity > 0:
                        order.status = OrderStatus.PARTIALLY_FILLED
                    
                    await self._save_order(order)
                    
            elif order.type == OrderType.MARKET:
                # Execute market order immediately
                trades = await self._execute_market_order(order)
                if trades:
                    order.status = OrderStatus.FILLED
                else:
                    order.status = OrderStatus.REJECTED
                
                await self._save_order(order)
            
            return {
                "success": True,
                "order_id": order.id,
                "status": order.status.value,
                "filled_quantity": float(order.filled_quantity),
                "trades": trades if 'trades' in locals() else []
            }
            
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return {"success": False, "message": str(e)}
    
    async def _execute_market_order(self, order: Order) -> List[Dict[str, Any]]:
        """Execute market order"""
        if order.symbol not in self.orderbooks:
            return []
        
        orderbook = self.orderbooks[order.symbol]
        trades = await self.order_matcher.match_order(order, orderbook)
        
        if trades:
            await self._execute_trades(trades)
            
            # Update order fill details
            total_quantity = sum(decimal.Decimal(str(t["quantity"])) for t in trades)
            total_value = sum(decimal.Decimal(str(t["total"])) for t in trades)
            order.filled_quantity = total_quantity
            order.average_price = total_value / total_quantity if total_quantity > 0 else 0
        
        return trades
    
    async def _execute_trades(self, trades: List[Dict[str, Any]]):
        """Execute trades and update balances"""
        for trade in trades:
            # Update database with trade
            trade_query = text("""
                INSERT INTO trades (buy_order_id, sell_order_id, symbol, quantity, price, total, created_at)
                VALUES (:buy_order_id, :sell_order_id, :symbol, :quantity, :price, :total, :created_at)
            """)
            
            self.db.execute(trade_query, {
                "buy_order_id": trade["buy_order_id"],
                "sell_order_id": trade["sell_order_id"],
                "symbol": trade["symbol"],
                "quantity": trade["quantity"],
                "price": trade["price"],
                "total": trade["total"],
                "created_at": trade["timestamp"]
            })
            
            # Update user balances
            await self._update_balances_after_trade(trade)
        
        self.db.commit()
    
    async def _update_balances_after_trade(self, trade: Dict[str, Any]):
        """Update user balances after trade execution"""
        # Get order details to determine user IDs
        buy_order_query = text("SELECT user_id, quantity FROM orders WHERE order_id = :order_id")
        sell_order_query = text("SELECT user_id, quantity FROM orders WHERE order_id = :order_id")
        
        buy_order = self.db.execute(buy_order_query, {"order_id": trade["buy_order_id"]}).fetchone()
        sell_order = self.db.execute(sell_order_query, {"order_id": trade["sell_order_id"]}).fetchone()
        
        if buy_order and sell_order:
            # Update buyer's balance (decrease quote, increase base)
            base_currency = trade["symbol"].split('/')[0] if '/' in trade["symbol"] else "BTC"
            quote_currency = trade["symbol"].split('/')[1] if '/' in trade["symbol"] else "USDT"
            
            # Buyer gets base currency
            self.db.execute(text("""
                UPDATE wallets SET balance = balance + :amount 
                WHERE user_id = :user_id AND currency = :currency
            """), {
                "user_id": buy_order.user_id,
                "amount": trade["quantity"],
                "currency": base_currency
            })
            
            # Seller gets quote currency
            self.db.execute(text("""
                UPDATE wallets SET balance = balance + :amount 
                WHERE user_id = :user_id AND currency = :currency
            """), {
                "user_id": sell_order.user_id,
                "amount": trade["total"],
                "currency": quote_currency
            })
    
    async def _save_order(self, order: Order):
        """Save order to database"""
        order_query = text("""
            INSERT INTO orders (order_id, user_id, symbol, side, type, quantity, price, 
                              stop_price, status, filled_quantity, average_price, 
                              time_in_force, created_at, updated_at)
            VALUES (:order_id, :user_id, :symbol, :side, :type, :quantity, :price,
                    :stop_price, :status, :filled_quantity, :average_price,
                    :time_in_force, :created_at, :updated_at)
            ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                filled_quantity = EXCLUDED.filled_quantity,
                average_price = EXCLUDED.average_price,
                updated_at = EXCLUDED.updated_at
        """)
        
        self.db.execute(order_query, {
            "order_id": order.id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "type": order.type.value,
            "quantity": float(order.quantity),
            "price": float(order.price) if order.price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "status": order.status.value,
            "filled_quantity": float(order.filled_quantity),
            "average_price": float(order.average_price),
            "time_in_force": order.time_in_force,
            "created_at": order.created_at,
            "updated_at": datetime.utcnow()
        })
        self.db.commit()
    
    async def cancel_order(self, order_id: str, user_id: int) -> Dict[str, Any]:
        """Cancel order"""
        try:
            # Get order details
            order_query = text("""
                SELECT symbol, side, status FROM orders 
                WHERE order_id = :order_id AND user_id = :user_id
            """)
            order = self.db.execute(order_query, {"order_id": order_id, "user_id": user_id}).fetchone()
            
            if not order:
                return {"success": False, "message": "Order not found"}
            
            if order.status not in ["open", "partially_filled"]:
                return {"success": False, "message": "Order cannot be cancelled"}
            
            # Update order status
            update_query = text("""
                UPDATE orders SET status = 'cancelled', updated_at = NOW()
                WHERE order_id = :order_id
            """)
            self.db.execute(update_query, {"order_id": order_id})
            self.db.commit()
            
            # Remove from orderbook
            if order.symbol in self.orderbooks:
                await self.orderbooks[order.symbol].remove_order(order_id, OrderSide(order.side))
            
            return {"success": True, "message": "Order cancelled successfully"}
            
        except Exception as e:
            logger.error(f"Order cancellation failed: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book for symbol"""
        if symbol not in self.orderbooks:
            return {"bids": [], "asks": []}
        
        orderbook = self.orderbooks[symbol]
        depth = await orderbook.get_order_book_depth(limit)
        
        # Get market data
        market_data = await self.market_data.aggregate_ticker_data(symbol)
        
        return {
            "symbol": symbol,
            "bids": depth["bids"],
            "asks": depth["asks"],
            "market_data": market_data
        }