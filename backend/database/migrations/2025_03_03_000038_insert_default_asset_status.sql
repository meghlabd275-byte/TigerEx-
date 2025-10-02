-- Insert Default Asset Deposit/Withdrawal Status
-- TigerEx Asset Management System

-- Insert default status for major cryptocurrencies
INSERT INTO asset_deposit_withdrawal_status (
    asset_id, asset_symbol, asset_name, blockchain,
    deposit_enabled, deposit_min_amount, deposit_max_amount, deposit_daily_limit,
    deposit_confirmations_required,
    withdrawal_enabled, withdrawal_min_amount, withdrawal_max_amount, withdrawal_daily_limit,
    withdrawal_fee_fixed, withdrawal_manual_approval_threshold,
    network_status, created_by
) VALUES 
-- Bitcoin
('BTC_BITCOIN', 'BTC', 'Bitcoin', 'Bitcoin',
 true, 0.0001, 100, 1000,
 3,
 true, 0.001, 50, 500,
 0.0005, 10,
 'online', 'system'),

-- Ethereum
('ETH_ETHEREUM', 'ETH', 'Ethereum', 'Ethereum',
 true, 0.01, 1000, 10000,
 12,
 true, 0.01, 500, 5000,
 0.005, 100,
 'online', 'system'),

-- USDT (ERC20)
('USDT_ERC20', 'USDT', 'Tether USD', 'Ethereum',
 true, 10, 1000000, 10000000,
 12,
 true, 10, 500000, 5000000,
 5, 50000,
 'online', 'system'),

-- USDT (TRC20)
('USDT_TRC20', 'USDT', 'Tether USD', 'Tron',
 true, 10, 1000000, 10000000,
 20,
 true, 10, 500000, 5000000,
 1, 50000,
 'online', 'system'),

-- USDT (BEP20)
('USDT_BEP20', 'USDT', 'Tether USD', 'BSC',
 true, 10, 1000000, 10000000,
 15,
 true, 10, 500000, 5000000,
 0.8, 50000,
 'online', 'system'),

-- USDC (ERC20)
('USDC_ERC20', 'USDC', 'USD Coin', 'Ethereum',
 true, 10, 1000000, 10000000,
 12,
 true, 10, 500000, 5000000,
 5, 50000,
 'online', 'system'),

-- BNB
('BNB_BSC', 'BNB', 'Binance Coin', 'BSC',
 true, 0.01, 10000, 100000,
 15,
 true, 0.01, 5000, 50000,
 0.0005, 1000,
 'online', 'system'),

-- MATIC
('MATIC_POLYGON', 'MATIC', 'Polygon', 'Polygon',
 true, 1, 1000000, 10000000,
 128,
 true, 1, 500000, 5000000,
 0.1, 10000,
 'online', 'system'),

-- AVAX
('AVAX_AVALANCHE', 'AVAX', 'Avalanche', 'Avalanche',
 true, 0.1, 10000, 100000,
 15,
 true, 0.1, 5000, 50000,
 0.01, 1000,
 'online', 'system'),

-- SOL
('SOL_SOLANA', 'SOL', 'Solana', 'Solana',
 true, 0.01, 10000, 100000,
 32,
 true, 0.01, 5000, 50000,
 0.000005, 1000,
 'online', 'system'),

-- ADA
('ADA_CARDANO', 'ADA', 'Cardano', 'Cardano',
 true, 1, 1000000, 10000000,
 15,
 true, 1, 500000, 5000000,
 0.17, 10000,
 'online', 'system'),

-- DOT
('DOT_POLKADOT', 'DOT', 'Polkadot', 'Polkadot',
 true, 0.1, 10000, 100000,
 10,
 true, 0.1, 5000, 50000,
 0.01, 1000,
 'online', 'system'),

-- LINK
('LINK_ETHEREUM', 'LINK', 'Chainlink', 'Ethereum',
 true, 0.1, 100000, 1000000,
 12,
 true, 0.1, 50000, 500000,
 0.5, 5000,
 'online', 'system'),

-- UNI
('UNI_ETHEREUM', 'UNI', 'Uniswap', 'Ethereum',
 true, 0.1, 100000, 1000000,
 12,
 true, 0.1, 50000, 500000,
 0.5, 5000,
 'online', 'system'),

-- AAVE
('AAVE_ETHEREUM', 'AAVE', 'Aave', 'Ethereum',
 true, 0.01, 10000, 100000,
 12,
 true, 0.01, 5000, 50000,
 0.05, 500,
 'online', 'system'),

-- DAI
('DAI_ETHEREUM', 'DAI', 'Dai Stablecoin', 'Ethereum',
 true, 10, 1000000, 10000000,
 12,
 true, 10, 500000, 5000000,
 5, 50000,
 'online', 'system'),

-- BUSD
('BUSD_BSC', 'BUSD', 'Binance USD', 'BSC',
 true, 10, 1000000, 10000000,
 15,
 true, 10, 500000, 5000000,
 0.8, 50000,
 'online', 'system'),

-- SHIB
('SHIB_ETHEREUM', 'SHIB', 'Shiba Inu', 'Ethereum',
 true, 1000000, 1000000000000, 10000000000000,
 12,
 true, 1000000, 500000000000, 5000000000000,
 500000, 50000000000,
 'online', 'system'),

-- DOGE
('DOGE_DOGECOIN', 'DOGE', 'Dogecoin', 'Dogecoin',
 true, 10, 1000000, 10000000,
 6,
 true, 10, 500000, 5000000,
 1, 50000,
 'online', 'system'),

-- TRX
('TRX_TRON', 'TRX', 'Tron', 'Tron',
 true, 1, 10000000, 100000000,
 20,
 true, 1, 5000000, 50000000,
 0.1, 500000,
 'online', 'system'),

-- TIGER (Native Token)
('TIGER_TIGERCHAIN', 'TIGER', 'Tiger Token', 'TigerChain',
 true, 1, 10000000, 100000000,
 10,
 true, 1, 5000000, 50000000,
 0.1, 100000,
 'online', 'system');

-- Insert system settings for deposit/withdrawal management
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public, required_permission) VALUES
('deposit_withdrawal_enabled', 'true', 'boolean', 'Global enable/disable for deposits and withdrawals', false, 'admin:deposit_withdrawal'),
('auto_pause_on_network_issues', 'true', 'boolean', 'Automatically pause deposits/withdrawals on network issues', false, 'admin:deposit_withdrawal'),
('manual_approval_threshold_usd', '10000', 'number', 'USD threshold for manual withdrawal approval', false, 'admin:deposit_withdrawal'),
('max_pending_deposits_per_user', '10', 'number', 'Maximum pending deposits per user', false, 'admin:deposit_withdrawal'),
('max_pending_withdrawals_per_user', '5', 'number', 'Maximum pending withdrawals per user', false, 'admin:deposit_withdrawal'),
('deposit_notification_enabled', 'true', 'boolean', 'Send notifications for deposits', true, 'admin:deposit_withdrawal'),
('withdrawal_notification_enabled', 'true', 'boolean', 'Send notifications for withdrawals', true, 'admin:deposit_withdrawal'),
('suspicious_activity_auto_pause', 'true', 'boolean', 'Auto-pause on suspicious activity detection', false, 'admin:deposit_withdrawal'),
('network_health_check_interval', '60', 'number', 'Network health check interval in seconds', false, 'admin:deposit_withdrawal'),
('withdrawal_processing_delay', '300', 'number', 'Withdrawal processing delay in seconds for security', false, 'admin:deposit_withdrawal');

COMMIT;