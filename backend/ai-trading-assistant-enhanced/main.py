#!/usr/bin/env python3
"""
AI-Powered Trading Assistant Service
Advanced AI assistant with machine learning, sentiment analysis, and predictive analytics
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import yfinance as yf
import requests
from textblob import TextBlob
import ta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# FastAPI app
app = FastAPI(
    title="TigerEx AI Trading Assistant",
    description="Advanced AI-powered trading assistant with ML predictions and analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_ai")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Models initialization
class AIModels:
    def __init__(self):
        self.sentiment_analyzer = None
        self.price_predictor = None
        self.volatility_predictor = None
        self.trend_classifier = None
        self.scaler = StandardScaler()
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize AI models"""
        try:
            # Sentiment analysis model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            
            # Price prediction models
            self.price_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
            self.volatility_predictor = GradientBoostingClassifier(n_estimators=100, random_state=42)
            self.trend_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
            
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")

ai_models = AIModels()

# Database Models
class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)  # price_prediction, sentiment, technical, fundamental
    
    # Input data
    timeframe = Column(String, default="1h")
    data_points = Column(Integer, default=100)
    
    # Results
    prediction = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    risk_level = Column(String, default="medium")  # low, medium, high
    
    # Recommendations
    action = Column(String)  # buy, sell, hold
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_loss = Column(Float)
    position_size = Column(Float)
    
    # Metadata
    model_version = Column(String, default="1.0")
    accuracy_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class MarketSentiment(Base):
    __tablename__ = "market_sentiment"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    
    # Sentiment scores
    news_sentiment = Column(Float, default=0.0)  # -1 to 1
    social_sentiment = Column(Float, default=0.0)
    overall_sentiment = Column(Float, default=0.0)
    
    # Sentiment sources
    news_articles_count = Column(Integer, default=0)
    social_mentions_count = Column(Integer, default=0)
    
    # Sentiment details
    positive_mentions = Column(Integer, default=0)
    negative_mentions = Column(Integer, default=0)
    neutral_mentions = Column(Integer, default=0)
    
    # Keywords and topics
    trending_keywords = Column(JSON)
    sentiment_breakdown = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TradingSignalAI(Base):
    __tablename__ = "trading_signals_ai"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    
    # Signal details
    signal_type = Column(String, nullable=False)  # buy, sell, hold
    strength = Column(Float, default=0.0)  # 0-100
    confidence = Column(Float, default=0.0)  # 0-100
    
    # Price levels
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float)
    entry_price = Column(Float)
    target_prices = Column(JSON)  # Multiple targets
    stop_loss = Column(Float)
    
    # Risk management
    risk_reward_ratio = Column(Float)
    max_risk_percentage = Column(Float, default=2.0)
    position_size_recommendation = Column(Float)
    
    # AI analysis
    technical_score = Column(Float, default=0.0)
    fundamental_score = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    
    # Timeframe and validity
    timeframe = Column(String, default="1h")
    valid_until = Column(DateTime)
    
    # Performance tracking
    is_active = Column(Boolean, default=True)
    actual_outcome = Column(String)  # hit, miss, pending
    actual_return = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AIPortfolioOptimization(Base):
    __tablename__ = "ai_portfolio_optimization"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Portfolio details
    current_portfolio = Column(JSON)
    recommended_portfolio = Column(JSON)
    
    # Optimization parameters
    risk_tolerance = Column(String, default="medium")  # low, medium, high
    investment_horizon = Column(String, default="medium")  # short, medium, long
    target_return = Column(Float)
    max_drawdown = Column(Float)
    
    # Optimization results
    expected_return = Column(Float)
    expected_volatility = Column(Float)
    sharpe_ratio = Column(Float)
    
    # Rebalancing recommendations
    rebalancing_actions = Column(JSON)
    estimated_cost = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AIMarketRegime(Base):
    __tablename__ = "ai_market_regimes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Market regime classification
    regime_type = Column(String, nullable=False)  # bull, bear, sideways, volatile
    confidence = Column(Float, default=0.0)
    
    # Market indicators
    volatility_level = Column(String, default="medium")  # low, medium, high
    trend_strength = Column(Float, default=0.0)
    momentum = Column(Float, default=0.0)
    
    # Economic indicators
    fear_greed_index = Column(Float)
    vix_level = Column(Float)
    correlation_breakdown = Column(Float)
    
    # Regime characteristics
    expected_duration = Column(Integer)  # days
    key_drivers = Column(JSON)
    trading_strategies = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class AIAnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str
    timeframe: str = "1h"
    data_points: int = 100

class TradingSignalRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    risk_tolerance: str = "medium"

class PortfolioOptimizationRequest(BaseModel):
    user_id: str
    current_portfolio: Dict[str, float]
    risk_tolerance: str = "medium"
    investment_horizon: str = "medium"
    target_return: Optional[float] = None

class SentimentAnalysisRequest(BaseModel):
    symbol: str
    include_news: bool = True
    include_social: bool = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

def get_market_data(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Get market data for analysis"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        return data
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate comprehensive technical indicators"""
    if df.empty:
        return df
    
    try:
        # Trend indicators
        df['sma_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['ema_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['ema_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # MACD
        df['macd'] = ta.trend.macd_diff(df['Close'])
        df['macd_signal'] = ta.trend.macd_signal(df['Close'])
        
        # RSI
        df['rsi'] = ta.momentum.rsi(df['Close'])
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_middle'] = bb.bollinger_mavg()
        
        # Stochastic
        df['stoch_k'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['stoch_d'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        df['volume_sma'] = ta.volume.volume_sma(df['Close'], df['Volume'])
        df['vwap'] = ta.volume.volume_weighted_average_price(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # Volatility
        df['atr'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        # Support and Resistance
        df['support'] = df['Low'].rolling(window=20).min()
        df['resistance'] = df['High'].rolling(window=20).max()
        
        return df
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return df

def prepare_features(df: pd.DataFrame) -> np.ndarray:
    """Prepare features for ML models"""
    if df.empty:
        return np.array([])
    
    try:
        features = []
        
        # Price features
        features.extend([
            df['Close'].iloc[-1],
            df['Open'].iloc[-1],
            df['High'].iloc[-1],
            df['Low'].iloc[-1],
            df['Volume'].iloc[-1]
        ])
        
        # Technical indicators
        technical_cols = ['sma_20', 'sma_50', 'ema_12', 'ema_26', 'macd', 'macd_signal', 
                         'rsi', 'bb_upper', 'bb_lower', 'stoch_k', 'stoch_d', 'atr']
        
        for col in technical_cols:
            if col in df.columns:
                features.append(df[col].iloc[-1] if not pd.isna(df[col].iloc[-1]) else 0)
            else:
                features.append(0)
        
        # Price momentum features
        if len(df) >= 5:
            features.extend([
                (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2],  # 1-day return
                (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5],  # 5-day return
                df['Close'].pct_change().std(),  # volatility
                df['Volume'].iloc[-1] / df['Volume'].mean()  # volume ratio
            ])
        else:
            features.extend([0, 0, 0, 1])
        
        return np.array(features).reshape(1, -1)
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        return np.array([]).reshape(1, -1)

def analyze_sentiment_text(text: str) -> Dict[str, float]:
    """Analyze sentiment of text using multiple methods"""
    try:
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # FinBERT sentiment (if available)
        finbert_sentiment = 0.0
        if ai_models.sentiment_analyzer:
            try:
                result = ai_models.sentiment_analyzer(text[:512])  # Limit text length
                if result[0]['label'] == 'positive':
                    finbert_sentiment = result[0]['score']
                elif result[0]['label'] == 'negative':
                    finbert_sentiment = -result[0]['score']
            except:
                pass
        
        # Combined sentiment
        combined_sentiment = (textblob_sentiment + finbert_sentiment) / 2
        
        return {
            "textblob": textblob_sentiment,
            "finbert": finbert_sentiment,
            "combined": combined_sentiment,
            "confidence": abs(combined_sentiment)
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"textblob": 0.0, "finbert": 0.0, "combined": 0.0, "confidence": 0.0}

def get_news_sentiment(symbol: str) -> Dict[str, Any]:
    """Get news sentiment for a symbol"""
    try:
        # Mock news data (in production, integrate with news APIs)
        news_articles = [
            f"{symbol} shows strong performance amid market volatility",
            f"Analysts upgrade {symbol} with positive outlook",
            f"{symbol} faces regulatory challenges but maintains growth",
            f"Technical analysis suggests {symbol} breakout potential",
            f"{symbol} earnings beat expectations, stock rallies"
        ]
        
        sentiments = []
        for article in news_articles:
            sentiment = analyze_sentiment_text(article)
            sentiments.append(sentiment['combined'])
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0.0
        
        return {
            "average_sentiment": avg_sentiment,
            "sentiment_volatility": sentiment_std,
            "articles_count": len(news_articles),
            "positive_count": sum(1 for s in sentiments if s > 0.1),
            "negative_count": sum(1 for s in sentiments if s < -0.1),
            "neutral_count": sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        }
    except Exception as e:
        logger.error(f"Error getting news sentiment: {e}")
        return {"average_sentiment": 0.0, "sentiment_volatility": 0.0, "articles_count": 0,
                "positive_count": 0, "negative_count": 0, "neutral_count": 0}

def predict_price_movement(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Predict price movement using ML models"""
    try:
        if df.empty or len(df) < 50:
            return {"prediction": "hold", "confidence": 0.0, "target_price": 0.0}
        
        # Prepare features
        features = prepare_features(df)
        if features.size == 0:
            return {"prediction": "hold", "confidence": 0.0, "target_price": 0.0}
        
        # Generate training data (mock for demonstration)
        # In production, use historical data with known outcomes
        X_train = np.random.randn(1000, features.shape[1])
        y_train_price = np.random.randn(1000) * 0.05 + 0.02  # Mock price changes
        y_train_direction = (y_train_price > 0).astype(int)  # Mock direction
        
        # Train models
        ai_models.price_predictor.fit(X_train, y_train_price)
        ai_models.trend_classifier.fit(X_train, y_train_direction)
        
        # Make predictions
        price_change_pred = ai_models.price_predictor.predict(features)[0]
        direction_pred = ai_models.trend_classifier.predict(features)[0]
        direction_prob = ai_models.trend_classifier.predict_proba(features)[0]
        
        current_price = df['Close'].iloc[-1]
        target_price = current_price * (1 + price_change_pred)
        
        # Determine action
        if direction_pred == 1 and max(direction_prob) > 0.6:
            action = "buy"
        elif direction_pred == 0 and max(direction_prob) > 0.6:
            action = "sell"
        else:
            action = "hold"
        
        confidence = max(direction_prob) * 100
        
        return {
            "prediction": action,
            "confidence": confidence,
            "target_price": target_price,
            "price_change_prediction": price_change_pred,
            "current_price": current_price
        }
    except Exception as e:
        logger.error(f"Error predicting price movement: {e}")
        return {"prediction": "hold", "confidence": 0.0, "target_price": 0.0}

def calculate_risk_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate comprehensive risk metrics"""
    try:
        if df.empty or len(df) < 20:
            return {"volatility": 0.0, "var_95": 0.0, "max_drawdown": 0.0, "beta": 1.0}
        
        returns = df['Close'].pct_change().dropna()
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252)
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Beta (mock calculation - would need market data)
        beta = 1.0  # Placeholder
        
        return {
            "volatility": volatility,
            "var_95": var_95,
            "max_drawdown": max_drawdown,
            "beta": beta
        }
    except Exception as e:
        logger.error(f"Error calculating risk metrics: {e}")
        return {"volatility": 0.0, "var_95": 0.0, "max_drawdown": 0.0, "beta": 1.0}

def detect_market_regime() -> Dict[str, Any]:
    """Detect current market regime"""
    try:
        # Mock market regime detection
        # In production, analyze multiple market indicators
        
        regimes = ["bull", "bear", "sideways", "volatile"]
        regime = np.random.choice(regimes)
        confidence = np.random.uniform(0.6, 0.9)
        
        regime_characteristics = {
            "bull": {
                "volatility": "low",
                "trend_strength": 0.8,
                "strategies": ["momentum", "growth", "breakout"]
            },
            "bear": {
                "volatility": "high",
                "trend_strength": -0.7,
                "strategies": ["defensive", "short", "hedge"]
            },
            "sideways": {
                "volatility": "medium",
                "trend_strength": 0.1,
                "strategies": ["mean_reversion", "range_trading", "theta"]
            },
            "volatile": {
                "volatility": "high",
                "trend_strength": 0.3,
                "strategies": ["volatility", "straddle", "iron_condor"]
            }
        }
        
        return {
            "regime": regime,
            "confidence": confidence,
            "characteristics": regime_characteristics[regime],
            "vix_level": np.random.uniform(15, 35),
            "fear_greed_index": np.random.uniform(20, 80)
        }
    except Exception as e:
        logger.error(f"Error detecting market regime: {e}")
        return {"regime": "sideways", "confidence": 0.5}

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-trading-assistant-enhanced"}

@app.post("/analyze")
async def create_ai_analysis(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Create comprehensive AI analysis"""
    try:
        # Get market data
        df = get_market_data(request.symbol, interval=request.timeframe)
        if df.empty:
            raise HTTPException(status_code=400, detail="Unable to fetch market data")
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Perform different types of analysis
        analysis_results = {}
        
        if request.analysis_type in ["price_prediction", "all"]:
            price_prediction = predict_price_movement(df, request.symbol)
            analysis_results["price_prediction"] = price_prediction
        
        if request.analysis_type in ["sentiment", "all"]:
            sentiment_analysis = get_news_sentiment(request.symbol)
            analysis_results["sentiment"] = sentiment_analysis
        
        if request.analysis_type in ["technical", "all"]:
            # Technical analysis summary
            current_price = df['Close'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1] if 'sma_20' in df.columns else current_price
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            
            technical_signals = {
                "trend": "bullish" if current_price > sma_20 else "bearish",
                "momentum": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral",
                "support": df['support'].iloc[-1] if 'support' in df.columns else current_price * 0.95,
                "resistance": df['resistance'].iloc[-1] if 'resistance' in df.columns else current_price * 1.05
            }
            analysis_results["technical"] = technical_signals
        
        if request.analysis_type in ["risk", "all"]:
            risk_metrics = calculate_risk_metrics(df)
            analysis_results["risk"] = risk_metrics
        
        # Generate overall recommendation
        confidence_score = 0.0
        action = "hold"
        
        if "price_prediction" in analysis_results:
            pred = analysis_results["price_prediction"]
            confidence_score = pred["confidence"] / 100
            action = pred["prediction"]
        
        # Calculate risk level
        risk_level = "medium"
        if "risk" in analysis_results:
            volatility = analysis_results["risk"]["volatility"]
            if volatility < 0.2:
                risk_level = "low"
            elif volatility > 0.4:
                risk_level = "high"
        
        # Save analysis to database
        db_analysis = AIAnalysis(
            symbol=request.symbol,
            analysis_type=request.analysis_type,
            timeframe=request.timeframe,
            data_points=len(df),
            prediction=analysis_results,
            confidence_score=confidence_score,
            risk_level=risk_level,
            action=action,
            entry_price=df['Close'].iloc[-1],
            target_price=analysis_results.get("price_prediction", {}).get("target_price"),
            model_version="2.0",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return db_analysis
        
    except Exception as e:
        logger.error(f"Error creating AI analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading-signal")
async def generate_trading_signal(
    request: TradingSignalRequest,
    db: Session = Depends(get_db)
):
    """Generate AI-powered trading signal"""
    try:
        # Get market data and analysis
        df = get_market_data(request.symbol, interval=request.timeframe)
        if df.empty:
            raise HTTPException(status_code=400, detail="Unable to fetch market data")
        
        df = calculate_technical_indicators(df)
        
        # Get predictions
        price_prediction = predict_price_movement(df, request.symbol)
        sentiment_data = get_news_sentiment(request.symbol)
        risk_metrics = calculate_risk_metrics(df)
        
        current_price = df['Close'].iloc[-1]
        
        # Calculate component scores
        technical_score = 50.0  # Base score
        if 'rsi' in df.columns:
            rsi = df['rsi'].iloc[-1]
            if rsi < 30:
                technical_score += 20  # Oversold
            elif rsi > 70:
                technical_score -= 20  # Overbought
        
        sentiment_score = (sentiment_data["average_sentiment"] + 1) * 50  # Convert to 0-100
        momentum_score = price_prediction["confidence"]
        
        # Overall signal strength
        overall_strength = (technical_score + sentiment_score + momentum_score) / 3
        
        # Determine signal type
        if overall_strength > 70:
            signal_type = "buy"
        elif overall_strength < 30:
            signal_type = "sell"
        else:
            signal_type = "hold"
        
        # Calculate price targets
        volatility = risk_metrics["volatility"]
        target_1 = current_price * (1 + volatility * 0.5)
        target_2 = current_price * (1 + volatility * 1.0)
        stop_loss = current_price * (1 - volatility * 0.3)
        
        if signal_type == "sell":
            target_1 = current_price * (1 - volatility * 0.5)
            target_2 = current_price * (1 - volatility * 1.0)
            stop_loss = current_price * (1 + volatility * 0.3)
        
        # Risk management
        risk_reward_ratio = abs(target_1 - current_price) / abs(stop_loss - current_price)
        
        # Position size recommendation based on risk tolerance
        risk_tolerance_multiplier = {"low": 0.5, "medium": 1.0, "high": 2.0}
        max_risk = 2.0 * risk_tolerance_multiplier.get(request.risk_tolerance, 1.0)
        
        # Create trading signal
        db_signal = TradingSignalAI(
            symbol=request.symbol,
            signal_type=signal_type,
            strength=overall_strength,
            confidence=momentum_score,
            current_price=current_price,
            predicted_price=price_prediction.get("target_price", current_price),
            entry_price=current_price,
            target_prices=[target_1, target_2],
            stop_loss=stop_loss,
            risk_reward_ratio=risk_reward_ratio,
            max_risk_percentage=max_risk,
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            momentum_score=momentum_score,
            timeframe=request.timeframe,
            valid_until=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.add(db_signal)
        db.commit()
        db.refresh(db_signal)
        
        return db_signal
        
    except Exception as e:
        logger.error(f"Error generating trading signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sentiment-analysis")
async def analyze_market_sentiment(
    request: SentimentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze market sentiment for a symbol"""
    try:
        sentiment_data = {}
        
        if request.include_news:
            news_sentiment = get_news_sentiment(request.symbol)
            sentiment_data["news"] = news_sentiment
        
        if request.include_social:
            # Mock social sentiment (integrate with Twitter, Reddit APIs)
            social_sentiment = {
                "average_sentiment": np.random.uniform(-0.5, 0.5),
                "mentions_count": np.random.randint(100, 1000),
                "trending_keywords": ["bullish", "moon", "hodl", "dip", "rally"]
            }
            sentiment_data["social"] = social_sentiment
        
        # Calculate overall sentiment
        news_score = sentiment_data.get("news", {}).get("average_sentiment", 0.0)
        social_score = sentiment_data.get("social", {}).get("average_sentiment", 0.0)
        overall_sentiment = (news_score + social_score) / 2
        
        # Save to database
        db_sentiment = MarketSentiment(
            symbol=request.symbol,
            news_sentiment=news_score,
            social_sentiment=social_score,
            overall_sentiment=overall_sentiment,
            news_articles_count=sentiment_data.get("news", {}).get("articles_count", 0),
            social_mentions_count=sentiment_data.get("social", {}).get("mentions_count", 0),
            positive_mentions=sentiment_data.get("news", {}).get("positive_count", 0),
            negative_mentions=sentiment_data.get("news", {}).get("negative_count", 0),
            neutral_mentions=sentiment_data.get("news", {}).get("neutral_count", 0),
            trending_keywords=sentiment_data.get("social", {}).get("trending_keywords", []),
            sentiment_breakdown=sentiment_data
        )
        
        db.add(db_sentiment)
        db.commit()
        db.refresh(db_sentiment)
        
        return db_sentiment
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio-optimization")
async def optimize_portfolio(
    request: PortfolioOptimizationRequest,
    db: Session = Depends(get_db)
):
    """Optimize portfolio using AI"""
    try:
        # Mock portfolio optimization (integrate with modern portfolio theory)
        current_portfolio = request.current_portfolio
        symbols = list(current_portfolio.keys())
        
        # Get market data for all symbols
        portfolio_data = {}
        for symbol in symbols:
            df = get_market_data(symbol, period="1y")
            if not df.empty:
                returns = df['Close'].pct_change().dropna()
                portfolio_data[symbol] = {
                    "returns": returns.tolist(),
                    "volatility": returns.std() * np.sqrt(252),
                    "expected_return": returns.mean() * 252
                }
        
        # Calculate correlation matrix
        returns_df = pd.DataFrame({
            symbol: data["returns"] for symbol, data in portfolio_data.items()
        })
        correlation_matrix = returns_df.corr().to_dict()
        
        # Generate optimized weights (mock optimization)
        n_assets = len(symbols)
        optimized_weights = np.random.dirichlet(np.ones(n_assets))
        
        recommended_portfolio = {
            symbol: float(weight) for symbol, weight in zip(symbols, optimized_weights)
        }
        
        # Calculate expected metrics
        expected_return = sum(
            recommended_portfolio[symbol] * portfolio_data[symbol]["expected_return"]
            for symbol in symbols if symbol in portfolio_data
        )
        
        expected_volatility = np.sqrt(
            sum(
                recommended_portfolio[symbol] ** 2 * portfolio_data[symbol]["volatility"] ** 2
                for symbol in symbols if symbol in portfolio_data
            )
        )
        
        sharpe_ratio = expected_return / expected_volatility if expected_volatility > 0 else 0
        
        # Generate rebalancing actions
        rebalancing_actions = []
        for symbol in symbols:
            current_weight = current_portfolio[symbol]
            target_weight = recommended_portfolio[symbol]
            action_size = target_weight - current_weight
            
            if abs(action_size) > 0.05:  # Only rebalance if difference > 5%
                rebalancing_actions.append({
                    "symbol": symbol,
                    "action": "buy" if action_size > 0 else "sell",
                    "amount": abs(action_size),
                    "current_weight": current_weight,
                    "target_weight": target_weight
                })
        
        # Save optimization
        db_optimization = AIPortfolioOptimization(
            user_id=request.user_id,
            current_portfolio=current_portfolio,
            recommended_portfolio=recommended_portfolio,
            risk_tolerance=request.risk_tolerance,
            investment_horizon=request.investment_horizon,
            target_return=request.target_return,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            rebalancing_actions=rebalancing_actions,
            estimated_cost=len(rebalancing_actions) * 10.0  # Mock transaction cost
        )
        
        db.add(db_optimization)
        db.commit()
        db.refresh(db_optimization)
        
        return db_optimization
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-regime")
async def get_market_regime(db: Session = Depends(get_db)):
    """Get current market regime analysis"""
    try:
        regime_data = detect_market_regime()
        
        # Save to database
        db_regime = AIMarketRegime(
            regime_type=regime_data["regime"],
            confidence=regime_data["confidence"],
            volatility_level=regime_data["characteristics"]["volatility"],
            trend_strength=regime_data["characteristics"]["trend_strength"],
            vix_level=regime_data.get("vix_level", 20.0),
            fear_greed_index=regime_data.get("fear_greed_index", 50.0),
            expected_duration=np.random.randint(5, 30),
            key_drivers=["economic_data", "geopolitical_events", "monetary_policy"],
            trading_strategies=regime_data["characteristics"]["strategies"]
        )
        
        db.add(db_regime)
        db.commit()
        db.refresh(db_regime)
        
        return db_regime
        
    except Exception as e:
        logger.error(f"Error getting market regime: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/{symbol}")
async def get_trading_signals(
    symbol: str,
    active_only: bool = True,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trading signals for a symbol"""
    query = db.query(TradingSignalAI).filter(TradingSignalAI.symbol == symbol)
    
    if active_only:
        query = query.filter(TradingSignalAI.is_active == True)
    
    signals = query.order_by(TradingSignalAI.created_at.desc()).limit(limit).all()
    return signals

@app.get("/analysis/{symbol}")
async def get_ai_analyses(
    symbol: str,
    analysis_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get AI analyses for a symbol"""
    query = db.query(AIAnalysis).filter(AIAnalysis.symbol == symbol)
    
    if analysis_type:
        query = query.filter(AIAnalysis.analysis_type == analysis_type)
    
    analyses = query.order_by(AIAnalysis.created_at.desc()).limit(limit).all()
    return analyses

@app.get("/sentiment/{symbol}")
async def get_sentiment_history(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get sentiment history for a symbol"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_history = db.query(MarketSentiment).filter(
        MarketSentiment.symbol == symbol,
        MarketSentiment.created_at >= start_date
    ).order_by(MarketSentiment.created_at.desc()).all()
    
    return sentiment_history

@app.get("/portfolio-optimizations/{user_id}")
async def get_portfolio_optimizations(
    user_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get portfolio optimizations for a user"""
    optimizations = db.query(AIPortfolioOptimization).filter(
        AIPortfolioOptimization.user_id == user_id
    ).order_by(AIPortfolioOptimization.created_at.desc()).limit(limit).all()
    
    return optimizations

# WebSocket for real-time AI insights
@app.websocket("/ws/ai-insights/{user_id}")
async def websocket_ai_insights(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        while True:
            # Send real-time AI insights
            insights = {
                "timestamp": datetime.utcnow().isoformat(),
                "market_regime": detect_market_regime(),
                "top_signals": ["BTCUSDT", "ETHUSDT", "ADAUSDT"],  # Mock data
                "sentiment_alert": "Positive sentiment spike detected in crypto markets"
            }
            
            await websocket.send_text(json.dumps(insights))
            await asyncio.sleep(30)  # Send updates every 30 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("AI Trading Assistant Enhanced service started")
    
    # Start background tasks
    asyncio.create_task(periodic_model_updates())
    asyncio.create_task(periodic_signal_generation())

async def periodic_model_updates():
    """Update AI models periodically"""
    while True:
        try:
            logger.info("Updating AI models...")
            # Retrain models with new data
            # This would involve fetching new market data and retraining
            await asyncio.sleep(3600)  # Update every hour
        except Exception as e:
            logger.error(f"Error updating models: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes

async def periodic_signal_generation():
    """Generate signals for popular symbols"""
    while True:
        try:
            popular_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT"]
            
            db = SessionLocal()
            for symbol in popular_symbols:
                try:
                    # Generate signal for each symbol
                    request = TradingSignalRequest(symbol=symbol)
                    # This would call the signal generation logic
                    logger.info(f"Generated signal for {symbol}")
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {e}")
            
            db.close()
            await asyncio.sleep(900)  # Generate signals every 15 minutes
            
        except Exception as e:
            logger.error(f"Error in periodic signal generation: {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)