"""
Advanced Backtesting Engine for Market Making Strategies
Including Monte Carlo simulation, walk-forward analysis, and optimization
"""

import asyncio
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import pickle
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from scipy import stats
from scipy.optimize import minimize
import itertools
from abc import ABC, abstractmethod
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005
    benchmark_symbol: str = "SPY"
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    data_frequency: str = "1min"  # 1min, 5min, 15min, 1h, 1d
    enable_short_selling: bool = True
    enable_leverage: bool = False
    max_leverage: float = 2.0
    position_sizing_method: str = "fixed"  # fixed, percentage, kelly, volatility
    risk_free_rate: float = 0.02
    enable monte_carlo: bool = True
    monte_carlo_simulations: int = 1000
    enable_walk_forward: bool = True
    walk_forward_windows: int = 5
    optimization_method: str = "grid"  # grid, random, bayesian
    optimization_metric: str = "sharpe_ratio"  # sharpe_ratio, sortino, calmar, profit_factor

@dataclass
class BacktestResult:
    """Results from backtesting"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    total_trades: int
    average_trade: float
    average_win: float
    average_loss: float
    best_trade: float
    worst_trade: float
    equity_curve: pd.Series
    trades: pd.DataFrame
    monthly_returns: pd.Series
    benchmark_return: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    var_95: float = 0.0
    cvar_95: float = 0.0
    monte_carlo_results: Optional[Dict] = None
    walk_forward_results: Optional[Dict] = None
    optimization_results: Optional[Dict] = None

class BaseStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.position = 0
        self.cash = config.get('initial_capital', 100000)
        self.equity = []
        self.trades = []
        
    @abstractmethod
    async def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: float, price: float, volatility: float) -> float:
        """Calculate position size"""
        pass

class MarketMakingStrategy(BaseStrategy):
    """Market making strategy for backtesting"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.spread_percentage = config.get('spread_percentage', 0.001)
        self.max_position = config.get('max_position', 10000)
        self.inventory_target = config.get('inventory_target', 0)
        self.refresh_interval = config.get('refresh_interval', 60)
        
    async def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate market making signals"""
        signals = pd.DataFrame(index=data.index, columns=['signal', 'price'])
        
        for i, (timestamp, row) in enumerate(data.iterrows()):
            if i % self.refresh_interval != 0:
                continue
                
            mid_price = (row['bid'] + row['ask']) / 2
            spread = mid_price * self.spread_percentage
            
            # Calculate inventory skew
            inventory_ratio = self.position / self.max_position
            
            # Generate buy/sell signals based on inventory and spread
            if inventory_ratio > 0.2:
                # Too long, favor sells
                sell_price = mid_price + spread * 0.5
                buy_price = mid_price - spread * 1.5
            elif inventory_ratio < -0.2:
                # Too short, favor buys
                buy_price = mid_price - spread * 0.5
                sell_price = mid_price + spread * 1.5
            else:
                # Balanced
                buy_price = mid_price - spread
                sell_price = mid_price + spread
            
            signals.loc[timestamp, 'signal'] = 1 if inventory_ratio < 0 else -1
            signals.loc[timestamp, 'price'] = buy_price if inventory_ratio < 0 else sell_price
            
        return signals
    
    def calculate_position_size(self, signal: float, price: float, volatility: float) -> float:
        """Calculate position size for market making"""
        base_size = self.config.get('base_order_size', 100)
        
        # Adjust for volatility
        volatility_adjustment = min(max(1 / (1 + volatility * 100), 0.5), 2.0)
        
        # Adjust for inventory
        inventory_ratio = self.position / self.max_position
        inventory_adjustment = 1 - abs(inventory_ratio)
        
        position_size = base_size * volatility_adjustment * inventory_adjustment
        
        return min(max(position_size, 10), self.max_position)

class AdvancedBacktester:
    """Advanced backtesting engine"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data_cache = {}
        self.executor = ProcessPoolExecutor(max_workers=mp.cpu_count())
        
    async def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame) -> BacktestResult:
        """Run comprehensive backtest"""
        try:
            logger.info(f"Starting backtest for {strategy.__class__.__name__}")
            
            # Prepare data
            prepared_data = await self._prepare_data(data)
            
            # Run basic backtest
            basic_result = await self._run_basic_backtest(strategy, prepared_data)
            
            # Run Monte Carlo simulation
            monte_carlo_results = None
            if self.config.enable_monte_carlo:
                monte_carlo_results = await self._run_monte_carlo_simulation(strategy, prepared_data)
            
            # Run walk-forward analysis
            walk_forward_results = None
            if self.config.enable_walk_forward:
                walk_forward_results = await self._run_walk_forward_analysis(strategy, prepared_data)
            
            # Combine results
            result = BacktestResult(
                strategy_name=strategy.__class__.__name__,
                start_date=self.config.start_date,
                end_date=self.config.end_date,
                monte_carlo_results=monte_carlo_results,
                walk_forward_results=walk_forward_results,
                **basic_result
            )
            
            logger.info(f"Backtest completed for {strategy.__class__.__name__}")
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise
    
    async def _prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for backtesting"""
        # Filter by date range
        mask = (data.index >= self.config.start_date) & (data.index <= self.config.end_date)
        filtered_data = data.loc[mask].copy()
        
        # Calculate additional features
        filtered_data['returns'] = filtered_data['close'].pct_change()
        filtered_data['volatility'] = filtered_data['returns'].rolling(window=20).std()
        filtered_data['log_returns'] = np.log(filtered_data['close'] / filtered_data['close'].shift(1))
        
        # Add technical indicators
        filtered_data['sma_20'] = filtered_data['close'].rolling(window=20).mean()
        filtered_data['rsi'] = self._calculate_rsi(filtered_data['close'])
        filtered_data['bollinger_upper'], filtered_data['bollinger_lower'] = self._calculate_bollinger_bands(filtered_data['close'])
        
        # Handle missing data
        filtered_data = filtered_data.fillna(method='ffill').fillna(0)
        
        return filtered_data
    
    async def _run_basic_backtest(self, strategy: BaseStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """Run basic backtesting logic"""
        equity_curve = []
        trades = []
        
        # Initialize strategy
        strategy.cash = self.config.initial_capital
        strategy.position = 0
        strategy.equity = []
        strategy.trades = []
        
        # Generate signals
        signals = await strategy.generate_signals(data)
        
        # Simulate trading
        for timestamp, row in data.iterrows():
            if timestamp not in signals.index:
                continue
                
            signal = signals.loc[timestamp, 'signal']
            price = signals.loc[timestamp, 'price']
            
            if signal != 0:
                # Calculate position size
                volatility = row.get('volatility', 0.01)
                position_size = strategy.calculate_position_size(signal, price, volatility)
                
                # Execute trade
                if signal > 0 and strategy.position < self.config.max_position:
                    # Buy
                    cost = position_size * price * (1 + self.config.commission + self.config.slippage)
                    if strategy.cash >= cost:
                        strategy.position += position_size
                        strategy.cash -= cost
                        
                        trades.append({
                            'timestamp': timestamp,
                            'type': 'buy',
                            'quantity': position_size,
                            'price': price,
                            'cost': cost,
                            'position': strategy.position,
                            'cash': strategy.cash
                        })
                        
                elif signal < 0 and strategy.position > -self.config.max_position:
                    # Sell
                    proceeds = abs(position_size) * price * (1 - self.config.commission - self.config.slippage)
                    if abs(strategy.position) >= position_size:
                        strategy.position -= position_size
                        strategy.cash += proceeds
                        
                        trades.append({
                            'timestamp': timestamp,
                            'type': 'sell',
                            'quantity': abs(position_size),
                            'price': price,
                            'proceeds': proceeds,
                            'position': strategy.position,
                            'cash': strategy.cash
                        })
            
            # Calculate equity
            portfolio_value = strategy.cash + strategy.position * row['close']
            equity_curve.append(portfolio_value)
            strategy.equity.append(portfolio_value)
        
        # Calculate performance metrics
        equity_series = pd.Series(equity_curve, index=data.index[:len(equity_curve)])
        trades_df = pd.DataFrame(trades)
        
        metrics = await self._calculate_performance_metrics(equity_series, trades_df, data)
        
        return metrics
    
    async def _calculate_performance_metrics(self, equity_curve: pd.Series, trades: pd.DataFrame, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if len(equity_curve) == 0:
            return {}
        
        # Basic returns
        returns = equity_curve.pct_change().dropna()
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Annualized metrics
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annualized_return = (1 + total_return) ** (365 / days) - 1
        volatility = returns.std() * np.sqrt(365 * 24 * 60)  # Assuming minute data
        
        # Risk-adjusted metrics
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        sortino_ratio = self._calculate_sortino_ratio(returns)
        calmar_ratio = annualized_return / abs(self._calculate_max_drawdown(equity_curve))
        
        # Drawdown
        max_drawdown, max_drawdown_duration = self._calculate_drawdown_metrics(equity_curve)
        
        # Trade metrics
        win_rate, profit_factor, avg_trade, avg_win, avg_loss, best_trade, worst_trade = self._calculate_trade_metrics(trades)
        
        # Benchmark comparison
        benchmark_return = self._calculate_benchmark_return(data)
        alpha, beta = self._calculate_alpha_beta(returns, data)
        
        # Risk metrics
        var_95, cvar_95 = self._calculate_var_cvar(returns)
        
        # Monthly returns
        monthly_returns = equity_curve.resample('M').last().pct_change().dropna()
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'average_trade': avg_trade,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'equity_curve': equity_curve,
            'trades': trades,
            'monthly_returns': monthly_returns,
            'benchmark_return': benchmark_return,
            'alpha': alpha,
            'beta': beta,
            'var_95': var_95,
            'cvar_95': cvar_95,
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_std = downside_returns.std()
        mean_return = returns.mean()
        
        if downside_std == 0:
            return 0
        
        return mean_return / downside_std * np.sqrt(252)
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()
    
    def _calculate_drawdown_metrics(self, equity_curve: pd.Series) -> Tuple[float, int]:
        """Calculate drawdown metrics"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        max_drawdown = drawdown.min()
        
        # Calculate drawdown duration
        drawdown_duration = 0
        current_duration = 0
        max_duration = 0
        
        for dd in drawdown:
            if dd < 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return abs(max_drawdown), max_duration
    
    def _calculate_trade_metrics(self, trades: pd.DataFrame) -> Tuple[float, float, float, float, float, float, float]:
        """Calculate trade-related metrics"""
        if len(trades) == 0:
            return 0, 0, 0, 0, 0, 0, 0
        
        # Calculate trade P&L
        trades['pnl'] = 0.0
        running_position = 0
        
        for i, trade in trades.iterrows():
            if trade['type'] == 'buy':
                running_position += trade['quantity']
                trades.loc[i, 'pnl'] = -trade['cost']
            else:
                running_position -= trade['quantity']
                trades.loc[i, 'pnl'] = trade['proceeds']
        
        # Win rate
        winning_trades = trades[trades['pnl'] > 0]
        win_rate = len(winning_trades) / len(trades)
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum()
        losing_trades = trades[trades['pnl'] < 0]
        gross_loss = abs(losing_trades['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Average metrics
        avg_trade = trades['pnl'].mean()
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        best_trade = trades['pnl'].max()
        worst_trade = trades['pnl'].min()
        
        return win_rate, profit_factor, avg_trade, avg_win, avg_loss, best_trade, worst_trade
    
    def _calculate_benchmark_return(self, data: pd.DataFrame) -> float:
        """Calculate benchmark return"""
        if self.config.benchmark_symbol not in data.columns:
            return 0.0
        
        benchmark_prices = data[self.config.benchmark_symbol]
        return (benchmark_prices.iloc[-1] / benchmark_prices.iloc[0]) - 1
    
    def _calculate_alpha_beta(self, returns: pd.Series, data: pd.DataFrame) -> Tuple[float, float]:
        """Calculate alpha and beta"""
        if self.config.benchmark_symbol not in data.columns:
            return 0.0, 0.0
        
        benchmark_returns = data[self.config.benchmark_symbol].pct_change().dropna()
        
        # Align returns
        common_index = returns.index.intersection(benchmark_returns.index)
        if len(common_index) < 10:
            return 0.0, 0.0
        
        strategy_returns = returns.loc[common_index]
        benchmark_aligned = benchmark_returns.loc[common_index]
        
        # Calculate beta (covariance / variance)
        covariance = np.cov(strategy_returns, benchmark_aligned)[0, 1]
        variance = np.var(benchmark_aligned)
        beta = covariance / variance if variance > 0 else 0
        
        # Calculate alpha
        risk_free_rate = self.config.risk_free_rate / 252  # Daily risk-free rate
        alpha = (strategy_returns.mean() - risk_free_rate) - beta * (benchmark_aligned.mean() - risk_free_rate)
        
        return alpha * 252, beta  # Annualized alpha
    
    def _calculate_var_cvar(self, returns: pd.Series) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional Value at Risk"""
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        return var_95, cvar_95
    
    async def _run_monte_carlo_simulation(self, strategy: BaseStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """Run Monte Carlo simulation"""
        logger.info("Starting Monte Carlo simulation")
        
        # Get original returns
        original_returns = data['close'].pct_change().dropna()
        
        # Simulate multiple scenarios
        simulations = []
        for i in range(self.config.monte_carlo_simulations):
            # Bootstrap returns with replacement
            simulated_returns = np.random.choice(original_returns, size=len(original_returns), replace=True)
            
            # Create simulated price series
            simulated_prices = [data['close'].iloc[0]]
            for ret in simulated_returns:
                simulated_prices.append(simulated_prices[-1] * (1 + ret))
            
            simulated_data = data.copy()
            simulated_data['close'] = simulated_prices[:len(data)]
            
            # Run backtest on simulated data
            sim_result = await self._run_basic_backtest(strategy, simulated_data)
            simulations.append(sim_result['total_return'])
        
        # Calculate statistics
        simulations = np.array(simulations)
        mean_return = np.mean(simulations)
        std_return = np.std(simulations)
        confidence_interval = np.percentile(simulations, [5, 95])
        
        return {
            'mean_return': mean_return,
            'std_return': std_return,
            'confidence_interval': confidence_interval,
            'probability_of_loss': np.mean(simulations < 0),
            'best_case': np.max(simulations),
            'worst_case': np.min(simulations),
            'all_simulations': simulations.tolist()
        }
    
    async def _run_walk_forward_analysis(self, strategy: BaseStrategy, data: pd.DataFrame) -> Dict[str, Any]:
        """Run walk-forward analysis"""
        logger.info("Starting walk-forward analysis")
        
        # Split data into windows
        window_size = len(data) // self.config.walk_forward_windows
        results = []
        
        for i in range(self.config.walk_forward_windows):
            start_idx = i * window_size
            end_idx = min((i + 1) * window_size, len(data))
            
            if end_idx - start_idx < 100:  # Minimum window size
                continue
            
            window_data = data.iloc[start_idx:end_idx]
            
            # Train on first 70% of window, test on last 30%
            split_idx = int(len(window_data) * 0.7)
            train_data = window_data.iloc[:split_idx]
            test_data = window_data.iloc[split_idx:]
            
            # Run backtest on test data
            test_result = await self._run_basic_backtest(strategy, test_data)
            results.append(test_result)
        
        # Calculate aggregate statistics
        returns = [r['total_return'] for r in results]
        sharpe_ratios = [r['sharpe_ratio'] for r in results]
        max_drawdowns = [r['max_drawdown'] for r in results]
        
        return {
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'mean_sharpe_ratio': np.mean(sharpe_ratios),
            'std_sharpe_ratio': np.std(sharpe_ratios),
            'mean_max_drawdown': np.mean(max_drawdowns),
            'stability_ratio': np.mean(sharpe_ratios) / np.std(sharpe_ratios) if np.std(sharpe_ratios) > 0 else 0,
            'window_results': results
        }

class StrategyOptimizer:
    """Strategy optimization using various methods"""
    
    def __init__(self, backtester: AdvancedBacktester):
        self.backtester = backtester
        
    async def optimize_strategy(self, strategy_class: type, param_grid: Dict[str, List[Any]], data: pd.DataFrame) -> Dict[str, Any]:
        """Optimize strategy parameters"""
        if self.backtester.config.optimization_method == "grid":
            return await self._grid_optimization(strategy_class, param_grid, data)
        elif self.backtester.config.optimization_method == "random":
            return await self._random_optimization(strategy_class, param_grid, data)
        elif self.backtester.config.optimization_method == "bayesian":
            return await self._bayesian_optimization(strategy_class, param_grid, data)
        else:
            raise ValueError(f"Unknown optimization method: {self.backtester.config.optimization_method}")
    
    async def _grid_optimization(self, strategy_class: type, param_grid: Dict[str, List[Any]], data: pd.DataFrame) -> Dict[str, Any]:
        """Grid search optimization"""
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(itertools.product(*param_values))
        
        best_score = -float('inf')
        best_params = None
        best_result = None
        
        logger.info(f"Grid search: testing {len(combinations)} parameter combinations")
        
        for i, combination in enumerate(combinations):
            params = dict(zip(param_names, combination))
            
            try:
                # Create strategy with current parameters
                config = {**params, 'initial_capital': self.backtester.config.initial_capital}
                strategy = strategy_class(config)
                
                # Run backtest
                result = await self.backtester.run_backtest(strategy, data)
                
                # Evaluate based on optimization metric
                if self.backtester.config.optimization_metric == "sharpe_ratio":
                    score = result.sharpe_ratio
                elif self.backtester.config.optimization_metric == "sortino":
                    score = result.sortino_ratio
                elif self.backtester.config.optimization_metric == "calmar":
                    score = result.calmar_ratio
                elif self.backtester.config.optimization_metric == "profit_factor":
                    score = result.profit_factor
                else:
                    score = result.total_return
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_result = result
                
                logger.info(f"Combination {i+1}/{len(combinations)}: {params} -> Score: {score:.4f}")
                
            except Exception as e:
                logger.error(f"Error testing combination {params}: {e}")
                continue
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'best_result': best_result,
            'total_combinations_tested': len(combinations)
        }
    
    async def _random_optimization(self, strategy_class: type, param_grid: Dict[str, List[Any]], data: pd.DataFrame) -> Dict[str, Any]:
        """Random search optimization"""
        import random
        
        best_score = -float('inf')
        best_params = None
        best_result = None
        num_iterations = 100  # Can be configurable
        
        logger.info(f"Random search: testing {num_iterations} random parameter combinations")
        
        for i in range(num_iterations):
            # Generate random combination
            params = {}
            for param_name, param_values in param_grid.items():
                params[param_name] = random.choice(param_values)
            
            try:
                # Create strategy with current parameters
                config = {**params, 'initial_capital': self.backtester.config.initial_capital}
                strategy = strategy_class(config)
                
                # Run backtest
                result = await self.backtester.run_backtest(strategy, data)
                
                # Evaluate based on optimization metric
                if self.backtester.config.optimization_metric == "sharpe_ratio":
                    score = result.sharpe_ratio
                elif self.backtester.config.optimization_metric == "sortino":
                    score = result.sortino_ratio
                elif self.backtester.config.optimization_metric == "calmar":
                    score = result.calmar_ratio
                elif self.backtester.config.optimization_metric == "profit_factor":
                    score = result.profit_factor
                else:
                    score = result.total_return
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_result = result
                
                logger.info(f"Iteration {i+1}/{num_iterations}: {params} -> Score: {score:.4f}")
                
            except Exception as e:
                logger.error(f"Error testing combination {params}: {e}")
                continue
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'best_result': best_result,
            'total_iterations': num_iterations
        }
    
    async def _bayesian_optimization(self, strategy_class: type, param_grid: Dict[str, List[Any]], data: pd.DataFrame) -> Dict[str, Any]:
        """Bayesian optimization (simplified version)"""
        # This would typically use libraries like scikit-optimize or optuna
        # For now, implement a simplified version
        
        logger.info("Bayesian optimization (simplified)")
        
        # Start with random points, then use heuristic to guide search
        initial_points = 20
        iterations = 50
        
        # Initial random sampling
        await self._random_optimization(strategy_class, param_grid, data)
        
        # For a full implementation, you would:
        # 1. Use a surrogate model (Gaussian Process)
        # 2. Define acquisition function (EI, UCB, etc.)
        # 3. Optimize acquisition function to select next parameters
        # 4. Update surrogate model with new results
        
        # Return simplified result for now
        return await self._random_optimization(strategy_class, param_grid, data)

class BacktestReporter:
    """Generate comprehensive backtest reports"""
    
    @staticmethod
    def generate_report(result: BacktestResult) -> Dict[str, Any]:
        """Generate comprehensive backtest report"""
        report = {
            'executive_summary': {
                'strategy_name': result.strategy_name,
                'period': f"{result.start_date.date()} to {result.end_date.date()}",
                'total_return': f"{result.total_return:.2%}",
                'annualized_return': f"{result.annualized_return:.2%}",
                'sharpe_ratio': f"{result.sharpe_ratio:.2f}",
                'max_drawdown': f"{result.max_drawdown:.2%}",
                'win_rate': f"{result.win_rate:.2%}",
                'total_trades': result.total_trades
            },
            'performance_metrics': {
                'risk_metrics': {
                    'volatility': f"{result.volatility:.2%}",
                    'sortino_ratio': f"{result.sortino_ratio:.2f}",
                    'calmar_ratio': f"{result.calmar_ratio:.2f}",
                    'max_drawdown_duration': f"{result.max_drawdown_duration} periods",
                    'var_95': f"{result.var_95:.2%}",
                    'cvar_95': f"{result.cvar_95:.2%}"
                },
                'return_metrics': {
                    'total_return': f"{result.total_return:.2%}",
                    'annualized_return': f"{result.annualized_return:.2%}",
                    'alpha': f"{result.alpha:.2%}",
                    'beta': f"{result.beta:.2f}",
                    'benchmark_return': f"{result.benchmark_return:.2%}"
                },
                'trade_metrics': {
                    'total_trades': result.total_trades,
                    'win_rate': f"{result.win_rate:.2%}",
                    'profit_factor': f"{result.profit_factor:.2f}",
                    'average_trade': f"${result.average_trade:.2f}",
                    'average_win': f"${result.average_win:.2f}",
                    'average_loss': f"${result.average_loss:.2f}",
                    'best_trade': f"${result.best_trade:.2f}",
                    'worst_trade': f"${result.worst_trade:.2f}"
                }
            },
            'monte_carlo_analysis': None,
            'walk_forward_analysis': None
        }
        
        # Add Monte Carlo results if available
        if result.monte_carlo_results:
            report['monte_carlo_analysis'] = {
                'mean_return': f"{result.monte_carlo_results['mean_return']:.2%}",
                'std_return': f"{result.monte_carlo_results['std_return']:.2%}",
                'confidence_interval': [
                    f"{result.monte_carlo_results['confidence_interval'][0]:.2%}",
                    f"{result.monte_carlo_results['confidence_interval'][1]:.2%}"
                ],
                'probability_of_loss': f"{result.monte_carlo_results['probability_of_loss']:.2%}",
                'best_case': f"{result.monte_carlo_results['best_case']:.2%}",
                'worst_case': f"{result.monte_carlo_results['worst_case']:.2%}"
            }
        
        # Add walk-forward results if available
        if result.walk_forward_results:
            report['walk_forward_analysis'] = {
                'mean_return': f"{result.walk_forward_results['mean_return']:.2%}",
                'std_return': f"{result.walk_forward_results['std_return']:.2%}",
                'mean_sharpe_ratio': f"{result.walk_forward_results['mean_sharpe_ratio']:.2f}",
                'stability_ratio': f"{result.walk_forward_results['stability_ratio']:.2f}",
                'mean_max_drawdown': f"{result.walk_forward_results['mean_max_drawdown']:.2%}"
            }
        
        return report
    
    @staticmethod
    def create_equity_chart(result: BacktestResult) -> go.Figure:
        """Create equity curve chart"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Equity Curve', 'Drawdown'),
            row_heights=[0.7, 0.3]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=result.equity_curve.index,
                y=result.equity_curve.values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#007AFF', width=2)
            ),
            row=1, col=1
        )
        
        # Drawdown
        peak = result.equity_curve.expanding().max()
        drawdown = (result.equity_curve - peak) / peak * 100
        
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values,
                mode='lines',
                name='Drawdown (%)',
                line=dict(color='#FF3B30', width=1),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'{result.strategy_name} - Backtest Results',
            height=600,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_returns_distribution(result: BacktestResult) -> go.Figure:
        """Create returns distribution chart"""
        monthly_returns = result.monthly_returns * 100
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Histogram(
                x=monthly_returns.values,
                nbinsx=20,
                name='Monthly Returns (%)',
                marker=dict(color='#007AFF', opacity=0.7)
            )
        )
        
        fig.add_vline(
            x=monthly_returns.mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {monthly_returns.mean():.2f}%"
        )
        
        fig.update_layout(
            title='Monthly Returns Distribution',
            xaxis_title='Monthly Return (%)',
            yaxis_title='Frequency',
            height=400
        )
        
        return fig

# Main backtesting orchestration
class BacktestingOrchestrator:
    """Main class for orchestrating backtesting operations"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.backtester = AdvancedBacktester(config)
        self.optimizer = StrategyOptimizer(self.backtester)
        self.reporter = BacktestReporter()
        
    async def run_comprehensive_backtest(self, strategy_class: type, strategy_params: Dict[str, Any], data: pd.DataFrame, optimize: bool = False) -> Dict[str, Any]:
        """Run comprehensive backtesting with optional optimization"""
        try:
            # Create initial strategy
            strategy = strategy_class(strategy_params)
            
            # Run basic backtest
            result = await self.backtester.run_backtest(strategy, data)
            
            # Optimization if requested
            optimization_results = None
            if optimize:
                # Define parameter grid (example)
                param_grid = {
                    'spread_percentage': [0.001, 0.002, 0.003, 0.004, 0.005],
                    'max_position': [5000, 10000, 15000, 20000],
                    'base_order_size': [50, 100, 150, 200],
                    'refresh_interval': [30, 60, 120, 300]
                }
                
                optimization_results = await self.optimizer.optimize_strategy(strategy_class, param_grid, data)
                
                # Run backtest with optimized parameters
                optimized_strategy = strategy_class(optimization_results['best_params'])
                optimized_result = await self.backtester.run_backtest(optimized_strategy, data)
                
                # Use optimized results as final
                result = optimized_result
            
            # Generate report
            report = self.reporter.generate_report(result)
            
            # Create charts
            equity_chart = self.reporter.create_equity_chart(result)
            returns_chart = self.reporter.create_returns_distribution(result)
            
            return {
                'backtest_result': result,
                'report': report,
                'charts': {
                    'equity_curve': equity_chart,
                    'returns_distribution': returns_chart
                },
                'optimization_results': optimization_results
            }
            
        except Exception as e:
            logger.error(f"Comprehensive backtest failed: {e}")
            raise