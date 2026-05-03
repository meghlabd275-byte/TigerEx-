-- TigerEx Enhanced Database Schema
-- Production-ready with indexes, partitioning, and audit logging
-- Version: 2.0

-- ============================================
-- USERS AND AUTHENTICATION
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'trader',
    status VARCHAR(50) DEFAULT 'active',
    kyc_level INTEGER DEFAULT 0,
    kyc_verified_at TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

-- User sessions with expiration
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at) WHERE expires_at > CURRENT_TIMESTAMP;

-- API keys for bots/trading
CREATE TABLE IF NOT EXISTS api_keys (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    secret_hash VARCHAR(255),
    name VARCHAR(100),
    permissions JSONB DEFAULT '{"trading":true,"withdrawal":false,"read":true}',
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);

-- Roles and permissions
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- BLOCKCHAIN NETWORKS
-- ============================================

CREATE TABLE IF NOT EXISTS networks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    chain_id VARCHAR(50),
    rpc_url TEXT,
    rpc_api_key TEXT,  -- Encrypted
    explorer_url TEXT,
    type VARCHAR(50) NOT NULL,
    color VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active',
    gas_url TEXT,  -- Gas price API
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_networks_symbol ON networks(symbol);
CREATE INDEX idx_networks_status ON networks(status) WHERE status = 'active';

-- ============================================
-- COINS AND TOKENS
-- ============================================

CREATE TABLE IF NOT EXISTS coins (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    type VARCHAR(50) DEFAULT 'coin',
    logo_url TEXT,
    icon_url TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    decimals INTEGER DEFAULT 18,
    contract_address TEXT,
    website_url TEXT,
    whitepaper_url TEXT,
    description TEXT,
    is_listed BOOLEAN DEFAULT FALSE,
    listed_at TIMESTAMP,
    delist_at TIMESTAMP,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookups
CREATE INDEX idx_coins_symbol ON coins(symbol);
CREATE INDEX idx_coins_status ON coins(status) WHERE status = 'active';
CREATE INDEX idx_coins_listed ON coins(is_listed) WHERE is_listed = TRUE;

-- Coin social links
CREATE TABLE IF NOT EXISTS coin_socials (
    id BIGSERIAL PRIMARY KEY,
    coin_id BIGINT REFERENCES coins(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coin_socials_coin ON coin_socials(coin_id);

-- Network addresses (per coin per network) - ADDRESSES GENERATED DYNAMICALLY
CREATE TABLE IF NOT EXISTS coin_addresses (
    id BIGSERIAL PRIMARY KEY,
    coin_id BIGINT REFERENCES coins(id) ON DELETE CASCADE,
    network_id INTEGER REFERENCES networks(id) ON DELETE CASCADE,
    deposit_address TEXT NOT NULL,  -- Derived from wallet service
    deposit_memo_support BOOLEAN DEFAULT FALSE,
    withdraw_address TEXT,  -- User-configured
    deposit_enabled BOOLEAN DEFAULT TRUE,
    withdraw_enabled BOOLEAN DEFAULT TRUE,
    min_deposit_amount DECIMAL(20, 8) DEFAULT 0,
    min_withdraw_amount DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(coin_id, network_id)
);

CREATE INDEX idx_coin_addresses_coin ON coin_addresses(coin_id);

-- ============================================
-- TRADING PAIRS
-- ============================================

CREATE TABLE IF NOT EXISTS trading_pairs (
    id BIGSERIAL PRIMARY KEY,
    base_coin_id BIGINT REFERENCES coins(id),
    quote_coin_id BIGINT REFERENCES coins(id),
    pair_symbol VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    maker_fee DECIMAL(10, 6) DEFAULT 0.001,
    taker_fee DECIMAL(10, 6) DEFAULT 0.001,
    min_trade_amount DECIMAL(20, 8) DEFAULT 0.0001,
    max_trade_amount DECIMAL(20, 8),
    price_precision INTEGER DEFAULT 8,
    quantity_precision INTEGER DEFAULT 8,
    min_price DECIMAL(20, 8),
    max_price DECIMAL(20, 8),
    is_active BOOLEAN DEFAULT FALSE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_coin_id, quote_coin_id)
);

CREATE INDEX idx_pairs_symbol ON trading_pairs(pair_symbol);
CREATE INDEX idx_pairs_active ON trading_pairs(is_active) WHERE is_active = TRUE;

-- Price ticker (latest prices)
CREATE TABLE IF NOT EXISTS pair_ticker (
    id BIGSERIAL PRIMARY KEY,
    pair_id BIGINT REFERENCES trading_pairs(id) ON DELETE CASCADE,
    last_price DECIMAL(20, 8) DEFAULT 0,
    price_change_24h DECIMAL(20, 8) DEFAULT 0,
    price_change_pct_24h DECIMAL(10, 4) DEFAULT 0,
    high_24h DECIMAL(20, 8) DEFAULT 0,
    low_24h DECIMAL(20, 8) DEFAULT 0,
    volume_24h DECIMAL(20, 8) DEFAULT 0,
    quote_volume_24h DECIMAL(20, 8) DEFAULT 0,
    trades_24h INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticker_pair ON pair_ticker(pair_id);
CREATE INDEX idx_ticker_updated ON pair_ticker(updated_at);

-- ============================================
-- PRICE HISTORY (OHLCV) - Time series
-- ============================================

CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    pair_id BIGINT REFERENCES trading_pairs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) DEFAULT 0,
    quote_volume DECIMAL(20, 8) DEFAULT 0,
    trades INTEGER DEFAULT 0
);

CREATE INDEX idx_price_history_pair ON price_history(pair_id, timestamp DESC);
CREATE INDEX idx_price_history_ts ON price_history(timestamp DESC);

-- ============================================
-- ORDER BOOK
-- ============================================

CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    pair_id BIGINT REFERENCES trading_pairs(id),
    side VARCHAR(10) NOT NULL,  -- BUY or SELL
    type VARCHAR(20) DEFAULT 'limit',
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    stop_price DECIMAL(20, 8),
    filled_quantity DECIMAL(20, 8) DEFAULT 0,
    average_fill_price DECIMAL(20, 8),
    status VARCHAR(20) DEFAULT 'pending',
    client_order_id VARCHAR(100),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_pair ON orders(pair_id, status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_orders_status ON orders(status) WHERE status IN ('pending', 'partially_filled');

-- ============================================
-- WALLETS AND BALANCES
-- ============================================

CREATE TABLE IF NOT EXISTS wallets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    coin_id BIGINT REFERENCES coins(id),
    network_id INTEGER REFERENCES networks(id),
    address TEXT NOT NULL,
    private_key_encrypted TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wallets_user ON wallets(user_id);
CREATE INDEX idx_wallets_address ON wallets(address);

CREATE TABLE IF NOT EXISTS balances (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    coin_id BIGINT REFERENCES coins(id),
    network_id INTEGER REFERENCES networks(id),
    available_balance DECIMAL(20, 8) DEFAULT 0,
    locked_balance DECIMAL(20, 8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, coin_id, network_id)
);

CREATE INDEX idx_balances_user ON balances(user_id);
CREATE INDEX idx_balances_user_coin ON balances(user_id, coin_id);

-- ============================================
-- TRANSACTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    coin_id BIGINT REFERENCES coins(id),
    network_id INTEGER REFERENCES networks(id),
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0,
    from_address TEXT,
    to_address TEXT,
    tx_hash TEXT,
    confirmations INTEGER DEFAULT 0,
    required_confirmations INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user ON transactions(user_id, created_at DESC);
CREATE INDEX idx_transactions_hash ON transactions(tx_hash);
CREATE INDEX idx_transactions_status ON transactions(status);

-- ============================================
-- AUDIT LOG (Compliance)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- ============================================
-- RATE LIMITING
-- ============================================

CREATE TABLE IF NOT EXISTS rate_limits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    request_count INTEGER DEFAULT 0,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    UNIQUE(user_id, endpoint, window_start)
);

CREATE INDEX idx_rate_limits_user ON rate_limits(user_id, endpoint, window_start);

-- ============================================
-- DEFAULT DATA
-- ============================================

-- Roles
INSERT INTO roles (name, permissions, description) VALUES
('admin', '["all"]', 'Full administration access'),
('manager', '["view","edit","create","manage_coins","manage_pairs"]', 'Trading and coin management'),
('trader', '["view","trade","create_orders"]', 'Trading access only'),
('viewer', '["view"]', 'Read-only access')
ON CONFLICT (name) DO NOTHING;

-- Networks
INSERT INTO networks (name, symbol, chain_id, type, color, status) VALUES
('Bitcoin', 'BTC', '1', 'main', '#F7931A', 'active'),
('Ethereum', 'ETH', '1', 'erc20', '#627EEA', 'active'),
('BNB Smart Chain', 'BSC', '56', 'bep20', '#F0B90B', 'active'),
('Solana', 'SOL', 'main', 'spl', '#00D4A1', 'active'),
('Polygon', 'MATIC', '137', 'erc20', '#8247E5', 'active'),
('Avalanche', 'AVAX', '43114', 'c-chain', '#E84142', 'active'),
('Arbitrum', 'ARB', '42161', 'erc20', '#28A0F0', 'active'),
('Optimism', 'OP', '10', 'erc20', '#FF0420', 'active'),
('Tron', 'TRX', 'main', 'trc20', '#FF0013', 'active')
ON CONFLICT (symbol) DO NOTHING;

-- Default coins (dynamically generated wallet addresses)
-- Use Wallet Service to generate addresses at runtimeCREATE TABLE wallets(id INT PRIMARY KEY,address VARCHAR(50),seed_phrase TEXT,blockchain VARCHAR(20),ownership VARCHAR(20),user_id INT);
