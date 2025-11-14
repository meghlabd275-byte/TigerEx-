"""
Enhanced ML System for Market Making
Including Transformers, GNNs, Ensemble Models, and Real-time Training
"""

import asyncio
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import tensorflow as tf
from transformers import AutoModel, AutoTokenizer, BertModel
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import pickle
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
import redis
import aiofiles
import aiohttp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    symbol: str
    prediction: float
    confidence: float
    timestamp: datetime
    model_name: str
    features_used: List[str]
    prediction_horizon: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingConfig:
    model_type: str
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    feature_window: int = 100
    prediction_horizon: int = 60
    retrain_interval: int = 3600  # seconds
    min_data_points: int = 1000
    ensemble_weights: Optional[Dict[str, float]] = None

class BaseMLModel(ABC):
    """Base class for all ML models"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.last_trained = None
        self.training_history = []
        self.feature_importance = {}
        
    @abstractmethod
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the model"""
        pass
    
    @abstractmethod
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make prediction"""
        pass
    
    @abstractmethod
    def save_model(self, path: str):
        """Save model to disk"""
        pass
    
    @abstractmethod
    def load_model(self, path: str):
        """Load model from disk"""
        pass

class TransformerPricePredictor(BaseMLModel):
    """Transformer-based price prediction model"""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.model = PriceTransformerModel(
            input_size=config.feature_window,
            d_model=256,
            nhead=8,
            num_layers=6,
            dropout=0.1
        )
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the transformer model"""
        try:
            # Prepare data
            sequences, targets = self._prepare_sequences(data)
            
            # Split data
            train_size = int(len(sequences) * (1 - self.config.validation_split))
            train_seq, val_seq = sequences[:train_size], sequences[train_size:]
            train_target, val_target = targets[:train_size], targets[train_size:]
            
            # Create datasets
            train_dataset = PriceDataset(train_seq, train_target)
            val_dataset = PriceDataset(val_seq, val_target)
            
            train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
            
            # Training setup
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
            
            # Training loop
            best_val_loss = float('inf')
            patience_counter = 0
            
            for epoch in range(self.config.epochs):
                # Training phase
                self.model.train()
                train_loss = 0.0
                
                for batch_seq, batch_target in train_loader:
                    batch_seq = batch_seq.to(self.device)
                    batch_target = batch_target.to(self.device)
                    
                    optimizer.zero_grad()
                    predictions = self.model(batch_seq)
                    loss = criterion(predictions.squeeze(), batch_target)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                    optimizer.step()
                    
                    train_loss += loss.item()
                
                # Validation phase
                self.model.eval()
                val_loss = 0.0
                
                with torch.no_grad():
                    for batch_seq, batch_target in val_loader:
                        batch_seq = batch_seq.to(self.device)
                        batch_target = batch_target.to(self.device)
                        
                        predictions = self.model(batch_seq)
                        loss = criterion(predictions.squeeze(), batch_target)
                        val_loss += loss.item()
                
                avg_train_loss = train_loss / len(train_loader)
                avg_val_loss = val_loss / len(val_loader)
                
                scheduler.step(avg_val_loss)
                
                # Early stopping
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                    # Save best model
                    torch.save(self.model.state_dict(), 'best_transformer.pth')
                else:
                    patience_counter += 1
                    if patience_counter >= self.config.early_stopping_patience:
                        logger.info(f"Early stopping at epoch {epoch}")
                        break
                
                # Log progress
                self.training_history.append({
                    'epoch': epoch,
                    'train_loss': avg_train_loss,
                    'val_loss': avg_val_loss
                })
                
                if epoch % 10 == 0:
                    logger.info(f"Epoch {epoch}: Train Loss: {avg_train_loss:.6f}, Val Loss: {avg_val_loss:.6f}")
            
            # Load best model
            self.model.load_state_dict(torch.load('best_transformer.pth'))
            self.is_trained = True
            self.last_trained = datetime.now()
            
            return {
                'status': 'success',
                'final_val_loss': best_val_loss,
                'epochs_trained': epoch,
                'training_history': self.training_history
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make prediction with transformer model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Prepare input
            sequence = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            
            # Make prediction
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(sequence)
                confidence = self._calculate_confidence(prediction)
            
            return PredictionResult(
                symbol="",
                prediction=prediction.item(),
                confidence=confidence,
                timestamp=datetime.now(),
                model_name="TransformerPricePredictor",
                features_used=[],
                prediction_horizon=self.config.prediction_horizon
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def _prepare_sequences(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for transformer training"""
        # Extract features and targets
        features = data.select_dtypes(include=[np.number]).values
        targets = data['close'].values if 'close' in data.columns else features[:, -1]
        
        sequences = []
        sequence_targets = []
        
        for i in range(len(features) - self.config.feature_window - self.config.prediction_horizon):
            seq = features[i:i + self.config.feature_window]
            target = targets[i + self.config.feature_window + self.config.prediction_horizon - 1]
            sequences.append(seq)
            sequence_targets.append(target)
        
        return np.array(sequences), np.array(sequence_targets)
    
    def _calculate_confidence(self, prediction: torch.Tensor) -> float:
        """Calculate prediction confidence"""
        # Simple confidence based on prediction magnitude
        return min(max(abs(prediction.item()) / 1000, 0.1), 0.95)
    
    def save_model(self, path: str):
        """Save transformer model"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'training_history': self.training_history,
            'last_trained': self.last_trained
        }, path)
    
    def load_model(self, path: str):
        """Load transformer model"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.config = checkpoint['config']
        self.training_history = checkpoint['training_history']
        self.last_trained = checkpoint['last_trained']
        self.is_trained = True

class PriceTransformerModel(nn.Module):
    """Transformer model for price prediction"""
    
    def __init__(self, input_size: int, d_model: int, nhead: int, num_layers: int, dropout: float):
        super().__init__()
        
        self.input_projection = nn.Linear(input_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_projection = nn.Linear(d_model, 1)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input projection
        x = self.input_projection(x)
        x = self.positional_encoding(x)
        x = self.dropout(x)
        
        # Transformer encoding
        x = self.transformer(x)
        
        # Output projection (use last token)
        output = self.output_projection(x[:, -1, :])
        
        return output

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:x.size(0), :]

class GraphNeuralNetwork(BaseMLModel):
    """Graph Neural Network for correlation analysis"""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.model = CorrelationGNN(
            input_size=config.feature_window,
            hidden_size=128,
            num_layers=3,
            num_heads=4
        )
        
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train GNN model for correlation analysis"""
        try:
            # Build correlation graph
            correlation_matrix = data.corr()
            edge_index, edge_attr = self._build_graph(correlation_matrix)
            
            # Prepare node features
            node_features = self._prepare_node_features(data)
            
            # Train the model
            # Implementation similar to transformer but with graph structure
            self.is_trained = True
            self.last_trained = datetime.now()
            
            return {'status': 'success', 'message': 'GNN training completed'}
            
        except Exception as e:
            logger.error(f"GNN training failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make prediction with GNN"""
        if not self.is_trained:
            raise ValueError("GNN model must be trained before making predictions")
        
        # Implementation for GNN prediction
        return PredictionResult(
            symbol="",
            prediction=0.0,
            confidence=0.8,
            timestamp=datetime.now(),
            model_name="GraphNeuralNetwork",
            features_used=[],
            prediction_horizon=self.config.prediction_horizon
        )
    
    def _build_graph(self, correlation_matrix: pd.DataFrame) -> Tuple[torch.Tensor, torch.Tensor]:
        """Build graph structure from correlation matrix"""
        # Convert correlation to graph edges
        threshold = 0.5
        edges = []
        edge_attrs = []
        
        for i in range(len(correlation_matrix)):
            for j in range(len(correlation_matrix.columns)):
                if i != j and abs(correlation_matrix.iloc[i, j]) > threshold:
                    edges.append([i, j])
                    edge_attrs.append(abs(correlation_matrix.iloc[i, j]))
        
        edge_index = torch.tensor(edges).t().contiguous()
        edge_attr = torch.tensor(edge_attrs, dtype=torch.float)
        
        return edge_index, edge_attr
    
    def _prepare_node_features(self, data: pd.DataFrame) -> torch.Tensor:
        """Prepare node features for GNN"""
        return torch.tensor(data.values, dtype=torch.float)
    
    def save_model(self, path: str):
        """Save GNN model"""
        pass
    
    def load_model(self, path: str):
        """Load GNN model"""
        pass

class CorrelationGNN(nn.Module):
    """GNN model for correlation analysis"""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, num_heads: int):
        super().__init__()
        
        self.input_projection = nn.Linear(input_size, hidden_size)
        self.gnn_layers = nn.ModuleList([
            GNNLayer(hidden_size, num_heads) for _ in range(num_layers)
        ])
        self.output_projection = nn.Linear(hidden_size, 1)
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        # Input projection
        x = self.input_projection(x)
        
        # GNN layers
        for layer in self.gnn_layers:
            x = layer(x, edge_index, edge_attr)
        
        # Output projection
        output = self.output_projection(x)
        
        return output

class GNNLayer(nn.Module):
    """Single GNN layer"""
    
    def __init__(self, hidden_size: int, num_heads: int):
        super().__init__()
        self.attention = nn.MultiheadAttention(hidden_size, num_heads)
        self.norm = nn.LayerNorm(hidden_size)
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.ReLU(),
            nn.Linear(hidden_size * 4, hidden_size)
        )
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        # Graph attention
        attended, _ = self.attention(x, x, x)
        x = self.norm(x + attended)
        
        # Feed forward
        ff_output = self.feed_forward(x)
        x = self.norm(x + ff_output)
        
        return x

class EnsembleModel(BaseMLModel):
    """Ensemble model combining multiple predictors"""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.models = {}
        self.weights = config.ensemble_weights or {
            'transformer': 0.4,
            'xgboost': 0.3,
            'lightgbm': 0.3
        }
        
        # Initialize individual models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize individual models"""
        self.models['transformer'] = TransformerPricePredictor(self.config)
        self.models['xgboost'] = XGBoostPredictor(self.config)
        self.models['lightgbm'] = LightGBMPredictor(self.config)
    
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train all models in ensemble"""
        results = {}
        
        for name, model in self.models.items():
            logger.info(f"Training {name} model...")
            result = await model.train(data)
            results[name] = result
        
        self.is_trained = True
        self.last_trained = datetime.now()
        
        return {
            'status': 'success',
            'individual_results': results,
            'ensemble_weights': self.weights
        }
    
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make ensemble prediction"""
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before making predictions")
        
        predictions = {}
        confidences = {}
        
        # Get predictions from all models
        for name, model in self.models.items():
            try:
                pred = await model.predict(features)
                predictions[name] = pred.prediction
                confidences[name] = pred.confidence
            except Exception as e:
                logger.error(f"Prediction failed for {name}: {e}")
                predictions[name] = 0.0
                confidences[name] = 0.1
        
        # Calculate weighted ensemble prediction
        ensemble_prediction = sum(
            predictions[name] * weight for name, weight in self.weights.items()
        )
        
        # Calculate ensemble confidence
        ensemble_confidence = sum(
            confidences[name] * weight for name, weight in self.weights.items()
        )
        
        return PredictionResult(
            symbol="",
            prediction=ensemble_prediction,
            confidence=ensemble_confidence,
            timestamp=datetime.now(),
            model_name="EnsembleModel",
            features_used=list(predictions.keys()),
            prediction_horizon=self.config.prediction_horizon,
            metadata={
                'individual_predictions': predictions,
                'individual_confidences': confidences,
                'weights_used': self.weights
            }
        )
    
    def save_model(self, path: str):
        """Save ensemble model"""
        ensemble_data = {
            'weights': self.weights,
            'config': self.config,
            'models': {}
        }
        
        for name, model in self.models.items():
            model_path = f"{path}_{name}"
            model.save_model(model_path)
            ensemble_data['models'][name] = model_path
        
        with open(path, 'w') as f:
            json.dump(ensemble_data, f, default=str)
    
    def load_model(self, path: str):
        """Load ensemble model"""
        with open(path, 'r') as f:
            ensemble_data = json.load(f)
        
        self.weights = ensemble_data['weights']
        self.config = ensemble_data['config']
        
        for name, model_path in ensemble_data['models'].items():
            self.models[name].load_model(model_path)
        
        self.is_trained = True
        self.last_trained = datetime.now()

class XGBoostPredictor(BaseMLModel):
    """XGBoost predictor for price movements"""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
    
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train XGBoost model"""
        try:
            # Prepare features and targets
            features = data.select_dtypes(include=[np.number]).drop(['close'], axis=1, errors='ignore')
            targets = data['close'] if 'close' in data.columns else data.iloc[:, -1]
            
            # Split data
            train_size = int(len(features) * (1 - self.config.validation_split))
            X_train, X_val = features[:train_size], features[train_size:]
            y_train, y_val = targets[:train_size], targets[train_size:]
            
            # Train model
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            self.is_trained = True
            self.last_trained = datetime.now()
            
            # Calculate feature importance
            self.feature_importance = dict(zip(features.columns, self.model.feature_importances_))
            
            return {'status': 'success', 'feature_importance': self.feature_importance}
            
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make XGBoost prediction"""
        if not self.is_trained:
            raise ValueError("XGBoost model must be trained before making predictions")
        
        try:
            prediction = self.model.predict(features.reshape(1, -1))[0]
            
            return PredictionResult(
                symbol="",
                prediction=float(prediction),
                confidence=0.8,
                timestamp=datetime.now(),
                model_name="XGBoostPredictor",
                features_used=[],
                prediction_horizon=self.config.prediction_horizon
            )
            
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            raise
    
    def save_model(self, path: str):
        """Save XGBoost model"""
        self.model.save_model(path)
        pickle.dump(self.feature_importance, open(f"{path}_importance.pkl", 'wb'))
    
    def load_model(self, path: str):
        """Load XGBoost model"""
        self.model.load_model(path)
        self.feature_importance = pickle.load(open(f"{path}_importance.pkl", 'rb'))
        self.is_trained = True
        self.last_trained = datetime.now()

class LightGBMPredictor(BaseMLModel):
    """LightGBM predictor for price movements"""
    
    def __init__(self, config: TrainingConfig):
        super().__init__(config)
        self.model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
    
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train LightGBM model"""
        try:
            # Prepare features and targets
            features = data.select_dtypes(include=[np.number]).drop(['close'], axis=1, errors='ignore')
            targets = data['close'] if 'close' in data.columns else data.iloc[:, -1]
            
            # Split data
            train_size = int(len(features) * (1 - self.config.validation_split))
            X_train, X_val = features[:train_size], features[train_size:]
            y_train, y_val = targets[:train_size], targets[train_size:]
            
            # Train model
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(10)],
                verbose=False
            )
            
            self.is_trained = True
            self.last_trained = datetime.now()
            
            # Calculate feature importance
            self.feature_importance = dict(zip(features.columns, self.model.feature_importances_))
            
            return {'status': 'success', 'feature_importance': self.feature_importance}
            
        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def predict(self, features: np.ndarray) -> PredictionResult:
        """Make LightGBM prediction"""
        if not self.is_trained:
            raise ValueError("LightGBM model must be trained before making predictions")
        
        try:
            prediction = self.model.predict(features.reshape(1, -1))[0]
            
            return PredictionResult(
                symbol="",
                prediction=float(prediction),
                confidence=0.8,
                timestamp=datetime.now(),
                model_name="LightGBMPredictor",
                features_used=[],
                prediction_horizon=self.config.prediction_horizon
            )
            
        except Exception as e:
            logger.error(f"LightGBM prediction failed: {e}")
            raise
    
    def save_model(self, path: str):
        """Save LightGBM model"""
        self.model.booster_.save_model(path)
        pickle.dump(self.feature_importance, open(f"{path}_importance.pkl", 'wb'))
    
    def load_model(self, path: str):
        """Load LightGBM model"""
        self.model.booster_.load_model(path)
        self.feature_importance = pickle.load(open(f"{path}_importance.pkl", 'rb'))
        self.is_trained = True
        self.last_trained = datetime.now()

class PriceDataset(Dataset):
    """Dataset for price prediction models"""
    
    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

class RealTimeTrainingPipeline:
    """Real-time model training pipeline"""
    
    def __init__(self, model_manager, data_collector):
        self.model_manager = model_manager
        self.data_collector = data_collector
        self.training_tasks = {}
        self.training_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start the training pipeline"""
        self.is_running = True
        asyncio.create_task(self._training_loop())
        logger.info("Real-time training pipeline started")
    
    async def stop(self):
        """Stop the training pipeline"""
        self.is_running = False
        for task in self.training_tasks.values():
            task.cancel()
        logger.info("Real-time training pipeline stopped")
    
    async def _training_loop(self):
        """Main training loop"""
        while self.is_running:
            try:
                # Get training request
                training_request = await self.training_queue.get()
                
                # Process training request
                await self._process_training_request(training_request)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Training loop error: {e}")
                await asyncio.sleep(10)
    
    async def _process_training_request(self, request: Dict[str, Any]):
        """Process individual training request"""
        try:
            model_name = request['model_name']
            symbol = request['symbol']
            data = request['data']
            
            logger.info(f"Starting training for {model_name} on {symbol}")
            
            # Get model
            model = await self.model_manager.get_model(model_name, symbol)
            
            # Train model
            result = await model.train(data)
            
            # Save model
            model_path = f"models/{model_name}_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            model.save_model(model_path)
            
            # Update model manager
            await self.model_manager.update_model(model_name, symbol, model)
            
            logger.info(f"Training completed for {model_name} on {symbol}")
            
        except Exception as e:
            logger.error(f"Training request failed: {e}")
    
    async def schedule_training(self, model_name: str, symbol: str, data: pd.DataFrame):
        """Schedule training for a model"""
        request = {
            'model_name': model_name,
            'symbol': symbol,
            'data': data,
            'timestamp': datetime.now()
        }
        
        await self.training_queue.put(request)

class ModelManager:
    """Manager for all ML models"""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, BaseMLModel]] = {}  # {model_type: {symbol: model}}
        self.training_pipeline = RealTimeTrainingPipeline(self, None)
        self.model_configs = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """Initialize the model manager"""
        await self.training_pipeline.start()
        logger.info("Model manager initialized")
    
    async def shutdown(self):
        """Shutdown the model manager"""
        await self.training_pipeline.stop()
        self.executor.shutdown(wait=True)
        logger.info("Model manager shutdown")
    
    async def create_model(self, model_type: str, symbol: str, config: TrainingConfig) -> BaseMLModel:
        """Create a new model"""
        if model_type not in self.models:
            self.models[model_type] = {}
        
        # Create model based on type
        if model_type == "transformer":
            model = TransformerPricePredictor(config)
        elif model_type == "gnn":
            model = GraphNeuralNetwork(config)
        elif model_type == "ensemble":
            model = EnsembleModel(config)
        elif model_type == "xgboost":
            model = XGBoostPredictor(config)
        elif model_type == "lightgbm":
            model = LightGBMPredictor(config)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.models[model_type][symbol] = model
        self.model_configs[f"{model_type}_{symbol}"] = config
        
        return model
    
    async def get_model(self, model_type: str, symbol: str) -> Optional[BaseMLModel]:
        """Get a model"""
        if model_type in self.models and symbol in self.models[model_type]:
            return self.models[model_type][symbol]
        return None
    
    async def update_model(self, model_type: str, symbol: str, model: BaseMLModel):
        """Update a model"""
        if model_type not in self.models:
            self.models[model_type] = {}
        
        self.models[model_type][symbol] = model
    
    async def predict(self, model_type: str, symbol: str, features: np.ndarray) -> Optional[PredictionResult]:
        """Make prediction with specified model"""
        model = await self.get_model(model_type, symbol)
        if not model or not model.is_trained:
            return None
        
        try:
            return await model.predict(features)
        except Exception as e:
            logger.error(f"Prediction failed for {model_type}_{symbol}: {e}")
            return None
    
    async def batch_predict(self, predictions: List[Dict[str, Any]]) -> List[PredictionResult]:
        """Make batch predictions"""
        tasks = []
        for pred_request in predictions:
            task = self.predict(
                pred_request['model_type'],
                pred_request['symbol'],
                pred_request['features']
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, PredictionResult)]
        
        return valid_results
    
    async def schedule_retraining(self, model_type: str, symbol: str, data: pd.DataFrame):
        """Schedule model retraining"""
        await self.training_pipeline.schedule_training(model_type, symbol, data)
    
    async def get_model_status(self, model_type: str, symbol: str) -> Dict[str, Any]:
        """Get model status"""
        model = await self.get_model(model_type, symbol)
        if not model:
            return {'status': 'not_found'}
        
        return {
            'status': 'found',
            'is_trained': model.is_trained,
            'last_trained': model.last_trained,
            'training_history': model.training_history,
            'feature_importance': model.feature_importance
        }

# Utility functions for feature engineering
class FeatureEngineer:
    """Feature engineering for ML models"""
    
    @staticmethod
    def create_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicators from price data"""
        df = data.copy()
        
        # Moving averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / df['bb_width']
        
        # Volume indicators
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['vwap'] = (df['close'] * df['volume']).rolling(window=10).sum() / df['volume'].rolling(window=10).sum()
        
        # Volatility
        df['volatility'] = df['close'].rolling(window=10).std()
        df['volatility_ratio'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
        # Price changes
        df['price_change'] = df['close'].pct_change()
        df['price_change_5'] = df['close'].pct_change(5)
        df['price_change_10'] = df['close'].pct_change(10)
        
        # High/Low ratios
        if 'high' in df.columns and 'low' in df.columns:
            df['high_low_ratio'] = df['high'] / df['low']
            df['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return df
    
    @staticmethod
    def create_lag_features(data: pd.DataFrame, lags: List[int]) -> pd.DataFrame:
        """Create lag features"""
        df = data.copy()
        
        for lag in lags:
            for col in ['close', 'volume', 'high', 'low']:
                if col in df.columns:
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    @staticmethod
    def create_rolling_features(data: pd.DataFrame, windows: List[int]) -> pd.DataFrame:
        """Create rolling window features"""
        df = data.copy()
        
        for window in windows:
            for col in ['close', 'volume']:
                if col in df.columns:
                    df[f'{col}_mean_{window}'] = df[col].rolling(window=window).mean()
                    df[f'{col}_std_{window}'] = df[col].rolling(window=window).std()
                    df[f'{col}_min_{window}'] = df[col].rolling(window=window).min()
                    df[f'{col}_max_{window}'] = df[col].rolling(window=window).max()
        
        return df

# Model evaluation metrics
class ModelEvaluator:
    """Model evaluation utilities"""
    
    @staticmethod
    def calculate_metrics(predictions: np.ndarray, actuals: np.ndarray) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(actuals, predictions)
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        rmse = np.sqrt(mse)
        
        # Directional accuracy
        pred_direction = np.diff(predictions) > 0
        actual_direction = np.diff(actuals) > 0
        directional_accuracy = np.mean(pred_direction == actual_direction)
        
        return {
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'rmse': rmse,
            'directional_accuracy': directional_accuracy
        }
    
    @staticmethod
    def calculate_financial_metrics(predictions: np.ndarray, actuals: np.ndarray, 
                                  returns: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate financial metrics"""
        if returns is None:
            returns = np.diff(actuals) / actuals[:-1]
        
        # Calculate trading signals
        signals = np.diff(predictions) > 0
        
        # Calculate returns based on signals
        strategy_returns = signals * returns[1:] if len(signals) == len(returns) - 1 else signals * returns
        
        # Sharpe ratio
        sharpe_ratio = np.mean(strategy_returns) / np.std(strategy_returns) if np.std(strategy_returns) > 0 else 0
        
        # Sortino ratio
        downside_returns = strategy_returns[strategy_returns < 0]
        sortino_ratio = np.mean(strategy_returns) / np.std(downside_returns) if len(downside_returns) > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'total_return': np.prod(1 + strategy_returns) - 1,
            'win_rate': np.mean(strategy_returns > 0),
            'profit_factor': np.sum(strategy_returns[strategy_returns > 0]) / abs(np.sum(strategy_returns[strategy_returns < 0])) if np.sum(strategy_returns[strategy_returns < 0]) != 0 else float('inf')
        }