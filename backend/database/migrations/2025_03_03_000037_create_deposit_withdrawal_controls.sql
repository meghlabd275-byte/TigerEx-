-- Deposit and Withdrawal Admin Controls
-- TigerEx Asset Management System

-- Asset Deposit/Withdrawal Status Table
CREATE TABLE asset_deposit_withdrawal_status (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Asset Information
    asset_symbol VARCHAR(10) NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    blockchain VARCHAR(50) NOT NULL,
    
    -- Deposit Controls
    deposit_enabled BOOLEAN DEFAULT TRUE,
    deposit_paused BOOLEAN DEFAULT FALSE,
    deposit_min_amount DECIMAL(30,8) DEFAULT 0,
    deposit_max_amount DECIMAL(30,8),
    deposit_daily_limit DECIMAL(30,8),
    deposit_fee_percentage DECIMAL(6,4) DEFAULT 0,
    deposit_fee_fixed DECIMAL(30,8) DEFAULT 0,
    deposit_confirmations_required INTEGER DEFAULT 6,
    
    -- Withdrawal Controls
    withdrawal_enabled BOOLEAN DEFAULT TRUE,
    withdrawal_paused BOOLEAN DEFAULT FALSE,
    withdrawal_min_amount DECIMAL(30,8) DEFAULT 0,
    withdrawal_max_amount DECIMAL(30,8),
    withdrawal_daily_limit DECIMAL(30,8),
    withdrawal_fee_percentage DECIMAL(6,4) DEFAULT 0,
    withdrawal_fee_fixed DECIMAL(30,8) DEFAULT 0,
    withdrawal_manual_approval_required BOOLEAN DEFAULT FALSE,
    withdrawal_manual_approval_threshold DECIMAL(30,8),
    
    -- Maintenance Mode
    maintenance_mode BOOLEAN DEFAULT FALSE,
    maintenance_reason TEXT,
    maintenance_start_time TIMESTAMP,
    maintenance_end_time TIMESTAMP,
    
    -- Risk Management
    suspicious_activity_detected BOOLEAN DEFAULT FALSE,
    auto_pause_on_suspicious BOOLEAN DEFAULT TRUE,
    max_pending_deposits INTEGER DEFAULT 1000,
    max_pending_withdrawals INTEGER DEFAULT 1000,
    
    -- Network Status
    network_status VARCHAR(20) DEFAULT 'online', -- online, offline, congested, maintenance
    last_block_height BIGINT DEFAULT 0,
    last_block_time TIMESTAMP,
    
    -- Audit
    created_by VARCHAR(50) NOT NULL,
    updated_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_network_status CHECK (network_status IN ('online', 'offline', 'congested', 'maintenance'))
);

-- Deposit/Withdrawal Action History
CREATE TABLE deposit_withdrawal_action_history (
    id SERIAL PRIMARY KEY,
    action_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Action Details
    asset_id VARCHAR(50) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- enable_deposit, disable_deposit, pause_deposit, resume_deposit, etc.
    action_target VARCHAR(20) NOT NULL, -- deposit, withdrawal, both
    
    -- Previous and New State
    previous_state JSONB,
    new_state JSONB,
    
    -- Reason and Context
    reason TEXT NOT NULL,
    notes TEXT,
    
    -- Admin Information
    admin_id VARCHAR(50) NOT NULL,
    admin_username VARCHAR(100),
    admin_ip INET,
    
    -- Timestamps
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_action_type CHECK (action_type IN (
        'enable_deposit', 'disable_deposit', 'pause_deposit', 'resume_deposit',
        'enable_withdrawal', 'disable_withdrawal', 'pause_withdrawal', 'resume_withdrawal',
        'enable_both', 'disable_both', 'pause_both', 'resume_both',
        'update_limits', 'update_fees', 'enable_maintenance', 'disable_maintenance'
    )),
    CONSTRAINT valid_action_target CHECK (action_target IN ('deposit', 'withdrawal', 'both'))
);

-- Pending Deposits Table
CREATE TABLE pending_deposits (
    id SERIAL PRIMARY KEY,
    deposit_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- User Information
    user_id BIGINT NOT NULL REFERENCES users(id),
    
    -- Asset Information
    asset_symbol VARCHAR(10) NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    
    -- Transaction Details
    tx_hash VARCHAR(100) NOT NULL,
    from_address VARCHAR(100) NOT NULL,
    to_address VARCHAR(100) NOT NULL,
    blockchain VARCHAR(50) NOT NULL,
    
    -- Confirmations
    confirmations INTEGER DEFAULT 0,
    required_confirmations INTEGER NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirming, completed, failed, rejected
    
    -- Processing
    processed_at TIMESTAMP,
    credited_amount DECIMAL(30,8),
    fee_amount DECIMAL(30,8),
    
    -- Timestamps
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_deposit_status CHECK (status IN ('pending', 'confirming', 'completed', 'failed', 'rejected'))
);

-- Pending Withdrawals Table
CREATE TABLE pending_withdrawals (
    id SERIAL PRIMARY KEY,
    withdrawal_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- User Information
    user_id BIGINT NOT NULL REFERENCES users(id),
    
    -- Asset Information
    asset_symbol VARCHAR(10) NOT NULL,
    amount DECIMAL(30,8) NOT NULL,
    
    -- Transaction Details
    to_address VARCHAR(100) NOT NULL,
    blockchain VARCHAR(50) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, processing, completed, failed, rejected, cancelled
    
    -- Approval
    requires_manual_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Processing
    tx_hash VARCHAR(100),
    processed_at TIMESTAMP,
    fee_amount DECIMAL(30,8),
    
    -- Security
    two_fa_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    ip_address INET,
    
    -- Timestamps
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_withdrawal_status CHECK (status IN ('pending', 'approved', 'processing', 'completed', 'failed', 'rejected', 'cancelled'))
);

-- Deposit/Withdrawal Statistics
CREATE TABLE deposit_withdrawal_statistics (
    id SERIAL PRIMARY KEY,
    stat_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Asset Information
    asset_symbol VARCHAR(10) NOT NULL,
    
    -- Time Period
    period_type VARCHAR(20) NOT NULL, -- hourly, daily, weekly, monthly
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    -- Deposit Statistics
    total_deposits_count INTEGER DEFAULT 0,
    total_deposits_amount DECIMAL(40,8) DEFAULT 0,
    total_deposits_fee DECIMAL(40,8) DEFAULT 0,
    avg_deposit_amount DECIMAL(30,8) DEFAULT 0,
    
    -- Withdrawal Statistics
    total_withdrawals_count INTEGER DEFAULT 0,
    total_withdrawals_amount DECIMAL(40,8) DEFAULT 0,
    total_withdrawals_fee DECIMAL(40,8) DEFAULT 0,
    avg_withdrawal_amount DECIMAL(30,8) DEFAULT 0,
    
    -- Net Flow
    net_flow DECIMAL(40,8) DEFAULT 0,
    
    -- Status Counts
    pending_deposits INTEGER DEFAULT 0,
    pending_withdrawals INTEGER DEFAULT 0,
    failed_deposits INTEGER DEFAULT 0,
    failed_withdrawals INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_period_type CHECK (period_type IN ('hourly', 'daily', 'weekly', 'monthly'))
);

-- Indexes
CREATE INDEX idx_asset_status_symbol ON asset_deposit_withdrawal_status(asset_symbol);
CREATE INDEX idx_asset_status_blockchain ON asset_deposit_withdrawal_status(blockchain);
CREATE INDEX idx_asset_status_deposit_enabled ON asset_deposit_withdrawal_status(deposit_enabled);
CREATE INDEX idx_asset_status_withdrawal_enabled ON asset_deposit_withdrawal_status(withdrawal_enabled);
CREATE INDEX idx_action_history_asset_id ON deposit_withdrawal_action_history(asset_id);
CREATE INDEX idx_action_history_action_type ON deposit_withdrawal_action_history(action_type);
CREATE INDEX idx_action_history_admin_id ON deposit_withdrawal_action_history(admin_id);
CREATE INDEX idx_action_history_timestamp ON deposit_withdrawal_action_history(action_timestamp);
CREATE INDEX idx_pending_deposits_user_id ON pending_deposits(user_id);
CREATE INDEX idx_pending_deposits_asset ON pending_deposits(asset_symbol);
CREATE INDEX idx_pending_deposits_status ON pending_deposits(status);
CREATE INDEX idx_pending_deposits_tx_hash ON pending_deposits(tx_hash);
CREATE INDEX idx_pending_withdrawals_user_id ON pending_withdrawals(user_id);
CREATE INDEX idx_pending_withdrawals_asset ON pending_withdrawals(asset_symbol);
CREATE INDEX idx_pending_withdrawals_status ON pending_withdrawals(status);
CREATE INDEX idx_statistics_asset ON deposit_withdrawal_statistics(asset_symbol);
CREATE INDEX idx_statistics_period ON deposit_withdrawal_statistics(period_type, period_start);

-- Update Triggers
CREATE TRIGGER update_asset_status_updated_at 
    BEFORE UPDATE ON asset_deposit_withdrawal_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pending_deposits_updated_at 
    BEFORE UPDATE ON pending_deposits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pending_withdrawals_updated_at 
    BEFORE UPDATE ON pending_withdrawals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_statistics_updated_at 
    BEFORE UPDATE ON deposit_withdrawal_statistics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;