#!/usr/bin/env python3

"""
Tiger Wealth Service
Category: wealth_management
Description: Comprehensive wealth management and investment platform for TigerEx
Features: Portfolio management, wealth tracking, investment strategies, automated investing
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-wealth-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    __tablename__ = 'tiger_wealth_users'
    
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    wealth_tier = db.Column(db.String(20), default='standard')  # standard, premium, elite, institutional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WealthPortfolio(db.Model):
    __tablename__ = 'tiger_wealth_portfolios'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tiger_wealth_users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    portfolio_type = db.Column(db.String(50), default='balanced')  # conservative, balanced, aggressive, custom
    total_value = db.Column(db.Numeric(20, 8), default=0)
    risk_level = db.Column(db.Integer, default=5)  # 1-10 scale
    target_return = db.Column(db.Numeric(10, 4))  # Annual target return %
    asset_allocation = db.Column(db.JSON)  # Asset allocation percentages
    performance_data = db.Column(db.JSON)  # Historical performance
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='portfolios')

class WealthAsset(db.Model):
    __tablename__ = 'tiger_wealth_assets'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = db.Column(db.String(50), db.ForeignKey('tiger_wealth_portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)  # crypto, stock, etf, bond, commodity
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    average_buy_price = db.Column(db.Numeric(20, 8), nullable=False)
    current_price = db.Column(db.Numeric(20, 8))
    current_value = db.Column(db.Numeric(20, 8))
    unrealized_pnl = db.Column(db.Numeric(20, 8))
    unrealized_pnl_percent = db.Column(db.Numeric(10, 4))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    portfolio = db.relationship('WealthPortfolio', backref='assets')

class InvestmentStrategy(db.Model):
    __tablename__ = 'tiger_investment_strategies'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategy_type = db.Column(db.String(50), nullable=False)  # dollar_cost_averaging, value_investing, growth, dividend
    risk_level = db.Column(db.Integer, nullable=False)
    min_investment = db.Column(db.Numeric(20, 8), nullable=False)
    expected_return = db.Column(db.Numeric(10, 4))
    asset_allocation = db.Column(db.JSON)
    rules = db.Column(db.JSON)  # Strategy rules and parameters
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(50), db.ForeignKey('tiger_wealth_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', backref='strategies')

class AutoInvestPlan(db.Model):
    __tablename__ = 'tiger_auto_invest_plans'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tiger_wealth_users.id'), nullable=False)
    portfolio_id = db.Column(db.String(50), db.ForeignKey('tiger_wealth_portfolios.id'), nullable=False)
    strategy_id = db.Column(db.String(50), db.ForeignKey('tiger_investment_strategies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    investment_amount = db.Column(db.Numeric(20, 8), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, quarterly
    next_execution = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    total_invested = db.Column(db.Numeric(20, 8), default=0)
    execution_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='auto_invest_plans')
    portfolio = db.relationship('WealthPortfolio', backref='auto_invest_plans')
    strategy = db.relationship('InvestmentStrategy', backref='auto_invest_plans')

# User Routes
@app.route('/api/tiger-wealth/portfolios', methods=['GET'])
@jwt_required()
def get_portfolios():
    try:
        user_id = get_jwt_identity()
        portfolios = WealthPortfolio.query.filter_by(user_id=user_id, is_active=True).all()
        
        portfolio_data = []
        for portfolio in portfolios:
            assets = WealthAsset.query.filter_by(portfolio_id=portfolio.id).all()
            total_value = sum(asset.current_value or 0 for asset in assets)
            
            portfolio_data.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'portfolio_type': portfolio.portfolio_type,
                'total_value': float(total_value),
                'risk_level': portfolio.risk_level,
                'target_return': float(portfolio.target_return) if portfolio.target_return else None,
                'asset_allocation': portfolio.asset_allocation,
                'asset_count': len(assets),
                'created_at': portfolio.created_at.isoformat(),
                'updated_at': portfolio.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'portfolios': portfolio_data,
            'total_portfolio_value': sum(p['total_value'] for p in portfolio_data)
        })
    except Exception as e:
        logger.error(f"Error getting portfolios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/portfolios', methods=['POST'])
@jwt_required()
def create_portfolio():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        portfolio = WealthPortfolio(
            user_id=user_id,
            name=data['name'],
            portfolio_type=data.get('portfolio_type', 'balanced'),
            risk_level=data.get('risk_level', 5),
            target_return=data.get('target_return'),
            asset_allocation=data.get('asset_allocation', {})
        )
        
        db.session.add(portfolio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio created successfully',
            'portfolio_id': portfolio.id
        })
    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/portfolios/<portfolio_id>/assets', methods=['GET'])
@jwt_required()
def get_portfolio_assets(portfolio_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify portfolio ownership
        portfolio = WealthPortfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        assets = WealthAsset.query.filter_by(portfolio_id=portfolio_id).all()
        
        assets_data = []
        for asset in assets:
            unrealized_pnl = (asset.current_price - asset.average_buy_price) * asset.quantity if asset.current_price else 0
            unrealized_pnl_percent = ((asset.current_price / asset.average_buy_price - 1) * 100) if asset.current_price and asset.average_buy_price != 0 else 0
            
            assets_data.append({
                'id': asset.id,
                'symbol': asset.symbol,
                'asset_type': asset.asset_type,
                'quantity': float(asset.quantity),
                'average_buy_price': float(asset.average_buy_price),
                'current_price': float(asset.current_price) if asset.current_price else None,
                'current_value': float(asset.current_value) if asset.current_value else None,
                'unrealized_pnl': float(unrealized_pnl),
                'unrealized_pnl_percent': float(unrealized_pnl_percent),
                'created_at': asset.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'assets': assets_data,
            'total_assets': len(assets_data)
        })
    except Exception as e:
        logger.error(f"Error getting portfolio assets: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/strategies', methods=['GET'])
@jwt_required()
def get_investment_strategies():
    try:
        strategies = InvestmentStrategy.query.filter_by(is_active=True).all()
        
        strategies_data = [{
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'strategy_type': strategy.strategy_type,
            'risk_level': strategy.risk_level,
            'min_investment': float(strategy.min_investment),
            'expected_return': float(strategy.expected_return) if strategy.expected_return else None,
            'asset_allocation': strategy.asset_allocation,
            'created_at': strategy.created_at.isoformat()
        } for strategy in strategies]
        
        return jsonify({
            'success': True,
            'strategies': strategies_data
        })
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/auto-invest', methods=['POST'])
@jwt_required()
def create_auto_invest_plan():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify portfolio ownership
        portfolio = WealthPortfolio.query.filter_by(id=data['portfolio_id'], user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        # Calculate next execution time
        frequency = data['frequency']
        next_execution = datetime.utcnow()
        
        if frequency == 'daily':
            next_execution += timedelta(days=1)
        elif frequency == 'weekly':
            next_execution += timedelta(weeks=1)
        elif frequency == 'monthly':
            next_execution += timedelta(days=30)
        elif frequency == 'quarterly':
            next_execution += timedelta(days=90)
        
        auto_invest = AutoInvestPlan(
            user_id=user_id,
            portfolio_id=data['portfolio_id'],
            strategy_id=data['strategy_id'],
            name=data['name'],
            investment_amount=data['investment_amount'],
            frequency=frequency,
            next_execution=next_execution
        )
        
        db.session.add(auto_invest)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Auto-invest plan created successfully',
            'plan_id': auto_invest.id,
            'next_execution': auto_invest.next_execution.isoformat()
        })
    except Exception as e:
        logger.error(f"Error creating auto-invest plan: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin Routes
@app.route('/api/tiger-wealth/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        total_portfolios = WealthPortfolio.query.count()
        total_assets = WealthAsset.query.count()
        active_auto_invest_plans = AutoInvestPlan.query.filter_by(is_active=True).count()
        total_strategies = InvestmentStrategy.query.filter_by(is_active=True).count()
        
        # Calculate total AUM (Assets Under Management)
        total_aum = db.session.query(db.func.sum(WealthAsset.current_value)).filter(
            WealthAsset.current_value.isnot(None)
        ).scalar() or 0
        
        # Portfolio type distribution
        portfolio_types = db.session.query(
            WealthPortfolio.portfolio_type,
            db.func.count(WealthPortfolio.id)
        ).group_by(WealthPortfolio.portfolio_type).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_portfolios': total_portfolios,
                'total_assets': total_assets,
                'total_aum': float(total_aum),
                'active_auto_invest_plans': active_auto_invest_plans,
                'total_strategies': total_strategies,
                'portfolio_types': {ptype: count for ptype, count in portfolio_types},
                'service_name': 'tiger-wealth-service',
                'category': 'wealth_management'
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/admin/users/<user_id>/upgrade-tier', methods=['PUT'])
@admin_required
def upgrade_user_tier(user_id):
    try:
        data = request.get_json()
        new_tier = data.get('tier')
        
        if new_tier not in ['standard', 'premium', 'elite', 'institutional']:
            return jsonify({'success': False, 'error': 'Invalid tier'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.wealth_tier = new_tier
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User tier upgraded to {new_tier}'
        })
    except Exception as e:
        logger.error(f"Error upgrading user tier: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-wealth/admin/strategies', methods=['POST'])
@admin_required
def create_strategy():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        strategy = InvestmentStrategy(
            name=data['name'],
            description=data.get('description', ''),
            strategy_type=data['strategy_type'],
            risk_level=data['risk_level'],
            min_investment=data['min_investment'],
            expected_return=data.get('expected_return'),
            asset_allocation=data.get('asset_allocation', {}),
            rules=data.get('rules', {}),
            created_by=current_user_id
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Strategy created successfully',
            'strategy_id': strategy.id
        })
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'tiger-wealth-service',
        'category': 'wealth_management',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5004)), debug=True)