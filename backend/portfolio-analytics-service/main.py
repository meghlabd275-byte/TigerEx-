#!/usr/bin/env python3
"""
Advanced Portfolio Analytics Service for TigerEx v11.0.0
Comprehensive portfolio management and analytics with AI-powered insights
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
import pandas as pd
from decimal import Decimal
import json

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

# Models
class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Portfolio metrics
    total_value = db.Column(db.Numeric(20, 8), default=0)
    total_invested = db.Column(db.Numeric(20, 8), default=0)
    total_pnl = db.Column(db.Numeric(20, 8), default=0)
    pnl_percentage = db.Column(db.Float, default=0)
    
    # Risk metrics
    volatility = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    beta = db.Column(db.Float)
    alpha = db.Column(db.Float)
    
    # Allocation metrics
    asset_allocation = db.Column(db.JSON)
    sector_allocation = db.Column(db.JSON)
    geographic_allocation = db.Column(db.JSON)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PortfolioAsset(db.Model):
    __tablename__ = 'portfolio_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.String(64), db.ForeignKey('portfolios.portfolio_id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_name = db.Column(db.String(100))
    asset_type = db.Column(db.String(20))  # crypto, stock, etf, bond
    
    # Holdings
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    average_cost = db.Column(db.Numeric(20, 8), nullable=False)
    current_price = db.Column(db.Numeric(20, 8))
    current_value = db.Column(db.Numeric(20, 8))
    
    # Performance
    unrealized_pnl = db.Column(db.Numeric(20, 8), default=0)
    unrealized_pnl_percent = db.Column(db.Float, default=0)
    
    # Asset metadata
    sector = db.Column(db.String(50))
    market_cap = db.Column(db.String(20))  # large, mid, small
    geography = db.Column(db.String(50))
    
    first_purchase = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    portfolio = db.relationship('Portfolio', backref=db.backref('assets', lazy=True, cascade="all, delete-orphan"))

class PortfolioTransaction(db.Model):
    __tablename__ = 'portfolio_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(64), nullable=False, unique=True)
    portfolio_id = db.Column(db.String(64), db.ForeignKey('portfolios.portfolio_id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, DEPOSIT, WITHDRAW
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    total_amount = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Fees
    trading_fee = db.Column(db.Numeric(20, 8), default=0)
    network_fee = db.Column(db.Numeric(20, 8), default=0)
    
    # Metadata
    exchange = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortfolioAnalytics(db.Model):
    __tablename__ = 'portfolio_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.String(64), db.ForeignKey('portfolios.portfolio_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Daily metrics
    portfolio_value = db.Column(db.Numeric(20, 8))
    daily_return = db.Column(db.Float)
    daily_volatility = db.Column(db.Float)
    
    # Risk metrics
    var_95 = db.Column(db.Numeric(20, 8))  # Value at Risk 95%
    var_99 = db.Column(db.Numeric(20, 8))  # Value at Risk 99%
    beta = db.Column(db.Float)
    correlation_to_market = db.Column(db.Float)
    
    # Performance metrics
    rolling_return_7d = db.Column(db.Float)
    rolling_return_30d = db.Column(db.Float)
    rolling_return_90d = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortfolioAnalyticsEngine:
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def calculate_portfolio_metrics(self, portfolio_id: str):
        """Calculate comprehensive portfolio metrics"""
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id).first()
        if not portfolio:
            return None
        
        assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio_id).all()
        if not assets:
            return None
        
        # Basic calculations
        total_value = sum(asset.current_value or 0 for asset in assets)
        total_invested = sum(asset.quantity * asset.average_cost for asset in assets)
        total_pnl = total_value - total_invested
        pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Risk calculations
        returns = self.calculate_historical_returns(portfolio_id)
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        sharpe_ratio = (np.mean(returns) * 252 - self.risk_free_rate) / volatility if volatility > 0 else 0
        
        # Allocation calculations
        asset_allocation = {}
        sector_allocation = {}
        geographic_allocation = {}
        
        for asset in assets:
            value = float(asset.current_value or 0)
            if value > 0:
                # Asset allocation by type
                asset_type = asset.asset_type or 'other'
                asset_allocation[asset_type] = asset_allocation.get(asset_type, 0) + (value / total_value * 100)
                
                # Sector allocation
                if asset.sector:
                    sector_allocation[asset.sector] = sector_allocation.get(asset.sector, 0) + (value / total_value * 100)
                
                # Geographic allocation
                if asset.geography:
                    geographic_allocation[asset.geography] = geographic_allocation.get(asset.geography, 0) + (value / total_value * 100)
        
        # Update portfolio
        portfolio.total_value = total_value
        portfolio.total_invested = total_invested
        portfolio.total_pnl = total_pnl
        portfolio.pnl_percentage = pnl_percentage
        portfolio.volatility = volatility
        portfolio.sharpe_ratio = sharpe_ratio
        portfolio.asset_allocation = asset_allocation
        portfolio.sector_allocation = sector_allocation
        portfolio.geographic_allocation = geographic_allocation
        portfolio.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'total_value': float(total_value),
            'total_invested': float(total_invested),
            'total_pnl': float(total_pnl),
            'pnl_percentage': pnl_percentage,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'asset_allocation': asset_allocation,
            'sector_allocation': sector_allocation,
            'geographic_allocation': geographic_allocation
        }
    
    def calculate_historical_returns(self, portfolio_id: str, days: int = 90):
        """Calculate historical portfolio returns"""
        analytics = PortfolioAnalytics.query.filter_by(portfolio_id=portfolio_id).order_by(
            PortfolioAnalytics.date.desc()).limit(days).all()
        
        if len(analytics) < 2:
            return []
        
        returns = []
        for i in range(1, len(analytics)):
            prev_value = float(analytics[i].portfolio_value or 0)
            curr_value = float(analytics[i-1].portfolio_value or 0)
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
        
        return returns
    
    def calculate_correlation_matrix(self, portfolio_id: str):
        """Calculate correlation matrix for portfolio assets"""
        assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio_id).all()
        if len(assets) < 2:
            return {}
        
        # Get historical returns for each asset (simplified for demo)
        symbols = [asset.symbol for asset in assets]
        correlation_data = {}
        
        for symbol in symbols:
            # Simulate correlation data (in real implementation, fetch from market data)
            for other_symbol in symbols:
                if symbol != other_symbol:
                    correlation = np.random.uniform(-0.5, 0.8)  # Simulated correlation
                    correlation_data[f"{symbol}_{other_symbol}"] = correlation
        
        return correlation_data
    
    def calculate_risk_metrics(self, portfolio_id: str):
        """Calculate advanced risk metrics"""
        returns = self.calculate_historical_returns(portfolio_id)
        if len(returns) < 30:
            return {}
        
        returns_array = np.array(returns)
        
        # Value at Risk calculations
        var_95 = np.percentile(returns_array, 5)
        var_99 = np.percentile(returns_array, 1)
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + returns_array)
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # Beta (simplified calculation)
        # In real implementation, calculate against market benchmark
        beta = np.random.uniform(0.5, 1.5)  # Simulated beta
        
        # Alpha calculation (simplified)
        market_return = np.random.uniform(0.05, 0.15)  # Simulated market return
        portfolio_return = np.mean(returns_array) * 252
        alpha = portfolio_return - (self.risk_free_rate + beta * (market_return - self.risk_free_rate))
        
        return {
            'var_95': float(var_95),
            'var_99': float(var_99),
            'max_drawdown': float(max_drawdown),
            'beta': float(beta),
            'alpha': float(alpha),
            'volatility': float(np.std(returns_array) * np.sqrt(252))
        }
    
    def generate_portfolio_recommendations(self, portfolio_id: str):
        """Generate AI-powered portfolio recommendations"""
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id).first()
        if not portfolio:
            return []
        
        metrics = self.calculate_portfolio_metrics(portfolio_id)
        risk_metrics = self.calculate_risk_metrics(portfolio_id)
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_metrics.get('volatility', 0) > 0.3:
            recommendations.append({
                'type': 'RISK',
                'priority': 'HIGH',
                'title': 'High Volatility Detected',
                'description': f"Portfolio volatility is {risk_metrics['volatility']:.1%}, consider adding stable assets",
                'action': 'Consider adding bonds or stablecoins to reduce portfolio volatility'
            })
        
        # Diversification recommendations
        if portfolio.asset_allocation:
            crypto_allocation = portfolio.asset_allocation.get('crypto', 0)
            if crypto_allocation > 80:
                recommendations.append({
                    'type': 'DIVERSIFICATION',
                    'priority': 'MEDIUM',
                    'title': 'Overexposed to Crypto',
                    'description': f"Crypto allocation is {crypto_allocation:.1f}%, consider diversifying",
                    'action': 'Add traditional assets like stocks or ETFs to improve diversification'
                })
        
        # Performance recommendations
        if portfolio.pnl_percentage < -10:
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'HIGH',
                'title': 'Underperforming Portfolio',
                'description': f"Portfolio is down {portfolio.pnl_percentage:.1f}%",
                'action': 'Review underperforming assets and consider rebalancing or stop-loss orders'
            })
        
        # Sharpe ratio recommendations
        if portfolio.sharpe_ratio and portfolio.sharpe_ratio < 0.5:
            recommendations.append({
                'type': 'EFFICIENCY',
                'priority': 'MEDIUM',
                'title': 'Low Risk-Adjusted Returns',
                'description': f"Sharpe ratio is {portfolio.sharpe_ratio:.2f}, below optimal range",
                'action': 'Consider optimizing asset allocation to improve risk-adjusted returns'
            })
        
        return recommendations

# Initialize analytics engine
analytics_engine = PortfolioAnalyticsEngine()

# API Routes
@app.route('/api/portfolio/create', methods=['POST'])
@jwt_required()
def create_portfolio():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        portfolio = Portfolio(
            portfolio_id=str(uuid.uuid4()),
            user_id=user_id,
            name=data.get('name'),
            description=data.get('description')
        )
        
        db.session.add(portfolio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'portfolio_id': portfolio.portfolio_id,
            'message': 'Portfolio created successfully'
        })
    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolios', methods=['GET'])
@jwt_required()
def get_user_portfolios():
    try:
        user_id = get_jwt_identity()
        portfolios = Portfolio.query.filter_by(user_id=user_id, is_active=True).all()
        
        return jsonify({
            'success': True,
            'portfolios': [
                {
                    'portfolio_id': portfolio.portfolio_id,
                    'name': portfolio.name,
                    'description': portfolio.description,
                    'total_value': float(portfolio.total_value or 0),
                    'total_pnl': float(portfolio.total_pnl or 0),
                    'pnl_percentage': portfolio.pnl_percentage or 0,
                    'created_at': portfolio.created_at.isoformat()
                }
                for portfolio in portfolios
            ]
        })
    except Exception as e:
        logger.error(f"Error getting portfolios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/<portfolio_id>/analytics', methods=['GET'])
@jwt_required()
def get_portfolio_analytics(portfolio_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        # Calculate analytics
        metrics = analytics_engine.calculate_portfolio_metrics(portfolio_id)
        risk_metrics = analytics_engine.calculate_risk_metrics(portfolio_id)
        correlations = analytics_engine.calculate_correlation_matrix(portfolio_id)
        recommendations = analytics_engine.generate_portfolio_recommendations(portfolio_id)
        
        return jsonify({
            'success': True,
            'analytics': {
                'basic_metrics': metrics,
                'risk_metrics': risk_metrics,
                'correlations': correlations,
                'recommendations': recommendations,
                'last_updated': portfolio.updated_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting portfolio analytics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/<portfolio_id>/assets', methods=['GET'])
@jwt_required()
def get_portfolio_assets(portfolio_id):
    try:
        user_id = get_jwt_identity()
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        assets = PortfolioAsset.query.filter_by(portfolio_id=portfolio_id).all()
        
        return jsonify({
            'success': True,
            'assets': [
                {
                    'symbol': asset.symbol,
                    'asset_name': asset.asset_name,
                    'asset_type': asset.asset_type,
                    'quantity': float(asset.quantity),
                    'average_cost': float(asset.average_cost),
                    'current_price': float(asset.current_price or 0),
                    'current_value': float(asset.current_value or 0),
                    'unrealized_pnl': float(asset.unrealized_pnl or 0),
                    'unrealized_pnl_percent': asset.unrealized_pnl_percent or 0,
                    'sector': asset.sector,
                    'geography': asset.geography
                }
                for asset in assets
            ]
        })
    except Exception as e:
        logger.error(f"Error getting portfolio assets: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/<portfolio_id>/performance', methods=['GET'])
@jwt_required()
def get_portfolio_performance(portfolio_id):
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        # Get historical analytics
        analytics = PortfolioAnalytics.query.filter_by(portfolio_id=portfolio_id).order_by(
            PortfolioAnalytics.date.desc()).limit(days).all()
        
        performance_data = []
        for analytic in analytics:
            performance_data.append({
                'date': analytic.date.isoformat(),
                'portfolio_value': float(analytic.portfolio_value or 0),
                'daily_return': analytic.daily_return or 0,
                'volatility': analytic.daily_volatility or 0
            })
        
        return jsonify({
            'success': True,
            'performance': performance_data
        })
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/portfolio/recommendations', methods=['GET'])
@jwt_required()
def get_portfolio_recommendations():
    try:
        user_id = get_jwt_identity()
        portfolio_id = request.args.get('portfolio_id')
        
        if not portfolio_id:
            return jsonify({'success': False, 'error': 'Portfolio ID is required'}), 400
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        
        recommendations = analytics_engine.generate_portfolio_recommendations(portfolio_id)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        logger.error(f"Error getting portfolio recommendations: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Portfolio Analytics Service started successfully")
    app.run(host='0.0.0.0', port=5005, debug=True)