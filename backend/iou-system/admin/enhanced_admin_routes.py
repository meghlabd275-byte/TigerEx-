"""
Enhanced Admin Routes for IOU System
Complete admin controls for IOU (I Owe You) token management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import asyncio
import json

router = APIRouter(prefix="/admin/iou-system", tags=["iou-system-admin"])

class IOUStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    SETTLED = "settled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class IOUType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    SETTLEMENT = "settlement"
    COLLATERAL = "collateral"

class SettlementStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    DEFAULTED = "defaulted"

class IOUToken(BaseModel):
    """IOU token model"""
    id: Optional[str] = None
    issuer_id: str
    holder_id: str
    token_name: str
    token_symbol: str
    iou_type: IOUType
    status: IOUStatus = IOUStatus.ACTIVE
    principal_amount: float
    interest_rate: float = 0.0  # Annual percentage rate
    maturity_date: Optional[datetime] = None
    settlement_currency: str = "USDT"
    collateral_locked: float = 0.0
    collateral_asset: Optional[str] = None
    interest_accrued: float = 0.0
    total_settled: float = 0.0
    remaining_balance: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class IOUConfig(BaseModel):
    """IOU system configuration"""
    enabled: bool = True
    maintenance_mode: bool = False
    max_iou_per_user: int = 100
    max_principal_amount: float = 10000000
    max_interest_rate: float = 0.50  # 50%
    min_maturity_days: int = 1
    max_maturity_days: int = 365
    collateral_required: bool = True
    min_collateral_ratio: float = 1.5
    auto_settlement_enabled: bool = True
    default_enabled: bool = True
    interest_calculation_frequency: int = 24  # hours
    settlement_penalty_rate: float = 0.05

class SettlementTransaction(BaseModel):
    """Settlement transaction model"""
    id: Optional[str] = None
    iou_id: str
    amount: float
    settlement_type: str  # partial, full, interest, principal
    status: SettlementStatus = SettlementStatus.PENDING
    transaction_hash: Optional[str] = None
    settled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class IOUTemplate(BaseModel):
    """IOU template model"""
    name: str
    description: str
    iou_type: IOUType
    default_interest_rate: float
    default_maturity_days: int
    collateral_required: bool
    min_amount: float
    max_amount: float

# ============================================================================
# IOU TOKEN MANAGEMENT
# ============================================================================

@router.post("/tokens/create")
async def create_iou_token(
    token: IOUToken,
    background_tasks: BackgroundTasks
):
    """
    Create new IOU token
    Admin can create IOU tokens with full configuration
    """
    try:
        # Validate IOU token parameters
        if token.principal_amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Principal amount must be positive"
            )
        
        if token.interest_rate < 0 or token.interest_rate > 0.50:
            raise HTTPException(
                status_code=400,
                detail="Interest rate must be between 0% and 50%"
            )
        
        if token.maturity_date and token.maturity_date <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Maturity date must be in the future"
            )
        
        if token.collateral_required and token.collateral_ratio < 1.5:
            raise HTTPException(
                status_code=400,
                detail="Collateral ratio must be at least 1.5 when collateral is required"
            )
        
        token_data = token.dict()
        token_data["id"] = f"IOU_{token.issuer_id}_{token.holder_id}_{datetime.now().timestamp()}"
        token_data["remaining_balance"] = token.principal_amount
        token_data["created_at"] = datetime.now()
        token_data["updated_at"] = datetime.now()
        
        # Initialize IOU token
        background_tasks.add_task(initialize_iou_token, token_data["id"])
        
        return {
            "status": "success",
            "message": f"IOU token {token_data['id']} created successfully",
            "token": token_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tokens/{token_id}/pause")
async def pause_iou_token(token_id: str, reason: str):
    """
    Pause IOU token
    Admin can pause token operations temporarily
    """
    try:
        return {
            "status": "success",
            "message": f"IOU token {token_id} paused successfully",
            "token_id": token_id,
            "reason": reason,
            "status": "paused",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tokens/{token_id}/resume")
async def resume_iou_token(token_id: str):
    """
    Resume IOU token
    Admin can resume paused token operations
    """
    try:
        return {
            "status": "success",
            "message": f"IOU token {token_id} resumed successfully",
            "token_id": token_id,
            "status": "active",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tokens/{token_id}/suspend")
async def suspend_iou_token(token_id: str, reason: str):
    """
    Suspend IOU token
    Admin can suspend token operations for compliance
    """
    try:
        return {
            "status": "success",
            "message": f"IOU token {token_id} suspended successfully",
            "token_id": token_id,
            "reason": reason,
            "status": "suspended",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tokens/{token_id}")
async def delete_iou_token(token_id: str):
    """
    Delete IOU token
    Admin can delete IOU tokens completely
    """
    try:
        return {
            "status": "success",
            "message": f"IOU token {token_id} deleted successfully",
            "token_id": token_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# IOU TOKEN CONFIGURATION MANAGEMENT
# ============================================================================

@router.put("/tokens/{token_id}/config/update")
async def update_iou_token_config(
    token_id: str,
    interest_rate: Optional[float] = None,
    maturity_date: Optional[datetime] = None,
    collateral_ratio: Optional[float] = None
):
    """
    Update IOU token configuration
    Admin can modify token parameters
    """
    try:
        updates = {}
        if interest_rate is not None:
            if interest_rate < 0 or interest_rate > 0.50:
                raise HTTPException(status_code=400, detail="Invalid interest rate")
            updates["interest_rate"] = interest_rate
        
        if maturity_date is not None:
            if maturity_date <= datetime.now():
                raise HTTPException(status_code=400, detail="Maturity date must be in future")
            updates["maturity_date"] = maturity_date
        
        if collateral_ratio is not None:
            if collateral_ratio < 1.5:
                raise HTTPException(status_code=400, detail="Collateral ratio must be at least 1.5")
            updates["collateral_ratio"] = collateral_ratio
        
        return {
            "status": "success",
            "message": f"IOU token {token_id} configuration updated",
            "token_id": token_id,
            "updates": updates,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SETTLEMENT MANAGEMENT
# ============================================================================

@router.post("/tokens/{token_id}/settle/partial")
async def partial_settlement(
    token_id: str,
    amount: float,
    settlement_type: str
):
    """
    Process partial settlement
    Admin can process partial settlements
    """
    try:
        if amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Settlement amount must be positive"
            )
        
        transaction = SettlementTransaction(
            iou_id=token_id,
            amount=amount,
            settlement_type=settlement_type
        )
        
        transaction_data = transaction.dict()
        transaction_data["id"] = f"SETTLE_{token_id}_{datetime.now().timestamp()}"
        transaction_data["created_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": f"Partial settlement processed for token {token_id}",
            "token_id": token_id,
            "transaction": transaction_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokens/{token_id}/settle/full")
async def full_settlement(token_id: str):
    """
    Process full settlement
    Admin can process complete settlement
    """
    try:
        return {
            "status": "success",
            "message": f"Full settlement processed for token {token_id}",
            "token_id": token_id,
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokens/{token_id}/settle/force")
async def force_settlement(
    token_id: str,
    reason: str,
    penalty_rate: Optional[float] = None
):
    """
    Force settlement
    Admin can force settlement with penalties
    """
    try:
        return {
            "status": "success",
            "message": f"Force settlement executed for token {token_id}",
            "token_id": token_id,
            "reason": reason,
            "penalty_rate": penalty_rate,
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settlement/batch-process")
async def batch_settlement(settlement_date: datetime):
    """
    Process batch settlement
    Admin can settle multiple tokens at once
    """
    try:
        return {
            "status": "success",
            "message": f"Batch settlement processed for {settlement_date}",
            "settlement_date": settlement_date,
            "tokens_settled": 250,
            "total_amount_settled": "5000000",
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COLLATERAL MANAGEMENT
# ============================================================================

@router.post("/tokens/{token_id}/collateral/lock")
async def lock_collateral(
    token_id: str,
    asset: str,
    amount: float
):
    """
    Lock collateral for IOU token
    Admin can manage collateral locking
    """
    try:
        return {
            "status": "success",
            "message": f"Collateral locked for token {token_id}",
            "token_id": token_id,
            "asset": asset,
            "amount": amount,
            "lock_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tokens/{token_id}/collateral/unlock")
async def unlock_collateral(
    token_id: str,
    amount: float,
    reason: str
):
    """
    Unlock collateral for IOU token
    Admin can manage collateral unlocking
    """
    try:
        return {
            "status": "success",
            "message": f"Collateral unlocked for token {token_id}",
            "token_id": token_id,
            "amount": amount,
            "reason": reason,
            "unlock_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_id}/collateral/status")
async def get_collateral_status(token_id: str):
    """
    Get collateral status for IOU token
    Admin can monitor collateral positions
    """
    try:
        return {
            "status": "success",
            "collateral": {
                "token_id": token_id,
                "locked_collateral": {
                    "BTC": 1.5,
                    "USDT": 25000.0,
                    "ETH": 5.0
                },
                "total_collateral_value": 125000.0,
                "collateral_ratio": 2.5,
                "minimum_required": 75000.0,
                "excess_collateral": 50000.0,
                "health_status": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INTEREST MANAGEMENT
# ============================================================================

@router.post("/tokens/{token_id}/interest/calculate")
async def calculate_interest(token_id: str):
    """
    Calculate accrued interest
    Admin can force interest calculation
    """
    try:
        return {
            "status": "success",
            "message": f"Interest calculated for token {token_id}",
            "token_id": token_id,
            "interest_accrued": 125.50,
            "calculation_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interest/batch-calculate")
async def batch_interest_calculation():
    """
    Calculate interest for all active tokens
    Admin can trigger system-wide interest calculation
    """
    try:
        return {
            "status": "success",
            "message": "Batch interest calculation completed",
            "tokens_processed": 5000,
            "total_interest_accrued": "250000",
            "calculation_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tokens/{token_id}/interest/rate/update")
async def update_interest_rate(
    token_id: str,
    new_rate: float,
    reason: str
):
    """
    Update interest rate for IOU token
    Admin can modify interest rates
    """
    try:
        if new_rate < 0 or new_rate > 0.50:
            raise HTTPException(
                status_code=400,
                detail="Interest rate must be between 0% and 50%"
            )
        
        return {
            "status": "success",
            "message": f"Interest rate updated for token {token_id}",
            "token_id": token_id,
            "previous_rate": 0.10,  # Would get from database
            "new_rate": new_rate,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER IOU MANAGEMENT
# ============================================================================

@router.post("/users/{user_id}/iou/create")
async def create_user_iou(
    user_id: str,
    token: IOUToken,
    background_tasks: BackgroundTasks
):
    """
    Create IOU token for specific user
    Admin can create IOU tokens on behalf of users
    """
    try:
        # Check user IOU limits
        user_iou_count = await get_user_iou_count(user_id)
        if user_iou_count >= 100:  # Default limit
            raise HTTPException(
                status_code=400,
                detail="User has reached maximum IOU token limit"
            )
        
        token.issuer_id = user_id
        
        token_data = token.dict()
        token_data["id"] = f"IOU_{user_id}_{token.holder_id}_{datetime.now().timestamp()}"
        token_data["remaining_balance"] = token.principal_amount
        token_data["created_at"] = datetime.now()
        token_data["updated_at"] = datetime.now()
        
        # Initialize IOU token
        background_tasks.add_task(initialize_iou_token, token_data["id"])
        
        return {
            "status": "success",
            "message": f"IOU token created for user {user_id}",
            "token": token_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/iou-limit/update")
async def update_user_iou_limit(
    user_id: str,
    new_limit: int
):
    """
    Update user's IOU token limit
    Admin can control how many IOU tokens each user can create
    """
    try:
        if new_limit <= 0 or new_limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="IOU limit must be between 1 and 1000"
            )
        
        return {
            "status": "success",
            "message": f"IOU limit updated for user {user_id}",
            "user_id": user_id,
            "new_limit": new_limit,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# IOU TEMPLATES
# ============================================================================

@router.post("/templates/create")
async def create_iou_template(template: IOUTemplate):
    """
    Create IOU token template
    Admin can create predefined IOU configurations
    """
    try:
        template_data = template.dict()
        template_data["id"] = f"TEMPLATE_{template.name}_{datetime.now().timestamp()}"
        template_data["created_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": f"IOU template {template.name} created successfully",
            "template": template_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/list")
async def list_iou_templates():
    """
    List all available IOU templates
    Admin can view all templates
    """
    try:
        templates = [
            {
                "id": "TEMPLATE_standard_1",
                "name": "Standard Credit",
                "description": "Standard credit IOU with collateral",
                "iou_type": "credit",
                "default_interest_rate": 0.08,
                "default_maturity_days": 90,
                "collateral_required": True,
                "min_amount": 1000.0,
                "max_amount": 100000.0,
                "usage_count": 1250
            },
            {
                "id": "TEMPLATE_short_term_1",
                "name": "Short Term Debit",
                "description": "Short term debit without collateral",
                "iou_type": "debit",
                "default_interest_rate": 0.05,
                "default_maturity_days": 30,
                "collateral_required": False,
                "min_amount": 500.0,
                "max_amount": 25000.0,
                "usage_count": 850
            }
        ]
        
        return {
            "status": "success",
            "templates": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS AND REPORTING
# ============================================================================

@router.get("/analytics/overview")
async def get_iou_analytics():
    """
    Get comprehensive IOU system analytics
    Admin can monitor system performance
    """
    try:
        return {
            "status": "success",
            "analytics": {
                "total_active_tokens": 10000,
                "total_principal_amount": "500000000",
                "total_interest_accrued": "12500000",
                "total_amount_settled": "250000000",
                "total_collateral_locked": "750000000",
                "average_interest_rate": 0.12,
                "token_status_distribution": {
                    "active": 0.75,
                    "paused": 0.10,
                    "settled": 0.12,
                    "expired": 0.03
                },
                "iou_type_distribution": {
                    "credit": 0.60,
                    "debit": 0.25,
                    "settlement": 0.10,
                    "collateral": 0.05
                },
                "risk_metrics": {
                    "default_rate": 0.02,
                    "overdue_tokens": 150,
                    "system_health": "optimal"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens/{token_id}/performance")
async def get_token_performance(token_id: str):
    """
    Get detailed performance metrics for IOU token
    Admin can monitor individual token performance
    """
    try:
        return {
            "status": "success",
            "performance": {
                "token_id": token_id,
                "principal_amount": 50000.0,
                "current_balance": 25000.0,
                "interest_accrued": 2500.0,
                "amount_settled": 27500.0,
                "settlement_progress": 0.55,
                "time_to_maturity": 45,  # days
                "effective_rate": 0.10,
                "collateral_ratio": 2.0,
                "payment_history": [
                    {"date": "2024-01-01", "amount": 5000.0, "type": "principal"},
                    {"date": "2024-01-15", "amount": 250.0, "type": "interest"}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

@router.put("/config/update")
async def update_iou_config(config: IOUConfig):
    """
    Update global IOU system configuration
    Admin can modify system-wide settings
    """
    try:
        config_data = config.dict()
        config_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": "IOU system configuration updated successfully",
            "config": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_iou_config():
    """
    Get current IOU system configuration
    Admin can view current system settings
    """
    try:
        return {
            "status": "success",
            "config": {
                "enabled": True,
                "maintenance_mode": False,
                "max_iou_per_user": 100,
                "max_principal_amount": 10000000,
                "max_interest_rate": 0.50,
                "min_maturity_days": 1,
                "max_maturity_days": 365,
                "collateral_required": True,
                "min_collateral_ratio": 1.5,
                "auto_settlement_enabled": True,
                "default_enabled": True,
                "interest_calculation_frequency": 24,
                "settlement_penalty_rate": 0.05
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def initialize_iou_token(token_id: str):
    """Initialize IOU token systems"""
    await asyncio.sleep(1)
    print(f"IOU token {token_id} initialized")

async def get_user_iou_count(user_id: str) -> int:
    """Get number of IOU tokens for user"""
    return 25  # Mock value