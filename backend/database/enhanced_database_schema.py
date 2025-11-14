#!/usr/bin/env python3
"""
Enhanced Database Schema for TigerEx Platform
Complete database system with all tables, relationships, and migrations
Supports all trading features, user management, and admin controls
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, JSON, Enum, ForeignKey, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timedelta
import uuid
import enum

Base = declarative_base()

# Enhanced Enums for better type safety
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    EXCHANGE_ADMIN = "exchange_admin"
    TRADING_ADMIN = "trading_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    SUPPORT_ADMIN = "support_admin"
    RISK_MANAGER = "risk_manager"
    MARKET_MAKER = "market_maker"
    INSTITUTIONAL_TRADER = "institutional_trader"
    VERIFIED_TRADER = "verified_trader"
    TRADER = "trader"
    PREMIUM_USER = "premium_user"
    VERIFIED_USER = "verified_user"
    USER = "user"

class TradingPermission(enum.Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    OPTIONS_TRADING = "options_trading"
    MARGIN_TRADING = "margin_trading"
    LEVERAGE_TRADING = "leverage_trading"
    ALGO_TRADING = "algo_trading"
    API_TRADING = "api_trading"
    OTC_TRADING = "otc_trading"
    P2P_TRADING = "p2p_trading"
    STAKING = "staking"
    LENDING = "lending"
    BORROWING = "borrowing"

class AdminPermission(enum.Enum):
    USER_MANAGEMENT = "user_management"
    TRADING_CONTROL = "trading_control"
    FINANCIAL_MANAGEMENT = "financial_management"
    SYSTEM_CONFIGURATION = "system_configuration"
    COMPLIANCE_MANAGEMENT = "compliance_management"
    RISK_MANAGEMENT = "risk_management"
    REPORTING = "reporting"
    AUDIT_LOG = "audit_log"
    API_MANAGEMENT = "api_management"
    NOTIFICATION_MANAGEMENT = "notification_management"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    FILL_OR_KILL = "fill_or_kill"
    IMMEDIATE_OR_CANCEL = "immediate_or_cancel"

class OrderSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    TRADE_FEE = "trade_fee"
    WITHDRAWAL_FEE = "withdrawal_fee"
    REFERRAL_BONUS = "referral_bonus"
    STAKING_REWARD = "staking_reward"
    LENDING_INTEREST = "lending_interest"
    BORROWING_INTEREST = "borrowing_interest"

class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    CLOSED = "closed"

class KYCStatus(enum.Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(enum.Enum):
    SYSTEM = "system"
    SECURITY = "security"
    TRADING = "trading"
    FINANCIAL = "financial"
    MARKETING = "marketing"
    SUPPORT = "support"

# Core User Management Tables
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Basic Information
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    phone_verified = Column(Boolean, default=False)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255))
    two_factor_secret = Column(String(32))
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_backup_codes = Column(JSON)
    
    # Roles and Permissions
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    trading_permissions = Column(ARRAY(String), default=list)
    admin_permissions = Column(ARRAY(String), default=list)
    
    # Status and Verification
    account_status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.NOT_SUBMITTED)
    is_premium = Column(Boolean, default=False)
    
    # Personal Information
    first_name = Column(String(50))
    last_name = Column(String(50))
    date_of_birth = Column(DateTime)
    country = Column(String(2))
    state = Column(String(50))
    city = Column(String(50))
    address = Column(Text)
    postal_code = Column(String(20))
    
    # Trading Limits and Settings
    daily_withdrawal_limit = Column(Float, default=10000.0)
    monthly_withdrawal_limit = Column(Float, default=100000.0)
    trading_limit = Column(Float, default=50000.0)
    leverage_limit = Column(Integer, default=10)
    max_positions = Column(Integer, default=50)
    api_trading_enabled = Column(Boolean, default=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login = Column(DateTime, index=True)
    last_login_ip = Column(String(45))
    password_changed_at = Column(DateTime)
    email_verified_at = Column(DateTime)
    phone_verified_at = Column(DateTime)
    
    # Session Management
    session_token = Column(String(255))
    refresh_token = Column(String(255))
    device_fingerprint = Column(String(255))
    
    # Referral System
    referral_code = Column(String(20), unique=True, index=True)
    referred_by = Column(String(50), ForeignKey('users.user_id'))
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    kyc_documents = relationship("KYCDocument", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_username_active', 'username', 'is_active'),
        Index('idx_user_role_status', 'role', 'account_status'),
        Index('idx_user_created_active', 'created_at', 'is_active'),
    )

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Wallet Details
    currency = Column(String(10), nullable=False, index=True)
    network = Column(String(20))  # blockchain network for crypto
    address = Column(String(255), index=True)
    private_key_encrypted = Column(Text)
    public_key = Column(String(255))
    memo = Column(String(100))
    
    # Balances
    balance = Column(Float, default=0.0)
    frozen_balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    pending_deposit = Column(Float, default=0.0)
    pending_withdrawal = Column(Float, default=0.0)
    
    # Wallet Type and Status
    wallet_type = Column(String(20), default='spot')  # spot, margin, futures, savings
    is_active = Column(Boolean, default=True)
    is_hot_wallet = Column(Boolean, default=True)
    is_depositable = Column(Boolean, default=True)
    is_withdrawable = Column(Boolean, default=True)
    
    # Security
    withdrawal_whitelist = Column(JSON)  # List of allowed withdrawal addresses
    daily_withdrawal_limit = Column(Float)
    requires_kyc_for_withdrawal = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_deposit_at = Column(DateTime)
    last_withdrawal_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")
    
    # Constraints
    __table_args__ = (
        Index('idx_wallet_user_currency', 'user_id', 'currency'),
        Index('idx_wallet_address_currency', 'address', 'currency'),
        CheckConstraint('balance >= 0', name='check_balance_positive'),
        CheckConstraint('frozen_balance >= 0', name='check_frozen_balance_positive'),
    )

# Trading Related Tables
class TradingPair(Base):
    __tablename__ = 'trading_pairs'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    base_currency = Column(String(10), nullable=False, index=True)
    quote_currency = Column(String(10), nullable=False, index=True)
    
    # Trading Info
    current_price = Column(Float)
    volume_24h = Column(Float, default=0.0)
    high_24h = Column(Float, default=0.0)
    low_24h = Column(Float, default=0.0)
    change_24h = Column(Float, default=0.0)
    open_24h = Column(Float, default=0.0)
    
    # Trading Rules
    min_order_amount = Column(Float, default=0.001)
    max_order_amount = Column(Float, default=1000000.0)
    min_price = Column(Float)
    max_price = Column(Float)
    price_precision = Column(Integer, default=8)
    quantity_precision = Column(Integer, default=8)
    
    # Fees
    maker_fee = Column(Float, default=0.001)
    taker_fee = Column(Float, default=0.001)
    
    # Status and Features
    is_active = Column(Boolean, default=True, index=True)
    is_margin_enabled = Column(Boolean, default=False)
    is_futures_enabled = Column(Boolean, default=False)
    is_options_enabled = Column(Boolean, default=False)
    is_p2p_enabled = Column(Boolean, default=False)
    
    # Market Data
    order_book_enabled = Column(Boolean, default=True)
    trade_history_enabled = Column(Boolean, default=True)
    candlestick_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="trading_pair")
    trades = relationship("Trade", back_populates="trading_pair")
    positions = relationship("Position", back_populates="trading_pair")
    order_book_entries = relationship("OrderBookEntry", back_populates="trading_pair")
    
    # Constraints
    __table_args__ = (
        Index('idx_pair_base_quote', 'base_currency', 'quote_currency'),
        CheckConstraint('min_order_amount > 0', name='check_min_order_positive'),
        CheckConstraint('max_order_amount > min_order_amount', name='check_max_order_greater'),
    )

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    trading_pair_id = Column(Integer, ForeignKey('trading_pairs.id'), nullable=False, index=True)
    
    # Order Details
    type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    stop_price = Column(Float)
    limit_price = Column(Float)
    
    # Execution Details
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    average_fill_price = Column(Float, default=0.0)
    
    # Trading Info
    leverage = Column(Integer, default=1)
    margin = Column(Float, default=0.0)
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(10))
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    is_active = Column(Boolean, default=True)
    is_reduce_only = Column(Boolean, default=False)
    is_post_only = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    
    # Time in Force
    time_in_force = Column(String(10), default='GTC')  # GTC, IOC, FOK
    
    # Advanced Order Settings
    iceberg_quantity = Column(Float)
    trailing_percent = Column(Float)
    activation_price = Column(Float)
    
    # Client Order ID
    client_order_id = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    activated_at = Column(DateTime)
    filled_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    trading_pair = relationship("TradingPair", back_populates="orders")
    trades = relationship("Trade", back_populates="order")
    
    # Constraints
    __table_args__ = (
        Index('idx_order_user_status', 'user_id', 'status'),
        Index('idx_order_pair_status', 'trading_pair_id', 'status'),
        Index('idx_order_created_status', 'created_at', 'status'),
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('filled_quantity >= 0', name='check_filled_quantity_positive'),
        CheckConstraint('leverage >= 1', name='check_leverage_positive'),
    )

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    trading_pair_id = Column(Integer, ForeignKey('trading_pairs.id'), nullable=False, index=True)
    
    # Trade Details
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Financial
    total = Column(Float)
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(10))
    
    # Matching Info
    maker_order_id = Column(String(50))
    taker_order_id = Column(String(50))
    is_maker = Column(Boolean, default=False)
    
    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    order = relationship("Order", back_populates="trades")
    trading_pair = relationship("TradingPair", back_populates="trades")
    
    # Constraints
    __table_args__ = (
        Index('idx_trade_user_executed', 'user_id', 'executed_at'),
        Index('idx_trade_pair_executed', 'trading_pair_id', 'executed_at'),
        CheckConstraint('quantity > 0', name='check_trade_quantity_positive'),
        CheckConstraint('price > 0', name='check_trade_price_positive'),
    )

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    trading_pair_id = Column(Integer, ForeignKey('trading_pairs.id'), nullable=False, index=True)
    
    # Position Details
    type = Column(String(10))  # long, short
    size = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    mark_price = Column(Float)
    
    # Financial
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    
    # Margin
    margin = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    margin_free = Column(Float, default=0.0)
    leverage = Column(Integer, default=1)
    
    # Risk Management
    liquidation_price = Column(Float)
    bankruptcy_price = Column(Float)
    maintenance_margin = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_auto_close = Column(Boolean, default=False)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    trading_pair = relationship("TradingPair", back_populates="positions")
    
    # Constraints
    __table_args__ = (
        Index('idx_position_user_active', 'user_id', 'is_active'),
        Index('idx_position_pair_active', 'trading_pair_id', 'is_active'),
        CheckConstraint('size != 0', name='check_position_size_nonzero'),
        CheckConstraint('leverage >= 1', name='check_position_leverage_positive'),
    )

class OrderBookEntry(Base):
    __tablename__ = 'order_book_entries'
    
    id = Column(Integer, primary_key=True, index=True)
    trading_pair_id = Column(Integer, ForeignKey('trading_pairs.id'), nullable=False, index=True)
    
    # Entry Details
    side = Column(Enum(OrderSide), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    
    # Aggregated Data
    total_quantity = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trading_pair = relationship("TradingPair", back_populates="order_book_entries")
    
    # Constraints
    __table_args__ = (
        Index('idx_orderbook_pair_price', 'trading_pair_id', 'price', 'side'),
        CheckConstraint('quantity > 0', name='check_orderbook_quantity_positive'),
    )

# Financial Tables
class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False, index=True)
    
    # Transaction Details
    type = Column(Enum(TransactionType), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    
    # Reference Information
    reference_id = Column(String(50))  # Order ID, withdrawal ID, etc.
    external_tx_id = Column(String(100))  # Blockchain transaction ID
    
    # Additional Details
    from_address = Column(String(255))
    to_address = Column(String(255))
    network = Column(String(20))
    confirmations = Column(Integer, default=0)
    required_confirmations = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    
    # Constraints
    __table_args__ = (
        Index('idx_transaction_user_status', 'user_id', 'status'),
        Index('idx_transaction_type_status', 'type', 'status'),
        CheckConstraint('amount != 0', name='check_transaction_amount_nonzero'),
    )

# Admin and Security Tables
class AdminLog(Base):
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), index=True)
    resource_id = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Risk Assessment
    risk_level = Column(String(20), default='low')  # low, medium, high, critical
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Constraints
    __table_args__ = (
        Index('idx_admin_log_action_time', 'action', 'timestamp'),
        Index('idx_admin_log_admin_time', 'admin_user_id', 'timestamp'),
    )

class SystemConfig(Base):
    __tablename__ = 'system_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(Text)
    category = Column(String(50), index=True)
    data_type = Column(String(20), default='string')  # string, number, boolean, json
    is_public = Column(Boolean, default=False)  # Whether config is accessible to users
    is_encrypted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Validation
    min_value = Column(Float)
    max_value = Column(Float)
    allowed_values = Column(JSON)
    
    # Audit
    updated_by = Column(String(50))
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        Index('idx_system_config_category', 'category', 'is_active'),
    )

class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Key Details
    name = Column(String(100))
    key_hash = Column(String(255), nullable=False)
    secret_hash = Column(String(255), nullable=False)
    
    # Permissions
    permissions = Column(ARRAY(String), default=list)
    ip_whitelist = Column(ARRAY(String), default=list)
    
    # Restrictions
    rate_limit = Column(Integer, default=100)  # requests per minute
    withdrawal_enabled = Column(Boolean, default=False)
    trading_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Constraints
    __table_args__ = (
        Index('idx_api_key_user_active', 'user_id', 'is_active'),
    )

class KYCDocument(Base):
    __tablename__ = 'kyc_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Document Details
    document_type = Column(String(50), nullable=False)  # passport, id_card, driver_license, etc.
    document_number = Column(String(100))
    issuing_country = Column(String(2))
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Files
    front_file_url = Column(String(500))
    back_file_url = Column(String(500))
    selfie_file_url = Column(String(500))
    
    # Verification
    verification_status = Column(String(20), default='pending')
    verified_by = Column(String(50))
    rejection_reason = Column(Text)
    verification_notes = Column(Text)
    
    # Metadata
    file_metadata = Column(JSON)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="kyc_documents")
    
    # Constraints
    __table_args__ = (
        Index('idx_kyc_user_status', 'user_id', 'verification_status'),
    )

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Ticket Details
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50))  # account, trading, withdrawal, technical, etc.
    
    # Status and Priority
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, index=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    
    # Assignment
    assigned_to = Column(String(50))
    department = Column(String(50))
    
    # Resolution
    resolution = Column(Text)
    resolved_at = Column(DateTime)
    
    # User Feedback
    user_rating = Column(Integer)
    user_feedback = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="support_tickets")
    
    # Constraints
    __table_args__ = (
        Index('idx_support_ticket_status', 'status', 'created_at'),
        Index('idx_support_ticket_user', 'user_id', 'status'),
    )

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Notification Details
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_email_sent = Column(Boolean, default=False)
    is_push_sent = Column(Boolean, default=False)
    
    # Action URL
    action_url = Column(String(500))
    action_text = Column(String(50))
    
    # Metadata
    data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Constraints
    __table_args__ = (
        Index('idx_notification_user_read', 'user_id', 'is_read'),
        Index('idx_notification_type_created', 'type', 'created_at'),
    )

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    
    # Change Details
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Request Info
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Risk Assessment
    risk_score = Column(Integer, default=0)
    is_suspicious = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Constraints
    __table_args__ = (
        Index('idx_audit_log_action_time', 'action', 'created_at'),
        Index('idx_audit_log_user_time', 'user_id', 'created_at'),
    )

# Migration Management
class Migration(Base):
    __tablename__ = 'migrations'
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Execution Status
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime)
    execution_time = Column(Float)  # seconds
    
    # Rollback Info
    can_rollback = Column(Boolean, default=True)
    rollback_script = Column(Text)
    
    # Metadata
    dependencies = Column(JSON)  # List of required migrations
    checksum = Column(String(64))  # SHA-256 of migration file
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        Index('idx_migration_version_applied', 'version', 'is_applied'),
    )

# Database initialization function
def create_database_schema(database_url: str):
    """Create all database tables with proper schema"""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    
    # Create indexes that aren't handled by SQLAlchemy
    with engine.connect() as conn:
        # Additional performance indexes
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_composite_active 
        ON users (is_active, account_status, created_at DESC);
        """)
        
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_composite_active 
        ON orders (is_active, status, created_at DESC);
        """)
        
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_trades_composite_time 
        ON trades (executed_at DESC, trading_pair_id, user_id);
        """)
        
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_composite_user 
        ON transactions (user_id, status, type, created_at DESC);
        """)
        
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_wallets_composite_balance 
        ON wallets (user_id, currency, balance DESC, updated_at DESC);
        """)
        
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_positions_composite_pnl 
        ON positions (user_id, is_active, unrealized_pnl DESC, updated_at DESC);
        """)
        
    return engine

# Migration utility functions
def run_migrations(engine):
    """Run pending database migrations"""
    # Implementation for running migrations
    pass

def create_migration(name: str, description: str):
    """Create a new migration file"""
    # Implementation for creating migrations
    pass

# Database utility functions
def get_database_stats(engine):
    """Get database statistics and health information"""
    with engine.connect() as conn:
        stats = {}
        
        # Table counts
        tables = ['users', 'orders', 'trades', 'wallets', 'transactions', 'positions']
        for table in tables:
            result = conn.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f'{table}_count'] = result.scalar()
        
        # Database size
        result = conn.execute("SELECT pg_size_pretty(pg_database_size('tigerex'))")
        stats['database_size'] = result.scalar()
        
        # Index usage
        result = conn.execute("""
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        ORDER BY idx_tup_read DESC 
        LIMIT 10
        """)
        stats['top_indexes'] = [dict(row) for row in result]
        
    return stats

if __name__ == "__main__":
    # Example usage
    database_url = "postgresql://user:password@localhost/tigerex"
    engine = create_database_schema(database_url)
    print("Database schema created successfully!")
    
    stats = get_database_stats(engine)
    print("Database stats:", stats)