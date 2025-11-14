"""
Advanced Backtesting Engine for Market Maker Bot
High-performance multi-timeframe analysis with comprehensive metrics
"""

import asyncio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
import sqlite3
import json
import pickle
import logging
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    commission: float = 0.001
    slippage: float = 0.0005
    strategy_params: Dict[str, Any] = None
    benchmark: str = 'SPY'
    timeframe: str = '1h'
    lookback_period: int = 100
    rebalance_frequency: str = '1h'
    risk_free_rate: float = 0.02
    max_position_size: float = 1.0
    stop_loss: float = 0.02
    take_profit: float = 0.05

@dataclass
class Trade:
    timestamp: datetime
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    commission: float
    slippage: float
    total_cost: float
    portfolio_value_before: float
    portfolio_value_after: float
    pnl: float
    cumulative_pnl: float
    reason: str

@dataclass
class BacktestResult:
    config: BacktestConfig
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    trades: List[Trade]
    equity_curve: pd.Series
    benchmark_return: float
    alpha: float
    beta: float
    information_ratio: float
    var_95: float
    cvar_95: float
    skewness: float
    kurtosis: float
    hit_ratio: float
    avg_trade_duration: float
    best_trade: float
    worst_trade: float
    recovery_factor: float
    payoff_ratio: float

class MarketMakerStrategy:
    """Market making strategy for backtesting"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.position = 0
        self.inventory = 0
        self.cash = config.initial_capital
        self.orders = []
        self.trades = []
        self.equity_curve = []
        self.spread_model = None
        self.inventory_model = None
        
    def initialize(self, data: pd.DataFrame):
        """Initialize strategy with historical data"""
        self.data = data
        self.spread_model = self._train_spread_model(data)
        self.inventory_model = self._train_inventory_model(data)
        
    def _train_spread_model(self, data: pd.DataFrame):
        """Train spread prediction model"""
        # Simple volatility-based spread model
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        
        def predict_spread(row):
            return max(0.001, volatility.loc[row.name] * 2) if row.name in volatility.index else 0.001
            
        return predict_spread
    
    def _train_inventory_model(self, data: pd.DataFrame):
        """Train inventory management model"""
        # Simple mean reversion model
        price_mean = data['close'].mean()
        price_std = data['close'].std()
        
        def adjust_for_inventory(price, inventory):
            # Adjust quotes based on inventory position
            inventory_adjustment = (inventory / 1000) * price_std * 0.1
            return price + inventory_adjustment
            
        return adjust_for_inventory
    
    def generate_orders(self, timestamp: datetime, market_data: pd.Series) -> List[Dict]:
        """Generate market making orders"""
        orders = []
        current_price = market_data['close']
        spread = self.spread_model(market_data)
        
        # Calculate adjusted prices based on inventory
        adjusted_price = self.inventory_model(current_price, self.inventory)
        
        # Generate bid and ask orders
        bid_price = adjusted_price - spread / 2
        ask_price = adjusted_price + spread / 2
        
        # Order size based on volatility and inventory
        volatility = market_data.get('volatility', 0.01)
        base_size = min(100, self.config.initial_capital * 0.01 / current_price)
        
        # Adjust size based on inventory risk
        if abs(self.inventory) > 500:
            size_adjustment = 0.5
        else:
            size_adjustment = 1.0
        
        order_size = base_size * size_adjustment
        
        # Create limit orders
        if self.inventory < 200:  # Can buy more
            orders.append({
                'timestamp': timestamp,
                'side': 'buy',
                'price': bid_price,
                'quantity': order_size,
                'type': 'limit',
                'reason': 'market_making'
            })
        
        if self.inventory > -200:  # Can sell more
            orders.append({
                'timestamp': timestamp,
                'side': 'sell',
                'price': ask_price,
                'quantity': order_size,
                'type': 'limit',
                'reason': 'market_making'
            })
        
        return orders

class AdvancedBacktester:
    """Advanced backtesting engine with multiple features"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data = None
        self.benchmark_data = None
        self.strategy = None
        self.results = None
        
    async def load_data(self) -> pd.DataFrame:
        """Load historical data for backtesting"""
        # Mock data generation - in practice, load from database or API
        date_range = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq=self.config.timeframe
        )
        
        # Generate realistic price data with trends and volatility
        np.random.seed(42)
        n_points = len(date_range)
        
        # Trend component
        trend = np.linspace(100, 150, n_points)
        
        # Cyclical component
        cycles = 5 * np.sin(np.linspace(0, 10 * np.pi, n_points))
        
        # Random walk component
        random_walk = np.cumsum(np.random.normal(0, 2, n_points))
        
        # Combine components
        prices = trend + cycles + random_walk + 100
        prices = np.maximum(prices, 10)  # Ensure positive prices
        
        # Generate OHLCV data
        data = pd.DataFrame({
            'timestamp': date_range,
            'open': prices * (1 + np.random.normal(0, 0.001, n_points)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.005, n_points))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.005, n_points))),
            'close': prices,
            'volume': np.random.lognormal(10, 1, n_points)
        })
        
        data.set_index('timestamp', inplace=True)
        
        # Add technical indicators
        data = self._add_technical_indicators(data)
        
        self.data = data
        return data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the data"""
        # Returns
        data['returns'] = data['close'].pct_change()
        
        # Moving averages
        data['sma_10'] = ta.trend.sma_indicator(data['close'], window=10)
        data['sma_20'] = ta.trend.sma_indicator(data['close'], window=20)
        data['sma_50'] = ta.trend.sma_indicator(data['close'], window=50)
        data['ema_12'] = ta.trend.ema_indicator(data['close'], window=12)
        data['ema_26'] = ta.trend.ema_indicator(data['close'], window=26)
        
        # MACD
        data['macd'] = ta.trend.macd(data['close'])
        data['macd_signal'] = ta.trend.macd_signal(data['close'])
        data['macd_histogram'] = ta.trend.macd_diff(data['close'])
        
        # RSI
        data['rsi'] = ta.momentum.rsi(data['close'], window=14)
        
        # Bollinger Bands
        data['bb_upper'] = ta.volatility.bollinger_hband(data['close'])
        data['bb_middle'] = ta.volatility.bollinger_mavg(data['close'])
        data['bb_lower'] = ta.volatility.bollinger_lband(data['close'])
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        # Stochastic
        data['stoch_k'] = ta.momentum.stoch(data['high'], data['low'], data['close'])
        data['stoch_d'] = ta.momentum.stoch_signal(data['high'], data['low'], data['close'])
        
        # ATR
        data['atr'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'])
        
        # Volume indicators
        data['volume_sma'] = ta.volume.volume_sma(data['close'], window=20)
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # Volatility
        data['volatility'] = data['returns'].rolling(window=20).std()
        
        # Price momentum
        data['momentum_5'] = data['close'].pct_change(5)
        data['momentum_10'] = data['close'].pct_change(10)
        
        return data.fillna(method='ffill').fillna(0)
    
    async def load_benchmark_data(self) -> pd.DataFrame:
        """Load benchmark data"""
        # Mock benchmark data
        date_range = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq=self.config.timeframe
        )
        
        # Generate benchmark data (e.g., S&P 500)
        np.random.seed(123)
        n_points = len(date_range)
        
        # Lower volatility for benchmark
        benchmark_prices = np.cumsum(np.random.normal(0.0003, 0.01, n_points)) + 100
        benchmark_prices = np.maximum(benchmark_prices, 10)
        
        benchmark_data = pd.DataFrame({
            'timestamp': date_range,
            'close': benchmark_prices,
            'returns': np.concatenate([[0], np.diff(benchmark_prices) / benchmark_prices[:-1]])
        })
        
        benchmark_data.set_index('timestamp', inplace=True)
        self.benchmark_data = benchmark_data
        return benchmark_data
    
    async def run_backtest(self) -> BacktestResult:
        """Run the backtest simulation"""
        logger.info(f"Starting backtest for {self.config.symbol}")
        
        # Load data
        data = await self.load_data()
        benchmark_data = await self.load_benchmark_data()
        
        # Initialize strategy
        self.strategy = MarketMakerStrategy(self.config)
        self.strategy.initialize(data)
        
        # Simulation variables
        trades = []
        equity_curve = []
        current_capital = self.config.initial_capital
        position = 0
        portfolio_value = current_capital
        
        # Simulate trading
        for i, (timestamp, row) in enumerate(data.iterrows()):
            # Generate orders
            orders = self.strategy.generate_orders(timestamp, row)
            
            # Simulate order execution (simplified)
            for order in orders:
                execution_price = self._calculate_execution_price(order, row)
                trade_cost = self._calculate_trade_cost(order, execution_price)
                
                # Update position and capital
                if order['side'] == 'buy':
                    position += order['quantity']
                    current_capital -= trade_cost
                else:
                    position -= order['quantity']
                    current_capital += trade_cost
                
                # Record trade
                portfolio_value_before = portfolio_value
                portfolio_value = current_capital + position * row['close']
                
                trade = Trade(
                    timestamp=timestamp,
                    symbol=self.config.symbol,
                    side=order['side'],
                    quantity=order['quantity'],
                    price=execution_price,
                    commission=self.config.commission * execution_price * order['quantity'],
                    slippage=self.config.slippage * execution_price,
                    total_cost=trade_cost,
                    portfolio_value_before=portfolio_value_before,
                    portfolio_value_after=portfolio_value,
                    pnl=portfolio_value - portfolio_value_before,
                    cumulative_pnl=portfolio_value - self.config.initial_capital,
                    reason=order['reason']
                )
                
                trades.append(trade)
            
            # Update strategy state
            self.strategy.position = position
            self.strategy.cash = current_capital
            self.strategy.inventory = position
            
            # Record equity curve
            equity_curve.append(portfolio_value)
        
        # Create equity curve series
        equity_series = pd.Series(equity_curve, index=data.index)
        
        # Calculate performance metrics
        results = await self._calculate_performance_metrics(
            equity_series, benchmark_data, trades
        )
        
        self.results = results
        logger.info(f"Backtest completed. Total return: {results.total_return:.2%}")
        
        return results
    
    def _calculate_execution_price(self, order: Dict, market_data: pd.Series) -> float:
        """Calculate realistic execution price with slippage"""
        base_price = market_data['close']
        
        if order['type'] == 'limit':
            # Limit order might not execute if price moves away
            if order['side'] == 'buy' and order['price'] >= base_price:
                return order['price']
            elif order['side'] == 'sell' and order['price'] <= base_price:
                return order['price']
            else:
                return None  # Order didn't execute
        else:
            # Market order with slippage
            slippage_multiplier = 1 + self.config.slippage if order['side'] == 'buy' else 1 - self.config.slippage
            return base_price * slippage_multiplier
    
    def _calculate_trade_cost(self, order: Dict, execution_price: float) -> float:
        """Calculate total trade cost including commission"""
        trade_value = execution_price * order['quantity']
        commission = self.config.commission * trade_value
        return trade_value + commission
    
    async def _calculate_performance_metrics(
        self, 
        equity_curve: pd.Series, 
        benchmark_data: pd.DataFrame,
        trades: List[Trade]
    ) -> BacktestResult:
        """Calculate comprehensive performance metrics"""
        
        # Basic returns
        returns = equity_curve.pct_change().dropna()
        benchmark_returns = benchmark_data['returns'].dropna()
        
        # Time-aligned returns
        min_length = min(len(returns), len(benchmark_returns))
        returns_aligned = returns.iloc[-min_length:]
        benchmark_returns_aligned = benchmark_returns.iloc[-min_length:]
        
        # Total return
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Annualized return
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annualized_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (365 / days) - 1
        
        # Volatility
        volatility = returns_aligned.std() * np.sqrt(252)
        
        # Sharpe ratio
        excess_returns = returns_aligned - self.config.risk_free_rate / 252
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # Sortino ratio
        downside_returns = returns_aligned[returns_aligned < 0]
        downside_std = downside_returns.std()
        sortino_ratio = excess_returns.mean() / downside_std * np.sqrt(252) if downside_std != 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns_aligned).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Maximum drawdown duration
        drawdown_duration = self._calculate_max_drawdown_duration(drawdown)
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Trade statistics
        trade_pnls = [trade.pnl for trade in trades if trade.pnl != 0]
        winning_trades = [pnl for pnl in trade_pnls if pnl > 0]
        losing_trades = [pnl for pnl in trade_pnls if pnl < 0]
        
        win_rate = len(winning_trades) / len(trade_pnls) if trade_pnls else 0
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        profit_factor = abs(sum(winning_trades) / sum(losing_trades)) if losing_trades else float('inf')
        
        # Beta and Alpha
        covariance = np.cov(returns_aligned, benchmark_returns_aligned)[0, 1]
        benchmark_variance = np.var(benchmark_returns_aligned)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        alpha = (annualized_return - self.config.risk_free_rate) - beta * (benchmark_returns_aligned.mean() * 252 - self.config.risk_free_rate)
        
        # Information ratio
        tracking_error = (returns_aligned - benchmark_returns_aligned).std() * np.sqrt(252)
        information_ratio = (annualized_return - benchmark_returns_aligned.mean() * 252) / tracking_error if tracking_error != 0 else 0
        
        # Risk metrics
        var_95 = np.percentile(returns_aligned, 5)
        cvar_95 = returns_aligned[returns_aligned <= var_95].mean()
        skewness = stats.skew(returns_aligned)
        kurtosis = stats.kurtosis(returns_aligned)
        
        # Additional metrics
        best_trade = max(trade_pnls) if trade_pnls else 0
        worst_trade = min(trade_pnls) if trade_pnls else 0
        recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        payoff_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else 0
        
        # Calculate average trade duration
        trade_durations = []
        for i, trade in enumerate(trades):
            if i > 0:
                duration = (trade.timestamp - trades[i-1].timestamp).total_seconds() / 3600  # in hours
                trade_durations.append(duration)
        avg_trade_duration = np.mean(trade_durations) if trade_durations else 0
        
        return BacktestResult(
            config=self.config,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            calmar_ratio=calmar_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            trades=trades,
            equity_curve=equity_curve,
            benchmark_return=benchmark_returns_aligned.sum(),
            alpha=alpha,
            beta=beta,
            information_ratio=information_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            skewness=skewness,
            kurtosis=kurtosis,
            hit_ratio=win_rate,
            avg_trade_duration=avg_trade_duration,
            best_trade=best_trade,
            worst_trade=worst_trade,
            recovery_factor=recovery_factor,
            payoff_ratio=payoff_ratio
        )
    
    def _calculate_max_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration in days"""
        is_drawdown = drawdown < 0
        drawdown_periods = []
        start = None
        
        for i, dd in enumerate(is_drawdown):
            if dd and start is None:
                start = i
            elif not dd and start is not None:
                duration = i - start
                drawdown_periods.append(duration)
                start = None
        
        if start is not None:
            drawdown_periods.append(len(drawdown) - start)
        
        return max(drawdown_periods) if drawdown_periods else 0
    
    def generate_report(self) -> str:
        """Generate comprehensive backtest report"""
        if not self.results:
            return "No backtest results available. Run backtest first."
        
        result = self.results
        
        report = f"""
# Backtest Report for {result.config.symbol}

## Configuration
- Symbol: {result.config.symbol}
- Period: {result.config.start_date.date()} to {result.config.end_date.date()}
- Initial Capital: ${result.config.initial_capital:,.2f}
- Commission: {result.config.commission:.2%}
- Slippage: {result.config.slippage:.2%}
- Timeframe: {result.config.timeframe}

## Performance Summary
- Total Return: {result.total_return:.2%}
- Annualized Return: {result.annualized_return:.2%}
- Volatility: {result.volatility:.2%}
- Sharpe Ratio: {result.sharpe_ratio:.2f}
- Sortino Ratio: {result.sortino_ratio:.2f}
- Maximum Drawdown: {result.max_drawdown:.2%}
- Max Drawdown Duration: {result.max_drawdown_duration} days
- Calmar Ratio: {result.calmar_ratio:.2f}

## Risk Metrics
- Beta: {result.beta:.2f}
- Alpha: {result.alpha:.2%}
- Information Ratio: {result.information_ratio:.2f}
- VaR (95%): {result.var_95:.2%}
- CVaR (95%): {result.cvar_95:.2%}
- Skewness: {result.skewness:.2f}
- Kurtosis: {result.kurtosis:.2f}

## Trading Statistics
- Total Trades: {result.total_trades}
- Winning Trades: {result.winning_trades}
- Losing Trades: {result.losing_trades}
- Win Rate: {result.win_rate:.2%}
- Average Win: ${result.avg_win:.2f}
- Average Loss: ${result.avg_loss:.2f}
- Profit Factor: {result.profit_factor:.2f}
- Best Trade: ${result.best_trade:.2f}
- Worst Trade: ${result.worst_trade:.2f}
- Average Trade Duration: {result.avg_trade_duration:.1f} hours
- Recovery Factor: {result.recovery_factor:.2f}
- Payoff Ratio: {result.payoff_ratio:.2f}

## Benchmark Comparison
- Benchmark Return: {result.benchmark_return:.2%}
- Outperformance: {(result.total_return - result.benchmark_return):.2%}

## Conclusion
{'Strong performance' if result.sharpe_ratio > 1 else 'Moderate performance' if result.sharpe_ratio > 0.5 else 'Poor performance'}
"""
        
        return report
    
    def plot_results(self) -> go.Figure:
        """Create comprehensive visualization of backtest results"""
        if not self.results:
            return None
        
        result = self.results
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=('Equity Curve', 'Drawdown', 'Monthly Returns', 'Trade Distribution',
                          'Rolling Sharpe', 'Underwater Plot', 'Trade PnL', 'Volume'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=result.equity_curve.index,
                y=result.equity_curve,
                name='Portfolio',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Drawdown
        cumulative = (1 + result.equity_curve.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown * 100,
                fill='tonexty',
                name='Drawdown',
                line=dict(color='red')
            ),
            row=1, col=2
        )
        
        # Monthly returns
        monthly_returns = result.equity_curve.resample('M').last().pct_change()
        fig.add_trace(
            go.Bar(
                x=monthly_returns.index,
                y=monthly_returns * 100,
                name='Monthly Returns',
                marker_color=['green' if x > 0 else 'red' for x in monthly_returns]
            ),
            row=2, col=1
        )
        
        # Trade distribution
        trade_pnls = [trade.pnl for trade in result.trades if trade.pnl != 0]
        fig.add_trace(
            go.Histogram(
                x=trade_pnls,
                nbinsx=50,
                name='Trade PnL Distribution',
                marker_color='blue'
            ),
            row=2, col=2
        )
        
        # Rolling Sharpe ratio
        rolling_sharpe = (
            result.equity_curve.pct_change().rolling(window=252).mean() / 
            result.equity_curve.pct_change().rolling(window=252).std()
        ) * np.sqrt(252)
        
        fig.add_trace(
            go.Scatter(
                x=rolling_sharpe.index,
                y=rolling_sharpe,
                name='Rolling Sharpe (1yr)',
                line=dict(color='green')
            ),
            row=3, col=1
        )
        
        # Underwater plot
        underwater = cumulative / running_max - 1
        fig.add_trace(
            go.Scatter(
                x=underwater.index,
                y=underwater * 100,
                fill='tonexty',
                name='Underwater',
                line=dict(color='red')
            ),
            row=3, col=2
        )
        
        # Trade PnL over time
        if result.trades:
            trade_times = [trade.timestamp for trade in result.trades]
            trade_pnls_cumulative = np.cumsum([trade.pnl for trade in result.trades])
            
            fig.add_trace(
                go.Scatter(
                    x=trade_times,
                    y=trade_pnls_cumulative,
                    name='Cumulative Trade PnL',
                    line=dict(color='purple')
                ),
                row=4, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f'Backtest Results - {result.config.symbol}',
            height=1200,
            showlegend=True
        )
        
        return fig
    
    def save_results(self, filename: str):
        """Save backtest results to file"""
        if not self.results:
            logger.error("No results to save")
            return
        
        # Save results as pickle
        with open(f"{filename}.pkl", 'wb') as f:
            pickle.dump(self.results, f)
        
        # Save report as text
        report = self.generate_report()
        with open(f"{filename}.txt", 'w') as f:
            f.write(report)
        
        # Save trades as CSV
        if self.results.trades:
            trades_df = pd.DataFrame([asdict(trade) for trade in self.results.trades])
            trades_df.to_csv(f"{filename}_trades.csv", index=False)
        
        logger.info(f"Results saved to {filename}")

class MultiAssetBacktester:
    """Backtester for multiple assets simultaneously"""
    
    def __init__(self, configs: List[BacktestConfig]):
        self.configs = configs
        self.results = {}
        
    async def run_multi_asset_backtest(self) -> Dict[str, BacktestResult]:
        """Run backtest for multiple assets"""
        tasks = []
        
        for config in self.configs:
            backtester = AdvancedBacktester(config)
            task = asyncio.create_task(backtester.run_backtest())
            tasks.append((config.symbol, task))
        
        # Wait for all tasks to complete
        for symbol, task in tasks:
            result = await task
            self.results[symbol] = result
        
        return self.results
    
    def generate_portfolio_report(self) -> str:
        """Generate portfolio-level report"""
        if not self.results:
            return "No results available"
        
        total_portfolio_return = 0
        total_portfolio_value = 0
        sharpe_ratios = []
        
        report = "# Multi-Asset Portfolio Backtest Report\n\n"
        
        for symbol, result in self.results.items():
            report += f"## {symbol}\n"
            report += f"- Total Return: {result.total_return:.2%}\n"
            report += f"- Sharpe Ratio: {result.sharpe_ratio:.2f}\n"
            report += f"- Max Drawdown: {result.max_drawdown:.2%}\n\n"
            
            total_portfolio_return += result.total_return
            total_portfolio_value += result.equity_curve.iloc[-1]
            sharpe_ratios.append(result.sharpe_ratio)
        
        # Portfolio metrics
        portfolio_sharpe = np.mean(sharpe_ratios)
        
        report += "## Portfolio Summary\n"
        report += f"- Portfolio Return: {total_portfolio_return:.2%}\n"
        report += f"- Portfolio Value: ${total_portfolio_value:,.2f}\n"
        report += f"- Portfolio Sharpe: {portfolio_sharpe:.2f}\n"
        
        return report

# Utility functions
async def run_parameter_optimization(
    base_config: BacktestConfig,
    param_ranges: Dict[str, List[Any]]
) -> Dict[str, BacktestResult]:
    """Run parameter optimization using grid search"""
    best_result = None
    best_sharpe = -float('inf')
    results = {}
    
    # Generate parameter combinations
    import itertools
    param_names = list(param_ranges.keys())
    param_values = list(param_ranges.values())
    
    for combination in itertools.product(*param_values):
        # Create config with new parameters
        strategy_params = dict(zip(param_names, combination))
        config = BacktestConfig(
            symbol=base_config.symbol,
            start_date=base_config.start_date,
            end_date=base_config.end_date,
            initial_capital=base_config.initial_capital,
            commission=base_config.commission,
            slippage=base_config.slippage,
            strategy_params=strategy_params,
            timeframe=base_config.timeframe
        )
        
        # Run backtest
        backtester = AdvancedBacktester(config)
        result = await backtester.run_backtest()
        
        # Store result
        param_key = "_".join([f"{k}={v}" for k, v in strategy_params.items()])
        results[param_key] = result
        
        # Check if this is the best result
        if result.sharpe_ratio > best_sharpe:
            best_sharpe = result.sharpe_ratio
            best_result = result
    
    results['best'] = best_result
    return results

# Main execution
async def main():
    # Example usage
    config = BacktestConfig(
        symbol='BTCUSDT',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005,
        timeframe='1h'
    )
    
    backtester = AdvancedBacktester(config)
    results = await backtester.run_backtest()
    
    print(backtester.generate_report())
    
    # Save results
    backtester.save_results('btc_backtest_results')
    
    # Create visualization
    fig = backtester.plot_results()
    fig.show()

if __name__ == "__main__":
    asyncio.run(main())