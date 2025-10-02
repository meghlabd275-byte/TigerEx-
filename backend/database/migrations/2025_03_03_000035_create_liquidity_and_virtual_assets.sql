-- Liquidity Pools and Virtual Assets Management
-- TigerEx Advanced Liquidity System

-- Virtual Asset Reserves Table
CREATE TABLE virtual_asset_reserves (
    id SERIAL PRIMARY KEY,
    reserve_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Asset Information
    asset_symbol VARCHAR(10) NOT NULL, -- USDT, USDC, ETH, BTC, etc.
    asset_name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) NOT NULL, -- stablecoin, crypto, fiat
    
    -- Reserve Amounts
    total_reserve DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (total_reserve >= 0),
    available_reserve DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (available_reserve >= 0),
    locked_reserve DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (locked_reserve >= 0),
    allocated_to_pools DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (allocated_to_pools >= 0),
    
    -- Virtual vs Real
    is_virtual BOOLEAN DEFAULT TRUE,
    backing_ratio DECIMAL(5,4) DEFAULT 1.0000, -- 1.0 = 100% backed
    real_asset_backing DECIMAL(30,8) DEFAULT 0,
    
    -- Risk Management
    max_allocation_per_pool DECIMAL(30,8) NOT NULL,
    min_reserve_threshold DECIMAL(30,8) NOT NULL,
    rebalance_threshold DECIMAL(5,4) DEFAULT 0.1000, -- 10%
    
    -- Performance Metrics
    total_volume_provided DECIMAL(40,8) DEFAULT 0,
    total_fees_earned DECIMAL(30,8) DEFAULT 0,
    utilization_rate DECIMAL(5,4) DEFAULT 0, -- 0-1
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    auto_rebalance_enabled BOOLEAN DEFAULT TRUE,
    
    -- Audit
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_rebalanced_at TIMESTAMP
);

-- Liquidity Pools Table
CREATE TABLE liquidity_pools (
    id SERIAL PRIMARY KEY,
    pool_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Pool Information
    pool_name VARCHAR(100) NOT NULL,
    pool_type VARCHAR(20) NOT NULL, -- amm, orderbook, hybrid
    
    -- Trading Pair
    base_asset VARCHAR(10) NOT NULL,
    quote_asset VARCHAR(10) NOT NULL,
    trading_pair VARCHAR(20) NOT NULL,
    
    -- Liquidity Amounts
    base_reserve DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (base_reserve >= 0),
    quote_reserve DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (quote_reserve >= 0),
    total_liquidity_usd DECIMAL(30,8) DEFAULT 0,
    
    -- Virtual Liquidity
    virtual_base_liquidity DECIMAL(30,8) DEFAULT 0,
    virtual_quote_liquidity DECIMAL(30,8) DEFAULT 0,
    virtual_liquidity_percentage DECIMAL(5,4) DEFAULT 0, -- 0-1
    
    -- AMM Parameters
    fee_rate DECIMAL(6,4) DEFAULT 0.003, -- 0.3%
    protocol_fee_rate DECIMAL(6,4) DEFAULT 0.0005, -- 0.05%
    slippage_tolerance DECIMAL(6,4) DEFAULT 0.01, -- 1%
    
    -- Price Information
    current_price DECIMAL(20,8),
    price_impact_threshold DECIMAL(6,4) DEFAULT 0.05, -- 5%
    
    -- Pool Metrics
    total_volume_24h DECIMAL(40,8) DEFAULT 0,
    total_trades_24h BIGINT DEFAULT 0,
    total_fees_24h DECIMAL(30,8) DEFAULT 0,
    apr DECIMAL(8,4) DEFAULT 0, -- Annual Percentage Rate
    
    -- Liquidity Provider Count
    total_lp_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Audit
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Liquidity Provider Positions Table
CREATE TABLE liquidity_provider_positions (
    id SERIAL PRIMARY KEY,
    position_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Provider Information
    user_id BIGINT REFERENCES users(id),
    pool_id INTEGER REFERENCES liquidity_pools(id),
    
    -- Position Details
    base_amount DECIMAL(30,8) NOT NULL CHECK (base_amount >= 0),
    quote_amount DECIMAL(30,8) NOT NULL CHECK (quote_amount >= 0),
    lp_tokens DECIMAL(30,8) NOT NULL CHECK (lp_tokens >= 0),
    
    -- Entry Information
    entry_price DECIMAL(20,8) NOT NULL,
    entry_value_usd DECIMAL(30,8) NOT NULL,
    
    -- Current Value
    current_value_usd DECIMAL(30,8) DEFAULT 0,
    impermanent_loss DECIMAL(30,8) DEFAULT 0,
    
    -- Earnings
    fees_earned DECIMAL(30,8) DEFAULT 0,
    rewards_earned DECIMAL(30,8) DEFAULT 0,
    total_earnings DECIMAL(30,8) DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at TIMESTAMP
);

-- IOU Tokens Table
CREATE TABLE iou_tokens (
    id SERIAL PRIMARY KEY,
    iou_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Token Information
    token_symbol VARCHAR(10) NOT NULL,
    token_name VARCHAR(100) NOT NULL,
    underlying_asset VARCHAR(10) NOT NULL,
    
    -- IOU Details
    total_supply DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (total_supply >= 0),
    circulating_supply DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (circulating_supply >= 0),
    
    -- Conversion
    conversion_ratio DECIMAL(20,8) DEFAULT 1.0, -- 1 IOU = X real tokens
    is_convertible BOOLEAN DEFAULT FALSE,
    conversion_start_date TIMESTAMP,
    conversion_end_date TIMESTAMP,
    
    -- Backing
    backing_amount DECIMAL(30,8) DEFAULT 0,
    backing_percentage DECIMAL(5,4) DEFAULT 0, -- 0-1
    
    -- Trading
    is_tradable BOOLEAN DEFAULT TRUE,
    current_price DECIMAL(20,8),
    market_cap_usd DECIMAL(40,8) DEFAULT 0,
    
    -- Liquidity
    has_liquidity_pool BOOLEAN DEFAULT FALSE,
    liquidity_pool_id INTEGER REFERENCES liquidity_pools(id),
    virtual_liquidity_provided DECIMAL(30,8) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, converting, converted, expired
    
    -- Metadata
    description TEXT,
    launch_date TIMESTAMP,
    expiry_date TIMESTAMP,
    
    -- Audit
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IOU Token Holdings Table
CREATE TABLE iou_token_holdings (
    id SERIAL PRIMARY KEY,
    holding_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Holder Information
    user_id BIGINT REFERENCES users(id),
    iou_token_id INTEGER REFERENCES iou_tokens(id),
    
    -- Holdings
    balance DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    locked_balance DECIMAL(30,8) NOT NULL DEFAULT 0 CHECK (locked_balance >= 0),
    
    -- Conversion Tracking
    converted_amount DECIMAL(30,8) DEFAULT 0,
    pending_conversion DECIMAL(30,8) DEFAULT 0,
    
    -- Acquisition
    avg_acquisition_price DECIMAL(20,8),
    total_invested_usd DECIMAL(30,8) DEFAULT 0,
    
    -- Earnings
    trading_profit DECIMAL(30,8) DEFAULT 0,
    
    -- Timestamps
    first_acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Virtual Liquidity Allocations Table
CREATE TABLE virtual_liquidity_allocations (
    id SERIAL PRIMARY KEY,
    allocation_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Source
    reserve_id INTEGER REFERENCES virtual_asset_reserves(id),
    pool_id INTEGER REFERENCES liquidity_pools(id),
    
    -- Allocation Details
    allocated_amount DECIMAL(30,8) NOT NULL CHECK (allocated_amount >= 0),
    asset_symbol VARCHAR(10) NOT NULL,
    
    -- Performance
    fees_generated DECIMAL(30,8) DEFAULT 0,
    volume_facilitated DECIMAL(40,8) DEFAULT 0,
    trades_facilitated BIGINT DEFAULT 0,
    
    -- Risk Metrics
    utilization_rate DECIMAL(5,4) DEFAULT 0,
    impermanent_loss DECIMAL(30,8) DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deallocated_at TIMESTAMP
);

-- Reserve Rebalancing History Table
CREATE TABLE reserve_rebalancing_history (
    id SERIAL PRIMARY KEY,
    rebalance_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Reserve Information
    reserve_id INTEGER REFERENCES virtual_asset_reserves(id),
    
    -- Rebalancing Details
    rebalance_type VARCHAR(20) NOT NULL, -- automatic, manual, emergency
    trigger_reason TEXT,
    
    -- Before State
    before_total_reserve DECIMAL(30,8) NOT NULL,
    before_available DECIMAL(30,8) NOT NULL,
    before_allocated DECIMAL(30,8) NOT NULL,
    
    -- After State
    after_total_reserve DECIMAL(30,8) NOT NULL,
    after_available DECIMAL(30,8) NOT NULL,
    after_allocated DECIMAL(30,8) NOT NULL,
    
    -- Changes
    amount_added DECIMAL(30,8) DEFAULT 0,
    amount_removed DECIMAL(30,8) DEFAULT 0,
    
    -- Audit
    executed_by VARCHAR(50) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    notes TEXT
);

-- Liquidity Pool Transactions Table
CREATE TABLE liquidity_pool_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Pool Information
    pool_id INTEGER REFERENCES liquidity_pools(id),
    user_id BIGINT REFERENCES users(id),
    
    -- Transaction Type
    transaction_type VARCHAR(20) NOT NULL, -- add_liquidity, remove_liquidity, swap
    
    -- Amounts
    base_amount DECIMAL(30,8) DEFAULT 0,
    quote_amount DECIMAL(30,8) DEFAULT 0,
    lp_tokens_amount DECIMAL(30,8) DEFAULT 0,
    
    -- Swap Details (if applicable)
    token_in VARCHAR(10),
    token_out VARCHAR(10),
    amount_in DECIMAL(30,8),
    amount_out DECIMAL(30,8),
    
    -- Fees
    fee_amount DECIMAL(30,8) DEFAULT 0,
    fee_asset VARCHAR(10),
    
    -- Price Impact
    price_before DECIMAL(20,8),
    price_after DECIMAL(20,8),
    price_impact DECIMAL(6,4),
    
    -- Virtual Liquidity Used
    virtual_liquidity_used BOOLEAN DEFAULT FALSE,
    virtual_amount DECIMAL(30,8) DEFAULT 0,
    
    -- Transaction Hash (if on-chain)
    tx_hash VARCHAR(100),
    block_number BIGINT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'completed', -- pending, completed, failed
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_virtual_asset_reserves_asset_symbol ON virtual_asset_reserves(asset_symbol);
CREATE INDEX idx_virtual_asset_reserves_is_active ON virtual_asset_reserves(is_active);
CREATE INDEX idx_liquidity_pools_trading_pair ON liquidity_pools(trading_pair);
CREATE INDEX idx_liquidity_pools_is_active ON liquidity_pools(is_active);
CREATE INDEX idx_liquidity_provider_positions_user_id ON liquidity_provider_positions(user_id);
CREATE INDEX idx_liquidity_provider_positions_pool_id ON liquidity_provider_positions(pool_id);
CREATE INDEX idx_iou_tokens_token_symbol ON iou_tokens(token_symbol);
CREATE INDEX idx_iou_tokens_status ON iou_tokens(status);
CREATE INDEX idx_iou_token_holdings_user_id ON iou_token_holdings(user_id);
CREATE INDEX idx_iou_token_holdings_iou_token_id ON iou_token_holdings(iou_token_id);
CREATE INDEX idx_virtual_liquidity_allocations_reserve_id ON virtual_liquidity_allocations(reserve_id);
CREATE INDEX idx_virtual_liquidity_allocations_pool_id ON virtual_liquidity_allocations(pool_id);
CREATE INDEX idx_reserve_rebalancing_history_reserve_id ON reserve_rebalancing_history(reserve_id);
CREATE INDEX idx_liquidity_pool_transactions_pool_id ON liquidity_pool_transactions(pool_id);
CREATE INDEX idx_liquidity_pool_transactions_user_id ON liquidity_pool_transactions(user_id);
CREATE INDEX idx_liquidity_pool_transactions_created_at ON liquidity_pool_transactions(created_at);

-- Update Triggers
CREATE TRIGGER update_virtual_asset_reserves_updated_at 
    BEFORE UPDATE ON virtual_asset_reserves 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_liquidity_pools_updated_at 
    BEFORE UPDATE ON liquidity_pools 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_liquidity_provider_positions_updated_at 
    BEFORE UPDATE ON liquidity_provider_positions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_iou_tokens_updated_at 
    BEFORE UPDATE ON iou_tokens 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_iou_token_holdings_updated_at 
    BEFORE UPDATE ON iou_token_holdings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_virtual_liquidity_allocations_updated_at 
    BEFORE UPDATE ON virtual_liquidity_allocations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;