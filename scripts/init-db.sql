-- TigerEx Database Initialization Script
-- This script creates the initial database schema for the TigerEx platform

-- Create databases
CREATE DATABASE IF NOT EXISTS tigerex;
CREATE DATABASE IF NOT EXISTS tigerex_test;
CREATE DATABASE IF NOT EXISTS tigerex_analytics;

-- Use main database
\c tigerex;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE user_role AS ENUM (
    'user', 'vip', 'institutional', 'affiliate', 'regional_partner',
    'super_admin', 'kyc_admin', 'customer_support', 'p2p_manager',
    'affiliate_manager', 'bdm', 'technical_team', 'listing_manager'
);

CREATE TYPE user_status AS ENUM ('active', 'suspended', 'banned', 'pending');
CREATE TYPE kyc_status AS ENUM ('pending', 'approved', 'rejected', 'required');
CREATE TYPE order_type AS ENUM ('market', 'limit', 'stop_loss', 'take_profit', 'oco', 'iceberg');
CREATE TYPE order_side AS ENUM ('buy', 'sell');
CREATE TYPE order_status AS ENUM ('pending', 'partial', 'filled', 'cancelled', 'rejected');
CREATE TYPE trade_type AS ENUM ('spot', 'margin', 'futures', 'options');
CREATE TYPE wallet_type AS ENUM ('hot', 'cold', 'custodial', 'non_custodial');
CREATE TYPE transaction_type AS ENUM ('deposit', 'withdrawal', 'trade', 'fee', 'reward', 'staking');
CREATE TYPE transaction_status AS ENUM ('pending', 'confirmed', 'failed', 'cancelled');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    country_code VARCHAR(3),
    date_of_birth DATE,
    role user_role DEFAULT 'user',
    status user_status DEFAULT 'pending',
    kyc_status kyc_status DEFAULT 'required',
    kyc_level INTEGER DEFAULT 0,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    security_settings JSONB DEFAULT '{}',
    trading_preferences JSONB DEFAULT '{}',
    referral_code VARCHAR(20) UNIQUE,
    referred_by UUID REFERENCES users(id),
    vip_level INTEGER DEFAULT 0,
    trading_volume_30d DECIMAL(20,8) DEFAULT 0,
    last_login_at TIMESTAMP,
    last_login_ip INET,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User devices table
CREATE TABLE user_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(100),
    device_type VARCHAR(50),
    device_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    is_trusted BOOLEAN DEFAULT FALSE,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Login history table
CREATE TABLE login_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cryptocurrencies table
CREATE TABLE cryptocurrencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    full_name VARCHAR(200),
    description TEXT,
    website VARCHAR(255),
    whitepaper VARCHAR(255),
    blockchain VARCHAR(50),
    contract_address VARCHAR(255),
    decimals INTEGER DEFAULT 18,
    total_supply DECIMAL(30,8),
    circulating_supply DECIMAL(30,8),
    market_cap DECIMAL(20,2),
    logo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_tradeable BOOLEAN DEFAULT TRUE,
    listing_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading pairs table
CREATE TABLE trading_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    quote_currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    min_order_size DECIMAL(20,8) DEFAULT 0.001,
    max_order_size DECIMAL(20,8),
    price_precision INTEGER DEFAULT 8,
    quantity_precision INTEGER DEFAULT 8,
    maker_fee DECIMAL(5,4) DEFAULT 0.001,
    taker_fee DECIMAL(5,4) DEFAULT 0.001,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_currency_id, quote_currency_id)
);

-- Wallets table
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    wallet_type wallet_type DEFAULT 'hot',
    address VARCHAR(255),
    private_key_encrypted TEXT,
    balance DECIMAL(30,8) DEFAULT 0,
    locked_balance DECIMAL(30,8) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, currency_id, wallet_type)
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    order_type order_type NOT NULL,
    side order_side NOT NULL,
    status order_status DEFAULT 'pending',
    trade_type trade_type DEFAULT 'spot',
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),
    stop_price DECIMAL(20,8),
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    remaining_quantity DECIMAL(20,8),
    average_price DECIMAL(20,8),
    total_value DECIMAL(20,8),
    fee DECIMAL(20,8) DEFAULT 0,
    fee_currency_id UUID REFERENCES cryptocurrencies(id),
    time_in_force VARCHAR(10) DEFAULT 'GTC',
    leverage DECIMAL(5,2) DEFAULT 1.0,
    margin_type VARCHAR(20),
    client_order_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP
);

-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    buyer_order_id UUID NOT NULL REFERENCES orders(id),
    seller_order_id UUID NOT NULL REFERENCES orders(id),
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID NOT NULL REFERENCES users(id),
    trade_type trade_type DEFAULT 'spot',
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    total_value DECIMAL(20,8) NOT NULL,
    buyer_fee DECIMAL(20,8) DEFAULT 0,
    seller_fee DECIMAL(20,8) DEFAULT 0,
    fee_currency_id UUID REFERENCES cryptocurrencies(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    transaction_type transaction_type NOT NULL,
    status transaction_status DEFAULT 'pending',
    amount DECIMAL(30,8) NOT NULL,
    fee DECIMAL(30,8) DEFAULT 0,
    from_address VARCHAR(255),
    to_address VARCHAR(255),
    tx_hash VARCHAR(255),
    block_number BIGINT,
    confirmations INTEGER DEFAULT 0,
    required_confirmations INTEGER DEFAULT 6,
    reference_id UUID,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Market data table
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trading_pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    open_price DECIMAL(20,8),
    high_price DECIMAL(20,8),
    low_price DECIMAL(20,8),
    close_price DECIMAL(20,8),
    volume DECIMAL(30,8),
    quote_volume DECIMAL(30,8),
    price_change DECIMAL(20,8),
    price_change_percent DECIMAL(8,4),
    weighted_avg_price DECIMAL(20,8),
    prev_close_price DECIMAL(20,8),
    last_price DECIMAL(20,8),
    bid_price DECIMAL(20,8),
    ask_price DECIMAL(20,8),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trading_pair_id, timestamp)
);

-- KYC documents table
CREATE TABLE kyc_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100),
    document_url VARCHAR(500),
    status kyc_status DEFAULT 'pending',
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP,
    rejection_reason TEXT,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- P2P orders table
CREATE TABLE p2p_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    fiat_currency VARCHAR(3) NOT NULL,
    order_type VARCHAR(10) NOT NULL, -- 'buy' or 'sell'
    status VARCHAR(20) DEFAULT 'active',
    quantity DECIMAL(20,8) NOT NULL,
    remaining_quantity DECIMAL(20,8),
    price DECIMAL(20,8) NOT NULL,
    min_amount DECIMAL(20,2),
    max_amount DECIMAL(20,2),
    payment_methods JSONB,
    terms TEXT,
    auto_reply TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- P2P trades table
CREATE TABLE p2p_trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES p2p_orders(id),
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID NOT NULL REFERENCES users(id),
    quantity DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    total_amount DECIMAL(20,2) NOT NULL,
    fiat_currency VARCHAR(3) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    payment_deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Staking pools table
CREATE TABLE staking_pools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    currency_id UUID NOT NULL REFERENCES cryptocurrencies(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    apy DECIMAL(8,4) NOT NULL,
    min_stake_amount DECIMAL(20,8),
    max_stake_amount DECIMAL(20,8),
    lock_period INTEGER, -- in days
    is_active BOOLEAN DEFAULT TRUE,
    total_staked DECIMAL(30,8) DEFAULT 0,
    max_pool_size DECIMAL(30,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User stakes table
CREATE TABLE user_stakes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    pool_id UUID NOT NULL REFERENCES staking_pools(id),
    amount DECIMAL(20,8) NOT NULL,
    rewards_earned DECIMAL(20,8) DEFAULT 0,
    last_reward_calculation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stake_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unlock_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System settings table
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_access_token ON user_sessions(access_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_trading_pair_id ON orders(trading_pair_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

CREATE INDEX idx_trades_trading_pair_id ON trades(trading_pair_id);
CREATE INDEX idx_trades_buyer_id ON trades(buyer_id);
CREATE INDEX idx_trades_seller_id ON trades(seller_id);
CREATE INDEX idx_trades_created_at ON trades(created_at);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_currency_id ON transactions(currency_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_currency_id ON wallets(currency_id);
CREATE INDEX idx_wallets_address ON wallets(address);

CREATE INDEX idx_market_data_trading_pair_id ON market_data(trading_pair_id);
CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);

CREATE INDEX idx_p2p_orders_user_id ON p2p_orders(user_id);
CREATE INDEX idx_p2p_orders_currency_id ON p2p_orders(currency_id);
CREATE INDEX idx_p2p_orders_status ON p2p_orders(status);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON user_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cryptocurrencies_updated_at BEFORE UPDATE ON cryptocurrencies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trading_pairs_updated_at BEFORE UPDATE ON trading_pairs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_wallets_updated_at BEFORE UPDATE ON wallets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kyc_documents_updated_at BEFORE UPDATE ON kyc_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_p2p_orders_updated_at BEFORE UPDATE ON p2p_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_p2p_trades_updated_at BEFORE UPDATE ON p2p_trades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_staking_pools_updated_at BEFORE UPDATE ON staking_pools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_stakes_updated_at BEFORE UPDATE ON user_stakes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial system settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
('platform_name', 'TigerEx', 'Platform name', true),
('platform_version', '1.0.0', 'Platform version', true),
('maintenance_mode', 'false', 'Maintenance mode flag', true),
('trading_enabled', 'true', 'Trading enabled flag', true),
('registration_enabled', 'true', 'Registration enabled flag', true),
('kyc_required', 'true', 'KYC requirement flag', true),
('min_withdrawal_amount', '0.001', 'Minimum withdrawal amount', true),
('max_withdrawal_amount', '100', 'Maximum withdrawal amount per day', true),
('withdrawal_fee_percentage', '0.1', 'Withdrawal fee percentage', true),
('trading_fee_percentage', '0.1', 'Default trading fee percentage', true),
('referral_bonus_percentage', '20', 'Referral bonus percentage', true),
('session_timeout_minutes', '30', 'Session timeout in minutes', false),
('max_login_attempts', '5', 'Maximum login attempts', false),
('account_lock_duration_minutes', '30', 'Account lock duration in minutes', false);

-- Insert initial cryptocurrencies
INSERT INTO cryptocurrencies (symbol, name, full_name, blockchain, decimals, is_active, is_tradeable) VALUES
('BTC', 'Bitcoin', 'Bitcoin', 'Bitcoin', 8, true, true),
('ETH', 'Ethereum', 'Ethereum', 'Ethereum', 18, true, true),
('USDT', 'Tether', 'Tether USD', 'Ethereum', 6, true, true),
('USDC', 'USD Coin', 'USD Coin', 'Ethereum', 6, true, true),
('BNB', 'BNB', 'Binance Coin', 'BSC', 18, true, true),
('ADA', 'Cardano', 'Cardano', 'Cardano', 6, true, true),
('SOL', 'Solana', 'Solana', 'Solana', 9, true, true),
('DOT', 'Polkadot', 'Polkadot', 'Polkadot', 10, true, true),
('MATIC', 'Polygon', 'Polygon', 'Polygon', 18, true, true),
('AVAX', 'Avalanche', 'Avalanche', 'Avalanche', 18, true, true);

-- Create initial trading pairs
WITH btc AS (SELECT id FROM cryptocurrencies WHERE symbol = 'BTC'),
     eth AS (SELECT id FROM cryptocurrencies WHERE symbol = 'ETH'),
     usdt AS (SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'),
     usdc AS (SELECT id FROM cryptocurrencies WHERE symbol = 'USDC'),
     bnb AS (SELECT id FROM cryptocurrencies WHERE symbol = 'BNB'),
     ada AS (SELECT id FROM cryptocurrencies WHERE symbol = 'ADA'),
     sol AS (SELECT id FROM cryptocurrencies WHERE symbol = 'SOL'),
     dot AS (SELECT id FROM cryptocurrencies WHERE symbol = 'DOT'),
     matic AS (SELECT id FROM cryptocurrencies WHERE symbol = 'MATIC'),
     avax AS (SELECT id FROM cryptocurrencies WHERE symbol = 'AVAX')

INSERT INTO trading_pairs (base_currency_id, quote_currency_id, symbol, min_order_size, price_precision, quantity_precision) VALUES
((SELECT id FROM btc), (SELECT id FROM usdt), 'BTCUSDT', 0.00001, 2, 5),
((SELECT id FROM btc), (SELECT id FROM usdc), 'BTCUSDC', 0.00001, 2, 5),
((SELECT id FROM eth), (SELECT id FROM usdt), 'ETHUSDT', 0.0001, 2, 4),
((SELECT id FROM eth), (SELECT id FROM usdc), 'ETHUSDC', 0.0001, 2, 4),
((SELECT id FROM eth), (SELECT id FROM btc), 'ETHBTC', 0.0001, 6, 4),
((SELECT id FROM bnb), (SELECT id FROM usdt), 'BNBUSDT', 0.01, 2, 2),
((SELECT id FROM ada), (SELECT id FROM usdt), 'ADAUSDT', 1, 4, 0),
((SELECT id FROM sol), (SELECT id FROM usdt), 'SOLUSDT', 0.01, 2, 2),
((SELECT id FROM dot), (SELECT id FROM usdt), 'DOTUSDT', 0.1, 3, 1),
((SELECT id FROM matic), (SELECT id FROM usdt), 'MATICUSDT', 1, 4, 0),
((SELECT id FROM avax), (SELECT id FROM usdt), 'AVAXUSDT', 0.01, 2, 2);

-- Create initial staking pools
WITH btc AS (SELECT id FROM cryptocurrencies WHERE symbol = 'BTC'),
     eth AS (SELECT id FROM cryptocurrencies WHERE symbol = 'ETH'),
     ada AS (SELECT id FROM cryptocurrencies WHERE symbol = 'ADA'),
     sol AS (SELECT id FROM cryptocurrencies WHERE symbol = 'SOL'),
     dot AS (SELECT id FROM cryptocurrencies WHERE symbol = 'DOT')

INSERT INTO staking_pools (currency_id, name, description, apy, min_stake_amount, lock_period, max_pool_size) VALUES
((SELECT id FROM eth), 'ETH Staking Pool', 'Ethereum 2.0 staking with competitive rewards', 5.5, 0.1, 30, 10000),
((SELECT id FROM ada), 'ADA Staking Pool', 'Cardano staking with flexible terms', 4.8, 10, 0, 1000000),
((SELECT id FROM sol), 'SOL Staking Pool', 'Solana staking with high yields', 7.2, 1, 7, 100000),
((SELECT id FROM dot), 'DOT Staking Pool', 'Polkadot staking with governance participation', 12.5, 1, 28, 50000);

COMMIT;