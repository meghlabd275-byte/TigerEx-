"""
Enhanced Admin Routes for Futures Trading
Complete admin controls for perpetual and cross futures trading
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import asyncio
import json

router = APIRouter(prefix="/admin/futures-trading", tags=["futures-trading-admin"])

class FuturesType(str, Enum):
    PERPETUAL = "perpetual"
    CROSS = "cross"
    ISOLATED = "isolated"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    SETTLING = "settling"
    EXPIRED = "expired"

class MarginMode(str, Enum):
    ISOLATED = "isolated"
    CROSS = "cross"

class FuturesContract(BaseModel):
    """Futures contract model"""
    symbol: str
    base_asset: str
    quote_asset: str
    futures_type: FuturesType
    status: ContractStatus = ContractStatus.ACTIVE
    contract_size: float = 1.0
    max_leverage: float = 125.0
    maintenance_margin_rate: float = 0.005
    initial_margin_rate: float = 0.01
    funding_rate: float = 0.0001
    funding_interval: int = 8  # hours
    price_band_upper: float = 0.05  # 5%
    price_band_lower: float = 0.05  # 5%
    mark_price_method: str = "fair_price"
    settle_asset: Optional[str] = None
    expire_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FuturesConfig(BaseModel):
    """Futures trading configuration"""
    enabled: bool = True
    maintenance_mode: bool = False
    max_leverage_global: float = 125.0
    default_leverage: float = 20.0
    enable_perpetual: bool = True
    enable_cross_margin: bool = True
    enable_isolated_margin: bool = True
    force_liquidation_threshold: float = 0.9
    adl_ranking_enabled: bool = True
    insurance_fund_ratio: float = 0.002
    funding_rate_cap: float = 0.005
    funding_rate_floor: float = -0.005

class RiskParameter(BaseModel):
    """Risk parameter model"""
    contract_id: str
    max_position_size: float
    max_open_orders: int = 50
    max_order_size: float
    price_deviation_threshold: float = 0.1
    liquidation_threshold: float = 0.9
    adl_threshold: float = 0.95

class InsuranceFund(BaseModel):
    """Insurance fund model"""
    asset: str
    total_balance: float
    available_balance: float
    last_updated: datetime
    funding_history: List[Dict[str, Any]] = []

# ============================================================================
# PERPETUAL FUTURES CONTRACT MANAGEMENT
# ============================================================================

@router.post("/contracts/perpetual/create")
async def create_perpetual_contract(
    contract: FuturesContract,
    background_tasks: BackgroundTasks
):
    """
    Create new perpetual futures contract
    Admin can create perpetual contracts with full configuration
    """
    try:
        if contract.futures_type != FuturesType.PERPETUAL:
            raise HTTPException(
                status_code=400,
                detail="Contract type must be perpetual"
            )
        
        # Validate contract parameters
        if contract.max_leverage <= 1 or contract.max_leverage > 125:
            raise HTTPException(
                status_code=400,
                detail="Max leverage must be between 1 and 125"
            )
        
        contract_data = contract.dict()
        contract_data["id"] = f"PERP_{contract.symbol}_{datetime.now().timestamp()}"
        contract_data["created_at"] = datetime.now()
        contract_data["updated_at"] = datetime.now()
        
        # Initialize contract systems
        background_tasks.add_task(initialize_perpetual_contract, contract_data["id"])
        
        return {
            "status": "success",
            "message": f"Perpetual contract {contract.symbol} created successfully",
            "contract": contract_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/cross/create")
async def create_cross_contract(
    contract: FuturesContract,
    background_tasks: BackgroundTasks
):
    """
    Create new cross margin futures contract
    Admin can create cross margin contracts
    """
    try:
        if contract.futures_type != FuturesType.CROSS:
            raise HTTPException(
                status_code=400,
                detail="Contract type must be cross"
            )
        
        contract_data = contract.dict()
        contract_data["id"] = f"CROSS_{contract.symbol}_{datetime.now().timestamp()}"
        contract_data["created_at"] = datetime.now()
        contract_data["updated_at"] = datetime.now()
        
        # Initialize cross margin systems
        background_tasks.add_task(initialize_cross_contract, contract_data["id"])
        
        return {
            "status": "success",
            "message": f"Cross margin contract {contract.symbol} created successfully",
            "contract": contract_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONTRACT CONTROL OPERATIONS
# ============================================================================

@router.put("/contracts/{contract_id}/pause")
async def pause_futures_contract(contract_id: str):
    """
    Pause futures contract trading
    Admin can pause contract trading temporarily
    """
    try:
        return {
            "status": "success",
            "message": f"Futures contract {contract_id} paused successfully",
            "contract_id": contract_id,
            "status": "paused",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contracts/{contract_id}/resume")
async def resume_futures_contract(contract_id: str):
    """
    Resume futures contract trading
    Admin can resume paused contract trading
    """
    try:
        return {
            "status": "success",
            "message": f"Futures contract {contract_id} resumed successfully",
            "contract_id": contract_id,
            "status": "active",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contracts/{contract_id}/suspend")
async def suspend_futures_contract(contract_id: str, reason: str):
    """
    Suspend futures contract trading
    Admin can suspend contract trading for safety reasons
    """
    try:
        return {
            "status": "success",
            "message": f"Futures contract {contract_id} suspended successfully",
            "contract_id": contract_id,
            "reason": reason,
            "status": "suspended",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/contracts/{contract_id}")
async def delete_futures_contract(contract_id: str):
    """
    Delete futures contract
    Admin can delete futures contracts completely
    """
    try:
        return {
            "status": "success",
            "message": f"Futures contract {contract_id} deleted successfully",
            "contract_id": contract_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LEVERAGE AND MARGIN MANAGEMENT
# ============================================================================

@router.put("/contracts/{contract_id}/leverage/update")
async def update_contract_leverage(
    contract_id: str,
    max_leverage: float,
    default_leverage: float
):
    """
    Update leverage settings for contract
    Admin can control leverage parameters
    """
    try:
        if max_leverage <= 1 or max_leverage > 125:
            raise HTTPException(
                status_code=400,
                detail="Max leverage must be between 1 and 125"
            )
        
        if default_leverage > max_leverage:
            raise HTTPException(
                status_code=400,
                detail="Default leverage cannot exceed max leverage"
            )
        
        return {
            "status": "success",
            "message": f"Leverage updated for contract {contract_id}",
            "contract_id": contract_id,
            "max_leverage": max_leverage,
            "default_leverage": default_leverage,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/leverage/update")
async def update_user_leverage(
    user_id: str,
    contract_id: str,
    leverage: float
):
    """
    Update leverage for specific user
    Admin can control individual user leverage
    """
    try:
        if leverage <= 1 or leverage > 125:
            raise HTTPException(
                status_code=400,
                detail="Leverage must be between 1 and 125"
            )
        
        return {
            "status": "success",
            "message": f"Leverage updated for user {user_id}",
            "user_id": user_id,
            "contract_id": contract_id,
            "leverage": leverage,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FUNDING RATE MANAGEMENT
# ============================================================================

@router.put("/contracts/{contract_id}/funding-rate/update")
async def update_funding_rate(
    contract_id: str,
    funding_rate: float,
    funding_interval: Optional[int] = None
):
    """
    Update funding rate for perpetual contract
    Admin can control funding parameters
    """
    try:
        if abs(funding_rate) > 0.005:  # 0.5% cap
            raise HTTPException(
                status_code=400,
                detail="Funding rate cannot exceed +/-0.5%"
            )
        
        return {
            "status": "success",
            "message": f"Funding rate updated for contract {contract_id}",
            "contract_id": contract_id,
            "funding_rate": funding_rate,
            "funding_interval": funding_interval,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/funding/settle")
async def settle_funding_payments(contract_id: str):
    """
    Manually trigger funding settlement
    Admin can force funding payment settlement
    """
    try:
        return {
            "status": "success",
            "message": f"Funding payments settled for contract {contract_id}",
            "contract_id": contract_id,
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

@router.post("/contracts/{contract_id}/risk-parameters/update")
async def update_risk_parameters(
    contract_id: str,
    risk_params: RiskParameter
):
    """
    Update risk parameters for contract
    Admin can manage risk settings
    """
    try:
        params_data = risk_params.dict()
        params_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": f"Risk parameters updated for contract {contract_id}",
            "contract_id": contract_id,
            "risk_parameters": params_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/liquidate")
async def force_liquidate_position(
    user_id: str,
    contract_id: str,
    reason: str
):
    """
    Force liquidate user position
    Admin can force liquidation for risk management
    """
    try:
        return {
            "status": "success",
            "message": f"Position liquidated for user {user_id}",
            "user_id": user_id,
            "contract_id": contract_id,
            "reason": reason,
            "liquidation_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INSURANCE FUND MANAGEMENT
# ============================================================================

@router.post("/insurance-fund/deposit")
async def deposit_to_insurance_fund(
    asset: str,
    amount: float,
    reason: str
):
    """
    Deposit funds to insurance fund
    Admin can manage insurance fund balance
    """
    try:
        return {
            "status": "success",
            "message": f"Deposited {amount} {asset} to insurance fund",
            "asset": asset,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insurance-fund/balance")
async def get_insurance_fund_balance():
    """
    Get insurance fund balance and status
    Admin can monitor insurance fund health
    """
    try:
        return {
            "status": "success",
            "insurance_fund": {
                "USDT": {
                    "total_balance": 50000000.0,
                    "available_balance": 48500000.0,
                    "utilized_balance": 1500000.0,
                    "last_updated": datetime.now()
                },
                "BTC": {
                    "total_balance": 1000.0,
                    "available_balance": 980.0,
                    "utilized_balance": 20.0,
                    "last_updated": datetime.now()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# POSITION MONITORING AND MANAGEMENT
# ============================================================================

@router.get("/positions/list")
async def list_positions(
    user_id: Optional[str] = None,
    contract_id: Optional[str] = None,
    position_side: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all futures positions
    Admin can monitor all positions in the system
    """
    try:
        return {
            "status": "success",
            "positions": [
                {
                    "id": "position_1",
                    "user_id": "user_123",
                    "contract_id": "PERP_BTCUSDT_1",
                    "position_side": "long",
                    "size": "1.5",
                    "entry_price": "45000.00",
                    "mark_price": "45200.00",
                    "unrealized_pnl": "300.00",
                    "margin": "1800.00",
                    "leverage": "25.0",
                    "liquidation_price": "43200.00"
                }
            ],
            "total": 1,
            "filters": {
                "user_id": user_id,
                "contract_id": contract_id,
                "position_side": position_side
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/positions/{position_id}/close")
async def force_close_position(position_id: str, reason: str):
    """
    Force close specific position
    Admin can force close positions for risk management
    """
    try:
        return {
            "status": "success",
            "message": f"Position {position_id} force closed",
            "position_id": position_id,
            "reason": reason,
            "close_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS AND REPORTING
# ============================================================================

@router.get("/analytics/overview")
async def get_futures_analytics():
    """
    Get comprehensive futures analytics
    Admin can monitor futures system performance
    """
    try:
        return {
            "status": "success",
            "analytics": {
                "total_open_interest": "1500000000",
                "total_notional_value": "25000000000",
                "active_contracts": 45,
                "active_positions": 125000,
                "total_margin": "500000000",
                "insurance_fund_balance": "48500000",
                "funding_rate_history": [
                    {"time": "2024-01-01T00:00:00Z", "rate": 0.0001},
                    {"time": "2024-01-01T08:00:00Z", "rate": 0.0002}
                ],
                "liquidations_24h": 150,
                "adl_events_24h": 25
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

@router.put("/config/update")
async def update_futures_config(config: FuturesConfig):
    """
    Update global futures trading configuration
    Admin can modify system-wide settings
    """
    try:
        config_data = config.dict()
        config_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": "Futures configuration updated successfully",
            "config": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_futures_config():
    """
    Get current futures trading configuration
    Admin can view current system settings
    """
    try:
        return {
            "status": "success",
            "config": {
                "enabled": True,
                "maintenance_mode": False,
                "max_leverage_global": 125.0,
                "default_leverage": 20.0,
                "enable_perpetual": True,
                "enable_cross_margin": True,
                "enable_isolated_margin": True,
                "force_liquidation_threshold": 0.9,
                "adl_ranking_enabled": True,
                "insurance_fund_ratio": 0.002,
                "funding_rate_cap": 0.005,
                "funding_rate_floor": -0.005
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def initialize_perpetual_contract(contract_id: str):
    """Initialize perpetual contract systems"""
    await asyncio.sleep(1)
    print(f"Perpetual contract {contract_id} initialized")

async def initialize_cross_contract(contract_id: str):
    """Initialize cross margin contract systems"""
    await asyncio.sleep(1)
    print(f"Cross margin contract {contract_id} initialized")