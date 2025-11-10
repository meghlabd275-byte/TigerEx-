#!/usr/bin/env python3
"""
AI-Powered Trading Insights Service for TigerEx v11.0.0
Advanced machine learning algorithms for trading predictions and analytics
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import redis
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

# Redis for caching predictions
redis_client = redis.Redis(host='localhost', port=6379, db=5, decode_responses=True)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Numeric(20, 8), nullable=False)
    high_price = db.Column(db.Numeric(20, 8), nullable=False)
    low_price = db.Column(db.Numeric(20, 8), nullable=False)
    close_price = db.Column(db.Numeric(20, 8), nullable=False)
    volume = db.Column(db.Numeric(20, 8), nullable=False)
    
    # Technical indicators
    sma_20 = db.Column(db.Numeric(20, 8))
    ema_20 = db.Column(db.Numeric(20, 8))
    rsi = db.Column(db.Numeric(10, 2))
    macd = db.Column(db.Numeric(20, 8))
    bollinger_upper = db.Column(db.Numeric(20, 8))
    bollinger_lower = db.Column(db.Numeric(20, 8))

class TradingSignal(db.Model):
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.String(64), nullable=False, unique=True)
    symbol = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    
    # Signal details
    signal_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)  # 0-100
    prediction_price = db.Column(db.Numeric(20, 8))
    time_horizon = db.Column(db.String(20))  # 1h, 4h, 1d, 1w
    
    # AI model info
    model_version = db.Column(db.String(20))
    model_accuracy = db.Column(db.Float)
    
    # Metadata
    features_used = db.Column(db.JSON)
    reasoning = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class AIModel(db.Model):
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(20), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # price_prediction, sentiment, risk
    
    # Model metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    
    # Training info
    training_data_start = db.Column(db.DateTime)
    training_data_end = db.Column(db.DateTime)
    last_training = db.Column(db.DateTime)
    
    # Model file path
    model_file_path = db.Column(db.String(255))
    scaler_file_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class SentimentData(db.Model):
    __tablename__ = 'sentiment_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(50))  # twitter, reddit, news
    content = db.Column(db.Text)
    sentiment_score = db.Column(db.Float)  # -1 to 1
    sentiment_magnitude = db.Column(db.Float)
    
    # Analysis results
    keywords = db.Column(db.JSON)
    topics = db.Column(db.JSON)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AITradingEngine:
    def __init__(self):
        self.price_model = None
        self.scaler = StandardScaler()
        self.load_models()
    
    def load_models(self):
        """Load pre-trained AI models"""
        try:
            # Try to load existing models
            self.price_model = joblib.load('models/price_prediction_model.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            logger.info("AI models loaded successfully")
        except FileNotFoundError:
            # Train new models if not found
            self.train_price_prediction_model()
    
    def train_price_prediction_model(self):
        """Train price prediction model using historical data"""
        logger.info("Training price prediction model...")
        
        # Get historical data
        data = MarketData.query.order_by(MarketData.timestamp.desc()).limit(10000).all()
        
        if len(data) < 1000:
            logger.warning("Insufficient data for training model")
            return
        
        # Create features
        df = pd.DataFrame([{
            'open': float(d.open_price),
            'high': float(d.high_price),
            'low': float(d.low_price),
            'close': float(d.close_price),
            'volume': float(d.volume),
            'sma_20': float(d.sma_20) if d.sma_20 else None,
            'ema_20': float(d.ema_20) if d.ema_20 else None,
            'rsi': float(d.rsi) if d.rsi else None,
            'macd': float(d.macd) if d.macd else None,
        } for d in data if d.sma_20 is not None])
        
        df = df.dropna()
        
        if len(df) < 500:
            logger.warning("Insufficient clean data for training")
            return
        
        # Feature engineering
        df['price_change'] = df['close'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volatility'] = df['price_change'].rolling(window=20).std()
        
        df = df.dropna()
        
        # Prepare features and target
        features = ['open', 'high', 'low', 'close', 'volume', 'sma_20', 'ema_20', 
                   'rsi', 'macd', 'price_change', 'high_low_ratio', 'volume_ma', 'volatility']
        X = df[features].values
        y = df['close'].shift(-1).values[:-1]  # Predict next close price
        X = X[:-1]  # Align with target
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.price_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.price_model.fit(X_scaled, y)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.price_model, 'models/price_prediction_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        # Save model metadata to database
        model = AIModel(
            model_name='price_prediction_rf',
            model_version='1.0.0',
            model_type='price_prediction',
            accuracy=self.price_model.score(X_scaled, y),
            model_file_path='models/price_prediction_model.pkl',
            scaler_file_path='models/scaler.pkl',
            last_training=datetime.utcnow()
        )
        db.session.add(model)
        db.session.commit()
        
        logger.info("Price prediction model trained successfully")
    
    def predict_price(self, symbol: str, time_horizon: str = '1d'):
        """Generate price prediction for a symbol"""
        cache_key = f"price_prediction_{symbol}_{time_horizon}"
        
        # Check cache
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Get recent data
        data = MarketData.query.filter_by(symbol=symbol).order_by(
            MarketData.timestamp.desc()).limit(100).all()
        
        if len(data) < 50 or not self.price_model:
            return None
        
        # Prepare features for prediction
        latest_data = data[0]
        features = np.array([[
            float(latest_data.open_price),
            float(latest_data.high_price),
            float(latest_data.low_price),
            float(latest_data.close_price),
            float(latest_data.volume),
            float(latest_data.sma_20) if latest_data.sma_20 else 0,
            float(latest_data.ema_20) if latest_data.ema_20 else 0,
            float(latest_data.rsi) if latest_data.rsi else 50,
            float(latest_data.macd) if latest_data.macd else 0,
            0.01,  # Recent price change
            1.02,  # High/low ratio
            float(latest_data.volume),  # Volume
            0.02   # Volatility
        ]])
        
        features_scaled = self.scaler.transform(features)
        prediction = self.price_model.predict(features_scaled)[0]
        
        # Calculate confidence based on model accuracy
        model = AIModel.query.filter_by(model_type='price_prediction', is_active=True).first()
        confidence = model.accuracy * 100 if model else 75.0
        
        result = {
            'symbol': symbol,
            'current_price': float(latest_data.close_price),
            'predicted_price': float(prediction),
            'price_change': float(prediction - latest_data.close_price),
            'price_change_percent': float((prediction - latest_data.close_price) / latest_data.close_price * 100),
            'confidence': confidence,
            'time_horizon': time_horizon,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Cache result for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(result))
        
        return result
    
    def analyze_sentiment(self, symbol: str):
        """Analyze sentiment for a symbol"""
        cache_key = f"sentiment_{symbol}"
        
        # Check cache
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Get recent sentiment data
        sentiments = SentimentData.query.filter_by(symbol=symbol).order_by(
            SentimentData.timestamp.desc()).limit(100).all()
        
        if not sentiments:
            return None
        
        # Calculate sentiment metrics
        positive_count = sum(1 for s in sentiments if s.sentiment_score > 0.1)
        negative_count = sum(1 for s in sentiments if s.sentiment_score < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        avg_sentiment = np.mean([s.sentiment_score for s in sentiments])
        sentiment_magnitude = np.mean([s.sentiment_magnitude for s in sentiments])
        
        # Extract common keywords
        all_keywords = []
        for s in sentiments:
            if s.keywords:
                all_keywords.extend(s.keywords)
        
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = {
            'symbol': symbol,
            'sentiment_score': float(avg_sentiment),
            'sentiment_magnitude': float(sentiment_magnitude),
            'sentiment_label': 'BULLISH' if avg_sentiment > 0.1 else 'BEARISH' if avg_sentiment < -0.1 else 'NEUTRAL',
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_mentions': len(sentiments),
            'top_keywords': top_keywords,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Cache result for 10 minutes
        redis_client.setex(cache_key, 600, json.dumps(result))
        
        return result
    
    def generate_trading_signal(self, symbol: str, user_id: str, time_horizon: str = '1d'):
        """Generate comprehensive trading signal"""
        # Get price prediction
        price_pred = self.predict_price(symbol, time_horizon)
        if not price_pred:
            return None
        
        # Get sentiment analysis
        sentiment = self.analyze_sentiment(symbol)
        
        # Calculate signal based on multiple factors
        price_signal = 'BUY' if price_pred['price_change_percent'] > 2 else 'SELL' if price_pred['price_change_percent'] < -2 else 'HOLD'
        sentiment_signal = 'BUY' if sentiment and sentiment['sentiment_score'] > 0.2 else 'SELL' if sentiment and sentiment['sentiment_score'] < -0.2 else 'HOLD'
        
        # Combine signals with weights
        price_weight = 0.7
        sentiment_weight = 0.3
        
        signal_score = 0
        if price_signal == 'BUY':
            signal_score += price_weight
        elif price_signal == 'SELL':
            signal_score -= price_weight
        
        if sentiment_signal == 'BUY':
            signal_score += sentiment_weight
        elif sentiment_signal == 'SELL':
            signal_score -= sentiment_weight
        
        final_signal = 'BUY' if signal_score > 0.3 else 'SELL' if signal_score < -0.3 else 'HOLD'
        confidence = min(abs(signal_score) * 100, 95)
        
        # Generate reasoning
        reasoning_parts = []
        if price_pred['price_change_percent'] > 2:
            reasoning_parts.append(f"Price prediction shows {price_pred['price_change_percent']:.1f}% upside potential")
        elif price_pred['price_change_percent'] < -2:
            reasoning_parts.append(f"Price prediction shows {price_pred['price_change_percent']:.1f}% downside risk")
        
        if sentiment:
            reasoning_parts.append(f"Market sentiment is {sentiment['sentiment_label'].lower()} with {sentiment['total_mentions']} recent mentions")
        
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Analysis based on technical indicators and market data"
        
        signal = TradingSignal(
            signal_id=str(uuid.uuid4()),
            symbol=symbol,
            user_id=user_id,
            signal_type=final_signal,
            confidence=confidence,
            prediction_price=price_pred['predicted_price'],
            time_horizon=time_horizon,
            model_version='1.0.0',
            model_accuracy=price_pred['confidence'],
            features_used=['price_indicators', 'sentiment_analysis'],
            reasoning=reasoning,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(signal)
        db.session.commit()
        
        return {
            'signal_id': signal.signal_id,
            'symbol': symbol,
            'signal_type': final_signal,
            'confidence': confidence,
            'prediction_price': float(price_pred['predicted_price']),
            'current_price': price_pred['current_price'],
            'price_change_percent': price_pred['price_change_percent'],
            'reasoning': reasoning,
            'time_horizon': time_horizon,
            'expires_at': signal.expires_at.isoformat()
        }

# Initialize AI engine
ai_engine = AITradingEngine()

# API Routes
@app.route('/api/ai/price-prediction/<symbol>', methods=['GET'])
@jwt_required()
def get_price_prediction(symbol):
    try:
        time_horizon = request.args.get('time_horizon', '1d')
        prediction = ai_engine.predict_price(symbol, time_horizon)
        
        if not prediction:
            return jsonify({'success': False, 'error': 'Insufficient data for prediction'}), 404
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        logger.error(f"Error getting price prediction: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/sentiment-analysis/<symbol>', methods=['GET'])
@jwt_required()
def get_sentiment_analysis(symbol):
    try:
        sentiment = ai_engine.analyze_sentiment(symbol)
        
        if not sentiment:
            return jsonify({'success': False, 'error': 'No sentiment data available'}), 404
        
        return jsonify({
            'success': True,
            'sentiment': sentiment
        })
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/trading-signal', methods=['POST'])
@jwt_required()
def generate_trading_signal():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symbol = data.get('symbol')
        time_horizon = data.get('time_horizon', '1d')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'}), 400
        
        signal = ai_engine.generate_trading_signal(symbol, user_id, time_horizon)
        
        if not signal:
            return jsonify({'success': False, 'error': 'Unable to generate signal'}), 500
        
        return jsonify({
            'success': True,
            'signal': signal
        })
    except Exception as e:
        logger.error(f"Error generating trading signal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/user-signals', methods=['GET'])
@jwt_required()
def get_user_signals():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        signals = TradingSignal.query.filter_by(user_id=user_id).order_by(
            TradingSignal.created_at.desc()).paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'signals': [
                {
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'confidence': signal.confidence,
                    'prediction_price': float(signal.prediction_price) if signal.prediction_price else None,
                    'reasoning': signal.reasoning,
                    'time_horizon': signal.time_horizon,
                    'created_at': signal.created_at.isoformat(),
                    'expires_at': signal.expires_at.isoformat() if signal.expires_at else None
                }
                for signal in signals.items
            ],
            'pagination': {
                'page': signals.page,
                'per_page': signals.per_page,
                'total': signals.total,
                'total_pages': signals.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting user signals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/model-performance', methods=['GET'])
@jwt_required()
def get_model_performance():
    try:
        models = AIModel.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'models': [
                {
                    'model_name': model.model_name,
                    'model_version': model.model_version,
                    'model_type': model.model_type,
                    'accuracy': model.accuracy,
                    'precision': model.precision,
                    'recall': model.recall,
                    'f1_score': model.f1_score,
                    'last_training': model.last_training.isoformat() if model.last_training else None
                }
                for model in models
            ]
        })
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/retrain-model', methods=['POST'])
@jwt_required()
def retrain_model():
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'price_prediction')
        
        if model_type == 'price_prediction':
            ai_engine.train_price_prediction_model()
            return jsonify({'success': True, 'message': 'Model retraining started'})
        else:
            return jsonify({'success': False, 'error': 'Unsupported model type'}), 400
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("AI Trading Insights Service started successfully")
    app.run(host='0.0.0.0', port=5004, debug=True)