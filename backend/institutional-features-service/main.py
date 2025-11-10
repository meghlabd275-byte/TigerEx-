#!/usr/bin/env python3
"""
Institutional Features Service for TigerEx v11.0.0
Advanced institutional trading tools and features
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
from decimal import Decimal
from enum import Enum
import pandas as pd

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
class InstitutionType(str, Enum):
    HEDGE_FUND = "hedge_fund"
    PROPRIETARY_TRADING = "proprietary_trading"
    ASSET_MANAGER = "asset_manager"
    FAMILY_OFFICE = "family_office"
    BANK = "bank"
    BROKER_DEALER = "broker_dealer"
    VENTURE_CAPITAL = "venture_capital"
    PRIVATE_EQUITY = "private_equity"

class OTCStatus(str, Enum):
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    SETTLED = "settled"

class AlgoStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

# Models
class Institution(db.Model):
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    institution_type = db.Column(db.Enum(InstitutionType), nullable=False)
    
    # Business information
    registration_number = db.Column(db.String(100))
    regulatory_authority = db.Column(db.String(100))
    assets_under_management = db.Column(db.Numeric(30, 8))
    establishment_date = db.Column(db.DateTime)
    
    # Contact information
    primary_contact_name = db.Column(db.String(100))
    primary_contact_email = db.Column(db.String(100))
    primary_contact_phone = db.Column(db.String(20))
    
    # Trading permissions
    trading_permissions = db.Column(db.JSON)
    max_daily_volume = db.Column(db.Numeric(30, 8))
    max_single_trade = db.Column(db.Numeric(30, 8))
    allowed_products = db.Column(db.JSON)
    
    # Compliance settings
    compliance_level = db.Column(db.String(20), default='standard')
    audit_required = db.Column(db.Boolean, default=True)
    reporting_frequency = db.Column(db.String(20), default='daily')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    credit_rating = db.Column(db.String(10))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InstitutionalUser(db.Model):
    __tablename__ = 'institutional_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    institution_id = db.Column(db.String(64), db.ForeignKey('institutions.institution_id'), nullable=False)
    
    # User details
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))  # trader, analyst, manager, compliance officer
    
    # Permissions
    trading_permissions = db.Column(db.JSON)
    api_access = db.Column(db.Boolean, default=False)
    api_rate_limit = db.Column(db.Integer, default=1000)
    
    # Trading limits
    max_position_size = db.Column(db.Numeric(30, 8))
    max_daily_trades = db.Column(db.Integer)
    max_leverage = db.Column(db.Integer, default=10)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    institution = db.relationship('Institution', backref=db.backref('users', lazy=True))

class OTCRequest(db.Model):
    __tablename__ = 'otc_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(64), nullable=False, unique=True)
    institution_id = db.Column(db.String(64), db.ForeignKey('institutions.institution_id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    
    # Request details
    product_type = db.Column(db.String(50), nullable=False)  # block_trade, custom_derivative, structured_product
    underlying_asset = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # BUY, SELL
    quantity = db.Column(db.Numeric(30, 8), nullable=False)
    target_price = db.Column(db.Numeric(20, 8))
    
    # Customization for structured products
    product_specifications = db.Column(db.JSON)
    settlement_terms = db.Column(db.JSON)
    
    # Negotiation
    best_bid = db.Column(db.Numeric(20, 8))
    best_ask = db.Column(db.Numeric(20, 8))
    counterparty_id = db.Column(db.String(64))
    
    # Status and timing
    status = db.Column(db.Enum(OTCStatus), default=OTCStatus.PENDING)
    expires_at = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    settled_at = db.Column(db.DateTime)
    
    # Notes and communications
    internal_notes = db.Column(db.Text)
    communication_history = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    institution = db.relationship('Institution', backref=db.backref('otc_requests', lazy=True))

class AlgorithmicStrategy(db.Model):
    __tablename__ = 'algorithmic_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.String(64), nullable=False, unique=True)
    institution_id = db.Column(db.String(64), db.ForeignKey('institutions.institution_id'), nullable=False)
    creator_user_id = db.Column(db.String(50), nullable=False)
    
    # Strategy details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategy_type = db.Column(db.String(50))  # market_making, arbitrage, statistical, trend_following
    
    # Configuration
    trading_pairs = db.Column(db.JSON)
    parameters = db.Column(db.JSON)
    risk_parameters = db.Column(db.JSON)
    
    # Performance metrics
    total_return = db.Column(db.Float, default=0)
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    win_rate = db.Column(db.Float)
    
    # Execution settings
    max_position_size = db.Column(db.Numeric(30, 8))
    daily_loss_limit = db.Column(db.Numeric(30, 8))
    execution_mode = db.Column(db.String(20), default='paper')  # paper, live
    
    # Status
    status = db.Column(db.Enum(AlgoStatus), default=AlgoStatus.PAUSED)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_execution = db.Column(db.DateTime)
    backtest_period_start = db.Column(db.DateTime)
    backtest_period_end = db.Column(db.DateTime)
    
    # Relationship
    institution = db.relationship('Institution', backref=db.backref('strategies', lazy=True))

class HighFrequencyTrade(db.Model):
    __tablename__ = 'high_frequency_trades'
    
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(64), nullable=False, unique=True)
    institution_id = db.Column(db.String(64), db.ForeignKey('institutions.institution_id'), nullable=False)
    strategy_id = db.Column(db.String(64), db.ForeignKey('algorithmic_strategies.strategy_id'))
    
    # Trade details
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Numeric(30, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    execution_time = db.Column(db.DateTime, nullable=False)
    
    # Latency metrics
    order_to_execution_ms = db.Column(db.Integer)
    latency_percentile = db.Column(db.String(10))
    
    # Market impact
    slippage_bps = db.Column(db.Float)  # basis points
    market_impact = db.Column(db.Float)
    
    # Strategy attribution
    alpha_generated = db.Column(db.Numeric(20, 8))
    cost_analysis = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = db.relationship('Institution', backref=db.backref('hf_trades', lazy=True))
    strategy = db.relationship('AlgorithmicStrategy', backref=db.backref('trades', lazy=True))

class MarketMakerInventory(db.Model):
    __tablename__ = 'market_maker_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.String(64), db.ForeignKey('institutions.institution_id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    
    # Inventory position
    net_position = db.Column(db.Numeric(30, 8), default=0)
    long_positions = db.Column(db.Numeric(30, 8), default=0)
    short_positions = db.Column(db.Numeric(30, 8), default=0)
    
    # Pricing
    bid_price = db.Column(db.Numeric(20, 8))
    ask_price = db.Column(db.Numeric(20, 8))
    bid_size = db.Column(db.Numeric(30, 8))
    ask_size = db.Column(db.Numeric(30, 8))
    
    # Risk metrics
    inventory_pnl = db.Column(db.Numeric(30, 8), default=0)
    max_position_limit = db.Column(db.Numeric(30, 8))
    inventory_utilization = db.Column(db.Float)
    
    # Quotes analytics
    total_quotes = db.Column(db.Integer, default=0)
    executed_trades = db.Column(db.Integer, default=0)
    quote_execution_ratio = db.Column(db.Float)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    institution = db.relationship('Institution', backref=db.backref('mm_inventory', lazy=True))

class InstitutionalFeaturesEngine:
    def __init__(self):
        self.default_permissions = {
            'hedge_fund': ['spot_trading', 'derivatives', 'short_selling', 'leverage', 'otc_trading'],
            'proprietary_trading': ['spot_trading', 'derivatives', 'short_selling', 'leverage', 'market_making', 'hft'],
            'asset_manager': ['spot_trading', 'derivatives', 'portfolio_management', 'reporting'],
            'family_office': ['spot_trading', 'derivatives', 'wealth_management', 'tax_optimization'],
            'bank': ['spot_trading', 'derivatives', 'custody', 'market_making', 'liquidity_provision'],
            'broker_dealer': ['spot_trading', 'derivatives', 'market_making', 'client_execution', 'otc_trading'],
            'venture_capital': ['spot_trading', 'private_deals', 'tokenization'],
            'private_equity': ['spot_trading', 'private_deals', 'structured_products']
        }
    
    def register_institution(self, institution_data):
        """Register a new institutional client"""
        try:
            institution = Institution(
                institution_id=str(uuid.uuid4()),
                name=institution_data.get('name'),
                institution_type=InstitutionType(institution_data.get('type')),
                registration_number=institution_data.get('registration_number'),
                regulatory_authority=institution_data.get('regulatory_authority'),
                assets_under_management=Decimal(str(institution_data.get('assets_under_management', 0))),
                establishment_date=datetime.strptime(institution_data.get('establishment_date'), '%Y-%m-%d') if institution_data.get('establishment_date') else None,
                primary_contact_name=institution_data.get('primary_contact_name'),
                primary_contact_email=institution_data.get('primary_contact_email'),
                primary_contact_phone=institution_data.get('primary_contact_phone'),
                trading_permissions=self.default_permissions.get(institution_data.get('type'), []),
                max_daily_volume=Decimal(str(institution_data.get('max_daily_volume', 1000000))),
                max_single_trade=Decimal(str(institution_data.get('max_single_trade', 100000))),
                allowed_products=institution_data.get('allowed_products', ['spot', 'futures', 'options']),
                compliance_level=institution_data.get('compliance_level', 'standard')
            )
            
            db.session.add(institution)
            db.session.commit()
            
            return institution
        except Exception as e:
            db.session.rollback()
            raise e
    
    def create_otc_request(self, institution_id, user_id, request_data):
        """Create a new OTC trading request"""
        try:
            request = OTCRequest(
                request_id=str(uuid.uuid4()),
                institution_id=institution_id,
                user_id=user_id,
                product_type=request_data.get('product_type'),
                underlying_asset=request_data.get('underlying_asset'),
                side=request_data.get('side'),
                quantity=Decimal(str(request_data.get('quantity'))),
                target_price=Decimal(str(request_data.get('target_price'))) if request_data.get('target_price') else None,
                product_specifications=request_data.get('product_specifications'),
                settlement_terms=request_data.get('settlement_terms'),
                expires_at=datetime.utcnow() + timedelta(hours=request_data.get('validity_hours', 24)),
                internal_notes=request_data.get('internal_notes')
            )
            
            db.session.add(request)
            db.session.commit()
            
            # Trigger internal matching process
            self.match_otc_request(request.request_id)
            
            return request
        except Exception as e:
            db.session.rollback()
            raise e
    
    def match_otc_request(self, request_id):
        """Match OTC request with available liquidity"""
        request = OTCRequest.query.filter_by(request_id=request_id).first()
        if not request:
            return None
        
        # Simplified matching logic - in practice, this would query internal liquidity desks
        # For demo, simulate finding a counterparty
        if request.product_type in ['block_trade', 'custom_derivative']:
            # Simulate price improvement
            if request.target_price:
                improvement_pct = 0.001  # 0.1% improvement
                if request.side == 'BUY':
                    request.best_ask = request.target_price * (1 - improvement_pct)
                else:
                    request.best_bid = request.target_price * (1 + improvement_pct)
                
                request.status = OTCStatus.NEGOTIATING
                db.session.commit()
        
        return request
    
    def deploy_algorithmic_strategy(self, institution_id, user_id, strategy_data):
        """Deploy a new algorithmic trading strategy"""
        try:
            strategy = AlgorithmicStrategy(
                strategy_id=str(uuid.uuid4()),
                institution_id=institution_id,
                creator_user_id=user_id,
                name=strategy_data.get('name'),
                description=strategy_data.get('description'),
                strategy_type=strategy_data.get('strategy_type'),
                trading_pairs=strategy_data.get('trading_pairs', []),
                parameters=strategy_data.get('parameters', {}),
                risk_parameters=strategy_data.get('risk_parameters', {}),
                max_position_size=Decimal(str(strategy_data.get('max_position_size', 1000000))),
                daily_loss_limit=Decimal(str(strategy_data.get('daily_loss_limit', 100000))),
                execution_mode=strategy_data.get('execution_mode', 'paper'),
                backtest_period_start=datetime.strptime(strategy_data.get('backtest_start'), '%Y-%m-%d') if strategy_data.get('backtest_start') else None,
                backtest_period_end=datetime.strptime(strategy_data.get('backtest_end'), '%Y-%m-%d') if strategy_data.get('backtest_end') else None
            )
            
            db.session.add(strategy)
            db.session.commit()
            
            # Run backtest if requested
            if strategy_data.get('run_backtest', False):
                self.run_strategy_backtest(strategy.strategy_id)
            
            return strategy
        except Exception as e:
            db.session.rollback()
            raise e
    
    def run_strategy_backtest(self, strategy_id):
        """Run backtest for algorithmic strategy"""
        strategy = AlgorithmicStrategy.query.filter_by(strategy_id=strategy_id).first()
        if not strategy:
            return None
        
        # Simplified backtest - in practice, would use historical market data
        backtest_results = {
            'total_return': np.random.uniform(-0.2, 0.5),
            'sharpe_ratio': np.random.uniform(0.5, 2.5),
            'max_drawdown': np.random.uniform(-0.3, -0.05),
            'win_rate': np.random.uniform(0.4, 0.7)
        }
        
        strategy.total_return = backtest_results['total_return']
        strategy.sharpe_ratio = backtest_results['sharpe_ratio']
        strategy.max_drawdown = backtest_results['max_drawdown']
        strategy.win_rate = backtest_results['win_rate']
        
        db.session.commit()
        
        return backtest_results
    
    def generate_institutional_report(self, institution_id, report_type, period):
        """Generate institutional compliance and performance reports"""
        institution = Institution.query.filter_by(institution_id=institution_id).first()
        if not institution:
            return None
        
        # Calculate period date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period)
        
        if report_type == 'trading_activity':
            # Get trading activity data
            trades = HighFrequencyTrade.query.filter(
                HighFrequencyTrade.institution_id == institution_id,
                HighFrequencyTrade.created_at >= start_date
            ).all()
            
            total_volume = sum(float(trade.quantity) * float(trade.price) for trade in trades)
            total_trades = len(trades)
            avg_execution_time = sum(trade.order_to_execution_ms or 0 for trade in trades) / total_trades if trades else 0
            
            report = {
                'institution_id': institution_id,
                'report_type': report_type,
                'period_days': period,
                'generated_at': datetime.utcnow().isoformat(),
                'metrics': {
                    'total_volume': total_volume,
                    'total_trades': total_trades,
                    'avg_execution_time_ms': avg_execution_time,
                    'trading_pairs': list(set(trade.symbol for trade in trades))
                }
            }
            
        elif report_type == 'risk_exposure':
            # Calculate risk exposure
            positions = MarketMakerInventory.query.filter_by(institution_id=institution_id).all()
            total_exposure = sum(float(position.net_position) for position in positions)
            
            report = {
                'institution_id': institution_id,
                'report_type': report_type,
                'period_days': period,
                'generated_at': datetime.utcnow().isoformat(),
                'metrics': {
                    'total_exposure': total_exposure,
                    'position_count': len(positions),
                    'positions_by_symbol': {pos.symbol: float(pos.net_position) for pos in positions}
                }
            }
        
        else:
            report = {'error': 'Unsupported report type'}
        
        return report
    
    def calculate_market_metrics(self, institution_id):
        """Calculate market maker metrics for institutional client"""
        inventory = MarketMakerInventory.query.filter_by(institution_id=institution_id).all()
        
        if not inventory:
            return {}
        
        total_inventory_pnl = sum(float(inv.inventory_pnl) for inv in inventory)
        total_quotes = sum(inv.total_quotes for inv in inventory)
        total_executions = sum(inv.executed_trades for inv in inventory)
        overall_execution_ratio = total_executions / total_quotes if total_quotes > 0 else 0
        
        return {
            'total_inventory_pnl': total_inventory_pnl,
            'total_quotes': total_quotes,
            'total_executions': total_executions,
            'execution_ratio': overall_execution_ratio,
            'active_symbols': [inv.symbol for inv in inventory if inv.net_position != 0]
        }

# Initialize institutional features engine
institutional_engine = InstitutionalFeaturesEngine()

# API Routes
@app.route('/api/institutional/register', methods=['POST'])
@jwt_required()
def register_institution():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        institution = institutional_engine.register_institution(data)
        
        # Add registering user as primary contact
        user = InstitutionalUser(
            user_id=user_id,
            institution_id=institution.institution_id,
            email=data.get('primary_contact_email'),
            name=data.get('primary_contact_name'),
            role='manager',
            trading_permissions=institution.trading_permissions,
            api_access=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'institution': {
                'institution_id': institution.institution_id,
                'name': institution.name,
                'type': institution.institution_type,
                'trading_permissions': institution.trading_permissions,
                'is_verified': institution.is_verified
            }
        })
    except Exception as e:
        logger.error(f"Error registering institution: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/institutional/otc/request', methods=['POST'])
@jwt_required()
def create_otc_request():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify user has OTC permissions
        user = InstitutionalUser.query.filter_by(user_id=user_id).first()
        if not user or 'otc_trading' not in user.trading_permissions:
            return jsonify({'success': False, 'error': 'OTC trading not permitted'}), 403
        
        request = institutional_engine.create_otc_request(user.institution_id, user_id, data)
        
        return jsonify({
            'success': True,
            'otc_request': {
                'request_id': request.request_id,
                'product_type': request.product_type,
                'underlying_asset': request.underlying_asset,
                'side': request.side,
                'quantity': float(request.quantity),
                'status': request.status,
                'expires_at': request.expires_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error creating OTC request: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/institutional/algorithms/deploy', methods=['POST'])
@jwt_required()
def deploy_algorithmic_strategy():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify user permissions
        user = InstitutionalUser.query.filter_by(user_id=user_id).first()
        if not user or 'algorithmic_trading' not in (user.trading_permissions or []):
            return jsonify({'success': False, 'error': 'Algorithmic trading not permitted'}), 403
        
        strategy = institutional_engine.deploy_algorithmic_strategy(user.institution_id, user_id, data)
        
        return jsonify({
            'success': True,
            'strategy': {
                'strategy_id': strategy.strategy_id,
                'name': strategy.name,
                'strategy_type': strategy.strategy_type,
                'status': strategy.status,
                'execution_mode': strategy.execution_mode
            }
        })
    except Exception as e:
        logger.error(f"Error deploying algorithmic strategy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/institutional/report/<report_type>', methods=['GET'])
@jwt_required()
def generate_institutional_report(report_type):
    try:
        user_id = get_jwt_identity()
        period = request.args.get('period', 30, type=int)
        
        user = InstitutionalUser.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'Institutional user not found'}), 404
        
        report = institutional_engine.generate_institutional_report(user.institution_id, report_type, period)
        
        if not report or 'error' in report:
            return jsonify({'success': False, 'error': 'Report generation failed'}), 500
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        logger.error(f"Error generating institutional report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/institutional/market-metrics', methods=['GET'])
@jwt_required()
def get_market_metrics():
    try:
        user_id = get_jwt_identity()
        
        user = InstitutionalUser.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'Institutional user not found'}), 404
        
        metrics = institutional_engine.calculate_market_metrics(user.institution_id)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting market metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/institutional/high-frequency/execute', methods=['POST'])
@jwt_required()
def execute_high_frequency_trade():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify HFT permissions
        user = InstitutionalUser.query.filter_by(user_id=user_id).first()
        if not user or 'hft' not in (user.trading_permissions or []):
            return jsonify({'success': False, 'error': 'High-frequency trading not permitted'}), 403
        
        # Create HFT trade record
        trade = HighFrequencyTrade(
            trade_id=str(uuid.uuid4()),
            institution_id=user.institution_id,
            strategy_id=data.get('strategy_id'),
            symbol=data.get('symbol'),
            side=data.get('side'),
            quantity=Decimal(str(data.get('quantity'))),
            price=Decimal(str(data.get('price'))),
            execution_time=datetime.utcnow(),
            order_to_execution_ms=data.get('latency_ms'),
            slippage_bps=data.get('slippage_bps'),
            alpha_generated=Decimal(str(data.get('alpha', 0)))
        )
        
        db.session.add(trade)
        
        # Update market maker inventory if applicable
        if user.institution.institution_type == InstitutionType.BROKER_DEALER:
            inventory = MarketMakerInventory.query.filter_by(
                institution_id=user.institution_id, symbol=data.get('symbol')
            ).first()
            
            if inventory:
                if data.get('side') == 'BUY':
                    inventory.net_position += trade.quantity
                    inventory.long_positions += trade.quantity
                else:
                    inventory.net_position -= trade.quantity
                    inventory.short_positions += trade.quantity
                
                inventory.inventory_pnl += trade.alpha_generated or 0
                inventory.total_quotes += 1
                inventory.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'trade': {
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': float(trade.quantity),
                'price': float(trade.price),
                'execution_time': trade.execution_time.isoformat(),
                'latency_ms': trade.order_to_execution_ms
            }
        })
    except Exception as e:
        logger.error(f"Error executing HFT trade: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Institutional Features Service started successfully")
    app.run(host='0.0.0.0', port=5008, debug=True)