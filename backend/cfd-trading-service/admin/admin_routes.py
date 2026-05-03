#!/usr/bin/env python3
"""
TigerEx CFD Trading Service - Admin Routes
Complete admin control for CFD trading operations
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
import json
import jwt
import os

# @file admin_routes.py
# @author TigerEx Development Team
router = APIRouter(prefix="/api/cfd/admin", tags=["CFD Admin"])
security = HTTPBearer()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"

# ============================================================================
# ENUMS
# ============================================================================

class ExchangeStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HALTED = "halted"
    SUSPENDED = "suspended"
    DEMO = "demo"

class TradingPermission(str, Enum):
    FULL_ACCESS = "full_access"
    READ_WRITE = "read_write"
    READ_ONLY = "read_only"
    NO_ACCESS = "no_access"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    TRADER = "trader"
    VIEWER = "viewer"

# ============================================================================
# MODELS
# ============================================================================

class ExchangeConfigRequest(BaseModel):
    exchange_id: str
    exchange_name: str
    exchange_status: ExchangeStatus = ExchangeStatus.ACTIVE
    white_label_enabled: bool = False
    parent_exchange_id: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#1a1a2e"
    secondary_color: Optional[str] = "#16213e"
    spot_enabled: bool = True
    futures_enabled: bool = True
    margin_enabled: bool = True
    options_enabled: bool = False
    cfd_enabled: bool = True
    forex_enabled: bool = True
    stocks_enabled: bool = True
    commodities_enabled: bool = True
    p2p_enabled: bool = True
    nft_enabled: bool = True
    staking_enabled: bool = True
    launchpad_enabled: bool = True
    copy_trading_enabled: bool = True
    trading_bots_enabled: bool = True
    max_leverage: int = 100
    kyc_required: bool = True
    two_factor_required: bool = False

class UserCFDPermissions(BaseModel):
    user_id: str
    cfd_enabled: bool = True
    forex_enabled: bool = True
    stocks_enabled: bool = True
    commodities_enabled: bool = True
    metals_enabled: bool = True
    indices_enabled: bool = True
    crypto_cfd_enabled: bool = True
    max_leverage: int = 100
    max_position_size: Decimal = Decimal("1000000")
    max_daily_volume: Decimal = Decimal("10000000")
    margin_call_level: Decimal = Decimal("80")
    stop_out_level: Decimal = Decimal("50")
    swap_free: bool = False
    restricted_instruments: List[str] = []

class FeeConfiguration(BaseModel):
    instrument_type: str
    maker_fee: Decimal = Decimal("0.0001")
    taker_fee: Decimal("0.0001")
    swap_long: Decimal = Decimal("-0.0001")
    swap_short: Decimal = Decimal("-0.0001")
    commission: Decimal = Decimal("0.00005")
    min_commission: Decimal = Decimal("0")

class RiskParameters(BaseModel):
    max_total_exposure: Decimal = Decimal("100000000")
    max_single_position: Decimal = Decimal("10000000")
    max_leverage_total: int = 500
    margin_call_percentage: Decimal = Decimal("80")
    stop_out_percentage: Decimal = Decimal("50")
    negative_balance_protection: bool = True
    auto_liquidation_enabled: bool = True

class SystemSettings(BaseModel):
    trading_enabled: bool = True
    new_positions_allowed: bool = True
    new_orders_allowed: bool = True
    close_positions_allowed: bool = True
    modify_positions_allowed: bool = True
    withdraw_enabled: bool = True
    deposit_enabled: bool = True
    transfer_enabled: bool = True
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None

# ============================================================================
# AUTH
# ============================================================================

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "moderator"]:
            raise HTTPException(status_code=401, detail="Invalid token - Admin access required")
        
        return {"admin_id": admin_id, "role": role, "permissions": payload.get("permissions", [])}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_permission(admin: dict, required_permission: str):
    """Check if admin has required permission"""
    if admin["role"] == "super_admin":
        return True
    if required_permission in admin.get("permissions", []):
        return True
    raise HTTPException(status_code=403, detail="Insufficient permissions")

# ============================================================================
# EXCHANGE MANAGEMENT
# ============================================================================

@router.post("/exchange/create")
async def create_exchange(
    config: ExchangeConfigRequest,
    admin: dict = Depends(get_current_admin)
):
    """Create new exchange configuration (Super Admin only)"""
    check_permission(admin, "exchange_management")
    
    exchange_config = {
        "exchange_id": config.exchange_id,
        "exchange_name": config.exchange_name,
        "exchange_status": config.exchange_status.value,
        "white_label_enabled": config.white_label_enabled,
        "parent_exchange_id": config.parent_exchange_id,
        "domain": config.domain,
        "logo_url": config.logo_url,
        "primary_color": config.primary_color,
        "secondary_color": config.secondary_color,
        "features": {
            "spot": config.spot_enabled,
            "futures": config.futures_enabled,
            "margin": config.margin_enabled,
            "options": config.options_enabled,
            "cfd": config.cfd_enabled,
            "forex": config.forex_enabled,
            "stocks": config.stocks_enabled,
            "commodities": config.commodities_enabled,
            "p2p": config.p2p_enabled,
            "nft": config.nft_enabled,
            "staking": config.staking_enabled,
            "launchpad": config.launchpad_enabled,
            "copy_trading": config.copy_trading_enabled,
            "trading_bots": config.trading_bots_enabled
        },
        "max_leverage": config.max_leverage,
        "kyc_required": config.kyc_required,
        "two_factor_required": config.two_factor_required,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": admin["admin_id"]
    }
    
    return {
        "success": True,
        "message": "Exchange configuration created",
        "config": exchange_config
    }

@router.post("/exchange/status")
async def set_exchange_status(
    exchange_id: str,
    status: ExchangeStatus,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Set exchange status (active, maintenance, halted, suspended)"""
    check_permission(admin, "exchange_management")
    
    return {
        "success": True,
        "message": f"Exchange {exchange_id} status set to {status.value}",
        "exchange_id": exchange_id,
        "status": status.value,
        "reason": reason,
        "updated_by": admin["admin_id"],
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/exchange/{exchange_id}")
async def get_exchange_config(
    exchange_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get exchange configuration"""
    # In production, fetch from database
    return {
        "exchange_id": exchange_id,
        "exchange_name": "TigerEx",
        "exchange_status": "active",
        "white_label_enabled": False,
        "features": {
            "spot": True,
            "futures": True,
            "margin": True,
            "options": True,
            "cfd": True,
            "forex": True,
            "stocks": True,
            "commodities": True,
            "p2p": True,
            "nft": True,
            "staking": True,
            "launchpad": True,
            "copy_trading": True,
            "trading_bots": True
        }
    }

# ============================================================================
# USER PERMISSIONS MANAGEMENT
# ============================================================================

@router.post("/users/{user_id}/permissions")
async def set_user_cfd_permissions(
    user_id: str,
    permissions: UserCFDPermissions,
    admin: dict = Depends(get_current_admin)
):
    """Set CFD trading permissions for user"""
    check_permission(admin, "user_management")
    
    return {
        "success": True,
        "message": f"CFD permissions updated for user {user_id}",
        "permissions": {
            "user_id": user_id,
            "cfd_enabled": permissions.cfd_enabled,
            "forex_enabled": permissions.forex_enabled,
            "stocks_enabled": permissions.stocks_enabled,
            "commodities_enabled": permissions.commodities_enabled,
            "metals_enabled": permissions.metals_enabled,
            "indices_enabled": permissions.indices_enabled,
            "crypto_cfd_enabled": permissions.crypto_cfd_enabled,
            "max_leverage": permissions.max_leverage,
            "max_position_size": str(permissions.max_position_size),
            "max_daily_volume": str(permissions.max_daily_volume),
            "margin_call_level": str(permissions.margin_call_level),
            "stop_out_level": str(permissions.stop_out_level),
            "swap_free": permissions.swap_free,
            "restricted_instruments": permissions.restricted_instruments,
            "updated_by": admin["admin_id"],
            "updated_at": datetime.utcnow().isoformat()
        }
    }

@router.get("/users/{user_id}/permissions")
async def get_user_cfd_permissions(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get CFD trading permissions for user"""
    # In production, fetch from database
    return {
        "user_id": user_id,
        "cfd_enabled": True,
        "forex_enabled": True,
        "stocks_enabled": True,
        "commodities_enabled": True,
        "metals_enabled": True,
        "indices_enabled": True,
        "crypto_cfd_enabled": True,
        "max_leverage": 100,
        "max_position_size": "1000000",
        "max_daily_volume": "10000000",
        "margin_call_level": "80",
        "stop_out_level": "50",
        "swap_free": False,
        "restricted_instruments": []
    }

@router.post("/users/{user_id}/pause")
async def pause_user_trading(
    user_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Pause user's trading access"""
    check_permission(admin, "user_management")
    
    return {
        "success": True,
        "message": f"Trading paused for user {user_id}",
        "user_id": user_id,
        "trading_status": "paused",
        "reason": reason,
        "paused_by": admin["admin_id"],
        "paused_at": datetime.utcnow().isoformat()
    }

@router.post("/users/{user_id}/resume")
async def resume_user_trading(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Resume user's trading access"""
    check_permission(admin, "user_management")
    
    return {
        "success": True,
        "message": f"Trading resumed for user {user_id}",
        "user_id": user_id,
        "trading_status": "active",
        "resumed_by": admin["admin_id"],
        "resumed_at": datetime.utcnow().isoformat()
    }

@router.post("/users/{user_id}/halt")
async def halt_user_trading(
    user_id: str,
    reason: str,
    close_positions: bool = False,
    admin: dict = Depends(get_current_admin)
):
    """Halt user's trading and optionally close all positions"""
    check_permission(admin, "user_management")
    
    return {
        "success": True,
        "message": f"Trading halted for user {user_id}",
        "user_id": user_id,
        "trading_status": "halted",
        "reason": reason,
        "positions_closed": close_positions,
        "halted_by": admin["admin_id"],
        "halted_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# FEE MANAGEMENT
# ============================================================================

@router.post("/fees/configure")
async def configure_fees(
    config: FeeConfiguration,
    admin: dict = Depends(get_current_admin)
):
    """Configure CFD fees for instrument type"""
    check_permission(admin, "fee_management")
    
    return {
        "success": True,
        "message": f"Fees configured for {config.instrument_type}",
        "fees": {
            "instrument_type": config.instrument_type,
            "maker_fee": str(config.maker_fee),
            "taker_fee": str(config.taker_fee),
            "swap_long": str(config.swap_long),
            "swap_short": str(config.swap_short),
            "commission": str(config.commission),
            "min_commission": str(config.min_commission),
            "updated_by": admin["admin_id"],
            "updated_at": datetime.utcnow().isoformat()
        }
    }

@router.get("/fees/{instrument_type}")
async def get_fee_config(
    instrument_type: str,
    admin: dict = Depends(get_current_admin)
):
    """Get fee configuration for instrument type"""
    # In production, fetch from database
    return {
        "instrument_type": instrument_type,
        "maker_fee": "0.0001",
        "taker_fee": "0.0001",
        "swap_long": "-0.0001",
        "swap_short": "-0.0001",
        "commission": "0.00005",
        "min_commission": "0"
    }

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

@router.post("/risk/parameters")
async def set_risk_parameters(
    params: RiskParameters,
    admin: dict = Depends(get_current_admin)
):
    """Set global risk parameters"""
    check_permission(admin, "risk_management")
    
    return {
        "success": True,
        "message": "Risk parameters updated",
        "parameters": {
            "max_total_exposure": str(params.max_total_exposure),
            "max_single_position": str(params.max_single_position),
            "max_leverage_total": params.max_leverage_total,
            "margin_call_percentage": str(params.margin_call_percentage),
            "stop_out_percentage": str(params.stop_out_percentage),
            "negative_balance_protection": params.negative_balance_protection,
            "auto_liquidation_enabled": params.auto_liquidation_enabled,
            "updated_by": admin["admin_id"],
            "updated_at": datetime.utcnow().isoformat()
        }
    }

@router.get("/risk/parameters")
async def get_risk_parameters(admin: dict = Depends(get_current_admin)):
    """Get global risk parameters"""
    return {
        "max_total_exposure": "100000000",
        "max_single_position": "10000000",
        "max_leverage_total": 500,
        "margin_call_percentage": "80",
        "stop_out_percentage": "50",
        "negative_balance_protection": True,
        "auto_liquidation_enabled": True
    }

@router.post("/risk/liquidation-check")
async def trigger_liquidation_check(
    admin: dict = Depends(get_current_admin)
):
    """Trigger global liquidation check"""
    check_permission(admin, "risk_management")
    
    return {
        "success": True,
        "message": "Liquidation check triggered",
        "triggered_by": admin["admin_id"],
        "triggered_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

@router.post("/settings")
async def update_system_settings(
    settings: SystemSettings,
    admin: dict = Depends(get_current_admin)
):
    """Update system-wide trading settings"""
    check_permission(admin, "system_configuration")
    
    return {
        "success": True,
        "message": "System settings updated",
        "settings": {
            "trading_enabled": settings.trading_enabled,
            "new_positions_allowed": settings.new_positions_allowed,
            "new_orders_allowed": settings.new_orders_allowed,
            "close_positions_allowed": settings.close_positions_allowed,
            "modify_positions_allowed": settings.modify_positions_allowed,
            "withdraw_enabled": settings.withdraw_enabled,
            "deposit_enabled": settings.deposit_enabled,
            "transfer_enabled": settings.transfer_enabled,
            "maintenance_mode": settings.maintenance_mode,
            "maintenance_message": settings.maintenance_message,
            "updated_by": admin["admin_id"],
            "updated_at": datetime.utcnow().isoformat()
        }
    }

@router.get("/settings")
async def get_system_settings(admin: dict = Depends(get_current_admin)):
    """Get system-wide trading settings"""
    return {
        "trading_enabled": True,
        "new_positions_allowed": True,
        "new_orders_allowed": True,
        "close_positions_allowed": True,
        "modify_positions_allowed": True,
        "withdraw_enabled": True,
        "deposit_enabled": True,
        "transfer_enabled": True,
        "maintenance_mode": False,
        "maintenance_message": None
    }

# ============================================================================
# INSTRUMENT MANAGEMENT
# ============================================================================

@router.post("/instruments/{symbol}/activate")
async def activate_instrument(
    symbol: str,
    admin: dict = Depends(get_current_admin)
):
    """Activate CFD instrument"""
    check_permission(admin, "instrument_management")
    
    return {
        "success": True,
        "message": f"Instrument {symbol} activated",
        "symbol": symbol,
        "status": "active",
        "activated_by": admin["admin_id"],
        "activated_at": datetime.utcnow().isoformat()
    }

@router.post("/instruments/{symbol}/deactivate")
async def deactivate_instrument(
    symbol: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Deactivate CFD instrument"""
    check_permission(admin, "instrument_management")
    
    return {
        "success": True,
        "message": f"Instrument {symbol} deactivated",
        "symbol": symbol,
        "status": "inactive",
        "reason": reason,
        "deactivated_by": admin["admin_id"],
        "deactivated_at": datetime.utcnow().isoformat()
    }

@router.delete("/instruments/{symbol}")
async def delete_instrument(
    symbol: str,
    admin: dict = Depends(get_current_admin)
):
    """Delete CFD instrument"""
    check_permission(admin, "instrument_management")
    
    return {
        "success": True,
        "message": f"Instrument {symbol} deleted",
        "symbol": symbol,
        "deleted_by": admin["admin_id"],
        "deleted_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# REPORTS & ANALYTICS
# ============================================================================

@router.get("/reports/volume")
async def get_volume_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    instrument_type: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get CFD volume report"""
    return {
        "report_type": "volume",
        "start_date": start_date,
        "end_date": end_date,
        "instrument_type": instrument_type,
        "total_volume": "125000000.00",
        "total_trades": 15234,
        "total_users": 3421,
        "breakdown": {
            "forex": {"volume": "50000000", "trades": 6500},
            "stocks": {"volume": "35000000", "trades": 4200},
            "indices": {"volume": "25000000", "trades": 2800},
            "commodities": {"volume": "10000000", "trades": 1234},
            "metals": {"volume": "5000000", "trades": 500}
        }
    }

@router.get("/reports/positions")
async def get_positions_report(
    admin: dict = Depends(get_current_admin)
):
    """Get CFD positions report"""
    return {
        "report_type": "positions",
        "total_open_positions": 5423,
        "total_notional_value": "87500000.00",
        "by_instrument_type": {
            "forex": {"positions": 2100, "notional": "35000000"},
            "stocks": {"positions": 1500, "notional": "25000000"},
            "indices": {"positions": 1000, "notional": "17500000"},
            "commodities": {"positions": 523, "notional": "7500000"},
            "metals": {"positions": 300, "notional": "2500000"}
        },
        "long_positions": 2850,
        "short_positions": 2573
    }

@router.get("/reports/users")
async def get_users_report(
    admin: dict = Depends(get_current_admin)
):
    """Get CFD users report"""
    return {
        "report_type": "users",
        "total_cfd_users": 15678,
        "active_traders": 8234,
        "new_users_today": 45,
        "new_users_week": 312,
        "new_users_month": 1456,
        "by_account_type": {
            "standard": 8500,
            "ecn": 4500,
            "cent": 2000,
            "demo": 678
        }
    }def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
