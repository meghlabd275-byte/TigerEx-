"""
Enhanced ML System for Market Maker Bot
Deep Learning, Reinforcement Learning, and Advanced Predictive Models
"""

import asyncio
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import gym
from gym import spaces
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import aiohttp
import requests
from textblob import TextBlob
import ta
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    symbol: str
    prediction: float
    confidence: float
    timestamp: datetime
    model_type: str
    features_used: List[str]

class MarketEnvironment(gym.Env):
    """Custom Gym environment for reinforcement learning market making"""
    
    def __init__(self, data: pd.DataFrame, initial_balance: float = 100000):
        super().__init__()
        
        self.data = data
        self.initial_balance = initial_balance
        self.current_step = 0
        self.balance = initial_balance
        self.position = 0
        self.position_value = 0
        self.total_pnl = 0
        
        # Action space: 0=hold, 1=buy, 2=sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: price, volume, indicators, portfolio state
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(20,), dtype=np.float32
        )
        
    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0
        self.position_value = 0
        self.total_pnl = 0
        return self._get_observation()
    
    def step(self, action):
        # Execute action
        current_price = self.data.iloc[self.current_step]['close']
        
        if action == 1:  # Buy
            if self.balance > current_price:
                self.position += 1
                self.balance -= current_price
                self.position_value += current_price
        elif action == 2:  # Sell
            if self.position > 0:
                self.position -= 1
                self.balance += current_price
                self.position_value -= current_price
        
        # Calculate reward
        new_price = self.data.iloc[self.current_step + 1]['close']
        if self.position > 0:
            reward = (new_price - current_price) * self.position
        else:
            reward = 0
        
        # Update step
        self.current_step += 1
        
        # Check if done
        done = self.current_step >= len(self.data) - 1
        
        return self._get_observation(), reward, done, {}
    
    def _get_observation(self):
        if self.current_step >= len(self.data):
            return np.zeros(20)
        
        row = self.data.iloc[self.current_step]
        
        # Features: price, volume, technical indicators, portfolio state
        obs = np.array([
            row.get('close', 0) / 100000,  # Normalized price
            row.get('volume', 0) / 1000000,  # Normalized volume
            row.get('rsi', 50) / 100,  # Normalized RSI
            row.get('macd', 0) / 100,  # Normalized MACD
            row.get('bb_upper', 0) / 100000,  # Normalized Bollinger Bands
            row.get('bb_lower', 0) / 100000,
            row.get('ema_20', 0) / 100000,  # Normalized EMA
            row.get('sma_50', 0) / 100000,
            self.position / 100,  # Position size
            self.balance / self.initial_balance,  # Balance ratio
            self.position_value / self.initial_balance,  # Position value ratio
            self.total_pnl / self.initial_balance,  # PnL ratio
            row.get('high', 0) / 100000,  # High
            row.get('low', 0) / 100000,  # Low
            row.get('open', 0) / 100000,  # Open
            (row.get('close', 0) - row.get('open', 0)) / row.get('open', 1),  # Price change
            row.get('volume_sma', 0) / 1000000,  # Volume SMA
            row.get('atr', 0) / 100,  # ATR
            self.current_step / len(self.data)  # Progress
        ], dtype=np.float32)
        
        return obs

class DeepLSTM(nn.Module):
    """Deep LSTM network for price prediction"""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int):
        super(DeepLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm1 = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.lstm2 = nn.LSTM(hidden_size, hidden_size // 2, num_layers, batch_first=True, dropout=0.2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size // 2, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM layers
        out, _ = self.lstm1(x)
        out, _ = self.lstm2(out)
        
        # Take the last output
        out = out[:, -1, :]
        
        # Fully connected layers
        out = self.dropout(out)
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.relu(self.fc2(out))
        out = self.fc3(out)
        
        return out

class ReinforcementLearningAgent:
    """Deep Q-Learning agent for market making"""
    
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 32
        
        # Neural network
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
    def _build_model(self):
        model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, self.action_size)
        )
        return model
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > 10000:
            self.memory.pop(0)
    
    def act(self, state):
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        act_values = self.model(state_tensor)
        return np.argmax(act_values.cpu().data.numpy())
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)
                target = reward + self.gamma * np.amax(
                    self.target_model(next_state_tensor).cpu().data.numpy()
                )
            
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            target_f = self.model(state_tensor)
            target_f[0][action] = target
            
            # Train the model
            self.optimizer.zero_grad()
            loss = nn.MSELoss()(self.model(state_tensor), target_f)
            loss.backward()
            self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class SentimentAnalyzer:
    """Sentiment analysis for market prediction"""
    
    def __init__(self):
        # Initialize sentiment analysis pipeline
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        # Financial news sentiment model
        self.finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    
    async def analyze_news_sentiment(self, news_articles: List[Dict]) -> float:
        """Analyze sentiment from news articles"""
        sentiments = []
        
        for article in news_articles:
            text = article.get('title', '') + ' ' + article.get('description', '')
            
            # Use general sentiment analyzer
            result = self.sentiment_pipeline(text[:512])  # Limit length
            sentiment_score = result[0]['score'] if result[0]['label'] == 'POSITIVE' else -result[0]['score']
            sentiments.append(sentiment_score)
        
        return np.mean(sentiments) if sentiments else 0.0
    
    async def analyze_social_sentiment(self, social_posts: List[str]) -> float:
        """Analyze sentiment from social media posts"""
        sentiments = []
        
        for post in social_posts:
            # TextBlob sentiment
            blob = TextBlob(post)
            sentiment = blob.sentiment.polarity
            sentiments.append(sentiment)
        
        return np.mean(sentiments) if sentiments else 0.0
    
    def analyze_financial_text(self, text: str) -> float:
        """Analyze financial text using FinBERT"""
        inputs = self.finbert_tokenizer(text[:512], return_tensors="pt", truncation=True)
        
        with torch.no_grad():
            outputs = self.finbert_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Map to sentiment score (positive - negative)
        positive_score = predictions[0][2].item()  # positive
        negative_score = predictions[0][0].item()  # negative
        
        return positive_score - negative_score

class AnomalyDetector:
    """Anomaly detection for market data"""
    
    def __init__(self):
        self.models = {}
    
    def fit(self, data: pd.DataFrame, symbol: str):
        """Fit anomaly detection model for a symbol"""
        # Use Isolation Forest for anomaly detection
        from sklearn.ensemble import IsolationForest
        
        features = ['close', 'volume', 'high', 'low']
        X = data[features].values
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        self.models[symbol] = model
    
    def predict(self, data: pd.DataFrame, symbol: str) -> np.ndarray:
        """Predict anomalies for a symbol"""
        if symbol not in self.models:
            return np.zeros(len(data))
        
        model = self.models[symbol]
        features = ['close', 'volume', 'high', 'low']
        X = data[features].values
        
        predictions = model.predict(X)
        # Convert to anomaly scores (1 = normal, -1 = anomaly)
        return (predictions == -1).astype(int)

class EnhancedMLSystem:
    """Complete ML system for market making"""
    
    def __init__(self):
        self.price_models = {}
        self.rl_agents = {}
        self.sentiment_analyzer = SentimentAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.scalers = {}
        self.feature_engineer = FeatureEngineer()
        
    async def initialize(self):
        """Initialize the ML system"""
        logger.info("Initializing Enhanced ML System")
        
        # Load pre-trained models or train new ones
        await self.load_or_train_models()
        
        logger.info("Enhanced ML System initialized")
    
    async def load_or_train_models(self):
        """Load existing models or train new ones"""
        # This would typically load from disk or train with historical data
        logger.info("Loading/Training ML models")
    
    async def predict_price(self, symbol: str, data: pd.DataFrame, 
                          horizon: int = 1) -> PredictionResult:
        """Predict future price using deep learning"""
        try:
            if symbol not in self.price_models:
                # Create and train model for symbol
                model = self._create_price_model(data)
                self.price_models[symbol] = model
                self.scalers[symbol] = MinMaxScaler()
            else:
                model = self.price_models[symbol]
            
            # Prepare features
            features = self.feature_engineer.create_features(data)
            
            # Scale features
            scaled_features = self.scalers[symbol].fit_transform(features)
            
            # Make prediction
            prediction = await self._predict_with_model(model, scaled_features, horizon)
            
            # Calculate confidence
            confidence = self._calculate_confidence(model, scaled_features)
            
            return PredictionResult(
                symbol=symbol,
                prediction=prediction,
                confidence=confidence,
                timestamp=datetime.now(),
                model_type="DeepLSTM",
                features_used=features.columns.tolist()
            )
            
        except Exception as e:
            logger.error(f"Error predicting price for {symbol}: {e}")
            return PredictionResult(
                symbol=symbol,
                prediction=0.0,
                confidence=0.0,
                timestamp=datetime.now(),
                model_type="DeepLSTM",
                features_used=[]
            )
    
    def _create_price_model(self, data: pd.DataFrame):
        """Create deep learning model for price prediction"""
        input_size = 20  # Number of features
        hidden_size = 128
        num_layers = 3
        output_size = 1
        
        model = DeepLSTM(input_size, hidden_size, num_layers, output_size)
        return model
    
    async def _predict_with_model(self, model, features, horizon):
        """Make prediction with model"""
        # Convert to tensor
        features_tensor = torch.FloatTensor(features).unsqueeze(0)
        
        with torch.no_grad():
            prediction = model(features_tensor)
        
        return prediction.item()
    
    def _calculate_confidence(self, model, features):
        """Calculate prediction confidence"""
        # Simple confidence based on model consistency
        # In practice, this would use ensemble methods or Bayesian approaches
        return min(0.95, max(0.5, 1.0 - np.std(features) / np.mean(features)))
    
    async def train_reinforcement_agent(self, symbol: str, historical_data: pd.DataFrame):
        """Train reinforcement learning agent"""
        try:
            # Create environment
            env = MarketEnvironment(historical_data)
            
            # Create agent
            state_size = env.observation_space.shape[0]
            action_size = env.action_space.n
            agent = ReinforcementLearningAgent(state_size, action_size)
            
            # Training parameters
            episodes = 1000
            batch_size = 32
            
            for episode in range(episodes):
                state = env.reset()
                total_reward = 0
                
                for step in range(len(historical_data) - 1):
                    # Choose action
                    action = agent.act(state)
                    
                    # Take action
                    next_state, reward, done, _ = env.step(action)
                    
                    # Remember experience
                    agent.remember(state, action, reward, next_state, done)
                    
                    state = next_state
                    total_reward += reward
                    
                    if done:
                        break
                
                # Train agent
                if len(agent.memory) > batch_size:
                    agent.replay()
                
                # Update target model
                if episode % 10 == 0:
                    agent.update_target_model()
                
                if episode % 100 == 0:
                    logger.info(f"Episode {episode}, Total Reward: {total_reward}")
            
            self.rl_agents[symbol] = agent
            logger.info(f"Training completed for {symbol}")
            
        except Exception as e:
            logger.error(f"Error training RL agent for {symbol}: {e}")
    
    async def get_market_sentiment(self, symbol: str) -> float:
        """Get market sentiment for a symbol"""
        try:
            # Fetch news (in practice, use real news API)
            news_articles = await self._fetch_news(symbol)
            
            # Fetch social media posts (in practice, use Twitter API, etc.)
            social_posts = await self._fetch_social_posts(symbol)
            
            # Analyze sentiment
            news_sentiment = await self.sentiment_analyzer.analyze_news_sentiment(news_articles)
            social_sentiment = await self.sentiment_analyzer.analyze_social_sentiment(social_posts)
            
            # Combine sentiments
            combined_sentiment = 0.6 * news_sentiment + 0.4 * social_sentiment
            
            return combined_sentiment
            
        except Exception as e:
            logger.error(f"Error getting market sentiment for {symbol}: {e}")
            return 0.0
    
    async def _fetch_news(self, symbol: str) -> List[Dict]:
        """Fetch news articles for symbol"""
        # Mock data - in practice, use news API
        return [
            {"title": f"Positive news for {symbol}", "description": "Company reports strong earnings"},
            {"title": f"Market update for {symbol}", "description": "Analysts maintain buy rating"}
        ]
    
    async def _fetch_social_posts(self, symbol: str) -> List[str]:
        """Fetch social media posts for symbol"""
        # Mock data - in practice, use Twitter API, Reddit API, etc.
        return [
            f"Bullish on {symbol} today!",
            f"{symbol} looking strong for next week",
            f"Watching {symbol} closely"
        ]
    
    async def detect_anomalies(self, symbol: str, data: pd.DataFrame) -> np.ndarray:
        """Detect anomalies in market data"""
        try:
            if symbol not in self.anomaly_detector.models:
                self.anomaly_detector.fit(data, symbol)
            
            return self.anomaly_detector.predict(data, symbol)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for {symbol}: {e}")
            return np.zeros(len(data))
    
    async def get_trading_signals(self, symbol: str, data: pd.DataFrame) -> Dict[str, float]:
        """Get comprehensive trading signals"""
        try:
            # Price prediction
            price_prediction = await self.predict_price(symbol, data)
            
            # Market sentiment
            sentiment = await self.get_market_sentiment(symbol)
            
            # Anomaly detection
            anomalies = await self.detect_anomalies(symbol, data)
            anomaly_score = np.mean(anomalies[-10:])  # Recent anomaly score
            
            # Technical indicators
            technical_signals = self._get_technical_signals(data)
            
            # Combine signals
            signals = {
                'price_prediction': price_prediction.prediction,
                'price_confidence': price_prediction.confidence,
                'sentiment': sentiment,
                'anomaly_score': anomaly_score,
                'rsi': technical_signals['rsi'],
                'macd': technical_signals['macd'],
                'bb_position': technical_signals['bb_position'],
                'volume_ratio': technical_signals['volume_ratio']
            }
            
            # Calculate overall signal
            signals['overall'] = self._calculate_overall_signal(signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting trading signals for {symbol}: {e}")
            return {'overall': 0.0}
    
    def _get_technical_signals(self, data: pd.DataFrame) -> Dict[str, float]:
        """Get technical analysis signals"""
        try:
            # RSI
            rsi = ta.momentum.rsi(data['close'], window=14)
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # MACD
            macd_line = ta.trend.macd(data['close'])
            macd_signal = ta.trend.macd_signal(data['close'])
            current_macd = macd_line.iloc[-1] - macd_signal.iloc[-1] if not macd_line.empty else 0
            
            # Bollinger Bands
            bb_upper = ta.volatility.bollinger_hband(data['close'])
            bb_lower = ta.volatility.bollinger_lband(data['close'])
            current_price = data['close'].iloc[-1]
            bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]) if not bb_upper.empty else 0.5
            
            # Volume ratio
            volume_sma = ta.volume.sma_volume(data['close'], window=20)
            volume_ratio = data['volume'].iloc[-1] / volume_sma.iloc[-1] if not volume_sma.empty else 1.0
            
            return {
                'rsi': current_rsi / 100,  # Normalized
                'macd': current_macd / 100,  # Normalized
                'bb_position': bb_position,
                'volume_ratio': min(volume_ratio / 2, 1.0)  # Normalized
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical signals: {e}")
            return {'rsi': 0.5, 'macd': 0.0, 'bb_position': 0.5, 'volume_ratio': 1.0}
    
    def _calculate_overall_signal(self, signals: Dict[str, float]) -> float:
        """Calculate overall trading signal"""
        weights = {
            'price_prediction': 0.3,
            'sentiment': 0.2,
            'rsi': 0.15,
            'macd': 0.1,
            'bb_position': 0.1,
            'volume_ratio': 0.1,
            'anomaly_score': -0.05  # Negative weight for anomalies
        }
        
        overall = 0.0
        for signal, weight in weights.items():
            if signal in signals:
                # Normalize signals to [-1, 1] range where appropriate
                if signal == 'rsi':
                    normalized_signal = (signals[signal] - 0.5) * 2  # Convert from [0,1] to [-1,1]
                elif signal == 'bb_position':
                    normalized_signal = (signals[signal] - 0.5) * 2
                elif signal == 'volume_ratio':
                    normalized_signal = min((signals[signal] - 1) / 2, 1)  # Volume > average is positive
                else:
                    normalized_signal = signals[signal]
                
                overall += normalized_signal * weight
        
        return np.clip(overall, -1.0, 1.0)

class FeatureEngineer:
    """Feature engineering for ML models"""
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML models"""
        features = data.copy()
        
        # Price-based features
        features['price_change'] = data['close'].pct_change()
        features['price_change_5'] = data['close'].pct_change(5)
        features['price_change_10'] = data['close'].pct_change(10)
        
        # Volume features
        features['volume_ratio'] = data['volume'] / data['volume'].rolling(20).mean()
        features['volume_change'] = data['volume'].pct_change()
        
        # Technical indicators
        features['rsi'] = ta.momentum.rsi(data['close'], window=14)
        features['macd'] = ta.trend.macd(data['close'])
        features['bb_upper'] = ta.volatility.bollinger_hband(data['close'])
        features['bb_lower'] = ta.volatility.bollinger_lband(data['close'])
        features['ema_20'] = ta.trend.ema_indicator(data['close'], window=20)
        features['sma_50'] = ta.trend.sma_indicator(data['close'], window=50)
        features['atr'] = ta.volatility.average_true_range(data['close'], data['high'], data['low'])
        
        # Lag features
        for lag in [1, 2, 3, 5, 10]:
            features[f'close_lag_{lag}'] = data['close'].shift(lag)
            features[f'volume_lag_{lag}'] = data['volume'].shift(lag)
        
        # Rolling statistics
        features['rolling_mean_5'] = data['close'].rolling(5).mean()
        features['rolling_std_5'] = data['close'].rolling(5).std()
        features['rolling_mean_20'] = data['close'].rolling(20).mean()
        features['rolling_std_20'] = data['close'].rolling(20).std()
        
        return features.fillna(0)

# Initialize and run the system
async def main():
    ml_system = EnhancedMLSystem()
    await ml_system.initialize()
    
    logger.info("Enhanced ML System is running")
    
    # Keep the system running
    while True:
        await asyncio.sleep(60)  # Update every minute

if __name__ == "__main__":
    asyncio.run(main())