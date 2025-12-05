#!/usr/bin/env python3

"""
TigerEx Copy Trading Service
Category: social_trading
Description: Advanced copy trading system with performance tracking, risk management
Features: Auto-copy, portfolio management, leaderboards, risk controls, analytics
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
from typing import Dict, List, Optional, Any
from decimal import Decimal
from functools import wraps
from enum import Enum
import asyncio
import threading
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-copy-trading-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopyMode(Enum):
    FIXED_AMOUNT = "fixed_amount"  # Copy fixed USD amount per trade
    PERCENTAGE = "percentage"  # Copy percentage of trader's position
    RATIO = "ratio"  # Copy with fixed ratio (e.g., 0.1x)
    MIRROR = "mirror"  # Mirror exact position size

class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class CopyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class TradingStrategy(db.Model):
    __tablename__ = 'tiger_copy_trading_strategies'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Strategy details
    trading_style = db.Column(db.String(50))  # scalping, swing, position, day_trading
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.MODERATE)
    target_assets = db.Column(db.JSON)  # List of preferred symbols
    avoid_assets = db.Column(db.JSON)  # Symbols to avoid
    max_position_size = db.Column(db.Numeric(20, 8))  # Maximum position size
    max_daily_trades = db.Column(db.Integer, default=10)
    max_risk_per_trade = db.Column(db.Numeric(5, 4), default=Decimal('0.02'))  # 2% default
    
    # Performance metrics
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    total_pnl = db.Column(db.Numeric(20, 8), default=0)
    max_drawdown = db.Column(db.Numeric(10, 4), default=0)
    sharpe_ratio = db.Column(db.Numeric(10, 4), default=0)
    win_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Social features
    is_public = db.Column(db.Boolean, default=True)
    subscription_fee = db.Column(db.Numeric(20, 8), default=0)  # Monthly fee
    min_copy_amount = db.Column(db.Numeric(20, 8))
    max_copiers = db.Column(db.Integer)
    
    # Statistics
    followers_count = db.Column(db.Integer, default=0)
    total_copied_volume = db.Column(db.Numeric(20, 8), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trade_at = db.Column(db.DateTime)

class CopyRelationship(db.Model):
    __tablename__ = 'tiger_copy_relationships'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    copier_id = db.Column(db.String(50), nullable=False)
    strategy_id = db.Column(db.String(50), db.ForeignKey('tiger_copy_trading_strategies.id'), nullable=False)
    
    # Copy settings
    copy_mode = db.Column(db.Enum(CopyMode), nullable=False)
    copy_amount = db.Column(db.Numeric(20, 8))  # USD amount for fixed_amount mode
    copy_percentage = db.Column(db.Numeric(5, 4))  # Percentage for percentage mode
    copy_ratio = db.Column(db.Numeric(10, 6))  # Ratio for ratio mode
    
    # Risk controls
    max_daily_loss = db.Column(db.Numeric(20, 8))  # Stop copying if daily loss exceeds this
    max_total_loss = db.Column(db.Numeric(20, 8))  # Stop copying if total loss exceeds this
    min_account_balance = db.Column(db.Numeric(20, 8))  # Stop copying if balance falls below this
    reverse_trades = db.Column(db.Boolean, default=False)  # Copy opposite direction
    
    # Filters
    copy_only_symbols = db.Column(db.JSON)  # Only copy trades for these symbols
    exclude_symbols = db.Column(db.JSON)  # Exclude these symbols
    min_trade_size = db.Column(db.Numeric(20, 8))  # Minimum trade size to copy
    max_trade_size = db.Column(db.Numeric(20, 8))  # Maximum trade size to copy
    
    # Status and performance
    status = db.Column(db.Enum(CopyStatus), default=CopyStatus.ACTIVE)
    total_copied_trades = db.Column(db.Integer, default=0)
    total_copied_volume = db.Column(db.Numeric(20, 8), default=0)
    total_pnl = db.Column(db.Numeric(20, 8), default=0)
    total_fees_paid = db.Column(db.Numeric(20, 8), default=0)
    
    # Daily tracking
    daily_pnl = db.Column(db.Numeric(20, 8), default=0)
    daily_trades = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_copied_at = db.Column(db.DateTime)
    
    strategy = db.relationship('TradingStrategy', backref='copiers')

class CopiedTrade(db.Model):
    __tablename__ = 'tiger_copied_trades'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    copy_relationship_id = db.Column(db.String(50), db.ForeignKey('tiger_copy_relationships.id'), nullable=False)
    original_trade_id = db.Column(db.String(50), nullable=False)
    
    # Trade details
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    original_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    copied_quantity = db.Column(db.Numeric(20, 8), nullable=False)
    original_price = db.Column(db.Numeric(20, 8))
    copied_price = db.Column(db.Numeric(20, 8))
    
    # Execution details
    original_order_id = db.Column(db.String(100))
    copied_order_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, executed, failed, cancelled
    
    # Financial details
    original_value = db.Column(db.Numeric(20, 8))
    copied_value = db.Column(db.Numeric(20, 8))
    execution_fee = db.Column(db.Numeric(20, 8))
    copy_fee = db.Column(db.Numeric(20, 8))  # Fee charged for copying
    
    # Performance tracking
    entry_price = db.Column(db.Numeric(20, 8))
    exit_price = db.Column(db.Numeric(20, 8))
    pnl = db.Column(db.Numeric(20, 8))
    pnl_percentage = db.Column(db.Numeric(10, 4))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    
    copy_relationship = db.relationship('CopyRelationship', backref='copied_trades')

class PerformanceAnalytics(db.Model):
    __tablename__ = 'tiger_copy_performance_analytics'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    strategy_id = db.Column(db.String(50))  # For traders
    
    # Time period
    period = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Performance metrics
    total_trades = db.Column(db.Integer, default=0)
    winning_trades = db.Column(db.Integer, default=0)
    losing_trades = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Financial metrics
    total_pnl = db.Column(db.Numeric(20, 8), default=0)
    total_fees = db.Column(db.Numeric(20, 8), default=0)
    net_pnl = db.Column(db.Numeric(20, 8), default=0)
    max_drawdown = db.Column(db.Numeric(10, 4), default=0)
    sharpe_ratio = db.Column(db.Numeric(10, 4), default=0)
    
    # Volume metrics
    total_volume = db.Column(db.Numeric(20, 8), default=0)
    average_trade_size = db.Column(db.Numeric(20, 8), default=0)
    
    # Risk metrics
    largest_win = db.Column(db.Numeric(20, 8), default=0)
    largest_loss = db.Column(db.Numeric(20, 8), default=0)
    average_win = db.Column(db.Numeric(20, 8), default=0)
    average_loss = db.Column(db.Numeric(20, 8), default=0)
    
    # Copy trading specific (for copiers)
    strategies_copied = db.Column(db.Integer, default=0)
    successful_copies = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CopyTradingEngine:
    def __init__(self):
        self.active_copies = {}
        self.running = False
        
    def start_engine(self):
        """Start the copy trading engine"""
        self.running = True
        threading.Thread(target=self.engine_loop, daemon=True).start()
        logger.info("Copy trading engine started")
    
    def stop_engine(self):
        """Stop the copy trading engine"""
        self.running = False
        logger.info("Copy trading engine stopped")
    
    def engine_loop(self):
        """Main engine loop"""
        while self.running:
            try:
                # Process active copy relationships
                self.process_active_copies()
                
                # Update performance metrics
                self.update_performance_metrics()
                
                # Check risk limits
                self.check_risk_limits()
                
                time.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in copy trading engine loop: {e}")
                time.sleep(30)
    
    def process_active_copies(self):
        """Process all active copy relationships"""
        active_relationships = CopyRelationship.query.filter_by(status=CopyStatus.ACTIVE).all()
        
        for relationship in active_relationships:
            try:
                self.process_copy_relationship(relationship)
            except Exception as e:
                logger.error(f"Error processing copy relationship {relationship.id}: {e}")
    
    def process_copy_relationship(self, relationship: CopyRelationship):
        """Process a single copy relationship"""
        # Reset daily stats if needed
        if relationship.last_reset_date < datetime.utcnow().date():
            relationship.daily_pnl = 0
            relationship.daily_trades = 0
            relationship.last_reset_date = datetime.utcnow().date()
            db.session.commit()
        
        # Get strategy
        strategy = relationship.strategy
        if not strategy:
            return
        
        # Check for new trades from strategy
        new_trades = self.get_new_strategy_trades(strategy, relationship.last_copied_at)
        
        for trade in new_trades:
            if self.should_copy_trade(relationship, trade):
                copied_trade = self.copy_trade(relationship, trade)
                if copied_trade:
                    relationship.last_copied_at = datetime.utcnow()
                    db.session.commit()
    
    def should_copy_trade(self, relationship: CopyRelationship, trade: Dict) -> bool:
        """Check if a trade should be copied"""
        # Check symbol filters
        if relationship.copy_only_symbols and trade['symbol'] not in relationship.copy_only_symbols:
            return False
        
        if relationship.exclude_symbols and trade['symbol'] in relationship.exclude_symbols:
            return False
        
        # Check trade size limits
        trade_value = Decimal(str(trade['quantity'])) * Decimal(str(trade.get('price', 1)))
        
        if relationship.min_trade_size and trade_value < relationship.min_trade_size:
            return False
        
        if relationship.max_trade_size and trade_value > relationship.max_trade_size:
            return False
        
        # Check risk limits
        if relationship.daily_pnl < -relationship.max_daily_loss:
            return False
        
        if relationship.total_pnl < -relationship.max_total_loss:
            return False
        
        return True
    
    def copy_trade(self, relationship: CopyRelationship, trade: Dict) -> Optional[CopiedTrade]:
        """Copy a trade"""
        try:
            # Calculate copied quantity based on copy mode
            copied_quantity = self.calculate_copy_quantity(relationship, trade)
            
            if copied_quantity <= 0:
                return None
            
            # Apply reverse trade if enabled
            copied_side = trade['side']
            if relationship.reverse_trades:
                copied_side = 'sell' if trade['side'] == 'buy' else 'buy'
            
            # Create copied trade record
            copied_trade = CopiedTrade(
                copy_relationship_id=relationship.id,
                original_trade_id=trade['trade_id'],
                symbol=trade['symbol'],
                side=copied_side,
                original_quantity=trade['quantity'],
                copied_quantity=copied_quantity,
                original_price=trade.get('price'),
                copied_price=trade.get('price'),
                original_value=Decimal(str(trade['quantity'])) * Decimal(str(trade.get('price', 1))),
                copied_value=copied_quantity * Decimal(str(trade.get('price', 1))),
                status='executed',
                executed_at=datetime.utcnow(),
                entry_price=trade.get('price')
            )
            
            db.session.add(copied_trade)
            
            # Update relationship stats
            relationship.total_copied_trades += 1
            relationship.total_copied_volume += copied_trade.copied_value
            relationship.daily_trades += 1
            relationship.last_copied_at = datetime.utcnow()
            
            # Here you would integrate with your trading engine
            # to actually place the copied order
            # For now, we'll simulate successful execution
            
            db.session.commit()
            
            logger.info(f"Copied trade {trade['trade_id']} for relationship {relationship.id}")
            return copied_trade
            
        except Exception as e:
            logger.error(f"Error copying trade: {e}")
            db.session.rollback()
            return None
    
    def calculate_copy_quantity(self, relationship: CopyRelationship, trade: Dict) -> Decimal:
        """Calculate the quantity to copy based on copy mode"""
        trade_price = Decimal(str(trade.get('price', 1)))
        
        if relationship.copy_mode == CopyMode.FIXED_AMOUNT:
            # Copy fixed USD amount
            return relationship.copy_amount / trade_price
        
        elif relationship.copy_mode == CopyMode.PERCENTAGE:
            # Copy percentage of original trade
            return Decimal(str(trade['quantity'])) * relationship.copy_percentage
        
        elif relationship.copy_mode == CopyMode.RATIO:
            # Copy with fixed ratio
            return Decimal(str(trade['quantity'])) * relationship.copy_ratio
        
        elif relationship.copy_mode == CopyMode.MIRROR:
            # Mirror exact position
            return Decimal(str(trade['quantity']))
        
        return Decimal('0')
    
    def get_new_strategy_trades(self, strategy: TradingStrategy, since: Optional[datetime]) -> List[Dict]:
        """Get new trades from a strategy since a given time"""
        # This would integrate with your trading system
        # For now, return empty list
        return []
    
    def update_performance_metrics(self):
        """Update performance metrics for all users and strategies"""
        try:
            # Update strategy performance
            strategies = TradingStrategy.query.all()
            for strategy in strategies:
                self.update_strategy_performance(strategy)
            
            # Update copier performance
            copiers = CopyRelationship.query.all()
            for copier in copiers:
                self.update_copier_performance(copier)
                
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def update_strategy_performance(self, strategy: TradingStrategy):
        """Update strategy performance metrics"""
        # Get all copied trades for this strategy
        trades = db.session.query(CopiedTrade).join(CopyRelationship).filter(
            CopyRelationship.strategy_id == strategy.id,
            CopiedTrade.status == 'executed'
        ).all()
        
        if not trades:
            return
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl and t.pnl > 0])
        total_pnl = sum([t.pnl or 0 for t in trades])
        
        strategy.total_trades = total_trades
        strategy.winning_trades = winning_trades
        strategy.total_pnl = total_pnl
        strategy.win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Update last trade time
        executed_trades = [t for t in trades if t.executed_at]
        if executed_trades:
            strategy.last_trade_at = max([t.executed_at for t in executed_trades])
        
        db.session.commit()
    
    def update_copier_performance(self, relationship: CopyRelationship):
        """Update copier performance metrics"""
        trades = CopiedTrade.query.filter_by(
            copy_relationship_id=relationship.id,
            status='executed'
        ).all()
        
        if not trades:
            return
        
        # Calculate metrics
        total_pnl = sum([t.pnl or 0 for t in trades])
        total_fees = sum([t.copy_fee or 0 for t in trades])
        
        relationship.total_copied_trades = len(trades)
        relationship.total_pnl = total_pnl
        relationship.total_fees_paid = total_fees
        
        db.session.commit()
    
    def check_risk_limits(self):
        """Check and enforce risk limits"""
        try:
            relationships = CopyRelationship.query.filter_by(status=CopyStatus.ACTIVE).all()
            
            for relationship in relationships:
                # Check daily loss limit
                if relationship.daily_pnl < -relationship.max_daily_loss:
                    relationship.status = CopyStatus.PAUSED
                    logger.warning(f"Paused copy relationship {relationship.id} due to daily loss limit")
                
                # Check total loss limit
                if relationship.total_pnl < -relationship.max_total_loss:
                    relationship.status = CopyStatus.PAUSED
                    logger.warning(f"Paused copy relationship {relationship.id} due to total loss limit")
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")

# Initialize the copy trading engine
copy_engine = CopyTradingEngine()

# API Routes
@app.route('/api/v1/copy-trading/strategies', methods=['POST'])
@jwt_required()
def create_strategy():
    """Create a new trading strategy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        strategy = TradingStrategy(
            trader_id=user_id,
            name=data['name'],
            description=data.get('description'),
            trading_style=data.get('trading_style'),
            risk_level=RiskLevel(data.get('risk_level', 'moderate')),
            target_assets=data.get('target_assets', []),
            avoid_assets=data.get('avoid_assets', []),
            max_position_size=data.get('max_position_size'),
            max_daily_trades=data.get('max_daily_trades', 10),
            max_risk_per_trade=Decimal(str(data.get('max_risk_per_trade', '0.02'))),
            is_public=data.get('is_public', True),
            subscription_fee=Decimal(str(data.get('subscription_fee', '0'))),
            min_copy_amount=data.get('min_copy_amount'),
            max_copiers=data.get('max_copiers')
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'strategy_id': strategy.id,
            'name': strategy.name
        })
        
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/copy-trading/strategies', methods=['GET'])
@jwt_required()
def list_strategies():
    """List available trading strategies"""
    try:
        # Query parameters
        trader_id = request.args.get('trader_id')
        risk_level = request.args.get('risk_level')
        trading_style = request.args.get('trading_style')
        featured = request.args.get('featured', '').lower() == 'true'
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'followers_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = TradingStrategy.query.filter_by(is_public=True)
        
        if trader_id:
            query = query.filter_by(trader_id=trader_id)
        
        if risk_level:
            query = query.filter_by(risk_level=RiskLevel(risk_level))
        
        if trading_style:
            query = query.filter_by(trading_style=trading_style)
        
        if featured:
            query = query.filter(TradingStrategy.followers_count >= 100)
        
        # Apply sorting
        if hasattr(TradingStrategy, sort_by):
            order_column = getattr(TradingStrategy, sort_by)
        else:
            order_column = TradingStrategy.followers_count
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # Paginate
        strategies = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'strategies': [{
                'id': strategy.id,
                'trader_id': strategy.trader_id,
                'name': strategy.name,
                'description': strategy.description,
                'trading_style': strategy.trading_style,
                'risk_level': strategy.risk_level.value,
                'total_trades': strategy.total_trades,
                'winning_trades': strategy.winning_trades,
                'total_pnl': str(strategy.total_pnl),
                'win_rate': str(strategy.win_rate),
                'max_drawdown': str(strategy.max_drawdown),
                'sharpe_ratio': str(strategy.sharpe_ratio),
                'followers_count': strategy.followers_count,
                'total_copied_volume': str(strategy.total_copied_volume),
                'subscription_fee': str(strategy.subscription_fee),
                'min_copy_amount': str(strategy.min_copy_amount) if strategy.min_copy_amount else None,
                'max_copiers': strategy.max_copiers,
                'created_at': strategy.created_at.isoformat(),
                'last_trade_at': strategy.last_trade_at.isoformat() if strategy.last_trade_at else None
            } for strategy in strategies.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': strategies.total,
                'pages': strategies.pages
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/copy-trading/copy', methods=['POST'])
@jwt_required()
def start_copying():
    """Start copying a strategy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate strategy exists
        strategy = TradingStrategy.query.get(data['strategy_id'])
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        # Check if already copying this strategy
        existing = CopyRelationship.query.filter_by(
            copier_id=user_id,
            strategy_id=data['strategy_id']
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Already copying this strategy'}), 400
        
        # Create copy relationship
        copy_relationship = CopyRelationship(
            copier_id=user_id,
            strategy_id=data['strategy_id'],
            copy_mode=CopyMode(data['copy_mode']),
            copy_amount=Decimal(str(data.get('copy_amount', '100'))),
            copy_percentage=Decimal(str(data.get('copy_percentage', '0.1'))),
            copy_ratio=Decimal(str(data.get('copy_ratio', '0.1'))),
            max_daily_loss=Decimal(str(data.get('max_daily_loss', '1000'))),
            max_total_loss=Decimal(str(data.get('max_total_loss', '5000'))),
            min_account_balance=Decimal(str(data.get('min_account_balance', '100'))),
            reverse_trades=data.get('reverse_trades', False),
            copy_only_symbols=data.get('copy_only_symbols', []),
            exclude_symbols=data.get('exclude_symbols', []),
            min_trade_size=data.get('min_trade_size'),
            max_trade_size=data.get('max_trade_size')
        )
        
        db.session.add(copy_relationship)
        
        # Update strategy followers count
        strategy.followers_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'copy_relationship_id': copy_relationship.id,
            'status': copy_relationship.status.value
        })
        
    except Exception as e:
        logger.error(f"Error starting copy: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'copy-trading-service',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Start the copy trading engine
    copy_engine.start_engine()
    
    port = int(os.getenv('PORT', 8002))
    app.run(host='0.0.0.0', port=port, debug=True)