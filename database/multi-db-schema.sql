-- =====================================================
-- TigerEx Multi-Database Architecture
-- High-Performance Exchange Databases
-- PostgreSQL + MongoDB + Redis + TimescaleDB
-- =====================================================

-- =====================================================
-- POSTGRESQL SCHEMA (Primary Database)
-- =====================================================

-- Users Table with Roles
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user','sub_admin','admin','super_admin')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active','suspended','banned','liquidated')),
    kyc_level INT DEFAULT 0,
    kyc_status VARCHAR(20) DEFAULT 'none',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    twofa_enabled BOOLEAN DEFAULT FALSE,
    twofa_secret VARCHAR(255),
    country VARCHAR(50),
    referral_code VARCHAR(20) UNIQUE,
    referred_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral ON users(referral_code);

-- Markets Table
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_asset VARCHAR(20) NOT NULL,
    quote_asset VARCHAR(20) NOT NULL,
    market_type VARCHAR(20) DEFAULT 'spot',
    status VARCHAR(20) DEFAULT 'trading',
    price DECIMAL(20,8) DEFAULT 0,
    price_change_24h DECIMAL(12,4) DEFAULT 0,
    volume_24h DECIMAL(30,8) DEFAULT 0,
    high_24h DECIMAL(20,8) DEFAULT 0,
    low_24h DECIMAL(20,8) DEFAULT 0,
    max_leverage INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table (Optimized for High Frequency)
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    side VARCHAR(10) CHECK (side IN ('buy','sell')),
    order_type VARCHAR(20) DEFAULT 'limit',
    price DECIMAL(20,8),
    quantity DECIMAL(20,8) NOT NULL,
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    avg_fill_price DECIMAL(20,8) DEFAULT 0,
    commission DECIMAL(20,8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    time_in_force VARCHAR(10) DEFAULT 'GTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for orders
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Trades Table
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    trade_id VARCHAR(50) UNIQUE NOT NULL,
    side VARCHAR(10),
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    commission DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_market ON trades(market_id, created_at);
CREATE INDEX idx_trades_user ON trades(user_id, created_at);

-- Positions Table
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    market_id INT NOT NULL,
    position_id VARCHAR(50) UNIQUE NOT NULL,
    position_side VARCHAR(10),
    quantity DECIMAL(20,8) DEFAULT 0,
    entry_price DECIMAL(20,8) DEFAULT 0,
    leverage INT DEFAULT 1,
    margin DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- Accounts (Multi-currency)
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    currency VARCHAR(20) NOT NULL,
    account_type VARCHAR(20) DEFAULT 'spot',
    balance DECIMAL(30,8) DEFAULT 0,
    available_balance DECIMAL(30,8) DEFAULT 0,
    locked_balance DECIMAL(30,8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, currency, account_type)
);

-- Transactions
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    tx_id VARCHAR(100) UNIQUE NOT NULL,
    tx_type VARCHAR(20) CHECK (tx_type IN ('deposit','withdraw','transfer','trade','fee')),
    currency VARCHAR(20) NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    fee DECIMAL(30,8) DEFAULT 0,
    address_from VARCHAR(255),
    address_to VARCHAR(255),
    tx_hash VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Fee Tiers
CREATE TABLE fee_tiers (
    id SERIAL PRIMARY KEY,
    tier_name VARCHAR(20),
    maker_fee DECIMAL(10,6) DEFAULT 0,
    taker_fee DECIMAL(10,6) DEFAULT 0,
    min_volume_30d DECIMAL(30,2) DEFAULT 0
);

-- API Keys
CREATE TABLE api_keys (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255),
    permissions JSONB,
    ip_whitelist TEXT[],
    rate_limit INT DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Audit Logs
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KYC Applications
CREATE TABLE kyc_applications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    kyc_type VARCHAR(20) DEFAULT 'individual',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    document_type VARCHAR(50),
    document_id VARCHAR(100),
    documents JSONB,
    selfie TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    reject_reason TEXT,
    reviewer_id BIGINT,
    reviewed_at TIMESTAMP,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- POSTGRESQL FUNCTIONS (Security)
-- =====================================================

-- Secure password hashing
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
    SELECT crypt(password, gen_salt('bf', 12));
$$ LANGUAGE plpgsql;

-- Verify password
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
    SELECT password = hash;
$$ LANGUAGE plpgsql;

-- Generate API key
CREATE OR REPLACE FUNCTION generate_api_key()
RETURNS TEXT AS $$
    SELECT encode(gen_random_bytes(32), 'hex');
$$ LANGUAGE plpgsql;

-- Row-level security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_select ON users FOR SELECT
    USING (id = current_setting('app.user_id')::BIGINT OR current_setting('app.role') IN ('admin','super_admin'));

CREATE POLICY orders_select ON orders FOR SELECT
    USING (user_id = current_setting('app.user_id')::BIGINT OR current_setting('app.role') IN ('admin','super_admin'));

-- =====================================================
-- REDIS CONFIGURATION (Caching & Session)
-- =====================================================

-- Redis Keys Structure:
-- user:{id}:session     - User session data
-- user:{id}:balance     - Cached balance
-- market:{symbol}:price - Current price cache
-- market:{symbol}:depth - Order book cache
-- order:{id}           - Order cache
-- rate:{user}:{ip}     - Rate limiting

-- Config (redis.conf):
# Redis Configuration for High Performance
bind 127.0.0.1
port 6379
protected-mode yes
timeout 0
tcp-keepalive 300
daemonize no

# Memory & Persistence
maxmemory 64gb
maxmemory-policy allkeys-lru
maxclients 100000

# Persistence
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Replication
replica-read-only yes
repl-diskless-sync yes

# Security
requirepass your_redis_password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Lua Scripting
maxmemory 8mb
maxmemory-samples 5

# Cluster
cluster-enabled yes
cluster-config-file nodes.conf

-- =====================================================
-- MONGODB COLLECTIONS (Document Store)
-- =====================================================

// MongoDB Collections

// Support Tickets
db.createCollection("support_tickets", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "subject", "status"],
            properties: {
                user_id: { bsonType: "int" },
                subject: { bsonType: "string" },
                status: { enum: ["open", "pending", "resolved", "closed"] },
                priority: { enum: ["low", "medium", "high", "urgent"] }
            }
        }
    }
})

// P2P Orders
db.createCollection("p2p_orders", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["ad_id", "buyer_id", "seller_id", "amount", "status"],
            properties: {
                ad_id: { bsonType: "int" },
                buyer_id: { bsonType: "int" },
                seller_id: { bsonType: "int" },
                amount: { bsonType: "decimal" },
                price: { bsonType: "decimal" },
                status: { enum: ["pending","paid","released","disputed","cancelled"] }
            }
        }
    }
})

// Notifications
db.createCollection("notifications", {
    capped: true,
    size: 104857600,
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "type"],
            properties: {
                user_id: { bsonType: "int" },
                type: { enum: ["trade","deposit","withdraw","system","kyc"] },
                title: { bsonType: "string" },
                message: { bsonType: "string" },
                read: { bsonType: "bool" }
            }
        }
    }
})

// KYC Documents (Large files)
db.createCollection("kyc_documents", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["application_id", "file_type"],
            properties: {
                application_id: { bsonType: "string" },
                file_type: { enum: ["id_front","id_back","selfie","proof"] },
                file_data: { bsonType: "binData" },
                uploaded_at: { bsonType: "date" }
            }
        }
    }
})

// Indexes for collections
db.support_tickets.createIndex({ user_id: 1, status: 1 })
db.support_tickets.createIndex({ status: 1, created_at: -1 })
db.p2p_orders.createIndex({ ad_id: 1 })
db.notifications.createIndex({ user_id: 1, read: 1 })
db.notifications.createIndex({ created_at: -1 })

// =====================================================
-- TIMESERIES EXTENSION (Market Data)
-- =====================================================

-- Install TimescaleDB
-- CREATE EXTENSION timescaledb;

-- Market Ticks (High-frequency)
CREATE TABLE market_ticks (
    time TIMESTAMPTZ NOT NULL,
    market_id INT NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) DEFAULT 0
);

SELECT create_hypertable('market_ticks', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Compress old data
ALTER TABLE market_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'market_id'
);

-- Add compression policy
SELECT add_compression_policy('market_ticks',
    compress_after => INTERVAL '7 days'
);

-- OHLCV Data (Aggregated)
CREATE TABLE ohlcv_1m (
    time TIMESTAMPTZ NOT NULL,
    market_id INT NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) DEFAULT 0,
    UNIQUE(time, market_id)
);

SELECT create_hypertable('ohlcv_1m', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- =====================================================
-- CONNECTION STRINGS
-- =====================================================

# PostgreSQL
DATABASE_URL=postgresql://tigerex:password@localhost:5432/tigerex

# MongoDB
MONGODB_URL=mongodb://tigerex:password@localhost:27017/tigerex

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# TimescaleDB (optional)
TIMESCALE_URL=postgresql://tigerex:password@localhost:5432/tigerex_timeseries