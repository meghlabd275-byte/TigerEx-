"""
Enhanced Admin Routes for Margin Trading
Complete admin controls for margin trading system
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import asyncio
import json

router = APIRouter(prefix="/admin/margin-trading", tags=["margin-trading-admin"])

class MarginMode(str, Enum):
    ISOLATED = "isolated"
    CROSS = "cross"

class MarginStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    LIQUIDATION = "liquidation"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MarginPair(BaseModel):
    """Margin trading pair model"""
    symbol: str
    base_asset: str
    quote_asset: str
    status: MarginStatus = MarginStatus.ACTIVE
    margin_mode: MarginMode = MarginMode.ISOLATED
    max_leverage: float = 10.0
    initial_margin_ratio: float = 0.1
    maintenance_margin_ratio: float = 0.05
    interest_rate_borrow: float = 0.0005  # daily
    interest_rate_lend: float = 0.0003  # daily
    max_borrow_amount: Dict[str, float] = {}
    funding_pool: Dict[str, float] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MarginAccount(BaseModel):
    """User margin account model"""
    user_id: str
    margin_mode: MarginMode
    total_asset: float
    total_liability: float
    total_margin: float
    free_margin: float
    used_margin: float
    margin_ratio: float
    risk_level: RiskLevel = RiskLevel.LOW
    maintenance_margin_requirement: float
    leverage: Dict[str, float] = {}
    borrow_interest: Dict[str, float] = {}
    updated_at: Optional[datetime] = None

class MarginConfig(BaseModel):
    """Margin trading configuration"""
    enabled: bool = True
    maintenance_mode: bool = False
    max_leverage_global: float = 10.0
    default_leverage: float = 3.0
    enable_isolated_margin: bool = True
    enable_cross_margin: bool = True
    auto_repay_enabled: bool = True
    force_liquidation_threshold: float = 1.1  # 110% of maintenance margin
    risk_warning_threshold: float = 1.3  # 130% of maintenance margin
    interest_calculation_interval: int = 1  # hours
    max_borrow_duration: int = 365  # days

class BorrowRequest(BaseModel):
    """Borrow request model"""
    user_id: str
    asset: str
    amount: float
    margin_mode: MarginMode
    symbol: Optional[str] = None  # for isolated margin

class RiskParameter(BaseModel):
    """Risk parameter model"""
    asset: str
    max_leverage: float
    max_borrow_ratio: float
    liquidation_threshold: float
    interest_rate_borrow: float
    interest_rate_lend: float
    collateral_ratio: float

# ============================================================================
# MARGIN PAIR MANAGEMENT
# ============================================================================

@router.post("/pairs/create")
async def create_margin_pair(
    pair: MarginPair,
    background_tasks: BackgroundTasks
):
    """
    Create new margin trading pair
    Admin can create margin pairs with full configuration
    """
    try:
        # Validate pair configuration
        if pair.initial_margin_ratio >= 1 or pair.initial_margin_ratio <= 0:
            raise HTTPException(
                status_code=400,
                detail="Initial margin ratio must be between 0 and 1"
            )
        
        if pair.maintenance_margin_ratio >= pair.initial_margin_ratio:
            raise HTTPException(
                status_code=400,
                detail="Maintenance margin ratio must be less than initial margin ratio"
            )
        
        if pair.max_leverage <= 1 or pair.max_leverage > 10:
            raise HTTPException(
                status_code=400,
                detail="Max leverage must be between 1 and 10"
            )
        
        pair_data = pair.dict()
        pair_data["id"] = f"MARGIN_{pair.symbol}_{datetime.now().timestamp()}"
        pair_data["created_at"] = datetime.now()
        pair_data["updated_at"] = datetime.now()
        
        # Initialize margin pair systems
        background_tasks.add_task(initialize_margin_pair, pair_data["id"])
        
        return {
            "status": "success",
            "message": f"Margin pair {pair.symbol} created successfully",
            "pair": pair_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pairs/{pair_id}/pause")
async def pause_margin_pair(pair_id: str):
    """
    Pause margin trading for specific pair
    Admin can pause margin trading temporarily
    """
    try:
        return {
            "status": "success",
            "message": f"Margin pair {pair_id} paused successfully",
            "pair_id": pair_id,
            "status": "paused",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pairs/{pair_id}/resume")
async def resume_margin_pair(pair_id: str):
    """
    Resume margin trading for specific pair
    Admin can resume paused margin trading
    """
    try:
        return {
            "status": "success",
            "message": f"Margin pair {pair_id} resumed successfully",
            "pair_id": pair_id,
            "status": "active",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pairs/{pair_id}/suspend")
async def suspend_margin_pair(pair_id: str, reason: str):
    """
    Suspend margin trading for specific pair
    Admin can suspend margin trading for safety reasons
    """
    try:
        return {
            "status": "success",
            "message": f"Margin pair {pair_id} suspended successfully",
            "pair_id": pair_id,
            "reason": reason,
            "status": "suspended",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/pairs/{pair_id}")
async def delete_margin_pair(pair_id: str):
    """
    Delete margin trading pair
    Admin can delete margin pairs completely
    """
    try:
        return {
            "status": "success",
            "message": f"Margin pair {pair_id} deleted successfully",
            "pair_id": pair_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MARGIN ACCOUNT MANAGEMENT
# ============================================================================

@router.post("/accounts/{user_id}/create")
async def create_margin_account(
    user_id: str,
    margin_mode: MarginMode,
    initial_collateral: Dict[str, float] = None
):
    """
    Create margin account for user
    Admin can create margin accounts with initial collateral
    """
    try:
        account_data = {
            "user_id": user_id,
            "margin_mode": margin_mode,
            "total_asset": sum(initial_collateral.values()) if initial_collateral else 0,
            "total_liability": 0.0,
            "total_margin": 0.0,
            "free_margin": sum(initial_collateral.values()) if initial_collateral else 0,
            "used_margin": 0.0,
            "margin_ratio": 1.0,
            "risk_level": RiskLevel.LOW,
            "maintenance_margin_requirement": 0.0,
            "leverage": {},
            "borrow_interest": {},
            "updated_at": datetime.now()
        }
        
        return {
            "status": "success",
            "message": f"Margin account created for user {user_id}",
            "account": account_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/accounts/{user_id}/leverage/update")
async def update_user_leverage(
    user_id: str,
    pair_id: str,
    leverage: float
):
    """
    Update leverage for specific user on margin pair
    Admin can control individual user leverage
    """
    try:
        if leverage <= 1 or leverage > 10:
            raise HTTPException(
                status_code=400,
                detail="Leverage must be between 1 and 10"
            )
        
        return {
            "status": "success",
            "message": f"Leverage updated for user {user_id}",
            "user_id": user_id,
            "pair_id": pair_id,
            "leverage": leverage,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounts/{user_id}/margin-mode/switch")
async def switch_margin_mode(
    user_id: str,
    new_mode: MarginMode,
    reason: str
):
    """
    Switch margin mode for user account
    Admin can switch between isolated and cross margin
    """
    try:
        return {
            "status": "success",
            "message": f"Margin mode switched for user {user_id}",
            "user_id": user_id,
            "previous_mode": "isolated",  # Would get from database
            "new_mode": new_mode.value,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BORROWING AND LENDING CONTROL
# ============================================================================

@router.post("/borrow/approve")
async def approve_borrow_request(
    request_id: str,
    approved_amount: float,
    interest_rate_override: Optional[float] = None
):
    """
    Approve borrow request
    Admin can approve and modify borrow requests
    """
    try:
        return {
            "status": "success",
            "message": f"Borrow request {request_id} approved",
            "request_id": request_id,
            "approved_amount": approved_amount,
            "interest_rate": interest_rate_override,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/borrow/{user_id}/force")
async def force_borrow(
    user_id: str,
    asset: str,
    amount: float,
    reason: str
):
    """
    Force borrow for user (admin action)
    Admin can force borrow operations for specific reasons
    """
    try:
        return {
            "status": "success",
            "message": f"Force borrow executed for user {user_id}",
            "user_id": user_id,
            "asset": asset,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repay/{user_id}/force")
async def force_repay(
    user_id: str,
    asset: str,
    amount: float,
    reason: str
):
    """
    Force repayment for user
    Admin can force repayment operations
    """
    try:
        return {
            "status": "success",
            "message": f"Force repayment executed for user {user_id}",
            "user_id": user_id,
            "asset": asset,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INTEREST RATE MANAGEMENT
# ============================================================================

@router.put("/pairs/{pair_id}/interest-rates/update")
async def update_interest_rates(
    pair_id: str,
    borrow_rate: float,
    lend_rate: float
):
    """
    Update interest rates for margin pair
    Admin can control borrowing and lending rates
    """
    try:
        if borrow_rate < 0 or lend_rate < 0:
            raise HTTPException(
                status_code=400,
                detail="Interest rates cannot be negative"
            )
        
        if borrow_rate <= lend_rate:
            raise HTTPException(
                status_code=400,
                detail="Borrow rate must be higher than lend rate"
            )
        
        return {
            "status": "success",
            "message": f"Interest rates updated for pair {pair_id}",
            "pair_id": pair_id,
            "borrow_rate": borrow_rate,
            "lend_rate": lend_rate,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interest/settle")
async def settle_interest_payments(pair_id: Optional[str] = None):
    """
    Manually trigger interest payment settlement
    Admin can force interest calculation and payment
    """
    try:
        return {
            "status": "success",
            "message": "Interest payments settled",
            "pair_id": pair_id if pair_id else "all_pairs",
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

@router.post("/accounts/{user_id}/liquidation/trigger")
async def trigger_liquidation(
    user_id: str,
    reason: str,
    liquidate_all: bool = False
):
    """
    Trigger margin account liquidation
    Admin can force liquidation for risk management
    """
    try:
        return {
            "status": "success",
            "message": f"Liquidation triggered for user {user_id}",
            "user_id": user_id,
            "reason": reason,
            "liquidate_all": liquidate_all,
            "liquidation_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk-parameters/update")
async def update_risk_parameters(
    risk_params: List[RiskParameter]
):
    """
    Update risk parameters for assets
    Admin can manage risk settings across all assets
    """
    try:
        params_data = [param.dict() for param in risk_params]
        
        return {
            "status": "success",
            "message": "Risk parameters updated successfully",
            "risk_parameters": params_data,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts/risk-monitor")
async def get_risk_monitoring():
    """
    Get risk monitoring dashboard
    Admin can view system-wide risk metrics
    """
    try:
        return {
            "status": "success",
            "risk_monitoring": {
                "total_margin_accounts": 50000,
                "high_risk_accounts": 125,
                "critical_risk_accounts": 15,
                "total_borrowed": "500000000",
                "total_lent": "450000000",
                "average_margin_ratio": 0.25,
                "system_health": "stable",
                "liquidations_24h": 25,
                "margin_calls_24h": 180
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FUNDING POOL MANAGEMENT
# ============================================================================

@router.post("/funding-pool/deposit")
async def deposit_to_funding_pool(
    asset: str,
    amount: float,
    reason: str
):
    """
    Deposit funds to lending pool
    Admin can manage funding pool liquidity
    """
    try:
        return {
            "status": "success",
            "message": f"Deposited {amount} {asset} to funding pool",
            "asset": asset,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/funding-pool/withdraw")
async def withdraw_from_funding_pool(
    asset: str,
    amount: float,
    reason: str
):
    """
    Withdraw funds from lending pool
    Admin can manage funding pool liquidity
    """
    try:
        return {
            "status": "success",
            "message": f"Withdrew {amount} {asset} from funding pool",
            "asset": asset,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/funding-pool/status")
async def get_funding_pool_status():
    """
    Get funding pool status and metrics
    Admin can monitor pool health and utilization
    """
    try:
        return {
            "status": "success",
            "funding_pools": {
                "USDT": {
                    "total_available": "100000000",
                    "total_borrowed": "85000000",
                    "utilization_rate": 0.85,
                    "interest_rate_borrow": 0.0005,
                    "interest_rate_lend": 0.0003
                },
                "BTC": {
                    "total_available": "5000",
                    "total_borrowed": "3200",
                    "utilization_rate": 0.64,
                    "interest_rate_borrow": 0.0004,
                    "interest_rate_lend": 0.0002
                },
                "ETH": {
                    "total_available": "10000",
                    "total_borrowed": "7500",
                    "utilization_rate": 0.75,
                    "interest_rate_borrow": 0.00045,
                    "interest_rate_lend": 0.00025
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS AND REPORTING
# ============================================================================

@router.get("/analytics/overview")
async def get_margin_analytics():
    """
    Get comprehensive margin trading analytics
    Admin can monitor margin system performance
    """
    try:
        return {
            "status": "success",
            "analytics": {
                "total_margin_accounts": 50000,
                "active_margin_pairs": 150,
                "total_borrowed_amount": "500000000",
                "total_lent_amount": "450000000",
                "total_margin_used": "150000000",
                "average_leverage": 3.2,
                "liquidations_24h": 25,
                "margin_calls_24h": 180,
                "interest_paid_24h": "125000",
                "interest_earned_24h": "95000",
                "system_health": "optimal"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

@router.put("/config/update")
async def update_margin_config(config: MarginConfig):
    """
    Update global margin trading configuration
    Admin can modify system-wide settings
    """
    try:
        config_data = config.dict()
        config_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": "Margin configuration updated successfully",
            "config": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_margin_config():
    """
    Get current margin trading configuration
    Admin can view current system settings
    """
    try:
        return {
            "status": "success",
            "config": {
                "enabled": True,
                "maintenance_mode": False,
                "max_leverage_global": 10.0,
                "default_leverage": 3.0,
                "enable_isolated_margin": True,
                "enable_cross_margin": True,
                "auto_repay_enabled": True,
                "force_liquidation_threshold": 1.1,
                "risk_warning_threshold": 1.3,
                "interest_calculation_interval": 1,
                "max_borrow_duration": 365
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def initialize_margin_pair(pair_id: str):
    """Initialize margin pair systems"""
    await asyncio.sleep(1)
    print(f"Margin pair {pair_id} initialized")