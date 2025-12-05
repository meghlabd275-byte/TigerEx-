#!/usr/bin/env python3

"""
TigerEx Technical Indicators Service
Category: trading_tools
Description: Advanced technical indicators including SKDJ, enhanced RSI, custom indicators
Features: SKDJ indicator, enhanced RSI with bands, custom indicator builder, multi-timeframe
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
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from functools import wraps
from enum import Enum
import talib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-technical-indicators-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndicatorType(Enum):
    SKDJ = "skdj"
    RSI_ENHANCED = "rsi_enhanced"
    MACD_ENHANCED = "macd_enhanced"
    BOLLINGER_ENHANCED = "bollinger_enhanced"
    CUSTOM = "custom"

class TimeFrame(Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"

class IndicatorCalculation(db.Model):
    __tablename__ = 'tiger_indicator_calculations'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.Enum(TimeFrame), nullable=False)
    indicator_type = db.Column(db.Enum(IndicatorType), nullable=False)
    
    # Calculation parameters (stored as JSON)
    parameters = db.Column(db.JSON)
    
    # Results (stored as JSON arrays)
    timestamps = db.Column(db.JSON)
    values = db.Column(db.JSON)  # Main indicator values
    signals = db.Column(db.JSON)  # Buy/sell signals
    additional_data = db.Column(db.JSON)  # Additional indicator-specific data
    
    # Metadata
    data_points = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class CustomIndicator(db.Model):
    __tablename__ = 'tiger_custom_indicators'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Indicator definition
    formula = db.Column(db.Text)  # Mathematical formula
    input_sources = db.Column(db.JSON)  # What data to use (price, volume, other indicators)
    parameters = db.Column(db.JSON)  # Default parameters
    calculation_code = db.Column(db.Text)  # Python code for custom calculations
    
    # Sharing settings
    is_public = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TechnicalIndicatorsEngine:
    def __init__(self):
        pass
    
    def calculate_skdj(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                      fastk_period: int = 9, slowk_period: int = 3, slowd_period: int = 3) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate SKDJ indicator (Enhanced KDJ)
        SKDJ provides smoother signals than traditional KDJ
        """
        try:
            # Calculate RSV (Raw Stochastic Value)
            highest_high = talib.MAX(high, timeperiod=fastk_period)
            lowest_low = talib.MIN(low, timeperiod=fastk_period)
            
            # Avoid division by zero
            rsv = np.where(
                highest_high - lowest_low != 0,
                100 * (close - lowest_low) / (highest_high - lowest_low),
                50
            )
            
            # Calculate K, D, J lines using exponential moving averages for smoother results
            k_values = talib.EMA(rsv, timeperiod=slowk_period)
            d_values = talib.EMA(k_values, timeperiod=slowd_period)
            j_values = 3 * k_values - 2 * d_values
            
            # Apply additional smoothing for SKDJ
            k_smooth = talib.EMA(k_values, timeperiod=2)
            d_smooth = talib.EMA(d_values, timeperiod=2)
            j_smooth = talib.EMA(j_values, timeperiod=2)
            
            # Clip values to 0-100 range for K and D
            k_smooth = np.clip(k_smooth, 0, 100)
            d_smooth = np.clip(d_smooth, 0, 100)
            
            return k_smooth, d_smooth, j_smooth
            
        except Exception as e:
            logger.error(f"Error calculating SKDJ: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def calculate_enhanced_rsi(self, close: np.ndarray, period: int = 14, 
                              upper_band: float = 70, lower_band: float = 30,
                              smoothing_period: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Enhanced RSI with bands and smoothing
        """
        try:
            # Calculate basic RSI
            rsi = talib.RSI(close, timeperiod=period)
            
            # Apply additional smoothing
            rsi_smooth = talib.EMA(rsi, timeperiod=smoothing_period)
            
            # Generate signals based on bands
            buy_signals = np.where((rsi_smooth < lower_band) & (rsi_smooth[:-1] >= lower_band[:-1]) if len(rsi_smooth) > 1 else False, 1, 0)
            sell_signals = np.where((rsi_smooth > upper_band) & (rsi_smooth[:-1] <= upper_band[:-1]) if len(rsi_smooth) > 1 else False, -1, 0)
            
            return rsi_smooth, buy_signals, sell_signals
            
        except Exception as e:
            logger.error(f"Error calculating enhanced RSI: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def calculate_enhanced_macd(self, close: np.ndarray, fast_period: int = 12,
                               slow_period: int = 26, signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Enhanced MACD with histogram signals
        """
        try:
            macd, signal, histogram = talib.MACD(close, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
            
            # Generate signals
            buy_signals = np.where((histogram > 0) & (histogram[:-1] <= 0) if len(histogram) > 1 else False, 1, 0)
            sell_signals = np.where((histogram < 0) & (histogram[:-1] >= 0) if len(histogram) > 1 else False, -1, 0)
            
            return macd, signal, histogram, buy_signals + sell_signals
            
        except Exception as e:
            logger.error(f"Error calculating enhanced MACD: {e}")
            return np.array([]), np.array([]), np.array([]), np.array([])
    
    def calculate_enhanced_bollinger(self, close: np.ndarray, period: int = 20, 
                                   std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Enhanced Bollinger Bands with squeeze detection
        """
        try:
            upper, middle, lower = talib.BBANDS(close, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            
            # Calculate bandwidth (squeeze detection)
            bandwidth = (upper - lower) / middle
            
            # Generate signals
            buy_signals = np.where((close < lower) & (close[:-1] >= lower[:-1]) if len(close) > 1 else False, 1, 0)
            sell_signals = np.where((close > upper) & (close[:-1] <= upper[:-1]) if len(close) > 1 else False, -1, 0)
            
            return upper, middle, lower, bandwidth
            
        except Exception as e:
            logger.error(f"Error calculating enhanced Bollinger Bands: {e}")
            return np.array([]), np.array([]), np.array([]), np.array([])
    
    def get_market_data(self, symbol: str, timeframe: TimeFrame, limit: int = 500) -> Optional[pd.DataFrame]:
        """
        Get market data for indicator calculations
        """
        try:
            # This would integrate with your market data service
            # For now, return mock data
            dates = pd.date_range(end=datetime.utcnow(), periods=limit, freq='1H')
            
            # Generate mock OHLCV data
            np.random.seed(42)  # For reproducible results
            base_price = 50000 if symbol == 'BTCUSDT' else 100
            
            price_changes = np.random.normal(0, 0.02, limit).cumsum()
            close_prices = base_price * (1 + price_changes)
            
            # Generate OHLC from close prices
            high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.01, limit)))
            low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.01, limit)))
            open_prices = np.roll(close_prices, 1)
            open_prices[0] = close_prices[0]
            
            volumes = np.random.uniform(100, 1000, limit)
            
            return pd.DataFrame({
                'timestamp': dates,
                'open': open_prices,
                'high': high_prices,
                'low': low_prices,
                'close': close_prices,
                'volume': volumes
            })
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None

# Initialize the indicators engine
indicators_engine = TechnicalIndicatorsEngine()

# API Routes
@app.route('/api/v1/indicators/skdj', methods=['POST'])
@jwt_required()
def calculate_skdj():
    """Calculate SKDJ indicator"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symbol = data['symbol']
        timeframe = TimeFrame(data['timeframe'])
        fastk_period = data.get('fastk_period', 9)
        slowk_period = data.get('slowk_period', 3)
        slowd_period = data.get('slowd_period', 3)
        limit = data.get('limit', 500)
        
        # Get market data
        market_data = indicators_engine.get_market_data(symbol, timeframe, limit)
        if market_data is None:
            return jsonify({'success': False, 'error': 'Failed to get market data'}), 500
        
        # Calculate SKDJ
        k_values, d_values, j_values = indicators_engine.calculate_skdj(
            market_data['high'].values,
            market_data['low'].values,
            market_data['close'].values,
            fastk_period,
            slowk_period,
            slowd_period
        )
        
        if len(k_values) == 0:
            return jsonify({'success': False, 'error': 'Failed to calculate SKDJ'}), 500
        
        # Generate signals
        signals = []
        for i in range(1, len(k_values)):
            if k_values[i-1] < 20 and k_values[i] >= 20 and d_values[i] > k_values[i]:
                signals.append(1)  # Buy signal
            elif k_values[i-1] > 80 and k_values[i] <= 80 and d_values[i] < k_values[i]:
                signals.append(-1)  # Sell signal
            else:
                signals.append(0)  # No signal
        
        signals.insert(0, 0)  # No signal for first data point
        
        # Store calculation
        calculation = IndicatorCalculation(
            user_id=user_id,
            symbol=symbol,
            timeframe=timeframe,
            indicator_type=IndicatorType.SKDJ,
            parameters={
                'fastk_period': fastk_period,
                'slowk_period': slowk_period,
                'slowd_period': slowd_period
            },
            timestamps=[ts.isoformat() for ts in market_data['timestamp']],
            values={
                'k': k_values.tolist(),
                'd': d_values.tolist(),
                'j': j_values.tolist()
            },
            signals=signals,
            additional_data={
                'overbought': 80,
                'oversold': 20
            },
            data_points=len(k_values)
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'calculation_id': calculation.id,
            'data': {
                'timestamps': [ts.isoformat() for ts in market_data['timestamp']],
                'k_values': k_values.tolist(),
                'd_values': d_values.tolist(),
                'j_values': j_values.tolist(),
                'signals': signals
            },
            'parameters': {
                'fastk_period': fastk_period,
                'slowk_period': slowk_period,
                'slowd_period': slowd_period
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating SKDJ: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/rsi-enhanced', methods=['POST'])
@jwt_required()
def calculate_enhanced_rsi():
    """Calculate Enhanced RSI with bands"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symbol = data['symbol']
        timeframe = TimeFrame(data['timeframe'])
        period = data.get('period', 14)
        upper_band = data.get('upper_band', 70)
        lower_band = data.get('lower_band', 30)
        smoothing_period = data.get('smoothing_period', 5)
        limit = data.get('limit', 500)
        
        # Get market data
        market_data = indicators_engine.get_market_data(symbol, timeframe, limit)
        if market_data is None:
            return jsonify({'success': False, 'error': 'Failed to get market data'}), 500
        
        # Calculate Enhanced RSI
        rsi_values, buy_signals, sell_signals = indicators_engine.calculate_enhanced_rsi(
            market_data['close'].values,
            period,
            upper_band,
            lower_band,
            smoothing_period
        )
        
        if len(rsi_values) == 0:
            return jsonify({'success': False, 'error': 'Failed to calculate Enhanced RSI'}), 500
        
        # Combine signals
        signals = (buy_signals + sell_signals).tolist()
        
        # Store calculation
        calculation = IndicatorCalculation(
            user_id=user_id,
            symbol=symbol,
            timeframe=timeframe,
            indicator_type=IndicatorType.RSI_ENHANCED,
            parameters={
                'period': period,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'smoothing_period': smoothing_period
            },
            timestamps=[ts.isoformat() for ts in market_data['timestamp']],
            values={'rsi': rsi_values.tolist()},
            signals=signals,
            additional_data={
                'upper_band': upper_band,
                'lower_band': lower_band
            },
            data_points=len(rsi_values)
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'calculation_id': calculation.id,
            'data': {
                'timestamps': [ts.isoformat() for ts in market_data['timestamp']],
                'rsi_values': rsi_values.tolist(),
                'signals': signals
            },
            'parameters': {
                'period': period,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'smoothing_period': smoothing_period
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating Enhanced RSI: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/multi-timeframe', methods=['POST'])
@jwt_required()
def calculate_multi_timeframe():
    """Calculate indicators across multiple timeframes"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symbol = data['symbol']
        indicator = data['indicator']
        timeframes = [TimeFrame(tf) for tf in data['timeframes']]
        parameters = data.get('parameters', {})
        
        results = {}
        
        for timeframe in timeframes:
            if indicator == 'skdj':
                fastk_period = parameters.get('fastk_period', 9)
                slowk_period = parameters.get('slowk_period', 3)
                slowd_period = parameters.get('slowd_period', 3)
                
                market_data = indicators_engine.get_market_data(symbol, timeframe, 500)
                if market_data is not None:
                    k_values, d_values, j_values = indicators_engine.calculate_skdj(
                        market_data['high'].values,
                        market_data['low'].values,
                        market_data['close'].values,
                        fastk_period,
                        slowk_period,
                        slowd_period
                    )
                    
                    results[timeframe.value] = {
                        'timestamps': [ts.isoformat() for ts in market_data['timestamp']],
                        'k_values': k_values.tolist(),
                        'd_values': d_values.tolist(),
                        'j_values': j_values.tolist()
                    }
            
            elif indicator == 'rsi_enhanced':
                period = parameters.get('period', 14)
                upper_band = parameters.get('upper_band', 70)
                lower_band = parameters.get('lower_band', 30)
                
                market_data = indicators_engine.get_market_data(symbol, timeframe, 500)
                if market_data is not None:
                    rsi_values, _, _ = indicators_engine.calculate_enhanced_rsi(
                        market_data['close'].values,
                        period,
                        upper_band,
                        lower_band
                    )
                    
                    results[timeframe.value] = {
                        'timestamps': [ts.isoformat() for ts in market_data['timestamp']],
                        'rsi_values': rsi_values.tolist()
                    }
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'indicator': indicator,
            'multi_timeframe_data': results
        })
        
    except Exception as e:
        logger.error(f"Error calculating multi-timeframe indicators: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/custom', methods=['POST'])
@jwt_required()
def create_custom_indicator():
    """Create a custom indicator"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        custom_indicator = CustomIndicator(
            user_id=user_id,
            name=data['name'],
            description=data.get('description'),
            formula=data.get('formula'),
            input_sources=data.get('input_sources', []),
            parameters=data.get('parameters', {}),
            calculation_code=data.get('calculation_code'),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(custom_indicator)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'indicator_id': custom_indicator.id,
            'name': custom_indicator.name
        })
        
    except Exception as e:
        logger.error(f"Error creating custom indicator: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/custom', methods=['GET'])
@jwt_required()
def list_custom_indicators():
    """List custom indicators"""
    try:
        user_id = get_jwt_identity()
        include_public = request.args.get('include_public', '').lower() == 'true'
        
        query = CustomIndicator.query.filter_by(user_id=user_id)
        
        if include_public:
            public_query = CustomIndicator.query.filter_by(is_public=True)
            query = query.union(public_query)
        
        indicators = query.order_by(CustomIndicator.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'indicators': [{
                'id': indicator.id,
                'name': indicator.name,
                'description': indicator.description,
                'input_sources': indicator.input_sources,
                'parameters': indicator.parameters,
                'is_public': indicator.is_public,
                'usage_count': indicator.usage_count,
                'created_at': indicator.created_at.isoformat()
            } for indicator in indicators]
        })
        
    except Exception as e:
        logger.error(f"Error listing custom indicators: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/calculations', methods=['GET'])
@jwt_required()
def list_calculations():
    """List user's indicator calculations"""
    try:
        user_id = get_jwt_identity()
        symbol = request.args.get('symbol')
        indicator_type = request.args.get('indicator_type')
        timeframe = request.args.get('timeframe')
        
        query = IndicatorCalculation.query.filter_by(user_id=user_id)
        
        if symbol:
            query = query.filter_by(symbol=symbol)
        
        if indicator_type:
            query = query.filter_by(indicator_type=IndicatorType(indicator_type))
        
        if timeframe:
            query = query.filter_by(timeframe=TimeFrame(timeframe))
        
        calculations = query.order_by(IndicatorCalculation.last_updated.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'calculations': [{
                'id': calc.id,
                'symbol': calc.symbol,
                'timeframe': calc.timeframe.value,
                'indicator_type': calc.indicator_type.value,
                'parameters': calc.parameters,
                'data_points': calc.data_points,
                'last_updated': calc.last_updated.isoformat()
            } for calc in calculations]
        })
        
    except Exception as e:
        logger.error(f"Error listing calculations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/indicators/calculations/<calculation_id>', methods=['GET'])
@jwt_required()
def get_calculation(calculation_id):
    """Get specific indicator calculation"""
    try:
        user_id = get_jwt_identity()
        
        calculation = IndicatorCalculation.query.filter_by(
            id=calculation_id,
            user_id=user_id
        ).first()
        
        if not calculation:
            return jsonify({'success': False, 'error': 'Calculation not found'}), 404
        
        return jsonify({
            'success': True,
            'calculation': {
                'id': calculation.id,
                'symbol': calculation.symbol,
                'timeframe': calculation.timeframe.value,
                'indicator_type': calculation.indicator_type.value,
                'parameters': calculation.parameters,
                'timestamps': calculation.timestamps,
                'values': calculation.values,
                'signals': calculation.signals,
                'additional_data': calculation.additional_data,
                'data_points': calculation.data_points,
                'last_updated': calculation.last_updated.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting calculation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'technical-indicators-service',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=True)