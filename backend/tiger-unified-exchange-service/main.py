#!/usr/bin/env python3

"""
Tiger Unified Exchange Service
Category: unified_trading
Description: Unified exchange integration for all major crypto exchanges
Features: Multi-exchange trading, unified API, advanced fetchers, admin controls
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
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from decimal import Decimal
from functools import wraps
from unified_exchange_fetchers import UnifiedExchangeFetcher, BinanceFetcher
from unified_admin_operations import AdminOperations
from unified_user_operations import UserOperations

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-unified-exchange-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize unified exchange components
unified_fetcher = UnifiedExchangeFetcher()
admin_ops = AdminOperations()
user_ops = UserOperations()

# Role-based access control
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'super_admin':
            return jsonify({'success': False, 'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Models
class User(db.Model):
    __tablename__ = 'tiger_unified_users'
    
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExchangeAccount(db.Model):
    __tablename__ = 'tiger_exchange_accounts'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tiger_unified_users.id'), nullable=False)
    exchange_name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    api_secret = db.Column(db.String(255), nullable=False)
    passphrase = db.Column(db.String(255))  # For exchanges like Coinbase
    is_active = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.JSON)  # Trading, withdrawal permissions
    last_sync = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='exchange_accounts')

class UnifiedOrder(db.Model):
    __tablename__ = 'tiger_unified_orders'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tiger_unified_users.id'), nullable=False)
    exchange_account_id = db.Column(db.String(50), db.ForeignKey('tiger_exchange_accounts.id'), nullable=False)
    exchange_order_id = db.Column(db.String(100))
    symbol = db.Column(db.String(20), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)  # market, limit, stop_loss, take_profit
    side = db.Column(db.String(10), nullable=False)  # buy, sell
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    filled_quantity = db.Column(db.Numeric(20, 8), default=0)
    status = db.Column(db.String(20), default='pending')  # pending, filled, cancelled, failed
    exchange_response = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='orders')
    exchange_account = db.relationship('ExchangeAccount', backref='orders')

class ExchangeSymbol(db.Model):
    __tablename__ = 'tiger_exchange_symbols'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange_name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    base_asset = db.Column(db.String(20), nullable=False)
    quote_asset = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    trading_enabled = db.Column(db.Boolean, default=True)
    min_order_size = db.Column(db.Numeric(20, 8))
    max_order_size = db.Column(db.Numeric(20, 8))
    price_precision = db.Column(db.Integer)
    quantity_precision = db.Column(db.Integer)
    tick_size = db.Column(db.Numeric(20, 8))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('exchange_name', 'symbol'),)

class MarketData(db.Model):
    __tablename__ = 'tiger_market_data'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange_name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # ticker, orderbook, trades, klines
    data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.Index('idx_market_data_lookup', 'exchange_name', 'symbol', 'data_type', 'timestamp'),)

# Market Data Routes
@app.route('/api/tiger-unified/market/ticker/<exchange>/<symbol>', methods=['GET'])
@jwt_required()
def get_ticker(exchange, symbol):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        ticker_data = loop.run_until_complete(
            unified_fetcher.get_ticker_24hr(exchange, symbol)
        )
        loop.close()
        
        # Store in database for historical tracking
        market_data = MarketData(
            exchange_name=exchange,
            symbol=symbol,
            data_type='ticker',
            data=ticker_data,
            timestamp=datetime.utcnow()
        )
        db.session.add(market_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exchange': exchange,
            'symbol': symbol,
            'data': ticker_data
        })
    except Exception as e:
        logger.error(f"Error getting ticker: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/market/orderbook/<exchange>/<symbol>', methods=['GET'])
@jwt_required()
def get_orderbook(exchange, symbol):
    try:
        limit = request.args.get('limit', 100, type=int)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        orderbook_data = loop.run_until_complete(
            unified_fetcher.get_order_book(exchange, symbol, limit)
        )
        loop.close()
        
        # Store in database
        market_data = MarketData(
            exchange_name=exchange,
            symbol=symbol,
            data_type='orderbook',
            data=orderbook_data,
            timestamp=datetime.utcnow()
        )
        db.session.add(market_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exchange': exchange,
            'symbol': symbol,
            'limit': limit,
            'data': orderbook_data
        })
    except Exception as e:
        logger.error(f"Error getting orderbook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/market/trades/<exchange>/<symbol>', methods=['GET'])
@jwt_required()
def get_recent_trades(exchange, symbol):
    try:
        limit = request.args.get('limit', 500, type=int)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        trades_data = loop.run_until_complete(
            unified_fetcher.get_recent_trades(exchange, symbol, limit)
        )
        loop.close()
        
        # Store in database
        market_data = MarketData(
            exchange_name=exchange,
            symbol=symbol,
            data_type='trades',
            data=trades_data,
            timestamp=datetime.utcnow()
        )
        db.session.add(market_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exchange': exchange,
            'symbol': symbol,
            'limit': limit,
            'data': trades_data
        })
    except Exception as e:
        logger.error(f"Error getting recent trades: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/market/klines/<exchange>/<symbol>', methods=['GET'])
@jwt_required()
def get_klines(exchange, symbol):
    try:
        interval = request.args.get('interval', '1h')
        limit = request.args.get('limit', 500, type=int)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        klines_data = loop.run_until_complete(
            unified_fetcher.get_klines(exchange, symbol, interval, limit)
        )
        loop.close()
        
        # Store in database
        market_data = MarketData(
            exchange_name=exchange,
            symbol=symbol,
            data_type='klines',
            data={'interval': interval, 'data': klines_data},
            timestamp=datetime.utcnow()
        )
        db.session.add(market_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exchange': exchange,
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'data': klines_data
        })
    except Exception as e:
        logger.error(f"Error getting klines: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Trading Routes
@app.route('/api/tiger-unified/trading/accounts', methods=['GET'])
@jwt_required()
def get_exchange_accounts():
    try:
        user_id = get_jwt_identity()
        accounts = ExchangeAccount.query.filter_by(user_id=user_id, is_active=True).all()
        
        accounts_data = []
        for account in accounts:
            # Hide sensitive data
            accounts_data.append({
                'id': account.id,
                'exchange_name': account.exchange_name,
                'is_active': account.is_active,
                'permissions': account.permissions,
                'last_sync': account.last_sync.isoformat() if account.last_sync else None,
                'created_at': account.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'accounts': accounts_data
        })
    except Exception as e:
        logger.error(f"Error getting exchange accounts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/trading/balance/<exchange_account_id>', methods=['GET'])
@jwt_required()
def get_account_balance(exchange_account_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify account ownership
        account = ExchangeAccount.query.filter_by(
            id=exchange_account_id, 
            user_id=user_id, 
            is_active=True
        ).first()
        
        if not account:
            return jsonify({'success': False, 'error': 'Exchange account not found'}), 404
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create fetcher for the specific exchange
        if account.exchange_name.lower() == 'binance':
            fetcher = BinanceFetcher(account.api_key, account.api_secret)
        else:
            return jsonify({'success': False, 'error': 'Exchange not supported yet'}), 400
        
        async with fetcher:
            balance_data = await fetcher.get_account_balance()
        
        loop.close()
        
        # Update last sync
        account.last_sync = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'exchange': account.exchange_name,
            'balance': balance_data,
            'last_sync': account.last_sync.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting account balance: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/trading/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        
        query = UnifiedOrder.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        orders = query.order_by(UnifiedOrder.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        orders_data = []
        for order in orders.items:
            orders_data.append({
                'id': order.id,
                'exchange': order.exchange_account.exchange_name,
                'symbol': order.symbol,
                'order_type': order.order_type,
                'side': order.side,
                'quantity': float(order.quantity),
                'price': float(order.price) if order.price else None,
                'filled_quantity': float(order.filled_quantity),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data,
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin Routes
@app.route('/api/tiger-unified/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        total_users = User.query.count()
        total_accounts = ExchangeAccount.query.count()
        total_orders = UnifiedOrder.query.count()
        total_symbols = ExchangeSymbol.query.count()
        
        # Exchange distribution
        exchange_distribution = db.session.query(
            ExchangeAccount.exchange_name,
            db.func.count(ExchangeAccount.id)
        ).group_by(ExchangeAccount.exchange_name).all()
        
        # Order status distribution
        order_status_distribution = db.session.query(
            UnifiedOrder.status,
            db.func.count(UnifiedOrder.id)
        ).group_by(UnifiedOrder.status).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_exchange_accounts': total_accounts,
                'total_orders': total_orders,
                'total_symbols': total_symbols,
                'exchange_distribution': {name: count for name, count in exchange_distribution},
                'order_status_distribution': {status: count for status, count in order_status_distribution},
                'service_name': 'tiger-unified-exchange-service',
                'category': 'unified_trading'
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in users.items:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'exchange_accounts_count': len(user.exchange_accounts),
                'orders_count': len(user.orders),
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting admin users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/admin/users/<user_id>/role', methods=['PUT'])
@super_admin_required
def admin_update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin', 'super_admin']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.role = new_role
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User role updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-unified/admin/exchanges', methods=['GET'])
@admin_required
def admin_get_exchanges():
    try:
        exchanges = db.session.query(
            ExchangeSymbol.exchange_name,
            db.func.count(ExchangeSymbol.id).label('symbol_count')
        ).group_by(ExchangeSymbol.exchange_name).all()
        
        exchanges_data = [{
            'name': exchange[0],
            'symbol_count': exchange[1]
        } for exchange in exchanges]
        
        return jsonify({
            'success': True,
            'exchanges': exchanges_data
        })
    except Exception as e:
        logger.error(f"Error getting admin exchanges: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'tiger-unified-exchange-service',
        'category': 'unified_trading',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5005)), debug=True)