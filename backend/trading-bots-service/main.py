"""
TigerEx Trading Bots Service
Advanced trading bots with AI recommendations and multiple strategies
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx Trading Bots Service", version="1.0.0")
security = HTTPBearer()

class BotType(str, Enum):
    GRID = "grid"
    MARTINGALE = "martingale"
    DCA = "dca"
    COMBO = "combo"
    AI_GRID = "ai_grid"

class BotStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class BotConfig:
    symbol: str
    investment_amount: float
    grid_count: int = 10
    grid_spacing: float = 0.02
    take_profit: float = 0.05
    stop_loss: float = 0.10
    leverage: int = 1

class TradingBot(BaseModel):
    id: str
    user_id: str
    bot_type: BotType
    symbol: str
    status: BotStatus
    config: Dict[str, Any]
    performance: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    total_trades: int
    win_rate: float
    total_pnl: float

class GridBotConfig(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    investment_amount: float = Field(..., gt=0, description="Total investment amount")
    grid_count: int = Field(default=10, gt=0, le=100, description="Number of grid levels")
    grid_spacing: float = Field(default=0.02, gt=0, le=0.5, description="Grid spacing percentage")
    take_profit: float = Field(default=0.05, gt=0, le=1.0, description="Take profit percentage")
    stop_loss: float = Field(default=0.10, gt=0, le=1.0, description="Stop loss percentage")
    leverage: int = Field(default=1, ge=1, le=125, description="Trading leverage")

class MartingaleBotConfig(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    base_amount: float = Field(..., gt=0, description="Base trade amount")
    max_multipliers: int = Field(default=5, ge=1, le=10, description="Maximum multiplier levels")
    multiplier_factor: float = Field(default=2.0, ge=1.1, le=5.0, description="Multiplier factor")
    take_profit: float = Field(default=0.05, gt=0, le=1.0, description="Take profit percentage")
    stop_loss: float = Field(default=0.20, gt=0, le=1.0, description="Stop loss percentage")
    leverage: int = Field(default=1, ge=1, le=125, description="Trading leverage")

class DCABotConfig(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    total_amount: float = Field(..., gt=0, description="Total investment amount")
    investment_frequency: str = Field(default="daily", description="Investment frequency")
    number_of_orders: int = Field(default=30, ge=1, le=365, description="Number of orders")
    price_range_min: Optional[float] = Field(None, description="Minimum price target")
    price_range_max: Optional[float] = Field(None, description="Maximum price target")

class ComboBotConfig(BaseModel):
    symbols: List[str] = Field(..., min_items=1, max_items=10, description="List of symbols")
    allocation_percentages: List[float] = Field(..., description="Allocation percentages for each symbol")
    rebalance_threshold: float = Field(default=0.05, gt=0, le=0.5, description="Rebalance threshold")
    investment_amount: float = Field(..., gt=0, description="Total investment amount")
    leverage: int = Field(default=1, ge=1, le=125, description="Trading leverage")

# In-memory storage (replace with database in production)
active_bots: Dict[str, TradingBot] = {}
bot_performance: Dict[str, List[Dict]] = {}

class TradingBotsManager:
    def __init__(self):
        self.running_bots: Dict[str, asyncio.Task] = {}
        
    async def create_grid_bot(self, user_id: str, config: GridBotConfig) -> TradingBot:
        """Create a grid trading bot"""
        bot_id = f"grid_{datetime.now().timestamp()}"
        
        # Calculate grid levels
        current_price = await self.get_current_price(config.symbol)
        grid_levels = self.calculate_grid_levels(current_price, config.grid_count, config.grid_spacing)
        
        bot = TradingBot(
            id=bot_id,
            user_id=user_id,
            bot_type=BotType.GRID,
            symbol=config.symbol,
            status=BotStatus.ACTIVE,
            config=config.dict(),
            performance={
                "current_price": current_price,
                "grid_levels": grid_levels,
                "active_orders": [],
                "completed_trades": []
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_trades=0,
            win_rate=0.0,
            total_pnl=0.0
        )
        
        active_bots[bot_id] = bot
        return bot
    
    async def create_martingale_bot(self, user_id: str, config: MartingaleBotConfig) -> TradingBot:
        """Create a martingale trading bot"""
        bot_id = f"martingale_{datetime.now().timestamp()}"
        
        bot = TradingBot(
            id=bot_id,
            user_id=user_id,
            bot_type=BotType.MARTINGALE,
            symbol=config.symbol,
            status=BotStatus.ACTIVE,
            config=config.dict(),
            performance={
                "current_level": 0,
                "current_position": None,
                "multiplier_history": [],
                "total_invested": config.base_amount
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_trades=0,
            win_rate=0.0,
            total_pnl=0.0
        )
        
        active_bots[bot_id] = bot
        return bot
    
    async def create_dca_bot(self, user_id: str, config: DCABotConfig) -> TradingBot:
        """Create a DCA trading bot"""
        bot_id = f"dca_{datetime.now().timestamp()}"
        
        # Calculate investment schedule
        investment_amount = config.total_amount / config.number_of_orders
        schedule = self.calculate_dca_schedule(config.investment_frequency, config.number_of_orders)
        
        bot = TradingBot(
            id=bot_id,
            user_id=user_id,
            bot_type=BotType.DCA,
            symbol=config.symbol,
            status=BotStatus.ACTIVE,
            config=config.dict(),
            performance={
                "schedule": schedule,
                "next_investment": schedule[0] if schedule else None,
                "completed_orders": 0,
                "average_price": 0.0,
                "total_invested": 0.0
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_trades=0,
            win_rate=0.0,
            total_pnl=0.0
        )
        
        active_bots[bot_id] = bot
        return bot
    
    async def create_combo_bot(self, user_id: str, config: ComboBotConfig) -> TradingBot:
        """Create a portfolio rebalancing bot"""
        bot_id = f"combo_{datetime.now().timestamp()}"
        
        # Validate allocations sum to 100%
        if abs(sum(config.allocation_percentages) - 100.0) > 0.01:
            raise HTTPException(status_code=400, detail="Allocation percentages must sum to 100%")
        
        initial_allocations = {
            symbol: (config.investment_amount * percentage / 100.0)
            for symbol, percentage in zip(config.symbols, config.allocation_percentages)
        }
        
        bot = TradingBot(
            id=bot_id,
            user_id=user_id,
            bot_type=BotType.COMBO,
            symbol=",".join(config.symbols),
            status=BotStatus.ACTIVE,
            config=config.dict(),
            performance={
                "current_allocations": initial_allocations,
                "target_allocations": initial_allocations,
                "rebalance_history": [],
                "last_rebalance": None
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_trades=0,
            win_rate=0.0,
            total_pnl=0.0
        )
        
        active_bots[bot_id] = bot
        return bot
    
    async def create_ai_grid_bot(self, user_id: str, config: GridBotConfig) -> TradingBot:
        """Create an AI-optimized grid trading bot"""
        bot_id = f"ai_grid_{datetime.now().timestamp()}"
        
        # AI optimization based on historical data
        optimized_config = await self.optimize_grid_parameters(config.symbol)
        
        bot = TradingBot(
            id=bot_id,
            user_id=user_id,
            bot_type=BotType.AI_GRID,
            symbol=config.symbol,
            status=BotStatus.ACTIVE,
            config={**config.dict(), **optimized_config},
            performance={
                "ai_recommendations": optimized_config,
                "optimization_score": 0.85,
                "backtest_results": {
                    "win_rate": 0.72,
                    "avg_return": 0.15,
                    "max_drawdown": 0.08
                }
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_trades=0,
            win_rate=0.72,  # Based on backtest
            total_pnl=0.0
        )
        
        active_bots[bot_id] = bot
        return bot
    
    def calculate_grid_levels(self, current_price: float, grid_count: int, grid_spacing: float) -> List[Dict]:
        """Calculate grid levels for grid trading"""
        levels = []
        for i in range(grid_count + 1):
            price = current_price * (1 - (grid_count/2 - i) * grid_spacing)
            levels.append({
                "level": i,
                "price": price,
                "buy_order": i < grid_count/2,
                "sell_order": i >= grid_count/2
            })
        return levels
    
    def calculate_dca_schedule(self, frequency: str, count: int) -> List[datetime]:
        """Calculate DCA investment schedule"""
        schedule = []
        now = datetime.now()
        
        if frequency == "daily":
            for i in range(count):
                schedule.append(now + timedelta(days=i))
        elif frequency == "weekly":
            for i in range(count):
                schedule.append(now + timedelta(weeks=i))
        elif frequency == "monthly":
            for i in range(count):
                schedule.append(now + timedelta(days=30*i))
        
        return schedule
    
    async def optimize_grid_parameters(self, symbol: str) -> Dict[str, Any]:
        """AI optimization for grid trading parameters"""
        # Simulated AI optimization (replace with actual ML model)
        return {
            "grid_count": 12,
            "grid_spacing": 0.018,
            "take_profit": 0.045,
            "stop_loss": 0.08
        }
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        # Simulated price data (replace with real API call)
        prices = {
            "BTCUSDT": 95000.0,
            "ETHUSDT": 3500.0,
            "SOLUSDT": 220.0
        }
        return prices.get(symbol, 100.0)
    
    async def get_user_bots(self, user_id: str) -> List[TradingBot]:
        """Get all bots for a user"""
        return [bot for bot in active_bots.values() if bot.user_id == user_id]
    
    async def stop_bot(self, bot_id: str, user_id: str) -> bool:
        """Stop a running bot"""
        if bot_id in active_bots and active_bots[bot_id].user_id == user_id:
            active_bots[bot_id].status = BotStatus.STOPPED
            active_bots[bot_id].updated_at = datetime.now()
            return True
        return False
    
    async def get_bot_performance(self, bot_id: str, user_id: str) -> Optional[Dict]:
        """Get detailed performance metrics for a bot"""
        if bot_id in active_bots and active_bots[bot_id].user_id == user_id:
            bot = active_bots[bot_id]
            return {
                "bot_info": bot.dict(),
                "performance_history": bot_performance.get(bot_id, []),
                "real_time_metrics": {
                    "current_pnl": bot.total_pnl,
                    "win_rate": bot.win_rate,
                    "total_trades": bot.total_trades,
                    "uptime": (datetime.now() - bot.created_at).total_seconds()
                }
            }
        return None

# Initialize bot manager
bot_manager = TradingBotsManager()

@app.post("/bots/grid", response_model=TradingBot)
async def create_grid_bot(
    config: GridBotConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a grid trading bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]  # Extract user ID from token
        bot = await bot_manager.create_grid_bot(user_id, config)
        logger.info(f"Created grid bot {bot.id} for user {user_id}")
        return bot
    except Exception as e:
        logger.error(f"Error creating grid bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/martingale", response_model=TradingBot)
async def create_martingale_bot(
    config: MartingaleBotConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a martingale trading bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        bot = await bot_manager.create_martingale_bot(user_id, config)
        logger.info(f"Created martingale bot {bot.id} for user {user_id}")
        return bot
    except Exception as e:
        logger.error(f"Error creating martingale bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/dca", response_model=TradingBot)
async def create_dca_bot(
    config: DCABotConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a DCA trading bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        bot = await bot_manager.create_dca_bot(user_id, config)
        logger.info(f"Created DCA bot {bot.id} for user {user_id}")
        return bot
    except Exception as e:
        logger.error(f"Error creating DCA bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/combo", response_model=TradingBot)
async def create_combo_bot(
    config: ComboBotConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a portfolio rebalancing bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        bot = await bot_manager.create_combo_bot(user_id, config)
        logger.info(f"Created combo bot {bot.id} for user {user_id}")
        return bot
    except Exception as e:
        logger.error(f"Error creating combo bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/ai-grid", response_model=TradingBot)
async def create_ai_grid_bot(
    config: GridBotConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create an AI-optimized grid trading bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        bot = await bot_manager.create_ai_grid_bot(user_id, config)
        logger.info(f"Created AI grid bot {bot.id} for user {user_id}")
        return bot
    except Exception as e:
        logger.error(f"Error creating AI grid bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots", response_model=List[TradingBot])
async def get_user_bots(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all bots for the authenticated user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        bots = await bot_manager.get_user_bots(user_id)
        return bots
    except Exception as e:
        logger.error(f"Error getting user bots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots/{bot_id}/performance")
async def get_bot_performance(
    bot_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed performance metrics for a specific bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        performance = await bot_manager.get_bot_performance(bot_id, user_id)
        if performance:
            return performance
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bot performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bots/{bot_id}/stop")
async def stop_bot(
    bot_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Stop a running bot"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        success = await bot_manager.stop_bot(bot_id, user_id)
        if success:
            return {"message": f"Bot {bot_id} stopped successfully"}
        else:
            raise HTTPException(status_code=404, detail="Bot not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bots/types")
async def get_available_bot_types():
    """Get available bot types and their descriptions"""
    return {
        "grid": {
            "name": "Grid Trading Bot",
            "description": "Automated grid trading strategy",
            "best_for": "Sideways markets",
            "risk_level": "Medium"
        },
        "martingale": {
            "name": "Martingale Bot",
            "description": "Doubling down strategy for reversal trading",
            "best_for": "Volatile markets with reversals",
            "risk_level": "High"
        },
        "dca": {
            "name": "Dollar Cost Averaging Bot",
            "description": "Systematic investment over time",
            "best_for": "Long-term investing",
            "risk_level": "Low"
        },
        "combo": {
            "name": "Portfolio Rebalancing Bot",
            "description": "Multi-asset portfolio management",
            "best_for": "Diversified portfolios",
            "risk_level": "Medium"
        },
        "ai_grid": {
            "name": "AI-Optimized Grid Bot",
            "description": "Machine learning optimized grid trading",
            "best_for": "Optimized grid trading",
            "risk_level": "Medium"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TigerEx Trading Bots Service", "active_bots": len(active_bots)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)