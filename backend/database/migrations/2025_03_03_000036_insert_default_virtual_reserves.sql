-- Insert Default Virtual Asset Reserves
-- TigerEx Virtual Liquidity System Initialization

-- Insert default virtual asset reserves for major assets
INSERT INTO virtual_asset_reserves (
    reserve_id, asset_symbol, asset_name, asset_type,
    total_reserve, available_reserve, locked_reserve, allocated_to_pools,
    is_virtual, backing_ratio, real_asset_backing,
    max_allocation_per_pool, min_reserve_threshold,
    is_active, auto_rebalance_enabled, created_by
) VALUES 
-- Virtual USDT Reserve
('VUSDT_RESERVE_001', 'USDT', 'Tether USD (Virtual)', 'stablecoin',
 100000000.00000000, 80000000.00000000, 0.00000000, 20000000.00000000,
 true, 0.2000, 20000000.00000000,
 10000000.00000000, 5000000.00000000,
 true, true, 'system'),

-- Virtual USDC Reserve
('VUSDC_RESERVE_001', 'USDC', 'USD Coin (Virtual)', 'stablecoin',
 100000000.00000000, 80000000.00000000, 0.00000000, 20000000.00000000,
 true, 0.2000, 20000000.00000000,
 10000000.00000000, 5000000.00000000,
 true, true, 'system'),

-- Virtual ETH Reserve
('VETH_RESERVE_001', 'ETH', 'Ethereum (Virtual)', 'crypto',
 50000.00000000, 40000.00000000, 0.00000000, 10000.00000000,
 true, 0.1500, 7500.00000000,
 5000.00000000, 2000.00000000,
 true, true, 'system'),

-- Virtual BTC Reserve
('VBTC_RESERVE_001', 'BTC', 'Bitcoin (Virtual)', 'crypto',
 2000.00000000, 1600.00000000, 0.00000000, 400.00000000,
 true, 0.1500, 300.00000000,
 200.00000000, 100.00000000,
 true, true, 'system'),

-- Virtual BNB Reserve
('VBNB_RESERVE_001', 'BNB', 'Binance Coin (Virtual)', 'crypto',
 100000.00000000, 80000.00000000, 0.00000000, 20000.00000000,
 true, 0.1000, 10000.00000000,
 10000.00000000, 5000.00000000,
 true, true, 'system'),

-- Virtual MATIC Reserve
('VMATIC_RESERVE_001', 'MATIC', 'Polygon (Virtual)', 'crypto',
 10000000.00000000, 8000000.00000000, 0.00000000, 2000000.00000000,
 true, 0.1000, 1000000.00000000,
 1000000.00000000, 500000.00000000,
 true, true, 'system'),

-- Virtual AVAX Reserve
('VAVAX_RESERVE_001', 'AVAX', 'Avalanche (Virtual)', 'crypto',
 500000.00000000, 400000.00000000, 0.00000000, 100000.00000000,
 true, 0.1000, 50000.00000000,
 50000.00000000, 25000.00000000,
 true, true, 'system'),

-- Virtual SOL Reserve
('VSOL_RESERVE_001', 'SOL', 'Solana (Virtual)', 'crypto',
 500000.00000000, 400000.00000000, 0.00000000, 100000.00000000,
 true, 0.1000, 50000.00000000,
 50000.00000000, 25000.00000000,
 true, true, 'system'),

-- Virtual DAI Reserve
('VDAI_RESERVE_001', 'DAI', 'Dai Stablecoin (Virtual)', 'stablecoin',
 50000000.00000000, 40000000.00000000, 0.00000000, 10000000.00000000,
 true, 0.2000, 10000000.00000000,
 5000000.00000000, 2500000.00000000,
 true, true, 'system'),

-- Virtual BUSD Reserve
('VBUSD_RESERVE_001', 'BUSD', 'Binance USD (Virtual)', 'stablecoin',
 50000000.00000000, 40000000.00000000, 0.00000000, 10000000.00000000,
 true, 0.2000, 10000000.00000000,
 5000000.00000000, 2500000.00000000,
 true, true, 'system');

-- Insert system settings for virtual liquidity management
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public, required_permission) VALUES
('virtual_liquidity_enabled', 'true', 'boolean', 'Enable virtual liquidity system', false, 'admin:liquidity'),
('virtual_liquidity_max_percentage', '0.7', 'number', 'Maximum percentage of virtual liquidity in pools (70%)', false, 'admin:liquidity'),
('virtual_liquidity_rebalance_interval', '3600', 'number', 'Rebalancing interval in seconds (1 hour)', false, 'admin:liquidity'),
('virtual_liquidity_min_backing_ratio', '0.1', 'number', 'Minimum backing ratio for virtual assets (10%)', false, 'admin:liquidity'),
('iou_token_enabled', 'true', 'boolean', 'Enable IOU token system', false, 'admin:tokens'),
('iou_token_default_conversion_ratio', '1.0', 'number', 'Default IOU to real token conversion ratio', false, 'admin:tokens'),
('liquidity_pool_creation_enabled', 'true', 'boolean', 'Allow creation of new liquidity pools', false, 'admin:liquidity'),
('liquidity_pool_min_liquidity_usd', '10000', 'number', 'Minimum liquidity in USD to create a pool', false, 'admin:liquidity'),
('auto_liquidity_provision_enabled', 'true', 'boolean', 'Automatically provide liquidity to new trading pairs', false, 'admin:liquidity'),
('virtual_reserve_alert_threshold', '0.2', 'number', 'Alert when reserve utilization exceeds 80%', false, 'admin:liquidity');

-- Create example liquidity pools with virtual liquidity
INSERT INTO liquidity_pools (
    pool_id, pool_name, pool_type,
    base_asset, quote_asset, trading_pair,
    base_reserve, quote_reserve, total_liquidity_usd,
    virtual_base_liquidity, virtual_quote_liquidity, virtual_liquidity_percentage,
    fee_rate, protocol_fee_rate,
    is_active, is_public, created_by
) VALUES
-- TIGER/USDT Pool with Virtual Liquidity
('POOL_TIGER_USDT_001', 'TIGER/USDT Liquidity Pool', 'amm',
 'TIGER', 'USDT', 'TIGERUSDT',
 1000000.00000000, 1000000.00000000, 2000000.00000000,
 700000.00000000, 700000.00000000, 0.7000,
 0.0030, 0.0005,
 true, true, 'system'),

-- TIGER/ETH Pool with Virtual Liquidity
('POOL_TIGER_ETH_001', 'TIGER/ETH Liquidity Pool', 'amm',
 'TIGER', 'ETH', 'TIGERETH',
 1000000.00000000, 500.00000000, 1000000.00000000,
 700000.00000000, 350.00000000, 0.7000,
 0.0030, 0.0005,
 true, true, 'system'),

-- TIGER/BTC Pool with Virtual Liquidity
('POOL_TIGER_BTC_001', 'TIGER/BTC Liquidity Pool', 'amm',
 'TIGER', 'BTC', 'TIGERBTC',
 1000000.00000000, 20.00000000, 1000000.00000000,
 700000.00000000, 14.00000000, 0.7000,
 0.0030, 0.0005,
 true, true, 'system');

-- Allocate virtual liquidity to pools
INSERT INTO virtual_liquidity_allocations (
    allocation_id, reserve_id, pool_id,
    allocated_amount, asset_symbol,
    is_active
) VALUES
-- USDT allocation to TIGER/USDT pool
('ALLOC_VUSDT_TIGER_001', 
 (SELECT id FROM virtual_asset_reserves WHERE reserve_id = 'VUSDT_RESERVE_001'),
 (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_TIGER_USDT_001'),
 700000.00000000, 'USDT', true),

-- ETH allocation to TIGER/ETH pool
('ALLOC_VETH_TIGER_001',
 (SELECT id FROM virtual_asset_reserves WHERE reserve_id = 'VETH_RESERVE_001'),
 (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_TIGER_ETH_001'),
 350.00000000, 'ETH', true),

-- BTC allocation to TIGER/BTC pool
('ALLOC_VBTC_TIGER_001',
 (SELECT id FROM virtual_asset_reserves WHERE reserve_id = 'VBTC_RESERVE_001'),
 (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_TIGER_BTC_001'),
 14.00000000, 'BTC', true);

-- Create example IOU tokens
INSERT INTO iou_tokens (
    iou_id, token_symbol, token_name, underlying_asset,
    total_supply, circulating_supply,
    conversion_ratio, is_convertible,
    backing_amount, backing_percentage,
    is_tradable, status,
    description, created_by
) VALUES
-- Pre-launch token IOU
('IOU_NEWTOKEN_001', 'NEWTOKEN-IOU', 'New Token IOU', 'NEWTOKEN',
 10000000.00000000, 5000000.00000000,
 1.00000000, false,
 0.00000000, 0.0000,
 true, 'active',
 'IOU token for upcoming NEWTOKEN launch. Will be convertible to real NEWTOKEN upon mainnet launch.',
 'system'),

-- Launchpad token IOU
('IOU_LAUNCHPAD_001', 'LAUNCH-IOU', 'Launchpad Token IOU', 'LAUNCHTOKEN',
 5000000.00000000, 2000000.00000000,
 1.00000000, false,
 0.00000000, 0.0000,
 true, 'active',
 'IOU token for launchpad project. Convertible after TGE (Token Generation Event).',
 'system');

-- Create liquidity pools for IOU tokens with virtual liquidity
INSERT INTO liquidity_pools (
    pool_id, pool_name, pool_type,
    base_asset, quote_asset, trading_pair,
    base_reserve, quote_reserve, total_liquidity_usd,
    virtual_base_liquidity, virtual_quote_liquidity, virtual_liquidity_percentage,
    fee_rate, protocol_fee_rate,
    is_active, is_public, created_by
) VALUES
-- NEWTOKEN-IOU/USDT Pool
('POOL_IOU_NEWTOKEN_USDT', 'NEWTOKEN-IOU/USDT Pool', 'amm',
 'NEWTOKEN-IOU', 'USDT', 'NEWTOKEN-IOUUSDT',
 500000.00000000, 500000.00000000, 1000000.00000000,
 0.00000000, 450000.00000000, 0.9000,
 0.0030, 0.0005,
 true, true, 'system'),

-- LAUNCH-IOU/USDT Pool
('POOL_IOU_LAUNCH_USDT', 'LAUNCH-IOU/USDT Pool', 'amm',
 'LAUNCH-IOU', 'USDT', 'LAUNCH-IOUUSDT',
 200000.00000000, 200000.00000000, 400000.00000000,
 0.00000000, 180000.00000000, 0.9000,
 0.0030, 0.0005,
 true, true, 'system');

-- Link IOU tokens to their liquidity pools
UPDATE iou_tokens 
SET has_liquidity_pool = true,
    liquidity_pool_id = (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_IOU_NEWTOKEN_USDT'),
    virtual_liquidity_provided = 450000.00000000
WHERE iou_id = 'IOU_NEWTOKEN_001';

UPDATE iou_tokens 
SET has_liquidity_pool = true,
    liquidity_pool_id = (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_IOU_LAUNCH_USDT'),
    virtual_liquidity_provided = 180000.00000000
WHERE iou_id = 'IOU_LAUNCHPAD_001';

-- Allocate virtual USDT to IOU token pools
INSERT INTO virtual_liquidity_allocations (
    allocation_id, reserve_id, pool_id,
    allocated_amount, asset_symbol,
    is_active
) VALUES
('ALLOC_VUSDT_IOU_NEW_001',
 (SELECT id FROM virtual_asset_reserves WHERE reserve_id = 'VUSDT_RESERVE_001'),
 (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_IOU_NEWTOKEN_USDT'),
 450000.00000000, 'USDT', true),

('ALLOC_VUSDT_IOU_LAUNCH_001',
 (SELECT id FROM virtual_asset_reserves WHERE reserve_id = 'VUSDT_RESERVE_001'),
 (SELECT id FROM liquidity_pools WHERE pool_id = 'POOL_IOU_LAUNCH_USDT'),
 180000.00000000, 'USDT', true);

COMMIT;