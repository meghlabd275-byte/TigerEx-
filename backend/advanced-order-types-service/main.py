#!/usr/bin/env python3

"""
TigerEx Advanced Order Types Service
Category: trading_enhancement
Description: Advanced order types including Chase Limit, Iceberg, TWAP, Conditional Orders
Features: Dynamic price adjustment, large order handling, algorithmic execution
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
import threading
import time
from dataclasses import dataclass
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-advanced-orders-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    CHASE_LIMIT = "chase_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    CONDITIONAL = "conditional"
    POST_ONLY = "post_only"

class OrderStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PARTIALLY_FILLED = "partially_filled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class MarketData:
    symbol: str
    best_bid: Decimal
    best_ask: Decimal
    bid_size: Decimal
    ask_size: Decimal
    volume_24h: Decimal
    timestamp: datetime

class AdvancedOrder(db.Model):
    __tablename__ = 'tiger_advanced_orders'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    order_type = db.Column(db.Enum(OrderType), nullable=False)
    side = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    
    # Base order parameters
    total_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    filled_quantity = db.Column(db.Numeric(20, 8), default=0)
    remaining_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Chase Limit specific
    chase_distance = db.Column(db.Numeric(10, 8))  # Distance from best bid/ask
    max_chase_price = db.Column(db.Numeric(20, 8))
    min_chase_price = db.Column(db.Numeric(20, 8))
    
    # Iceberg specific
    display_quantity = db.Column(db.Numeric(20, 8))  # Visible quantity
    randomization = db.Column(db.Numeric(5, 4), default=0)  # Randomization factor
    
    # TWAP specific
    duration_minutes = db.Column(db.Integer)
    num_slices = db.Column(db.Integer)
    
    # Conditional specific
    condition_type = db.Column(db.String(20))  # price_trigger, time_trigger, volume_trigger
    condition_value = db.Column(db.Numeric(20, 8))
    trigger_symbol = db.Column(db.String(20))  # For cross-market conditions
    
    # Common fields
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Execution parameters
    time_in_force = db.Column(db.String(10), default='GTC')  # GTC, IOC, FOK
    reduce_only = db.Column(db.Boolean, default=False)
    post_only = db.Column(db.Boolean, default=False)
    
    # Metadata
    metadata = db.Column(db.JSON)
    child_orders = db.Column(db.JSON)  # Track generated child orders

class OrderExecution(db.Model):
    __tablename__ = 'tiger_order_executions'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    advanced_order_id = db.Column(db.String(50), db.ForeignKey('tiger_advanced_orders.id'), nullable=False)
    child_order_id = db.Column(db.String(50))
    
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(4), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    execution_price = db.Column(db.Numeric(20, 8))
    
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    
    # Execution details
    fee = db.Column(db.Numeric(20, 8))
    fee_currency = db.Column(db.String(10))
    exchange_order_id = db.Column(db.String(100))
    
    advanced_order = db.relationship('AdvancedOrder', backref='executions')

class ChaseLimitOrderManager:
    def __init__(self):
        self.active_orders = {}
        self.market_data = {}
        
    async def execute_chase_limit(self, order: AdvancedOrder, market_data: MarketData):
        """Execute Chase Limit Order logic"""
        if order.side == 'buy':
            # For buy orders, chase the best ask
            target_price = market_data.best_ask - Decimal(str(order.chase_distance))
            if order.max_chase_price:
                target_price = min(target_price, Decimal(str(order.max_chase_price)))
            if order.min_chase_price:
                target_price = max(target_price, Decimal(str(order.min_chase_price)))
        else:
            # For sell orders, chase the best bid
            target_price = market_data.best_bid + Decimal(str(order.chase_distance))
            if order.max_chase_price:
                target_price = min(target_price, Decimal(str(order.max_chase_price)))
            if order.min_chase_price:
                target_price = max(target_price, Decimal(str(order.min_chase_price)))
        
        return target_price
    
    async def monitor_and_adjust(self, order: AdvancedOrder):
        """Monitor market and adjust chase limit orders"""
        while order.status == OrderStatus.ACTIVE:
            try:
                # Get latest market data
                current_market = await self.get_market_data(order.symbol)
                if not current_market:
                    await asyncio.sleep(1)
                    continue
                
                # Calculate new target price
                new_price = await self.execute_chase_limit(order, current_market)
                
                # Check if we should place/update order
                if await self.should_place_order(order, new_price, current_market):
                    await self.place_or_update_order(order, new_price)
                
                await asyncio.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                logger.error(f"Error in chase limit monitoring for order {order.id}: {e}")
                await asyncio.sleep(1)
    
    async def should_place_order(self, order: AdvancedOrder, target_price: Decimal, market_data: MarketData) -> bool:
        """Determine if we should place a new order"""
        # Logic to determine if order should be placed based on market conditions
        if order.side == 'buy':
            return target_price >= market_data.best_ask - Decimal('0.01')  # Within 0.01 of market
        else:
            return target_price <= market_data.best_bid + Decimal('0.01')
    
    async def place_or_update_order(self, order: AdvancedOrder, price: Decimal):
        """Place or update the chase limit order"""
        # Implementation to place/update order on exchange
        execution = OrderExecution(
            advanced_order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=min(Decimal(str(order.remaining_quantity)), Decimal('1.0')),  # Chunk size
            price=price
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # Update order status
        order.updated_at = datetime.utcnow()
        db.session.commit()

class IcebergOrderManager:
    def __init__(self):
        self.active_orders = {}
        
    async def execute_iceberg(self, order: AdvancedOrder):
        """Execute Iceberg Order logic"""
        display_qty = Decimal(str(order.display_quantity))
        
        # Apply randomization if specified
        if order.randomization:
            random_factor = 1 + (order.randomization * (0.5 - time.time() % 1))
            display_qty = display_qty * Decimal(str(random_factor))
        
        return display_qty
    
    async def place_iceberg_slice(self, order: AdvancedOrder):
        """Place a slice of the iceberg order"""
        slice_quantity = await self.execute_iceberg(order)
        slice_quantity = min(slice_quantity, Decimal(str(order.remaining_quantity)))
        
        if slice_quantity <= 0:
            return None
        
        execution = OrderExecution(
            advanced_order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=slice_quantity
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # Update remaining quantity
        order.remaining_quantity -= slice_quantity
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return execution

class TWAPOrderManager:
    def __init__(self):
        self.active_orders = {}
        
    async def execute_twap(self, order: AdvancedOrder):
        """Execute TWAP (Time-Weighted Average Price) Order logic"""
        duration_seconds = order.duration_minutes * 60
        slice_interval = duration_seconds / order.num_slices
        slice_quantity = Decimal(str(order.total_quantity)) / order.num_slices
        
        return {
            'interval': slice_interval,
            'quantity': slice_quantity,
            'total_slices': order.num_slices
        }
    
    async def place_twap_slice(self, order: AdvancedOrder):
        """Place a TWAP slice"""
        twap_params = await self.execute_twap(order)
        
        execution = OrderExecution(
            advanced_order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=twap_params['quantity']
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # Update remaining quantity
        order.remaining_quantity -= twap_params['quantity']
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return execution, twap_params['interval']

class ConditionalOrderManager:
    def __init__(self):
        self.active_orders = {}
        
    async def check_condition(self, order: AdvancedOrder, market_data: MarketData) -> bool:
        """Check if conditional order conditions are met"""
        if order.condition_type == 'price_trigger':
            if order.side == 'buy':
                return market_data.best_ask <= Decimal(str(order.condition_value))
            else:
                return market_data.best_bid >= Decimal(str(order.condition_value))
        
        elif order.condition_type == 'volume_trigger':
            return market_data.volume_24h >= Decimal(str(order.condition_value))
        
        elif order.condition_type == 'time_trigger':
            trigger_time = datetime.fromisoformat(order.condition_value)
            return datetime.utcnow() >= trigger_time
        
        return False
    
    async def activate_conditional_order(self, order: AdvancedOrder):
        """Activate order when conditions are met"""
        order.status = OrderStatus.ACTIVE
        order.activated_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Place the actual order
        execution = OrderExecution(
            advanced_order_id=order.id,
            symbol=order.symbol,
            side=order.side,
            quantity=Decimal(str(order.remaining_quantity))
        )
        
        db.session.add(execution)
        db.session.commit()
        return execution

# Initialize managers
chase_manager = ChaseLimitOrderManager()
iceberg_manager = IcebergOrderManager()
twap_manager = TWAPOrderManager()
conditional_manager = ConditionalOrderManager()

# API Routes
@app.route('/api/v1/advanced-orders', methods=['POST'])
@jwt_required()
def create_advanced_order():
    """Create an advanced order"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        order = AdvancedOrder(
            user_id=user_id,
            symbol=data['symbol'],
            order_type=OrderType(data['order_type']),
            side=data['side'],
            total_quantity=data['total_quantity'],
            remaining_quantity=data['total_quantity'],
            time_in_force=data.get('time_in_force', 'GTC'),
            reduce_only=data.get('reduce_only', False),
            post_only=data.get('post_only', False),
            metadata=data.get('metadata', {})
        )
        
        # Set type-specific parameters
        if order.order_type == OrderType.CHASE_LIMIT:
            order.chase_distance = data.get('chase_distance', '0.01')
            order.max_chase_price = data.get('max_chase_price')
            order.min_chase_price = data.get('min_chase_price')
        
        elif order.order_type == OrderType.ICEBERG:
            order.display_quantity = data['display_quantity']
            order.randomization = data.get('randomization', 0)
        
        elif order.order_type == OrderType.TWAP:
            order.duration_minutes = data['duration_minutes']
            order.num_slices = data['num_slices']
        
        elif order.order_type == OrderType.CONDITIONAL:
            order.condition_type = data['condition_type']
            order.condition_value = data['condition_value']
            order.trigger_symbol = data.get('trigger_symbol')
        
        db.session.add(order)
        db.session.commit()
        
        # Start execution in background
        threading.Thread(target=start_order_execution, args=(order.id,), daemon=True).start()
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'status': order.status.value
        })
        
    except Exception as e:
        logger.error(f"Error creating advanced order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/advanced-orders/<order_id>', methods=['GET'])
@jwt_required()
def get_advanced_order(order_id):
    """Get advanced order details"""
    try:
        user_id = get_jwt_identity()
        order = AdvancedOrder.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        executions = OrderExecution.query.filter_by(advanced_order_id=order_id).all()
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'symbol': order.symbol,
                'order_type': order.order_type.value,
                'side': order.side,
                'total_quantity': str(order.total_quantity),
                'filled_quantity': str(order.filled_quantity),
                'remaining_quantity': str(order.remaining_quantity),
                'status': order.status.value,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
                'metadata': order.metadata
            },
            'executions': [{
                'id': exec.id,
                'quantity': str(exec.quantity),
                'price': str(exec.price) if exec.price else None,
                'execution_price': str(exec.execution_price) if exec.execution_price else None,
                'status': exec.status,
                'created_at': exec.created_at.isoformat()
            } for exec in executions]
        })
        
    except Exception as e:
        logger.error(f"Error getting advanced order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/advanced-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_advanced_order(order_id):
    """Cancel an advanced order"""
    try:
        user_id = get_jwt_identity()
        order = AdvancedOrder.query.filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            return jsonify({'success': False, 'error': 'Order cannot be cancelled'}), 400
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'status': 'cancelled'})
        
    except Exception as e:
        logger.error(f"Error cancelling advanced order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/advanced-orders', methods=['GET'])
@jwt_required()
def list_advanced_orders():
    """List user's advanced orders"""
    try:
        user_id = get_jwt_identity()
        status_filter = request.args.get('status')
        symbol_filter = request.args.get('symbol')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = AdvancedOrder.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter_by(status=OrderType(status_filter))
        if symbol_filter:
            query = query.filter_by(symbol=symbol_filter)
        
        orders = query.order_by(AdvancedOrder.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'orders': [{
                'id': order.id,
                'symbol': order.symbol,
                'order_type': order.order_type.value,
                'side': order.side,
                'total_quantity': str(order.total_quantity),
                'filled_quantity': str(order.filled_quantity),
                'remaining_quantity': str(order.remaining_quantity),
                'status': order.status.value,
                'created_at': order.created_at.isoformat()
            } for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing advanced orders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def start_order_execution(order_id):
    """Background thread to execute advanced order"""
    try:
        order = AdvancedOrder.query.get(order_id)
        if not order:
            return
        
        order.status = OrderStatus.ACTIVE
        order.activated_at = datetime.utcnow()
        db.session.commit()
        
        if order.order_type == OrderType.CHASE_LIMIT:
            # Start async chase limit execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(chase_manager.monitor_and_adjust(order))
            loop.close()
            
        elif order.order_type == OrderType.ICEBERG:
            # Execute iceberg slices
            while order.remaining_quantity > 0 and order.status == OrderStatus.ACTIVE:
                execution = iceberg_manager.place_iceberg_slice(order)
                if execution:
                    time.sleep(2)  # Wait between slices
                else:
                    break
                    
        elif order.order_type == OrderType.TWAP:
            # Execute TWAP slices
            execution, interval = twap_manager.place_twap_slice(order)
            while order.remaining_quantity > 0 and order.status == OrderStatus.ACTIVE:
                time.sleep(interval)
                execution, _ = twap_manager.place_twap_slice(order)
                
        elif order.order_type == OrderType.CONDITIONAL:
            # Monitor conditions
            while order.status == OrderStatus.ACTIVE:
                market_data = get_market_data(order.symbol)
                if market_data and conditional_manager.check_condition(order, market_data):
                    conditional_manager.activate_conditional_order(order)
                    break
                time.sleep(5)
        
        # Check if order is completed
        if order.remaining_quantity <= 0:
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error in order execution for {order_id}: {e}")
        order.status = OrderStatus.FAILED
        db.session.commit()

def get_market_data(symbol):
    """Get current market data for a symbol"""
    # This would integrate with your market data service
    # For now, return mock data
    return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5004, debug=True)