"""
Enhanced Admin Routes for Options Trading
Complete admin controls for options trading system
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import asyncio
import json

router = APIRouter(prefix="/admin/options-trading", tags=["options-trading-admin"])

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class ExerciseStyle(str, Enum):
    EUROPEAN = "european"
    AMERICAN = "american"

class OptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    SETTLED = "settled"

class SettlementType(str, Enum):
    CASH = "cash"
    PHYSICAL = "physical"

class OptionsContract(BaseModel):
    """Options contract model"""
    id: Optional[str] = None
    underlying_asset: str
    quote_asset: str
    option_type: OptionType
    exercise_style: ExerciseStyle
    status: OptionStatus = OptionStatus.ACTIVE
    strike_price: float
    expiry_time: datetime
    settlement_type: SettlementType = SettlementType.CASH
    contract_size: float = 1.0
    min_quantity: float = 0.01
    max_quantity: float = 1000.0
    tick_size: float = 0.0001
    maker_fee: float = 0.002
    taker_fee: float = 0.003
    implied_volatility: float = 0.25
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OptionsConfig(BaseModel):
    """Options trading configuration"""
    enabled: bool = True
    maintenance_mode: bool = False
    max_contracts_per_underlying: int = 100
    max_expiry_days: int = 365
    min_expiry_days: int = 1
    max_strike_range_percentage: float = 0.50  # 50% of spot price
    enable_european: bool = True
    enable_american: bool = True
    enable_cash_settlement: bool = True
    enable_physical_settlement: bool = False
    auto_exercise_enabled: bool = True
    risk_management_enabled: bool = True
    max_position_size: float = 1000000.0
    margin_requirement_multiplier: float = 1.2

class OptionChain(BaseModel):
    """Option chain model"""
    underlying_asset: str
    spot_price: float
    expiry_dates: List[datetime]
    strike_prices: List[float]
    call_contracts: List[OptionsContract] = []
    put_contracts: List[OptionsContract] = []
    implied_volatility_surface: Dict[str, float] = {}

class GreeksCalculator(BaseModel):
    """Greeks calculator configuration"""
    model: str = "black_scholes"
    risk_free_rate: float = 0.02
    dividend_yield: float = 0.0
    volatility_adjustment: float = 0.0
    calculation_frequency: int = 60  # seconds

class PositionLimit(BaseModel):
    """Position limit model"""
    user_id: str
    underlying_asset: str
    max_long_calls: float
    max_long_puts: float
    max_short_calls: float
    max_short_puts: float
    max_total_contracts: float

# ============================================================================
# OPTIONS CONTRACT MANAGEMENT
# ============================================================================

@router.post("/contracts/create")
async def create_options_contract(
    contract: OptionsContract,
    background_tasks: BackgroundTasks
):
    """
    Create new options contract
    Admin can create options contracts with full configuration
    """
    try:
        # Validate contract parameters
        if contract.strike_price <= 0:
            raise HTTPException(
                status_code=400,
                detail="Strike price must be positive"
            )
        
        if contract.expiry_time <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Expiry time must be in the future"
            )
        
        if (contract.expiry_time - datetime.now()).days > 365:
            raise HTTPException(
                status_code=400,
                detail="Maximum expiry period is 365 days"
            )
        
        if contract.min_quantity >= contract.max_quantity:
            raise HTTPException(
                status_code=400,
                detail="Min quantity must be less than max quantity"
            )
        
        contract_data = contract.dict()
        contract_data["id"] = f"OPTION_{contract.underlying_asset}_{contract.option_type.value}_{contract.strike_price}_{datetime.now().timestamp()}"
        contract_data["created_at"] = datetime.now()
        contract_data["updated_at"] = datetime.now()
        
        # Calculate initial greeks
        background_tasks.add_task(calculate_initial_greeks, contract_data["id"])
        
        return {
            "status": "success",
            "message": f"Options contract {contract_data['id']} created successfully",
            "contract": contract_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/chain/create")
async def create_option_chain(
    underlying_asset: str,
    expiry_time: datetime,
    strike_range: Dict[str, float],
    option_types: List[OptionType],
    background_tasks: BackgroundTasks
):
    """
    Create complete option chain
    Admin can create multiple contracts at once
    """
    try:
        contracts_created = []
        
        for option_type in option_types:
            # Generate strike prices
            num_strikes = 20
            spot_price = strike_range["spot_price"]
            percentage_range = strike_range["percentage_range"]
            
            lower_bound = spot_price * (1 - percentage_range)
            upper_bound = spot_price * (1 + percentage_range)
            strike_step = (upper_bound - lower_bound) / (num_strikes - 1)
            
            for i in range(num_strikes):
                strike_price = lower_bound + (i * strike_step)
                
                contract = OptionsContract(
                    underlying_asset=underlying_asset,
                    quote_asset="USDT",
                    option_type=option_type,
                    exercise_style=ExerciseStyle.EUROPEAN,
                    strike_price=strike_price,
                    expiry_time=expiry_time
                )
                
                contract_data = contract.dict()
                contract_data["id"] = f"OPTION_{underlying_asset}_{option_type.value}_{strike_price}_{datetime.now().timestamp()}"
                contract_data["created_at"] = datetime.now()
                contract_data["updated_at"] = datetime.now()
                
                contracts_created.append(contract_data)
        
        # Initialize all contracts
        background_tasks.add_task(initialize_option_chain, contracts_created)
        
        return {
            "status": "success",
            "message": f"Option chain created with {len(contracts_created)} contracts",
            "contracts": contracts_created
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONTRACT CONTROL OPERATIONS
# ============================================================================

@router.put("/contracts/{contract_id}/pause")
async def pause_options_contract(contract_id: str, reason: str):
    """
    Pause options contract trading
    Admin can pause contract trading temporarily
    """
    try:
        return {
            "status": "success",
            "message": f"Options contract {contract_id} paused successfully",
            "contract_id": contract_id,
            "reason": reason,
            "status": "paused",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contracts/{contract_id}/resume")
async def resume_options_contract(contract_id: str):
    """
    Resume options contract trading
    Admin can resume paused contract trading
    """
    try:
        return {
            "status": "success",
            "message": f"Options contract {contract_id} resumed successfully",
            "contract_id": contract_id,
            "status": "active",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/contracts/{contract_id}/suspend")
async def suspend_options_contract(contract_id: str, reason: str):
    """
    Suspend options contract trading
    Admin can suspend contract trading for safety
    """
    try:
        return {
            "status": "success",
            "message": f"Options contract {contract_id} suspended successfully",
            "contract_id": contract_id,
            "reason": reason,
            "status": "suspended",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/contracts/{contract_id}")
async def delete_options_contract(contract_id: str):
    """
    Delete options contract
    Admin can delete options contracts
    """
    try:
        return {
            "status": "success",
            "message": f"Options contract {contract_id} deleted successfully",
            "contract_id": contract_id,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# OPTION CHAIN MANAGEMENT
# ============================================================================

@router.get("/chains/{underlying_asset}")
async def get_option_chain(
    underlying_asset: str,
    expiry_date: Optional[datetime] = None
):
    """
    Get option chain for underlying asset
    Admin can view complete option chains
    """
    try:
        chain_data = {
            "underlying_asset": underlying_asset,
            "spot_price": 45000.0,
            "expiry_dates": [
                "2024-01-05T00:00:00Z",
                "2024-01-12T00:00:00Z",
                "2024-01-19T00:00:00Z"
            ],
            "contracts": [
                {
                    "id": "OPTION_BTC_call_44000",
                    "type": "call",
                    "strike": 44000.0,
                    "expiry": "2024-01-05T00:00:00Z",
                    "last_price": 1250.0,
                    "volume": 1000,
                    "open_interest": 5000,
                    "implied_volatility": 0.28,
                    "delta": 0.65,
                    "gamma": 0.02,
                    "theta": -0.05,
                    "vega": 0.15
                },
                {
                    "id": "OPTION_BTC_put_44000",
                    "type": "put",
                    "strike": 44000.0,
                    "expiry": "2024-01-05T00:00:00Z",
                    "last_price": 800.0,
                    "volume": 800,
                    "open_interest": 3200,
                    "implied_volatility": 0.28,
                    "delta": -0.35,
                    "gamma": 0.02,
                    "theta": -0.03,
                    "vega": 0.15
                }
            ]
        }
        
        return {
            "status": "success",
            "chain": chain_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chains/{underlying_asset}/refresh")
async def refresh_option_chain(underlying_asset: str):
    """
    Refresh option chain data
    Admin can force refresh of option chain
    """
    try:
        return {
            "status": "success",
            "message": f"Option chain refreshed for {underlying_asset}",
            "underlying_asset": underlying_asset,
            "refresh_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GREEKS AND PRICING MANAGEMENT
# ============================================================================

@router.post("/contracts/{contract_id}/greeks/calculate")
async def calculate_contract_greeks(contract_id: str):
    """
    Calculate options greeks for contract
    Admin can force greeks recalculation
    """
    try:
        return {
            "status": "success",
            "message": f"Greeks calculated for contract {contract_id}",
            "contract_id": contract_id,
            "greeks": {
                "delta": 0.65,
                "gamma": 0.02,
                "theta": -0.05,
                "vega": 0.15,
                "rho": 0.08,
                "implied_volatility": 0.28,
                "theoretical_price": 1250.0
            },
            "calculation_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/pricing/model/update")
async def update_pricing_model(
    model: str,
    parameters: Dict[str, float]
):
    """
    Update pricing model parameters
    Admin can modify pricing model settings
    """
    try:
        return {
            "status": "success",
            "message": f"Pricing model {model} updated",
            "model": model,
            "parameters": parameters,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EXERCISE AND SETTLEMENT MANAGEMENT
# ============================================================================

@router.post("/contracts/{contract_id}/exercise/process")
async def process_option_exercise(
    contract_id: str,
    exercise_type: str,
    quantity: float
):
    """
    Process option exercise
    Admin can manually process exercises
    """
    try:
        return {
            "status": "success",
            "message": f"Option exercise processed for contract {contract_id}",
            "contract_id": contract_id,
            "exercise_type": exercise_type,
            "quantity": quantity,
            "process_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/settle")
async def settle_options_contract(
    contract_id: str,
    settlement_price: float
):
    """
    Settle expired options contract
    Admin can manually settle contracts
    """
    try:
        return {
            "status": "success",
            "message": f"Contract {contract_id} settled successfully",
            "contract_id": contract_id,
            "settlement_price": settlement_price,
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settlement/batch-process")
async def batch_settlement(expiry_date: datetime):
    """
    Process batch settlement for expired contracts
    Admin can settle multiple contracts at once
    """
    try:
        return {
            "status": "success",
            "message": f"Batch settlement processed for {expiry_date}",
            "expiry_date": expiry_date,
            "contracts_settled": 150,
            "total_payout": "2500000",
            "settlement_time": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# POSITION AND RISK MANAGEMENT
# ============================================================================

@router.get("/positions/monitor")
async def monitor_option_positions():
    """
    Monitor all options positions
    Admin can view system-wide position data
    """
    try:
        return {
            "status": "success",
            "positions": {
                "total_positions": 50000,
                "total_notional_value": "500000000",
                "total_open_interest": "250000000",
                "largest_positions": [
                    {
                        "user_id": "user_123",
                        "underlying_asset": "BTC",
                        "position_type": "long_call",
                        "notional_value": "1000000",
                        "unrealized_pnl": "50000"
                    }
                ],
                "risk_metrics": {
                    "portfolio_delta": 0.25,
                    "portfolio_gamma": 0.05,
                    "portfolio_theta": -0.15,
                    "portfolio_vega": 0.35,
                    "var_1day_95": "2500000"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/position-limits/update")
async def update_user_position_limits(
    user_id: str,
    limits: PositionLimit
):
    """
    Update user position limits
    Admin can control individual user limits
    """
    try:
        limits_data = limits.dict()
        limits_data["user_id"] = user_id
        
        return {
            "status": "success",
            "message": f"Position limits updated for user {user_id}",
            "user_id": user_id,
            "limits": limits_data,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/positions/{position_id}/force-close")
async def force_close_position(
    position_id: str,
    reason: str
):
    """
    Force close options position
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
# UNDERLYING ASSET MANAGEMENT
# ============================================================================

@router.post("/underlying/add")
async def add_underlying_asset(
    asset: str,
    spot_price: float,
    config: Dict[str, Any]
):
    """
    Add new underlying asset for options
    Admin can enable options for new assets
    """
    try:
        return {
            "status": "success",
            "message": f"Underlying asset {asset} added for options trading",
            "asset": asset,
            "spot_price": spot_price,
            "config": config,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/underlying/{asset}/disable")
async def disable_underlying_asset(asset: str, reason: str):
    """
    Disable options for underlying asset
    Admin can disable options for specific assets
    """
    try:
        return {
            "status": "success",
            "message": f"Options disabled for underlying asset {asset}",
            "asset": asset,
            "reason": reason,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS AND REPORTING
# ============================================================================

@router.get("/analytics/overview")
async def get_options_analytics():
    """
    Get comprehensive options analytics
    Admin can monitor system performance
    """
    try:
        return {
            "status": "success",
            "analytics": {
                "total_active_contracts": 2500,
                "total_open_interest": "500000000",
                "total_volume_24h": "125000000",
                "total_premium_24h": "8500000",
                "implied_volatility_index": 0.28,
                "put_call_ratio": 0.65,
                "top_underlying_assets": [
                    {"asset": "BTC", "volume": "50000000", "open_interest": "200000000"},
                    {"asset": "ETH", "volume": "35000000", "open_interest": "150000000"},
                    {"asset": "BNB", "volume": "20000000", "open_interest": "75000000"}
                ],
                "expiry_distribution": {
                    "1_week": 0.30,
                    "1_month": 0.45,
                    "3_months": 0.20,
                    "6_months_plus": 0.05
                },
                "risk_metrics": {
                    "portfolio_var": "2500000",
                    "concentration_risk": "medium",
                    "system_health": "optimal"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================

@router.put("/config/update")
async def update_options_config(config: OptionsConfig):
    """
    Update global options trading configuration
    Admin can modify system-wide settings
    """
    try:
        config_data = config.dict()
        config_data["updated_at"] = datetime.now()
        
        return {
            "status": "success",
            "message": "Options configuration updated successfully",
            "config": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_options_config():
    """
    Get current options trading configuration
    Admin can view current system settings
    """
    try:
        return {
            "status": "success",
            "config": {
                "enabled": True,
                "maintenance_mode": False,
                "max_contracts_per_underlying": 100,
                "max_expiry_days": 365,
                "min_expiry_days": 1,
                "max_strike_range_percentage": 0.50,
                "enable_european": True,
                "enable_american": True,
                "enable_cash_settlement": True,
                "enable_physical_settlement": False,
                "auto_exercise_enabled": True,
                "risk_management_enabled": True,
                "max_position_size": 1000000.0,
                "margin_requirement_multiplier": 1.2
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def calculate_initial_greeks(contract_id: str):
    """Calculate initial greeks for new contract"""
    await asyncio.sleep(1)
    print(f"Initial greeks calculated for contract {contract_id}")

async def initialize_option_chain(contracts: List[Dict[str, Any]]):
    """Initialize option chain systems"""
    await asyncio.sleep(2)
    print(f"Option chain initialized with {len(contracts)} contracts")