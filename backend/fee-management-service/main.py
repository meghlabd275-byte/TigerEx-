"""
TigerEx Fee Management Service
Complete trading fees, withdrawal fees, and fee collection system
Port: 8180
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import jwt

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"

# Global connections
db_pool = None
redis_client = None

security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class FeeType(str, Enum):
    TRADING_MAKER = "trading_maker"
    TRADING_TAKER = "trading_taker"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    CONVERSION = "conversion"
    MARGIN_INTEREST = "margin_interest"
    FUNDING_RATE = "funding_rate"
    LIQUIDATION = "liquidation"
    P2P = "p2p"
    NFT_ROYALTY = "nft_royalty"

class FeeTier(str, Enum):
    REGULAR = "regular"
    VIP1 = "vip1"
    VIP2 = "vip2"
    VIP3 = "vip3"
    VIP4 = "vip4"
    VIP5 = "vip5"
    VIP_ELITE = "vip_elite"
    INSTITUTIONAL = "institutional"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_PROVIDER = "liquidity_provider"

class UserTier(str, Enum):
    REGULAR = "regular"
    VIP1 = "vip1"
    VIP2 = "vip2"
    VIP3 = "vip3"
    VIP4 = "vip4"
    VIP5 = "vip5"
    VIP_ELITE = "vip_elite"
    INSTITUTIONAL = "institutional"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_PROVIDER = "liquidity_provider"

class ExchangeStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HALTED = "halted"
    SUSPENDED = "suspended"
    DEMO = "demo"

class ExchangeMode(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    DEMO = "demo"

# ============================================================================
# MODELS
# ============================================================================

class FeeConfiguration(BaseModel):
    fee_type: FeeType
    asset: Optional[str] = None
    trading_pair: Optional[str] = None
    user_tier: UserTier
    base_fee: Decimal = Field(..., gt=0, le=1)
    min_fee: Decimal = Field(default=Decimal("0"), ge=0)
    max_fee: Optional[Decimal] = None
    fee_currency: str = "USDT"
    is_percentage: bool = True
    is_active: bool = True

class FeeTierConfig(BaseModel):
    tier_name: str
    min_volume_30d: Decimal = Decimal("0")
    min_balance: Decimal = Decimal("0")
    maker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    taker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    withdrawal_discount: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    deposit_discount: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    benefits: Dict[str, Any] = {}

class WithdrawalFeeConfig(BaseModel):
    asset: str
    network: str
    fee_amount: Decimal = Field(..., ge=0)
    min_fee: Decimal = Field(default=Decimal("0"), ge=0)
    max_fee: Optional[Decimal] = None
    is_dynamic: bool = False
    dynamic_multiplier: Decimal = Decimal("1.0")
    is_active: bool = True

class ExchangeConfig(BaseModel):
    exchange_id: str
    exchange_name: str
    exchange_status: ExchangeStatus
    exchange_mode: ExchangeMode
    white_label_enabled: bool = False
    parent_exchange_id: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    domain: Optional[str] = None
    
    # Features
    spot_enabled: bool = True
    futures_enabled: bool = True
    margin_enabled: bool = True
    options_enabled: bool = False
    p2p_enabled: bool = True
    nft_enabled: bool = True
    staking_enabled: bool = True
    launchpad_enabled: bool = True
    
    # Limits
    max_withdrawal_daily: Decimal = Decimal("100000")
    max_deposit_daily: Decimal = Decimal("1000000")
    max_leverage: int = 100
    
    # Fees
    default_maker_fee: Decimal = Decimal("0.001")
    default_taker_fee: Decimal = Decimal("0.001")
    
    # Settings
    kyc_required: bool = True
    kyc_level_required: int = 1
    two_factor_required: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FeeCollectionRecord(BaseModel):
    user_id: str
    fee_type: FeeType
    asset: str
    amount: Decimal
    trading_pair: Optional[str] = None
    order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    fee_rate: Decimal
    original_amount: Decimal
    collected_at: datetime = Field(default_factory=datetime.utcnow)

class UserFeeOverride(BaseModel):
    user_id: str
    fee_type: FeeType
    custom_rate: Decimal
    reason: str
    valid_until: Optional[datetime] = None
    created_by: str

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="TigerEx Fee Management Service",
    description="Complete fee management for trading, withdrawal, and deposits",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "technical_admin"]:
            raise HTTPException(status_code=401, detail="Invalid token")
        
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
# EXCHANGE CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/fees/exchange/config")
async def get_exchange_config(admin: dict = Depends(get_current_admin)):
    """Get current exchange configuration"""
    check_permission(admin, "view_config")
    
    # Get from cache or database
    config = await redis_client.get("exchange:config")
    if config:
        return json.loads(config)
    
    # Default config
    default_config = {
        "exchange_id": "TIGEREX_MAIN",
        "exchange_name": "TigerEx",
        "exchange_status": "active",
        "exchange_mode": "production",
        "white_label_enabled": False,
        "spot_enabled": True,
        "futures_enabled": True,
        "margin_enabled": True,
        "options_enabled": False,
        "p2p_enabled": True,
        "nft_enabled": True,
        "staking_enabled": True,
        "launchpad_enabled": True,
        "max_withdrawal_daily": "100000",
        "max_deposit_daily": "1000000",
        "max_leverage": 100,
        "default_maker_fee": "0.001",
        "default_taker_fee": "0.001",
        "kyc_required": True,
        "kyc_level_required": 1
    }
    
    return default_config

@app.post("/api/fees/exchange/config")
async def update_exchange_config(
    config: ExchangeConfig,
    admin: dict = Depends(get_current_admin)
):
    """Update exchange configuration (Super Admin only)"""
    check_permission(admin, "system_config")
    
    # Store in Redis cache
    await redis_client.set("exchange:config", config.json())
    await redis_client.set("exchange:config:updated_at", datetime.utcnow().isoformat())
    await redis_client.set("exchange:config:updated_by", admin["admin_id"])
    
    # Log audit
    await log_audit(admin["admin_id"], "update_exchange_config", details=config.dict())
    
    return {"success": True, "message": "Exchange configuration updated", "config": config}

@app.post("/api/fees/exchange/status")
async def set_exchange_status(
    status: ExchangeStatus,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Set exchange status (active, maintenance, halted, suspended)"""
    check_permission(admin, "system_config")
    
    await redis_client.set("exchange:status", status.value)
    await redis_client.set("exchange:status:reason", reason)
    await redis_client.set("exchange:status:updated_at", datetime.utcnow().isoformat())
    await redis_client.set("exchange:status:updated_by", admin["admin_id"])
    
    # Notify all services
    await redis_client.publish("exchange:status:changed", json.dumps({
        "status": status.value,
        "reason": reason,
        "updated_by": admin["admin_id"],
        "updated_at": datetime.utcnow().isoformat()
    }))
    
    await log_audit(admin["admin_id"], "set_exchange_status", details={
        "status": status.value,
        "reason": reason
    })
    
    return {"success": True, "status": status.value, "reason": reason}

@app.post("/api/fees/exchange/white-label")
async def configure_white_label(
    exchange_id: str,
    exchange_name: str,
    domain: str,
    logo_url: Optional[str] = None,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    parent_exchange_id: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Configure white-label exchange"""
    check_permission(admin, "system_config")
    
    white_label_config = {
        "exchange_id": exchange_id,
        "exchange_name": exchange_name,
        "domain": domain,
        "logo_url": logo_url,
        "primary_color": primary_color or "#1a1a2e",
        "secondary_color": secondary_color or "#16213e",
        "parent_exchange_id": parent_exchange_id or "TIGEREX_MAIN",
        "white_label_enabled": True,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": admin["admin_id"]
    }
    
    await redis_client.set(f"whitelabel:{exchange_id}:config", json.dumps(white_label_config))
    await redis_client.sadd("whitelabel:exchanges", exchange_id)
    
    await log_audit(admin["admin_id"], "configure_white_label", details=white_label_config)
    
    return {"success": True, "message": "White-label exchange configured", "config": white_label_config}

# ============================================================================
# FEE TIER MANAGEMENT
# ============================================================================

@app.get("/api/fees/tiers")
async def get_fee_tiers():
    """Get all fee tiers"""
    tiers = await redis_client.get("fee:tiers:config")
    if tiers:
        return json.loads(tiers)
    
    # Default fee tiers
    default_tiers = [
        {
            "tier": "regular",
            "name": "Regular",
            "min_volume_30d": "0",
            "maker_fee": "0.001",
            "taker_fee": "0.001",
            "withdrawal_discount": "0",
            "withdrawal_fee_discount": "0"
        },
        {
            "tier": "vip1",
            "name": "VIP 1",
            "min_volume_30d": "10000",
            "maker_fee": "0.0009",
            "taker_fee": "0.001",
            "withdrawal_discount": "0.05",
            "withdrawal_fee_discount": "0.05"
        },
        {
            "tier": "vip2",
            "name": "VIP 2",
            "min_volume_30d": "50000",
            "maker_fee": "0.0008",
            "taker_fee": "0.0009",
            "withdrawal_discount": "0.10",
            "withdrawal_fee_discount": "0.10"
        },
        {
            "tier": "vip3",
            "name": "VIP 3",
            "min_volume_30d": "100000",
            "maker_fee": "0.0006",
            "taker_fee": "0.0008",
            "withdrawal_discount": "0.15",
            "withdrawal_fee_discount": "0.15"
        },
        {
            "tier": "vip4",
            "name": "VIP 4",
            "min_volume_30d": "500000",
            "maker_fee": "0.0004",
            "taker_fee": "0.0006",
            "withdrawal_discount": "0.20",
            "withdrawal_fee_discount": "0.20"
        },
        {
            "tier": "vip5",
            "name": "VIP 5",
            "min_volume_30d": "1000000",
            "maker_fee": "0.0002",
            "taker_fee": "0.0004",
            "withdrawal_discount": "0.25",
            "withdrawal_fee_discount": "0.25"
        },
        {
            "tier": "vip_elite",
            "name": "VIP Elite",
            "min_volume_30d": "5000000",
            "maker_fee": "0.0001",
            "taker_fee": "0.0002",
            "withdrawal_discount": "0.30",
            "withdrawal_fee_discount": "0.30"
        },
        {
            "tier": "institutional",
            "name": "Institutional",
            "min_volume_30d": "10000000",
            "maker_fee": "0.00005",
            "taker_fee": "0.0001",
            "withdrawal_discount": "0.40",
            "withdrawal_fee_discount": "0.40"
        },
        {
            "tier": "market_maker",
            "name": "Market Maker",
            "min_volume_30d": "50000000",
            "maker_fee": "0.00002",
            "taker_fee": "0.00005",
            "withdrawal_discount": "0.50",
            "withdrawal_fee_discount": "0.50"
        },
        {
            "tier": "liquidity_provider",
            "name": "Liquidity Provider",
            "min_volume_30d": "100000000",
            "maker_fee": "0.00001",
            "taker_fee": "0.00002",
            "withdrawal_discount": "0.60",
            "withdrawal_fee_discount": "0.60"
        }
    ]
    
    await redis_client.set("fee:tiers:config", json.dumps(default_tiers))
    return default_tiers

@app.post("/api/fees/tiers")
async def update_fee_tier(
    tier_config: FeeTierConfig,
    admin: dict = Depends(get_current_admin)
):
    """Update fee tier configuration"""
    check_permission(admin, "manage_fees")
    
    # Get existing tiers
    tiers = await get_fee_tiers()
    
    # Update or add tier
    tier_found = False
    for i, tier in enumerate(tiers):
        if tier["tier"] == tier_config.tier_name.lower():
            tiers[i] = {
                "tier": tier_config.tier_name.lower(),
                "name": tier_config.tier_name,
                "min_volume_30d": str(tier_config.min_volume_30d),
                "maker_fee": str(tier_config.maker_fee),
                "taker_fee": str(tier_config.taker_fee),
                "withdrawal_discount": str(tier_config.withdrawal_discount),
                "withdrawal_fee_discount": str(tier_config.deposit_discount)
            }
            tier_found = True
            break
    
    if not tier_found:
        tiers.append({
            "tier": tier_config.tier_name.lower(),
            "name": tier_config.tier_name,
            "min_volume_30d": str(tier_config.min_volume_30d),
            "maker_fee": str(tier_config.maker_fee),
            "taker_fee": str(tier_config.taker_fee),
            "withdrawal_discount": str(tier_config.withdrawal_discount),
            "withdrawal_fee_discount": str(tier_config.deposit_discount)
        })
    
    await redis_client.set("fee:tiers:config", json.dumps(tiers))
    
    await log_audit(admin["admin_id"], "update_fee_tier", details=tier_config.dict())
    
    return {"success": True, "message": "Fee tier updated", "tiers": tiers}

# ============================================================================
# WITHDRAWAL FEE MANAGEMENT
# ============================================================================

@app.get("/api/fees/withdrawal")
async def get_withdrawal_fees():
    """Get all withdrawal fees"""
    fees = await redis_client.get("fees:withdrawal:config")
    if fees:
        return json.loads(fees)
    
    # Default withdrawal fees
    default_fees = [
        {"asset": "BTC", "network": "BTC", "fee": "0.0005", "min_fee": "0.0001", "max_fee": "0.01"},
        {"asset": "ETH", "network": "ETH", "fee": "0.005", "min_fee": "0.001", "max_fee": "0.1"},
        {"asset": "USDT", "network": "ERC20", "fee": "5", "min_fee": "1", "max_fee": "100"},
        {"asset": "USDT", "network": "TRC20", "fee": "1", "min_fee": "0.5", "max_fee": "10"},
        {"asset": "USDT", "network": "BEP20", "fee": "0.8", "min_fee": "0.5", "max_fee": "10"},
        {"asset": "BNB", "network": "BEP20", "fee": "0.0005", "min_fee": "0.0001", "max_fee": "0.01"},
        {"asset": "SOL", "network": "SOL", "fee": "0.01", "min_fee": "0.005", "max_fee": "0.5"},
        {"asset": "XRP", "network": "XRP", "fee": "0.25", "min_fee": "0.1", "max_fee": "5"},
        {"asset": "ADA", "network": "ADA", "fee": "1", "min_fee": "0.5", "max_fee": "10"},
        {"asset": "DOGE", "network": "DOGE", "fee": "5", "min_fee": "2", "max_fee": "50"}
    ]
    
    await redis_client.set("fees:withdrawal:config", json.dumps(default_fees))
    return default_fees

@app.post("/api/fees/withdrawal")
async def set_withdrawal_fee(
    config: WithdrawalFeeConfig,
    admin: dict = Depends(get_current_admin)
):
    """Set withdrawal fee for asset/network"""
    check_permission(admin, "manage_fees")
    
    fees = await get_withdrawal_fees()
    
    # Update or add fee
    fee_found = False
    for i, fee in enumerate(fees):
        if fee["asset"] == config.asset and fee["network"] == config.network:
            fees[i] = {
                "asset": config.asset,
                "network": config.network,
                "fee": str(config.fee_amount),
                "min_fee": str(config.min_fee),
                "max_fee": str(config.max_fee) if config.max_fee else None,
                "is_dynamic": config.is_dynamic,
                "dynamic_multiplier": str(config.dynamic_multiplier),
                "is_active": config.is_active
            }
            fee_found = True
            break
    
    if not fee_found:
        fees.append({
            "asset": config.asset,
            "network": config.network,
            "fee": str(config.fee_amount),
            "min_fee": str(config.min_fee),
            "max_fee": str(config.max_fee) if config.max_fee else None,
            "is_dynamic": config.is_dynamic,
            "dynamic_multiplier": str(config.dynamic_multiplier),
            "is_active": config.is_active
        })
    
    await redis_client.set("fees:withdrawal:config", json.dumps(fees))
    
    await log_audit(admin["admin_id"], "set_withdrawal_fee", details=config.dict())
    
    return {"success": True, "message": "Withdrawal fee updated", "fees": fees}

@app.post("/api/fees/withdrawal/calculate")
async def calculate_withdrawal_fee(
    asset: str,
    network: str,
    amount: Decimal,
    user_id: str
):
    """Calculate withdrawal fee for a user"""
    # Get user tier
    user_tier = await get_user_tier(user_id)
    
    # Get withdrawal fees
    fees = await get_withdrawal_fees()
    
    base_fee = None
    for fee in fees:
        if fee["asset"] == asset and fee["network"] == network:
            base_fee = Decimal(fee["fee"])
            break
    
    if base_fee is None:
        raise HTTPException(status_code=400, detail="Fee configuration not found")
    
    # Get tier discount
    tiers = await get_fee_tiers()
    discount = Decimal("0")
    for tier in tiers:
        if tier["tier"] == user_tier:
            discount = Decimal(tier.get("withdrawal_fee_discount", "0"))
            break
    
    # Calculate final fee
    final_fee = base_fee * (1 - discount)
    final_fee = max(final_fee, Decimal("0"))
    
    return {
        "asset": asset,
        "network": network,
        "amount": str(amount),
        "base_fee": str(base_fee),
        "discount_percent": str(discount * 100),
        "final_fee": str(final_fee),
        "user_tier": user_tier,
        "net_amount": str(amount - final_fee)
    }

# ============================================================================
# TRADING FEE CALCULATION
# ============================================================================

@app.post("/api/fees/trading/calculate")
async def calculate_trading_fee(
    trading_pair: str,
    side: str,
    amount: Decimal,
    price: Decimal,
    user_id: str,
    order_type: str = "limit"
):
    """Calculate trading fee for an order"""
    # Get user tier
    user_tier = await get_user_tier(user_id)
    
    # Get fee tiers
    tiers = await get_fee_tiers()
    
    maker_fee = Decimal("0.001")
    taker_fee = Decimal("0.001")
    
    for tier in tiers:
        if tier["tier"] == user_tier:
            maker_fee = Decimal(tier["maker_fee"])
            taker_fee = Decimal(tier["taker_fee"])
            break
    
    # Determine if maker or taker
    is_maker = order_type == "limit"
    fee_rate = maker_fee if is_maker else taker_fee
    
    # Calculate fee
    order_value = amount * price
    fee_amount = order_value * fee_rate
    
    return {
        "trading_pair": trading_pair,
        "side": side,
        "amount": str(amount),
        "price": str(price),
        "order_value": str(order_value),
        "order_type": order_type,
        "is_maker": is_maker,
        "fee_rate": str(fee_rate),
        "fee_amount": str(fee_amount),
        "user_tier": user_tier,
        "fee_currency": trading_pair.replace("USDT", "").replace("BUSD", "") + "USDT" if "USDT" in trading_pair or "BUSD" in trading_pair else trading_pair.split("/")[1] if "/" in trading_pair else "USDT"
    }

# ============================================================================
# FEE COLLECTION
# ============================================================================

@app.post("/api/fees/collect")
async def collect_fee(
    record: FeeCollectionRecord,
    background_tasks: BackgroundTasks,
    admin: dict = Depends(get_current_admin)
):
    """Record a fee collection"""
    check_permission(admin, "manage_fees")
    
    # Store in database
    fee_record = {
        "id": os.urandom(16).hex(),
        "user_id": record.user_id,
        "fee_type": record.fee_type.value,
        "asset": record.asset,
        "amount": str(record.amount),
        "trading_pair": record.trading_pair,
        "order_id": record.order_id,
        "transaction_id": record.transaction_id,
        "fee_rate": str(record.fee_rate),
        "original_amount": str(record.original_amount),
        "collected_at": record.collected_at.isoformat()
    }
    
    # Add to fee collection list
    await redis_client.lpush("fees:collected:recent", json.dumps(fee_record))
    await redis_client.ltrim("fees:collected:recent", 0, 9999)  # Keep last 10000
    
    # Update daily totals
    today = datetime.utcnow().strftime("%Y-%m-%d")
    await redis_client.incrbyfloat(f"fees:daily:{today}:total", float(record.amount))
    await redis_client.incrbyfloat(f"fees:daily:{today}:{record.fee_type.value}", float(record.amount))
    await redis_client.incrbyfloat(f"fees:user:{record.user_id}:total", float(record.amount))
    
    return {"success": True, "record": fee_record}

@app.get("/api/fees/collected/stats")
async def get_fee_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get fee collection statistics"""
    check_permission(admin, "view_financials")
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Get daily totals
    daily_total = await redis_client.get(f"fees:daily:{today}:total") or "0"
    
    # Get fee breakdown by type
    fee_types = ["trading_maker", "trading_taker", "withdrawal", "deposit", "transfer", "margin_interest"]
    breakdown = {}
    for fee_type in fee_types:
        amount = await redis_client.get(f"fees:daily:{today}:{fee_type}") or "0"
        breakdown[fee_type] = amount
    
    # Get recent collections
    recent = await redis_client.lrange("fees:collected:recent", 0, 9)
    recent_fees = [json.loads(r) for r in recent]
    
    return {
        "date": today,
        "daily_total": daily_total,
        "breakdown": breakdown,
        "recent_collections": recent_fees
    }

# ============================================================================
# USER FEE OVERRIDES
# ============================================================================

@app.post("/api/fees/user/override")
async def set_user_fee_override(
    override: UserFeeOverride,
    admin: dict = Depends(get_current_admin)
):
    """Set custom fee rate for a user"""
    check_permission(admin, "manage_fees")
    
    override_data = {
        "user_id": override.user_id,
        "fee_type": override.fee_type.value,
        "custom_rate": str(override.custom_rate),
        "reason": override.reason,
        "valid_until": override.valid_until.isoformat() if override.valid_until else None,
        "created_by": override.created_by,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await redis_client.set(
        f"fees:override:{override.user_id}:{override.fee_type.value}",
        json.dumps(override_data)
    )
    
    await log_audit(admin["admin_id"], "set_user_fee_override", details=override_data)
    
    return {"success": True, "message": "Fee override set", "override": override_data}

@app.delete("/api/fees/user/override")
async def remove_user_fee_override(
    user_id: str,
    fee_type: FeeType,
    admin: dict = Depends(get_current_admin)
):
    """Remove custom fee rate for a user"""
    check_permission(admin, "manage_fees")
    
    await redis_client.delete(f"fees:override:{user_id}:{fee_type.value}")
    
    await log_audit(admin["admin_id"], "remove_user_fee_override", details={
        "user_id": user_id,
        "fee_type": fee_type.value
    })
    
    return {"success": True, "message": "Fee override removed"}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_user_tier(user_id: str) -> str:
    """Get user's fee tier based on 30-day volume"""
    tier = await redis_client.get(f"user:{user_id}:tier")
    if tier:
        return tier
    
    # Calculate based on volume
    volume = await redis_client.get(f"user:{user_id}:volume:30d")
    volume = Decimal(volume or "0")
    
    tiers = await get_fee_tiers()
    current_tier = "regular"
    
    for tier_config in sorted(tiers, key=lambda x: Decimal(x["min_volume_30d"]), reverse=True):
        if volume >= Decimal(tier_config["min_volume_30d"]):
            current_tier = tier_config["tier"]
            break
    
    await redis_client.set(f"user:{user_id}:tier", current_tier)
    return current_tier

async def log_audit(admin_id: str, action: str, details: dict = None):
    """Log admin action for audit"""
    await redis_client.lpush("admin:audit:log", json.dumps({
        "admin_id": admin_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fee-management-service",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "service": "TigerEx Fee Management Service",
        "version": "2.0.0",
        "endpoints": {
            "exchange_config": "/api/fees/exchange/config",
            "fee_tiers": "/api/fees/tiers",
            "withdrawal_fees": "/api/fees/withdrawal",
            "trading_fees": "/api/fees/trading/calculate",
            "fee_collection": "/api/fees/collect",
            "fee_stats": "/api/fees/collected/stats"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8180)