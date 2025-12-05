#!/usr/bin/env python3
"""
Tiger Trading Service
Category: trading
Description: Comprehensive unified trading platform incorporating best features from all major exchanges
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
from decimal import Decimal
from functools import wraps
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    kyc_status = db.Column(db.String(50), default='pending')
    vip_level = db.Column(db.String(20), default='basic')  # 'basic', 'silver', 'gold', 'platinum'
    trading_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradingPair(db.Model):
    __tablename__ = 'trading_pairs'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    base_asset = db.Column(db.String(20), nullable=False)
    quote_asset = db.Column(db.String(20), nullable=False)
    min_price = db.Column(db.Numeric(20, 8))
    max_price = db.Column(db.Numeric(20, 8))
    tick_size = db.Column(db.Numeric(20, 8))
    min_qty = db.Column(db.Numeric(20, 8))
    max_qty = db.Column(db.Numeric(20, 8))
    step_size = db.Column(db.Numeric(20, 8))
    is_active = db.Column(db.Boolean, default=True)
    trading_type = db.Column(db.String(20), default='spot')  # 'spot', 'futures', 'options', 'margin'
    leverage = db.Column(db.Numeric(5, 2))  # For futures/margin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)  # 'limit', 'market', 'stop_loss', 'take_profit', 'stop_limit'
    side = db.Column(db.String(10), nullable=False)  # 'buy', 'sell'
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    stop_price = db.Column(db.Numeric(20, 8))
    time_in_force = db.Column(db.String(20), default='GTC')  # 'GTC', 'IOC', 'FOK', 'GTX'
    status = db.Column(db.String(20), default='open')  # 'open', 'filled', 'partially_filled', 'cancelled', 'rejected'
    executed_quantity = db.Column(db.Numeric(20, 8), default=0)
    executed_value = db.Column(db.Numeric(20, 8), default=0)
    average_price = db.Column(db.Numeric(20, 8))
    fee = db.Column(db.Numeric(20, 8), default=0)
    fee_currency = db.Column(db.String(20))
    trading_type = db.Column(db.String(20), default='spot')
    leverage = db.Column(db.Numeric(5, 2))
    margin_used = db.Column(db.Numeric(20, 8), default=0)
    post_only = db.Column(db.Boolean, default=False)
    reduce_only = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(100), unique=True, nullable=False)
    order_id = db.Column(db.String(100), db.ForeignKey('orders.order_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    quote_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    fee = db.Column(db.Numeric(20, 8), default=0)
    fee_currency = db.Column(db.String(20))
    trading_type = db.Column(db.String(20), default='spot')
    is_maker = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Numeric(20, 8), default=0)
    locked_balance = db.Column(db.Numeric(20, 8), default=0)
    available_balance = db.Column(db.Numeric(20, 8), default=0)
    wallet_type = db.Column(db.String(20), default='spot')  # 'spot', 'margin', 'futures', 'earn'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradingBot(db.Model):
    __tablename__ = 'trading_bots'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bot_id = db.Column(db.String(100), unique=True, nullable=False)
    bot_name = db.Column(db.String(100), nullable=False)
    bot_type = db.Column(db.String(50), nullable=False)  # 'grid', 'dca', 'martingale', 'scalping', 'arbitrage'
    symbol = db.Column(db.String(20), nullable=False)
    strategy_config = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='stopped')  # 'running', 'stopped', 'paused', 'error'
    total_profit = db.Column(db.Numeric(20, 8), default=0)
    total_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Numeric(5, 2), default=0)
    max_drawdown = db.Column(db.Numeric(10, 4), default=0)
    initial_investment = db.Column(db.Numeric(20, 8))
    current_value = db.Column(db.Numeric(20, 8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    stopped_at = db.Column(db.DateTime)
    last_trade_at = db.Column(db.DateTime)

class CopyTrading(db.Model):
    __tablename__ = 'copy_trading'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    copy_ratio = db.Column(db.Numeric(5, 2), nullable=False)  # Percentage of trader's position to copy
    max_amount = db.Column(db.Numeric(20, 8))
    min_amount = db.Column(db.Numeric(20, 8))
    copy_long = db.Column(db.Boolean, default=True)
    copy_short = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # 'active', 'paused', 'stopped'
    total_copied_trades = db.Column(db.Integer, default=0)
    total_profit = db.Column(db.Numeric(20, 8), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketData(db.Model):
    __tablename__ = 'market_data'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    open_price = db.Column(db.Numeric(20, 8))
    high_price = db.Column(db.Numeric(20, 8))
    low_price = db.Column(db.Numeric(20, 8))
    close_price = db.Column(db.Numeric(20, 8))
    volume = db.Column(db.Numeric(20, 8))
    quote_volume = db.Column(db.Numeric(20, 8))
    price_change = db.Column(db.Numeric(20, 8))
    price_change_percent = db.Column(db.Numeric(10, 4))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    interval = db.Column(db.String(10), default='1m')  # '1m', '5m', '15m', '1h', '4h', '1d'

def require_kyc(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.kyc_status != 'verified':
            return jsonify({'error': 'KYC verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_trading_enabled(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.trading_enabled:
            return jsonify({'error': 'Trading not enabled'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Trading Service',
        'version': '1.0.0'
    })

@app.route('/api/trading-pairs', methods=['GET'])
def get_trading_pairs():
    trading_type = request.args.get('type', 'spot')
    search = request.args.get('search')
    
    query = TradingPair.query.filter_by(is_active=True, trading_type=trading_type)
    
    if search:
        query = query.filter(TradingPair.symbol.ilike(f'%{search}%'))
    
    pairs = query.order_by(TradingPair.symbol).all()
    
    return jsonify({
        'trading_pairs': [{
            'id': pair.id,
            'symbol': pair.symbol,
            'base_asset': pair.base_asset,
            'quote_asset': pair.quote_asset,
            'min_price': float(pair.min_price) if pair.min_price else None,
            'max_price': float(pair.max_price) if pair.max_price else None,
            'tick_size': float(pair.tick_size) if pair.tick_size else None,
            'min_qty': float(pair.min_qty) if pair.min_qty else None,
            'max_qty': float(pair.max_qty) if pair.max_qty else None,
            'step_size': float(pair.step_size) if pair.step_size else None,
            'trading_type': pair.trading_type,
            'leverage': float(pair.leverage) if pair.leverage else None
        } for pair in pairs]
    })

@app.route('/api/ticker/<symbol>', methods=['GET'])
def get_ticker(symbol):
    # Get latest market data
    latest_data = MarketData.query.filter_by(symbol=symbol)\
        .order_by(MarketData.timestamp.desc())\
        .first()
    
    if not latest_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    # Get 24h statistics
    day_ago = datetime.utcnow() - timedelta(hours=24)
    day_data = MarketData.query.filter(
        MarketData.symbol == symbol,
        MarketData.timestamp >= day_ago
    ).all()
    
    volume_24h = sum(d.volume for d in day_data if d.volume)
    high_24h = max((d.high_price for d in day_data if d.high_price), default=latest_data.high_price)
    low_24h = min((d.low_price for d in day_data if d.low_price), default=latest_data.low_price)
    
    return jsonify({
        'symbol': symbol,
        'price': float(latest_data.close_price),
        'price_change': float(latest_data.price_change) if latest_data.price_change else 0,
        'price_change_percent': float(latest_data.price_change_percent) if latest_data.price_change_percent else 0,
        'high_24h': float(high_24h),
        'low_24h': float(low_24h),
        'volume_24h': float(volume_24h),
        'timestamp': latest_data.timestamp.isoformat()
    })

@app.route('/api/orderbook/<symbol>', methods=['GET'])
def get_orderbook(symbol):
    limit = request.args.get('limit', 100, type=int)
    
    # This is a simplified orderbook implementation
    # In production, this would connect to a real-time orderbook system
    bids = [
        [49000.50, 0.5],
        [49000.00, 1.2],
        [48999.75, 0.8],
        [48999.00, 2.1],
        [48998.50, 0.3]
    ]
    
    asks = [
        [49001.00, 0.7],
        [49001.50, 1.5],
        [49002.00, 0.9],
        [49002.75, 1.8],
        [49003.00, 0.4]
    ]
    
    return jsonify({
        'symbol': symbol,
        'bids': bids[:limit],
        'asks': asks[:limit],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/orders', methods=['POST'])
@jwt_required()
@require_kyc
@require_trading_enabled
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['symbol', 'side', 'type', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate trading pair
    trading_pair = TradingPair.query.filter_by(symbol=data['symbol'], is_active=True).first()
    if not trading_pair:
        return jsonify({'error': 'Invalid trading pair'}), 400
    
    # Validate order parameters
    quantity = Decimal(str(data['quantity']))
    if quantity <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    if data['type'] in ['limit', 'stop_limit'] and not data.get('price'):
        return jsonify({'error': 'Price is required for limit orders'}), 400
    
    if data['type'] in ['stop_loss', 'stop_limit'] and not data.get('stop_price'):
        return jsonify({'error': 'Stop price is required for stop orders'}), 400
    
    # Check user balance
    user_wallet = Wallet.query.filter_by(
        user_id=user_id,
        asset=data['quote_asset'] if data['side'] == 'buy' else data['base_asset'],
        wallet_type=data.get('trading_type', 'spot')
    ).first()
    
    if not user_wallet:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Calculate required balance
    if data['side'] == 'buy':
        price = Decimal(str(data.get('price', 0)))
        required_balance = quantity * price if price > 0 else Decimal('0')
        if data['type'] == 'market':
            # For market buy, use estimated price
            required_balance = quantity * Decimal('50000')  # Estimated price
    else:
        required_balance = quantity
    
    if user_wallet.available_balance < required_balance:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Generate order ID
    order_id = f"TO{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Create order
    order = Order(
        order_id=order_id,
        user_id=user_id,
        symbol=data['symbol'],
        order_type=data['type'],
        side=data['side'],
        quantity=quantity,
        price=Decimal(str(data['price'])) if data.get('price') else None,
        stop_price=Decimal(str(data['stop_price'])) if data.get('stop_price') else None,
        time_in_force=data.get('time_in_force', 'GTC'),
        trading_type=data.get('trading_type', 'spot'),
        leverage=Decimal(str(data['leverage'])) if data.get('leverage') else None,
        post_only=data.get('post_only', False),
        reduce_only=data.get('reduce_only', False),
        expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
    )
    
    db.session.add(order)
    
    # Lock funds
    if data['side'] == 'buy':
        user_wallet.locked_balance += required_balance
        user_wallet.available_balance -= required_balance
    else:
        user_wallet.locked_balance += quantity
        user_wallet.available_balance -= quantity
    
    db.session.commit()
    
    # Process market orders immediately
    if order.order_type == 'market':
        process_market_order(order)
    
    return jsonify({
        'order_id': order_id,
        'symbol': data['symbol'],
        'side': data['side'],
        'type': data['type'],
        'quantity': float(quantity),
        'price': float(data['price']) if data.get('price') else None,
        'status': order.status
    }), 201

def process_market_order(order):
    """Process market order execution"""
    # This is a simplified market order processing
    # In production, this would match with the orderbook
    estimated_price = Decimal('50000')  # Get from orderbook
    executed_quantity = order.quantity
    executed_value = executed_quantity * estimated_price
    
    # Update order
    order.status = 'filled'
    order.executed_quantity = executed_quantity
    order.executed_value = executed_value
    order.average_price = estimated_price
    order.updated_at = datetime.utcnow()
    
    # Calculate fee
    fee_rate = Decimal('0.001')  # 0.1% fee
    order.fee = executed_value * fee_rate
    order.fee_currency = order.quote_asset
    
    # Create trade record
    trade_id = f"TT{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    trade = Trade(
        trade_id=trade_id,
        order_id=order.order_id,
        user_id=order.user_id,
        symbol=order.symbol,
        side=order.side,
        quantity=executed_quantity,
        price=estimated_price,
        quote_quantity=executed_value,
        fee=order.fee,
        fee_currency=order.fee_currency,
        trading_type=order.trading_type,
        is_maker=False
    )
    
    db.session.add(trade)
    
    # Update user wallets
    update_wallets_after_trade(order, trade)
    
    db.session.commit()

def update_wallets_after_trade(order, trade):
    """Update user wallets after trade execution"""
    user_id = order.user_id
    
    if order.side == 'buy':
        # Buying: deduct quote currency, add base currency
        quote_wallet = Wallet.query.filter_by(
            user_id=user_id,
            asset=order.quote_asset,
            wallet_type=order.trading_type
        ).first()
        
        base_wallet = Wallet.query.filter_by(
            user_id=user_id,
            asset=order.base_asset,
            wallet_type=order.trading_type
        ).first()
        
        if not base_wallet:
            base_wallet = Wallet(
                user_id=user_id,
                asset=order.base_asset,
                wallet_type=order.trading_type
            )
            db.session.add(base_wallet)
        
        # Update quote wallet
        if quote_wallet:
            quote_wallet.locked_balance -= order.executed_value
            quote_wallet.balance -= order.executed_value + trade.fee
            quote_wallet.available_balance = quote_wallet.balance - quote_wallet.locked_balance
        
        # Update base wallet
        base_wallet.balance += trade.quantity
        base_wallet.available_balance = base_wallet.balance - base_wallet.locked_balance
        
    else:  # sell
        # Selling: add quote currency, deduct base currency
        base_wallet = Wallet.query.filter_by(
            user_id=user_id,
            asset=order.base_asset,
            wallet_type=order.trading_type
        ).first()
        
        quote_wallet = Wallet.query.filter_by(
            user_id=user_id,
            asset=order.quote_asset,
            wallet_type=order.trading_type
        ).first()
        
        if not quote_wallet:
            quote_wallet = Wallet(
                user_id=user_id,
                asset=order.quote_asset,
                wallet_type=order.trading_type
            )
            db.session.add(quote_wallet)
        
        # Update base wallet
        if base_wallet:
            base_wallet.locked_balance -= order.quantity
            base_wallet.balance -= order.quantity
            base_wallet.available_balance = base_wallet.balance - base_wallet.locked_balance
        
        # Update quote wallet
        quote_wallet.balance += order.executed_value - trade.fee
        quote_wallet.available_balance = quote_wallet.balance - quote_wallet.locked_balance

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    symbol = request.args.get('symbol')
    
    query = Order.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    if symbol:
        query = query.filter_by(symbol=symbol)
    
    orders = query.order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'orders': [{
            'order_id': order.order_id,
            'symbol': order.symbol,
            'order_type': order.order_type,
            'side': order.side,
            'quantity': float(order.quantity),
            'price': float(order.price) if order.price else None,
            'stop_price': float(order.stop_price) if order.stop_price else None,
            'executed_quantity': float(order.executed_quantity),
            'executed_value': float(order.executed_value),
            'average_price': float(order.average_price) if order.average_price else None,
            'status': order.status,
            'fee': float(order.fee),
            'fee_currency': order.fee_currency,
            'trading_type': order.trading_type,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        } for order in orders.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': orders.total,
            'pages': orders.pages
        }
    })

@app.route('/api/orders/<order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    user_id = get_jwt_identity()
    
    order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status not in ['open', 'partially_filled']:
        return jsonify({'error': 'Order cannot be cancelled'}), 400
    
    # Unlock funds
    user_wallet = Wallet.query.filter_by(
        user_id=user_id,
        asset=order.quote_asset if order.side == 'buy' else order.base_asset,
        wallet_type=order.trading_type
    ).first()
    
    if user_wallet:
        remaining_quantity = order.quantity - order.executed_quantity
        if order.side == 'buy':
            remaining_value = remaining_quantity * (order.price or Decimal('0'))
            user_wallet.locked_balance -= remaining_value
            user_wallet.available_balance += remaining_value
        else:
            user_wallet.locked_balance -= remaining_quantity
            user_wallet.available_balance += remaining_quantity
    
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order_id': order_id
    })

@app.route('/api/wallet', methods=['GET'])
@jwt_required()
def get_wallet():
    user_id = get_jwt_identity()
    wallet_type = request.args.get('type', 'spot')
    
    wallets = Wallet.query.filter_by(user_id=user_id, wallet_type=wallet_type).all()
    
    return jsonify({
        'wallets': [{
            'asset': wallet.asset,
            'balance': float(wallet.balance),
            'locked_balance': float(wallet.locked_balance),
            'available_balance': float(wallet.available_balance),
            'wallet_type': wallet.wallet_type
        } for wallet in wallets]
    })

@app.route('/api/trading-bots', methods=['GET'])
@jwt_required()
def get_trading_bots():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    bots = TradingBot.query.filter_by(user_id=user_id)\
        .order_by(TradingBot.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'bots': [{
            'id': bot.id,
            'bot_id': bot.bot_id,
            'bot_name': bot.bot_name,
            'bot_type': bot.bot_type,
            'symbol': bot.symbol,
            'status': bot.status,
            'total_profit': float(bot.total_profit),
            'total_trades': bot.total_trades,
            'win_rate': float(bot.win_rate),
            'max_drawdown': float(bot.max_drawdown),
            'initial_investment': float(bot.initial_investment) if bot.initial_investment else None,
            'current_value': float(bot.current_value) if bot.current_value else None,
            'created_at': bot.created_at.isoformat(),
            'started_at': bot.started_at.isoformat() if bot.started_at else None,
            'stopped_at': bot.stopped_at.isoformat() if bot.stopped_at else None
        } for bot in bots.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': bots.total,
            'pages': bots.pages
        }
    })

@app.route('/api/trading-bots', methods=['POST'])
@jwt_required()
@require_kyc
def create_trading_bot():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['bot_name', 'bot_type', 'symbol', 'strategy_config']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    bot_id = f"TB{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    bot = TradingBot(
        user_id=user_id,
        bot_id=bot_id,
        bot_name=data['bot_name'],
        bot_type=data['bot_type'],
        symbol=data['symbol'],
        strategy_config=data['strategy_config'],
        initial_investment=Decimal(str(data.get('initial_investment', 0))),
        current_value=Decimal(str(data.get('initial_investment', 0)))
    )
    
    db.session.add(bot)
    db.session.commit()
    
    return jsonify({
        'message': 'Trading bot created successfully',
        'bot_id': bot_id,
        'status': bot.status
    }), 201

@app.route('/api/copy-trading/follow', methods=['POST'])
@jwt_required()
@require_kyc
def follow_trader():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['trader_id', 'copy_ratio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if already following
    existing = CopyTrading.query.filter_by(
        follower_id=user_id,
        trader_id=data['trader_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'Already following this trader'}), 400
    
    copy_trading = CopyTrading(
        follower_id=user_id,
        trader_id=data['trader_id'],
        copy_ratio=Decimal(str(data['copy_ratio'])),
        max_amount=Decimal(str(data['max_amount'])) if data.get('max_amount') else None,
        min_amount=Decimal(str(data['min_amount'])) if data.get('min_amount') else None,
        copy_long=data.get('copy_long', True),
        copy_short=data.get('copy_short', True)
    )
    
    db.session.add(copy_trading)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully started copying trader',
        'trader_id': data['trader_id'],
        'copy_ratio': float(data['copy_ratio'])
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5006, debug=True)