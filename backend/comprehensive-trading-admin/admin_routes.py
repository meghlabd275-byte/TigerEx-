"""
Comprehensive Trading Admin System
Complete admin controls for all trading types:
- Spot Trading
- Future Perpetual Trading
- Future Cross Trading
- Margin Trading
- Grid Trading
- Copy Trading
- Option Trading
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from fastapi import APIRouter, HTTPException, Depends, Query, Body, BackgroundTasks
from pydantic import BaseModel, Field, validator
import json
import logging
import asyncio
from dataclasses import dataclass
import redis
import asyncpg
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/trading", tags=["comprehensive-trading-admin"])

# ============================================================================
# DATABASE CONNECTIONS
# ============================================================================

# Redis client for caching and real-time data
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ============================================================================
# ENUMS AND DATA MODELS
# ============================================================================

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURE_PERPETUAL = "future_perpetual"
    FUTURE_CROSS = "future_cross"
    MARGIN = "margin"
    GRID = "grid"
    COPY = "copy"
    OPTION = "option"

class TradingStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    EMERGENCY_STOP = "emergency_stop"
    MAINTENANCE = "maintenance"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    SETTLING = "settling"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class AdminAction(BaseModel):
    action: str
    trading_type: TradingType
    symbol: Optional[str] = None
    contract_id: Optional[str] = None
    user_id: Optional[str] = None
    reason: str
    force: bool = False
    metadata: Optional[Dict[str, Any]] = {}

class ContractConfig(BaseModel):
    contract_id: str
    trading_type: TradingType
    symbol: str
    base_asset: str
    quote_asset: str
    status: ContractStatus = ContractStatus.ACTIVE
    leverage_limit: float = 20.0
    position_size_limit: float = 1000000.0
    order_size_limit: float = 1000000.0
    price_deviation_limit: float = 0.1
    funding_rate: Optional[float] = None
    settlement_type: Optional[str] = None
    contract_size: Optional[float] = None
    tick_size: float = 0.01
    step_size: float = 0.01
    min_order_size: float = 0.001
    max_order_size: float = 1000000.0
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    maintenance_margin: float = 0.005
    initial_margin: float = 0.01
    max_market_order_size: float = 1000000.0
    price_band_upper: float = 0.1
    price_band_lower: float = 0.1
    trading_hours: Optional[Dict[str, Any]] = None
    risk_params: Optional[Dict[str, Any]] = None

class TradingConfig(BaseModel):
    trading_type: TradingType
    enabled: bool = True
    maintenance_mode: bool = False
    max_leverage: float = 20.0
    max_position_size: float = 1000000.0
    max_order_size: float = 1000000.0
    max_daily_volume: float = 10000000.0
    price_deviation_threshold: float = 0.05
    circuit_breaker_threshold: float = 0.1
    rate_limit_per_minute: int = 1000
    cooldown_period: int = 300
    auto_liquidation: bool = True
    insurance_fund_ratio: float = 0.005
    funding_interval: int = 28800  # 8 hours
    mark_price_source: str = "composite"

class UserTradingLimits(BaseModel):
    user_id: str
    trading_type: TradingType
    max_leverage: float = 20.0
    max_position_size: float = 1000000.0
    max_order_size: float = 1000000.0
    max_daily_orders: int = 1000
    max_open_positions: int = 100
    margin_call_ratio: float = 0.8
    liquidation_ratio: float = 0.9
    daily_volume_limit: float = 10000000.0
    api_rate_limit: int = 100
    withdraw_limit: float = 1000000.0

# ============================================================================
# IN-MEMORY STORAGE (In production, use database)
# ============================================================================

# Trading configurations for all types
trading_configs = {
    TradingType.SPOT: TradingConfig(
        trading_type=TradingType.SPOT,
        enabled=True,
        max_leverage=1.0,
        max_position_size=1000000.0,
        max_order_size=1000000.0,
        maker_fee=0.001,
        taker_fee=0.001
    ),
    TradingType.FUTURE_PERPETUAL: TradingConfig(
        trading_type=TradingType.FUTURE_PERPETUAL,
        enabled=True,
        max_leverage=125.0,
        funding_interval=28800,
        mark_price_source="composite"
    ),
    TradingType.FUTURE_CROSS: TradingConfig(
        trading_type=TradingType.FUTURE_CROSS,
        enabled=True,
        max_leverage=125.0,
        settlement_type="cash"
    ),
    TradingType.MARGIN: TradingConfig(
        trading_type=TradingType.MARGIN,
        enabled=True,
        max_leverage=10.0,
        margin_call_ratio=0.8,
        liquidation_ratio=0.9
    ),
    TradingType.GRID: TradingConfig(
        trading_type=TradingType.GRID,
        enabled=True,
        max_leverage=5.0,
        grid_spread=0.01,
        grid_levels=10
    ),
    TradingType.COPY: TradingConfig(
        trading_type=TradingType.COPY,
        enabled=True,
        max_followers=1000,
        min_copy_amount=100.0
    ),
    TradingType.OPTION: TradingConfig(
        trading_type=TradingType.OPTION,
        enabled=True,
        max_leverage=10.0,
        settlement_type="cash",
        option_type="european"
    )
}

# Contract storage
contracts = {}

# User limits
user_limits = {}

# Trading status per type
trading_status = {
    TradingType.SPOT: TradingStatus.ACTIVE,
    TradingType.FUTURE_PERPETUAL: TradingStatus.ACTIVE,
    TradingType.FUTURE_CROSS: TradingStatus.ACTIVE,
    TradingType.MARGIN: TradingStatus.ACTIVE,
    TradingType.GRID: TradingStatus.ACTIVE,
    TradingType.COPY: TradingStatus.ACTIVE,
    TradingType.OPTION: TradingStatus.ACTIVE
}

# Paused symbols per trading type
paused_symbols = {
    TradingType.SPOT: set(),
    TradingType.FUTURE_PERPETUAL: set(),
    TradingType.FUTURE_CROSS: set(),
    TradingType.MARGIN: set(),
    TradingType.GRID: set(),
    TradingType.COPY: set(),
    TradingType.OPTION: set()
}

# Admin action log
admin_action_log = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log_admin_action(admin_id: str, action: AdminAction, result: Dict[str, Any]):
    """Log admin action for audit purposes"""
    log_entry = {
        "admin_id": admin_id,
        "action": action.action,
        "trading_type": action.trading_type,
        "symbol": action.symbol,
        "contract_id": action.contract_id,
        "user_id": action.user_id,
        "reason": action.reason,
        "result": result,
        "metadata": action.metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    admin_action_log.append(log_entry)
    logger.info(f"Admin action logged: {log_entry}")

async def notify_services(action: AdminAction):
    """Notify relevant services about admin action"""
    # In production, this would send messages to relevant microservices
    pass

# ============================================================================
# COMPREHENSIVE TRADING CONTROL ENDPOINTS
# ============================================================================

@router.get("/overview")
async def get_trading_overview():
    """Get overview of all trading systems"""
    return {
        "trading_types": {
            trading_type.value: {
                "status": trading_status[trading_type].value,
                "enabled": trading_configs[trading_type].enabled,
                "maintenance_mode": trading_configs[trading_type].maintenance_mode,
                "paused_symbols": list(paused_symbols[trading_type]),
                "active_contracts": len([c for c in contracts.values() if c.trading_type == trading_type and c.status == ContractStatus.ACTIVE]),
                "total_contracts": len([c for c in contracts.values() if c.trading_type == trading_type])
            }
            for trading_type in TradingType
        },
        "summary": {
            "total_trading_types": len(TradingType),
            "active_trading_types": len([t for t in TradingType if trading_status[t] == TradingStatus.ACTIVE]),
            "paused_trading_types": len([t for t in TradingType if trading_status[t] == TradingStatus.PAUSED]),
            "total_contracts": len(contracts),
            "active_contracts": len([c for c in contracts.values() if c.status == ContractStatus.ACTIVE]),
            "total_admin_actions": len(admin_action_log)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/control")
async def control_trading_system(action: AdminAction, admin_id: str = "system"):
    """Control trading operations for any trading type"""
    try:
        trading_type = action.trading_type
        action_type = action.action.lower()
        
        if action_type == "pause":
            if action.symbol:
                paused_symbols[trading_type].add(action.symbol)
            else:
                trading_status[trading_type] = TradingStatus.PAUSED
                
        elif action_type == "resume":
            if action.symbol:
                paused_symbols[trading_type].discard(action.symbol)
            else:
                trading_status[trading_type] = TradingStatus.ACTIVE
                
        elif action_type == "suspend":
            trading_status[trading_type] = TradingStatus.SUSPENDED
            
        elif action_type == "emergency_stop":
            trading_status[trading_type] = TradingStatus.EMERGENCY_STOP
            # Cancel all orders for this trading type
            await emergency_cancel_all_orders(trading_type, action.symbol)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        result = {
            "success": True,
            "action": action_type,
            "trading_type": trading_type.value,
            "symbol": action.symbol,
            "new_status": trading_status[trading_type].value,
            "paused_symbols": list(paused_symbols[trading_type])
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to control trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONTRACT MANAGEMENT
# ============================================================================

@router.post("/contracts")
async def create_contract(
    contract: ContractConfig,
    admin_id: str = "system"
):
    """Create new trading contract"""
    try:
        if contract.contract_id in contracts:
            raise HTTPException(status_code=400, detail="Contract already exists")
        
        contracts[contract.contract_id] = contract
        
        action = AdminAction(
            action="create_contract",
            trading_type=contract.trading_type,
            symbol=contract.symbol,
            contract_id=contract.contract_id,
            reason="New contract created"
        )
        
        result = {
            "success": True,
            "contract_id": contract.contract_id,
            "trading_type": contract.trading_type.value,
            "symbol": contract.symbol
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts")
async def get_contracts(
    trading_type: Optional[TradingType] = None,
    status: Optional[ContractStatus] = None,
    symbol: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get list of contracts with filters"""
    filtered_contracts = []
    
    for contract in contracts.values():
        if trading_type and contract.trading_type != trading_type:
            continue
        if status and contract.status != status:
            continue
        if symbol and contract.symbol != symbol:
            continue
        filtered_contracts.append(contract.dict())
    
    # Sort by creation time (would need timestamp in real implementation)
    filtered_contracts.sort(key=lambda x: x.get('contract_id', ''), reverse=True)
    
    total = len(filtered_contracts)
    paginated_contracts = filtered_contracts[offset:offset + limit]
    
    return {
        "contracts": paginated_contracts,
        "total": total,
        "limit": limit,
        "offset": offset,
        "filters": {
            "trading_type": trading_type.value if trading_type else None,
            "status": status.value if status else None,
            "symbol": symbol
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.put("/contracts/{contract_id}")
async def update_contract(
    contract_id: str,
    contract: ContractConfig,
    admin_id: str = "system"
):
    """Update existing contract"""
    try:
        if contract_id not in contracts:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contracts[contract_id] = contract
        
        action = AdminAction(
            action="update_contract",
            trading_type=contract.trading_type,
            symbol=contract.symbol,
            contract_id=contract.contract_id,
            reason="Contract updated"
        )
        
        result = {
            "success": True,
            "contract_id": contract_id,
            "contract": contract.dict()
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/pause")
async def pause_contract(
    contract_id: str,
    reason: str = "Contract paused by admin",
    admin_id: str = "system"
):
    """Pause specific contract"""
    try:
        if contract_id not in contracts:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contract = contracts[contract_id]
        contract.status = ContractStatus.PAUSED
        
        action = AdminAction(
            action="pause_contract",
            trading_type=contract.trading_type,
            symbol=contract.symbol,
            contract_id=contract_id,
            reason=reason
        )
        
        result = {
            "success": True,
            "contract_id": contract_id,
            "status": contract.status.value
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/resume")
async def resume_contract(
    contract_id: str,
    admin_id: str = "system"
):
    """Resume specific contract"""
    try:
        if contract_id not in contracts:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contract = contracts[contract_id]
        contract.status = ContractStatus.ACTIVE
        
        action = AdminAction(
            action="resume_contract",
            trading_type=contract.trading_type,
            symbol=contract.symbol,
            contract_id=contract_id,
            reason="Contract resumed"
        )
        
        result = {
            "success": True,
            "contract_id": contract_id,
            "status": contract.status.value
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/contracts/{contract_id}")
async def delete_contract(
    contract_id: str,
    reason: str = "Contract deleted by admin",
    admin_id: str = "system"
):
    """Delete specific contract"""
    try:
        if contract_id not in contracts:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contract = contracts.pop(contract_id)
        
        action = AdminAction(
            action="delete_contract",
            trading_type=contract.trading_type,
            symbol=contract.symbol,
            contract_id=contract_id,
            reason=reason
        )
        
        result = {
            "success": True,
            "contract_id": contract_id,
            "deleted_contract": contract.dict()
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER MANAGEMENT AND LIMITS
# ============================================================================

@router.get("/users/{user_id}/limits")
async def get_user_limits(user_id: str, trading_type: Optional[TradingType] = None):
    """Get trading limits for specific user"""
    if trading_type:
        user_limit_key = f"{user_id}_{trading_type.value}"
        limits = user_limits.get(user_limit_key)
        return {
            "user_id": user_id,
            "trading_type": trading_type.value,
            "limits": limits.dict() if limits else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        user_limits_data = {}
        for key, limits in user_limits.items():
            if key.startswith(user_id):
                user_limits_data[key] = limits.dict()
        return {
            "user_id": user_id,
            "limits": user_limits_data,
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/users/{user_id}/limits")
async def set_user_limits(
    user_id: str,
    limits: UserTradingLimits,
    admin_id: str = "system"
):
    """Set trading limits for specific user"""
    try:
        user_limit_key = f"{user_id}_{limits.trading_type.value}"
        user_limits[user_limit_key] = limits
        
        action = AdminAction(
            action="set_user_limits",
            trading_type=limits.trading_type,
            user_id=user_id,
            reason="User limits updated"
        )
        
        result = {
            "success": True,
            "user_id": user_id,
            "trading_type": limits.trading_type.value,
            "limits": limits.dict()
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to set user limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/positions")
async def get_user_positions(
    user_id: str,
    trading_type: Optional[TradingType] = None
):
    """Get all positions for a user (admin view)"""
    # In production, this would query the actual database
    return {
        "user_id": user_id,
        "trading_type": trading_type.value if trading_type else "all",
        "positions": [],
        "total_positions": 0,
        "total_value": "0.0",
        "unrealized_pnl": "0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/users/{user_id}/close-all-positions")
async def close_all_user_positions(
    user_id: str,
    trading_type: Optional[TradingType] = None,
    reason: str = "Emergency closure by admin",
    admin_id: str = "system"
):
    """Close all positions for a user (admin emergency function)"""
    try:
        # In production, this would close actual positions
        
        action = AdminAction(
            action="close_all_positions",
            trading_type=trading_type if trading_type else TradingType.SPOT,
            user_id=user_id,
            reason=reason
        )
        
        result = {
            "success": True,
            "user_id": user_id,
            "trading_type": trading_type.value if trading_type else "all",
            "closed_positions": 0,
            "total_value": "0.0"
        }
        
        log_admin_action(admin_id, action, result)
        await notify_services(action)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to close user positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def emergency_cancel_all_orders(trading_type: TradingType, symbol: Optional[str] = None):
    """Emergency function to cancel all orders"""
    logger.info(f"Emergency cancelling all orders for {trading_type.value} {symbol or 'all symbols'}")
    # In production, this would cancel actual orders
    pass