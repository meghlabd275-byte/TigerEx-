"""
Options Trading Support System
Complete options pricing, Greeks calculation, and automated trading
"""

import asyncio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import yfinance as yf
import requests
import json
from decimal import Decimal
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class OptionStyle(Enum):
    EUROPEAN = "european"
    AMERICAN = "american"

class ExerciseStyle(Enum):
    VANILLA = "vanilla"
    BINARY = "binary"
    ASIAN = "asian"
    BARRIER = "barrier"

@dataclass
class OptionContract:
    symbol: str
    underlying: str
    option_type: OptionType
    strike: float
    expiration: datetime
    style: OptionStyle
    exercise_style: ExerciseStyle
    multiplier: float = 100.0
    last_price: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    volume: int = 0
    open_interest: int = 0
    implied_volatility: float = 0.0
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0
    timestamp: datetime = None

@dataclass
class OptionPosition:
    contract: OptionContract
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    entry_date: datetime
    last_updated: datetime

@dataclass
class OptionStrategy:
    name: str
    positions: List[OptionPosition]
    max_profit: float
    max_loss: float
    break_even_points: List[float]
    payoff_at_expiration: callable
    current_greeks: Dict[str, float]
    margin_requirement: float

@dataclass
class VolatilitySurface:
    strikes: np.ndarray
    expirations: np.ndarray
    implied_volatilities: np.ndarray
    risk_free_rate: float
    underlying_price: float

class BlackScholesModel:
    """Black-Scholes option pricing model"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_price(
        self,
        S: float,  # Underlying price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        r: float,  # Risk-free rate
        sigma: float,  # Volatility
        option_type: OptionType
    ) -> float:
        """Calculate option price using Black-Scholes formula"""
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == OptionType.CALL:
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return price
    
    def calculate_greeks(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType
    ) -> Dict[str, float]:
        """Calculate option Greeks"""
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Delta
        if option_type == OptionType.CALL:
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
        
        # Gamma
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # Theta
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        if option_type == OptionType.CALL:
            theta -= r * K * np.exp(-r * T) * norm.cdf(d2)
        else:
            theta += r * K * np.exp(-r * T) * norm.cdf(-d2)
        theta /= 365  # Convert to daily theta
        
        # Vega
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        # Rho
        if option_type == OptionType.CALL:
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def calculate_implied_volatility(
        self,
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: OptionType,
        initial_guess: float = 0.2,
        tolerance: float = 1e-6,
        max_iterations: int = 100
    ) -> float:
        """Calculate implied volatility using Newton-Raphson method"""
        
        sigma = initial_guess
        
        for _ in range(max_iterations):
            price = self.calculate_price(S, K, T, r, sigma, option_type)
            diff = price - market_price
            
            if abs(diff) < tolerance:
                return sigma
            
            # Calculate vega for Newton-Raphson
            d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            vega = S * norm.pdf(d1) * np.sqrt(T)
            
            if vega == 0:
                break
            
            sigma = sigma - diff / vega
            sigma = max(0.01, sigma)  # Keep sigma positive
        
        return sigma

class BinomialTreeModel:
    """Binomial tree model for American options"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
    
    def calculate_price(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType,
        style: OptionStyle,
        n_steps: int = 100
    ) -> float:
        """Calculate option price using binomial tree"""
        
        dt = T / n_steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r * dt) - d) / (u - d)
        
        # Initialize stock prices at maturity
        stock_prices = np.zeros(n_steps + 1)
        for i in range(n_steps + 1):
            stock_prices[i] = S * (u ** (n_steps - 2 * i))
        
        # Initialize option values at maturity
        option_values = np.zeros(n_steps + 1)
        for i in range(n_steps + 1):
            if option_type == OptionType.CALL:
                option_values[i] = max(0, stock_prices[i] - K)
            else:
                option_values[i] = max(0, K - stock_prices[i])
        
        # Work backwards through the tree
        for j in range(n_steps - 1, -1, -1):
            for i in range(j + 1):
                stock_price = S * (u ** (j - 2 * i))
                
                # Expected value
                holding_value = np.exp(-r * dt) * (p * option_values[i] + (1 - p) * option_values[i + 1])
                
                # Early exercise value (for American options)
                if style == OptionStyle.AMERICAN:
                    if option_type == OptionType.CALL:
                        exercise_value = max(0, stock_price - K)
                    else:
                        exercise_value = max(0, K - stock_price)
                    
                    option_values[i] = max(holding_value, exercise_value)
                else:
                    option_values[i] = holding_value
        
        return option_values[0]

class VolatilityModel:
    """Volatility modeling and forecasting"""
    
    def __init__(self):
        self.historical_volatility = None
        self.garch_model = None
    
    def calculate_historical_volatility(
        self,
        prices: pd.Series,
        window: int = 252,
        trading_days: int = 252
    ) -> float:
        """Calculate historical volatility"""
        
        returns = np.log(prices / prices.shift(1)).dropna()
        volatility = returns.rolling(window=window).std() * np.sqrt(trading_days)
        
        self.historical_volatility = volatility.iloc[-1] if not volatility.empty else 0.0
        return self.historical_volatility
    
    def garch_forecast(
        self,
        returns: pd.Series,
        forecast_horizon: int = 30
    ) -> pd.Series:
        """GARCH volatility forecast (simplified implementation)"""
        
        # Simple EWMA volatility as GARCH approximation
        lambda_param = 0.94
        squared_returns = returns ** 2
        
        # Initialize
        forecast = []
        current_variance = squared_returns.rolling(window=22).mean().iloc[-1]
        
        for _ in range(forecast_horizon):
            forecast.append(np.sqrt(current_variance))
            current_variance = lambda_param * current_variance + (1 - lambda_param) * squared_returns.mean()
        
        return pd.Series(forecast)

class OptionsPricer:
    """Advanced options pricing system"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.black_scholes = BlackScholesModel(risk_free_rate)
        self.binomial = BinomialTreeModel(risk_free_rate)
        self.volatility_model = VolatilityModel()
        self.volatility_surface = None
    
    async def price_option(
        self,
        contract: OptionContract,
        underlying_price: float,
        volatility: float
    ) -> Dict[str, Any]:
        """Price an option contract"""
        
        time_to_expiration = (contract.expiration - datetime.now()).days / 365.0
        
        if time_to_expiration <= 0:
            return {'price': 0.0, 'greeks': {}}
        
        # Choose pricing model
        if contract.style == OptionStyle.EUROPEAN:
            price = self.black_scholes.calculate_price(
                underlying_price,
                contract.strike,
                time_to_expiration,
                self.black_scholes.risk_free_rate,
                volatility,
                contract.option_type
            )
            
            greeks = self.black_scholes.calculate_greeks(
                underlying_price,
                contract.strike,
                time_to_expiration,
                self.black_scholes.risk_free_rate,
                volatility,
                contract.option_type
            )
        else:  # American
            price = self.binomial.calculate_price(
                underlying_price,
                contract.strike,
                time_to_expiration,
                self.black_scholes.risk_free_rate,
                volatility,
                contract.option_type,
                contract.style
            )
            
            # Approximate Greeks using finite differences
            greeks = self._calculate_numerical_greeks(
                contract, underlying_price, time_to_expiration, volatility
            )
        
        return {
            'price': price,
            'greeks': greeks,
            'model': 'black_scholes' if contract.style == OptionStyle.EUROPEAN else 'binomial'
        }
    
    def _calculate_numerical_greeks(
        self,
        contract: OptionContract,
        S: float,
        T: float,
        sigma: float,
        epsilon: float = 0.01
    ) -> Dict[str, float]:
        """Calculate Greeks using finite differences"""
        
        r = self.black_scholes.risk_free_rate
        
        # Delta
        price_up = self.binomial.calculate_price(S * (1 + epsilon), contract.strike, T, r, sigma, contract.option_type, contract.style)
        price_down = self.binomial.calculate_price(S * (1 - epsilon), contract.strike, T, r, sigma, contract.option_type, contract.style)
        delta = (price_up - price_down) / (2 * epsilon * S)
        
        # Gamma
        price_center = self.binomial.calculate_price(S, contract.strike, T, r, sigma, contract.option_type, contract.style)
        gamma = (price_up - 2 * price_center + price_down) / ((epsilon * S) ** 2)
        
        # Theta
        if T > epsilon / 365:
            price_t_minus = self.binomial.calculate_price(S, contract.strike, T - epsilon / 365, r, sigma, contract.option_type, contract.style)
            theta = (price_t_minus - price_center) / epsilon
        else:
            theta = 0
        
        # Vega
        price_sigma_up = self.binomial.calculate_price(S, contract.strike, T, r, sigma * (1 + epsilon), contract.option_type, contract.style)
        price_sigma_down = self.binomial.calculate_price(S, contract.strike, T, r, sigma * (1 - epsilon), contract.option_type, contract.style)
        vega = (price_sigma_up - price_sigma_down) / (2 * epsilon * sigma)
        
        # Rho
        price_r_up = self.binomial.calculate_price(S, contract.strike, T, r * (1 + epsilon), sigma, contract.option_type, contract.style)
        price_r_down = self.binomial.calculate_price(S, contract.strike, T, r * (1 - epsilon), sigma, contract.option_type, contract.style)
        rho = (price_r_up - price_r_down) / (2 * epsilon * r)
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def calculate_volatility_surface(
        self,
        option_chain: List[OptionContract],
        underlying_price: float
    ) -> VolatilitySurface:
        """Build implied volatility surface"""
        
        strikes = sorted(set([contract.strike for contract in option_chain]))
        expirations = sorted(set([contract.expiration for contract in option_chain]))
        
        # Create volatility matrix
        vol_matrix = np.zeros((len(expirations), len(strikes)))
        
        for i, expiration in enumerate(expirations):
            for j, strike in enumerate(strikes):
                # Find matching option
                matching_options = [
                    opt for opt in option_chain 
                    if opt.expiration == expiration and opt.strike == strike
                ]
                
                if matching_options:
                    # Use average implied volatility
                    vol = np.mean([opt.implied_volatility for opt in matching_options if opt.implied_volatility > 0])
                    vol_matrix[i, j] = vol if vol > 0 else self._extrapolate_volatility(
                        strike, expiration, underlying_price, strikes, expirations, vol_matrix
                    )
        
        return VolatilitySurface(
            strikes=np.array(strikes),
            expirations=np.array(expirations),
            implied_volatilities=vol_matrix,
            risk_free_rate=self.black_scholes.risk_free_rate,
            underlying_price=underlying_price
        )
    
    def _extrapolate_volatility(
        self,
        strike: float,
        expiration: datetime,
        underlying_price: float,
        strikes: List[float],
        expirations: List[datetime],
        vol_matrix: np.ndarray
    ) -> float:
        """Extrapolate volatility for missing points"""
        # Simple linear interpolation/extrapolation
        # In practice, would use more sophisticated methods
        
        # Find nearest strikes
        if len(strikes) < 2:
            return 0.2  # Default volatility
        
        # Linear interpolation in strike dimension
        if strike < strikes[0]:
            return vol_matrix[0, 0] if vol_matrix[0, 0] > 0 else 0.2
        elif strike > strikes[-1]:
            return vol_matrix[0, -1] if vol_matrix[0, -1] > 0 else 0.2
        else:
            # Find surrounding strikes
            lower_idx = np.searchsorted(strikes, strike) - 1
            upper_idx = lower_idx + 1
            
            if upper_idx >= len(strikes):
                return vol_matrix[0, lower_idx] if vol_matrix[0, lower_idx] > 0 else 0.2
            
            # Interpolate
            weight = (strike - strikes[lower_idx]) / (strikes[upper_idx] - strikes[lower_idx])
            lower_vol = vol_matrix[0, lower_idx] if vol_matrix[0, lower_idx] > 0 else 0.2
            upper_vol = vol_matrix[0, upper_idx] if vol_matrix[0, upper_idx] > 0 else 0.2
            
            return lower_vol + weight * (upper_vol - lower_vol)

class OptionsStrategyBuilder:
    """Build and analyze options strategies"""
    
    def __init__(self, pricer: OptionsPricer):
        self.pricer = pricer
    
    def create_covered_call(
        self,
        underlying_price: float,
        strike: float,
        expiration: datetime,
        quantity: int = 100
    ) -> OptionStrategy:
        """Create covered call strategy"""
        
        # Create call option contract
        call_contract = OptionContract(
            symbol=f"CALL_{strike}_{expiration.strftime('%Y%m%d')}",
            underlying="STOCK",
            option_type=OptionType.CALL,
            strike=strike,
            expiration=expiration,
            style=OptionStyle.AMERICAN,
            exercise_style=ExerciseStyle.VANILLA
        )
        
        # Price the option
        pricing_result = await self.pricer.price_option(call_contract, underlying_price, 0.25)
        option_price = pricing_result['price']
        
        # Create positions
        stock_position = OptionPosition(
            contract=None,  # Stock position
            quantity=quantity,
            entry_price=underlying_price,
            current_price=underlying_price,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            entry_date=datetime.now(),
            last_updated=datetime.now()
        )
        
        call_position = OptionPosition(
            contract=call_contract,
            quantity=-quantity,
            entry_price=option_price,
            current_price=option_price,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            entry_date=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Strategy payoff function
        def covered_call_payoff(underlying_at_expiration):
            stock_pnl = (underlying_at_expiration - underlying_price) * quantity
            option_pnl = max(0, underlying_at_expiration - strike) * -quantity
            return stock_pnl + option_pnl
        
        return OptionStrategy(
            name="Covered Call",
            positions=[stock_position, call_position],
            max_profit=(strike - underlying_price + option_price) * quantity,
            max_loss=(underlying_price - option_price) * quantity,
            break_even_points=[underlying_price - option_price],
            payoff_at_expiration=covered_call_payoff,
            current_greeks={
                'delta': quantity + call_position.quantity * pricing_result['greeks']['delta'],
                'gamma': call_position.quantity * pricing_result['greeks']['gamma'],
                'theta': call_position.quantity * pricing_result['greeks']['theta'],
                'vega': call_position.quantity * pricing_result['greeks']['vega'],
                'rho': call_position.quantity * pricing_result['greeks']['rho']
            },
            margin_requirement=0
        )
    
    def create_iron_condor(
        self,
        underlying_price: float,
        lower_put_strike: float,
        upper_put_strike: float,
        lower_call_strike: float,
        upper_call_strike: float,
        expiration: datetime,
        quantity: int = 10
    ) -> OptionStrategy:
        """Create iron condor strategy"""
        
        strikes = [lower_put_strike, upper_put_strike, lower_call_strike, upper_call_strike]
        option_types = [OptionType.PUT, OptionType.PUT, OptionType.CALL, OptionType.CALL]
        quantities = [quantity, -quantity, -quantity, quantity]  # Sell middle strikes, buy outer strikes
        
        positions = []
        net_credit = 0
        total_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
        for i, (strike, opt_type, qty) in enumerate(zip(strikes, option_types, quantities)):
            contract = OptionContract(
                symbol=f"{opt_type.value.upper()}_{strike}_{expiration.strftime('%Y%m%d')}",
                underlying="STOCK",
                option_type=opt_type,
                strike=strike,
                expiration=expiration,
                style=OptionStyle.AMERICAN,
                exercise_style=ExerciseStyle.VANILLA
            )
            
            # Price the option
            pricing_result = await self.pricer.price_option(contract, underlying_price, 0.25)
            option_price = pricing_result['price']
            
            position = OptionPosition(
                contract=contract,
                quantity=qty,
                entry_price=option_price,
                current_price=option_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                entry_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            positions.append(position)
            net_credit += qty * option_price
            
            # Add to total Greeks
            for greek in total_greeks:
                total_greeks[greek] += qty * pricing_result['greeks'][greek]
        
        # Iron condor payoff function
        def iron_condor_payoff(underlying_at_expiration):
            payoff = 0
            for position in positions:
                if position.contract.option_type == OptionType.CALL:
                    option_payout = max(0, underlying_at_expiration - position.contract.strike)
                else:
                    option_payout = max(0, position.contract.strike - underlying_at_expiration)
                
                payoff += option_payout * position.quantity
            
            return payoff + net_credit
        
        return OptionStrategy(
            name="Iron Condor",
            positions=positions,
            max_profit=net_credit * 100 * quantity,  # Convert to actual dollar amount
            max_loss=(upper_call_strike - lower_call_strike - net_credit * 100) * quantity,
            break_even_points=[lower_put_strike - net_credit * 100, upper_call_strike + net_credit * 100],
            payoff_at_expiration=iron_condor_payoff,
            current_greeks=total_greeks,
            margin_requirement=(upper_call_strike - lower_call_strike) * quantity * 100
        )
    
    def create_straddle(
        self,
        underlying_price: float,
        strike: float,
        expiration: datetime,
        quantity: int = 10
    ) -> OptionStrategy:
        """Create straddle strategy"""
        
        # Create call and put options
        call_contract = OptionContract(
            symbol=f"CALL_{strike}_{expiration.strftime('%Y%m%d')}",
            underlying="STOCK",
            option_type=OptionType.CALL,
            strike=strike,
            expiration=expiration,
            style=OptionStyle.AMERICAN,
            exercise_style=ExerciseStyle.VANILLA
        )
        
        put_contract = OptionContract(
            symbol=f"PUT_{strike}_{expiration.strftime('%Y%m%d')}",
            underlying="STOCK",
            option_type=OptionType.PUT,
            strike=strike,
            expiration=expiration,
            style=OptionStyle.AMERICAN,
            exercise_style=ExerciseStyle.VANILLA
        )
        
        positions = []
        total_cost = 0
        total_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
        for contract in [call_contract, put_contract]:
            pricing_result = await self.pricer.price_option(contract, underlying_price, 0.25)
            option_price = pricing_result['price']
            
            position = OptionPosition(
                contract=contract,
                quantity=quantity,
                entry_price=option_price,
                current_price=option_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                entry_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            positions.append(position)
            total_cost += option_price * quantity
            
            # Add to total Greeks
            for greek in total_greeks:
                total_greeks[greek] += quantity * pricing_result['greeks'][greek]
        
        # Straddle payoff function
        def straddle_payoff(underlying_at_expiration):
            call_payout = max(0, underlying_at_expiration - strike)
            put_payout = max(0, strike - underlying_at_expiration)
            return (call_payout + put_payout - total_cost) * quantity
        
        return OptionStrategy(
            name="Straddle",
            positions=positions,
            max_profit=float('inf'),  # Unlimited upside
            max_loss=total_cost * quantity * 100,
            break_even_points=[strike - total_cost * 100 / quantity, strike + total_cost * 100 / quantity],
            payoff_at_expiration=straddle_payoff,
            current_greeks=total_greeks,
            margin_requirement=total_cost * quantity * 100
        )

class OptionsRiskManager:
    """Options position risk management"""
    
    def __init__(self, pricer: OptionsPricer):
        self.pricer = pricer
        self.position_limits = {
            'max_total_delta': 1000,
            'max_total_gamma': 500,
            'max_total_vega': 10000,
            'max_total_theta': -5000,
            'max_position_size': 100,
            'max_concentration': 0.2
        }
    
    def calculate_portfolio_greeks(self, strategies: List[OptionStrategy]) -> Dict[str, float]:
        """Calculate portfolio-level Greeks"""
        
        total_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
        for strategy in strategies:
            for greek in total_greeks:
                total_greeks[greek] += strategy.current_greeks.get(greek, 0)
        
        return total_greeks
    
    def check_risk_limits(self, strategies: List[OptionStrategy]) -> Dict[str, Any]:
        """Check if portfolio is within risk limits"""
        
        portfolio_greeks = self.calculate_portfolio_greeks(strategies)
        violations = []
        
        # Check Greek limits
        for greek, limit in self.position_limits.items():
            if greek.startswith('max_total_'):
                greek_name = greek.replace('max_total_', '')
                current_value = portfolio_greeks.get(greek_name, 0)
                
                if abs(current_value) > limit:
                    violations.append({
                        'type': 'greek_limit',
                        'greek': greek_name,
                        'current_value': current_value,
                        'limit': limit,
                        'violation': abs(current_value) - limit
                    })
        
        # Check position concentration
        total_positions = sum(len(strategy.positions) for strategy in strategies)
        underlying_concentration = {}
        
        for strategy in strategies:
            for position in strategy.positions:
                if position.contract:
                    underlying = position.contract.underlying
                    underlying_concentration[underlying] = underlying_concentration.get(underlying, 0) + abs(position.quantity)
        
        for underlying, concentration in underlying_concentration.items():
            concentration_ratio = concentration / total_positions if total_positions > 0 else 0
            if concentration_ratio > self.position_limits['max_concentration']:
                violations.append({
                    'type': 'concentration_limit',
                    'underlying': underlying,
                    'current_concentration': concentration_ratio,
                    'limit': self.position_limits['max_concentration'],
                    'violation': concentration_ratio - self.position_limits['max_concentration']
                })
        
        return {
            'portfolio_greeks': portfolio_greeks,
            'violations': violations,
            'within_limits': len(violations) == 0
        }
    
    def calculate_var(
        self,
        strategies: List[OptionStrategy],
        underlying_price: float,
        confidence_level: float = 0.05
    ) -> float:
        """Calculate Value at Risk for options portfolio"""
        
        # Monte Carlo simulation for portfolio VaR
        n_simulations = 10000
        time_horizon = 1  # 1 day
        
        # Generate price scenarios
        np.random.seed(42)
        returns = np.random.normal(0, 0.02, n_simulations)  # 2% daily volatility
        price_scenarios = underlying_price * (1 + returns)
        
        portfolio_values = []
        
        for price in price_scenarios:
            portfolio_value = 0
            
            for strategy in strategies:
                # Simplified valuation - would use full pricing model
                for position in strategy.positions:
                    if position.contract:
                        # Re-price option with new underlying
                        new_pricing = await self.pricer.price_option(
                            position.contract, price, 0.25
                        )
                        new_price = new_pricing['price']
                        pnl = (new_price - position.current_price) * position.quantity
                        portfolio_value += pnl
            
            portfolio_values.append(portfolio_value)
        
        # Calculate VaR
        var = np.percentile(portfolio_values, confidence_level * 100)
        
        return var

class OptionsMarketMaker:
    """Automated options market making system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pricer = OptionsPricer(config.get('risk_free_rate', 0.02))
        self.strategy_builder = OptionsStrategyBuilder(self.pricer)
        self.risk_manager = OptionsRiskManager(self.pricer)
        self.positions = []
        self.active_orders = []
    
    async def initialize(self):
        """Initialize the market maker"""
        logger.info("Initializing Options Market Maker")
        
        # Load existing positions
        await self._load_positions()
        
        logger.info("Options Market Maker initialized")
    
    async def _load_positions(self):
        """Load existing option positions"""
        # This would load from database
        pass
    
    async def market_make_options(
        self,
        underlying_symbol: str,
        expiration_dates: List[datetime],
        strike_range: Tuple[float, float],
        strike_spacing: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Create market making orders for options"""
        
        market_orders = []
        
        # Get current underlying price
        underlying_price = await self._get_underlying_price(underlying_symbol)
        
        for expiration in expiration_dates:
            # Generate strikes
            strikes = np.arange(
                strike_range[0],
                strike_range[1] + strike_spacing,
                strike_spacing
            )
            
            for strike in strikes:
                # Create both call and put options
                for option_type in [OptionType.CALL, OptionType.PUT]:
                    contract = OptionContract(
                        symbol=f"{option_type.value.upper()}_{underlying_symbol}_{strike}_{expiration.strftime('%Y%m%d')}",
                        underlying=underlying_symbol,
                        option_type=option_type,
                        strike=strike,
                        expiration=expiration,
                        style=OptionStyle.AMERICAN,
                        exercise_style=ExerciseStyle.VANILLA
                    )
                    
                    # Price the option
                    pricing_result = await self.pricer.price_option(contract, underlying_price, 0.25)
                    theoretical_price = pricing_result['price']
                    
                    # Create bid/ask spread
                    spread_percentage = 0.05  # 5% spread
                    bid_price = theoretical_price * (1 - spread_percentage / 2)
                    ask_price = theoretical_price * (1 + spread_percentage / 2)
                    
                    # Calculate size based on risk limits
                    size = self._calculate_order_size(contract, pricing_result['greeks'])
                    
                    market_orders.append({
                        'contract': contract,
                        'bid_price': bid_price,
                        'ask_price': ask_price,
                        'bid_size': size,
                        'ask_size': size,
                        'theoretical_price': theoretical_price,
                        'greeks': pricing_result['greeks']
                    })
        
        return market_orders
    
    async def _get_underlying_price(self, symbol: str) -> float:
        """Get current price of underlying asset"""
        # Mock implementation - would use real market data
        return 100.0
    
    def _calculate_order_size(self, contract: OptionContract, greeks: Dict[str, float]) -> int:
        """Calculate appropriate order size based on risk limits"""
        
        # Simple size calculation based on delta exposure
        max_delta_per_option = abs(greeks['delta'])
        max_total_delta = self.risk_manager.position_limits['max_total_delta']
        
        # Allow up to 10% of delta limit per option
        max_options_by_delta = int(max_total_delta * 0.1 / max_delta_per_option)
        
        # Also limit by position size
        max_by_position_limit = self.risk_manager.position_limits['max_position_size']
        
        return min(max_options_by_delta, max_by_position_limit, 50)  # Cap at 50
    
    async def delta_hedge_portfolio(self) -> List[Dict[str, Any]]:
        """Delta hedge the options portfolio"""
        
        hedge_actions = []
        
        # Calculate current portfolio delta
        portfolio_greeks = self.risk_manager.calculate_portfolio_greeks(
            [self._position_to_strategy(pos) for pos in self.positions]
        )
        
        current_delta = portfolio_greeks['delta']
        
        if abs(current_delta) > 100:  # Hedge if delta > 100
            # Calculate hedge quantity
            underlying_price = await self._get_underlying_price("STOCK")
            hedge_quantity = -current_delta
            
            # Determine hedge direction
            if hedge_quantity > 0:
                action = 'buy'
            else:
                action = 'sell'
                hedge_quantity = abs(hedge_quantity)
            
            hedge_actions.append({
                'action': action,
                'underlying': 'STOCK',
                'quantity': hedge_quantity,
                'price': underlying_price,
                'reason': 'delta_hedge',
                'current_delta': current_delta,
                'target_delta': 0
            })
        
        return hedge_actions
    
    def _position_to_strategy(self, position: OptionPosition) -> OptionStrategy:
        """Convert position to strategy for risk calculation"""
        # Simplified conversion
        return OptionStrategy(
            name=f"{position.contract.symbol}_position",
            positions=[position],
            max_profit=float('inf'),
            max_loss=float('inf'),
            break_even_points=[],
            payoff_at_expiration=lambda x: 0,
            current_greeks={},
            margin_requirement=0
        )
    
    async def_volatility_arbitrage(self, option_chain: List[OptionContract]) -> List[Dict[str, Any]]:
        """Find volatility arbitrage opportunities"""
        
        opportunities = []
        
        # Build volatility surface
        underlying_price = await self._get_underlying_price("STOCK")
        vol_surface = self.pricer.calculate_volatility_surface(option_chain, underlying_price)
        
        # Look for mispriced options
        for contract in option_chain:
            if contract.implied_volatility == 0:
                continue
            
            # Get theoretical volatility from surface
            theoretical_vol = self._get_theoretical_volatility(contract, vol_surface)
            
            # Check for significant deviation
            vol_diff = abs(contract.implied_volatility - theoretical_vol)
            
            if vol_diff > theoretical_vol * 0.1:  # 10% deviation
                # Determine if IV is too high or too low
                if contract.implied_volatility > theoretical_vol:
                    action = 'sell'
                    expected_profit = vol_diff * 100  # Simplified profit estimate
                else:
                    action = 'buy'
                    expected_profit = vol_diff * 100
                
                opportunities.append({
                    'type': 'volatility_arbitrage',
                    'contract': contract,
                    'action': action,
                    'current_iv': contract.implied_volatility,
                    'theoretical_iv': theoretical_vol,
                    'vol_difference': vol_diff,
                    'expected_profit': expected_profit,
                    'confidence': min(0.9, vol_diff / theoretical_vol)
                })
        
        # Sort by expected profit
        opportunities.sort(key=lambda x: x['expected_profit'], reverse=True)
        
        return opportunities
    
    def _get_theoretical_volatility(
        self,
        contract: OptionContract,
        vol_surface: VolatilitySurface
    ) -> float:
        """Get theoretical volatility from surface"""
        
        # Find nearest strike and expiration
        strike_idx = np.argmin(np.abs(vol_surface.strikes - contract.strike))
        exp_idx = np.argmin(np.abs(vol_surface.expirations - contract.expiration))
        
        return vol_surface.implied_volatilities[exp_idx, strike_idx]

# Main execution
async def main():
    # Configuration
    config = {
        'risk_free_rate': 0.02,
        'max_positions': 100,
        'max_risk': 10000.0
    }
    
    # Initialize market maker
    market_maker = OptionsMarketMaker(config)
    await market_maker.initialize()
    
    # Create market making orders
    expirations = [
        datetime.now() + timedelta(days=30),
        datetime.now() + timedelta(days=60),
        datetime.now() + timedelta(days=90)
    ]
    
    orders = await market_maker.market_make_options(
        underlying_symbol="AAPL",
        expiration_dates=expirations,
        strike_range=(150, 200),
        strike_spacing=5.0
    )
    
    logger.info(f"Created {len(orders)} market making orders")
    
    # Create example strategies
    underlying_price = 175.0
    strike = 175.0
    expiration = datetime.now() + timedelta(days=45)
    
    # Covered call
    covered_call = await market_maker.strategy_builder.create_covered_call(
        underlying_price, strike, expiration
    )
    logger.info(f"Created covered call with max profit: {covered_call.max_profit}")
    
    # Iron condor
    iron_condor = await market_maker.strategy_builder.create_iron_condor(
        underlying_price, 170, 165, 180, 185, expiration
    )
    logger.info(f"Created iron condor with max profit: {iron_condor.max_profit}")
    
    # Check risk limits
    risk_check = market_maker.risk_manager.check_risk_limits([covered_call, iron_condor])
    logger.info(f"Risk check passed: {risk_check['within_limits']}")

if __name__ == "__main__":
    asyncio.run(main())