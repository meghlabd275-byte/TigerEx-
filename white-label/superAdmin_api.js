#!/usr/bin/env node

/**
 * TigerEx Super Admin API
 * Complete control over all white label clients
 */

const express = require('express');
const { Pool } = require('pg');
const Redis = require('ioredis');
const crypto = require('crypto');

const app = express();
const pg = new Pool({
    host: process.env.PG_HOST || 'localhost',
    database: process.env.PG_DB || 'tigerex',
    user: process.env.PG_USER || 'tigerex',
    max: 50
});

const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: 6379
});

app.use(express.json());

// ==================== MIDDLEWARE ====================

// Super Admin authentication
function requireSuperAdmin(req, res, next) {
    const apiKey = req.headers['x-super-key'];
    if (apiKey !== process.env.SUPER_ADMIN_KEY) {
        return res.status(403).json({ error: 'Unauthorized. Super admin key required.' });
    }
    next();
}

// ==================== CLIENT MANAGEMENT ====================

// List all clients
app.get('/api/v1/super/clients', requireSuperAdmin, async (req, res) => {
    try {
        const { status, page = 1, limit = 20 } = req.query;
        
        let query = 'SELECT * FROM whitelabel_clients';
        const params = [];
        
        if (status) {
            params.push(status);
            query += ` WHERE status = $${params.length}`;
        }
        
        params.push(parseInt(limit));
        query += ` ORDER BY created_at DESC LIMIT $${params.length}`;
        
        const clients = await pg.query(query, params);
        
        res.json({
            success: true,
            clients: clients.rows,
            total: clients.rows.length
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get client details
app.get('/api/v1/super/client/:clientId', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        const client = await pg.query(
            'SELECT * FROM whitelabel_clients WHERE client_id = $1',
            [clientId]
        );
        
        if (client.rows.length === 0) {
            return res.status(404).json({ error: 'Client not found' });
        }
        
        // Get user count
        const userCount = await pg.query(
            'SELECT COUNT(*) FROM users WHERE client_id = $1',
            [clientId]
        );
        
        // Get volume
        const volume = await pg.query(
            'SELECT SUM(volume) FROM transactions WHERE client_id = $1 AND created_at > NOW() - INTERVAL \'30 days\'',
            [clientId]
        );
        
        res.json({
            success: true,
            client: client.rows[0],
            stats: {
                users: parseInt(userCount.rows[0].count),
                volume: volume.rows[0].sum || 0
            }
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Suspend client
app.post('/api/v1/super/client/:clientId/suspend', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { reason } = req.body;
        
        // Update client status
        await pg.query(
            'UPDATE whitelabel_clients SET status = $1, suspended_at = NOW(), suspend_reason = $2 WHERE client_id = $3',
            ['suspended', reason, clientId]
        );
        
        // Disable all services
        await redis.del(`services:${clientId}:*`);
        
        // Log action
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'client', $2, $3, 'superadmin', NOW())`,
            ['suspend', clientId, reason]
        );
        
        res.json({
            success: true,
            message: `Client ${clientId} has been SUSPENDED`,
            reason
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Activate client
app.post('/api/v1/super/client/:clientId/activate', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        await pg.query(
            'UPDATE whitelabel_clients SET status = $1, suspended_at = NULL, suspend_reason = NULL WHERE client_id = $2',
            ['active', clientId]
        );
        
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'client', $2, $3, 'superadmin', NOW())`,
            ['activate', clientId, 'Reactivated by super admin']
        );
        
        res.json({
            success: true,
            message: `Client ${clientId} has been ACTIVATED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Delete client
app.delete('/api/v1/super/client/:clientId', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        // Delete all client data
        await pg.query('DELETE FROM users WHERE client_id = $1', [clientId]);
        await pg.query('DELETE FROM transactions WHERE client_id = $1', [clientId]);
        await pg.query('DELETE FROM wallets WHERE client_id = $1', [clientId]);
        await pg.query('DELETE FROM custom_chains WHERE client_id = $1', [clientId]);
        await pg.query('DELETE FROM whitelabel_clients WHERE client_id = $1', [clientId]);
        
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'client', $2, $3, 'superadmin', NOW())`,
            ['delete', clientId, 'Client deleted by super admin']
        );
        
        res.json({
            success: true,
            message: `Client ${clientId} has been DELETED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Update client settings (override)
app.patch('/api/v1/super/client/:clientId/settings', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { settings } = req.body;
        
        await pg.query(
            'UPDATE whitelabel_clients SET settings = $1, updated_at = NOW() WHERE client_id = $2',
            [JSON.stringify(settings), clientId]
        );
        
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'client', $2, $3, 'superadmin', NOW())`,
            ['update_settings', clientId, JSON.stringify(settings)]
        );
        
        res.json({
            success: true,
            message: `Settings updated for ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== USER MANAGEMENT ====================

// Get all users across clients
app.get('/api/v1/super/users', requireSuperAdmin, async (req, res) => {
    try {
        const { page = 1, limit = 50 } = req.query;
        
        const users = await pg.query(
            `SELECT u.*, wc.company_name as client_name 
             FROM users u 
             JOIN whitelabel_clients wc ON u.client_id = wc.client_id 
             ORDER BY u.created_at DESC 
             LIMIT $1 OFFSET $2`,
            [parseInt(limit), (page - 1) * limit]
        );
        
        res.json({
            success: true,
            users: users.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Ban user across all clients
app.post('/api/v1/super/user/:userId/ban', requireSuperAdmin, async (req, res) => {
    try {
        const { userId } = req.params;
        const { reason } = req.body;
        
        await pg.query(
            'UPDATE users SET status = $1, ban_reason = $2 WHERE user_id = $3',
            ['banned', reason, userId]
        );
        
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'user', $2, $3, 'superadmin', NOW())`,
            ['ban_user', userId, reason]
        );
        
        res.json({
            success: true,
            message: 'User has been banned'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== BLOCKCHAIN MANAGEMENT ====================

// Stop custom blockchain
app.post('/api/v1/super/chain/:chainId/stop', requireSuperAdmin, async (req, res) => {
    try {
        const { chainId } = req.params;
        
        await pg.query(
            'UPDATE custom_chains SET status = $1 WHERE chain_id = $2',
            ['stopped', chainId]
        );
        
        await redis.del(`chain:${chainId}`);
        
        res.json({
            success: true,
            message: `Chain ${chainId} has been STOPPED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Start custom blockchain
app.post('/api/v1/super/chain/:chainId/start', requireSuperAdmin, async (req, res) => {
    try {
        const { chainId } = req.params;
        
        await pg.query(
            'UPDATE custom_chains SET status = $1 WHERE chain_id = $2',
            ['active', chainId]
        );
        
        res.json({
            success: true,
            message: `Chain ${chainId} has been STARTED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Delete custom blockchain
app.delete('/api/v1/super/chain/:chainId', requireSuperAdmin, async (req, res) => {
    try {
        const { chainId } = req.params;
        
        await pg.query('DELETE FROM custom_chains WHERE chain_id = $1', [chainId]);
        await redis.del(`chain:${chainId}`);
        
        res.json({
            success: true,
            message: `Chain ${chainId} has been DELETED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== GLOBAL ACTIONS ====================

// Pause all trading
app.post('/api/v1/super/global/pause-trading', requireSuperAdmin, async (req, res) => {
    try {
        await redis.set('global:trading_paused', 'true');
        
        await pg.query(
            `INSERT INTO super_admin_logs (action, target_type, target_id, details, admin_id, created_at)
             VALUES ($1, 'system', 'all', $2, 'superadmin', NOW())`,
            ['pause_trading', 'All trading paused']
        );
        
        res.json({
            success: true,
            message: 'Trading has been paused globally'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Resume all trading
app.post('/api/v1/super/global/resume-trading', requireSuperAdmin, async (req, res) => {
    try {
        await redis.set('global:trading_paused', 'false');
        
        res.json({
            success: true,
            message: 'Trading has been resumed globally'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Halt all services
app.post('/api/v1/super/global/halt', requireSuperAdmin, async (req, res) => {
    try {
        await redis.set('global:halted', 'true');
        
        res.json({
            success: true,
            message: 'ALL SERVICES HAVE BEEN HALTED'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Resume all services
app.post('/api/v1/super/global/resume', requireSuperAdmin, async (req, res) => {
    try {
        await redis.set('global:halted', 'false');
        await redis.set('global:trading_paused', 'false');
        
        res.json({
            success: true,
            message: 'All services resumed'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== REVENUE ====================

// Get revenue
app.get('/api/v1/super/revenue', requireSuperAdmin, async (req, res) => {
    try {
        const total = await pg.query(
            'SELECT SUM(amount) FROM client_fees WHERE created_at > NOW() - INTERVAL \'30 days\''
        );
        
        const byClient = await pg.query(
            `SELECT wc.client_id, wc.company_name, SUM(cf.amount) as revenue
             FROM client_fees cf
             JOIN whitelabel_clients wc ON cf.client_id = wc.client_id
             WHERE cf.created_at > NOW() - INTERVAL \'30 days\'
             GROUP BY wc.client_id, wc.company_name`
        );
        
        res.json({
            success: true,
            total: total.rows[0].sum || 0,
            byClient: byClient.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== AUDIT LOG ====================

// Get audit logs
app.get('/api/v1/super/logs', requireSuperAdmin, async (req, res) => {
    try {
        const { limit = 100 } = req.query;
        
        const logs = await pg.query(
            'SELECT * FROM super_admin_logs ORDER BY created_at DESC LIMIT $1',
            [parseInt(limit)]
        );
        
        res.json({
            success: true,
            logs: logs.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== WHITE LABEL PRODUCT PERMISSIONS ====================

// Grant product access to client
app.post('/api/v1/super/client/:clientId/product/:productId/grant', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId, productId } = req.params;
        
        await pg.query(
            `INSERT INTO client_products (client_id, product_id, status, granted_at)
             VALUES ($1, $2, 'active', NOW())
             ON CONFLICT DO UPDATE SET status = 'active'`,
            [clientId, productId]
        );
        
        res.json({
            success: true,
            message: `Product ${productId} granted to client ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Revoke product access from client
app.post('/api/v1/super/client/:clientId/product/:productId/revoke', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId, productId } = req.params;
        
        await pg.query(
            'UPDATE client_products SET status = $1 WHERE client_id = $2 AND product_id = $3',
            ['revoked', clientId, productId]
        );
        
        res.json({
            success: true,
            message: `Product ${productId} revoked from client ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get all products
app.get('/api/v1/super/products', requireSuperAdmin, (req, res) => {
    const products = [
        { id: 'spot', name: 'Spot Trading', description: 'Basic spot exchange' },
        { id: 'futures', name: 'Futures', description: 'USDT-M Futures' },
        { id: 'margin', name: 'Margin Trading', description: 'Up to 125x leverage' },
        { id: 'staking', name: 'Staking', description: 'Lock and earn' },
        { id: 'bridge', name: 'Bridge', description: 'Cross-chain transfers' },
        { id: 'wallet', name: 'Wallet', description: 'Multi-chain wallet' },
        { id: 'launchpad', name: 'Launchpad', description: 'Token sales' },
        { id: 'nft', name: 'NFT Marketplace', description: 'NFT trading' },
        { id: 'p2p', name: 'P2P Trading', description: 'Peer-to-peer' },
        { id: 'copy', name: 'Copy Trading', description: 'Follow traders' }
    ];
    
    res.json({ success: true, products });
});

// ==================== TRADING PAIR MANAGEMENT ====================

// Get client trading pairs
app.get('/api/v1/super/client/:clientId/pairs', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        const pairs = await pg.query(
            'SELECT * FROM trading_pairs WHERE client_id = $1 ORDER BY volume DESC',
            [clientId]
        );
        
        res.json({
            success: true,
            pairs: pairs.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Add trading pair
app.post('/api/v1/super/client/:clientId/pair', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { base, quote, initialPrice, minPrice, maxPrice, minQty, maxQty } = req.body;
        
        const pairId = `${base}/${quote}`.toUpperCase();
        
        await pg.query(
            `INSERT INTO trading_pairs (client_id, pair_id, base, quote, status, created_at)
             VALUES ($1, $2, $3, $4, 'active', NOW())`,
            [clientId, pairId, base, quote]
        );
        
        res.json({
            success: true,
            pair: pairId,
            message: `Trading pair ${pairId} created`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Delist trading pair
app.post('/api/v1/super/client/:clientId/pair/:pairId/delist', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId, pairId } = req.params;
        
        await pg.query(
            'UPDATE trading_pairs SET status = $1 WHERE client_id = $2 AND pair_id = $3',
            ['delisted', clientId, pairId]
        );
        
        res.json({
            success: true,
            message: `Pair ${pairId} has been DELISTED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Resume trading pair
app.post('/api/v1/super/client/:clientId/pair/:pairId/resume', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId, pairId } = req.params;
        
        await pg.query(
            'UPDATE trading_pairs SET status = $1 WHERE client_id = $2 AND pair_id = $3',
            ['active', clientId, pairId]
        );
        
        res.json({
            success: true,
            message: `Pair ${pairId} has been RESUMED`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== TRADING CONTROL ====================

// Pause all trading for client
app.post('/api/v1/super/client/:clientId/trading/pause', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        await redis.set(`trading:${clientId}:status`, 'paused');
        
        res.json({
            success: true,
            message: `Trading paused for client ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Resume trading for client  
app.post('/api/v1/super/client/:clientId/trading/resume', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        await redis.set(`trading:${clientId}:status`, 'active');
        
        res.json({
            success: true,
            message: `Trading resumed for client ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Halt trading for client
app.post('/api/v1/super/client/:clientId/trading/halt', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        await redis.set(`trading:${clientId}:status`, 'halted');
        
        res.json({
            success: true,
            message: `Trading HALTED for client ${clientId}`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== LIQUIDITY MANAGEMENT ====================

// Get liquidity pools
app.get('/api/v1/super/client/:clientId/liquidity', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        
        const pools = await pg.query(
            'SELECT * FROM liquidity_pools WHERE client_id = $1',
            [clientId]
        );
        
        res.json({
            success: true,
            pools: pools.rows
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Add liquidity pool
app.post('/api/v1/super/client/:clientId/liquidity', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId } = req.params;
        const { tokenA, tokenB, amountA, amountB, apr } = req.body;
        
        await pg.query(
            `INSERT INTO liquidity_pools (client_id, token_a, token_b, amount_a, amount_b, apr, created_at)
             VALUES ($1, $2, $3, $4, $5, $6, NOW())`,
            [clientId, tokenA, tokenB, amountA, amountB, apr]
        );
        
        res.json({
            success: true,
            message: `Liquidity pool ${tokenA}-${tokenB} created`
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Remove liquidity pool
app.delete('/api/v1/super/client/:clientId/liquidity/:poolId', requireSuperAdmin, async (req, res) => {
    try {
        const { clientId, poolId } = req.params;
        
        await pg.query(
            'DELETE FROM liquidity_pools WHERE client_id = $1 AND id = $2',
            [clientId, poolId]
        );
        
        res.json({
            success: true,
            message: 'Liquidity pool removed'
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== HEALTH ====================

app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        service: 'TigerEx Super Admin API',
        version: '1.0.0'
    });
});

// Start
const PORT = process.env.PORT || 7000;
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║        TigerEx Super Admin API v1.0                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                         ║
║  Features:                                              ║
║    ✓ Super Admin Authentication                    ║
║    ✓ Client Management (Suspend/Delete/Activate)    ║
║    ✓ User Management (Ban anywhere)               ║
║    ✓ Blockchain Control (Start/Stop/Delete)        ║
║    ✓ Global Actions (Pause/Halt/Resume)            ║
║    ✓ Revenue Management                         ║
║    ✓ Complete Audit Log                         ║
╚═══════════════════════════════════════════════════════════════╝
    `);
});

module.exports = { app, pg, redis };