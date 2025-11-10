#!/usr/bin/env python3
"""
Derivatives Trading Service for TigerEx v11.0.0
Advanced derivatives trading with options, futures, and perpetual contracts
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import numpy as np
from decimal import Decimal
from enum import Enum

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

# Enums
class DerivativeType(str, Enum):
    FUTURE = "future"
    PERPETUAL = "perpetual"
    OPTION_CALL = "option_call"
    OPTION_PUT = "option_put"

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class OrderSide(str, Enum):
    LONG = "long"
    SHORT = "short"

class OrderStatus(str, Enum):
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    LIQUIDATED = "liquidated"

# Models
class DerivativeContract(db.Model):
    __tablename__ = 'derivative_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(64), nullable=False, unique=True)
    symbol = db.Column(db.String(20), nullable=False)
    contract_type = db.Column(db.Enum(DerivativeType), nullable=False)
    underlying_asset = db.Column(db.String(20), nullable=False)
    
    # Contract specifications
    contract_size = db.Column(db.Numeric(20, 8), nullable=False)
    tick_size = db.Column(db.Numeric(20, 8), nullable=False)
    notional_value = db.Column(db.Numeric(20, 8))
    
    # Futures/Perpetual specific
    settlement_date = db.Column(db.DateTime)
    funding_rate = db.Column(db.Float, default=0)
    funding_interval = db.Column(db.Integer, default=8)  # hours
    
    # Options specific
    strike_price = db.Column(db.Numeric(20, 8))
    expiration_date = db.Column(db.DateTime)
    option_type = db.Column(db.Enum(OptionType))
    implied_volatility = db.Column(db.Float)
    
    # Risk parameters
    initial_margin = db.Column(db.Float)
    maintenance_margin = db.Column(db.Float)
    max_leverage = db.Column(db.Integer, default=10)
    
    # Market data
    mark_price = db.Column(db.Numeric(20, 8))
    index_price = db.Column(db.Numeric(20, 8))
    fair_price = db.Column(db.Numeric(20, 8))
    
    # Volume and open interest
    volume_24h = db.Column(db.Numeric(20, 8), default=0)
    open_interest = db.Column(db.Numeric(20, 8), default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DerivativeOrder(db.Model):
    __tablename__ = 'derivative_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.String(50), nullable=False)
    contract_id = db.Column(db.String(64), db.ForeignKey('derivative_contracts.contract_id'), nullable=False)
    
    # Order details
    side = db.Column(db.Enum(OrderSide), nullable=False)
    order_type = db.Column(db.String(20), default='market')  # market, limit, stop, stop_limit
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    
    # Execution details
    executed_quantity = db.Column(db.Numeric(20, 8), default=0)
    executed_price = db.Column(db.Numeric(20, 8))
    average_price = db.Column(db.Numeric(20, 8))
    
    # Leverage and margin
    leverage = db.Column(db.Integer, default=1)
    initial_margin = db.Column(db.Numeric(20, 8))
    maintenance_margin = db.Column(db.Numeric(20, 8))
    
    # Status and timing
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.OPEN)
    time_in_force = db.Column(db.String(10), default='GTC')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = db.Column(db.DateTime)
    
    # Relationship
    contract = db.relationship('DerivativeContract', backref=db.backref('orders', lazy=True))

class DerivativePosition(db.Model):
    __tablename__ = 'derivative_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.String(50), nullable=False)
    contract_id = db.Column(db.String(64), db.ForeignKey('derivative_contracts.contract_id'), nullable=False)
    
    # Position details
    side = db.Column(db.Enum(OrderSide), nullable=False)
    size = db.Column(db.Numeric(20, 8), nullable=False)
    entry_price = db.Column(db.Numeric(20, 8), nullable=False)
    mark_price = db.Column(db.Numeric(20, 8))
    
    # P&L calculations
    unrealized_pnl = db.Column(db.Numeric(20, 8), default=0)
    realized_pnl = db.Column(db.Numeric(20, 8), default=0)
    funding_payments = db.Column(db.Numeric(20, 8), default=0)
    
    # Margin calculations
    initial_margin = db.Column(db.Numeric(20, 8))
    maintenance_margin = db.Column(db.Numeric(20, 8))
    margin_ratio = db.Column(db.Float)
    
    # Risk metrics
    liquidation_price = db.Column(db.Numeric(20, 8))
    bankruptcy_price = db.Column(db.Numeric(20, 8))
    leverage = db.Column(db.Integer)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    contract = db.relationship('DerivativeContract', backref=db.backref('positions', lazy=True))

class DerivativeTrade(db.Model):
    __tablename__ = 'derivative_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(64), nullable=False, unique=True)
    order_id = db.Column(db.String(64), db.ForeignKey('derivative_orders.order_id'), nullable=False)
    contract_id = db.Column(db.String(64), db.ForeignKey('derivative_contracts.contract_id'), nullable=False)
    
    # Trade details
    side = db.Column(db.Enum(OrderSide), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    notional_value = db.Column(db.Numeric(20, 8))
    
    # Fees
    trading_fee = db.Column(db.Numeric(20, 8), default=0)
    funding_fee = db.Column(db.Numeric(20, 8), default=0)
    
    # P&L for closing trades
    realized_pnl = db.Column(db.Numeric(20, 8), default=0)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('DerivativeOrder', backref=db.backref('trades', lazy=True))
    contract = db.relationship('DerivativeContract', backref=db.backref('trades', lazy=True))

class FundingRate(db.Model):
    __tablename__ = 'funding_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(64), db.ForeignKey('derivative_contracts.contract_id'), nullable=False)
    
    # Rate information
    rate = db.Column(db.Float, nullable=False)
    index_price = db.Column(db.Numeric(20, 8))
    mark_price = db.Column(db.Numeric(20, 8))
    
    # Calculation period
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    contract = db.relationship('DerivativeContract', backref=db.backref('funding_rates', lazy=True))

class DerivativesEngine:
    def __init__(self):
        self.black_scholes_params = {
            'risk_free_rate': 0.02,
            'default_volatility': 0.25
        }
    
    def calculate_option_price(self, option_type, S, K, T, r=0.02, sigma=0.25):
        """Calculate option price using Black-Scholes model"""
        from scipy.stats import norm
        
        if T <= 0:
            if option_type == OptionType.CALL:
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == OptionType.CALL:
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return price
    
    def calculate_funding_rate(self, contract_id):
        """Calculate funding rate for perpetual contracts"""
        contract = DerivativeContract.query.filter_by(contract_id=contract_id).first()
        if not contract or contract.contract_type != DerivativeType.PERPETUAL:
            return 0
        
        # Simplified funding rate calculation
        # In practice, this would be based on the difference between index and mark price
        index_price = float(contract.index_price or 0)
        mark_price = float(contract.mark_price or index_price)
        
        if index_price > 0 and mark_price > 0:
            price_diff = (mark_price - index_price) / index_price
            funding_rate = price_diff / (24 / contract.funding_interval)  # Normalize to funding interval
        else:
            funding_rate = 0.01  # Default 1% daily
        
        # Cap funding rate to prevent extreme values
        funding_rate = max(min(funding_rate, 0.01), -0.01)
        
        return funding_rate
    
    def calculate_liquidation_price(self, position):
        """Calculate liquidation price for a position"""
        contract = position.contract
        entry_price = float(position.entry_price)
        leverage = position.leverage or contract.max_leverage
        maintenance_margin = contract.maintenance_margin / 100
        
        if position.side == OrderSide.LONG:
            # For long positions
            liquidation_price = entry_price * (1 - 1/leverage + maintenance_margin)
        else:
            # For short positions
            liquidation_price = entry_price * (1 + 1/leverage - maintenance_margin)
        
        return liquidation_price
    
    def calculate_unrealized_pnl(self, position):
        """Calculate unrealized P&L for a position"""
        mark_price = float(position.contract.mark_price or position.entry_price)
        entry_price = float(position.entry_price)
        size = float(position.size)
        
        if position.side == OrderSide.LONG:
            pnl = (mark_price - entry_price) * size
        else:
            pnl = (entry_price - mark_price) * size
        
        return pnl
    
    def process_funding_payment(self, position, funding_rate):
        """Process funding payment for perpetual positions"""
        if position.contract.contract_type != DerivativeType.PERPETUAL:
            return 0
        
        mark_price = float(position.contract.mark_price or 0)
        size = float(position.size)
        
        # Funding payment = position_size * mark_price * funding_rate * (funding_interval / 24)
        funding_payment = size * mark_price * funding_rate * (position.contract.funding_interval / 24)
        
        # Apply payment based on position side
        if position.side == OrderSide.LONG:
            # Long positions pay funding if rate is positive
            if funding_rate > 0:
                position.funding_payments -= funding_payment
            else:
                position.funding_payments += abs(funding_payment)
        else:
            # Short positions receive funding if rate is positive
            if funding_rate > 0:
                position.funding_payments += funding_payment
            else:
                position.funding_payments -= abs(funding_payment)
        
        return funding_payment
    
    def check_margin_requirements(self, position):
        """Check if position meets margin requirements"""
        unrealized_pnl = self.calculate_unrealized_pnl(position)
        initial_margin = float(position.initial_margin)
        
        # Account for unrealized P&L and funding payments
        available_margin = initial_margin + unrealized_pnl + position.funding_payments
        maintenance_margin = float(position.maintenance_margin)
        
        return available_margin >= maintenance_margin
    
    def calculate_option_greeks(self, option_type, S, K, T, r=0.02, sigma=0.25):
        """Calculate option Greeks using Black-Scholes"""
        from scipy.stats import norm
        
        if T <= 0:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == OptionType.CALL:
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                     - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100 if option_type == OptionType.CALL else -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }

# Initialize derivatives engine
derivatives_engine = DerivativesEngine()

# API Routes
@app.route('/api/derivatives/contracts', methods=['GET'])
@jwt_required()
def get_derivative_contracts():
    try:
        contract_type = request.args.get('type')
        underlying = request.args.get('underlying')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = DerivativeContract.query
        
        if contract_type:
            query = query.filter_by(contract_type=DerivativeType(contract_type))
        if underlying:
            query = query.filter_by(underlying_asset=underlying)
        if active_only:
            query = query.filter_by(is_active=True)
        
        contracts = query.all()
        
        return jsonify({
            'success': True,
            'contracts': [
                {
                    'contract_id': contract.contract_id,
                    'symbol': contract.symbol,
                    'contract_type': contract.contract_type,
                    'underlying_asset': contract.underlying_asset,
                    'contract_size': float(contract.contract_size),
                    'tick_size': float(contract.tick_size),
                    'settlement_date': contract.settlement_date.isoformat() if contract.settlement_date else None,
                    'strike_price': float(contract.strike_price) if contract.strike_price else None,
                    'expiration_date': contract.expiration_date.isoformat() if contract.expiration_date else None,
                    'option_type': contract.option_type,
                    'funding_rate': contract.funding_rate,
                    'mark_price': float(contract.mark_price or 0),
                    'volume_24h': float(contract.volume_24h),
                    'open_interest': float(contract.open_interest),
                    'max_leverage': contract.max_leverage
                }
                for contract in contracts
            ]
        })
    except Exception as e:
        logger.error(f"Error getting derivative contracts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/derivatives/order', methods=['POST'])
@jwt_required()
def create_derivative_order():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        contract_id = data.get('contract_id')
        side = OrderSide(data.get('side'))
        quantity = Decimal(str(data.get('quantity')))
        price = Decimal(str(data.get('price'))) if data.get('price') else None
        leverage = data.get('leverage', 1)
        
        # Validate contract
        contract = DerivativeContract.query.filter_by(contract_id=contract_id, is_active=True).first()
        if not contract:
            return jsonify({'success': False, 'error': 'Contract not found or inactive'}), 404
        
        # Validate leverage
        if leverage > contract.max_leverage:
            return jsonify({'success': False, 'error': f'Leverage exceeds maximum of {contract.max_leverage}x'}), 400
        
        # Calculate margin requirements
        if price is None:
            price = contract.mark_price or Decimal('0')
        
        notional_value = quantity * price
        initial_margin = notional_value / leverage
        maintenance_margin = notional_value / contract.max_leverage * (contract.maintenance_margin / 100)
        
        # Create order
        order = DerivativeOrder(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            contract_id=contract_id,
            side=side,
            order_type=data.get('order_type', 'market'),
            quantity=quantity,
            price=price,
            leverage=leverage,
            initial_margin=initial_margin,
            maintenance_margin=maintenance_margin
        )
        
        db.session.add(order)
        db.session.flush()
        
        # For market orders, execute immediately (simplified)
        if order.order_type == 'market':
            order.status = OrderStatus.FILLED
            order.executed_quantity = quantity
            order.executed_price = price
            order.average_price = price
            order.filled_at = datetime.utcnow()
            
            # Create or update position
            position = DerivativePosition.query.filter_by(
                user_id=user_id, contract_id=contract_id, side=side, is_active=True
            ).first()
            
            if position:
                # Update existing position
                total_size = position.size + quantity
                position.entry_price = ((position.entry_price * position.size) + (price * quantity)) / total_size
                position.size = total_size
                position.initial_margin += initial_margin
                position.maintenance_margin += maintenance_margin
                position.leverage = leverage
            else:
                # Create new position
                position = DerivativePosition(
                    position_id=str(uuid.uuid4()),
                    user_id=user_id,
                    contract_id=contract_id,
                    side=side,
                    size=quantity,
                    entry_price=price,
                    mark_price=price,
                    initial_margin=initial_margin,
                    maintenance_margin=maintenance_margin,
                    leverage=leverage
                )
                db.session.add(position)
            
            # Calculate liquidation price
            position.liquidation_price = derivatives_engine.calculate_liquidation_price(position)
            
            # Create trade record
            trade = DerivativeTrade(
                trade_id=str(uuid.uuid4()),
                order_id=order.order_id,
                contract_id=contract_id,
                side=side,
                quantity=quantity,
                price=price,
                notional_value=notional_value
            )
            db.session.add(trade)
            
            # Update contract volume
            contract.volume_24h += quantity
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order': {
                'order_id': order.order_id,
                'contract_id': contract_id,
                'side': side,
                'quantity': float(quantity),
                'price': float(price),
                'status': order.status,
                'leverage': leverage,
                'initial_margin': float(initial_margin)
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating derivative order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/derivatives/positions', methods=['GET'])
@jwt_required()
def get_derivative_positions():
    try:
        user_id = get_jwt_identity()
        contract_id = request.args.get('contract_id')
        
        query = DerivativePosition.query.filter_by(user_id=user_id, is_active=True)
        
        if contract_id:
            query = query.filter_by(contract_id=contract_id)
        
        positions = query.all()
        
        result = []
        for position in positions:
            # Update unrealized P&L
            unrealized_pnl = derivatives_engine.calculate_unrealized_pnl(position)
            position.unrealized_pnl = unrealized_pnl
            position.mark_price = position.contract.mark_price
            
            result.append({
                'position_id': position.position_id,
                'contract_id': position.contract_id,
                'symbol': position.contract.symbol,
                'side': position.side,
                'size': float(position.size),
                'entry_price': float(position.entry_price),
                'mark_price': float(position.mark_price or 0),
                'unrealized_pnl': float(unrealized_pnl),
                'realized_pnl': float(position.realized_pnl),
                'funding_payments': float(position.funding_payments),
                'leverage': position.leverage,
                'initial_margin': float(position.initial_margin),
                'maintenance_margin': float(position.maintenance_margin),
                'liquidation_price': float(position.liquidation_price) if position.liquidation_price else None,
                'created_at': position.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'positions': result
        })
    except Exception as e:
        logger.error(f"Error getting derivative positions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/derivatives/option-pricing', methods=['POST'])
@jwt_required()
def calculate_option_price():
    try:
        data = request.get_json()
        
        option_type = OptionType(data.get('option_type'))
        underlying_price = float(data.get('underlying_price'))
        strike_price = float(data.get('strike_price'))
        time_to_expiry = float(data.get('time_to_expiry'))  # in years
        volatility = float(data.get('volatility', 0.25))
        risk_free_rate = float(data.get('risk_free_rate', 0.02))
        
        # Calculate option price
        price = derivatives_engine.calculate_option_price(
            option_type, underlying_price, strike_price, time_to_expiry, risk_free_rate, volatility
        )
        
        # Calculate Greeks
        greeks = derivatives_engine.calculate_option_greeks(
            option_type, underlying_price, strike_price, time_to_expiry, risk_free_rate, volatility
        )
        
        return jsonify({
            'success': True,
            'pricing': {
                'option_price': float(price),
                'greeks': greeks,
                'inputs': {
                    'option_type': option_type,
                    'underlying_price': underlying_price,
                    'strike_price': strike_price,
                    'time_to_expiry': time_to_expiry,
                    'volatility': volatility,
                    'risk_free_rate': risk_free_rate
                }
            }
        })
    except Exception as e:
        logger.error(f"Error calculating option price: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/derivatives/funding-rate/<contract_id>', methods=['GET'])
@jwt_required()
def get_funding_rate(contract_id):
    try:
        # Get current funding rate
        current_rate = derivatives_engine.calculate_funding_rate(contract_id)
        
        # Get historical funding rates
        rates = FundingRate.query.filter_by(contract_id=contract_id).order_by(
            FundingRate.period_end.desc()).limit(24).all()
        
        return jsonify({
            'success': True,
            'current_rate': current_rate,
            'historical_rates': [
                {
                    'rate': rate.rate,
                    'index_price': float(rate.index_price) if rate.index_price else None,
                    'mark_price': float(rate.mark_price) if rate.mark_price else None,
                    'period_start': rate.period_start.isoformat(),
                    'period_end': rate.period_end.isoformat()
                }
                for rate in rates
            ]
        })
    except Exception as e:
        logger.error(f"Error getting funding rate: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/derivatives/close-position/<position_id>', methods=['POST'])
@jwt_required()
def close_derivative_position(position_id):
    try:
        user_id = get_jwt_identity()
        
        position = DerivativePosition.query.filter_by(
            position_id=position_id, user_id=user_id, is_active=True
        ).first()
        
        if not position:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        # Create closing order
        closing_quantity = position.size
        closing_price = position.contract.mark_price or position.entry_price
        
        closing_order = DerivativeOrder(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            contract_id=position.contract_id,
            side=OrderSide.SHORT if position.side == OrderSide.LONG else OrderSide.LONG,
            order_type='market',
            quantity=closing_quantity,
            price=closing_price,
            leverage=position.leverage,
            status=OrderStatus.FILLED,
            executed_quantity=closing_quantity,
            executed_price=closing_price,
            average_price=closing_price,
            filled_at=datetime.utcnow()
        )
        
        db.session.add(closing_order)
        
        # Calculate realized P&L
        if position.side == OrderSide.LONG:
            realized_pnl = (closing_price - position.entry_price) * closing_quantity
        else:
            realized_pnl = (position.entry_price - closing_price) * closing_quantity
        
        # Update position
        position.realized_pnl = realized_pnl
        position.is_active = False
        
        # Create closing trade
        trade = DerivativeTrade(
            trade_id=str(uuid.uuid4()),
            order_id=closing_order.order_id,
            contract_id=position.contract_id,
            side=closing_order.side,
            quantity=closing_quantity,
            price=closing_price,
            notional_value=closing_quantity * closing_price,
            realized_pnl=realized_pnl
        )
        db.session.add(trade)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'closing_result': {
                'position_id': position_id,
                'realized_pnl': float(realized_pnl),
                'closing_price': float(closing_price),
                'closing_quantity': float(closing_quantity)
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error closing derivative position: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Derivatives Trading Service started successfully")
    app.run(host='0.0.0.0', port=5007, debug=True)