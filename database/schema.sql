-- TigerEx Complete Database Schema (MySQL)
-- Database: tigerex

-- ==================== USERS ====================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    kyc_status ENUM('none','pending','approved','rejected') DEFAULT 'none',
    kyc_level INT DEFAULT 0,
    email_verified BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    country VARCHAR(50),
    referral_code VARCHAR(20),
    referred_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==================== MARKETS ====================
CREATE TABLE IF NOT EXISTS markets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    price DECIMAL(20,8) DEFAULT 0,
    change_24h DECIMAL(10,4) DEFAULT 0,
    volume_24h DECIMAL(20,2) DEFAULT 0,
    high_24h DECIMAL(20,8) DEFAULT 0,
    low_24h DECIMAL(20,8) DEFAULT 0,
    status ENUM('active','suspended','delisted') DEFAULT 'active',
    min_order DECIMAL(20,8) DEFAULT 0,
    max_order DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== ORDERS ====================
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    type ENUM('limit','market','stop_limit') DEFAULT 'limit',
    amount DECIMAL(20,8) NOT NULL,
    price DECIMAL(20,8),
    filled DECIMAL(20,8) DEFAULT 0,
    status ENUM('pending','filled','partially_filled','cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP NULL
);

-- ==================== POSITIONS (FUTURES) ====================
CREATE TABLE IF NOT EXISTS positions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side ENUM('long','short') NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    leverage INT DEFAULT 1,
    entry_price DECIMAL(20,8),
    margin DECIMAL(20,8) NOT NULL,
    pnl DECIMAL(20,8) DEFAULT 0,
    status ENUM('open','closed') DEFAULT 'open',
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL
);

-- ==================== OPTIONS ====================
CREATE TABLE IF NOT EXISTS options_orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strike DECIMAL(20,8) NOT NULL,
    expiry DATE NOT NULL,
    type ENUM('call','put') NOT NULL,
    premium DECIMAL(20,8) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    status ENUM('open','exercised','expired') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== BALANCES ====================
CREATE TABLE IF NOT EXISTS balances (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    balance DECIMAL(20,8) DEFAULT 0,
    locked DECIMAL(20,8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id, currency)
);

-- ==================== TRANSACTIONS ====================
CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('deposit','withdraw','transfer','trade','fee') NOT NULL,
    currency VARCHAR(20) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    fee DECIMAL(20,8) DEFAULT 0,
    address VARCHAR(255),
    txid VARCHAR(255),
    status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL
);

-- ==================== P2P ====================
CREATE TABLE IF NOT EXISTS p2p_ads (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    side ENUM('buy','sell') NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    limits_min DECIMAL(20,2) NOT NULL,
    limits_max DECIMAL(20,2) NOT NULL,
    payment_methods TEXT,
    terms TEXT,
    status ENUM('active','paused','completed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== COPY TRADING ====================
CREATE TABLE IF NOT EXISTS copy_following (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    trader_id INT NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    status ENUM('active','paused') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== KYC ====================
CREATE TABLE IF NOT EXISTS kyc (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('individual','corporate') DEFAULT 'individual',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    document_type VARCHAR(50),
    document_id VARCHAR(100),
    document_front TEXT,
    document_back TEXT,
    selfie TEXT,
    status ENUM('pending','approved','rejected') DEFAULT 'pending',
    rejection_reason TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL
);

-- ==================== API KEYS ====================
CREATE TABLE IF NOT EXISTS api_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    key_name VARCHAR(100),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255),
    permissions TEXT,
    rate_limit INT DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== SESSIONS ====================
CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== STAKING ====================
CREATE TABLE IF NOT EXISTS staking (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    apy DECIMAL(10,4) NOT NULL,
    lock_period INT NOT NULL,
    start_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unlock_at TIMESTAMP,
    status ENUM('active','unlocked') DEFAULT 'active'
);

-- ==================== INDEXES ====================
CREATE INDEX idx_orders_user ON orders(user_id, created_at);
CREATE INDEX idx_orders_symbol ON orders(symbol, created_at);
CREATE INDEX idx_positions_user ON positions(user_id, status);
CREATE INDEX idx_transactions_user ON transactions(user_id, created_at);
CREATE INDEX idx_balances_user ON balances(user_id);

-- ==================== SAMPLE DATA ====================
INSERT INTO markets (symbol, name, price, change_24h, volume_24h, status) VALUES
('BTC/USDT','Bitcoin',42500.00,2.5,1250000000,'active'),
('ETH/USDT','Ethereum',2250.00,3.2,890000000,'active'),
('BNB/USDT','BNB',320.00,1.8,450000000,'active'),
('SOL/USDT','Solana',98.00,5.5,320000000,'active'),
('XRP/USDT','Ripple',0.62,-1.2,280000000,'active');

-- Demo: INSERT INTO users (email, username, password) VALUES ('demo@tigerex.com','demo','$2b$10$ hashed password here');
-- ==================== WALLETS (UPGRADED) ====================
-- User wallets with 24-word seed - FULL CONTROL
CREATE TABLE IF NOT EXISTS wallets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    wallet_id VARCHAR(50) UNIQUE NOT NULL,
    wallet_type ENUM('custodial','non_custodial') NOT NULL,
    chain VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    encrypted_key TEXT,
    seed_phrase TEXT,
    backup_key VARCHAR(100),
    ownership VARCHAR(20) DEFAULT 'USER_OWNS',
    full_control BOOLEAN DEFAULT TRUE,
    limitations VARCHAR(20) DEFAULT 'NONE',
    status ENUM('active','frozen') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_wallets (user_id),
    INDEX idx_wallet_address (address)
);

-- ==================== DEFI POSITIONS ====================
CREATE TABLE IF NOT EXISTS defi_positions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    wallet_id BIGINT NOT NULL,
    position_type ENUM('liquidity','staking','farming') NOT NULL,
    pool_id VARCHAR(50),
    token_a VARCHAR(20),
    token_b VARCHAR(20),
    amount_a DECIMAL(30,8) DEFAULT 0,
    amount_b DECIMAL(30,8) DEFAULT 0,
    lp_tokens DECIMAL(30,8) DEFAULT 0,
    apy DECIMAL(10,4) DEFAULT 0,
    status ENUM('active','removed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_defi (user_id)
);

-- ==================== ADMIN GAS FEES ====================
CREATE TABLE IF NOT EXISTS gas_fees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain VARCHAR(20) NOT NULL,
    tx_type VARCHAR(20) NOT NULL,
    fee DECIMAL(20,8) DEFAULT 0.001,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (chain, tx_type)
);

-- ==================== MULTI-CHAIN SUPPORT ====================
CREATE TABLE IF NOT EXISTS chains (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    chain_type ENUM('evm','non_evm') DEFAULT 'evm',
    rpc_url TEXT,
    explorer_url TEXT,
    status ENUM('active','inactive') DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain VARCHAR(20) NOT NULL,
    contract_address VARCHAR(255),
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    decimals INT DEFAULT 18,
    is_native BOOLEAN DEFAULT FALSE,
    status ENUM('active','inactive') DEFAULT 'active',
    UNIQUE KEY (chain, contract_address)
);

-- Insert default gas fees
INSERT INTO gas_fees (chain, tx_type, fee) VALUES 
('ethereum', 'send', 0.001),
('ethereum', 'swap', 0.002),
('ethereum', 'create_token', 0.01),
('bsc', 'send', 0.0005),
('bsc', 'swap', 0.001),
('bsc', 'create_token', 0.005),
('polygon', 'send', 0.0001),
('polygon', 'swap', 0.0002),
('polygon', 'create_token', 0.002);

-- Insert default chains
INSERT INTO chains (chain_id, name, symbol, chain_type, status) VALUES 
('ethereum', 'Ethereum', 'ETH', 'evm', 'active'),
('bsc', 'BNB Chain', 'BNB', 'evm', 'active'),
('polygon', 'Polygon', 'MATIC', 'evm', 'active'),
('avalanche', 'Avalanche', 'AVAX', 'evm', 'active'),
('arbitrum', 'Arbitrum', 'ETH', 'evm', 'active'),
('solana', 'Solana', 'SOL', 'non_evm', 'active');
