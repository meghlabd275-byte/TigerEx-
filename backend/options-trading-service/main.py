"""
TigerEx Options Trading Service
Advanced options trading platform with multiple strategies
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx Options Trading Service", version="1.0.0")
security = HTTPBearer()

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class OptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    EXERCISED = "exercised"
    CLOSED = "closed"

class StrategyType(str, Enum):
    BUY_CALL = "buy_call"
    BUY_PUT = "buy_put"
    SELL_CALL = "sell_call"
    SELL_PUT = "sell_put"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    IRON_CONDOR = "iron_condor"
    BUTTERFLY_SPREAD = "butterfly_spread"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"

@dataclass
class OptionContract:
    symbol: str
    option_type: OptionType
    strike_price: float
    expiration_date: datetime
    premium: float
    volume: int
    open_interest: int
    implied_volatility: float

class OptionContractModel(BaseModel):
    symbol: str = Field(..., description="Underlying symbol (BTC, ETH, SOL)")
    option_type: OptionType = Field(..., description="Call or Put option")
    strike_price: float = Field(..., gt=0, description="Strike price")
    expiration_date: datetime = Field(..., description="Expiration date")
    premium: float = Field(..., gt=0, description="Option premium")
    volume: int = Field(default=0, ge=0, description="Trading volume")
    open_interest: int = Field(default=0, ge=0, description="Open interest")
    implied_volatility: float = Field(default=0.0, ge=0, le=5.0, description="Implied volatility")

class OptionPosition(BaseModel):
    id: str
    user_id: str
    contract: OptionContractModel
    position_size: int
    entry_price: float
    current_price: float
    pnl: float
    status: OptionStatus
    created_at: datetime
    updated_at: datetime

class StrategyRequest(BaseModel):
    strategy_type: StrategyType
    symbol: str = Field(..., description="Underlying symbol")
    investment_amount: float = Field(..., gt=0, description="Total investment amount")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance level")
    market_outlook: str = Field(default="neutral", description="Market outlook")
    expiration_days: int = Field(default=30, ge=1, le=365, description="Days to expiration")

class StrategyResponse(BaseModel):
    strategy_id: str
    strategy_type: StrategyType
    symbol: str
    positions: List[Dict[str, Any]]
    total_cost: float
    max_profit: float
    max_loss: float
    break_even_points: List[float]
    risk_reward_ratio: float
    greeks: Dict[str, float]

# In-memory storage (replace with database in production)
active_positions: Dict[str, OptionPosition] = {}
option_contracts: Dict[str, List[OptionContract]] = {}
strategy_templates: Dict[str, Dict] = {}

class OptionsPricingEngine:
    """Black-Scholes options pricing model"""
    
    @staticmethod
    def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Black-Scholes call option price"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call_price = S * 0.5 * (1 + math.erf(d1 / np.sqrt(2))) - K * np.exp(-r * T) * 0.5 * (1 + math.erf(d2 / np.sqrt(2)))
        return call_price
    
    @staticmethod
    def black_scholes_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Black-Scholes put option price"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        put_price = K * np.exp(-r * T) * 0.5 * (1 - math.erf(d2 / np.sqrt(2))) - S * 0.5 * (1 - math.erf(d1 / np.sqrt(2)))
        return put_price
    
    @staticmethod
    def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: OptionType) -> Dict[str, float]:
        """Calculate option Greeks"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Delta
        if option_type == OptionType.CALL:
            delta = 0.5 * (1 + math.erf(d1 / np.sqrt(2)))
        else:
            delta = 0.5 * (1 + math.erf(d1 / np.sqrt(2))) - 1
        
        # Gamma
        gamma = (1 / (S * sigma * np.sqrt(T))) * (1 / np.sqrt(2 * np.pi)) * np.exp(-d1 ** 2 / 2)
        
        # Theta
        if option_type == OptionType.CALL:
            theta = (-S * sigma * (1 / np.sqrt(2 * np.pi)) * np.exp(-d1 ** 2 / 2)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * 0.5 * (1 + math.erf(d2 / np.sqrt(2)))
        else:
            theta = (-S * sigma * (1 / np.sqrt(2 * np.pi)) * np.exp(-d1 ** 2 / 2)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * 0.5 * (1 - math.erf(d2 / np.sqrt(2)))
        
        # Vega
        vega = (S * np.sqrt(T) * (1 / np.sqrt(2 * np.pi)) * np.exp(-d1 ** 2 / 2)) / 100
        
        # Rho
        if option_type == OptionType.CALL:
            rho = K * T * np.exp(-r * T) * 0.5 * (1 + math.erf(d2 / np.sqrt(2))) / 100
        else:
            rho = -K * T * np.exp(-r * T) * 0.5 * (1 - math.erf(d2 / np.sqrt(2))) / 100
        
        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta / 365,  # Convert to daily theta
            "vega": vega,
            "rho": rho
        }

class OptionsStrategyBuilder:
    """Advanced options strategy builder"""
    
    def __init__(self):
        self.pricing_engine = OptionsPricingEngine()
    
    async def build_strategy(self, request: StrategyRequest) -> StrategyResponse:
        """Build an options strategy based on request parameters"""
        
        # Get current market data
        current_price = await self.get_current_price(request.symbol)
        volatility = await self.get_implied_volatility(request.symbol)
        
        if request.strategy_type == StrategyType.BUY_CALL:
            return await self.build_buy_call_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.BUY_PUT:
            return await self.build_buy_put_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.SELL_CALL:
            return await self.build_sell_call_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.SELL_PUT:
            return await self.build_sell_put_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.STRADDLE:
            return await self.build_straddle_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.STRANGLE:
            return await self.build_strangle_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.IRON_CONDOR:
            return await self.build_iron_condor_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.BUTTERFLY_SPREAD:
            return await self.build_butterfly_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.COVERED_CALL:
            return await self.build_covered_call_strategy(request, current_price, volatility)
        elif request.strategy_type == StrategyType.PROTECTIVE_PUT:
            return await self.build_protective_put_strategy(request, current_price, volatility)
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy type")
    
    async def build_buy_call_strategy(self, request: StrategyRequest, current_price: float, volatility: float) -> StrategyResponse:
        """Build a simple call buying strategy"""
        # Choose strike price based on outlook
        if request.market_outlook == "bullish":
            strike_price = current_price * 1.05  # Slightly OTM
        elif request.market_outlook == "very_bullish":
            strike_price = current_price * 1.10  # More OTM
        else:
            strike_price = current_price  # ATM
        
        # Calculate premium
        T = request.expiration_days / 365.0
        r = 0.05  # Risk-free rate
        premium = self.pricing_engine.black_scholes_call(current_price, strike_price, T, r, volatility)
        
        # Calculate position size
        position_size = int(request.investment_amount / (premium * 100))
        
        # Calculate Greeks
        greeks = self.pricing_engine.calculate_greeks(current_price, strike_price, T, r, volatility, OptionType.CALL)
        
        positions = [{
            "type": "call",
            "strike": strike_price,
            "premium": premium,
            "position_size": position_size,
            "action": "buy"
        }]
        
        return StrategyResponse(
            strategy_id=f"call_{datetime.now().timestamp()}",
            strategy_type=StrategyType.BUY_CALL,
            symbol=request.symbol,
            positions=positions,
            total_cost=premium * position_size * 100,
            max_profit=float('inf'),  # Unlimited for calls
            max_loss=premium * position_size * 100,
            break_even_points=[strike_price + premium],
            risk_reward_ratio=float('inf'),  # Unlimited upside
            greeks=greeks
        )
    
    async def build_straddle_strategy(self, request: StrategyRequest, current_price: float, volatility: float) -> StrategyResponse:
        """Build a straddle strategy (buy both call and put at same strike)"""
        strike_price = current_price  # ATM
        T = request.expiration_days / 365.0
        r = 0.05
        
        call_premium = self.pricing_engine.black_scholes_call(current_price, strike_price, T, r, volatility)
        put_premium = self.pricing_engine.black_scholes_put(current_price, strike_price, T, r, volatility)
        total_premium = call_premium + put_premium
        
        position_size = int(request.investment_amount / (total_premium * 100))
        
        call_greeks = self.pricing_engine.calculate_greeks(current_price, strike_price, T, r, volatility, OptionType.CALL)
        put_greeks = self.pricing_engine.calculate_greeks(current_price, strike_price, T, r, volatility, OptionType.PUT)
        
        # Combine Greeks
        combined_greeks = {
            "delta": call_greeks["delta"] + put_greeks["delta"],
            "gamma": call_greeks["gamma"] + put_greeks["gamma"],
            "theta": call_greeks["theta"] + put_greeks["theta"],
            "vega": call_greeks["vega"] + put_greeks["vega"],
            "rho": call_greeks["rho"] + put_greeks["rho"]
        }
        
        positions = [
            {
                "type": "call",
                "strike": strike_price,
                "premium": call_premium,
                "position_size": position_size,
                "action": "buy"
            },
            {
                "type": "put",
                "strike": strike_price,
                "premium": put_premium,
                "position_size": position_size,
                "action": "buy"
            }
        ]
        
        return StrategyResponse(
            strategy_id=f"straddle_{datetime.now().timestamp()}",
            strategy_type=StrategyType.STRADDLE,
            symbol=request.symbol,
            positions=positions,
            total_cost=total_premium * position_size * 100,
            max_profit=float('inf'),
            max_loss=total_premium * position_size * 100,
            break_even_points=[
                strike_price - total_premium,
                strike_price + total_premium
            ],
            risk_reward_ratio=float('inf'),
            greeks=combined_greeks
        )
    
    async def build_iron_condor_strategy(self, request: StrategyRequest, current_price: float, volatility: float) -> StrategyResponse:
        """Build an iron condor strategy (complex income strategy)"""
        T = request.expiration_days / 365.0
        r = 0.05
        
        # Define strikes
        width = current_price * 0.05  # 5% wing width
        short_call_strike = current_price + width
        short_put_strike = current_price - width
        long_call_strike = current_price + (2 * width)
        long_put_strike = current_price - (2 * width)
        
        # Calculate premiums
        short_call_premium = self.pricing_engine.black_scholes_call(current_price, short_call_strike, T, r, volatility)
        short_put_premium = self.pricing_engine.black_scholes_put(current_price, short_put_strike, T, r, volatility)
        long_call_premium = self.pricing_engine.black_scholes_call(current_price, long_call_strike, T, r, volatility)
        long_put_premium = self.pricing_engine.black_scholes_put(current_price, long_put_strike, T, r, volatility)
        
        # Net premium received
        net_credit = (short_call_premium + short_put_premium) - (long_call_premium + long_put_premium)
        
        position_size = int(request.investment_amount / (net_credit * 100))
        
        positions = [
            {"type": "call", "strike": short_call_strike, "premium": short_call_premium, "position_size": position_size, "action": "sell"},
            {"type": "put", "strike": short_put_strike, "premium": short_put_premium, "position_size": position_size, "action": "sell"},
            {"type": "call", "strike": long_call_strike, "premium": long_call_premium, "position_size": position_size, "action": "buy"},
            {"type": "put", "strike": long_put_strike, "premium": long_put_premium, "position_size": position_size, "action": "buy"}
        ]
        
        return StrategyResponse(
            strategy_id=f"iron_condor_{datetime.now().timestamp()}",
            strategy_type=StrategyType.IRON_CONDOR,
            symbol=request.symbol,
            positions=positions,
            total_cost=-net_credit * position_size * 100,  # Negative = credit received
            max_profit=net_credit * position_size * 100,
            max_loss=width * position_size * 100 - net_credit * position_size * 100,
            break_even_points=[
                short_put_strike - net_credit,
                short_call_strike + net_credit
            ],
            risk_reward_ratio=(net_credit * position_size * 100) / (width * position_size * 100 - net_credit * position_size * 100),
            greeks={"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}  # Near-neutral Greeks
        )
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        # Simulated price data (replace with real API call)
        prices = {
            "BTC": 95000.0,
            "ETH": 3500.0,
            "SOL": 220.0
        }
        return prices.get(symbol, 100.0)
    
    async def get_implied_volatility(self, symbol: str) -> float:
        """Get implied volatility for a symbol"""
        # Simulated volatility data
        volatilities = {
            "BTC": 0.65,
            "ETH": 0.75,
            "SOL": 0.85
        }
        return volatilities.get(symbol, 0.70)

class OptionsTradingManager:
    """Manage options trading operations"""
    
    def __init__(self):
        self.strategy_builder = OptionsStrategyBuilder()
    
    async def create_strategy(self, user_id: str, request: StrategyRequest) -> StrategyResponse:
        """Create an options strategy"""
        try:
            strategy = await self.strategy_builder.build_strategy(request)
            
            # Store positions
            for position in strategy.positions:
                position_id = f"pos_{datetime.now().timestamp()}_{len(active_positions)}"
                option_position = OptionPosition(
                    id=position_id,
                    user_id=user_id,
                    contract=OptionContractModel(
                        symbol=request.symbol,
                        option_type=OptionType.CALL if position["type"] == "call" else OptionType.PUT,
                        strike_price=position["strike"],
                        expiration_date=datetime.now() + timedelta(days=request.expiration_days),
                        premium=position["premium"]
                    ),
                    position_size=position["position_size"],
                    entry_price=position["premium"],
                    current_price=position["premium"],
                    pnl=0.0,
                    status=OptionStatus.ACTIVE,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                active_positions[position_id] = option_position
            
            return strategy
        except Exception as e:
            logger.error(f"Error creating strategy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user_positions(self, user_id: str) -> List[OptionPosition]:
        """Get all option positions for a user"""
        return [pos for pos in active_positions.values() if pos.user_id == user_id]
    
    async def close_position(self, position_id: str, user_id: str) -> bool:
        """Close an option position"""
        if position_id in active_positions and active_positions[position_id].user_id == user_id:
            active_positions[position_id].status = OptionStatus.CLOSED
            active_positions[position_id].updated_at = datetime.now()
            return True
        return False

# Initialize manager
options_manager = OptionsTradingManager()

@app.post("/options/strategy", response_model=StrategyResponse)
async def create_options_strategy(
    request: StrategyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create an options trading strategy"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        strategy = await options_manager.create_strategy(user_id, request)
        logger.info(f"Created options strategy {strategy.strategy_id} for user {user_id}")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating options strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/options/positions", response_model=List[OptionPosition])
async def get_option_positions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all option positions for the authenticated user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        positions = await options_manager.get_user_positions(user_id)
        return positions
    except Exception as e:
        logger.error(f"Error getting option positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/options/positions/{position_id}/close")
async def close_option_position(
    position_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Close an option position"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        success = await options_manager.close_position(position_id, user_id)
        if success:
            return {"message": f"Position {position_id} closed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Position not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/options/strategies")
async def get_available_strategies():
    """Get available options strategies with descriptions"""
    return {
        "buy_call": {
            "name": "Buy Call",
            "description": "Basic bullish strategy",
            "market_outlook": "Bullish",
            "risk_level": "Limited",
            "max_profit": "Unlimited"
        },
        "buy_put": {
            "name": "Buy Put",
            "description": "Basic bearish strategy",
            "market_outlook": "Bearish",
            "risk_level": "Limited",
            "max_profit": "Limited"
        },
        "sell_call": {
            "name": "Sell Call",
            "description": "Income strategy for neutral/bearish outlook",
            "market_outlook": "Neutral/Bearish",
            "risk_level": "High",
            "max_profit": "Limited"
        },
        "sell_put": {
            "name": "Sell Put",
            "description": "Income strategy for neutral/bullish outlook",
            "market_outlook": "Neutral/Bullish",
            "risk_level": "High",
            "max_profit": "Limited"
        },
        "straddle": {
            "name": "Straddle",
            "description": "Buy both call and put at same strike",
            "market_outlook": "High volatility",
            "risk_level": "Limited",
            "max_profit": "Unlimited"
        },
        "strangle": {
            "name": "Strangle",
            "description": "Buy out-of-money call and put",
            "market_outlook": "High volatility",
            "risk_level": "Limited",
            "max_profit": "Unlimited"
        },
        "iron_condor": {
            "name": "Iron Condor",
            "description": "Complex income strategy",
            "market_outlook": "Low volatility",
            "risk_level": "Limited",
            "max_profit": "Limited"
        },
        "butterfly_spread": {
            "name": "Butterfly Spread",
            "description": "Low-cost directional strategy",
            "market_outlook": "Low volatility",
            "risk_level": "Limited",
            "max_profit": "Limited"
        },
        "covered_call": {
            "name": "Covered Call",
            "description": "Income strategy with underlying asset",
            "market_outlook": "Neutral/Bullish",
            "risk_level": "Reduced",
            "max_profit": "Limited"
        },
        "protective_put": {
            "name": "Protective Put",
            "description": "Insurance for long positions",
            "market_outlook": "Insurance",
            "risk_level": "Reduced",
            "max_profit": "Unlimited"
        }
    }

@app.get("/options/chains/{symbol}")
async def get_option_chain(symbol: str):
    """Get option chain for a symbol"""
    try:
        current_price = await options_manager.strategy_builder.get_current_price(symbol)
        volatility = await options_manager.strategy_builder.get_implied_volatility(symbol)
        
        # Generate option chain
        strikes = []
        for i in range(-5, 6):  # 5 strikes below and above ATM
            strike = current_price * (1 + i * 0.05)
            T = 30 / 365.0  # 30 days to expiration
            r = 0.05
            
            call_premium = options_manager.strategy_builder.pricing_engine.black_scholes_call(current_price, strike, T, r, volatility)
            put_premium = options_manager.strategy_builder.pricing_engine.black_scholes_put(current_price, strike, T, r, volatility)
            
            strikes.append({
                "strike": strike,
                "call_premium": call_premium,
                "put_premium": put_premium,
                "call_volume": np.random.randint(100, 10000),
                "put_volume": np.random.randint(100, 10000),
                "call_open_interest": np.random.randint(1000, 50000),
                "put_open_interest": np.random.randint(1000, 50000)
            })
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "strikes": strikes
        }
    except Exception as e:
        logger.error(f"Error getting option chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TigerEx Options Trading Service", "active_positions": len(active_positions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)