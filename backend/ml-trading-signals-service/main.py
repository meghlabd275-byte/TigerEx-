from fastapi import FastAPI
from admin.admin_routes import router as admin_router

from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any

app = FastAPI(title="TigerEx ML Trading Signals Service")

# Include admin router
app.include_router(admin_router)

class TradingSignalEngine:
    def __init__(self):
        self.signals_cache = {}
        self.models = {
            'trend_following': self.trend_following_model,
            'mean_reversion': self.mean_reversion_model,
            'momentum': self.momentum_model,
            'volatility': self.volatility_model
        }
    
    def generate_trading_signals(self, symbol: str, timeframe: str = '1h') -> Dict:
        """Generate ML-based trading signals"""
        # Simulate ML model predictions
        current_price = self.get_current_price(symbol)
        historical_data = self.get_historical_data(symbol, timeframe)
        
        signals = {}
        
        # Generate signals from different models
        for model_name, model_func in self.models.items():
            signal = model_func(historical_data, current_price)
            signals[model_name] = signal
        
        # Combine signals
        combined_signal = self.combine_signals(signals)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': current_price,
            'signals': signals,
            'combined_signal': combined_signal,
            'confidence': combined_signal['confidence'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def trend_following_model(self, data: List[float], current_price: float) -> Dict:
        """Trend following model"""
        # Simple trend detection
        if len(data) < 20:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
        
        short_ma = np.mean(data[-10:])
        long_ma = np.mean(data[-20:])
        
        if current_price > short_ma > long_ma:
            return {'signal': 'BUY', 'strength': 70, 'confidence': 0.75}
        elif current_price < short_ma < long_ma:
            return {'signal': 'SELL', 'strength': 70, 'confidence': 0.75}
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
    
    def mean_reversion_model(self, data: List[float], current_price: float) -> Dict:
        """Mean reversion model"""
        if len(data) < 50:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
        
        mean_price = np.mean(data)
        std_price = np.std(data)
        
        z_score = (current_price - mean_price) / std_price
        
        if z_score > 2:
            return {'signal': 'SELL', 'strength': 80, 'confidence': 0.8}
        elif z_score < -2:
            return {'signal': 'BUY', 'strength': 80, 'confidence': 0.8}
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
    
    def momentum_model(self, data: List[float], current_price: float) -> Dict:
        """Momentum model"""
        if len(data) < 14:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
        
        # Calculate RSI-like momentum
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = np.mean(gains) if gains else 0
        avg_loss = np.mean(losses) if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi > 70:
            return {'signal': 'SELL', 'strength': 60, 'confidence': 0.65}
        elif rsi < 30:
            return {'signal': 'BUY', 'strength': 60, 'confidence': 0.65}
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
    
    def volatility_model(self, data: List[float], current_price: float) -> Dict:
        """Volatility-based model"""
        if len(data) < 20:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
        
        # Calculate volatility
        returns = []
        for i in range(1, len(data)):
            returns.append((data[i] - data[i-1]) / data[i-1])
        
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        
        if volatility > 0.8:
            return {'signal': 'SELL', 'strength': 40, 'confidence': 0.6}
        elif volatility < 0.2:
            return {'signal': 'BUY', 'strength': 40, 'confidence': 0.6}
        else:
            return {'signal': 'NEUTRAL', 'strength': 0, 'confidence': 0.5}
    
    def combine_signals(self, signals: Dict) -> Dict:
        """Combine signals from multiple models"""
        buy_signals = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_signals = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        neutral_signals = sum(1 for s in signals.values() if s['signal'] == 'NEUTRAL')
        
        total_confidence = sum(s['confidence'] for s in signals.values())
        
        if buy_signals > sell_signals and buy_signals > neutral_signals:
            final_signal = 'BUY'
            strength = sum(s['strength'] for s in signals.values() if s['signal'] == 'BUY') / buy_signals
            confidence = total_confidence / len(signals) * 1.1  # Boost confidence for consensus
        elif sell_signals > buy_signals and sell_signals > neutral_signals:
            final_signal = 'SELL'
            strength = sum(s['strength'] for s in signals.values() if s['signal'] == 'SELL') / sell_signals
            confidence = total_confidence / len(signals) * 1.1
        else:
            final_signal = 'NEUTRAL'
            strength = 0
            confidence = total_confidence / len(signals) * 0.9
        
        return {
            'signal': final_signal,
            'strength': min(strength, 100),
            'confidence': min(confidence, 1.0),
            'consensus': f"{max(buy_signals, sell_signals, neutral_signals)}/{len(signals)}"
        }
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price (simulated)"""
        # Simulate current price based on symbol
        base_prices = {
            'BTCUSDT': 50000,
            'ETHUSDT': 3000,
            'ADAUSDT': 1.2,
            'BTCUSD': 50000,
            'ETHUSD': 3000
        }
        return base_prices.get(symbol, 100)
    
    def get_historical_data(self, symbol: str, timeframe: str) -> List[float]:
        """Get historical price data (simulated)"""
        # Generate simulated historical data
        import random
        base_price = self.get_current_price(symbol)
        data_points = 100
        
        # Generate random walk data
        data = [base_price]
        for i in range(1, data_points):
            change = random.uniform(-0.02, 0.02) * data[-1]
            data.append(data[-1] + change)
        
        return data

# API Endpoints
@app.post("/api/v1/signals/generate")
async def generate_signals(symbol: str, timeframe: str = "1h"):
    """Generate ML trading signals"""
    engine = TradingSignalEngine()
    signals = engine.generate_trading_signals(symbol, timeframe)
    
    return {
        "success": True,
        "data": signals
    }

@app.post("/api/v1/signals/backtest")
async def backtest_strategy(symbol: str, strategy: str, start_date: str, end_date: str):
    """Backtest trading strategy"""
    # Simulate backtesting results
    backtest_results = {
        "strategy": strategy,
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "total_trades": 150,
        "winning_trades": 95,
        "losing_trades": 55,
        "win_rate": 63.3,
        "total_return": 12.5,
        "max_drawdown": 8.2,
        "sharpe_ratio": 1.8,
        "profit_factor": 1.4
    }
    
    return {
        "success": True,
        "backtest_results": backtest_results
    }

@app.get("/api/v1/signals/history/{symbol}")
async def get_signal_history(symbol: str, days: int = 30):
    """Get signal history for symbol"""
    # Generate historical signals
    import datetime
    from datetime import timedelta
    
    history = []
    current_time = datetime.datetime.utcnow()
    
    for i in range(days):
        time = current_time - timedelta(days=i)
        signal = {
            "timestamp": time.isoformat(),
            "symbol": symbol,
            "price": 50000 + (i * 100),  # Simulated
            "signal": "BUY" if i % 3 == 0 else "SELL" if i % 5 == 0 else "NEUTRAL",
            "strength": 70 if i % 3 == 0 else 60,
            "confidence": 0.75
        }
        history.append(signal)
    
    return {
        "success": True,
        "symbol": symbol,
        "history": history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8297)
