"""
TigerEx Unified Backend v2
A single, unified backend that combines the best features of the existing services
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import jwt
import asyncio
import json
import csv
import io
import base64
from passlib.context import CryptContext
import redis
import asyncpg
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import pandas as pd
import numpy as np
from sqlalchemy.sql import func
import secrets
from decimal import Decimal

# Initialize FastAPI
app = FastAPI(
    title="TigerEx Unified Backend v2",
    version="2.0.0",
    description="A single, unified backend that combines the best features of the existing services"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "tigerex-unified-backend-secret-key-2025"
ALGORITHM = "HS256"

# Database Configuration
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_unified"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis Configuration
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ==================== MODELS ====================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    LISTINGS_MANAGER = "listings_manager"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    MARKET_MAKER_CLIENT = "market_maker_client"
    DIRECTOR = "director"
    TRADER = "trader"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    RESTRICTED = "restricted"
    BANNED = "banned"

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[str]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None

class Permission(str, Enum):
    # User Management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    USER_VERIFY = "user:verify"

    # Financial Controls
    WITHDRAWAL_APPROVE = "withdrawal:approve"
    WITHDRAWAL_REJECT = "withdrawal:reject"
    DEPOSIT_MONITOR = "deposit:monitor"
    TRANSACTION_REVIEW = "transaction:review"
    FEE_MANAGE = "fee:manage"

    # Trading Controls
    TRADING_HALT = "trading:halt"
    TRADING_RESUME = "trading:resume"
    PAIR_MANAGE = "pair:manage"
    TOKEN_MANAGE = "token:manage"
    LIQUIDITY_MANAGE = "liquidity:manage"

    # Risk Management
    RISK_CONFIGURE = "risk:configure"
    POSITION_MONITOR = "position:monitor"
    LIQUIDATION_MANAGE = "liquidation:manage"

    # System Controls
    SYSTEM_CONFIG = "system:config"
    FEATURE_FLAG = "feature:flag"
    MAINTENANCE_MODE = "maintenance:mode"

    # Compliance
    KYC_APPROVE = "kyc:approve"
    KYC_REJECT = "kyc:reject"
    AML_MONITOR = "aml:monitor"
    COMPLIANCE_REPORT = "compliance:report"

    # Content Management
    ANNOUNCEMENT_CREATE = "announcement:create"
    ANNOUNCEMENT_UPDATE = "announcement:update"
    ANNOUNCEMENT_DELETE = "announcement:delete"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    REPORT_GENERATE = "report:generate"
    AUDIT_LOG_VIEW = "audit:view"

ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [p.value for p in Permission],
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.SYSTEM_CONFIG, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.MODERATOR: [
        Permission.USER_VIEW, Permission.USER_SUSPEND,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANALYTICS_VIEW
    ],
    UserRole.SUPPORT: [
        Permission.USER_VIEW, Permission.TRANSACTION_REVIEW,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.COMPLIANCE: [
        Permission.USER_VIEW, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.AUDIT_LOG_VIEW
    ],
    UserRole.RISK_MANAGER: [
        Permission.POSITION_MONITOR, Permission.RISK_CONFIGURE,
        Permission.LIQUIDATION_MANAGE, Permission.TRADING_HALT,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE
    ],
    UserRole.LISTINGS_MANAGER: [
        Permission.PAIR_MANAGE, Permission.TOKEN_MANAGE,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.LIQUIDITY_PROVIDER: [
        Permission.LIQUIDITY_MANAGE, Permission.POSITION_MONITOR,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.MARKET_MAKER_CLIENT: [
        Permission.POSITION_MONITOR, Permission.ANALYTICS_VIEW
    ],
    UserRole.DIRECTOR: [
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE,
        Permission.AUDIT_LOG_VIEW
    ],
    UserRole.TRADER: [],
    UserRole.USER: []
}

class KYCStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class TradingStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    RESTRICTED = "restricted"
    MARGIN_CALL = "margin_call"
    LIQUIDATION = "liquidation"

class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"
    POLKADOT = "polkadot"

class TokenStandard(str, Enum):
    ERC20 = "ERC20"
    ERC721 = "ERC721"
    ERC1155 = "ERC1155"
    BEP20 = "BEP20"
    SPL = "SPL"
    NATIVE = "NATIVE"

class TokenStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELISTED = "delisted"

class TradingPairStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DELISTED = "delisted"

# ==================== Pydantic Models ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    kyc_status: Optional[KYCStatus] = None
    trading_status: Optional[TradingStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_2fa_enabled: Optional[bool] = None
    profile_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    security_settings: Optional[Dict[str, Any]] = None
    trading_preferences: Optional[Dict[str, Any]] = None
    risk_profile: Optional[Dict[str, Any]] = None
    trading_limits: Optional[Dict[str, Any]] = None

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(50), default=UserRole.USER)
    status = Column(String(50), default=UserStatus.UNVERIFIED)
    kyc_status = Column(String(50), default=KYCStatus.NOT_SUBMITTED)
    trading_status = Column(String(50), default=TradingStatus.DISABLED)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_2fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)

    # Profile data
    profile_data = Column(JSON)
    preferences = Column(JSON)
    security_settings = Column(JSON)

    # Trading data
    trading_preferences = Column(JSON)
    risk_profile = Column(JSON)
    trading_limits = Column(JSON)

    # Relationships
    trading_accounts = relationship("TradingAccount", back_populates="user")

class Blockchain(Base):
    __tablename__ = "blockchains"

    id = Column(Integer, primary_key=True, index=True)
    blockchain_id = Column(String(50), unique=True, nullable=False, index=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=False)
    network = Column(String(50), nullable=False)

    # Technical Details
    rpc_url = Column(String(500), nullable=False)
    chain_id = Column(Integer, nullable=False)
    block_explorer_url = Column(String(500))

    # Configuration
    is_testnet = Column(Boolean, default=False)
    supports_smart_contracts = Column(Boolean, default=True)
    native_currency_symbol = Column(String(10), nullable=False)
    native_currency_decimals = Column(Integer, default=18)

    # Integration Status
    is_active = Column(Boolean, default=True)
    is_trading_enabled = Column(Boolean, default=True)
    is_deposit_enabled = Column(Boolean, default=True)
    is_withdrawal_enabled = Column(Boolean, default=True)

    # Fees
    gas_price_gwei = Column(Float)
    withdrawal_fee = Column(Float)
    min_withdrawal_amount = Column(Float)

    # Metadata
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    documentation_url = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tokens = relationship("Token", back_populates="blockchain")

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(50), unique=True, nullable=False, index=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    decimals = Column(Integer, nullable=False, default=18)

    # Blockchain Reference
    blockchain_id = Column(Integer, ForeignKey("blockchains.id"), nullable=False)
    blockchain = relationship("Blockchain", back_populates="tokens")

    # Contract Information
    contract_address = Column(String(100), index=True)
    token_standard = Column(String(50), nullable=False)

    # Supply Information
    total_supply = Column(Float)
    circulating_supply = Column(Float)
    max_supply = Column(Float)

    # Market Data
    current_price_usd = Column(Float)
    market_cap_usd = Column(Float)
    volume_24h_usd = Column(Float)
    price_change_24h = Column(Float)

    # External IDs
    coingecko_id = Column(String(100))
    coinmarketcap_id = Column(String(100))

    # Metadata
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    whitepaper_url = Column(String(500))

    # Social Links
    twitter_url = Column(String(500))
    telegram_url = Column(String(500))
    discord_url = Column(String(500))
    github_url = Column(String(500))

    # Trading Configuration
    is_tradable = Column(Boolean, default=True)
    min_trade_amount = Column(Float)
    max_trade_amount = Column(Float)

    # Deposit/Withdrawal Configuration
    is_deposit_enabled = Column(Boolean, default=True)
    is_withdrawal_enabled = Column(Boolean, default=True)
    min_deposit_amount = Column(Float)
    min_withdrawal_amount = Column(Float)
    withdrawal_fee = Column(Float)

    # Status
    status = Column(String(50), default=TokenStatus.PENDING)
    listing_date = Column(DateTime)
    delisting_date = Column(DateTime)

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_level = Column(Integer, default=0)  # 0-5 verification levels

    # Risk Assessment
    risk_score = Column(Integer, default=50)  # 0-100
    risk_factors = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    base_pairs = relationship("TradingPair", foreign_keys="TradingPair.base_token_id", back_populates="base_token")
    quote_pairs = relationship("TradingPair", foreign_keys="TradingPair.quote_token_id", back_populates="quote_token")

class TradingPair(Base):
    __tablename__ = "trading_pairs"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(String(50), unique=True, nullable=False, index=True)

    # Token References
    base_token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    quote_token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    base_token = relationship("Token", foreign_keys=[base_token_id], back_populates="base_pairs")
    quote_token = relationship("Token", foreign_keys=[quote_token_id], back_populates="quote_pairs")

    # Pair Information
    symbol = Column(String(20), nullable=False, unique=True, index=True)  # e.g., BTCUSDT

    # Trading Configuration
    min_order_size = Column(Float, nullable=False)
    max_order_size = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    price_precision = Column(Integer, default=8)
    quantity_precision = Column(Integer, default=8)

    # Fees
    maker_fee = Column(Float, default=0.001)  # 0.1%
    taker_fee = Column(Float, default=0.001)  # 0.1%

    # Market Data
    last_price = Column(Float)
    volume_24h = Column(Float, default=0)
    high_24h = Column(Float)
    low_24h = Column(Float)
    price_change_24h = Column(Float, default=0)

    # Status
    status = Column(String(50), default=TradingPairStatus.ACTIVE)
    is_spot_enabled = Column(Boolean, default=True)
    is_margin_enabled = Column(Boolean, default=False)
    is_futures_enabled = Column(Boolean, default=False)

    # Listing Information
    listed_at = Column(DateTime, default=datetime.utcnow)
    delisted_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    kyc_status: KYCStatus
    trading_status: TradingStatus
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    login_count: int
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    profile_data: Optional[Dict[str, Any]]
    preferences: Optional[Dict[str, Any]]
    security_settings: Optional[Dict[str, Any]]
    trading_preferences: Optional[Dict[str, Any]]
    risk_profile: Optional[Dict[str, Any]]
    trading_limits: Optional[Dict[str, Any]]

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderCreate(BaseModel):
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None  # Required for limit orders
    stop_price: Optional[float] = None # Required for stop orders

    @validator('price', always=True)
    def validate_price(cls, v, values):
        if values.get('order_type') in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError('Price is required for limit and stop-limit orders')
        return v

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    filled_quantity: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

class WalletType(str, Enum):
    HOT = "hot"
    COLD = "cold"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), index=True)
    wallet_id = Column(String(50), unique=True, nullable=False, index=True)
    blockchain = Column(String(50), nullable=False)
    address = Column(String(255), unique=True, nullable=False, index=True)
    wallet_type = Column(String(20), default=WalletType.DEPOSIT)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(50), unique=True, nullable=False, index=True)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"))
    transaction_type = Column(String(20)) # deposit, withdrawal, transfer
    from_address = Column(String(255))
    to_address = Column(String(255))
    amount = Column(Float)
    currency = Column(String(20))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class WalletResponse(BaseModel):
    wallet_id: str
    blockchain: str
    address: str
    wallet_type: WalletType
    balance: float
    is_active: bool

class WalletTransactionResponse(BaseModel):
    transaction_id: str
    wallet_id: str
    transaction_type: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    status: str
    created_at: datetime

class UserBalanceResponse(BaseModel):
    account_type: str
    currency: str
    balance: float
    frozen_balance: float

class UserFullProfileResponse(UserResponse):
    balances: List[UserBalanceResponse]
    order_history: List[OrderResponse]

# P2P Models
class P2PUser(Base):
    __tablename__ = "p2p_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    country_code = Column(String(3), nullable=False)
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    total_volume = Column(DECIMAL(20, 2), default=0)
    average_rating = Column(DECIMAL(3, 2), default=0)
    total_ratings = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_p2p_enabled = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    first_trade_at = Column(DateTime)
    last_active_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    method_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    user = relationship("P2PUser", back_populates="payment_methods")
    method_type = Column(String(50), nullable=False)
    method_name = Column(String(100), nullable=False)
    account_details = Column(JSON, nullable=False)
    supported_currencies = Column(JSON)
    supported_countries = Column(JSON)
    min_amount = Column(DECIMAL(20, 2))
    max_amount = Column(DECIMAL(20, 2))
    daily_limit = Column(DECIMAL(20, 2))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

P2PUser.payment_methods = relationship("PaymentMethod", order_by=PaymentMethod.id, back_populates="user")

class P2POrder(Base):
    __tablename__ = "p2p_orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    user = relationship("P2PUser", foreign_keys=[user_id])
    order_type = Column(String(10), nullable=False)
    cryptocurrency = Column(String(10), nullable=False)
    fiat_currency = Column(String(3), nullable=False)
    crypto_amount = Column(DECIMAL(30, 8), nullable=False)
    price_per_unit = Column(DECIMAL(20, 8), nullable=False)
    total_fiat_amount = Column(DECIMAL(20, 2), nullable=False)
    min_trade_amount = Column(DECIMAL(20, 2))
    max_trade_amount = Column(DECIMAL(20, 2))
    accepted_payment_methods = Column(JSON)
    terms = Column(Text)
    auto_reply_message = Column(Text)
    allowed_countries = Column(JSON)
    blocked_countries = Column(JSON)
    status = Column(String(20), default="active")
    expires_at = Column(DateTime)
    completed_trades = Column(Integer, default=0)
    total_volume = Column(DECIMAL(20, 2), default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class P2PTrade(Base):
    __tablename__ = "p2p_trades"
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("p2p_orders.id"), nullable=False)
    order = relationship("P2POrder")
    buyer_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    buyer = relationship("P2PUser", foreign_keys=[buyer_id])
    seller = relationship("P2PUser", foreign_keys=[seller_id])
    crypto_amount = Column(DECIMAL(30, 8), nullable=False)
    fiat_amount = Column(DECIMAL(20, 2), nullable=False)
    price_per_unit = Column(DECIMAL(20, 8), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_reference = Column(String(100))
    status = Column(String(20), default="pending")
    payment_deadline = Column(DateTime, nullable=False)
    escrow_address = Column(String(100))
    escrow_transaction_hash = Column(String(100))
    release_transaction_hash = Column(String(100))
    chat_room_id = Column(String(50), nullable=False)
    platform_fee = Column(DECIMAL(20, 8), default=0)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

class TradeMessage(Base):
    __tablename__ = "trade_messages"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(50), unique=True, nullable=False, index=True)
    trade_id = Column(Integer, ForeignKey("p2p_trades.id"), nullable=False)
    trade = relationship("P2PTrade")
    sender_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    message_type = Column(String(20), default="text")
    content = Column(Text, nullable=False)
    file_url = Column(String(500))
    is_read = Column(Boolean, default=False)
    is_system_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class TradeDispute(Base):
    __tablename__ = "trade_disputes"
    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(String(50), unique=True, nullable=False, index=True)
    trade_id = Column(Integer, ForeignKey("p2p_trades.id"), nullable=False)
    trade = relationship("P2PTrade")
    initiated_by = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    dispute_reason = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    evidence_urls = Column(JSON)
    assigned_admin = Column(String(50))
    admin_notes = Column(Text)
    status = Column(String(20), default="open")
    resolution = Column(Text)
    winner = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)

class P2PFeedback(Base):
    __tablename__ = "p2p_feedback"
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String(50), unique=True, nullable=False, index=True)
    trade_id = Column(Integer, ForeignKey("p2p_trades.id"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("p2p_users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    communication_rating = Column(Integer)
    payment_speed_rating = Column(Integer)
    reliability_rating = Column(Integer)
    created_at = Column(DateTime, default=func.now())

# P2P Pydantic Models
class P2POrderCreate(BaseModel):
    order_type: str
    cryptocurrency: str
    fiat_currency: str
    crypto_amount: float
    price_per_unit: float
    min_trade_amount: Optional[float] = None
    max_trade_amount: Optional[float] = None
    accepted_payment_methods: List[str]
    terms: Optional[str] = None

class P2PTradeCreate(BaseModel):
    order_id: str
    fiat_amount: float
    payment_method_id: str

# Copy Trading Models
class Trader(Base):
    __tablename__ = "traders"
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text)
    avatar_url = Column(String(500))
    trading_since = Column(DateTime, nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_return = Column(DECIMAL(10, 4), default=0)
    monthly_return = Column(DECIMAL(10, 4), default=0)
    followers_count = Column(Integer, default=0)
    total_copied_volume = Column(DECIMAL(20, 2), default=0)
    is_public = Column(Boolean, default=True)
    allow_copying = Column(Boolean, default=True)
    min_copy_amount = Column(DECIMAL(20, 2), default=10)
    max_copy_amount = Column(DECIMAL(20, 2), default=100000)
    performance_fee = Column(DECIMAL(5, 2), default=20)
    is_verified = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())

class CopyRelationship(Base):
    __tablename__ = "copy_relationships"
    id = Column(Integer, primary_key=True, index=True)
    relationship_id = Column(String(50), unique=True, nullable=False, index=True)
    follower_id = Column(String(50), nullable=False, index=True)
    trader_id = Column(Integer, ForeignKey("traders.id"), nullable=False)
    trader = relationship("Trader")
    copy_amount = Column(DECIMAL(20, 2), nullable=False)
    status = Column(String(20), default="active")
    started_at = Column(DateTime, default=func.now())

# Copy Trading Pydantic Models
class TraderCreate(BaseModel):
    display_name: str
    bio: Optional[str] = None
    is_public: bool = True
    allow_copying: bool = True
    min_copy_amount: float = 10
    max_copy_amount: float = 100000
    performance_fee: float = 20

class CopyRelationshipCreate(BaseModel):
    trader_id: str
    copy_amount: float

# P2P Admin Models
class P2PAdminAction(Base):
    __tablename__ = "p2p_admin_actions"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, nullable=False, index=True)
    admin_id = Column(String(50), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class P2PSettings(Base):
    __tablename__ = "p2p_settings"
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_by = Column(String(50), nullable=False)
    updated_at = Column(DateTime, default=func.now())

# P2P Admin Pydantic Models
class DisputeResolution(BaseModel):
    resolution: str
    winner: str

class UserAction(BaseModel):
    action: str
    reason: Optional[str] = None

class TokenListing(Base):
    __tablename__ = "token_listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String(50), unique=True, nullable=False, index=True)

    # Token Information
    token_name = Column(String(100), nullable=False)
    token_symbol = Column(String(20), nullable=False)
    blockchain_network = Column(String(50), nullable=False)
    contract_address = Column(String(100))

    # Applicant Information
    applicant_name = Column(String(100), nullable=False)
    applicant_email = Column(String(255), nullable=False)
    company_name = Column(String(255))

    # Token Details
    total_supply = Column(Float)
    circulating_supply = Column(Float)
    token_description = Column(Text)
    use_case = Column(Text)

    # Documentation
    whitepaper_url = Column(String(500))
    audit_report_url = Column(String(500))
    legal_opinion_url = Column(String(500))

    # Market Information
    current_exchanges = Column(JSON)  # List of current exchanges
    trading_volume = Column(Float)
    market_cap = Column(Float)

    # Application Status
    status = Column(String(20), default="pending")  # pending, under_review, approved, rejected
    review_notes = Column(Text)
    reviewed_by = Column(String(50))
    reviewed_at = Column(DateTime)

    # Fees
    listing_fee_paid = Column(Boolean, default=False)
    listing_fee_amount = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlockchainCreate(BaseModel):
    name: str
    symbol: str
    network: BlockchainNetwork
    rpc_url: str
    chain_id: int
    block_explorer_url: Optional[str] = None
    is_testnet: bool = False
    supports_smart_contracts: bool = True
    native_currency_symbol: str
    native_currency_decimals: int = 18
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None

class TokenCreate(BaseModel):
    name: str
    symbol: str
    decimals: int = 18
    blockchain_id: str
    contract_address: Optional[str] = None
    token_standard: TokenStandard
    total_supply: Optional[float] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    coingecko_id: Optional[str] = None

    @validator('symbol')
    def validate_symbol(cls, v):
        if len(v) < 2 or len(v) > 10:
            raise ValueError('Symbol must be between 2 and 10 characters')
        return v.upper()

class TradingPairCreate(BaseModel):
    base_token_symbol: str
    quote_token_symbol: str
    min_order_size: float
    max_order_size: Optional[float] = None
    price_precision: int = 8
    quantity_precision: int = 8
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    is_margin_enabled: bool = False
    is_futures_enabled: bool = False

class TokenListingApplication(BaseModel):
    token_name: str
    token_symbol: str
    blockchain_network: BlockchainNetwork
    contract_address: Optional[str] = None
    applicant_name: str
    applicant_email: EmailStr
    company_name: Optional[str] = None
    total_supply: float
    circulating_supply: float
    token_description: str
    use_case: str
    whitepaper_url: Optional[str] = None
    website_url: Optional[str] = None

class BulkActionRequest(BaseModel):
    user_ids: List[str]
    action: str  # activate, deactivate, suspend, delete, etc.
    parameters: Optional[Dict[str, Any]] = None

class SystemConfigRequest(BaseModel):
    config_key: str
    config_value: Any
    description: Optional[str] = None

class TradingAccount(Base):
    __tablename__ = "trading_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="trading_accounts")
    account_type = Column(String(50))  # spot, margin, futures
    currency = Column(String(10))
    balance = Column(Float, default=0.0)
    frozen_balance = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    document_type = Column(String(50))  # passport, id_card, driver_license, proof_of_address
    document_number = Column(String(100))
    document_url = Column(Text)
    status = Column(String(50), default=KYCStatus.PENDING)
    review_notes = Column(Text)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradingOrder(Base):
    __tablename__ = "trading_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float)  # Nullable for market orders
    stop_price = Column(Float) # Nullable for non-stop orders
    filled_quantity = Column(Float, default=0.0)
    avg_fill_price = Column(Float)
    status = Column(String(20), default=OrderStatus.PENDING, index=True)
    time_in_force = Column(String(20), default="GTC") # Good 'til Canceled
    client_order_id = Column(String(100)) # Optional client-side ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))
    resource = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== UTILITIES ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles and current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def log_audit_event(user_id: str, action: str, resource: str, details: Dict[str, Any], ip_address: str, user_agent: str):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db = SessionLocal()
    try:
        db.add(audit_log)
        db.commit()
    finally:
        db.close()

# ==================== ADMIN ENDPOINTS ====================

@app.post("/admin/auth/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update login info
    user.last_login = datetime.utcnow()
    user.login_count += 1
    user.failed_login_attempts = 0
    db.commit()

    # Create access token
    access_token_expires = timedelta(hours=24 if request.remember_me else 8)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Log audit event
    log_audit_event(
        user_id=str(user.id),
        action="login",
        resource="admin_panel",
        details={"remember_me": request.remember_me},
        ip_address="0.0.0.0",  # Get from request
        user_agent="admin_panel"
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=UserResponse.from_orm(user)
    )

@app.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    kyc_status: Optional[KYCStatus] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR])),
    db: Session = Depends(get_db)
):
    """Get all users with filtering and pagination"""
    query = db.query(User)

    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%")) |
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(User.role == role)

    if status:
        query = query.filter(User.status == status)

    if kyc_status:
        query = query.filter(User.kyc_status == kyc_status)

    users = query.offset(skip).limit(limit).all()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_users",
        resource="admin_panel",
        details={"filters": {"search": search, "role": role, "status": status, "kyc_status": kyc_status}},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return [UserResponse.from_orm(user) for user in users]

@app.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new user"""

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status=UserStatus.ACTIVE if user_data.role != UserRole.USER else UserStatus.UNVERIFIED,
        is_active=True,
        is_verified=user_data.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create trading account
    trading_account = TradingAccount(
        user_id=db_user.id,
        account_type="spot",
        currency="BTC"
    )
    db.add(trading_account)
    db.commit()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="create_user",
        resource="admin_panel",
        details={"created_user_id": str(db_user.id), "email": db_user.email, "role": db_user.role},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return UserResponse.from_orm(db_user)

@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR])),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_user",
        resource="admin_panel",
        details={"viewed_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return UserResponse.from_orm(user)

@app.get("/admin/users/{user_id}/profile", response_model=UserFullProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR])),
    db: Session = Depends(get_db)
):
    """Get a user's full profile, including balances and order history."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    balances = [UserBalanceResponse.from_orm(acc) for acc in user.trading_accounts]
    orders = db.query(TradingOrder).filter(TradingOrder.user_id == user.id).limit(100).all()
    order_history = [OrderResponse.from_orm(order) for order in orders]

    user_profile = UserFullProfileResponse(
        **UserResponse.from_orm(user).dict(),
        balances=balances,
        order_history=order_history
    )
    return user_profile

@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions for role changes
    if user_data.role and current_user.role != UserRole.SUPER_ADMIN:
        if user_data.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can assign admin roles"
            )

    # Update user fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="update_user",
        resource="admin_panel",
        details={"updated_user_id": str(user.id), "changes": update_data},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return UserResponse.from_orm(user)

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete user (soft delete)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete
    user.is_active = False
    user.status = UserStatus.BANNED
    user.updated_at = datetime.utcnow()
    db.commit()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="delete_user",
        resource="admin_panel",
        details={"deleted_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {"message": "User deleted successfully"}

@app.post("/admin/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Reset user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new password
    new_password = str(uuid.uuid4())[:12]
    hashed_password = get_password_hash(new_password)

    user.hashed_password = hashed_password
    user.updated_at = datetime.utcnow()
    user.is_2fa_enabled = False  # Disable 2FA on password reset
    db.commit()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="reset_password",
        resource="admin_panel",
        details={"reset_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {"message": "Password reset successfully", "new_password": new_password}

@app.post("/admin/users/bulk-action")
async def bulk_user_action(
    bulk_request: "BulkActionRequest",
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on users"""
    updated_count = 0

    for user_id in bulk_request.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if bulk_request.action == "activate":
                user.is_active = True
                user.status = UserStatus.ACTIVE
                updated_count += 1
            elif bulk_request.action == "deactivate":
                user.is_active = False
                user.status = UserStatus.INACTIVE
                updated_count += 1
            elif bulk_request.action == "suspend":
                user.is_active = False
                user.status = UserStatus.SUSPENDED
                updated_count += 1
            elif bulk_request.action == "verify":
                user.is_verified = True
                user.kyc_status = KYCStatus.APPROVED
                updated_count += 1
            elif bulk_request.action == "enable_trading":
                user.trading_status = TradingStatus.ENABLED
                updated_count += 1
            elif bulk_request.action == "disable_trading":
                user.trading_status = TradingStatus.DISABLED
                updated_count += 1

    db.commit()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="bulk_action",
        resource="admin_panel",
        details={
            "action": bulk_request.action,
            "user_count": updated_count,
            "total_requested": len(bulk_request.user_ids)
        },
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {"message": f"Bulk action completed. {updated_count} users updated."}

@app.get("/admin/system/health")
async def system_health_check(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    """Get system health status"""

    # Check database connection
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    finally:
        db.close()

    # Check Redis connection
    try:
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"

    # Get system metrics
    import psutil
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="health_check",
        resource="admin_panel",
        details={},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        },
        "metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage
        }
    }

@app.get("/admin/export/users")
async def export_users(
    format: str = "csv",
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Export users data"""

    users = db.query(User).all()

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "ID", "Email", "Username", "First Name", "Last Name", "Phone",
            "Role", "Status", "KYC Status", "Trading Status", "Is Active",
            "Is Verified", "Created At", "Last Login", "Login Count"
        ])

        # Write data
        for user in users:
            writer.writerow([
                str(user.id), user.email, user.username, user.first_name,
                user.last_name, user.phone, user.role, user.status,
                user.kyc_status, user.trading_status, user.is_active,
                user.is_verified, user.created_at, user.last_login,
                user.login_count
            ])

        output.seek(0)

        # Log audit event
        log_audit_event(
            user_id=str(current_user.id),
            action="export_users",
            resource="admin_panel",
            details={"format": format},
            ip_address="0.0.0.0",
            user_agent="admin_panel"
        )

        return JSONResponse(
            content={"data": output.getvalue()},
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )

    elif format.lower() == "json":
        users_data = [UserResponse.from_orm(user).dict() for user in users]

        # Log audit event
        log_audit_event(
            user_id=str(current_user.id),
            action="export_users",
            resource="admin_panel",
            details={"format": format},
            ip_address="0.0.0.0",
            user_agent="admin_panel"
        )

        return JSONResponse(
            content={"users": users_data},
            headers={"Content-Disposition": "attachment; filename=users_export.json"}
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use 'csv' or 'json'"
        )

@app.get("/admin/config")
async def get_system_config(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Get system configuration"""

    config = {
        "system": {
            "version": "2.0.0",
            "environment": "production",
            "timezone": "UTC",
            "maintenance_mode": False
        },
        "security": {
            "password_min_length": 8,
            "max_login_attempts": 5,
            "session_timeout": 86400,
            "2fa_required": False
        },
        "trading": {
            "min_order_size": 0.001,
            "max_order_size": 1000000,
            "max_leverage": 10,
            "trading_enabled": True
        },
        "kyc": {
            "required_for_trading": True,
            "auto_approve": False,
            "document_expiry_days": 365
        },
        "notifications": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True
        }
    }

    return config

@app.post("/admin/config")
async def update_system_config(
    config_request: SystemConfigRequest,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Update system configuration"""

    # Store in Redis for persistent configuration
    redis_client.set(f"config:{config_request.config_key}", json.dumps(config_request.config_value))

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="update_config",
        resource="admin_panel",
        details={
            "config_key": config_request.config_key,
            "config_value": config_request.config_value
        },
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {"message": "Configuration updated successfully"}

@app.get("/admin/analytics/users")
async def get_user_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR])),
    db: Session = Depends(get_db)
):
    """Get user analytics"""

    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    # Get user statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    kyc_approved = db.query(User).filter(User.kyc_status == KYCStatus.APPROVED).count()

    # Get new users by date
    new_users_by_date = db.query(User).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()

    # Get users by role
    users_by_role = db.query(User.role, db.func.count(User.id)).group_by(User.role).all()

    # Get users by status
    users_by_status = db.query(User.status, db.func.count(User.id)).group_by(User.status).all()

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_analytics",
        resource="admin_panel",
        details={"start_date": start_date, "end_date": end_date},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "kyc_approved": kyc_approved,
        "new_users_count": len(new_users_by_date),
        "users_by_role": dict(users_by_role),
        "users_by_status": dict(users_by_status),
        "registration_trend": [
            {
                "date": user.created_at.date().isoformat(),
                "count": 1
            } for user in new_users_by_date
        ]
    }

@app.get("/admin/roles")
async def get_roles(
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Get all roles and their permissions"""
    return ROLE_PERMISSIONS

@app.put("/admin/roles/{role_name}")
async def update_role_permissions(
    role_name: UserRole,
    permissions: List[Permission],
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Update permissions for a role"""
    if role_name == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify Super Admin role"
        )

    ROLE_PERMISSIONS[role_name] = [p.value for p in permissions]

    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="update_role_permissions",
        resource="admin_panel",
        details={"role": role_name, "permissions": [p.value for p in permissions]},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )

    return {"message": f"Permissions for role '{role_name}' updated successfully"}

# ==================== HEALTH ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TigerEx Unified Backend v2",
        "version": "2.0.0",
        "status": "running"
    }

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

    # Create default super admin if not exists
    db = SessionLocal()
    try:
        super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        if not super_admin:
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@tigerex.com",
                username="superadmin",
                hashed_password=hashed_password,
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            print("Default super admin created: username=superadmin, password=admin123")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

class AdminPanelManager:
    def __init__(self):
        self.redis_client = None
        # self.web3_clients = {}
        self.s3_client = None

    async def initialize(self):
        """Initialize async components"""
        # self.redis_client = await aioredis.from_url(config.REDIS_URL)

        # Initialize Web3 clients
        # self.web3_clients = {
        #     BlockchainNetwork.ETHEREUM: Web3(Web3.HTTPProvider(config.ETHEREUM_RPC_URL)),
        #     BlockchainNetwork.POLYGON: Web3(Web3.HTTPProvider(config.POLYGON_RPC_URL)),
        #     BlockchainNetwork.BSC: Web3(Web3.HTTPProvider(config.BSC_RPC_URL)),
        #     BlockchainNetwork.ARBITRUM: Web3(Web3.HTTPProvider(config.ARBITRUM_RPC_URL)),
        #     BlockchainNetwork.OPTIMISM: Web3(Web3.HTTPProvider(config.OPTIMISM_RPC_URL)),
        #     BlockchainNetwork.AVALANCHE: Web3(Web3.HTTPProvider(config.AVALANCHE_RPC_URL))
        # }

        # Initialize S3 client
        # if config.AWS_ACCESS_KEY_ID:
        #     self.s3_client = boto3.client(
        #         's3',
        #         aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        #         aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        #     )

    async def create_blockchain(self, blockchain_data: BlockchainCreate, admin: Dict[str, Any], db: Session):
        """Create new blockchain integration"""

        # Check if blockchain already exists
        existing = db.query(Blockchain).filter(
            (Blockchain.name == blockchain_data.name) |
            (Blockchain.chain_id == blockchain_data.chain_id)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Blockchain already exists")

        blockchain_id = f"CHAIN_{secrets.token_hex(8).upper()}"

        # Test RPC connection
        # try:
        #     web3 = Web3(Web3.HTTPProvider(str(blockchain_data.rpc_url)))
        #     if not web3.is_connected():
        #         raise HTTPException(status_code=400, detail="Cannot connect to RPC URL")

        #     # Verify chain ID
        #     actual_chain_id = web3.eth.chain_id
        #     if actual_chain_id != blockchain_data.chain_id:
        #         raise HTTPException(status_code=400, detail=f"Chain ID mismatch. Expected {blockchain_data.chain_id}, got {actual_chain_id}")

        # except Exception as e:
        #     raise HTTPException(status_code=400, detail=f"RPC connection failed: {str(e)}")

        blockchain = Blockchain(
            blockchain_id=blockchain_id,
            name=blockchain_data.name,
            symbol=blockchain_data.symbol,
            network=blockchain_data.network,
            rpc_url=str(blockchain_data.rpc_url),
            chain_id=blockchain_data.chain_id,
            block_explorer_url=str(blockchain_data.block_explorer_url) if blockchain_data.block_explorer_url else None,
            is_testnet=blockchain_data.is_testnet,
            supports_smart_contracts=blockchain_data.supports_smart_contracts,
            native_currency_symbol=blockchain_data.native_currency_symbol,
            native_currency_decimals=blockchain_data.native_currency_decimals,
            description=blockchain_data.description,
            logo_url=str(blockchain_data.logo_url) if blockchain_data.logo_url else None,
            website_url=str(blockchain_data.website_url) if blockchain_data.website_url else None
        )

        db.add(blockchain)
        db.commit()
        db.refresh(blockchain)

        # Add to Web3 clients
        # self.web3_clients[blockchain_data.network] = web3

        return blockchain

    async def update_blockchain(self, blockchain_id: str, blockchain_data: BlockchainCreate, admin: Dict[str, Any], db: Session):
        """Update existing blockchain integration"""

        blockchain = db.query(Blockchain).filter(Blockchain.blockchain_id == blockchain_id).first()

        if not blockchain:
            raise HTTPException(status_code=404, detail="Blockchain not found")

        update_data = blockchain_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(blockchain, field, value)

        blockchain.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(blockchain)

        return blockchain

    async def create_token(self, token_data: TokenCreate, admin: Dict[str, Any], db: Session):
        """Create new token"""

        # Get blockchain
        blockchain = db.query(Blockchain).filter(
            Blockchain.blockchain_id == token_data.blockchain_id
        ).first()

        if not blockchain:
            raise HTTPException(status_code=404, detail="Blockchain not found")

        # Check if token already exists
        existing = db.query(Token).filter(
            Token.symbol == token_data.symbol,
            Token.blockchain_id == blockchain.id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Token already exists on this blockchain")

        token_id = f"TOKEN_{secrets.token_hex(8).upper()}"

        # Validate contract address if provided
        if token_data.contract_address and blockchain.supports_smart_contracts:
            await self.validate_token_contract(token_data.contract_address, blockchain, token_data)

        # Fetch market data if external IDs provided
        market_data = {}
        if token_data.coingecko_id:
            market_data = await self.fetch_coingecko_data(token_data.coingecko_id)

        token = Token(
            token_id=token_id,
            name=token_data.name,
            symbol=token_data.symbol,
            decimals=token_data.decimals,
            blockchain_id=blockchain.id,
            contract_address=token_data.contract_address,
            token_standard=token_data.token_standard,
            total_supply=token_data.total_supply,
            description=token_data.description,
            logo_url=str(token_data.logo_url) if token_data.logo_url else None,
            website_url=str(token_data.website_url) if token_data.website_url else None,
            coingecko_id=token_data.coingecko_id,
            current_price_usd=market_data.get('current_price'),
            market_cap_usd=market_data.get('market_cap'),
            volume_24h_usd=market_data.get('volume_24h')
        )

        db.add(token)
        db.commit()
        db.refresh(token)

        return token

    async def update_token(self, token_id: str, token_data: TokenCreate, admin: Dict[str, Any], db: Session):
        """Update existing token"""

        token = db.query(Token).filter(Token.token_id == token_id).first()

        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        update_data = token_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(token, field, value)

        token.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(token)

        return token

    async def create_trading_pair(self, pair_data: TradingPairCreate, admin: Dict[str, Any], db: Session):
        """Create new trading pair"""

        # Get tokens
        base_token = db.query(Token).filter(Token.symbol == pair_data.base_token_symbol).first()
        quote_token = db.query(Token).filter(Token.symbol == pair_data.quote_token_symbol).first()

        if not base_token:
            raise HTTPException(status_code=404, detail=f"Base token {pair_data.base_token_symbol} not found")

        if not quote_token:
            raise HTTPException(status_code=404, detail=f"Quote token {pair_data.quote_token_symbol} not found")

        # Check if pair already exists
        existing = db.query(TradingPair).filter(
            TradingPair.base_token_id == base_token.id,
            TradingPair.quote_token_id == quote_token.id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Trading pair already exists")

        pair_id = f"PAIR_{secrets.token_hex(8).upper()}"
        symbol = f"{base_token.symbol}{quote_token.symbol}"

        trading_pair = TradingPair(
            pair_id=pair_id,
            base_token_id=base_token.id,
            quote_token_id=quote_token.id,
            symbol=symbol,
            min_order_size=pair_data.min_order_size,
            max_order_size=pair_data.max_order_size,
            price_precision=pair_data.price_precision,
            quantity_precision=pair_data.quantity_precision,
            maker_fee=pair_data.maker_fee,
            taker_fee=pair_data.taker_fee,
            is_margin_enabled=pair_data.is_margin_enabled,
            is_futures_enabled=pair_data.is_futures_enabled
        )

        db.add(trading_pair)
        db.commit()
        db.refresh(trading_pair)

        return trading_pair

    async def update_trading_pair(self, pair_id: str, pair_data: TradingPairCreate, admin: Dict[str, Any], db: Session):
        """Update existing trading pair"""

        pair = db.query(TradingPair).filter(TradingPair.pair_id == pair_id).first()

        if not pair:
            raise HTTPException(status_code=404, detail="Trading pair not found")

        update_data = pair_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pair, field, value)

        pair.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pair)

        return pair

    # async def validate_token_contract(self, contract_address: str, blockchain: Blockchain, token_data: TokenCreate):
    #     """Validate token contract on blockchain"""

    #     web3 = self.web3_clients.get(blockchain.network)
    #     if not web3:
    #         return

    #     try:
    #         # Check if address is valid
    #         if not web3.is_address(contract_address):
    #             raise HTTPException(status_code=400, detail="Invalid contract address")

    #         # Check if contract exists
    #         code = web3.eth.get_code(web3.to_checksum_address(contract_address))
    #         if code == b'':
    #             raise HTTPException(status_code=400, detail="No contract found at address")

    #         # For ERC20 tokens, validate basic functions
    #         if token_data.token_standard == TokenStandard.ERC20:
    #             # This would include more comprehensive contract validation
    #             # For now, we'll just check that it's a contract
    #             pass

    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=f"Contract validation failed: {str(e)}")

    async def fetch_coingecko_data(self, coingecko_id: str) -> Dict[str, Any]:
        """Fetch token data from CoinGecko"""

        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}"
            headers = {}

            if config.COINGECKO_API_KEY:
                headers["X-CG-Demo-API-Key"] = config.COINGECKO_API_KEY

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'current_price': data.get('market_data', {}).get('current_price', {}).get('usd'),
                            'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd'),
                            'volume_24h': data.get('market_data', {}).get('total_volume', {}).get('usd')
                        }
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")

        return {}

    async def update_token_market_data(self, db: Session):
        """Update market data for all tokens"""

        tokens = db.query(Token).filter(
            Token.coingecko_id.isnot(None),
            Token.status == TokenStatus.ACTIVE
        ).all()

        for token in tokens:
            try:
                market_data = await self.fetch_coingecko_data(token.coingecko_id)

                if market_data:
                    token.current_price_usd = market_data.get('current_price')
                    token.market_cap_usd = market_data.get('market_cap')
                    token.volume_24h_usd = market_data.get('volume_24h')

                    db.commit()

            except Exception as e:
                logger.error(f"Error updating market data for {token.symbol}: {e}")

    async def submit_listing_application(self, application_data: TokenListingApplication, db: Session):
        """Submit token listing application"""

        listing_id = f"LISTING_{secrets.token_hex(8).upper()}"

        listing = TokenListing(
            listing_id=listing_id,
            token_name=application_data.token_name,
            token_symbol=application_data.token_symbol,
            blockchain_network=application_data.blockchain_network,
            contract_address=application_data.contract_address,
            applicant_name=application_data.applicant_name,
            applicant_email=application_data.applicant_email,
            company_name=application_data.company_name,
            total_supply=application_data.total_supply,
            circulating_supply=application_data.circulating_supply,
            token_description=application_data.token_description,
            use_case=application_data.use_case,
            whitepaper_url=str(application_data.whitepaper_url) if application_data.whitepaper_url else None
        )

        db.add(listing)
        db.commit()
        db.refresh(listing)

        return listing

# Initialize admin manager
admin_manager = AdminPanelManager()

class TradingManager:
    """
    Manages trading operations, including order creation, execution, and tracking.
    """

    def __init__(self):
        # In a real system, this would connect to a matching engine
        self.order_book = {}  # In-memory order book for simulation

    async def create_order(self, order_data: OrderCreate, user: User, db: Session):
        """
        Create a new trading order.
        """

        # 1. Validate trading pair
        trading_pair = db.query(TradingPair).filter(TradingPair.symbol == order_data.symbol).first()
        if not trading_pair or trading_pair.status != TradingPairStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Invalid or inactive trading pair")

        # 2. Check user's trading status and balance
        if user.trading_status != TradingStatus.ENABLED:
            raise HTTPException(status_code=403, detail="Trading is disabled for this account")

        # Balance check would be more complex in a real system
        # This is a simplified check

        # 3. Create and save the order
        order_id = f"ORD_{secrets.token_hex(12).upper()}"

        db_order = TradingOrder(
            order_id=order_id,
            user_id=user.id,
            symbol=order_data.symbol,
            order_type=order_data.order_type,
            side=order_data.side,
            quantity=order_data.quantity,
            price=order_data.price,
            stop_price=order_data.stop_price,
            status=OrderStatus.OPEN if order_data.order_type == OrderType.LIMIT else OrderStatus.PENDING
        )

        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # 4. Process the order
        if db_order.order_type == OrderType.MARKET:
            await self.execute_market_order(db_order, trading_pair, db)
        elif db_order.order_type == OrderType.LIMIT:
            # In a real system, this would be submitted to the matching engine
            pass # Limit orders are open until matched
        elif db_order.order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]:
            # These orders are not executed immediately, but are triggered by price changes
            pass

        return db_order

    async def process_triggered_orders(self, db: Session):
        """Process triggered stop-loss and take-profit orders."""
        orders = db.query(TradingOrder).filter(
            (TradingOrder.status == OrderStatus.PENDING) &
            (TradingOrder.order_type.in_([OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]))
        ).all()

        for order in orders:
            pair = db.query(TradingPair).filter(TradingPair.symbol == order.symbol).first()
            if not pair or not pair.last_price:
                continue

            triggered = False
            if order.order_type == OrderType.STOP_LOSS:
                if (order.side == OrderSide.SELL and pair.last_price <= order.stop_price) or \
                   (order.side == OrderSide.BUY and pair.last_price >= order.stop_price):
                    triggered = True
            elif order.order_type == OrderType.TAKE_PROFIT:
                if (order.side == OrderSide.SELL and pair.last_price >= order.stop_price) or \
                   (order.side == OrderSide.BUY and pair.last_price <= order.stop_price):
                    triggered = True

            if triggered:
                await self.execute_market_order(order, pair, db)

    async def execute_market_order(self, order: TradingOrder, pair: TradingPair, db: Session):
        """
        Simulate the execution of a market order.
        """

        # In a real system, this would interact with the order book to find the best price
        # For simulation, we'll use the last known price

        if not pair.last_price:
            order.status = OrderStatus.REJECTED
            order.review_notes = "No market price available to execute order"
            db.commit()
            return

        order.filled_quantity = order.quantity
        order.avg_fill_price = pair.last_price
        order.status = OrderStatus.FILLED
        order.updated_at = datetime.utcnow()
        db.commit()

        # Here, you would update user balances and notify the user

    async def get_orders_for_user(self, user: User, db: Session, symbol: Optional[str] = None, status: Optional[OrderStatus] = None, limit: int = 50, offset: int = 0):
        """
        Get all orders for a user.
        """
        query = db.query(TradingOrder).filter(TradingOrder.user_id == user.id)

        if symbol:
            query = query.filter(TradingOrder.symbol == symbol)

        if status:
            query = query.filter(TradingOrder.status == status)

        orders = query.order_by(TradingOrder.created_at.desc()).offset(offset).limit(limit).all()
        return orders

trading_manager = TradingManager()

class WalletManager:
    """
    Manages wallet operations, including creation, balance updates, and transfers.
    """

    def __init__(self):
        # In a real system, this would integrate with a secure key management service
        pass

    async def create_wallet(self, blockchain: str, wallet_type: WalletType, db: Session):
        """
        Create a new wallet for a given blockchain.
        """
        # In a real system, this would generate a new address using the appropriate library
        # for the blockchain (e.g., web3.py for Ethereum).
        # This is a simplified placeholder.
        new_address = f"0x{secrets.token_hex(20)}"
        wallet_id = f"WLT_{secrets.token_hex(12).upper()}"

        db_wallet = Wallet(
            wallet_id=wallet_id,
            blockchain=blockchain,
            address=new_address,
            wallet_type=wallet_type
        )

        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)

        return db_wallet

    async def transfer_funds(self, from_wallet: Wallet, to_wallet: Wallet, amount: float, currency: str, db: Session):
        """
        Transfer funds between two wallets.
        """
        if from_wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Create transaction records
        tx_id_out = f"TX_{secrets.token_hex(12).upper()}"
        tx_id_in = f"TX_{secrets.token_hex(12).upper()}"

        # Debit from source wallet
        from_wallet.balance -= amount
        db.add(WalletTransaction(
            transaction_id=tx_id_out,
            wallet_id=from_wallet.id,
            transaction_type="transfer_out",
            from_address=from_wallet.address,
            to_address=to_wallet.address,
            amount=-amount,
            currency=currency,
            status="completed"
        ))

        # Credit to destination wallet
        to_wallet.balance += amount
        db.add(WalletTransaction(
            transaction_id=tx_id_in,
            wallet_id=to_wallet.id,
            transaction_type="transfer_in",
            from_address=from_wallet.address,
            to_address=to_wallet.address,
            amount=amount,
            currency=currency,
            status="completed"
        ))

        db.commit()

    async def get_deposit_address(self, user: User, blockchain: str, db: Session):
        """Get or create a deposit address for a user."""
        wallet = db.query(Wallet).filter(
            Wallet.user_id == str(user.id),
            Wallet.blockchain == blockchain,
            Wallet.wallet_type == WalletType.DEPOSIT
        ).first()

        if not wallet:
            wallet = await self.create_wallet(blockchain, WalletType.DEPOSIT, db)
            wallet.user_id = str(user.id)
            db.commit()

        return wallet

    async def request_withdrawal(self, user: User, blockchain: str, address: str, amount: float, currency: str, db: Session):
        """Request a withdrawal."""
        # In a real system, this would involve more complex validation and security checks
        user_wallet = db.query(Wallet).filter(
            Wallet.user_id == str(user.id),
            Wallet.blockchain == blockchain,
            Wallet.wallet_type == WalletType.DEPOSIT
        ).first()

        if not user_wallet or user_wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        tx_id = f"WTH_{secrets.token_hex(12).upper()}"
        transaction = WalletTransaction(
            transaction_id=tx_id,
            wallet_id=user_wallet.id,
            transaction_type="withdrawal",
            to_address=address,
            amount=amount,
            currency=currency,
            status="pending"
        )
        db.add(transaction)
        user_wallet.balance -= amount
        db.commit()

        return transaction

wallet_manager = WalletManager()

class P2PManager:
    async def get_or_create_p2p_user(self, user: User, db: Session) -> P2PUser:
        p2p_user = db.query(P2PUser).filter(P2PUser.user_id == str(user.id)).first()
        if not p2p_user:
            p2p_user = P2PUser(
                user_id=str(user.id),
                username=user.username,
                email=user.email,
                country_code="US"  # Placeholder
            )
            db.add(p2p_user)
            db.commit()
            db.refresh(p2p_user)
        return p2p_user

    async def create_p2p_order(self, order_data: P2POrderCreate, user: User, db: Session):
        p2p_user = await self.get_or_create_p2p_user(user, db)
        order_id = f"P2P_{secrets.token_hex(8).upper()}"
        total_fiat = order_data.crypto_amount * order_data.price_per_unit
        order = P2POrder(
            order_id=order_id,
            user_id=p2p_user.id,
            order_type=order_data.order_type,
            cryptocurrency=order_data.cryptocurrency,
            fiat_currency=order_data.fiat_currency,
            crypto_amount=order_data.crypto_amount,
            price_per_unit=order_data.price_per_unit,
            total_fiat_amount=total_fiat,
            min_trade_amount=order_data.min_trade_amount or total_fiat,
            max_trade_amount=order_data.max_trade_amount or total_fiat,
            accepted_payment_methods=order_data.accepted_payment_methods,
            terms=order_data.terms
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    async def create_p2p_trade(self, trade_data: P2PTradeCreate, user: User, db: Session):
        p2p_user = await self.get_or_create_p2p_user(user, db)
        order = db.query(P2POrder).filter(P2POrder.order_id == trade_data.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        crypto_amount = trade_data.fiat_amount / order.price_per_unit
        trade_id = f"TRADE_{secrets.token_hex(8).upper()}"
        chat_room_id = f"CHAT_{secrets.token_hex(8).upper()}"

        if order.order_type == "sell":
            buyer_id = p2p_user.id
            seller_id = order.user_id
        else:
            buyer_id = order.user_id
            seller_id = p2p_user.id

        trade = P2PTrade(
            trade_id=trade_id,
            order_id=order.id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            crypto_amount=crypto_amount,
            fiat_amount=trade_data.fiat_amount,
            price_per_unit=order.price_per_unit,
            payment_method_id=int(trade_data.payment_method_id),
            payment_deadline=datetime.utcnow() + timedelta(hours=24),
            chat_room_id=chat_room_id,
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

p2p_manager = P2PManager()

class CopyTradingManager:
    async def create_trader_profile(self, trader_data: TraderCreate, user: User, db: Session):
        existing_trader = db.query(Trader).filter(Trader.user_id == str(user.id)).first()
        if existing_trader:
            raise HTTPException(status_code=400, detail="User already has a trader profile")

        trader_id = f"TRADER_{secrets.token_hex(8).upper()}"
        trader = Trader(
            trader_id=trader_id,
            user_id=str(user.id),
            display_name=trader_data.display_name,
            bio=trader_data.bio,
            trading_since=datetime.now(),
            is_public=trader_data.is_public,
            allow_copying=trader_data.allow_copying,
            min_copy_amount=trader_data.min_copy_amount,
            max_copy_amount=trader_data.max_copy_amount,
            performance_fee=trader_data.performance_fee
        )
        db.add(trader)
        db.commit()
        db.refresh(trader)
        return trader

    async def create_copy_relationship(self, copy_data: CopyRelationshipCreate, follower: User, db: Session):
        trader = db.query(Trader).filter(Trader.trader_id == copy_data.trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")

        relationship_id = f"COPY_{secrets.token_hex(8).upper()}"
        relationship = CopyRelationship(
            relationship_id=relationship_id,
            follower_id=str(follower.id),
            trader_id=trader.id,
            copy_amount=copy_data.copy_amount
        )
        db.add(relationship)
        trader.followers_count += 1
        db.commit()
        db.refresh(relationship)
        return relationship

copy_trading_manager = CopyTradingManager()

class P2PAdminManager:
    async def resolve_dispute(self, dispute_id: str, resolution_data: DisputeResolution, admin: User, db: Session):
        dispute = db.query(TradeDispute).filter(TradeDispute.dispute_id == dispute_id).first()
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")

        dispute.status = "resolved"
        dispute.resolution = resolution_data.resolution
        dispute.winner = resolution_data.winner
        dispute.assigned_admin = str(admin.id)
        dispute.resolved_at = datetime.utcnow()

        trade = dispute.trade
        if resolution_data.winner == "buyer":
            trade.status = "completed"
        elif resolution_data.winner == "seller":
            trade.status = "cancelled"

        db.commit()
        return dispute

    async def manage_user(self, user_id: str, action_data: UserAction, admin: User, db: Session):
        user = db.query(P2PUser).filter(P2PUser.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if action_data.action == "block":
            user.is_blocked = True
        elif action_data.action == "unblock":
            user.is_blocked = False
        elif action_data.action == "verify":
            user.is_verified = True

        db.commit()
        return user

p2p_admin_manager = P2PAdminManager()

async def run_background_tasks(db: Session):
    while True:
        await trading_manager.process_triggered_orders(db)
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    await admin_manager.initialize()
    asyncio.create_task(run_background_tasks(SessionLocal()))

# API Endpoints
@app.post("/api/v1/admin/blockchains")
async def create_blockchain(
    blockchain_data: BlockchainCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new blockchain integration"""
    blockchain = await admin_manager.create_blockchain(blockchain_data, current_admin, db)
    return {
        "blockchain_id": blockchain.blockchain_id,
        "name": blockchain.name,
        "network": blockchain.network,
        "chain_id": blockchain.chain_id,
        "status": "created"
    }

@app.put("/api/v1/admin/blockchains/{blockchain_id}")
async def update_blockchain(
    blockchain_id: str,
    blockchain_data: BlockchainCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update existing blockchain integration"""
    blockchain = await admin_manager.update_blockchain(blockchain_id, blockchain_data, current_admin, db)
    return {
        "blockchain_id": blockchain.blockchain_id,
        "name": blockchain.name,
        "status": "updated"
    }

@app.get("/api/v1/admin/blockchains")
async def get_blockchains(
    is_active: Optional[bool] = None,
    network: Optional[BlockchainNetwork] = None,
    db: Session = Depends(get_db)
):
    """Get all blockchains"""
    query = db.query(Blockchain)

    if is_active is not None:
        query = query.filter(Blockchain.is_active == is_active)

    if network:
        query = query.filter(Blockchain.network == network)

    blockchains = query.all()

    return {
        "blockchains": [
            {
                "blockchain_id": bc.blockchain_id,
                "name": bc.name,
                "symbol": bc.symbol,
                "network": bc.network,
                "chain_id": bc.chain_id,
                "rpc_url": bc.rpc_url,
                "is_active": bc.is_active,
                "is_trading_enabled": bc.is_trading_enabled,
                "native_currency_symbol": bc.native_currency_symbol,
                "created_at": bc.created_at.isoformat()
            }
            for bc in blockchains
        ]
    }

@app.post("/api/v1/admin/tokens")
async def create_token(
    token_data: TokenCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new token"""
    token = await admin_manager.create_token(token_data, current_admin, db)
    return {
        "token_id": token.token_id,
        "name": token.name,
        "symbol": token.symbol,
        "blockchain": token.blockchain.name,
        "status": token.status
    }

@app.put("/api/v1/admin/tokens/{token_id}")
async def update_token(
    token_id: str,
    token_data: TokenCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update existing token"""
    token = await admin_manager.update_token(token_id, token_data, current_admin, db)
    return {
        "token_id": token.token_id,
        "name": token.name,
        "status": "updated"
    }

@app.get("/api/v1/admin/tokens")
async def get_tokens(
    status: Optional[TokenStatus] = None,
    blockchain_id: Optional[str] = None,
    is_tradable: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all tokens"""
    query = db.query(Token)

    if status:
        query = query.filter(Token.status == status)

    if blockchain_id:
        blockchain = db.query(Blockchain).filter(Blockchain.blockchain_id == blockchain_id).first()
        if blockchain:
            query = query.filter(Token.blockchain_id == blockchain.id)

    if is_tradable is not None:
        query = query.filter(Token.is_tradable == is_tradable)

    tokens = query.offset(offset).limit(limit).all()

    return {
        "tokens": [
            {
                "token_id": token.token_id,
                "name": token.name,
                "symbol": token.symbol,
                "blockchain": token.blockchain.name,
                "contract_address": token.contract_address,
                "status": token.status,
                "current_price_usd": str(token.current_price_usd) if token.current_price_usd else None,
                "market_cap_usd": str(token.market_cap_usd) if token.market_cap_usd else None,
                "is_tradable": token.is_tradable,
                "created_at": token.created_at.isoformat()
            }
            for token in tokens
        ]
    }

@app.post("/api/v1/admin/trading-pairs")
async def create_trading_pair(
    pair_data: TradingPairCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new trading pair"""
    pair = await admin_manager.create_trading_pair(pair_data, current_admin, db)
    return {
        "pair_id": pair.pair_id,
        "symbol": pair.symbol,
        "base_token": pair.base_token.symbol,
        "quote_token": pair.quote_token.symbol,
        "status": pair.status
    }

@app.put("/api/v1/admin/trading-pairs/{pair_id}")
async def update_trading_pair(
    pair_id: str,
    pair_data: TradingPairCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update existing trading pair"""
    pair = await admin_manager.update_trading_pair(pair_id, pair_data, current_admin, db)
    return {
        "pair_id": pair.pair_id,
        "symbol": pair.symbol,
        "status": "updated"
    }

@app.get("/api/v1/admin/trading-pairs")
async def get_trading_pairs(
    status: Optional[TradingPairStatus] = None,
    base_token: Optional[str] = None,
    quote_token: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all trading pairs"""
    query = db.query(TradingPair)

    if status:
        query = query.filter(TradingPair.status == status)

    if base_token:
        base_token_obj = db.query(Token).filter(Token.symbol == base_token).first()
        if base_token_obj:
            query = query.filter(TradingPair.base_token_id == base_token_obj.id)

    if quote_token:
        quote_token_obj = db.query(Token).filter(Token.symbol == quote_token).first()
        if quote_token_obj:
            query = query.filter(TradingPair.quote_token_id == quote_token_obj.id)

    pairs = query.offset(offset).limit(limit).all()

    return {
        "trading_pairs": [
            {
                "pair_id": pair.pair_id,
                "symbol": pair.symbol,
                "base_token": pair.base_token.symbol,
                "quote_token": pair.quote_token.symbol,
                "status": pair.status,
                "last_price": str(pair.last_price) if pair.last_price else None,
                "volume_24h": str(pair.volume_24h),
                "price_change_24h": str(pair.price_change_24h),
                "is_spot_enabled": pair.is_spot_enabled,
                "is_margin_enabled": pair.is_margin_enabled,
                "is_futures_enabled": pair.is_futures_enabled,
                "created_at": pair.created_at.isoformat()
            }
            for pair in pairs
        ]
    }

@app.put("/api/v1/admin/trading-pairs/{pair_id}/status")
async def update_trading_pair_status(
    pair_id: str,
    status: TradingPairStatus,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update trading pair status"""
    pair = db.query(TradingPair).filter(TradingPair.pair_id == pair_id).first()

    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")

    pair.status = status
    if status == TradingPairStatus.DELISTED:
        pair.delisted_at = datetime.utcnow()

    db.commit()

    return {
        "pair_id": pair_id,
        "status": status,
        "message": "Trading pair status updated successfully"
    }

@app.delete("/api/v1/admin/trading-pairs/{pair_id}")
async def delete_trading_pair(
    pair_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete trading pair"""
    pair = db.query(TradingPair).filter(TradingPair.pair_id == pair_id).first()

    if not pair:
        raise HTTPException(status_code=404, detail="Trading pair not found")

    # Set status to delisted instead of actual deletion
    pair.status = TradingPairStatus.DELISTED
    pair.delisted_at = datetime.utcnow()

    db.commit()

    return {"message": "Trading pair deleted successfully"}

@app.post("/api/v1/admin/token-listings")
async def submit_token_listing(
    application_data: TokenListingApplication,
    db: Session = Depends(get_db)
):
    """Submit token listing application"""
    listing = await admin_manager.submit_listing_application(application_data, db)
    return {
        "listing_id": listing.listing_id,
        "token_symbol": listing.token_symbol,
        "status": listing.status,
        "message": "Token listing application submitted successfully"
    }

@app.get("/api/v1/admin/token-listings")
async def get_token_listings(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get token listing applications"""
    query = db.query(TokenListing)

    if status:
        query = query.filter(TokenListing.status == status)

    listings = query.order_by(TokenListing.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "listings": [
            {
                "listing_id": listing.listing_id,
                "token_name": listing.token_name,
                "token_symbol": listing.token_symbol,
                "blockchain_network": listing.blockchain_network,
                "applicant_name": listing.applicant_name,
                "applicant_email": listing.applicant_email,
                "status": listing.status,
                "created_at": listing.created_at.isoformat()
            }
            for listing in listings
        ]
    }

@app.put("/api/v1/admin/token-listings/{listing_id}/review")
async def review_token_listing(
    listing_id: str,
    status: str,
    review_notes: Optional[str] = None,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Review token listing application"""
    listing = db.query(TokenListing).filter(TokenListing.listing_id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Token listing not found")

    listing.status = status
    listing.review_notes = review_notes
    listing.reviewed_by = current_admin["user_id"]
    listing.reviewed_at = datetime.utcnow()

    db.commit()

    return {
        "listing_id": listing_id,
        "status": status,
        "message": "Token listing reviewed successfully"
    }

@app.post("/api/v1/admin/market-data/update")
async def update_market_data(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Update market data for all tokens"""
    background_tasks.add_task(admin_manager.update_token_market_data, db)
    return {"message": "Market data update initiated"}

# ==================== TRADING ENDPOINTS ====================

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by its ID.
    """
    order = db.query(TradingOrder).filter(
        TradingOrder.order_id == order_id,
        TradingOrder.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        order_id=order.order_id,
        user_id=str(order.user_id),
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        stop_price=order.stop_price,
        filled_quantity=order.filled_quantity,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

# ==================== P2P TRADING ENDPOINTS ====================

@app.post("/api/v1/p2p/orders")
async def create_p2p_order(
    order_data: P2POrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = await p2p_manager.create_p2p_order(order_data, current_user, db)
    return {"order_id": order.order_id, "status": order.status}

@app.get("/api/v1/p2p/orders")
async def get_p2p_orders(db: Session = Depends(get_db)):
    orders = db.query(P2POrder).filter(P2POrder.status == "active").all()
    return orders

@app.post("/api/v1/p2p/trades")
async def create_p2p_trade(
    trade_data: P2PTradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trade = await p2p_manager.create_p2p_trade(trade_data, current_user, db)
    return {"trade_id": trade.trade_id, "status": trade.status}

@app.get("/api/v1/p2p/trades")
async def get_user_trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    p2p_user = await p2p_manager.get_or_create_p2p_user(current_user, db)
    trades = db.query(P2PTrade).filter(
        (P2PTrade.buyer_id == p2p_user.id) | (P2PTrade.seller_id == p2p_user.id)
    ).all()
    return trades

# ==================== COPY TRADING ENDPOINTS ====================

@app.post("/api/v1/traders")
async def create_trader_profile(
    trader_data: TraderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trader = await copy_trading_manager.create_trader_profile(trader_data, current_user, db)
    return {"trader_id": trader.trader_id, "status": "created"}

@app.get("/api/v1/traders")
async def get_traders(db: Session = Depends(get_db)):
    traders = db.query(Trader).filter(Trader.is_public == True).all()
    return traders

@app.post("/api/v1/copy")
async def create_copy_relationship(
    copy_data: CopyRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    relationship = await copy_trading_manager.create_copy_relationship(copy_data, current_user, db)
    return {"relationship_id": relationship.relationship_id, "status": "active"}

# ==================== P2P ADMIN ENDPOINTS ====================

@app.get("/api/v1/p2p-admin/disputes")
async def get_disputes(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    disputes = db.query(TradeDispute).filter(TradeDispute.status == "open").all()
    return disputes

@app.post("/api/v1/p2p-admin/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    resolution_data: DisputeResolution,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    dispute = await p2p_admin_manager.resolve_dispute(dispute_id, resolution_data, current_admin, db)
    return {"dispute_id": dispute.dispute_id, "status": dispute.status}

@app.post("/api/v1/p2p-admin/users/{user_id}/action")
async def manage_user(
    user_id: str,
    action_data: UserAction,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    user = await p2p_admin_manager.manage_user(user_id, action_data, current_admin, db)
    return {"user_id": user.user_id, "is_blocked": user.is_blocked, "is_verified": user.is_verified}

# ==================== WALLET ENDPOINTS ====================

@app.get("/api/v1/wallet/deposit-address")
async def get_deposit_address(
    blockchain: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wallet = await wallet_manager.get_deposit_address(current_user, blockchain, db)
    return WalletResponse.from_orm(wallet)

@app.post("/api/v1/wallet/request-withdrawal")
async def request_withdrawal(
    blockchain: str,
    address: str,
    amount: float,
    currency: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = await wallet_manager.request_withdrawal(current_user, blockchain, address, amount, currency, db)
    return {"transaction_id": transaction.transaction_id, "status": transaction.status}

@app.post("/api/v1/admin/wallets", response_model=WalletResponse)
async def create_wallet(
    blockchain: str,
    wallet_type: WalletType,
    current_admin: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Create a new wallet.
    """
    wallet = await wallet_manager.create_wallet(blockchain, wallet_type, db)
    return WalletResponse.from_orm(wallet)

@app.get("/api/v1/admin/wallets", response_model=List[WalletResponse])
async def get_wallets(
    wallet_type: Optional[WalletType] = None,
    blockchain: Optional[str] = None,
    current_admin: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get all wallets.
    """
    query = db.query(Wallet)
    if wallet_type:
        query = query.filter(Wallet.wallet_type == wallet_type)
    if blockchain:
        query = query.filter(Wallet.blockchain == blockchain)
    wallets = query.all()
    return [WalletResponse.from_orm(wallet) for wallet in wallets]

@app.post("/api/v1/admin/wallets/transfer")
async def transfer_funds(
    from_wallet_id: str,
    to_wallet_id: str,
    amount: float,
    currency: str,
    current_admin: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Transfer funds between wallets.
    """
    from_wallet = db.query(Wallet).filter(Wallet.wallet_id == from_wallet_id).first()
    to_wallet = db.query(Wallet).filter(Wallet.wallet_id == to_wallet_id).first()

    if not from_wallet or not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    await wallet_manager.transfer_funds(from_wallet, to_wallet, amount, currency, db)
    return {"message": "Transfer completed successfully"}

@app.get("/api/v1/admin/wallets/{wallet_id}/transactions", response_model=List[WalletTransactionResponse])
async def get_wallet_transactions(
    wallet_id: str,
    current_admin: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Get transaction history for a wallet.
    """
    wallet = db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    transactions = db.query(WalletTransaction).filter(WalletTransaction.wallet_id == wallet.id).all()
    return [WalletTransactionResponse.from_orm(tx) for tx in transactions]
    """
    Create a new trading order.
    """
    order = await trading_manager.create_order(order_data, current_user, db)
    return OrderResponse(
        order_id=order.order_id,
        user_id=str(order.user_id),
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        stop_price=order.stop_price,
        filled_quantity=order.filled_quantity,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@app.get("/api/v1/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders for the current user.
    """
    orders = await trading_manager.get_orders_for_user(current_user, db, symbol, status, limit, offset)
    return [
        OrderResponse(
            order_id=order.order_id,
            user_id=str(order.user_id),
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
            stop_price=order.stop_price,
            filled_quantity=order.filled_quantity,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        ) for order in orders
    ]

@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific order by its ID.
    """
    order = db.query(TradingOrder).filter(
        TradingOrder.order_id == order_id,
        TradingOrder.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        order_id=order.order_id,
        user_id=str(order.user_id),
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        stop_price=order.stop_price,
        filled_quantity=order.filled_quantity,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at
    )
