-- TigerEx Database Schema for Trading Pair and Coin Management
-- Supports multiple blockchain networks, deposit/withdrawal addresses, role-based access

-- ============================================
-- USERS AND ROLES
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'trader',
    status VARCHAR(50) DEFAULT 'active',
    kyc_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
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
    explorer_url TEXT,
    type VARCHAR(50) NOT NULL,
    color VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- COINS AND TOKENS
-- ============================================

CREATE TABLE IF NOT EXISTS coins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    type VARCHAR(50) DEFAULT 'coin',
    logo_url TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    decimals INTEGER DEFAULT 18,
    contract_address TEXT,
    website_url TEXT,
    whitepaper_url TEXT,
    description TEXT,
    is_listed BOOLEAN DEFAULT FALSE,
    listed_at TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coin_socials (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- NETWORK ADDRESSES (Deposit/Withdrawal)
-- ============================================

CREATE TABLE IF NOT EXISTS coin_addresses (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    network_id INTEGER REFERENCES networks(id) ON DELETE CASCADE,
    deposit_address TEXT,
    withdraw_address TEXT,
    deposit_enabled BOOLEAN DEFAULT TRUE,
    withdraw_enabled BOOLEAN DEFAULT TRUE,
    min_deposit_amount DECIMAL(20, 8) DEFAULT 0,
    min_withdraw_amount DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(coin_id, network_id)
);

-- ============================================
-- TRADING PAIRS
-- ============================================

CREATE TABLE IF NOT EXISTS trading_pairs (
    id SERIAL PRIMARY KEY,
    base_coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    quote_coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    pair_symbol VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    maker_fee DECIMAL(10, 6) DEFAULT 0.001,
    taker_fee DECIMAL(10, 6) DEFAULT 0.001,
    min_trade_amount DECIMAL(20, 8) DEFAULT 0.0001,
    max_trade_amount DECIMAL(20, 8),
    price_precision INTEGER DEFAULT 8,
    quantity_precision INTEGER DEFAULT 8,
    is_active BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_coin_id, quote_coin_id)
);

-- ============================================
-- WALLETS AND BALANCES
-- ============================================

CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    network_id INTEGER REFERENCES networks(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    private_key_encrypted TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    network_id INTEGER REFERENCES networks(id) ON DELETE CASCADE,
    available_balance DECIMAL(20, 8) DEFAULT 0,
    locked_balance DECIMAL(20, 8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, coin_id, network_id)
);

-- ============================================
-- TRANSACTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    coin_id INTEGER REFERENCES coins(id),
    network_id INTEGER REFERENCES networks(id),
    type VARCHAR(50) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0,
    from_address TEXT,
    to_address TEXT,
    tx_hash TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ROLE PERMISSIONS
-- ============================================

INSERT INTO roles (name, permissions, description) VALUES
('admin', '["all"]', 'Full administration access'),
('manager', '["view", "edit", "create", "manage_coins", "manage_pairs"]', 'Trading and coin management'),
('trader', '["view", "trade", "create_orders"]', 'Trading access only'),
('viewer', '["view"]', 'Read-only access');

-- ============================================
-- DEFAULT NETWORKS
-- ============================================

INSERT INTO networks (name, symbol, chain_id, type, color, status) VALUES
('Bitcoin', 'BTC', '1', 'main', '#F7931A', 'active'),
('Ethereum', 'ETH', '1', 'erc20', '#627EEA', 'active'),
('BNB Smart Chain', 'BSC', '56', 'bep20', '#F0B90B', 'active'),
('Solana', 'SOL', 'main', 'spl', '#00D4A1', 'active'),
('Polygon', 'MATIC', '137', 'erc20', '#8247E5', 'active'),
('Avalanche', 'AVAX', '43114', 'c-chain', '#E84142', 'active'),
('Arbitrum', 'ARB', '42161', 'erc20', '#28A0F0', 'active'),
('Optimism', 'OP', '10', 'erc20', '#FF0420', 'active'),
('Tron', 'TRX', 'main', 'trc20', '#FF0013', 'active');

-- ============================================
-- DEFAULT COINS
-- ============================================

INSERT INTO coins (name, symbol, type, status, is_listed, description) VALUES
('Bitcoin', 'BTC', 'coin', 'active', TRUE, 'Bitcoin is a decentralized digital currency.'),
('Ethereum', 'ETH', 'token', 'active', TRUE, 'Ethereum is a decentralized blockchain.'),
('BNB', 'BNB', 'token', 'active', TRUE, 'BNB is the native token of BNB Chain.'),
('Solana', 'SOL', 'coin', 'active', TRUE, 'Solana is a high-performance blockchain.'),
('Tether USD', 'USDT', 'token', 'active', TRUE, 'USD-pegged stablecoin');

-- ============================================
-- ADMIN USER (default password: admin123)
-- ============================================

INSERT INTO users (username, email, password_hash, role, status) VALUES
('admin', 'admin@tigerex.com', '$2a$10$x4Z5Y9Q8Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9', 'admin', 'active');