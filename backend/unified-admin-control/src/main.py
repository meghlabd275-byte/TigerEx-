"""
TigerEx Unified Admin Control Panel
Complete admin control over all services with role-based access
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator, EmailStr
import jwt
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TigerEx Unified Admin Control",
    description="Complete admin control over all services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/tigerex")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-secret-key")
    JWT_ALGORITHM = "HS256"

config = Config()
security = HTTPBearer()


# Enums
class ServiceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class ActionType(str, Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    HALT = "halt"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Models
@dataclass
class ServiceInfo:
    name: str
    status: ServiceStatus
    health: float
    cpu_usage: float
    memory_usage: float
    requests_per_second: float
    error_rate: float
    last_check: datetime


@dataclass
class SystemAlert:
    id: str
    service: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    acknowledged: bool
    resolved: bool


# Request/Response Models
class ServiceActionRequest(BaseModel):
    service_name: str
    action: ActionType
    reason: Optional[str] = None


class UserActionRequest(BaseModel):
    user_id: str
    action: str
    reason: Optional[str] = None
    duration: Optional[int] = None  # in hours


class TradingPairActionRequest(BaseModel):
    symbol: str
    action: str  # pause, resume, halt, delist
    reason: Optional[str] = None


class WithdrawalActionRequest(BaseModel):
    withdrawal_id: str
    action: str  # approve, reject, hold
    reason: Optional[str] = None


class FeeUpdateRequest(BaseModel):
    pair_symbol: str
    maker_fee: float
    taker_fee: float
    reason: str


class SystemConfigRequest(BaseModel):
    config_key: str
    config_value: str
    reason: str


class SocialAuthRequest(BaseModel):
    provider: str
    provider_user_id: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class TradingPairCreateRequest(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    market_type: str = "spot"  # spot, futures, options, etf, derivatives
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    max_leverage: int = 1


class TradingPairImportRequest(BaseModel):
    source_exchange: str
    symbol: str
    market_type: str = "spot"


class LiquidityPoolRequest(BaseModel):
    pool_name: str
    symbol: str
    liquidity_amount: float
    source_exchange: Optional[str] = None


class ExchangeStatusRequest(BaseModel):
    exchange_id: str
    status: str
    reason: Optional[str] = None


# Admin Control Manager
class UnifiedAdminControl:
    """Complete admin control over all exchange services"""
    
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.services: Dict[str, ServiceInfo] = {}
        self.alerts: List[SystemAlert] = []
        self.trading_pairs: Dict[str, dict] = {}
        self.liquidity_pools: Dict[str, dict] = {}
        self.exchange_statuses: Dict[str, dict] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize connections and services"""
        try:
            self.redis_client = await aioredis.from_url(
                config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
        try:
            self.db_pool = await asyncpg.create_pool(config.DATABASE_URL)
            logger.info("Database pool created")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
        
        # Initialize services
        await self._initialize_services()
        self._initialized = True
    
    async def _initialize_services(self):
        """Initialize all service monitors"""
        service_names = [
            "auth-service", "trading-engine", "wallet-service", "order-service",
            "market-data-service", "user-service", "kyc-service", "notification-service",
            "api-gateway", "matching-engine", "settlement-service", "risk-engine",
            "compliance-service", "liquidity-service", "affiliate-service",
            "support-service", "admin-service", "analytics-service", "blockchain-service",
            "deposit-service", "withdrawal-service", "p2p-service", "nft-service",
            "futures-service", "margin-service", "copy-trading-service", "bot-trading-service"
        ]
        
        for name in service_names:
            self.services[name] = ServiceInfo(
                name=name,
                status=ServiceStatus.RUNNING,
                health=100.0,
                cpu_usage=0.0,
                memory_usage=0.0,
                requests_per_second=0.0,
                error_rate=0.0,
                last_check=datetime.utcnow()
            )

        # Seed default market metadata used by admin controls
        self.trading_pairs.update({
            "BTC-USDT": {"symbol": "BTC-USDT", "market_type": "spot", "status": "active", "maker_fee": 0.001, "taker_fee": 0.001, "source": "tigerex"},
            "ETH-USDT": {"symbol": "ETH-USDT", "market_type": "spot", "status": "active", "maker_fee": 0.001, "taker_fee": 0.001, "source": "tigerex"},
        })
    
    async def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get status of a specific service"""
        return self.services.get(service_name)
    
    async def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get status of all services"""
        return self.services
    
    async def control_service(self, service_name: str, action: ActionType, reason: str = None) -> bool:
        """Control a service (start, stop, pause, resume, halt)"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        
        if action == ActionType.START:
            service.status = ServiceStatus.RUNNING
        elif action == ActionType.STOP:
            service.status = ServiceStatus.STOPPED
        elif action == ActionType.PAUSE:
            service.status = ServiceStatus.PAUSED
        elif action == ActionType.RESUME:
            service.status = ServiceStatus.RUNNING
        elif action == ActionType.RESTART:
            service.status = ServiceStatus.RUNNING
        elif action == ActionType.HALT:
            service.status = ServiceStatus.STOPPED
        
        # Log action
        await self._log_admin_action(
            action=f"service_{action.value}",
            target=service_name,
            reason=reason
        )
        
        return True
    
    async def halt_all_trading(self, reason: str) -> bool:
        """Emergency halt all trading"""
        trading_services = ["trading-engine", "matching-engine", "order-service", 
                          "futures-service", "margin-service"]
        
        for service_name in trading_services:
            await self.control_service(service_name, ActionType.HALT, reason)
        
        # Set global halt flag
        if self.redis_client:
            await self.redis_client.set("global:trading_halt", "true")
            await self.redis_client.set("global:halt_reason", reason)
            await self.redis_client.set("global:halt_time", datetime.utcnow().isoformat())
        
        await self._log_admin_action(
            action="emergency_halt_all_trading",
            target="all_trading_services",
            reason=reason
        )
        
        return True
    
    async def resume_all_trading(self, reason: str) -> bool:
        """Resume all trading after halt"""
        trading_services = ["trading-engine", "matching-engine", "order-service",
                          "futures-service", "margin-service"]
        
        for service_name in trading_services:
            await self.control_service(service_name, ActionType.START, reason)
        
        # Clear global halt flag
        if self.redis_client:
            await self.redis_client.delete("global:trading_halt")
            await self.redis_client.delete("global:halt_reason")
            await self.redis_client.delete("global:halt_time")
        
        await self._log_admin_action(
            action="resume_all_trading",
            target="all_trading_services",
            reason=reason
        )
        
        return True
    
    # User Management
    async def suspend_user(self, user_id: str, reason: str, duration: int = None) -> bool:
        """Suspend a user account"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET status = 'suspended', suspension_reason = $1, suspended_until = $2 WHERE user_id = $3",
                    reason,
                    datetime.utcnow() + timedelta(hours=duration) if duration else None,
                    user_id
                )
        
        # Invalidate user sessions
        if self.redis_client:
            await self.redis_client.delete(f"user:session:{user_id}")
            await self.redis_client.sadd("suspended:users", user_id)
        
        await self._log_admin_action(
            action="suspend_user",
            target=user_id,
            reason=reason
        )
        
        return True
    
    async def ban_user(self, user_id: str, reason: str) -> bool:
        """Permanently ban a user"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET status = 'banned', ban_reason = $1 WHERE user_id = $2",
                    reason, user_id
                )
        
        if self.redis_client:
            await self.redis_client.delete(f"user:session:{user_id}")
            await self.redis_client.sadd("banned:users", user_id)
        
        await self._log_admin_action(
            action="ban_user",
            target=user_id,
            reason=reason
        )
        
        return True
    
    async def unsuspend_user(self, user_id: str, reason: str) -> bool:
        """Unsuspend a user"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET status = 'active', suspension_reason = NULL, suspended_until = NULL WHERE user_id = $1",
                    user_id
                )
        
        if self.redis_client:
            await self.redis_client.srem("suspended:users", user_id)
        
        await self._log_admin_action(
            action="unsuspend_user",
            target=user_id,
            reason=reason
        )
        
        return True
    
    async def reset_user_password(self, user_id: str, reason: str) -> str:
        """Reset user password and return temporary password"""
        import secrets
        temp_password = secrets.token_urlsafe(16)
        
        # Hash and store
        import bcrypt
        hashed = bcrypt.hashpw(temp_password.encode(), bcrypt.gensalt())
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET password_hash = $1, require_password_change = true WHERE user_id = $2",
                    hashed.decode(), user_id
                )
        
        await self._log_admin_action(
            action="reset_user_password",
            target=user_id,
            reason=reason
        )
        
        return temp_password
    
    async def modify_user_balance(self, user_id: str, currency: str, amount: Decimal, reason: str) -> bool:
        """Modify user balance (admin adjustment)"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                # Get current balance
                current = await conn.fetchval(
                    "SELECT balance FROM balances WHERE user_id = $1 AND currency = $2",
                    user_id, currency
                )
                
                new_balance = (current or Decimal(0)) + amount
                
                await conn.execute(
                    """
                    INSERT INTO balances (user_id, currency, balance) 
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, currency) 
                    DO UPDATE SET balance = $3
                    """,
                    user_id, currency, new_balance
                )
                
                # Log adjustment
                await conn.execute(
                    """
                    INSERT INTO balance_adjustments (user_id, currency, old_balance, new_balance, adjustment, reason, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_id, currency, current, new_balance, amount, reason, datetime.utcnow()
                )
        
        await self._log_admin_action(
            action="modify_user_balance",
            target=f"{user_id}:{currency}",
            reason=reason
        )
        
        return True
    
    # Trading Control
    async def pause_trading_pair(self, symbol: str, reason: str) -> bool:
        """Pause a trading pair"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE trading_pairs SET status = 'paused', pause_reason = $1 WHERE symbol = $2",
                    reason, symbol
                )
        
        if self.redis_client:
            await self.redis_client.sadd("paused:pairs", symbol)
        
        await self._log_admin_action(
            action="pause_trading_pair",
            target=symbol,
            reason=reason
        )
        
        return True
    
    async def resume_trading_pair(self, symbol: str, reason: str) -> bool:
        """Resume a trading pair"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE trading_pairs SET status = 'active', pause_reason = NULL WHERE symbol = $1",
                    symbol
                )
        
        if self.redis_client:
            await self.redis_client.srem("paused:pairs", symbol)
        
        await self._log_admin_action(
            action="resume_trading_pair",
            target=symbol,
            reason=reason
        )
        
        return True
    
    async def delist_trading_pair(self, symbol: str, reason: str) -> bool:
        """Delist a trading pair"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE trading_pairs SET status = 'delisted', delist_reason = $1 WHERE symbol = $2",
                    reason, symbol
                )
        
        if self.redis_client:
            await self.redis_client.srem("active:pairs", symbol)
            await self.redis_client.sadd("delisted:pairs", symbol)
        
        await self._log_admin_action(
            action="delist_trading_pair",
            target=symbol,
            reason=reason
        )
        
        return True
    
    async def update_trading_fees(self, symbol: str, maker_fee: float, taker_fee: float, reason: str) -> bool:
        """Update trading fees for a pair"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE trading_pairs SET maker_fee = $1, taker_fee = $2 WHERE symbol = $3",
                    maker_fee, taker_fee, symbol
                )
        
        if self.redis_client:
            await self.redis_client.hset(f"fees:{symbol}", mapping={
                "maker": str(maker_fee),
                "taker": str(taker_fee)
            })
        
        await self._log_admin_action(
            action="update_trading_fees",
            target=symbol,
            reason=f"Maker: {maker_fee}, Taker: {taker_fee}. {reason}"
        )
        
        return True
    
    async def set_leverage_limits(self, symbol: str, max_leverage: int, reason: str) -> bool:
        """Set maximum leverage for a trading pair"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE trading_pairs SET max_leverage = $1 WHERE symbol = $2",
                    max_leverage, symbol
                )
        
        if self.redis_client:
            await self.redis_client.hset(f"leverage:{symbol}", "max", max_leverage)
        
        await self._log_admin_action(
            action="set_leverage_limits",
            target=symbol,
            reason=f"Max leverage: {max_leverage}. {reason}"
        )
        
        return True
    
    async def create_or_update_trading_pair(self, payload: TradingPairCreateRequest, reason: str) -> dict:
        """Create or update a trading pair with full admin control metadata"""
        record = {
            "symbol": payload.symbol,
            "base_asset": payload.base_asset,
            "quote_asset": payload.quote_asset,
            "market_type": payload.market_type,
            "maker_fee": payload.maker_fee,
            "taker_fee": payload.taker_fee,
            "max_leverage": payload.max_leverage,
            "status": "active",
            "source": "tigerex",
            "updated_at": datetime.utcnow().isoformat()
        }
        self.trading_pairs[payload.symbol] = record

        await self._log_admin_action("create_or_update_trading_pair", payload.symbol, reason, details=record)
        return record

    async def set_trading_pair_status(self, symbol: str, status: str, reason: str) -> bool:
        pair = self.trading_pairs.get(symbol)
        if not pair:
            return False
        pair["status"] = status
        pair["status_reason"] = reason
        pair["updated_at"] = datetime.utcnow().isoformat()
        await self._log_admin_action("set_trading_pair_status", symbol, reason, details={"status": status})
        return True

    async def import_trading_pair(self, payload: TradingPairImportRequest, reason: str) -> dict:
        imported = {
            "symbol": payload.symbol,
            "market_type": payload.market_type,
            "status": "active",
            "source": payload.source_exchange.lower(),
            "maker_fee": 0.001,
            "taker_fee": 0.001,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.trading_pairs[payload.symbol] = imported
        await self._log_admin_action("import_trading_pair", payload.symbol, reason, details=imported)
        return imported

    async def create_liquidity_pool(self, payload: LiquidityPoolRequest, reason: str) -> dict:
        pool_id = str(uuid.uuid4())
        pool = {
            "pool_id": pool_id,
            "pool_name": payload.pool_name,
            "symbol": payload.symbol,
            "liquidity_amount": payload.liquidity_amount,
            "source_exchange": payload.source_exchange or "tigerex",
            "status": "active",
            "updated_at": datetime.utcnow().isoformat()
        }
        self.liquidity_pools[pool_id] = pool
        await self._log_admin_action("create_liquidity_pool", pool_id, reason, details=pool)
        return pool

    async def set_exchange_status(self, payload: ExchangeStatusRequest) -> dict:
        exchange = {
            "exchange_id": payload.exchange_id,
            "status": payload.status,
            "reason": payload.reason,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.exchange_statuses[payload.exchange_id] = exchange
        await self._log_admin_action("set_exchange_status", payload.exchange_id, payload.reason, details=exchange)
        return exchange

    # Withdrawal Management
    async def approve_withdrawal(self, withdrawal_id: str, reason: str = None) -> bool:
        """Approve a withdrawal request"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE withdrawals SET status = 'approved', approved_at = $1, approved_by = $2 WHERE id = $3",
                    datetime.utcnow(), "admin", withdrawal_id
                )
        
        await self._log_admin_action(
            action="approve_withdrawal",
            target=withdrawal_id,
            reason=reason
        )
        
        return True
    
    async def reject_withdrawal(self, withdrawal_id: str, reason: str) -> bool:
        """Reject a withdrawal request"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE withdrawals SET status = 'rejected', rejected_at = $1, rejected_by = $2, rejection_reason = $3 WHERE id = $4",
                    datetime.utcnow(), "admin", reason, withdrawal_id
                )
        
        await self._log_admin_action(
            action="reject_withdrawal",
            target=withdrawal_id,
            reason=reason
        )
        
        return True
    
    async def hold_withdrawal(self, withdrawal_id: str, reason: str) -> bool:
        """Put a withdrawal on hold"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE withdrawals SET status = 'on_hold', hold_reason = $1 WHERE id = $2",
                    reason, withdrawal_id
                )
        
        await self._log_admin_action(
            action="hold_withdrawal",
            target=withdrawal_id,
            reason=reason
        )
        
        return True
    
    # System Configuration
    async def update_system_config(self, key: str, value: str, reason: str) -> bool:
        """Update system configuration"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO system_config (key, value, updated_at, updated_by)
                    VALUES ($1, $2, $3, 'admin')
                    ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = $3, updated_by = 'admin'
                    """,
                    key, value, datetime.utcnow()
                )
        
        if self.redis_client:
            await self.redis_client.set(f"config:{key}", value)
        
        await self._log_admin_action(
            action="update_system_config",
            target=key,
            reason=f"New value: {value}. {reason}"
        )
        
        return True
    
    async def get_system_config(self, key: str) -> Optional[str]:
        """Get system configuration value"""
        if self.redis_client:
            value = await self.redis_client.get(f"config:{key}")
            if value:
                return value
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                value = await conn.fetchval(
                    "SELECT value FROM system_config WHERE key = $1",
                    key
                )
                return value
        
        return None
    
    # Audit Logging
    async def _log_admin_action(self, action: str, target: str, reason: str = None, details: dict = None):
        """Log admin action for audit"""
        log_entry = {
            "action": action,
            "target": target,
            "reason": reason,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "admin_id": "system"  # Would be actual admin ID in production
        }
        
        if self.redis_client:
            await self.redis_client.lpush("audit:admin_actions", json.dumps(log_entry))
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO admin_audit_log (action, target, reason, details, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    action, target, reason, json.dumps(details or {}), datetime.utcnow()
                )
    
    async def get_audit_logs(self, limit: int = 100, action_filter: str = None) -> List[dict]:
        """Get admin audit logs"""
        logs = []
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                if action_filter:
                    rows = await conn.fetch(
                        "SELECT * FROM admin_audit_log WHERE action LIKE $1 ORDER BY created_at DESC LIMIT $2",
                        f"%{action_filter}%", limit
                    )
                else:
                    rows = await conn.fetch(
                        "SELECT * FROM admin_audit_log ORDER BY created_at DESC LIMIT $1",
                        limit
                    )
                
                logs = [dict(row) for row in rows]
        
        return logs
    
    # Alerts
    async def create_alert(self, service: str, severity: AlertSeverity, message: str) -> SystemAlert:
        """Create a system alert"""
        import uuid
        alert = SystemAlert(
            id=str(uuid.uuid4()),
            service=service,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            acknowledged=False,
            resolved=False
        )
        
        self.alerts.append(alert)
        
        if self.redis_client:
            await self.redis_client.lpush("alerts:active", json.dumps({
                "id": alert.id,
                "service": alert.service,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat()
            }))
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                return True
        return False


# Global Admin Control
admin_control = UnifiedAdminControl()


# Authentication Dependency
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")




def create_access_token(subject: str, role: str = "user", extra: Optional[dict] = None) -> str:
    payload = {
        "sub": subject,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

# API Endpoints

@app.get("/api/v1/admin/dashboard")
async def get_admin_dashboard(admin: dict = Depends(get_current_admin)):
    """Get admin dashboard overview"""
    services = await admin_control.get_all_services()
    
    return {
        "overview": {
            "total_services": len(services),
            "running": sum(1 for s in services.values() if s.status == ServiceStatus.RUNNING),
            "stopped": sum(1 for s in services.values() if s.status == ServiceStatus.STOPPED),
            "paused": sum(1 for s in services.values() if s.status == ServiceStatus.PAUSED),
            "errors": sum(1 for s in services.values() if s.status == ServiceStatus.ERROR),
        },
        "services": {name: {
            "status": svc.status.value,
            "health": svc.health,
            "cpu": svc.cpu_usage,
            "memory": svc.memory_usage
        } for name, svc in services.items()},
        "active_alerts": len([a for a in admin_control.alerts if not a.resolved])
    }


@app.post("/api/v1/auth/social/login")
async def social_login(request: SocialAuthRequest):
    """Social login/register bootstrap endpoint for web, mobile, and desktop clients."""
    provider = request.provider.lower()
    supported = {"google", "facebook", "twitter", "telegram", "apple", "github"}
    if provider not in supported:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

    identity = f"{provider}:{request.provider_user_id}"
    token = create_access_token(
        subject=identity,
        role="user",
        extra={
            "provider": provider,
            "email": request.email,
            "name": request.full_name,
        },
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": identity,
            "provider": provider,
            "email": request.email,
            "full_name": request.full_name,
        },
    }


# Service Control Endpoints
@app.get("/api/v1/admin/services")
async def list_services(admin: dict = Depends(get_current_admin)):
    """List all services"""
    services = await admin_control.get_all_services()
    return {"services": {name: svc.__dict__ for name, svc in services.items()}}


@app.post("/api/v1/admin/services/control")
async def control_service(
    request: ServiceActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Control a service"""
    success = await admin_control.control_service(
        request.service_name,
        request.action,
        request.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to control service")
    return {"success": True, "message": f"Service {request.service_name} {request.action.value}ed"}


@app.post("/api/v1/admin/trading/halt-all")
async def halt_all_trading(
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Emergency halt all trading"""
    await admin_control.halt_all_trading(reason)
    return {"success": True, "message": "All trading halted"}


@app.post("/api/v1/admin/trading/resume-all")
async def resume_all_trading(
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Resume all trading"""
    await admin_control.resume_all_trading(reason)
    return {"success": True, "message": "All trading resumed"}


# User Management Endpoints
@app.post("/api/v1/admin/users/suspend")
async def suspend_user(
    request: UserActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Suspend a user"""
    await admin_control.suspend_user(request.user_id, request.reason, request.duration)
    return {"success": True, "message": f"User {request.user_id} suspended"}


@app.post("/api/v1/admin/users/ban")
async def ban_user(
    request: UserActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Ban a user"""
    await admin_control.ban_user(request.user_id, request.reason)
    return {"success": True, "message": f"User {request.user_id} banned"}


@app.post("/api/v1/admin/users/unsuspend")
async def unsuspend_user(
    request: UserActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Unsuspend a user"""
    await admin_control.unsuspend_user(request.user_id, request.reason)
    return {"success": True, "message": f"User {request.user_id} unsuspended"}


@app.post("/api/v1/admin/users/reset-password")
async def reset_user_password(
    request: UserActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Reset user password"""
    temp_password = await admin_control.reset_user_password(request.user_id, request.reason)
    return {"success": True, "temp_password": temp_password}


@app.post("/api/v1/admin/users/balance")
async def modify_user_balance(
    user_id: str,
    currency: str,
    amount: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Modify user balance"""
    await admin_control.modify_user_balance(user_id, currency, Decimal(amount), reason)
    return {"success": True, "message": f"Balance modified for {user_id}"}


# Trading Control Endpoints
@app.post("/api/v1/admin/trading/pair/pause")
async def pause_trading_pair(
    request: TradingPairActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Pause a trading pair"""
    await admin_control.pause_trading_pair(request.symbol, request.reason)
    return {"success": True, "message": f"Trading pair {request.symbol} paused"}


@app.post("/api/v1/admin/trading/pair/resume")
async def resume_trading_pair(
    request: TradingPairActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Resume a trading pair"""
    await admin_control.resume_trading_pair(request.symbol, request.reason)
    return {"success": True, "message": f"Trading pair {request.symbol} resumed"}


@app.post("/api/v1/admin/trading/pair/delist")
async def delist_trading_pair(
    request: TradingPairActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Delist a trading pair"""
    await admin_control.delist_trading_pair(request.symbol, request.reason)
    return {"success": True, "message": f"Trading pair {request.symbol} delisted"}



@app.post("/api/v1/admin/tradfi/pairs")
async def create_or_update_pair(
    request: TradingPairCreateRequest,
    reason: str = "admin update",
    admin: dict = Depends(get_current_admin)
):
    pair = await admin_control.create_or_update_trading_pair(request, reason)
    return {"success": True, "pair": pair}


@app.post("/api/v1/admin/tradfi/pairs/import")
async def import_pair(
    request: TradingPairImportRequest,
    reason: str = "import from reputed exchange",
    admin: dict = Depends(get_current_admin)
):
    pair = await admin_control.import_trading_pair(request, reason)
    return {"success": True, "pair": pair}


@app.post("/api/v1/admin/tradfi/pairs/{symbol}/status")
async def set_pair_status(
    symbol: str,
    status: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    ok = await admin_control.set_trading_pair_status(symbol, status, reason)
    if not ok:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    return {"success": True, "symbol": symbol, "status": status}


@app.get("/api/v1/admin/tradfi/pairs")
async def list_pairs(admin: dict = Depends(get_current_admin)):
    return {"pairs": list(admin_control.trading_pairs.values())}


@app.post("/api/v1/admin/tradfi/liquidity-pools")
async def create_pool(
    request: LiquidityPoolRequest,
    reason: str = "admin liquidity action",
    admin: dict = Depends(get_current_admin)
):
    pool = await admin_control.create_liquidity_pool(request, reason)
    return {"success": True, "pool": pool}


@app.get("/api/v1/admin/tradfi/liquidity-pools")
async def list_pools(admin: dict = Depends(get_current_admin)):
    return {"pools": list(admin_control.liquidity_pools.values())}


@app.post("/api/v1/admin/exchange/status")
async def update_exchange_status(
    request: ExchangeStatusRequest,
    admin: dict = Depends(get_current_admin)
):
    exchange = await admin_control.set_exchange_status(request)
    return {"success": True, "exchange": exchange}


@app.get("/api/v1/admin/exchange/status/{exchange_id}")
async def get_exchange_status(exchange_id: str, admin: dict = Depends(get_current_admin)):
    status = admin_control.exchange_statuses.get(exchange_id)
    if not status:
        raise HTTPException(status_code=404, detail="Exchange status not found")
    return status


@app.post("/api/v1/admin/trading/fees")
async def update_trading_fees(
    request: FeeUpdateRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update trading fees"""
    await admin_control.update_trading_fees(request.pair_symbol, request.maker_fee, request.taker_fee, request.reason)
    return {"success": True, "message": f"Fees updated for {request.pair_symbol}"}


@app.post("/api/v1/admin/trading/leverage")
async def set_leverage_limits(
    symbol: str,
    max_leverage: int,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Set leverage limits"""
    await admin_control.set_leverage_limits(symbol, max_leverage, reason)
    return {"success": True, "message": f"Leverage limits set for {symbol}"}


# Withdrawal Management Endpoints
@app.post("/api/v1/admin/withdrawals/approve")
async def approve_withdrawal(
    request: WithdrawalActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Approve a withdrawal"""
    await admin_control.approve_withdrawal(request.withdrawal_id, request.reason)
    return {"success": True, "message": f"Withdrawal {request.withdrawal_id} approved"}


@app.post("/api/v1/admin/withdrawals/reject")
async def reject_withdrawal(
    request: WithdrawalActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Reject a withdrawal"""
    await admin_control.reject_withdrawal(request.withdrawal_id, request.reason)
    return {"success": True, "message": f"Withdrawal {request.withdrawal_id} rejected"}


@app.post("/api/v1/admin/withdrawals/hold")
async def hold_withdrawal(
    request: WithdrawalActionRequest,
    admin: dict = Depends(get_current_admin)
):
    """Put a withdrawal on hold"""
    await admin_control.hold_withdrawal(request.withdrawal_id, request.reason)
    return {"success": True, "message": f"Withdrawal {request.withdrawal_id} on hold"}


# System Configuration Endpoints
@app.post("/api/v1/admin/config")
async def update_system_config(
    request: SystemConfigRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update system configuration"""
    await admin_control.update_system_config(request.config_key, request.config_value, request.reason)
    return {"success": True, "message": f"Config {request.config_key} updated"}


@app.get("/api/v1/admin/config/{key}")
async def get_system_config(
    key: str,
    admin: dict = Depends(get_current_admin)
):
    """Get system configuration"""
    value = await admin_control.get_system_config(key)
    return {"key": key, "value": value}


# Audit Endpoints
@app.get("/api/v1/admin/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    action_filter: str = None,
    admin: dict = Depends(get_current_admin)
):
    """Get admin audit logs"""
    logs = await admin_control.get_audit_logs(limit, action_filter)
    return {"logs": logs}


# Alert Endpoints
@app.get("/api/v1/admin/alerts")
async def get_alerts(admin: dict = Depends(get_current_admin)):
    """Get all alerts"""
    return {
        "alerts": [
            {
                "id": a.id,
                "service": a.service,
                "severity": a.severity.value,
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
                "acknowledged": a.acknowledged,
                "resolved": a.resolved
            }
            for a in admin_control.alerts
        ]
    }


@app.post("/api/v1/admin/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Acknowledge an alert"""
    success = await admin_control.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@app.post("/api/v1/admin/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Resolve an alert"""
    success = await admin_control.resolve_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@app.on_event("startup")
async def startup_event():
    await admin_control.initialize()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "unified-admin-control"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)