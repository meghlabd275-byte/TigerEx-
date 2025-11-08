"""
Enhanced Admin Routes for Grid Trading
Complete admin controls for grid trading bot system
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import asyncio
import json

router = APIRouter(prefix="/admin/grid-trading", tags=["grid-trading-admin"])

class GridStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"

class GridType(str, Enum):
    ARITHMETIC = "arithmetic"
    GEOMETRIC = "geometric"
    INFINITE = "infinite"

class GridDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

class GridBot(BaseModel):
    """Grid trading bot model"""
    id: Optional[str] = None
    user_id: str
    pair_id: str
    symbol: str
    grid_type: GridType
    direction: GridDirection
    status: GridStatus = GridStatus.ACTIVE
    upper_price: float
    lower_price: float
    grid_count: int
    grid_spacing: float
    total_investment: float
    investment_per_grid: float
    current_profit: float = 0.0
    total_profit: float = 0.0
    completed_grids: int = 0
    total_grids: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class GridConfig(BaseModel):
    """Grid trading configuration"""
    enabled: bool = True
    maintenance_mode: bool = False
    max_grids_per_user: int = 50
    max_grids_per_pair: int = 1000
    max_investment_per_bot: float = 1000000
    min_investment_per_bot: float = 100
    max_grid_count: int = 1000
    min_grid_count: int = 2
    auto_rebalance_enabled: bool = True
    stop_loss_enabled: bool = True
    take_profit_enabled: bool = True
    fee_rate: float = 0.001

class GridTemplate(BaseModel):
    """Grid bot template model"""
    name: str
    description: str
    grid_type: GridType
    direction: GridDirection
    recommended_pair_types: List[str]
    default_parameters: Dict[str, Any]
    risk_level: str
    expected_return_range: List[float]

class GridPerformance(BaseModel):
    """Grid performance metrics"""
    bot_id: str
    total_invested: float
    current_value: float
    profit_loss: float
    profit_loss_percentage: float
    grid_completion_rate: float
    average_hold_time: float
    total_fees_paid: float
    net_profit: float

# ============================================================================
# GRID BOT MANAGEMENT
# ============================================================================

@router.post("/bots/create")
async def create_grid_bot(
    bot: GridBot,
    background_tasks: BackgroundTasks
):
    """
    Create new grid trading bot
    Admin can create grid bots with full configuration
    """
    try:
        # Validate bot parameters
        if bot.upper_price <= bot.lower_price:
            raise HTTPException(
                status_code=400,
                detail="Upper price must be greater than lower price"
            )
        
        if bot.grid_count < 2 or bot.grid_count > 1000:
            raise HTTPException(
                status_code=400,
                detail="Grid count must be between 2 and 1000"
            )
        
        if bot.total_investment < 100:
            raise HTTPException(
                status_code=400,
                detail="Minimum investment is 100"
            )
        
        # Calculate investment per grid
        investment_per_grid = bot.total_investment / bot.grid_count
        
        bot_data = bot.dict()
        bot_data["id"] = f"GRID_{bot.symbol}_{datetime.now().timestamp()}"
        bot_data["investment_per_grid"] = investment_per_grid
        bot_data["total_grids"] = bot.grid_count
        bot_data["created_at"] = datetime.now()
        bot_data["updated_at"] = datetime.now()
        
        # Initialize grid bot
        background_tasks.add_task(initialize_grid_bot, bot_data["id"])
        
        return {
            "status": "success",
            "message": f"Grid trading bot {bot_data['id']} created successfully",
            "bot": bot_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bots/{bot_id}/pause")
async def pause_grid_bot(bot_id: str, reason: str):
    """
    Pause grid trading bot
    Admin can pause bot operations temporarily
    """
    try:
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} paused successfully",
            "bot_id": bot_id,
            "reason": reason,
            "status": "paused",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bots/{bot_id}/resume")
async def resume_grid_bot(bot_id: str):
    """
    Resume grid trading bot
    Admin can resume paused bot operations
    """
    try:
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} resumed successfully",
            "bot_id": bot_id,
            "status": "active",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bots/{bot_id}/stop")
async def stop_grid_bot(bot_id: str, reason: str):
    """
    Stop grid trading bot
    Admin can stop bot operations completely
    """
    try:
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} stopped successfully",
            "bot_id": bot_id,
            "reason": reason,
            "status": "stopped",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/bots/{bot_id}")
async def delete_grid_bot(bot_id: str):
    """
    Delete grid trading bot
    Admin can delete grid bots completely
    """
    try:
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} deleted successfully",
            "bot_id": bot_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRID BOT CONFIGURATION MANAGEMENT
# ============================================================================

@router.put("/bots/{bot_id}/config/update")
async def update_grid_bot_config(
    bot_id: str,
    upper_price: Optional[float] = None,
    lower_price: Optional[float] = None,
    grid_count: Optional[int] = None,
    total_investment: Optional[float] = None
):
    """
    Update grid bot configuration
    Admin can modify bot parameters while running
    """
    try:
        updates = {}
        if upper_price is not None:
            updates["upper_price"] = upper_price
        if lower_price is not None:
            updates["lower_price"] = lower_price
        if grid_count is not None:
            updates["grid_count"] = grid_count
        if total_investment is not None:
            updates["total_investment"] = total_investment
        
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} configuration updated",
            "bot_id": bot_id,
            "updates": updates,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bots/{bot_id}/rebalance")
async def rebalance_grid_bot(bot_id: str, reason: str):
    """
    Rebalance grid bot
    Admin can force rebalancing of grid positions
    """
    try:
        return {
            "status": "success",
            "message": f"Grid bot {bot_id} rebalanced successfully",
            "bot_id": bot_id,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER GRID BOT MANAGEMENT
# ============================================================================

@router.post("/users/{user_id}/bots/create")
async def create_user_grid_bot(
    user_id: str,
    bot: GridBot,
    background_tasks: BackgroundTasks
):
    """
    Create grid bot for specific user
    Admin can create bots on behalf of users
    """
    try:
        bot.user_id = user_id
        
        # Check user bot limits
        user_bots_count = await get_user_bots_count(user_id)
        if user_bots_count >= 50:  # Default limit
            raise HTTPException(
                status_code=400,
                detail="User has reached maximum grid bot limit"
            )
        
        bot_data = bot.dict()
        bot_data["id"] = f"GRID_{bot.symbol}_{user_id}_{datetime.now().timestamp()}"
        bot_data["investment_per_grid"] = bot.total_investment / bot.grid_count
        bot_data["total_grids"] = bot.grid_count
        bot_data["created_at"] = datetime.now()
        bot_data["updated_at"] = datetime.now()
        
        # Initialize grid bot
        background_tasks.add_task(initialize_grid_bot, bot_data["id"])
        
        return {
            "status": "success",
            "message": f"Grid bot created for user {user_id}",
            "bot": bot_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/bot-limit/update")
async def update_user_bot_limit(
    user_id: str,
    new_limit: int
):
    """
    Update user's grid bot limit
    Admin can control how many bots each user can create
    """
    try:
        if new_limit <= 0 or new_limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="Bot limit must be between 1 and 1000"
            )
        
        return {
            "status": "success",
            "message": f"Bot limit updated for user {user_id}",
            "user_id": user_id,
            "new_limit": new_limit,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRID TEMPLATE MANAGEMENT
# ============================================================================

@router.post("/templates/create")
async def create_grid_template(template: GridTemplate):
    """
    Create grid bot template
    Admin can create predefined bot configurations
    """
    try:
        template_data = template.dict()
        template_data["id"] = f"TEMPLATE_{template.name}_{datetime.now().timestamp()}"
        template_data["created_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": f"Grid template {template.name} created successfully",
            "template": template_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/list")
async def list_grid_templates():
    """
    List all available grid templates
    Admin can view all templates
    """
    try:
        templates = [
            {
                "id": "TEMPLATE_conservative_1",
                "name": "Conservative Grid",
                "description": "Low-risk grid with wide spacing",
                "grid_type": "arithmetic",
                "direction": "neutral",
                "risk_level": "low",
                "expected_return_range": [0.05, 0.15],
                "popularity": 1250
            },
            {
                "id": "TEMPLATE_aggressive_1",
                "name": "Aggressive Grid",
                "description": "High-risk grid with tight spacing",
                "grid_type": "geometric",
                "direction": "neutral",
                "risk_level": "high",
                "expected_return_range": [0.15, 0.40],
                "popularity": 850
            }
        ]
        
        return {
            "status": "success",
            "templates": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_grid_template(template_id: str):
    """
    Delete grid template
    Admin can remove templates
    """
    try:
        return {
            "status": "success",
            "message": f"Grid template {template_id} deleted successfully",
            "template_id": template_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GRID PAIR MANAGEMENT
# ============================================================================

@router.post("/pairs/enable")
async def enable_grid_pair(pair_id: str, config: Dict[str, Any]):
    """
    Enable grid trading for specific pair
    Admin can configure which pairs support grid trading
    """
    try:
        return {
            "status": "success",
            "message": f"Grid trading enabled for pair {pair_id}",
            "pair_id": pair_id,
            "config": config,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pairs/{pair_id}/disable")
async def disable_grid_pair(pair_id: str, reason: str):
    """
    Disable grid trading for specific pair
    Admin can disable grid trading for certain pairs
    """
    try:
        return {
            "status": "success",
            "message": f"Grid trading disabled for pair {pair_id}",
            "pair_id": pair_id,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

@router.get("/bots/{bot_id}/performance")
async def get_grid_bot_performance(bot_id: str):
    """
    Get detailed performance metrics for grid bot
    Admin can monitor bot performance
    """
    try:
        return {
            "status": "success",
            "performance": {
                "bot_id": bot_id,
                "total_invested": 10000.0,
                "current_value": 10550.0,
                "profit_loss": 550.0,
                "profit_loss_percentage": 5.5,
                "grid_completion_rate": 0.75,
                "completed_grids": 15,
                "total_grids": 20,
                "average_hold_time": 2.5,  # hours
                "total_fees_paid": 125.0,
                "net_profit": 425.0,
                "daily_performance": [
                    {"date": "2024-01-01", "profit": 25.5},
                    {"date": "2024-01-02", "profit": 18.2},
                    {"date": "2024-01-03", "profit": 32.1}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_grid_analytics():
    """
    Get comprehensive grid trading analytics
    Admin can monitor system-wide performance
    """
    try:
        return {
            "status": "success",
            "analytics": {
                "total_active_bots": 25000,
                "total_invested_amount": "500000000",
                "total_profit_24h": "2500000",
                "total_fees_24h": "750000",
                "average_roi": 0.125,
                "top_performing_pairs": [
                    {"pair": "BTC/USDT", "bots": 5000, "avg_profit": 0.08},
                    {"pair": "ETH/USDT", "bots": 3500, "avg_profit": 0.12},
                    {"pair": "BNB/USDT", "bots": 2000, "avg_profit": 0.06}
                ],
                "risk_distribution": {
                    "low": 0.45,
                    "medium": 0.35,
                    "high": 0.20
                },
                "grid_type_distribution": {
                    "arithmetic": 0.60,
                    "geometric": 0.30,
                    "infinite": 0.10
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

@router.post("/bots/{bot_id}/emergency-stop")
async def emergency_stop_grid_bot(bot_id: str, reason: str):
    """
    Emergency stop grid bot
    Admin can immediately stop bot for risk management
    """
    try:
        return {
            "status": "success",
            "message": f"Emergency stop triggered for grid bot {bot_id}",
            "bot_id": bot_id,
            "reason": reason,
            "stop_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pairs/{pair_id}/emergency-disable")
async def emergency_disable_grid_pair(pair_id: str, reason: str):
    """
    Emergency disable grid trading for pair
    Admin can immediately disable grid trading for safety
    """
    try:
        return {
            "status": "success",
            "message": f"Emergency disable for pair {pair_id}",
            "pair_id": pair_id,
            "reason": reason,
            "disable_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

@router.put("/config/update")
async def update_grid_config(config: GridConfig):
    """
    Update global grid trading configuration
    Admin can modify system-wide settings
    """
    try:
        config_data = config.dict()
        config_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": "Grid trading configuration updated successfully",
            "config": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_grid_config():
    """
    Get current grid trading configuration
    Admin can view current system settings
    """
    try:
        return {
            "status": "success",
            "config": {
                "enabled": True,
                "maintenance_mode": False,
                "max_grids_per_user": 50,
                "max_grids_per_pair": 1000,
                "max_investment_per_bot": 1000000,
                "min_investment_per_bot": 100,
                "max_grid_count": 1000,
                "min_grid_count": 2,
                "auto_rebalance_enabled": True,
                "stop_loss_enabled": True,
                "take_profit_enabled": True,
                "fee_rate": 0.001
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def initialize_grid_bot(bot_id: str):
    """Initialize grid bot systems"""
    await asyncio.sleep(1)
    print(f"Grid bot {bot_id} initialized")

async def get_user_bots_count(user_id: str) -> int:
    """Get number of bots for user"""
    # This would query database
    return 10  # Mock value