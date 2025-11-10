"""
Advanced Portfolio Analytics Service
TigerEx v11.0.0 - Comprehensive Portfolio Analysis and Management
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
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Advanced Portfolio Analytics Service", version="1.0.0")

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

# Data Models
@dataclass
class PortfolioMetrics:
    total_value: float
    total_return: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    correlation_matrix: Dict[str, float]
    sector_allocation: Dict[str, float]
    asset_allocation: Dict[str, float]

class PortfolioRequest(BaseModel):
    user_id: str
    portfolio_id: Optional[str] = None
    timeframe: str = Field(default="1M", regex="^(1D|1W|1M|3M|6M|1Y|ALL)$")
    include_benchmarks: bool = True
    benchmark_symbol: str = "SPY"

class AssetAllocation(BaseModel):
    symbol: str
    name: str
    quantity: float
    current_price: float
    market_value: float
    weight: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    sector: str
    asset_type: str

class RiskAnalysis(BaseModel):
    portfolio_risk_score: float
    volatility_risk: float
    concentration_risk: float
    currency_risk: float
    liquidity_risk: float
    sector_risk: Dict[str, float]
    recommendations: List[str]

class PerformanceMetrics(BaseModel):
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    beta: float
    alpha: float
    information_ratio: float
    tracking_error: float

class RebalanceRecommendation(BaseModel):
    symbol: str
    current_weight: float
    target_weight: float
    recommended_action: str  # BUY/SELL/HOLD
    quantity: float
    estimated_cost: float
    priority: int

class TaxOptimization(BaseModel):
    tax_loss_harvesting_opportunities: List[Dict[str, Any]]
    wash_sale_warnings: List[Dict[str, Any]]
    tax_efficiency_score: float
    recommendations: List[str]

# Service Classes
class PortfolioAnalyticsEngine:
    """Advanced portfolio analytics and risk management"""
    
    def __init__(self):
        self.cache = {}
        self.risk_free_rate = 0.02  # 2% risk-free rate
        
    async def calculate_portfolio_metrics(self, portfolio_data: Dict[str, Any]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        try:
            holdings = portfolio_data.get('holdings', [])
            historical_data = portfolio_data.get('historical_data', [])
            
            if not holdings:
                raise ValueError("Portfolio has no holdings")
                
            # Basic calculations
            total_value = sum(h['market_value'] for h in holdings)
            total_cost = sum(h['cost_basis'] for h in holdings)
            total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0
            
            # Daily returns calculation
            daily_returns = self._calculate_daily_returns(historical_data)
            
            # Risk metrics
            volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0
            sharpe_ratio = (total_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            max_drawdown = self._calculate_max_drawdown(historical_data)
            
            # Beta and Alpha calculation
            benchmark_data = portfolio_data.get('benchmark_data', [])
            beta, alpha = self._calculate_beta_alpha(daily_returns, benchmark_data)
            
            # Value at Risk
            var_95 = np.percentile(daily_returns, 5) if daily_returns else 0
            var_99 = np.percentile(daily_returns, 1) if daily_returns else 0
            
            # Correlation matrix
            correlation_matrix = self._calculate_correlation_matrix(holdings)
            
            # Allocations
            sector_allocation = self._calculate_sector_allocation(holdings)
            asset_allocation = self._calculate_asset_allocation(holdings)
            
            return PortfolioMetrics(
                total_value=total_value,
                total_return=total_return,
                daily_return=daily_returns[-1] if daily_returns else 0,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha,
                var_95=var_95,
                var_99=var_99,
                correlation_matrix=correlation_matrix,
                sector_allocation=sector_allocation,
                asset_allocation=asset_allocation
            )
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_daily_returns(self, historical_data: List[Dict]) -> List[float]:
        """Calculate daily returns from historical data"""
        if len(historical_data) < 2:
            return []
        
        returns = []
        for i in range(1, len(historical_data)):
            prev_value = historical_data[i-1]['portfolio_value']
            curr_value = historical_data[i]['portfolio_value']
            daily_return = (curr_value - prev_value) / prev_value if prev_value > 0 else 0
            returns.append(daily_return)
        
        return returns
    
    def _calculate_max_drawdown(self, historical_data: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if len(historical_data) < 2:
            return 0
        
        peak = historical_data[0]['portfolio_value']
        max_dd = 0
        
        for data in historical_data[1:]:
            if data['portfolio_value'] > peak:
                peak = data['portfolio_value']
            else:
                drawdown = (peak - data['portfolio_value']) / peak if peak > 0 else 0
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_beta_alpha(self, portfolio_returns: List[float], benchmark_data: List[Dict]) -> tuple:
        """Calculate beta and alpha relative to benchmark"""
        if len(portfolio_returns) < 2 or len(benchmark_data) < 2:
            return 0, 0
        
        # Calculate benchmark returns
        benchmark_returns = []
        for i in range(1, len(benchmark_data)):
            prev_val = benchmark_data[i-1]['value']
            curr_val = benchmark_data[i]['value']
            bench_return = (curr_val - prev_val) / prev_val if prev_val > 0 else 0
            benchmark_returns.append(bench_return)
        
        # Align data lengths
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]
        
        if len(portfolio_returns) < 2:
            return 0, 0
        
        # Calculate beta
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        # Calculate alpha
        portfolio_return = np.mean(portfolio_returns) * 252
        benchmark_return = np.mean(benchmark_returns) * 252
        alpha = portfolio_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
        
        return beta, alpha
    
    def _calculate_correlation_matrix(self, holdings: List[Dict]) -> Dict[str, float]:
        """Calculate correlation matrix for portfolio holdings"""
        # Simplified correlation calculation
        symbols = [h['symbol'] for h in holdings]
        correlation_matrix = {}
        
        for i, symbol1 in enumerate(symbols):
            correlation_matrix[symbol1] = {}
            for j, symbol2 in enumerate(symbols):
                if i == j:
                    correlation_matrix[symbol1][symbol2] = 1.0
                else:
                    # Placeholder - would need historical price data for real calculation
                    correlation_matrix[symbol1][symbol2] = 0.3 + (hash(symbol1 + symbol2) % 100) / 200
        
        return correlation_matrix
    
    def _calculate_sector_allocation(self, holdings: List[Dict]) -> Dict[str, float]:
        """Calculate sector allocation percentages"""
        sector_totals = defaultdict(float)
        total_value = sum(h['market_value'] for h in holdings)
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            sector_totals[sector] += holding['market_value']
        
        return {sector: (value / total_value * 100) for sector, value in sector_totals.items()}
    
    def _calculate_asset_allocation(self, holdings: List[Dict]) -> Dict[str, float]:
        """Calculate asset allocation percentages"""
        asset_totals = defaultdict(float)
        total_value = sum(h['market_value'] for h in holdings)
        
        for holding in holdings:
            asset_type = holding.get('asset_type', 'Unknown')
            asset_totals[asset_type] += holding['market_value']
        
        return {asset_type: (value / total_value * 100) for asset_type, value in asset_totals.items()}

class RiskAnalysisEngine:
    """Advanced risk analysis and assessment"""
    
    def __init__(self):
        self.risk_factors = {
            'market_risk': 0.3,
            'credit_risk': 0.2,
            'liquidity_risk': 0.2,
            'operational_risk': 0.15,
            'concentration_risk': 0.15
        }
    
    async def analyze_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> RiskAnalysis:
        """Perform comprehensive risk analysis"""
        try:
            holdings = portfolio_data.get('holdings', [])
            total_value = sum(h['market_value'] for h in holdings)
            
            # Calculate various risk metrics
            volatility_risk = self._assess_volatility_risk(holdings)
            concentration_risk = self._assess_concentration_risk(holdings, total_value)
            currency_risk = self._assess_currency_risk(holdings)
            liquidity_risk = self._assess_liquidity_risk(holdings)
            
            # Calculate overall risk score
            portfolio_risk_score = (
                volatility_risk * 0.3 +
                concentration_risk * 0.25 +
                currency_risk * 0.2 +
                liquidity_risk * 0.25
            )
            
            # Sector-specific risks
            sector_risk = self._analyze_sector_risks(holdings)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(
                volatility_risk, concentration_risk, currency_risk, liquidity_risk
            )
            
            return RiskAnalysis(
                portfolio_risk_score=portfolio_risk_score,
                volatility_risk=volatility_risk,
                concentration_risk=concentration_risk,
                currency_risk=currency_risk,
                liquidity_risk=liquidity_risk,
                sector_risk=sector_risk,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _assess_volatility_risk(self, holdings: List[Dict]) -> float:
        """Assess volatility risk based on asset types and history"""
        # Simplified volatility risk calculation
        high_vol_assets = ['CRYPTO', 'OPTIONS', 'FUTURES']
        risk_score = 0
        
        for holding in holdings:
            if holding.get('asset_type') in high_vol_assets:
                risk_score += holding['market_value'] * 0.1
            else:
                risk_score += holding['market_value'] * 0.05
        
        total_value = sum(h['market_value'] for h in holdings)
        return min(risk_score / total_value, 1.0) if total_value > 0 else 0
    
    def _assess_concentration_risk(self, holdings: List[Dict], total_value: float) -> float:
        """Assess concentration risk"""
        if not holdings:
            return 0
        
        # Calculate Herfindahl-Hirschman Index for concentration
        weights = [h['market_value'] / total_value for h in holdings]
        hhi = sum(w**2 for w in weights)
        
        # Normalize to 0-1 scale
        return (hhi - 1/len(holdings)) / (1 - 1/len(holdings)) if len(holdings) > 1 else 1
    
    def _assess_currency_risk(self, holdings: List[Dict]) -> float:
        """Assess currency risk for international holdings"""
        currency_exposure = defaultdict(float)
        total_value = sum(h['market_value'] for h in holdings)
        
        for holding in holdings:
            currency = holding.get('currency', 'USD')
            if currency != 'USD':
                currency_exposure[currency] += holding['market_value']
        
        foreign_value = sum(currency_exposure.values())
        return foreign_value / total_value if total_value > 0 else 0
    
    def _assess_liquidity_risk(self, holdings: List[Dict]) -> float:
        """Assess liquidity risk based on asset types and volumes"""
        illiquid_assets = ['REAL_ESTATE', 'PRIVATE_EQUITY', 'COLLECTIBLES']
        illiquid_value = 0
        total_value = sum(h['market_value'] for h in holdings)
        
        for holding in holdings:
            if holding.get('asset_type') in illiquid_assets:
                illiquid_value += holding['market_value']
        
        return illiquid_value / total_value if total_value > 0 else 0
    
    def _analyze_sector_risks(self, holdings: List[Dict]) -> Dict[str, float]:
        """Analyze sector-specific risks"""
        sector_risk_scores = {
            'Technology': 0.7,
            'Healthcare': 0.4,
            'Finance': 0.6,
            'Energy': 0.8,
            'Consumer': 0.3,
            'Industrial': 0.5,
            'Utilities': 0.2,
            'Real Estate': 0.6,
            'Materials': 0.7,
            'Unknown': 0.5
        }
        
        sector_exposure = defaultdict(float)
        total_value = sum(h['market_value'] for h in holdings)
        
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            sector_exposure[sector] += holding['market_value']
        
        sector_risks = {}
        for sector, exposure in sector_exposure.items():
            base_risk = sector_risk_scores.get(sector, 0.5)
            concentration_factor = exposure / total_value if total_value > 0 else 0
            sector_risks[sector] = base_risk * concentration_factor
        
        return sector_risks
    
    def _generate_risk_recommendations(self, volatility_risk: float, 
                                     concentration_risk: float, 
                                     currency_risk: float, 
                                     liquidity_risk: float) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if volatility_risk > 0.7:
            recommendations.append("Consider reducing exposure to high-volatility assets")
        
        if concentration_risk > 0.6:
            recommendations.append("Diversify portfolio to reduce concentration risk")
        
        if currency_risk > 0.4:
            recommendations.append("Consider currency hedging for international exposure")
        
        if liquidity_risk > 0.5:
            recommendations.append("Increase allocation to liquid assets for better flexibility")
        
        if not recommendations:
            recommendations.append("Portfolio risk profile appears well-balanced")
        
        return recommendations

class PerformanceAnalysisEngine:
    """Advanced performance analysis and benchmarking"""
    
    def __init__(self):
        self.benchmarks = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ 100',
            'DIA': 'Dow Jones',
            'VTI': 'Total Stock Market',
            'BND': 'Total Bond Market'
        }
    
    async def analyze_performance(self, portfolio_data: Dict[str, Any]) -> PerformanceMetrics:
        """Perform comprehensive performance analysis"""
        try:
            historical_data = portfolio_data.get('historical_data', [])
            benchmark_data = portfolio_data.get('benchmark_data', [])
            
            if len(historical_data) < 2:
                raise ValueError("Insufficient historical data for analysis")
            
            # Calculate returns
            returns = self._calculate_returns_series(historical_data)
            total_return = returns[-1] if returns else 0
            
            # Annualized metrics
            days = len(historical_data)
            annualized_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
            
            # Risk metrics
            volatility = np.std(returns) * np.sqrt(252) if returns else 0
            downside_returns = [r for r in returns if r < 0]
            downside_volatility = np.std(downside_returns) * np.sqrt(252) if downside_returns else 0
            
            # Performance ratios
            risk_free_rate = 0.02
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
            sortino_ratio = (annualized_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
            
            # Drawdown metrics
            max_drawdown = self._calculate_max_drawdown(historical_data)
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Benchmark comparison
            beta, alpha, tracking_error, information_ratio = self._benchmark_comparison(
                returns, benchmark_data
            )
            
            return PerformanceMetrics(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_drawdown,
                calmar_ratio=calmar_ratio,
                beta=beta,
                alpha=alpha,
                information_ratio=information_ratio,
                tracking_error=tracking_error
            )
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _calculate_returns_series(self, historical_data: List[Dict]) -> List[float]:
        """Calculate returns series from historical data"""
        if len(historical_data) < 2:
            return []
        
        returns = []
        base_value = historical_data[0]['portfolio_value']
        
        for data in historical_data[1:]:
            current_value = data['portfolio_value']
            period_return = (current_value - base_value) / base_value if base_value > 0 else 0
            returns.append(period_return)
        
        return returns
    
    def _calculate_max_drawdown(self, historical_data: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if len(historical_data) < 2:
            return 0
        
        peak = historical_data[0]['portfolio_value']
        max_dd = 0
        
        for data in historical_data[1:]:
            if data['portfolio_value'] > peak:
                peak = data['portfolio_value']
            else:
                drawdown = (peak - data['portfolio_value']) / peak if peak > 0 else 0
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _benchmark_comparison(self, portfolio_returns: List[float], 
                            benchmark_data: List[Dict]) -> tuple:
        """Compare portfolio performance against benchmark"""
        if len(benchmark_data) < 2:
            return 1.0, 0.0, 0.0, 0.0
        
        # Calculate benchmark returns
        benchmark_returns = []
        for i in range(1, len(benchmark_data)):
            prev_val = benchmark_data[i-1]['value']
            curr_val = benchmark_data[i]['value']
            bench_return = (curr_val - prev_val) / prev_val if prev_val > 0 else 0
            benchmark_returns.append(bench_return)
        
        # Align data
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]
        
        if len(portfolio_returns) < 2:
            return 1.0, 0.0, 0.0, 0.0
        
        # Beta calculation
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        
        # Alpha calculation
        portfolio_mean = np.mean(portfolio_returns) * 252
        benchmark_mean = np.mean(benchmark_returns) * 252
        risk_free_rate = 0.02
        alpha = portfolio_mean - (risk_free_rate + beta * (benchmark_mean - risk_free_rate))
        
        # Tracking Error
        tracking_error = np.std([p - b for p, b in zip(portfolio_returns, benchmark_returns)]) * np.sqrt(252)
        
        # Information Ratio
        information_ratio = alpha / tracking_error if tracking_error > 0 else 0
        
        return beta, alpha, tracking_error, information_ratio

# Initialize services
portfolio_analytics = PortfolioAnalyticsEngine()
risk_analyzer = RiskAnalysisEngine()
performance_analyzer = PerformanceAnalysisEngine()

# API Endpoints
@app.post("/api/v1/portfolio/metrics")
async def get_portfolio_metrics(request: PortfolioRequest,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get comprehensive portfolio metrics"""
    try:
        # Mock portfolio data - would come from portfolio service
        portfolio_data = {
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'market_value': 50000,
                    'cost_basis': 45000,
                    'sector': 'Technology',
                    'asset_type': 'EQUITY',
                    'currency': 'USD'
                },
                {
                    'symbol': 'BTC',
                    'market_value': 30000,
                    'cost_basis': 25000,
                    'sector': 'Cryptocurrency',
                    'asset_type': 'CRYPTO',
                    'currency': 'USD'
                }
            ],
            'historical_data': [
                {'date': '2024-01-01', 'portfolio_value': 70000},
                {'date': '2024-01-02', 'portfolio_value': 72000},
                {'date': '2024-01-03', 'portfolio_value': 75000},
                {'date': '2024-01-04', 'portfolio_value': 73000},
                {'date': '2024-01-05', 'portfolio_value': 78000}
            ],
            'benchmark_data': [
                {'date': '2024-01-01', 'value': 100},
                {'date': '2024-01-02', 'value': 101},
                {'date': '2024-01-03', 'value': 102},
                {'date': '2024-01-04', 'value': 101.5},
                {'date': '2024-01-05', 'value': 103}
            ]
        }
        
        metrics = await portfolio_analytics.calculate_portfolio_metrics(portfolio_data)
        
        return {
            "success": True,
            "data": {
                "portfolio_id": request.portfolio_id,
                "timeframe": request.timeframe,
                "metrics": {
                    "total_value": metrics.total_value,
                    "total_return": metrics.total_return,
                    "daily_return": metrics.daily_return,
                    "volatility": metrics.volatility,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "max_drawdown": metrics.max_drawdown,
                    "beta": metrics.beta,
                    "alpha": metrics.alpha,
                    "var_95": metrics.var_95,
                    "var_99": metrics.var_99,
                    "sector_allocation": metrics.sector_allocation,
                    "asset_allocation": metrics.asset_allocation
                },
                "risk_analysis": await risk_analyzer.analyze_portfolio_risk(portfolio_data),
                "performance_metrics": await performance_analyzer.analyze_performance(portfolio_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio metrics endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/risk-analysis")
async def get_risk_analysis(request: PortfolioRequest,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get detailed risk analysis"""
    try:
        # Mock data
        portfolio_data = {
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'market_value': 50000,
                    'sector': 'Technology',
                    'asset_type': 'EQUITY',
                    'currency': 'USD'
                }
            ]
        }
        
        risk_analysis = await risk_analyzer.analyze_portfolio_risk(portfolio_data)
        
        return {
            "success": True,
            "data": risk_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in risk analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/performance-analysis")
async def get_performance_analysis(request: PortfolioRequest,
                                  credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get detailed performance analysis"""
    try:
        # Mock data
        portfolio_data = {
            'historical_data': [
                {'date': '2024-01-01', 'portfolio_value': 70000},
                {'date': '2024-01-02', 'portfolio_value': 72000},
                {'date': '2024-01-03', 'portfolio_value': 75000},
                {'date': '2024-01-04', 'portfolio_value': 73000},
                {'date': '2024-01-05', 'portfolio_value': 78000}
            ],
            'benchmark_data': [
                {'date': '2024-01-01', 'value': 100},
                {'date': '2024-01-02', 'value': 101},
                {'date': '2024-01-03', 'value': 102},
                {'date': '2024-01-04', 'value': 101.5},
                {'date': '2024-01-05', 'value': 103}
            ]
        }
        
        performance = await performance_analyzer.analyze_performance(portfolio_data)
        
        return {
            "success": True,
            "data": performance
        }
        
    except Exception as e:
        logger.error(f"Error in performance analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/rebalance-recommendations")
async def get_rebalance_recommendations(request: PortfolioRequest,
                                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get portfolio rebalancing recommendations"""
    try:
        # Mock rebalancing logic
        recommendations = [
            RebalanceRecommendation(
                symbol="AAPL",
                current_weight=0.65,
                target_weight=0.60,
                recommended_action="SELL",
                quantity=5,
                estimated_cost=850.0,
                priority=1
            ),
            RebalanceRecommendation(
                symbol="MSFT",
                current_weight=0.15,
                target_weight=0.20,
                recommended_action="BUY",
                quantity=8,
                estimated_cost=3200.0,
                priority=2
            )
        ]
        
        return {
            "success": True,
            "data": {
                "rebalance_required": True,
                "recommendations": [r.__dict__ for r in recommendations],
                "estimated_cost": sum(r.estimated_cost for r in recommendations),
                "target_allocation": {
                    "Technology": 0.40,
                    "Healthcare": 0.20,
                    "Finance": 0.15,
                    "Consumer": 0.15,
                    "Bonds": 0.10
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error in rebalance recommendations endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/tax-optimization")
async def get_tax_optimization(request: PortfolioRequest,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get tax optimization recommendations"""
    try:
        tax_optimization = TaxOptimization(
            tax_loss_harvesting_opportunities=[
                {
                    "symbol": "NVDA",
                    "unrealized_loss": -2500,
                    "potential_tax_savings": 600,
                    "recommendation": "Consider selling to realize tax loss"
                }
            ],
            wash_sale_warnings=[
                {
                    "symbol": "AAPL",
                    "warning": "Recently purchased similar AAPL position",
                    "recommendation": "Wait 30 days before repurchasing"
                }
            ],
            tax_efficiency_score=0.75,
            recommendations=[
                "Consider tax-loss harvesting on underperforming positions",
                "Utilize tax-advantaged accounts for high-growth assets",
                "Review holding periods for long-term capital gains"
            ]
        )
        
        return {
            "success": True,
            "data": tax_optimization.__dict__
        }
        
    except Exception as e:
        logger.error(f"Error in tax optimization endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "advanced-portfolio-analytics"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)