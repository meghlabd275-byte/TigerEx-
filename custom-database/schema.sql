-- TigerEx Database Schema
-- PostgreSQL schema for TigerEx exchange

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== USERS ====================

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    kyc_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- ==================== ACCOUNTS ====================

CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(40, 0) DEFAULT 0,
    frozen_balance DECIMAL(40, 0) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- ==================== ORDERS ====================

CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    pair VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    order_type VARCHAR(10) NOT NULL,
    price DECIMAL(40, 8),
    quantity DECIMAL(40, 8),
    filled DECIMAL(40, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_pair ON orders(pair);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- ==================== TRANSACTIONS ====================

CREATE TABLE IF NOT EXISTS transactions (
    tx_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(order_id),
    user_id UUID REFERENCES users(user_id),
    type VARCHAR(20) NOT NULL,
    amount DECIMAL(40, 8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    hash VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_order ON transactions(order_id);
CREATE INDEX idx_transactions_hash ON transactions(hash);

-- ==================== DEPOSITS ====================

CREATE TABLE IF NOT EXISTS deposits (
    deposit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    asset VARCHAR(20) NOT NULL,
    amount DECIMAL(40, 8) NOT NULL,
    tx_hash VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    confirmations INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_deposits_user ON deposits(user_id);
CREATE INDEX idx_deposits_hash ON deposits(tx_hash);

-- ==================== WITHDRAWALS ====================

CREATE TABLE IF NOT EXISTS withdrawals (
    withdrawal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    asset VARCHAR(20) NOT NULL,
    amount DECIMAL(40, 8) NOT NULL,
    address VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    tx_hash VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_withdrawals_user ON withdrawals(user_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);

-- ==================== BLOCKS (Blockchain) ====================

CREATE TABLE IF NOT EXISTS blocks (
    number BIGINT PRIMARY KEY,
    hash VARCHAR(100) UNIQUE NOT NULL,
    parent_hash VARCHAR(100) NOT NULL,
    validator VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    transactions INTEGER DEFAULT 0,
    gas_used BIGINT DEFAULT 0,
    extra_data TEXT
);

CREATE INDEX idx_blocks_hash ON blocks(hash);
CREATE INDEX idx_blocks_validator ON blocks(validator);

-- ==================== BLOCK ACCOUNTS ====================

CREATE TABLE IF NOT EXISTS block_accounts (
    address VARCHAR(100) PRIMARY KEY,
    balance DECIMAL(40, 8) DEFAULT 0,
    nonce BIGINT DEFAULT 0,
    code_hash VARCHAR(100),
    storage_root VARCHAR(100)
);

-- ==================== TOKENS ====================

CREATE TABLE IF NOT EXISTS tokens (
    chain VARCHAR(20) NOT NULL,
    address VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    decimals INTEGER NOT NULL,
    total_supply DECIMAL(40, 8),
    creator VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (chain, address)
);

CREATE INDEX idx_tokens_symbol ON tokens(symbol);

-- ==================== LIQUIDITY POOLS ====================

CREATE TABLE IF NOT EXISTS liquidity_pools (
    pool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_a VARCHAR(100) NOT NULL,
    token_b VARCHAR(100) NOT NULL,
    dex VARCHAR(50) NOT NULL,
    liquidity_a DECIMAL(40, 8) DEFAULT 0,
    liquidity_b DECIMAL(40, 8) DEFAULT 0,
    shares DECIMAL(40, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pools_tokens ON liquidity_pools(token_a, token_b);

-- ==================== TRIGGER FUNCTIONS ====================

-- Update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_users_updated
    BEFORE UPDATE ON users FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_accounts_updated
    BEFORE UPDATE ON accounts FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_orders_updated
    BEFORE UPDATE ON orders FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_liquidity_updated
    BEFORE UPDATE ON liquidity_pools FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();-- TigerEx Wallet API Tables
CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    address VARCHAR(42) UNIQUE NOT NULL,
    seed_phrase VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    ownership VARCHAR(50) DEFAULT 'USER_OWNS',
    chain VARCHAR(20) DEFAULT 'ETH',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE wallets(id INT PRIMARY KEY,address VARCHAR(50),seed_phrase TEXT,blockchain VARCHAR(20),ownership VARCHAR(20),user_id INT);
