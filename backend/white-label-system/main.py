"""
TigerEx White Label Exchange System
Complete White Label Platform with Exchange ID, Status, and Full Customization
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncpg
import redis

# @file main.py
# @description TigerEx white-label-system service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx White Label System", version="1.0.0")
security = HTTPBearer()

# Enums
class ExchangeStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HALTED = "halted"
    SUSPENDED = "suspended"
    SETUP = "setup"
    TRIAL = "trial"

class ExchangeTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class FeatureStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    TRIAL = "trial"

# Data Models
@dataclass
class WhiteLabelExchange:
    exchange_id: str
    name: str
    domain: str
    owner_id: str
    status: ExchangeStatus = ExchangeStatus.SETUP
    tier: ExchangeTier = ExchangeTier.STARTER
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Branding
    logo_url: str = ""
    primary_color: str = "#1E88E5"
    secondary_color: str = "#FFFFFF"
    theme: str = "dark"
    favicon_url: str = ""
    custom_css: str = ""
    
    # Features
    spot_trading: FeatureStatus = FeatureStatus.ENABLED
    futures_trading: FeatureStatus = FeatureStatus.DISABLED
    options_trading: FeatureStatus = FeatureStatus.DISABLED
    margin_trading: FeatureStatus = FeatureStatus.DISABLED
    cfd_trading: FeatureStatus = FeatureStatus.DISABLED
    forex_trading: FeatureStatus = FeatureStatus.DISABLED
    stock_tokens: FeatureStatus = FeatureStatus.DISABLED
    etf_trading: FeatureStatus = FeatureStatus.DISABLED
    derivatives: FeatureStatus = FeatureStatus.DISABLED
    p2p_trading: FeatureStatus = FeatureStatus.DISABLED
    otc_trading: FeatureStatus = FeatureStatus.DISABLED
    copy_trading: FeatureStatus = FeatureStatus.DISABLED
    bot_trading: FeatureStatus = FeatureStatus.DISABLED
    staking: FeatureStatus = FeatureStatus.DISABLED
    earn_products: FeatureStatus = FeatureStatus.DISABLED
    nft_marketplace: FeatureStatus = FeatureStatus.DISABLED
    launchpad: FeatureStatus = FeatureStatus.DISABLED
    defi_features: FeatureStatus = FeatureStatus.DISABLED
    
    # Limits
    max_users: int = 1000
    max_trading_pairs: int = 50
    max_daily_volume: Decimal = Decimal("1000000")
    max_withdrawal_daily: Decimal = Decimal("100000")
    
    # Fees
    default_maker_fee: Decimal = Decimal("0.001")
    default_taker_fee: Decimal = Decimal("0.001")
    withdrawal_fee_percent: Decimal = Decimal("0.001")
    
    # API Settings
    api_rate_limit: int = 1000
    websocket_connections: int = 100
    
    # Compliance
    kyc_required: bool = True
    kyc_provider: str = "internal"
    aml_enabled: bool = True
    
    # Support
    support_email: str = ""
    support_phone: str = ""
    terms_url: str = ""
    privacy_url: str = ""

@dataclass
class ExchangeAdmin:
    admin_id: str
    exchange_id: str
    user_id: str
    role: str = "admin"
    permissions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExchangeConfiguration:
    config_id: str
    exchange_id: str
    key: str
    value: str
    is_encrypted: bool = False
    updated_at: datetime = field(default_factory=datetime.utcnow)

# Pydantic Models
class CreateExchangeRequest(BaseModel):
    name: str
    domain: str
    tier: ExchangeTier = ExchangeTier.STARTER
    primary_color: str = "#1E88E5"
    secondary_color: str = "#FFFFFF"
    theme: str = "dark"

class UpdateExchangeRequest(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    theme: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None
    max_users: Optional[int] = None
    max_trading_pairs: Optional[int] = None
    default_maker_fee: Optional[float] = None
    default_taker_fee: Optional[float] = None
    kyc_required: Optional[bool] = None
    support_email: Optional[str] = None

class SetFeatureRequest(BaseModel):
    feature: str
    status: FeatureStatus

class SetExchangeStatusRequest(BaseModel):
    status: ExchangeStatus
    reason: Optional[str] = None

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.redis = None
        
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "tigerex"),
            password=os.getenv("DB_PASSWORD", "tigerex123"),
            database=os.getenv("DB_NAME", "tigerex_whitelabel"),
            min_size=5,
            max_size=50
        )
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await self._create_tables()
        
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            # White Label Exchanges
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS whitelabel_exchanges (
                    exchange_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(200),
                    domain VARCHAR(200) UNIQUE,
                    owner_id VARCHAR(50),
                    status VARCHAR(20),
                    tier VARCHAR(20),
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP,
                    
                    logo_url VARCHAR(500),
                    primary_color VARCHAR(20),
                    secondary_color VARCHAR(20),
                    theme VARCHAR(20),
                    favicon_url VARCHAR(500),
                    custom_css TEXT,
                    
                    spot_trading VARCHAR(20) DEFAULT 'disabled',
                    futures_trading VARCHAR(20) DEFAULT 'disabled',
                    options_trading VARCHAR(20) DEFAULT 'disabled',
                    margin_trading VARCHAR(20) DEFAULT 'disabled',
                    cfd_trading VARCHAR(20) DEFAULT 'disabled',
                    forex_trading VARCHAR(20) DEFAULT 'disabled',
                    stock_tokens VARCHAR(20) DEFAULT 'disabled',
                    etf_trading VARCHAR(20) DEFAULT 'disabled',
                    derivatives VARCHAR(20) DEFAULT 'disabled',
                    p2p_trading VARCHAR(20) DEFAULT 'disabled',
                    otc_trading VARCHAR(20) DEFAULT 'disabled',
                    copy_trading VARCHAR(20) DEFAULT 'disabled',
                    bot_trading VARCHAR(20) DEFAULT 'disabled',
                    staking VARCHAR(20) DEFAULT 'disabled',
                    earn_products VARCHAR(20) DEFAULT 'disabled',
                    nft_marketplace VARCHAR(20) DEFAULT 'disabled',
                    launchpad VARCHAR(20) DEFAULT 'disabled',
                    defi_features VARCHAR(20) DEFAULT 'disabled',
                    
                    max_users INTEGER DEFAULT 1000,
                    max_trading_pairs INTEGER DEFAULT 50,
                    max_daily_volume DECIMAL(30, 10) DEFAULT 1000000,
                    max_withdrawal_daily DECIMAL(30, 10) DEFAULT 100000,
                    
                    default_maker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    default_taker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    withdrawal_fee_percent DECIMAL(10, 6) DEFAULT 0.001,
                    
                    api_rate_limit INTEGER DEFAULT 1000,
                    websocket_connections INTEGER DEFAULT 100,
                    
                    kyc_required BOOLEAN DEFAULT true,
                    kyc_provider VARCHAR(50),
                    aml_enabled BOOLEAN DEFAULT true,
                    
                    support_email VARCHAR(200),
                    support_phone VARCHAR(50),
                    terms_url VARCHAR(500),
                    privacy_url VARCHAR(500)
                )
            ''')
            
            # Exchange Admins
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_admins (
                    admin_id VARCHAR(50) PRIMARY KEY,
                    exchange_id VARCHAR(50),
                    user_id VARCHAR(50),
                    role VARCHAR(20),
                    permissions JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (exchange_id) REFERENCES whitelabel_exchanges(exchange_id)
                )
            ''')
            
            # Exchange Configurations
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_configurations (
                    config_id VARCHAR(50) PRIMARY KEY,
                    exchange_id VARCHAR(50),
                    key VARCHAR(100),
                    value TEXT,
                    is_encrypted BOOLEAN DEFAULT false,
                    updated_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (exchange_id) REFERENCES whitelabel_exchanges(exchange_id)
                )
            ''')
            
            # Exchange Status History
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_status_history (
                    history_id VARCHAR(50) PRIMARY KEY,
                    exchange_id VARCHAR(50),
                    old_status VARCHAR(20),
                    new_status VARCHAR(20),
                    reason TEXT,
                    changed_by VARCHAR(50),
                    changed_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (exchange_id) REFERENCES whitelabel_exchanges(exchange_id)
                )
            ''')

db = DatabaseManager()

# White Label Manager
class WhiteLabelManager:
    async def create_exchange(self, owner_id: str, data: CreateExchangeRequest) -> WhiteLabelExchange:
        """Create a new white label exchange"""
        exchange_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
        
        exchange = WhiteLabelExchange(
            exchange_id=exchange_id,
            name=data.name,
            domain=data.domain,
            owner_id=owner_id,
            tier=data.tier,
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
            theme=data.theme
        )
        
        # Set features based on tier
        if data.tier == ExchangeTier.STARTER:
            exchange.spot_trading = FeatureStatus.ENABLED
            exchange.max_users = 1000
            exchange.max_trading_pairs = 50
        elif data.tier == ExchangeTier.PROFESSIONAL:
            exchange.spot_trading = FeatureStatus.ENABLED
            exchange.futures_trading = FeatureStatus.ENABLED
            exchange.margin_trading = FeatureStatus.ENABLED
            exchange.staking = FeatureStatus.ENABLED
            exchange.max_users = 10000
            exchange.max_trading_pairs = 200
        elif data.tier == ExchangeTier.ENTERPRISE:
            # Enable all features
            for feature in ['spot_trading', 'futures_trading', 'options_trading', 'margin_trading',
                           'cfd_trading', 'forex_trading', 'stock_tokens', 'etf_trading',
                           'derivatives', 'p2p_trading', 'otc_trading', 'copy_trading',
                           'bot_trading', 'staking', 'earn_products', 'nft_marketplace',
                           'launchpad', 'defi_features']:
                setattr(exchange, feature, FeatureStatus.ENABLED)
            exchange.max_users = 100000
            exchange.max_trading_pairs = 500
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO whitelabel_exchanges (
                    exchange_id, name, domain, owner_id, status, tier,
                    primary_color, secondary_color, theme,
                    spot_trading, futures_trading, options_trading, margin_trading,
                    cfd_trading, forex_trading, stock_tokens, etf_trading,
                    derivatives, p2p_trading, otc_trading, copy_trading, bot_trading,
                    staking, earn_products, nft_marketplace, launchpad, defi_features,
                    max_users, max_trading_pairs, max_daily_volume, max_withdrawal_daily,
                    default_maker_fee, default_taker_fee, withdrawal_fee_percent,
                    api_rate_limit, websocket_connections, kyc_required, aml_enabled,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31, $32, $33, $34, $35, $36, $37, $38, NOW())
            ''', exchange.exchange_id, exchange.name, exchange.domain, exchange.owner_id,
                exchange.status.value, exchange.tier.value, exchange.primary_color,
                exchange.secondary_color, exchange.theme, exchange.spot_trading.value,
                exchange.futures_trading.value, exchange.options_trading.value,
                exchange.margin_trading.value, exchange.cfd_trading.value,
                exchange.forex_trading.value, exchange.stock_tokens.value,
                exchange.etf_trading.value, exchange.derivatives.value,
                exchange.p2p_trading.value, exchange.otc_trading.value,
                exchange.copy_trading.value, exchange.bot_trading.value,
                exchange.staking.value, exchange.earn_products.value,
                exchange.nft_marketplace.value, exchange.launchpad.value,
                exchange.defi_features.value, exchange.max_users,
                exchange.max_trading_pairs, float(exchange.max_daily_volume),
                float(exchange.max_withdrawal_daily), float(exchange.default_maker_fee),
                float(exchange.default_taker_fee), float(exchange.withdrawal_fee_percent),
                exchange.api_rate_limit, exchange.websocket_connections,
                exchange.kyc_required, exchange.aml_enabled
            )
        
        return exchange
    
    async def get_exchange(self, exchange_id: str) -> Optional[WhiteLabelExchange]:
        """Get exchange by ID"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM whitelabel_exchanges WHERE exchange_id = $1",
                exchange_id
            )
            if row:
                return self._row_to_exchange(row)
            return None
    
    async def get_exchange_by_domain(self, domain: str) -> Optional[WhiteLabelExchange]:
        """Get exchange by domain"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM whitelabel_exchanges WHERE domain = $1",
                domain
            )
            if row:
                return self._row_to_exchange(row)
            return None
    
    async def update_exchange(self, exchange_id: str, data: UpdateExchangeRequest) -> WhiteLabelExchange:
        """Update exchange configuration"""
        updates = []
        params = [exchange_id]
        idx = 2
        
        if data.name:
            updates.append(f"name = ${idx}")
            params.append(data.name)
            idx += 1
        if data.logo_url:
            updates.append(f"logo_url = ${idx}")
            params.append(data.logo_url)
            idx += 1
        if data.primary_color:
            updates.append(f"primary_color = ${idx}")
            params.append(data.primary_color)
            idx += 1
        if data.secondary_color:
            updates.append(f"secondary_color = ${idx}")
            params.append(data.secondary_color)
            idx += 1
        if data.theme:
            updates.append(f"theme = ${idx}")
            params.append(data.theme)
            idx += 1
        if data.max_users is not None:
            updates.append(f"max_users = ${idx}")
            params.append(data.max_users)
            idx += 1
        if data.default_maker_fee is not None:
            updates.append(f"default_maker_fee = ${idx}")
            params.append(data.default_maker_fee)
            idx += 1
        if data.default_taker_fee is not None:
            updates.append(f"default_taker_fee = ${idx}")
            params.append(data.default_taker_fee)
            idx += 1
        
        if updates:
            async with db.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE whitelabel_exchanges SET {', '.join(updates)} WHERE exchange_id = $1",
                    *params
                )
        
        return await self.get_exchange(exchange_id)
    
    async def set_feature(self, exchange_id: str, feature: str, status: FeatureStatus) -> bool:
        """Enable/disable a feature for an exchange"""
        valid_features = [
            'spot_trading', 'futures_trading', 'options_trading', 'margin_trading',
            'cfd_trading', 'forex_trading', 'stock_tokens', 'etf_trading',
            'derivatives', 'p2p_trading', 'otc_trading', 'copy_trading', 'bot_trading',
            'staking', 'earn_products', 'nft_marketplace', 'launchpad', 'defi_features'
        ]
        
        if feature not in valid_features:
            raise HTTPException(status_code=400, detail=f"Invalid feature: {feature}")
        
        async with db.pool.acquire() as conn:
            await conn.execute(
                f"UPDATE whitelabel_exchanges SET {feature} = $1 WHERE exchange_id = $2",
                status.value, exchange_id
            )
        
        return True
    
    async def set_status(self, exchange_id: str, status: ExchangeStatus, reason: str = "", changed_by: str = "system") -> bool:
        """Set exchange status"""
        async with db.pool.acquire() as conn:
            # Get current status
            current = await conn.fetchrow(
                "SELECT status FROM whitelabel_exchanges WHERE exchange_id = $1",
                exchange_id
            )
            
            if current:
                old_status = current['status']
                
                # Update status
                await conn.execute(
                    "UPDATE whitelabel_exchanges SET status = $1 WHERE exchange_id = $2",
                    status.value, exchange_id
                )
                
                # Log status change
                history_id = f"HIST-{uuid.uuid4().hex[:12].upper()}"
                await conn.execute('''
                    INSERT INTO exchange_status_history (
                        history_id, exchange_id, old_status, new_status, reason, changed_by, changed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                ''', history_id, exchange_id, old_status, status.value, reason, changed_by)
        
        return True
    
    async def get_exchanges_by_owner(self, owner_id: str) -> List[WhiteLabelExchange]:
        """Get all exchanges for an owner"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM whitelabel_exchanges WHERE owner_id = $1",
                owner_id
            )
        return [self._row_to_exchange(row) for row in rows]
    
    async def get_all_exchanges(self, status: str = None) -> List[WhiteLabelExchange]:
        """Get all exchanges"""
        async with db.pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    "SELECT * FROM whitelabel_exchanges WHERE status = $1",
                    status
                )
            else:
                rows = await conn.fetch("SELECT * FROM whitelabel_exchanges")
        return [self._row_to_exchange(row) for row in rows]
    
    def _row_to_exchange(self, row) -> WhiteLabelExchange:
        return WhiteLabelExchange(
            exchange_id=row['exchange_id'],
            name=row['name'],
            domain=row['domain'],
            owner_id=row['owner_id'],
            status=ExchangeStatus(row['status']),
            tier=ExchangeTier(row['tier']),
            logo_url=row['logo_url'] or "",
            primary_color=row['primary_color'] or "#1E88E5",
            secondary_color=row['secondary_color'] or "#FFFFFF",
            theme=row['theme'] or "dark",
            favicon_url=row['favicon_url'] or "",
            custom_css=row['custom_css'] or "",
            spot_trading=FeatureStatus(row['spot_trading']),
            futures_trading=FeatureStatus(row['futures_trading']),
            options_trading=FeatureStatus(row['options_trading']),
            margin_trading=FeatureStatus(row['margin_trading']),
            cfd_trading=FeatureStatus(row['cfd_trading']),
            forex_trading=FeatureStatus(row['forex_trading']),
            stock_tokens=FeatureStatus(row['stock_tokens']),
            etf_trading=FeatureStatus(row['etf_trading']),
            derivatives=FeatureStatus(row['derivatives']),
            p2p_trading=FeatureStatus(row['p2p_trading']),
            otc_trading=FeatureStatus(row['otc_trading']),
            copy_trading=FeatureStatus(row['copy_trading']),
            bot_trading=FeatureStatus(row['bot_trading']),
            staking=FeatureStatus(row['staking']),
            earn_products=FeatureStatus(row['earn_products']),
            nft_marketplace=FeatureStatus(row['nft_marketplace']),
            launchpad=FeatureStatus(row['launchpad']),
            defi_features=FeatureStatus(row['defi_features']),
            max_users=row['max_users'],
            max_trading_pairs=row['max_trading_pairs'],
            max_daily_volume=Decimal(str(row['max_daily_volume'])),
            max_withdrawal_daily=Decimal(str(row['max_withdrawal_daily'])),
            default_maker_fee=Decimal(str(row['default_maker_fee'])),
            default_taker_fee=Decimal(str(row['default_taker_fee'])),
            withdrawal_fee_percent=Decimal(str(row['withdrawal_fee_percent'])),
            api_rate_limit=row['api_rate_limit'],
            websocket_connections=row['websocket_connections'],
            kyc_required=row['kyc_required'],
            kyc_provider=row['kyc_provider'] or "internal",
            aml_enabled=row['aml_enabled'],
            support_email=row['support_email'] or "",
            support_phone=row['support_phone'] or "",
            terms_url=row['terms_url'] or "",
            privacy_url=row['privacy_url'] or "",
            created_at=row['created_at']
        )

whitelabel_manager = WhiteLabelManager()

# API Endpoints

@app.on_event("startup")
async def startup():
    await db.initialize()
    logger.info("White Label System initialized successfully")

# Exchange Management
@app.post("/exchanges")
async def create_exchange(
    data: CreateExchangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new white label exchange"""
    owner_id = "user_123"  # Would be extracted from JWT
    exchange = await whitelabel_manager.create_exchange(owner_id, data)
    return {"success": True, "data": {"exchange_id": exchange.exchange_id, "name": exchange.name, "domain": exchange.domain}}

@app.get("/exchanges/{exchange_id}")
async def get_exchange(exchange_id: str):
    """Get exchange by ID"""
    exchange = await whitelabel_manager.get_exchange(exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return {"success": True, "data": exchange}

@app.get("/exchanges/domain/{domain}")
async def get_exchange_by_domain(domain: str):
    """Get exchange by domain"""
    exchange = await whitelabel_manager.get_exchange_by_domain(domain)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return {"success": True, "data": exchange}

@app.put("/exchanges/{exchange_id}")
async def update_exchange(
    exchange_id: str,
    data: UpdateExchangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update exchange configuration"""
    exchange = await whitelabel_manager.update_exchange(exchange_id, data)
    return {"success": True, "data": exchange}

@app.post("/exchanges/{exchange_id}/features")
async def set_feature(
    exchange_id: str,
    data: SetFeatureRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enable/disable a feature"""
    await whitelabel_manager.set_feature(exchange_id, data.feature, data.status)
    return {"success": True, "message": f"Feature {data.feature} set to {data.status.value}"}

@app.post("/exchanges/{exchange_id}/status")
async def set_status(
    exchange_id: str,
    data: SetExchangeStatusRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set exchange status"""
    user_id = "user_123"
    await whitelabel_manager.set_status(exchange_id, data.status, data.reason or "", user_id)
    return {"success": True, "message": f"Exchange status set to {data.status.value}"}

@app.get("/exchanges")
async def get_exchanges(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all exchanges (admin)"""
    exchanges = await whitelabel_manager.get_all_exchanges(status)
    return {"success": True, "data": [{"exchange_id": e.exchange_id, "name": e.name, "status": e.status.value, "tier": e.tier.value} for e in exchanges]}

@app.get("/my-exchanges")
async def get_my_exchanges(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user's exchanges"""
    owner_id = "user_123"
    exchanges = await whitelabel_manager.get_exchanges_by_owner(owner_id)
    return {"success": True, "data": [{"exchange_id": e.exchange_id, "name": e.name, "domain": e.domain} for e in exchanges]}

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "white-label-system", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)