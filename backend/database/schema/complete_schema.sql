-- TigerEx Complete Database Schema
-- Version: 2.0.0

-- ============================================================================
-- USERS AND AUTHENTICATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'banned', 'deleted')),
    
    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    country VARCHAR(2),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Security
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    anti_phishing_code VARCHAR(50),
    
    -- KYC
    kyc_status VARCHAR(20) DEFAULT 'pending' CHECK (kyc_status IN ('pending', 'submitted', 'under_review', 'approved', 'rejected')),
    kyc_level INTEGER DEFAULT 0,
    kyc_submitted_at TIMESTAMP,
    kyc_approved_at TIMESTAMP,
    
    -- VIP
    vip_level INTEGER DEFAULT 0,
    vip_expires_at TIMESTAMP,
    
    -- Referral
    referral_code VARCHAR(20) UNIQUE,
    referred_by UUID REFERENCES users(id),
    
    -- Timestamps
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Suspension/Ban info
    suspension_reason TEXT,
    suspended_until TIMESTAMP,
    suspended_at TIMESTAMP,
    suspended_by UUID,
    ban_reason TEXT,
    banned_at TIMESTAMP,
    banned_by UUID,
    unsuspended_at TIMESTAMP,
    unsuspended_by UUID
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_referral_code ON users(referral_code);

-- Social Accounts
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('google', 'facebook', 'twitter', 'telegram', 'discord', 'apple', 'github', 'linkedin')),
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_name VARCHAR(255),
    provider_picture VARCHAR(500),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_social_accounts_user ON social_accounts(user_id);
CREATE INDEX idx_social_accounts_provider ON social_accounts(provider, provider_user_id);

-- ============================================================================
-- WALLETS AND BALANCES
-- ============================================================================

CREATE TABLE IF NOT EXISTS wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    wallet_type VARCHAR(20) NOT NULL CHECK (wallet_type IN ('spot', 'margin', 'futures', 'funding', 'earn', 'options')),
    address VARCHAR(255),
    derivation_path VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, wallet_type)
);

CREATE TABLE IF NOT EXISTS balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    wallet_id UUID REFERENCES wallets(id),
    asset VARCHAR(20) NOT NULL,
    available DECIMAL(38, 18) DEFAULT 0,
    frozen DECIMAL(38, 18) DEFAULT 0,
    total DECIMAL(38, 18) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, asset, wallet_id)
);

CREATE INDEX idx_balances_user ON balances(user_id);
CREATE INDEX idx_balances_asset ON balances(asset);

-- ============================================================================
-- TRADING PAIRS AND MARKETS
-- ============================================================================

CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('crypto', 'fiat', 'nft', 'token', 'iou')),
    blockchain_id UUID,
    contract_address VARCHAR(255),
    decimals INTEGER DEFAULT 8,
    total_supply DECIMAL(38, 18),
    circulating_supply DECIMAL(38, 18),
    logo_url VARCHAR(500),
    website VARCHAR(500),
    description TEXT,
    is_listed BOOLEAN DEFAULT TRUE,
    is_tradable BOOLEAN DEFAULT TRUE,
    is_deposit_enabled BOOLEAN DEFAULT TRUE,
    is_withdraw_enabled BOOLEAN DEFAULT TRUE,
    min_deposit DECIMAL(38, 18) DEFAULT 0,
    min_withdraw DECIMAL(38, 18) DEFAULT 0,
    withdraw_fee DECIMAL(38, 18) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trading_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_asset_id UUID REFERENCES assets(id),
    quote_asset_id UUID REFERENCES assets(id),
    trading_type VARCHAR(20) NOT NULL CHECK (trading_type IN ('spot', 'futures', 'margin', 'options', 'etf')),
    
    -- Trading parameters
    min_order_size DECIMAL(38, 18) NOT NULL,
    max_order_size DECIMAL(38, 18),
    min_price DECIMAL(38, 18) NOT NULL,
    max_price DECIMAL(38, 18),
    price_precision INTEGER DEFAULT 8,
    quantity_precision INTEGER DEFAULT 8,
    
    -- Fees
    maker_fee DECIMAL(10, 6) DEFAULT 0.001,
    taker_fee DECIMAL(10, 6) DEFAULT 0.001,
    
    -- Futures specific
    contract_size DECIMAL(38, 18),
    leverage_max INTEGER DEFAULT 100,
    margin_asset_id UUID REFERENCES assets(id),
    settlement_time TIMESTAMP,
    funding_rate_interval INTEGER DEFAULT 480, -- minutes
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'halted', 'delisted')),
    listed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trading_pairs_symbol ON trading_pairs(symbol);
CREATE INDEX idx_trading_pairs_base ON trading_pairs(base_asset_id);
CREATE INDEX idx_trading_pairs_quote ON trading_pairs(quote_asset_id);

-- ============================================================================
-- ORDERS
-- ============================================================================

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    trading_pair_id UUID REFERENCES trading_pairs(id),
    
    -- Order details
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit', 'stop_market', 'stop_limit', 'trailing_stop', 'iceberg', 'twap', 'vwap', 'oco', 'bracket')),
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    position_side VARCHAR(10) CHECK (position_side IN ('long', 'short', 'both')),
    
    -- Price and quantity
    price DECIMAL(38, 18),
    trigger_price DECIMAL(38, 18),
    quantity DECIMAL(38, 18) NOT NULL,
    filled_quantity DECIMAL(38, 18) DEFAULT 0,
    avg_fill_price DECIMAL(38, 18) DEFAULT 0,
    
    -- Iceberg/TWAP
    display_quantity DECIMAL(38, 18),
    hidden_quantity DECIMAL(38, 18),
    
    -- Stop/Limit
    stop_price DECIMAL(38, 18),
    stop_trigger VARCHAR(20) CHECK (stop_trigger IN ('mark', 'last', 'index')),
    
    -- Trailing stop
    trailing_percent DECIMAL(10, 6),
    trailing_amount DECIMAL(38, 18),
    
    -- Time in force
    time_in_force VARCHAR(10) DEFAULT 'GTC' CHECK (time_in_force IN ('GTC', 'IOC', 'FOK', 'GTX', 'GTD')),
    expire_at TIMESTAMP,
    
    -- Fees
    maker_fee DECIMAL(38, 18) DEFAULT 0,
    taker_fee DECIMAL(38, 18) DEFAULT 0,
    total_fee DECIMAL(38, 18) DEFAULT 0,
    fee_asset VARCHAR(20),
    
    -- Margin
    margin_used DECIMAL(38, 18),
    leverage INTEGER DEFAULT 1,
    margin_mode VARCHAR(20) CHECK (margin_mode IN ('cross', 'isolated')),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'partially_filled', 'filled', 'cancelled', 'rejected', 'expired')),
    reject_reason TEXT,
    
    -- Admin control
    is_admin_cancelled BOOLEAN DEFAULT FALSE,
    cancelled_by UUID,
    cancelled_at TIMESTAMP,
    cancel_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_pair ON orders(trading_pair_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);

-- ============================================================================
-- POSITIONS (Futures/Margin)
-- ============================================================================

CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    trading_pair_id UUID REFERENCES trading_pairs(id),
    
    -- Position details
    position_side VARCHAR(10) NOT NULL CHECK (position_side IN ('long', 'short')),
    quantity DECIMAL(38, 18) NOT NULL,
    entry_price DECIMAL(38, 18) NOT NULL,
    mark_price DECIMAL(38, 18),
    liquidation_price DECIMAL(38, 18),
    
    -- Margin
    margin DECIMAL(38, 18) NOT NULL,
    margin_mode VARCHAR(20) CHECK (margin_mode IN ('cross', 'isolated')),
    leverage INTEGER DEFAULT 1,
    
    -- PnL
    unrealized_pnl DECIMAL(38, 18) DEFAULT 0,
    realized_pnl DECIMAL(38, 18) DEFAULT 0,
    total_funding_fee DECIMAL(38, 18) DEFAULT 0,
    
    -- TP/SL
    take_profit_price DECIMAL(38, 18),
    stop_loss_price DECIMAL(38, 18),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'liquidated')),
    
    -- Closing info
    closed_at TIMESTAMP,
    closed_by UUID,
    close_reason VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_user ON positions(user_id);
CREATE INDEX idx_positions_pair ON positions(trading_pair_id);
CREATE INDEX idx_positions_status ON positions(status);

-- ============================================================================
-- TRANSACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(30) NOT NULL CHECK (type IN (
        'deposit', 'withdrawal', 'transfer', 'trade', 'fee', 'funding_fee', 
        'liquidation_fee', 'interest', 'rebate', 'referral_bonus', 
        'airdrop', 'staking_reward', 'admin_adjustment'
    )),
    
    -- Asset and amount
    asset VARCHAR(20) NOT NULL,
    amount DECIMAL(38, 18) NOT NULL,
    fee DECIMAL(38, 18) DEFAULT 0,
    net_amount DECIMAL(38, 18) NOT NULL,
    
    -- Reference
    reference_id UUID,
    reference_type VARCHAR(50),
    
    -- Blockchain info
    tx_hash VARCHAR(255),
    block_number BIGINT,
    from_address VARCHAR(255),
    to_address VARCHAR(255),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    
    -- Admin approval
    approved_by UUID,
    approved_at TIMESTAMP,
    rejected_by UUID,
    rejected_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Description
    description TEXT,
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_tx_hash ON transactions(tx_hash);

-- ============================================================================
-- KYC VERIFICATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    document_type VARCHAR(30) NOT NULL CHECK (document_type IN (
        'passport', 'national_id', 'drivers_license', 'utility_bill', 
        'bank_statement', 'selfie', 'tax_document'
    )),
    document_number VARCHAR(100),
    issuing_country VARCHAR(2),
    issue_date DATE,
    expiry_date DATE,
    
    -- Files
    front_image_url VARCHAR(500),
    back_image_url VARCHAR(500),
    selfie_image_url VARCHAR(500),
    
    -- OCR data
    extracted_data JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'under_review', 'approved', 'rejected')),
    rejection_reason TEXT,
    
    -- Admin review
    reviewed_by UUID,
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_documents_user ON kyc_documents(user_id);
CREATE INDEX idx_kyc_documents_status ON kyc_documents(status);

-- ============================================================================
-- ADMIN AND RBAC
-- ============================================================================

CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) NOT NULL CHECK (role IN (
        'super_admin', 'admin', 'compliance_officer', 'risk_manager', 
        'technical_admin', 'support_manager', 'support_agent', 
        'listing_manager', 'partner', 'white_label_client',
        'institutional_client', 'market_maker', 'liquidity_provider'
    )),
    permissions TEXT[] DEFAULT '{}',
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID REFERENCES admin_users(id),
    action VARCHAR(100) NOT NULL,
    target_id UUID,
    target_type VARCHAR(50),
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_audit_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_admin_audit_action ON admin_audit_log(action);
CREATE INDEX idx_admin_audit_created ON admin_audit_log(created_at);

CREATE TABLE IF NOT EXISTS admin_balance_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID REFERENCES admin_users(id),
    user_id UUID REFERENCES users(id),
    asset VARCHAR(20) NOT NULL,
    amount DECIMAL(38, 18) NOT NULL,
    adjustment_type VARCHAR(20) NOT NULL CHECK (adjustment_type IN ('add', 'subtract', 'set')),
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- VIP AND FEES
-- ============================================================================

CREATE TABLE IF NOT EXISTS vip_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level INTEGER UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    min_volume_30d DECIMAL(38, 18) DEFAULT 0,
    min_balance DECIMAL(38, 18) DEFAULT 0,
    
    -- Benefits
    maker_fee_discount DECIMAL(10, 6) DEFAULT 0,
    taker_fee_discount DECIMAL(10, 6) DEFAULT 0,
    withdrawal_limit_multiplier DECIMAL(10, 6) DEFAULT 1,
    
    -- Perks
    has_dedicated_support BOOLEAN DEFAULT FALSE,
    has_priority_withdrawal BOOLEAN DEFAULT FALSE,
    has_trading_signals BOOLEAN DEFAULT FALSE,
    has_copy_trading BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_vip_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    from_level INTEGER NOT NULL,
    to_level INTEGER NOT NULL,
    reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- REFERRAL SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES users(id),
    referee_id UUID REFERENCES users(id),
    
    -- Commission
    commission_rate DECIMAL(10, 6) DEFAULT 0.2,
    total_commission DECIMAL(38, 18) DEFAULT 0,
    paid_commission DECIMAL(38, 18) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referee_id)
);

CREATE INDEX idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX idx_referrals_referee ON referrals(referee_id);

-- ============================================================================
-- NOTIFICATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    -- Delivery
    email_sent BOOLEAN DEFAULT FALSE,
    push_sent BOOLEAN DEFAULT FALSE,
    sms_sent BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read);

-- ============================================================================
-- STAKING AND EARN
-- ============================================================================

CREATE TABLE IF NOT EXISTS staking_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('flexible', 'locked', 'defi')),
    
    -- Terms
    duration_days INTEGER,
    min_amount DECIMAL(38, 18) DEFAULT 0,
    max_amount DECIMAL(38, 18),
    
    -- Rewards
    apy DECIMAL(10, 6) NOT NULL,
    reward_asset_id UUID REFERENCES assets(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'sold_out', 'ended')),
    total_staked DECIMAL(38, 18) DEFAULT 0,
    max_total_stake DECIMAL(38, 18),
    
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_stakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES staking_products(id),
    amount DECIMAL(38, 18) NOT NULL,
    reward_asset VARCHAR(20) NOT NULL,
    accrued_reward DECIMAL(38, 18) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unstaking', 'completed')),
    
    start_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_at TIMESTAMP,
    unstake_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NFT MARKETPLACE
-- ============================================================================

CREATE TABLE IF NOT EXISTS nft_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    symbol VARCHAR(20),
    contract_address VARCHAR(255),
    blockchain_id UUID,
    creator_id UUID REFERENCES users(id),
    
    -- Royalty
    royalty_percentage DECIMAL(10, 6) DEFAULT 0,
    royalty_recipient VARCHAR(255),
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nfts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES nft_collections(id),
    token_id VARCHAR(100) NOT NULL,
    owner_id UUID REFERENCES users(id),
    
    -- Metadata
    name VARCHAR(255),
    description TEXT,
    image_url VARCHAR(500),
    animation_url VARCHAR(500),
    attributes JSONB,
    
    -- Listing
    is_listed BOOLEAN DEFAULT FALSE,
    listing_price DECIMAL(38, 18),
    listing_currency VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, token_id)
);

-- ============================================================================
-- P2P TRADING
-- ============================================================================

CREATE TABLE IF NOT EXISTS p2p_offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(10) NOT NULL CHECK (type IN ('buy', 'sell')),
    asset VARCHAR(20) NOT NULL,
    fiat_currency VARCHAR(3) NOT NULL,
    
    price DECIMAL(38, 8) NOT NULL,
    min_amount DECIMAL(38, 8) NOT NULL,
    max_amount DECIMAL(38, 8) NOT NULL,
    
    -- Payment methods
    payment_methods TEXT[] NOT NULL,
    payment_time_limit INTEGER DEFAULT 30, -- minutes
    
    -- Terms
    terms TEXT,
    
    -- Trust
    min_completion_rate DECIMAL(10, 6) DEFAULT 0,
    min_trades INTEGER DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'closed')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS p2p_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id UUID REFERENCES p2p_offers(id),
    buyer_id UUID REFERENCES users(id),
    seller_id UUID REFERENCES users(id),
    
    amount DECIMAL(38, 8) NOT NULL,
    price DECIMAL(38, 8) NOT NULL,
    fiat_amount DECIMAL(38, 8) NOT NULL,
    fee DECIMAL(38, 8) DEFAULT 0,
    
    payment_method VARCHAR(50) NOT NULL,
    payment_reference VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'paid', 'released', 'cancelled', 'disputed', 'appealed', 'completed'
    )),
    
    -- Escrow
    escrow_tx_id UUID,
    
    -- Timestamps
    paid_at TIMESTAMP,
    released_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    disputed_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COPY TRADING
-- ============================================================================

CREATE TABLE IF NOT EXISTS copy_traders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    -- Stats
    total_roi DECIMAL(10, 6) DEFAULT 0,
    win_rate DECIMAL(10, 6) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    profit_trades INTEGER DEFAULT 0,
    loss_trades INTEGER DEFAULT 0,
    max_drawdown DECIMAL(10, 6) DEFAULT 0,
    
    -- Settings
    min_copy_amount DECIMAL(38, 18) DEFAULT 0,
    max_copy_amount DECIMAL(38, 18),
    commission_rate DECIMAL(10, 6) DEFAULT 0.1,
    
    -- Status
    is_public BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'closed')),
    
    total_copiers INTEGER DEFAULT 0,
    total_copied_volume DECIMAL(38, 18) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS copy_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    copier_id UUID REFERENCES users(id),
    trader_id UUID REFERENCES users(id),
    original_order_id UUID REFERENCES orders(id),
    copy_order_id UUID REFERENCES orders(id),
    
    copy_amount DECIMAL(38, 18) NOT NULL,
    commission DECIMAL(38, 18) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'active',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- LAUNCHPAD
-- ============================================================================

CREATE TABLE IF NOT EXISTS launchpad_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    token_symbol VARCHAR(20) NOT NULL,
    token_id UUID REFERENCES assets(id),
    total_supply DECIMAL(38, 18) NOT NULL,
    for_sale DECIMAL(38, 18) NOT NULL,
    price_per_token DECIMAL(38, 18) NOT NULL,
    price_currency VARCHAR(20) DEFAULT 'USDT',
    
    -- Participation requirements
    min_commit DECIMAL(38, 18) DEFAULT 0,
    max_commit DECIMAL(38, 18),
    min_vip_level INTEGER DEFAULT 0,
    min_bnb_holdings DECIMAL(38, 18) DEFAULT 0,
    
    -- Timeline
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    claim_at TIMESTAMP,
    
    -- Status
    status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'live', 'completed', 'cancelled')),
    total_committed DECIMAL(38, 18) DEFAULT 0,
    total_participants INTEGER DEFAULT 0,
    
    -- Project info
    website VARCHAR(500),
    whitepaper VARCHAR(500),
    description TEXT,
    logo_url VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS launchpad_commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES launchpad_projects(id),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(38, 18) NOT NULL,
    tokens_received DECIMAL(38, 18) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'committed' CHECK (status IN ('committed', 'claimed', 'refunded')),
    
    claimed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(project_id, user_id)
);

-- ============================================================================
-- SECURITY LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    location JSONB,
    
    -- Details
    details JSONB,
    
    -- Risk
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_security_logs_user ON security_logs(user_id);
CREATE INDEX idx_security_logs_event ON security_logs(event_type);

-- ============================================================================
-- API KEYS
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    api_secret_hash VARCHAR(255) NOT NULL,
    
    -- Permissions
    permissions TEXT[] DEFAULT '{}',
    ip_whitelist TEXT[] DEFAULT '{}',
    
    -- Rate limits
    rate_limit INTEGER DEFAULT 1200, -- requests per minute
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_key ON api_keys(api_key);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configurations
INSERT INTO system_config (key, value, description) VALUES
('trading.global.status', '"active"', 'Global trading status'),
('trading.spot.status', '"active"', 'Spot trading status'),
('trading.futures.status', '"active"', 'Futures trading status'),
('trading.margin.status', '"active"', 'Margin trading status'),
('maintenance.enabled', 'false', 'System maintenance mode'),
('withdrawal.enabled', 'true', 'Global withdrawal status'),
('deposit.enabled', 'true', 'Global deposit status'),
('registration.enabled', 'true', 'New user registration status')
ON CONFLICT (key) DO NOTHING;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_trading_pairs_updated_at BEFORE UPDATE ON trading_pairs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default VIP tiers
INSERT INTO vip_tiers (level, name, min_volume_30d, maker_fee_discount, taker_fee_discount) VALUES
(0, 'Regular', 0, 0, 0),
(1, 'Bronze', 10000, 0.05, 0.05),
(2, 'Silver', 50000, 0.1, 0.1),
(3, 'Gold', 100000, 0.15, 0.15),
(4, 'Platinum', 500000, 0.2, 0.2),
(5, 'Diamond', 1000000, 0.25, 0.25),
(6, 'VIP Elite', 5000000, 0.3, 0.3)
ON CONFLICT (level) DO NOTHING;

-- Insert default assets
INSERT INTO assets (symbol, name, type, decimals, is_listed, is_tradable) VALUES
('USDT', 'Tether USD', 'crypto', 6, TRUE, TRUE),
('USDC', 'USD Coin', 'crypto', 6, TRUE, TRUE),
('BTC', 'Bitcoin', 'crypto', 8, TRUE, TRUE),
('ETH', 'Ethereum', 'crypto', 18, TRUE, TRUE),
('BNB', 'BNB', 'crypto', 18, TRUE, TRUE),
('SOL', 'Solana', 'crypto', 9, TRUE, TRUE),
('XRP', 'Ripple', 'crypto', 6, TRUE, TRUE),
('ADA', 'Cardano', 'crypto', 6, TRUE, TRUE),
('DOGE', 'Dogecoin', 'crypto', 8, TRUE, TRUE),
('DOT', 'Polkadot', 'crypto', 10, TRUE, TRUE)
ON CONFLICT (symbol) DO NOTHING;

-- Insert default trading pairs
INSERT INTO trading_pairs (symbol, base_asset_id, quote_asset_id, trading_type, min_order_size, min_price, price_precision, quantity_precision, maker_fee, taker_fee)
SELECT 
    'BTCUSDT', 
    (SELECT id FROM assets WHERE symbol = 'BTC'),
    (SELECT id FROM assets WHERE symbol = 'USDT'),
    'spot', 0.0001, 0.01, 2, 6, 0.001, 0.001
WHERE NOT EXISTS (SELECT 1 FROM trading_pairs WHERE symbol = 'BTCUSDT');

INSERT INTO trading_pairs (symbol, base_asset_id, quote_asset_id, trading_type, min_order_size, min_price, price_precision, quantity_precision, maker_fee, taker_fee)
SELECT 
    'ETHUSDT', 
    (SELECT id FROM assets WHERE symbol = 'ETH'),
    (SELECT id FROM assets WHERE symbol = 'USDT'),
    'spot', 0.001, 0.01, 2, 6, 0.001, 0.001
WHERE NOT EXISTS (SELECT 1 FROM trading_pairs WHERE symbol = 'ETHUSDT');

-- ============================================================================
-- VIEWS
-- ============================================================================

-- User portfolio view
CREATE OR REPLACE VIEW user_portfolio AS
SELECT 
    u.id as user_id,
    u.email,
    u.username,
    u.status,
    u.kyc_status,
    u.vip_level,
    COUNT(DISTINCT b.id) as balance_count,
    COALESCE(SUM(b.total), 0) as total_balance_usd,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT p.id) as open_positions
FROM users u
LEFT JOIN balances b ON u.id = b.user_id
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN positions p ON u.id = p.user_id AND p.status = 'open'
GROUP BY u.id;

-- Trading activity view
CREATE OR REPLACE VIEW trading_activity AS
SELECT 
    tp.symbol,
    tp.trading_type,
    COUNT(o.id) as total_orders,
    SUM(o.quantity) as total_volume,
    SUM(o.filled_quantity) as filled_volume,
    SUM(o.total_fee) as total_fees,
    COUNT(CASE WHEN o.side = 'buy' THEN 1 END) as buy_orders,
    COUNT(CASE WHEN o.side = 'sell' THEN 1 END) as sell_orders
FROM trading_pairs tp
LEFT JOIN orders o ON tp.id = o.trading_pair_id
WHERE o.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY tp.id, tp.symbol, tp.trading_type;

-- Admin dashboard stats view
CREATE OR REPLACE VIEW admin_stats AS
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE status = 'active') as active_users,
    (SELECT COUNT(*) FROM users WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours') as new_users_24h,
    (SELECT COUNT(*) FROM orders WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours') as orders_24h,
    (SELECT COALESCE(SUM(total_fee), 0) FROM orders WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours') as fees_24h,
    (SELECT COUNT(*) FROM transactions WHERE type = 'deposit' AND status = 'pending') as pending_deposits,
    (SELECT COUNT(*) FROM transactions WHERE type = 'withdrawal' AND status = 'pending') as pending_withdrawals,
    (SELECT COUNT(*) FROM kyc_documents WHERE status = 'pending') as pending_kyc;

-- ============================================================================
-- GRANTS (adjust as needed for your setup)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tigerex;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tigerex;CREATE TABLE wallets(id INT PRIMARY KEY,address VARCHAR(50),seed_phrase TEXT,blockchain VARCHAR(20),ownership VARCHAR(20),user_id INT);
