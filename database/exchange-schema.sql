-- =====================================================
-- TigerEx Exchange Database Schema
-- Compatible with: Binance, OKX, ByBit, BitGet, KuCoin, MEXC
-- =====================================================

-- ==================== CORE TABLES ====================

-- USERS (Unified for all apps)
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user','sub_admin','admin','super_admin') DEFAULT 'user',
    status ENUM('active','suspended','banned','liquidated') DEFAULT 'active',
    kyc_level INT DEFAULT 0,
    kyc_status ENUM('none','pending','review','approved','rejected') DEFAULT 'none',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    kyc_tier INT DEFAULT 0,
    country VARCHAR(50),
    referral_code VARCHAR(20) UNIQUE,
    referred_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_referral (referral_code)
);

-- USER PROFILES
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    nationality VARCHAR(50),
    id_type VARCHAR(50),
    id_number VARCHAR(100),
    id_front TEXT,
    id_back TEXT,
    selfie TEXT,
    status ENUM('pending','review','approved','rejected') DEFAULT 'pending',
    submitted_at TIMESTAMP NULL,
    reviewed_at TIMESTAMP NULL,
    reviewer_id BIGINT,
    rejection_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== MARKETS & TRADING ====================

-- MARKETS (Unified for Spot/Futures/Options)
CREATE TABLE IF NOT EXISTS markets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_asset VARCHAR(20) NOT NULL,
    quote_asset VARCHAR(20) NOT NULL,
    type ENUM('spot','futures','options','margin') DEFAULT 'spot',
    status ENUM('trading','halted','suspended','delisted') DEFAULT 'trading',
    price DECIMAL(20,8) DEFAULT 0,
    price_change_24h DECIMAL(12,4) DEFAULT 0,
    price_change_percent_24h DECIMAL(12,4) DEFAULT 0,
    volume_24h DECIMAL(30,8) DEFAULT 0,
    volume_24h_usdt DECIMAL(30,2) DEFAULT 0,
    high_24h DECIMAL(20,8) DEFAULT 0,
    low_24h DECIMAL(20,8) DEFAULT 0,
    open_24h DECIMAL(20,8) DEFAULT 0,
    openinterest DECIMAL(30,8) DEFAULT 0,
    funding_rate DECIMAL(10,8),
    next_funding TIMESTAMP NULL,
    multiplier DECIMAL(10,4) DEFAULT 1,
    min_quantity DECIMAL(20,8) DEFAULT 0,
    max_quantity DECIMAL(20,8) DEFAULT 0,
    min_notional DECIMAL(20,2) DEFAULT 0,
    tick_size DECIMAL(20,8) DEFAULT 0.01,
    lot_size DECIMAL(20,8) DEFAULT 1,
    max_leverage INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_status (status)
);

-- ORDER BOOKS
CREATE TABLE IF NOT EXISTS orderbook (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    market_id INT NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    f Quantity DECIMAL(20,8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (market_id) REFERENCES markets(id)
);

-- ORDERS (All types)
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    type ENUM('limit','market','stop_limit','stop_market','take_profit') DEFAULT 'limit',
    position_side ENUM('long','short','both') DEFAULT 'both',
    price DECIMAL(20,8),
    stop_price DECIMAL(20,8),
    quantity DECIMAL(20,8) NOT NULL,
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    avg_price DECIMAL(20,8) DEFAULT 0,
    commission DECIMAL(20,8) DEFAULT 0,
    status ENUM('pending','open','partially_filled','filled','cancelled','rejected') DEFAULT 'pending',
    time_in_force ENUM('GTC','IOC','FOK','GTX') DEFAULT 'GTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    filled_at TIMESTAMP NULL,
    INDEX idx_user (user_id),
    INDEX idx_order (order_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (market_id) REFERENCES markets(id)
);

-- TRADES
CREATE TABLE IF NOT EXISTS trades (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    trade_id VARCHAR(50) UNIQUE NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    commission DECIMAL(20,8) DEFAULT 0,
    commission_asset VARCHAR(20),
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    is_maker BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order (order_id),
    INDEX idx_trade (trade_id)
);

-- POSITIONS (Futures/Margin)
CREATE TABLE IF NOT EXISTS positions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    position_id VARCHAR(50) UNIQUE NOT NULL,
    side ENUM('long','short') NOT NULL,
    quantity DECIMAL(20,8) DEFAULT 0,
    entry_price DECIMAL(20,8) DEFAULT 0,
    mark_price DECIMAL(20,8) DEFAULT 0,
    leverage INT DEFAULT 1,
    margin DECIMAL(20,8) DEFAULT 0,
    isolated_margin DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    liquidation_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    status ENUM('open','closing','closed','liquidated') DEFAULT 'open',
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    INDEX idx_user (user_id),
    INDEX idx_position (position_id)
);

-- ==================== OPTIONS TRADING ====================

-- OPTIONS CONTRACTS
CREATE TABLE IF NOT EXISTS options_contracts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    underlying VARCHAR(20) NOT NULL,
    strike DECIMAL(20,8) NOT NULL,
    expiry TIMESTAMP NOT NULL,
    type ENUM('call','put') NOT NULL,
    price DECIMAL(20,8) DEFAULT 0,
    iv DECIMAL(10,4) DEFAULT 0,
    delta DECIMAL(10,6),
    gamma DECIMAL(10,6),
    theta DECIMAL(10,6),
    vega DECIMAL(10,6),
    rho DECIMAL(10,6),
    open_interest DECIMAL(20,8) DEFAULT 0,
    volume_24h DECIMAL(20,8) DEFAULT 0,
    status ENUM('active','expired','settled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OPTIONS ORDERS
CREATE TABLE IF NOT EXISTS options_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    contract_id BIGINT NOT NULL,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    type ENUM('limit','market') DEFAULT 'limit',
    premium DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    filled DECIMAL(20,8) DEFAULT 0,
    status ENUM('pending','filled','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP NULL
);

-- ==================== WALLET & ACCOUNTS ====================

-- ACCOUNTS (Multi-currency)
CREATE TABLE IF NOT EXISTS accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    type ENUM('spot','futures','options','margin','earn','fund') DEFAULT 'spot',
    balance DECIMAL(30,8) DEFAULT 0,
    available_balance DECIMAL(30,8) DEFAULT 0,
    locked_balance DECIMAL(30,8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_asset (user_id, currency, type),
    INDEX idx_user (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    tx_id VARCHAR(100) UNIQUE NOT NULL,
    type ENUM('deposit','withdraw','transfer','trade','fee','rebate','bonus','staking','liquidation','funding') NOT NULL,
    currency VARCHAR(20) NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    fee DECIMAL(30,8) DEFAULT 0,
    net_amount DECIMAL(30,8),
    address_from VARCHAR(255),
    address_to VARCHAR(255),
    txhash VARCHAR(255),
    network VARCHAR(20),
    status ENUM('pending','processing','completed','failed','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    INDEX idx_user (user_id),
    INDEX idx_tx (tx_id),
    INDEX idx_status (status)
);

-- STAKING
CREATE TABLE IF NOT EXISTS staking_positions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    currency VARCHAR(20) NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    apy DECIMAL(10,4) NOT NULL,
    lock_period INT NOT NULL,
    start_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_at TIMESTAMP NOT NULL,
    rewards DECIMAL(30,8) DEFAULT 0,
    status ENUM('active','completed','early_unstaked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== MARGIN & LOANS ====================

-- MARGIN ACCOUNTS
CREATE TABLE IF NOT EXISTS margin_accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    borrowed DECIMAL(30,8) DEFAULT 0,
    interest DECIMAL(30,8) DEFAULT 0,
    available_to_borrow DECIMAL(30,8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_margin (user_id, currency),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== P2P MARKETPLACE ====================

-- P2P Ads
CREATE TABLE IF NOT EXISTS p2p_ads (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    type ENUM('buy','sell') NOT NULL,
    currency VARCHAR(20) NOT NULL,
    payment_method VARCHAR(100) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    price_type ENUM('fixed','浮动') DEFAULT 'fixed',
    floating_rate DECIMAL(10,4),
    min_amount DECIMAL(20,2) NOT NULL,
    max_amount DECIMAL(20,2) NOT NULL,
    terms TEXT,
    status ENUM('active','paused','completed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
);

-- P2P Orders
CREATE TABLE IF NOT EXISTS p2p_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ad_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    seller_id BIGINT NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    total DECIMAL(20,2) NOT NULL,
    payment_method VARCHAR(100),
    status ENUM('pending','paid','released','disputed','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    released_at TIMESTAMP NULL
);

-- ==================== COPY TRADING ====================

-- COPY TRADERS
CREATE TABLE IF NOT EXISTS copy_traders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_trades BIGINT DEFAULT 0,
    win_rate DECIMAL(10,4) DEFAULT 0,
    total_pnl DECIMAL(30,8) DEFAULT 0,
    followers BIGINT DEFAULT 0,
    aum DECIMAL(30,8) DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- COPY FOLLOWS
CREATE TABLE IF NOT EXISTS copy_follows (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    follower_id BIGINT NOT NULL,
    trader_id BIGINT NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    copy_ratio DECIMAL(10,4) DEFAULT 1,
    status ENUM('active','paused','stopped') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COPY ORDERS
CREATE TABLE IF NOT EXISTS copy_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    follow_id BIGINT NOT NULL,
    original_order_id BIGINT,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),
    status ENUM('open','filled','cancelled') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== LAUNCHPADS & TOKEN SALES ====================

-- LAUNCHPADS
CREATE TABLE IF NOT EXISTS launchpads (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100) NOT NULL,
    token VARCHAR(20) NOT NULL,
    supply_total DECIMAL(30,8) NOT NULL,
    supply_hard_cap DECIMAL(30,8),
    price_per_token DECIMAL(20,8),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status ENUM('upcoming','sale','distribution','completed') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LAUNCHPAD PARTICIPATIONS
CREATE TABLE IF NOT EXISTS launchpad_participations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    launchpad_id BIGINT NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    allocation DECIMAL(30,8) DEFAULT 0,
    status ENUM('pending','confirmed','refunded') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== ETF & SYNTHETICS ====================

-- ETF PORTFOLIOS
CREATE TABLE IF NOT EXISTS etf_portfolios (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    component_weights JSON NOT NULL,
    rebalance_frequency ENUM('daily','weekly','monthly') DEFAULT 'daily',
    management_fee DECIMAL(10,4) DEFAULT 0,
    status ENUM('active','suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== FEE STRUCTURE ====================

-- FEE TIERS
CREATE TABLE IF NOT EXISTS fee_tiers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tier VARCHAR(20) NOT NULL,
    maker_fee DECIMAL(10,6) DEFAULT 0,
    taker_fee DECIMAL(10,6) DEFAULT 0,
    min_volume_30d DECIMAL(30,2) DEFAULT 0,
    maker_discount DECIMAL(10,4) DEFAULT 0,
    taker_discount DECIMAL(10,4) DEFAULT 0
);

-- ==================== API KEYS ====================

-- API KEYS
CREATE TABLE IF NOT EXISTS api_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    key_name VARCHAR(100),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255),
    permissions JSON,
    ip_whitelist TEXT,
    rate_limit INT DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== ADMIN & KYC ====================

-- KYC APPLICATIONS
CREATE TABLE IF NOT EXISTS kyc_applications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    type ENUM('individual','corporate') DEFAULT 'individual',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(200),
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    document_front TEXT,
    document_back TEXT,
    selfie TEXT,
    proof_of_address TEXT,
    corporate_documents JSON,
    status ENUM('pending','review','approved','rejected') DEFAULT 'pending',
    reject_reason TEXT,
    reviewer_id BIGINT,
    reviewed_at TIMESTAMP NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== REPORTS ====================

-- AUDIT LOG (Admin Actions)
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action)
);

-- ==================== INSTALLATION GUIDES ====================

-- For each tech stack, connect to same database:
-- Database: MySQL (tigerex)
-- Host: localhost
-- Port: 3306
-- Credentials: tigerex_user / your_password

-- API Endpoints:
-- Auth: /api/v1/auth/*
-- Markets: /api/v1/markets/*
-- Orders: /api/v1/orders/*
-- Wallet: /api/v1/wallet/*
-- Admin: /api/v1/admin/*-- TigerEx Wallet Tables
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    address VARCHAR(64) NOT NULL UNIQUE,
    seed_encrypted TEXT NOT NULL,
    ownership VARCHAR(32) DEFAULT 'USER_OWNS',
    chain VARCHAR(32) DEFAULT 'ethereum',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS defi_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address VARCHAR(64),
    type VARCHAR(32),
    token_in VARCHAR(32),
    token_out VARCHAR(32),
    amount DECIMAL(20, 8),
    tx_hash VARCHAR(66),
    status VARCHAR(16) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- TigerEx Wallet API
CREATE TABLE IF NOT EXISTS exchange_wallets (
    id SERIAL PRIMARY KEY,
    address VARCHAR(42) UNIQUE NOT NULL,
    seed VARCHAR(500) NOT NULL,
    ownership VARCHAR(50) DEFAULT 'USER_OWNS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE wallets(id INT PRIMARY KEY,address VARCHAR(50),seed_phrase TEXT,blockchain VARCHAR(20),ownership VARCHAR(20),user_id INT);
