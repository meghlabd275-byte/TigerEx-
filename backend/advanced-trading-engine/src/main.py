#!/usr/bin/env python3
"""
Advanced Trading Engine for TigerEx Platform
Complete trading system with order matching, risk management, and liquidity provision
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
import decimal
from decimal import Decimal
from enum import Enum
import threading
import time
from typing import Dict, List, Optional, Tuple
import redis
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

# Redis for order book and caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"

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

class TradingPair(db.Model):
    __tablename__ = 'trading_pairs'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    base_asset = db.Column(db.String(10), nullable=False)
    quote_asset = db.Column(db.String(10), nullable=False)
    min_price = db.Column(db.Numeric(20, 8), nullable=False)
    max_price = db.Column(db.Numeric(20, 8), nullable=False)
    min_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    max_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    step_size = db.Column(db.Numeric(20, 8), nullable=False)
    tick_size = db.Column(db.Numeric(20, 8), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    order_type = db.Column(db.Enum(OrderType), nullable=False)
    side = db.Column(db.Enum(OrderSide), nullable=False)
    
    # Order details
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    stop_price = db.Column(db.Numeric(20, 8))
    
    # Execution details
    executed_quantity = db.Column(db.Numeric(20, 8), default=0)
    executed_price = db.Column(db.Numeric(20, 8), default=0)
    filled_quantity = db.Column(db.Numeric(20, 8), default=0)
    
    # Status and metadata
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    time_in_force = db.Column(db.String(10), default='GTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Commission
    commission = db.Column(db.Numeric(20, 8), default=0)
    commission_asset = db.Column(db.String(10))

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(64), nullable=False, unique=True)
    order_id = db.Column(db.String(64), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    buyer_order_id = db.Column(db.String(64))
    seller_order_id = db.Column(db.String(64))
    
    # Trade details
    price = db.Column(db.Numeric(20, 8), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    quote_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Commission
    commission = db.Column(db.Numeric(20, 8), default=0)
    commission_asset = db.Column(db.String(10))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids = []  # List of (price, quantity) tuples, sorted descending
        self.asks = []  # List of (price, quantity) tuples, sorted ascending
        self.lock = threading.Lock()
    
    def add_bid(self, price: Decimal, quantity: Decimal) -> None:
        with self.lock:
            # Insert at correct position (sorted by price descending)
            for i, (bid_price, bid_quantity) in enumerate(self.bids):
                if price > bid_price:
                    self.bids.insert(i, (price, quantity))
                    return
                elif price == bid_price:
                    self.bids[i] = (price, bid_quantity + quantity)
                    return
            self.bids.append((price, quantity))
    
    def add_ask(self, price: Decimal, quantity: Decimal) -> None:
        with self.lock:
            # Insert at correct position (sorted by price ascending)
            for i, (ask_price, ask_quantity) in enumerate(self.asks):
                if price < ask_price:
                    self.asks.insert(i, (price, quantity))
                    return
                elif price == ask_price:
                    self.asks[i] = (price, ask_quantity + quantity)
                    return
            self.asks.append((price, quantity))
    
    def remove_bid(self, price: Decimal, quantity: Decimal) -> bool:
        with self.lock:
            for i, (bid_price, bid_quantity) in enumerate(self.bids):
                if bid_price == price:
                    if bid_quantity <= quantity:
                        self.bids.pop(i)
                    else:
                        self.bids[i] = (price, bid_quantity - quantity)
                    return True
            return False
    
    def remove_ask(self, price: Decimal, quantity: Decimal) -> bool:
        with self.lock:
            for i, (ask_price, ask_quantity) in enumerate(self.asks):
                if ask_price == price:
                    if ask_quantity <= quantity:
                        self.asks.pop(i)
                    else:
                        self.asks[i] = (price, ask_quantity - quantity)
                    return True
            return False
    
    def get_best_bid(self) -> Optional[Tuple[Decimal, Decimal]]:
        with self.lock:
            return self.bids[0] if self.bids else None
    
    def get_best_ask(self) -> Optional[Tuple[Decimal, Decimal]]:
        with self.lock:
            return self.asks[0] if self.asks else None
    
    def get_spread(self) -> Optional[Decimal]:
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask[0] - best_bid[0]
        return None

# Global order books
order_books: Dict[str, OrderBook] = {}

def get_order_book(symbol: str) -> OrderBook:
    if symbol not in order_books:
        order_books[symbol] = OrderBook(symbol)
    return order_books[symbol]

def validate_order(order_data: dict) -> Tuple[bool, str]:
    """Validate order parameters"""
    try:
        symbol = order_data.get('symbol')
        order_type = OrderType(order_data.get('order_type'))
        side = OrderSide(order_data.get('side'))
        quantity = Decimal(str(order_data.get('quantity')))
        
        if quantity <= 0:
            return False, "Quantity must be positive"
        
        # Get trading pair info
        pair = TradingPair.query.filter_by(symbol=symbol, is_active=True).first()
        if not pair:
            return False, "Trading pair not found or inactive"
        
        if quantity < pair.min_quantity:
            return False, f"Quantity below minimum {pair.min_quantity}"
        if quantity > pair.max_quantity:
            return False, f"Quantity above maximum {pair.max_quantity}"
        
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            price = Decimal(str(order_data.get('price')))
            if price <= 0:
                return False, "Price must be positive"
            if price < pair.min_price:
                return False, f"Price below minimum {pair.min_price}"
            if price > pair.max_price:
                return False, f"Price above maximum {pair.max_price}"
        
        return True, "Valid"
    except Exception as e:
        return False, str(e)

def match_orders(order: Order, order_book: OrderBook) -> List[Trade]:
    """Match order against order book and return list of trades"""
    trades = []
    
    if order.side == OrderSide.BUY:
        # Match against asks
        while (order.quantity - order.executed_quantity > 0 and 
               order_book.asks and 
               (order.order_type == OrderType.MARKET or 
                order.price >= order_book.asks[0][0])):
            
            ask_price, ask_quantity = order_book.asks[0]
            fill_quantity = min(order.quantity - order.executed_quantity, ask_quantity)
            
            # Create trade
            trade = Trade(
                trade_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                price=ask_price,
                quantity=fill_quantity,
                quote_quantity=ask_price * fill_quantity
            )
            trades.append(trade)
            
            # Update order
            order.executed_quantity += fill_quantity
            order.executed_price = ((order.executed_price * (order.executed_quantity - fill_quantity)) + 
                                   (ask_price * fill_quantity)) / order.executed_quantity
            
            # Remove from order book
            order_book.remove_ask(ask_price, fill_quantity)
            
            if order.order_type == OrderType.MARKET:
                break
    
    else:  # SELL
        # Match against bids
        while (order.quantity - order.executed_quantity > 0 and 
               order_book.bids and 
               (order.order_type == OrderType.MARKET or 
                order.price <= order_book.bids[0][0])):
            
            bid_price, bid_quantity = order_book.bids[0]
            fill_quantity = min(order.quantity - order.executed_quantity, bid_quantity)
            
            # Create trade
            trade = Trade(
                trade_id=str(uuid.uuid4()),
                order_id=order.order_id,
                symbol=order.symbol,
                price=bid_price,
                quantity=fill_quantity,
                quote_quantity=bid_price * fill_quantity
            )
            trades.append(trade)
            
            # Update order
            order.executed_quantity += fill_quantity
            order.executed_price = ((order.executed_price * (order.executed_quantity - fill_quantity)) + 
                                   (bid_price * fill_quantity)) / order.executed_quantity
            
            # Remove from order book
            order_book.remove_bid(bid_price, fill_quantity)
            
            if order.order_type == OrderType.MARKET:
                break
    
    # Update order status
    if order.executed_quantity == order.quantity:
        order.status = OrderStatus.FILLED
    elif order.executed_quantity > 0:
        order.status = OrderStatus.PARTIALLY_FILLED
    
    return trades

# API Routes
@app.route('/api/trading/pairs', methods=['GET'])
def get_trading_pairs():
    try:
        pairs = TradingPair.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'pairs': [
                {
                    'symbol': pair.symbol,
                    'base_asset': pair.base_asset,
                    'quote_asset': pair.quote_asset,
                    'min_price': str(pair.min_price),
                    'max_price': str(pair.max_price),
                    'min_quantity': str(pair.min_quantity),
                    'max_quantity': str(pair.max_quantity),
                    'step_size': str(pair.step_size),
                    'tick_size': str(pair.tick_size)
                }
                for pair in pairs
            ]
        })
    except Exception as e:
        logger.error(f"Error getting trading pairs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading/orderbook/<symbol>', methods=['GET'])
def get_order_book_endpoint(symbol):
    try:
        order_book = get_order_book(symbol)
        
        # Get depth (default 20 levels)
        limit = request.args.get('limit', 20, type=int)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'bids': [[str(price), str(quantity)] for price, quantity in order_book.bids[:limit]],
            'asks': [[str(price), str(quantity)] for price, quantity in order_book.asks[:limit]],
            'spread': str(order_book.get_spread()) if order_book.get_spread() else None
        })
    except Exception as e:
        logger.error(f"Error getting order book: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading/order', methods=['POST'])
@jwt_required()
def create_order():
    try:
        user_id = get_jwt_identity()
        order_data = request.get_json()
        
        # Validate order
        is_valid, error_msg = validate_order(order_data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Create order
        order = Order(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            symbol=order_data['symbol'],
            order_type=OrderType(order_data['order_type']),
            side=OrderSide(order_data['side']),
            quantity=Decimal(str(order_data['quantity'])),
            price=Decimal(str(order_data['price'])) if 'price' in order_data else None,
            stop_price=Decimal(str(order_data['stop_price'])) if 'stop_price' in order_data else None,
            time_in_force=order_data.get('time_in_force', 'GTC')
        )
        
        # Get order book
        order_book = get_order_book(order_data['symbol'])
        
        # Process order
        if order.order_type == OrderType.MARKET:
            # Market orders are executed immediately
            trades = match_orders(order, order_book)
            for trade in trades:
                db.session.add(trade)
        else:
            # Limit orders are added to the book
            if order.side == OrderSide.BUY:
                order_book.add_bid(order.price, order.quantity)
            else:
                order_book.add_ask(order.price, order.quantity)
            order.status = OrderStatus.OPEN
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'order_type': order.order_type,
                'side': order.side,
                'quantity': str(order.quantity),
                'price': str(order.price) if order.price else None,
                'status': order.status,
                'executed_quantity': str(order.executed_quantity),
                'executed_price': str(order.executed_price) if order.executed_price else None
            }
        })
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    try:
        user_id = get_jwt_identity()
        symbol = request.args.get('symbol')
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Order.query.filter_by(user_id=user_id)
        
        if symbol:
            query = query.filter_by(symbol=symbol)
        if status:
            query = query.filter_by(status=OrderStatus(status))
        
        orders = query.order_by(Order.created_at.desc()).paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'orders': [
                {
                    'order_id': order.order_id,
                    'symbol': order.symbol,
                    'order_type': order.order_type,
                    'side': order.side,
                    'quantity': str(order.quantity),
                    'price': str(order.price) if order.price else None,
                    'executed_quantity': str(order.executed_quantity),
                    'executed_price': str(order.executed_price) if order.executed_price else None,
                    'status': order.status,
                    'created_at': order.created_at.isoformat()
                }
                for order in orders.items
            ],
            'pagination': {
                'page': orders.page,
                'per_page': orders.per_page,
                'total': orders.total,
                'total_pages': orders.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting user orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading/orders/<order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        if order.status not in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
            return jsonify({'success': False, 'error': 'Order cannot be cancelled'}), 400
        
        # Remove from order book if limit order
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            order_book = get_order_book(order.symbol)
            if order.side == OrderSide.BUY:
                order_book.remove_bid(order.price, order.quantity - order.executed_quantity)
            else:
                order_book.remove_ask(order.price, order.quantity - order.executed_quantity)
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order cancelled successfully'})
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trading/trades', methods=['GET'])
@jwt_required()
def get_user_trades():
    try:
        user_id = get_jwt_identity()
        symbol = request.args.get('symbol')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Trade.query.join(Order).filter(Order.user_id == user_id)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        
        trades = query.order_by(Trade.timestamp.desc()).paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'trades': [
                {
                    'trade_id': trade.trade_id,
                    'order_id': trade.order_id,
                    'symbol': trade.symbol,
                    'price': str(trade.price),
                    'quantity': str(trade.quantity),
                    'quote_quantity': str(trade.quote_quantity),
                    'commission': str(trade.commission),
                    'timestamp': trade.timestamp.isoformat()
                }
                for trade in trades.items
            ],
            'pagination': {
                'page': trades.page,
                'per_page': trades.per_page,
                'total': trades.total,
                'total_pages': trades.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting user trades: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create default trading pairs if not exists
    default_pairs = [
        {
            'symbol': 'BTCUSDT',
            'base_asset': 'BTC',
            'quote_asset': 'USDT',
            'min_price': Decimal('0.01'),
            'max_price': Decimal('1000000'),
            'min_quantity': Decimal('0.00000001'),
            'max_quantity': Decimal('9000'),
            'step_size': Decimal('0.00000001'),
            'tick_size': Decimal('0.01')
        },
        {
            'symbol': 'ETHUSDT',
            'base_asset': 'ETH',
            'quote_asset': 'USDT',
            'min_price': Decimal('0.01'),
            'max_price': Decimal('100000'),
            'min_quantity': Decimal('0.00000001'),
            'max_quantity': Decimal('1000000'),
            'step_size': Decimal('0.00000001'),
            'tick_size': Decimal('0.01')
        }
    ]
    
    for pair_data in default_pairs:
        if not TradingPair.query.filter_by(symbol=pair_data['symbol']).first():
            pair = TradingPair(**pair_data)
            db.session.add(pair)
    
    db.session.commit()
    logger.info("Trading engine initialized successfully")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Advanced Trading Engine started successfully")
    app.run(host='0.0.0.0', port=5003, debug=True)