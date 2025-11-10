"""
Advanced Algorithmic Trading Service
TigerEx v11.0.0 - Sophisticated Algorithmic Trading Platform
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import uvicorn
import httpx
from datetime import datetime, timedelta
import json
import logging
import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from collections import defaultdict
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Advanced Algorithmic Trading Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enums
class AlgorithmType(str, Enum):
    GRID_TRADING = "grid_trading"
    DCA = "dollar_cost_averaging"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    TWAP = "time_weighted_average_price"
    VWAP = "volume_weighted_average_price"
    ICEBERG = "iceberg"
    PEGGING = "pegging"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    PAIR_TRADING = "pair_trading"
    NEWS_SENTIMENT = "news_sentiment"
    MACHINE_LEARNING = "machine_learning"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

# Data Models
class TradingAlgorithm(BaseModel):
    algorithm_id: str
    name: str
    type: AlgorithmType
    description: str
    parameters: Dict[str, Any]
    risk_settings: Dict[str, Any]
    performance_metrics: Dict[str, float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AlgorithmExecutionRequest(BaseModel):
    user_id: str
    algorithm_id: str
    symbol: str
    capital: Decimal = Field(..., gt=0)
    parameters: Optional[Dict[str, Any]] = {}
    risk_limits: Optional[Dict[str, Any]] = {}
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class BacktestRequest(BaseModel):
    algorithm_id: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal = Field(..., gt=0)
    parameters: Optional[Dict[str, Any]] = {}

class GridTradingRequest(BaseModel):
    symbol: str
    grid_count: int = Field(..., gt=1, le=100)
    lower_price: float = Field(..., gt=0)
    upper_price: float = Field(..., gt=0)
    investment_amount: Decimal = Field(..., gt=0)
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None

class DCARequest(BaseModel):
    symbol: str
    total_investment: Decimal = Field(..., gt=0)
    purchase_frequency: str = Field(default="daily", regex="^(hourly|daily|weekly|monthly)$")
    number_of_purchases: int = Field(..., gt=1)
    start_date: datetime
    end_date: Optional[datetime] = None
    price_target_percentage: Optional[float] = None

# Service Classes
class AlgorithmEngine:
    """Core algorithmic trading engine"""
    
    def __init__(self):
        self.algorithms = {}
        self.active_strategies = {}
        self.market_data = {}
        self.execution_queue = asyncio.Queue()
        self._initialize_built_in_algorithms()
    
    def _initialize_built_in_algorithms(self):
        """Initialize built-in trading algorithms"""
        algorithms = {
            "grid_trading": {
                "name": "Grid Trading Bot",
                "type": AlgorithmType.GRID_TRADING,
                "description": "Place buy and sell orders at regular price intervals",
                "parameters": {
                    "grid_count": {"type": "integer", "min": 2, "max": 100, "default": 10},
                    "lower_price": {"type": "float", "min": 0},
                    "upper_price": {"type": "float", "min": 0},
                    "investment_amount": {"type": "decimal", "min": 0}
                },
                "risk_settings": {
                    "max_position_size": {"type": "decimal", "default": 10000},
                    "stop_loss": {"type": "float", "default": 0.05},
                    "take_profit": {"type": "float", "default": 0.10}
                }
            },
            "dca_bot": {
                "name": "Dollar Cost Averaging",
                "type": AlgorithmType.DCA,
                "description": "Invest fixed amounts at regular intervals",
                "parameters": {
                    "total_investment": {"type": "decimal", "min": 0},
                    "purchase_frequency": {"type": "string", "options": ["hourly", "daily", "weekly", "monthly"]},
                    "number_of_purchases": {"type": "integer", "min": 1}
                },
                "risk_settings": {
                    "max_single_purchase": {"type": "decimal", "default": 1000}
                }
            },
            "momentum_strategy": {
                "name": "Momentum Trading",
                "type": AlgorithmType.MOMENTUM,
                "description": "Buy strong upward trends, sell downward trends",
                "parameters": {
                    "lookback_period": {"type": "integer", "min": 5, "max": 200, "default": 20},
                    "entry_threshold": {"type": "float", "default": 0.02},
                    "exit_threshold": {"type": "float", "default": -0.02}
                },
                "risk_settings": {
                    "max_drawdown": {"type": "float", "default": 0.10},
                    "position_sizing": {"type": "string", "default": "fixed"}
                }
            },
            "mean_reversion": {
                "name": "Mean Reversion",
                "type": AlgorithmType.MEAN_REVERSION,
                "description": "Trade deviations from historical mean",
                "parameters": {
                    "lookback_period": {"type": "integer", "min": 10, "max": 500, "default": 50},
                    "entry_std_dev": {"type": "float", "default": 2.0},
                    "exit_std_dev": {"type": "float", "default": 0.5}
                },
                "risk_settings": {
                    "max_position_size": {"type": "decimal", "default": 5000},
                    "stop_loss": {"type": "float", "default": 0.08}
                }
            },
            "arbitrage_bot": {
                "name": "Triangular Arbitrage",
                "type": AlgorithmType.ARBITRAGE,
                "description": "Exploit price differences between currency pairs",
                "parameters": {
                    "min_profit_threshold": {"type": "float", "default": 0.005},
                    "max_slippage": {"type": "float", "default": 0.001},
                    "execution_speed": {"type": "string", "options": ["fast", "normal"], "default": "fast"}
                },
                "risk_settings": {
                    "max_exposure": {"type": "decimal", "default": 10000}
                }
            },
            "twap_algorithm": {
                "name": "TWAP Execution",
                "type": AlgorithmType.TWAP,
                "description": "Execute large orders over time to minimize market impact",
                "parameters": {
                    "total_quantity": {"type": "decimal", "min": 0},
                    "time_period": {"type": "integer", "min": 1, "max": 1440},  # minutes
                    "slice_interval": {"type": "integer", "min": 1, "default": 5}
                },
                "risk_settings": {
                    "max_participation_rate": {"type": "float", "default": 0.1}
                }
            },
            "vwap_algorithm": {
                "name": "VWAP Execution",
                "type": AlgorithmType.VWAP,
                "description": "Execute orders in line with volume-weighted average price",
                "parameters": {
                    "total_quantity": {"type": "decimal", "min": 0},
                    "lookback_volume": {"type": "integer", "default": 30},
                    "participation_rate": {"type": "float", "default": 0.05}
                },
                "risk_settings": {
                    "max_deviation": {"type": "float", "default": 0.02}
                }
            },
            "pair_trading": {
                "name": "Statistical Pair Trading",
                "type": AlgorithmType.PAIR_TRADING,
                "description": "Trade correlated pairs when they diverge",
                "parameters": {
                    "pair_symbols": {"type": "array", "items": "string"},
                    "lookback_period": {"type": "integer", "default": 60},
                    "entry_threshold": {"type": "float", "default": 2.0},
                    "exit_threshold": {"type": "float", "default": 0.5}
                },
                "risk_settings": {
                    "max_position_per_leg": {"type": "decimal", "default": 5000},
                    "correlation_threshold": {"type": "float", "default": 0.7}
                }
            }
        }
        
        self.algorithms = algorithms
    
    async def execute_algorithm(self, request: AlgorithmExecutionRequest) -> Dict[str, Any]:
        """Execute trading algorithm"""
        try:
            execution_id = str(uuid.uuid4())
            
            # Get algorithm configuration
            algorithm_config = self.algorithms.get(request.algorithm_id)
            if not algorithm_config:
                raise HTTPException(status_code=404, detail="Algorithm not found")
            
            # Create execution instance
            execution = {
                "execution_id": execution_id,
                "user_id": request.user_id,
                "algorithm_id": request.algorithm_id,
                "symbol": request.symbol,
                "capital": float(request.capital),
                "parameters": request.parameters or {},
                "risk_limits": request.risk_limits or {},
                "status": "initializing",
                "created_at": datetime.utcnow(),
                "start_time": request.start_time or datetime.utcnow(),
                "end_time": request.end_time,
                "performance": {
                    "total_trades": 0,
                    "profitable_trades": 0,
                    "total_pnl": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0
                }
            }
            
            self.active_strategies[execution_id] = execution
            
            # Start algorithm execution
            asyncio.create_task(self._run_algorithm(execution))
            
            return {
                "execution_id": execution_id,
                "status": "started",
                "algorithm": algorithm_config["name"],
                "symbol": request.symbol,
                "capital": float(request.capital)
            }
            
        except Exception as e:
            logger.error(f"Error executing algorithm: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _run_algorithm(self, execution: Dict[str, Any]):
        """Run algorithm in background"""
        try:
            execution["status"] = "running"
            algorithm_type = self.algorithms[execution["algorithm_id"]]["type"]
            
            if algorithm_type == AlgorithmType.GRID_TRADING:
                await self._execute_grid_trading(execution)
            elif algorithm_type == AlgorithmType.DCA:
                await self._execute_dca(execution)
            elif algorithm_type == AlgorithmType.MOMENTUM:
                await self._execute_momentum(execution)
            elif algorithm_type == AlgorithmType.MEAN_REVERSION:
                await self._execute_mean_reversion(execution)
            elif algorithm_type == AlgorithmType.ARBITRAGE:
                await self._execute_arbitrage(execution)
            elif algorithm_type == AlgorithmType.TWAP:
                await self._execute_twap(execution)
            elif algorithm_type == AlgorithmType.VWAP:
                await self._execute_vwap(execution)
            elif algorithm_type == AlgorithmType.PAIR_TRADING:
                await self._execute_pair_trading(execution)
            else:
                execution["status"] = "completed"
                execution["error"] = f"Algorithm type {algorithm_type} not implemented"
            
        except Exception as e:
            logger.error(f"Error running algorithm {execution['execution_id']}: {str(e)}")
            execution["status"] = "error"
            execution["error"] = str(e)
    
    async def _execute_grid_trading(self, execution: Dict[str, Any]):
        """Execute grid trading strategy"""
        params = execution["parameters"]
        grid_count = params.get("grid_count", 10)
        lower_price = params.get("lower_price", 90)
        upper_price = params.get("upper_price", 110)
        capital = execution["capital"]
        
        # Calculate grid levels
        grid_spacing = (upper_price - lower_price) / (grid_count - 1)
        grid_levels = [lower_price + i * grid_spacing for i in range(grid_count)]
        
        # Calculate position size per grid level
        position_size = capital / (grid_count * grid_levels[grid_count // 2])
        
        # Place initial grid orders
        orders_placed = 0
        for i, price in enumerate(grid_levels):
            if i < len(grid_levels) // 2:
                # Buy orders below middle
                await self._place_order(execution, "buy", price, position_size)
            else:
                # Sell orders above middle
                await self._place_order(execution, "sell", price, position_size)
            orders_placed += 1
        
        execution["performance"]["total_trades"] = orders_placed
        execution["status"] = "completed"
    
    async def _execute_dca(self, execution: Dict[str, Any]):
        """Execute dollar cost averaging strategy"""
        params = execution["parameters"]
        total_investment = params.get("total_investment", 10000)
        frequency = params.get("purchase_frequency", "daily")
        num_purchases = params.get("number_of_purchases", 30)
        
        # Calculate purchase amount
        purchase_amount = total_investment / num_purchases
        
        # Calculate interval in seconds
        intervals = {"hourly": 3600, "daily": 86400, "weekly": 604800, "monthly": 2592000}
        interval_seconds = intervals.get(frequency, 86400)
        
        # Execute purchases
        for i in range(num_purchases):
            current_price = await self._get_market_price(execution["symbol"])
            quantity = purchase_amount / current_price
            
            await self._place_order(execution, "buy", current_price, quantity)
            execution["performance"]["total_trades"] += 1
            
            # Wait for next purchase (simulate with shorter time for demo)
            await asyncio.sleep(1)  # Replace with interval_seconds in production
        
        execution["status"] = "completed"
    
    async def _execute_momentum(self, execution: Dict[str, Any]):
        """Execute momentum trading strategy"""
        params = execution["parameters"]
        lookback_period = params.get("lookback_period", 20)
        entry_threshold = params.get("entry_threshold", 0.02)
        exit_threshold = params.get("exit_threshold", -0.02)
        
        # Get historical prices (mock)
        prices = await self._get_historical_prices(execution["symbol"], lookback_period)
        
        # Calculate momentum
        current_momentum = (prices[-1] - prices[0]) / prices[0]
        
        if current_momentum > entry_threshold:
            # Buy signal
            position_size = execution["capital"] * 0.5  # Use 50% of capital
            current_price = prices[-1]
            quantity = position_size / current_price
            await self._place_order(execution, "buy", current_price, quantity)
            execution["performance"]["total_trades"] += 1
            
        elif current_momentum < exit_threshold:
            # Sell signal
            position_size = execution["capital"] * 0.5
            current_price = prices[-1]
            quantity = position_size / current_price
            await self._place_order(execution, "sell", current_price, quantity)
            execution["performance"]["total_trades"] += 1
        
        execution["status"] = "completed"
    
    async def _execute_mean_reversion(self, execution: Dict[str, Any]):
        """Execute mean reversion strategy"""
        params = execution["parameters"]
        lookback_period = params.get("lookback_period", 50)
        entry_std_dev = params.get("entry_std_dev", 2.0)
        exit_std_dev = params.get("exit_std_dev", 0.5)
        
        # Get historical prices and calculate statistics
        prices = await self._get_historical_prices(execution["symbol"], lookback_period)
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        current_price = prices[-1]
        
        # Calculate z-score
        z_score = (current_price - mean_price) / std_price
        
        if z_score > entry_std_dev:
            # Price is too high - sell
            position_size = execution["capital"] * 0.3
            quantity = position_size / current_price
            await self._place_order(execution, "sell", current_price, quantity)
            execution["performance"]["total_trades"] += 1
            
        elif z_score < -entry_std_dev:
            # Price is too low - buy
            position_size = execution["capital"] * 0.3
            quantity = position_size / current_price
            await self._place_order(execution, "buy", current_price, quantity)
            execution["performance"]["total_trades"] += 1
        
        execution["status"] = "completed"
    
    async def _execute_arbitrage(self, execution: Dict[str, Any]):
        """Execute arbitrage strategy"""
        # Mock arbitrage detection
        # In real implementation, would monitor multiple exchanges
        arbitrage_opportunities = [
            {"pair": "BTC/USDT", "exchange1": "binance", "price1": 45000, 
             "exchange2": "coinbase", "price2": 45200, "profit": 0.0044},
            {"pair": "ETH/USDT", "exchange1": "kraken", "price1": 3000, 
             "exchange2": "binance", "price2": 3015, "profit": 0.0050}
        ]
        
        params = execution["parameters"]
        min_profit_threshold = params.get("min_profit_threshold", 0.005)
        
        for opportunity in arbitrage_opportunities:
            if opportunity["profit"] >= min_profit_threshold:
                # Execute arbitrage
                execution["performance"]["total_trades"] += 2  # Buy and sell
                execution["performance"]["total_pnl"] += opportunity["profit"] * execution["capital"]
        
        execution["status"] = "completed"
    
    async def _execute_twap(self, execution: Dict[str, Any]):
        """Execute TWAP algorithm"""
        params = execution["parameters"]
        total_quantity = params.get("total_quantity", 1000)
        time_period = params.get("time_period", 60)  # minutes
        slice_interval = params.get("slice_interval", 5)  # minutes
        
        # Calculate slice size
        num_slices = time_period // slice_interval
        slice_size = total_quantity / num_slices
        
        # Execute slices
        for i in range(num_slices):
            current_price = await self._get_market_price(execution["symbol"])
            await self._place_order(execution, "buy" if i % 2 == 0 else "sell", current_price, slice_size)
            execution["performance"]["total_trades"] += 1
            await asyncio.sleep(1)  # Simulate time between slices
        
        execution["status"] = "completed"
    
    async def _execute_vwap(self, execution: Dict[str, Any]):
        """Execute VWAP algorithm"""
        params = execution["parameters"]
        total_quantity = params.get("total_quantity", 1000)
        participation_rate = params.get("participation_rate", 0.05)
        
        # Mock market volume data
        market_volumes = [100000, 120000, 110000, 130000, 115000]  # Sample volumes
        total_market_volume = sum(market_volumes)
        
        # Calculate target volume
        target_volume = total_market_volume * participation_rate
        
        # Execute based on volume distribution
        slice_size = total_quantity / len(market_volumes)
        for i, volume in enumerate(market_volumes):
            current_price = await self._get_market_price(execution["symbol"])
            await self._place_order(execution, "buy", current_price, slice_size)
            execution["performance"]["total_trades"] += 1
            await asyncio.sleep(1)
        
        execution["status"] = "completed"
    
    async def _execute_pair_trading(self, execution: Dict[str, Any]):
        """Execute pair trading strategy"""
        params = execution["parameters"]
        pair_symbols = params.get("pair_symbols", ["BTC/USDT", "ETH/USDT"])
        lookback_period = params.get("lookback_period", 60)
        entry_threshold = params.get("entry_threshold", 2.0)
        
        # Get price data for both symbols
        prices1 = await self._get_historical_prices(pair_symbols[0], lookback_period)
        prices2 = await self._get_historical_prices(pair_symbols[1], lookback_period)
        
        # Calculate spread
        current_spread = prices1[-1] - prices2[-1]
        historical_spreads = [p1 - p2 for p1, p2 in zip(prices1, prices2)]
        spread_mean = np.mean(historical_spreads)
        spread_std = np.std(historical_spreads)
        spread_z_score = (current_spread - spread_mean) / spread_std
        
        # Execute pair trade
        if abs(spread_z_score) > entry_threshold:
            # Determine which leg to buy/sell
            if spread_z_score > 0:
                # Symbol1 is expensive, Symbol2 is cheap
                await self._place_order(execution, "sell", prices1[-1], 1, pair_symbols[0])
                await self._place_order(execution, "buy", prices2[-1], 1, pair_symbols[1])
            else:
                # Symbol1 is cheap, Symbol2 is expensive
                await self._place_order(execution, "buy", prices1[-1], 1, pair_symbols[0])
                await self._place_order(execution, "sell", prices2[-1], 1, pair_symbols[1])
            
            execution["performance"]["total_trades"] += 2
        
        execution["status"] = "completed"
    
    async def _place_order(self, execution: Dict[str, Any], side: str, price: float, 
                          quantity: float, symbol: str = None):
        """Place order (mock implementation)"""
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "execution_id": execution["execution_id"],
            "symbol": symbol or execution["symbol"],
            "side": side,
            "price": price,
            "quantity": quantity,
            "status": "filled",
            "timestamp": datetime.utcnow()
        }
        
        # Update performance metrics
        if side == "sell":
            execution["performance"]["total_pnl"] += price * quantity * 0.001  # Mock profit
        execution["performance"]["total_trades"] += 1
        
        logger.info(f"Placed order: {order}")
        return order
    
    async def _get_market_price(self, symbol: str) -> float:
        """Get current market price (mock)"""
        # Mock price data
        prices = {
            "BTC/USDT": 45000.0,
            "ETH/USDT": 3000.0,
            "AAPL": 150.0,
            "GOOGL": 2800.0
        }
        return prices.get(symbol, 100.0)
    
    async def _get_historical_prices(self, symbol: str, lookback_period: int) -> List[float]:
        """Get historical prices (mock)"""
        base_price = await self._get_market_price(symbol)
        # Generate mock price series
        prices = []
        for i in range(lookback_period):
            variation = np.random.normal(0, 0.02)  # 2% daily volatility
            price = base_price * (1 + variation)
            prices.append(price)
        return prices

class BacktestEngine:
    """Backtesting engine for trading algorithms"""
    
    def __init__(self):
        self.backtest_results = {}
    
    async def run_backtest(self, request: BacktestRequest) -> Dict[str, Any]:
        """Run backtest for algorithm"""
        try:
            backtest_id = str(uuid.uuid4())
            
            # Get historical data
            historical_data = await self._get_historical_data(
                request.symbol, request.start_date, request.end_date
            )
            
            # Run algorithm on historical data
            results = await self._simulate_algorithm(
                request.algorithm_id, historical_data, request.initial_capital, request.parameters
            )
            
            # Calculate performance metrics
            performance = await self._calculate_performance_metrics(results)
            
            backtest_result = {
                "backtest_id": backtest_id,
                "algorithm_id": request.algorithm_id,
                "symbol": request.symbol,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "initial_capital": float(request.initial_capital),
                "final_capital": performance["final_capital"],
                "total_return": performance["total_return"],
                "sharpe_ratio": performance["sharpe_ratio"],
                "max_drawdown": performance["max_drawdown"],
                "win_rate": performance["win_rate"],
                "total_trades": performance["total_trades"],
                "profitable_trades": performance["profitable_trades"],
                "trade_history": results["trades"][:10]  # Return first 10 trades
            }
            
            self.backtest_results[backtest_id] = backtest_result
            
            return backtest_result
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical data for backtesting"""
        # Mock historical data generation
        data = []
        current_date = start_date
        base_price = 100.0
        
        while current_date <= end_date:
            # Generate mock OHLCV data
            variation = np.random.normal(0, 0.02)
            open_price = base_price * (1 + variation)
            close_price = open_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.005)))
            volume = np.random.randint(1000000, 10000000)
            
            data.append({
                "timestamp": current_date,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
            
            base_price = close_price
            current_date += timedelta(days=1)
        
        return data
    
    async def _simulate_algorithm(self, algorithm_id: str, historical_data: List[Dict], 
                                 initial_capital: Decimal, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate algorithm on historical data"""
        # Mock algorithm simulation
        trades = []
        capital = float(initial_capital)
        position = 0
        
        for i, candle in enumerate(historical_data[::10]):  # Sample every 10th candle
            price = candle["close"]
            
            # Simple trading logic for demo
            if i % 20 == 0 and capital > 1000:  # Buy signal
                quantity = min(capital * 0.1 / price, 10)
                capital -= quantity * price
                position += quantity
                trades.append({
                    "timestamp": candle["timestamp"],
                    "type": "buy",
                    "price": price,
                    "quantity": quantity,
                    "capital": capital + position * price
                })
            
            elif i % 25 == 0 and position > 0:  # Sell signal
                quantity = min(position, 5)
                capital += quantity * price
                position -= quantity
                trades.append({
                    "timestamp": candle["timestamp"],
                    "type": "sell",
                    "price": price,
                    "quantity": quantity,
                    "capital": capital + position * price
                })
        
        final_value = capital + position * historical_data[-1]["close"]
        
        return {
            "trades": trades,
            "final_capital": final_value,
            "initial_capital": float(initial_capital)
        }
    
    async def _calculate_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        initial_capital = results["initial_capital"]
        final_capital = results["final_capital"]
        trades = results["trades"]
        
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Calculate Sharpe ratio (simplified)
        daily_returns = []
        for i in range(1, len(trades)):
            prev_value = trades[i-1]["capital"]
            curr_value = trades[i]["capital"]
            daily_return = (curr_value - prev_value) / prev_value if prev_value > 0 else 0
            daily_returns.append(daily_return)
        
        sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) if daily_returns else 0
        
        # Calculate max drawdown
        peak = trades[0]["capital"] if trades else initial_capital
        max_drawdown = 0
        for trade in trades:
            value = trade["capital"]
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate win rate
        profitable_trades = sum(1 for trade in trades if trade["type"] == "sell")
        win_rate = profitable_trades / len(trades) if trades else 0
        
        return {
            "final_capital": final_capital,
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": len(trades),
            "profitable_trades": profitable_trades
        }

# Initialize services
algorithm_engine = AlgorithmEngine()
backtest_engine = BacktestEngine()

# API Endpoints
@app.get("/api/v1/algorithms")
async def get_algorithms(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get available trading algorithms"""
    try:
        algorithms = []
        for algo_id, config in algorithm_engine.algorithms.items():
            algorithms.append({
                "algorithm_id": algo_id,
                "name": config["name"],
                "type": config["type"],
                "description": config["description"],
                "parameters": config["parameters"],
                "risk_settings": config["risk_settings"]
            })
        
        return {
            "success": True,
            "data": algorithms
        }
        
    except Exception as e:
        logger.error(f"Error getting algorithms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/algorithms/execute")
async def execute_algorithm(request: AlgorithmExecutionRequest,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Execute trading algorithm"""
    try:
        result = await algorithm_engine.execute_algorithm(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error executing algorithm: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/algorithms/executions/{execution_id}/status")
async def get_execution_status(execution_id: str,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get algorithm execution status"""
    try:
        if execution_id not in algorithm_engine.active_strategies:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution = algorithm_engine.active_strategies[execution_id]
        
        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "status": execution["status"],
                "algorithm_id": execution["algorithm_id"],
                "symbol": execution["symbol"],
                "performance": execution["performance"],
                "created_at": execution["created_at"].isoformat(),
                "error": execution.get("error")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/algorithms/backtest")
async def run_backtest(request: BacktestRequest,
                      credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Run algorithm backtest"""
    try:
        result = await backtest_engine.run_backtest(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error running backtest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/algorithms/grid-trading")
async def create_grid_trading_strategy(request: GridTradingRequest,
                                      credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create grid trading strategy"""
    try:
        # Create custom algorithm execution
        execution_request = AlgorithmExecutionRequest(
            user_id="demo_user",
            algorithm_id="grid_trading",
            symbol=request.symbol,
            capital=request.investment_amount,
            parameters={
                "grid_count": request.grid_count,
                "lower_price": request.lower_price,
                "upper_price": request.upper_price
            },
            risk_limits={
                "stop_loss": request.stop_loss,
                "take_profit": request.take_profit
            }
        )
        
        result = await algorithm_engine.execute_algorithm(execution_request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating grid trading strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/algorithms/dca")
async def create_dca_strategy(request: DCARequest,
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create DCA strategy"""
    try:
        execution_request = AlgorithmExecutionRequest(
            user_id="demo_user",
            algorithm_id="dca_bot",
            symbol=request.symbol,
            capital=request.total_investment,
            parameters={
                "total_investment": float(request.total_investment),
                "purchase_frequency": request.purchase_frequency,
                "number_of_purchases": request.number_of_purchases,
                "price_target_percentage": request.price_target_percentage
            },
            start_time=request.start_date,
            end_time=request.end_date
        )
        
        result = await algorithm_engine.execute_algorithm(execution_request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creating DCA strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/algorithms/performance/summary")
async def get_performance_summary(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get performance summary of all active algorithms"""
    try:
        summary = {
            "active_strategies": len(algorithm_engine.active_strategies),
            "total_capital_deployed": sum(
                strategy["capital"] for strategy in algorithm_engine.active_strategies.values()
                if strategy["status"] == "running"
            ),
            "total_trades_today": 1250,
            "best_performing_algorithm": {
                "name": "Grid Trading Bot",
                "return": 12.5
            },
            "algorithm_performance": [
                {
                    "algorithm_type": "Grid Trading",
                    "active_strategies": 45,
                    "avg_return": 8.2,
                    "win_rate": 0.65
                },
                {
                    "algorithm_type": "DCA",
                    "active_strategies": 120,
                    "avg_return": 5.8,
                    "win_rate": 0.72
                },
                {
                    "algorithm_type": "Momentum",
                    "active_strategies": 25,
                    "avg_return": 15.3,
                    "win_rate": 0.58
                },
                {
                    "algorithm_type": "Mean Reversion",
                    "active_strategies": 30,
                    "avg_return": 6.7,
                    "win_rate": 0.62
                }
            ]
        }
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "advanced-algorithmic-trading"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8015)