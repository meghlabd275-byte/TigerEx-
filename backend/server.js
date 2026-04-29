/**
 * TigerEx Complete Backend API
 * High-Performance Exchange Platform
 * Target: 500K TPS
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');
const Redis = require('ioredis');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// ==================== DATABASE CONNECTIONS ====================
const pg = new Pool({
    host: process.env.PG_HOST || 'localhost',
    port: process.env.PG_PORT || 5432,
    database: process.env.PG_DB || 'tigerex',
    user: process.env.PG_USER || 'tigerex',
    password: process.env.PG_PASS || 'password',
    max: 100,
    idleTimeoutMillis: 30000
});

const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASS,
    maxRetriesPerRequest: 3
});

const pubRedis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379
});

// ==================== MIDDLEWARE ====================
app.use(cors());
app.use(helmet());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate Limiting
const limiter = rateLimit({
    windowMs: 60 * 1000,
    max: 1000,
    message: { error: 'Too many requests' }
});
app.use('/api/', limiter);

// ==================== AUTH MIDDLEWARE ====================
const JWT_SECRET = process.env.JWT_SECRET || 'tigerex_jwt_secret_2024';

const auth = async (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        
        // Check Redis session
        const session = await redis.get(`session:${decoded.userId}`);
        if (!session) {
            return res.status(401).json({ error: 'Session expired' });
        }
        
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

const adminAuth = async (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const user = await pg.query('SELECT role FROM users WHERE id = $1', [decoded.userId]);
        
        if (user.rows[0]?.role !== 'admin' && user.rows[0]?.role !== 'super_admin') {
            return res.status(403).json({ error: 'Admin access required' });
        }
        
        req.user = decoded;
        req.adminRole = user.rows[0].role;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

// ==================== USER ROUTES ====================

// Register
app.post('/api/auth/register', async (req, res) => {
    try {
        const { email, password, username, referralCode } = req.body;
        
        // Check existing
        const existing = await pg.query('SELECT id FROM users WHERE email = $1 OR username = $2', [email, username]);
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'User already exists' });
        }
        
        const hash = await bcrypt.hash(password, 12);
        const referral = 'REF' + Math.random().toString(36).substr(2, 8).toUpperCase();
        
        const result = await pg.query(
            `INSERT INTO users (email, username, password_hash, referral_code, created_at) 
             VALUES ($1, $2, $3, $4, NOW()) RETURNING id, email, username`,
            [email, username, hash, referral]
        );
        
        const token = jwt.sign({ userId: result.rows[0].id, email }, JWT_SECRET, { expiresIn: '7d' });
        await redis.set(`session:${result.rows[0].id}`, token, 'EX', 86400 * 7);
        
        res.json({ success: true, user: result.rows[0], token });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        const result = await pg.query('SELECT * FROM users WHERE email = $1', [email]);
        const user = result.rows[0];
        
        if (!user || !await bcrypt.compare(password, user.password_hash)) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        if (user.status !== 'active') {
            return res.status(403).json({ error: 'Account suspended' });
        }
        
        const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
        await redis.set(`session:${user.id}`, token, 'EX', 86400 * 7);
        
        // Log action
        await pg.query(
            'INSERT INTO audit_logs (user_id, action, ip_address, user_agent, created_at) VALUES ($1, $2, $3, $4, NOW())',
            [user.id, 'login', req.ip, req.headers['user-agent']]
        );
        
        res.json({ 
            success: true, 
            token, 
            user: { id: user.id, email: user.email, username: user.username, kycStatus: user.kyc_status }
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Logout
app.post('/api/auth/logout', auth, async (req, res) => {
    await redis.del(`session:${req.user.userId}`);
    res.json({ success: true });
});

// Get Markets
app.get('/api/markets', async (req, res) => {
    try {
        // Try Redis first
        let markets = await redis.get('markets:all');
        
        if (markets) {
            return res.json({ success: true, markets: JSON.parse(markets) });
        }
        
        const result = await pg.query(`
            SELECT symbol, base_asset, quote_asset, type, status, price, 
                   price_change_24h, volume_24h, high_24h, low_24h, max_leverage
            FROM markets WHERE status = 'trading' ORDER BY volume_24h DESC
        `);
        
        await redis.set('markets:all', JSON.stringify(result.rows), 'EX', 5);
        res.json({ success: true, markets: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get Single Market
app.get('/api/market/:symbol', async (req, res) => {
    try {
        const { symbol } = req.params;
        
        let market = await redis.get(`market:${symbol}`);
        if (market) {
            return res.json({ success: true, market: JSON.parse(market) });
        }
        
        const result = await pg.query('SELECT * FROM markets WHERE symbol = $1', [symbol]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Market not found' });
        }
        
        await redis.set(`market:${symbol}`, JSON.stringify(result.rows[0]), 'EX', 5);
        res.json({ success: true, market: result.rows[0] });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Place Order
app.post('/api/order', auth, async (req, res) => {
    try {
        const { symbol, side, type, quantity, price, stopPrice } = req.body;
        
        const orderId = 'ORD' + Date.now() + Math.random().toString(36).substr(2, 9).toUpperCase();
        
        // Insert order
        const result = await pg.query(
            `INSERT INTO orders (user_id, market_id, order_id, side, type, price, quantity, status, created_at)
             VALUES ($1, (SELECT id FROM markets WHERE symbol = $2), $3, $4, $5, $6, $7, 'pending', NOW())
             RETURNING id, order_id`,
            [req.user.userId, symbol, orderId, side, type, price || 0, quantity]
        );
        
        // Emit to WebSocket
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({ type: 'order', data: { orderId, symbol, side, quantity, price } }));
            }
        });
        
        res.json({ success: true, orderId: result.rows[0].order_id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Cancel Order
app.delete('/api/order/:orderId', auth, async (req, res) => {
    try {
        const { orderId } = req.params;
        
        await pg.query(
            "UPDATE orders SET status = 'cancelled', updated_at = NOW() WHERE order_id = $1 AND user_id = $2",
            [orderId, req.user.userId]
        );
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get Orders
app.get('/api/orders', auth, async (req, res) => {
    try {
        const { status = 'all', limit = 50, offset = 0 } = req.query;
        
        let query = `SELECT o.*, m.symbol FROM orders o JOIN markets m ON o.market_id = m.id WHERE o.user_id = $1`;
        const params = [req.user.userId];
        
        if (status !== 'all') {
            query += ` AND o.status = $2`;
            params.push(status);
        }
        
        query += ` ORDER BY o.created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
        params.push(parseInt(limit), parseInt(offset));
        
        const result = await pg.query(query, params);
        res.json({ success: true, orders: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get Balance
app.get('/api/wallet/balance', auth, async (req, res) => {
    try {
        let balances = await redis.get(`balance:${req.user.userId}`);
        
        if (balances) {
            return res.json({ success: true, balances: JSON.parse(balances) });
        }
        
        const result = await pg.query(
            'SELECT currency, available_balance, locked_balance FROM accounts WHERE user_id = $1',
            [req.user.userId]
        );
        
        await redis.set(`balance:${req.user.userId}`, JSON.stringify(result.rows), 'EX', 10);
        res.json({ success: true, balances: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Deposit
app.post('/api/wallet/deposit', auth, async (req, res) => {
    try {
        const { currency, amount, txHash } = req.body;
        const txId = 'TX' + Date.now() + Math.random().toString(36).substr(2, 9).toUpperCase();
        
        await pg.query(
            `INSERT INTO transactions (user_id, tx_id, tx_type, currency, amount, tx_hash, status, created_at)
             VALUES ($1, $2, 'deposit', $3, $4, $5, 'pending', NOW())`,
            [req.user.userId, txId, currency, amount, txHash]
        );
        
        // Emit notification
        pubRedis.publish('notifications', JSON.stringify({
            userId: req.user.userId,
            type: 'deposit',
            message: `Deposit of ${amount} ${currency} pending`
        }));
        
        res.json({ success: true, txId });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Withdraw
app.post('/api/wallet/withdraw', auth, async (req, res) => {
    try {
        const { currency, amount, address } = req.body;
        const txId = 'TX' + Date.now() + Math.random().toString(36).substr(2, 9).toUpperCase();
        
        // Check balance
        const balance = await pg.query(
            'SELECT available_balance FROM accounts WHERE user_id = $1 AND currency = $2',
            [req.user.userId, currency]
        );
        
        if (balance.rows.length === 0 || parseFloat(balance.rows[0].available_balance) < amount) {
            return res.status(400).json({ error: 'Insufficient balance' });
        }
        
        await pg.query(
            `INSERT INTO transactions (user_id, tx_id, tx_type, currency, amount, address_to, status, created_at)
             VALUES ($1, $2, 'withdraw', $3, $4, $5, 'pending', NOW())`,
            [req.user.userId, txId, currency, amount, address]
        );
        
        // Lock balance
        await pg.query(
            'UPDATE accounts SET available_balance = available_balance - $1, locked_balance = locked_balance + $1 WHERE user_id = $2 AND currency = $3',
            [amount, req.user.userId, currency]
        );
        
        res.json({ success: true, txId });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// P2P Ads
app.get('/api/p2p/ads', async (req, res) => {
    try {
        const { type, currency, paymentMethod } = req.query;
        
        let query = 'SELECT * FROM p2p_ads WHERE status = $1';
        const params = ['active'];
        
        if (type) {
            params.push(type);
            query += ` AND type = $${params.length}`;
        }
        if (currency) {
            params.push(currency);
            query += ` AND currency = $${params.length}`;
        }
        
        const result = await pg.query(query, params);
        res.json({ success: true, ads: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Create P2P Ad
app.post('/api/p2p/ad', auth, async (req, res) => {
    try {
        const { type, currency, price, minAmount, maxAmount, paymentMethod, terms } = req.body;
        
        const result = await pg.query(
            `INSERT INTO p2p_ads (user_id, type, currency, price, min_amount, max_amount, payment_method, terms, status, created_at)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'active', NOW()) RETURNING id`,
            [req.user.userId, type, currency, price, minAmount, maxAmount, paymentMethod, terms]
        );
        
        res.json({ success: true, adId: result.rows[0].id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Staking Products
app.get('/api/staking/products', async (req, res) => {
    try {
        let products = await redis.get('staking:products');
        
        if (products) {
            return res.json({ success: true, products: JSON.parse(products) });
        }
        
        const result = await pg.query('SELECT * FROM staking_products WHERE status = $1 AND end_time > NOW()', ['active']);
        
        await redis.set('staking:products', JSON.stringify(result.rows), 'EX', 60);
        res.json({ success: true, products: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Stake
app.post('/api/staking/stake', auth, async (req, res) => {
    try {
        const { productId, amount } = req.body;
        
        const result = await pg.query(
            `INSERT INTO staking_positions (user_id, product_id, amount, start_at, end_at, status)
             SELECT $1, $2, $3, NOW(), NOW() + INTERVAL '1 day' * sp.lock_period, 'active'
             FROM staking_products sp WHERE sp.id = $2 AND sp.status = 'active'
             RETURNING id`,
            [req.user.userId, productId, amount]
        );
        
        res.json({ success: true, stakeId: result.rows[0].id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== ADMIN ROUTES ====================

// Dashboard Stats
app.get('/api/admin/stats', adminAuth, async (req, res) => {
    try {
        const stats = await redis.get('admin:stats');
        
        if (stats) {
            return res.json({ success: true, stats: JSON.parse(stats) });
        }
        
        const [users, orders, volume, deposits, withdrawals] = await Promise.all([
            pg.query('SELECT COUNT(*) as total FROM users'),
            pg.query("SELECT COUNT(*) as total FROM orders WHERE created_at > NOW() - INTERVAL '24 hours'"),
            pg.query("SELECT SUM(amount) as volume FROM transactions WHERE type = 'deposit' AND created_at > NOW() - INTERVAL '24 hours'"),
            pg.query("SELECT COUNT(*) as total FROM transactions WHERE type = 'deposit' AND status = 'pending'"),
            pg.query("SELECT COUNT(*) as total FROM transactions WHERE type = 'withdraw' AND status = 'pending'")
        ]);
        
        const result = {
            totalUsers: parseInt(users.rows[0].total),
            orders24h: parseInt(orders.rows[0].total),
            volume24h: parseFloat(volume.rows[0].volume) || 0,
            pendingDeposits: parseInt(deposits.rows[0].total),
            pendingWithdrawals: parseInt(withdrawals.rows[0].total)
        };
        
        await redis.set('admin:stats', JSON.stringify(result), 'EX', 30);
        res.json({ success: true, stats: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Get All Users
app.get('/api/admin/users', adminAuth, async (req, res) => {
    try {
        const { page = 1, limit = 50, status, search } = req.query;
        const offset = (page - 1) * limit;
        
        let query = 'SELECT id, email, username, kyc_status, status, created_at FROM users WHERE 1=1';
        const params = [];
        
        if (status) {
            params.push(status);
            query += ` AND status = $${params.length}`;
        }
        if (search) {
            params.push(`%${search}%`);
            query += ` AND (email LIKE $${params.length} OR username LIKE $${params.length})`;
        }
        
        query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
        params.push(parseInt(limit), offset);
        
        const result = await pg.query(query, params);
        res.json({ success: true, users: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Update User Status
app.patch('/api/admin/user/:userId/status', adminAuth, async (req, res) => {
    try {
        const { userId } = req.params;
        const { status } = req.body;
        
        await pg.query('UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2', [status, userId]);
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// KYC Applications
app.get('/api/admin/kyc', adminAuth, async (req, res) => {
    try {
        const { status = 'pending' } = req.query;
        
        const result = await pg.query(
            'SELECT * FROM kyc_applications WHERE status = $1 ORDER BY submitted_at DESC',
            [status]
        );
        
        res.json({ success: true, applications: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Approve KYC
app.post('/api/admin/kyc/:id/approve', adminAuth, async (req, res) => {
    try {
        const { id } = req.params;
        
        await pg.query(
            "UPDATE kyc_applications SET status = 'approved', reviewed_at = NOW(), reviewer_id = $1 WHERE id = $2",
            [req.user.userId, id]
        );
        
        // Update user KYC level
        const app = await pg.query('SELECT user_id FROM kyc_applications WHERE id = $1', [id]);
        if (app.rows.length > 0) {
            await pg.query(
                "UPDATE users SET kyc_status = 'approved', kyc_level = 2 WHERE id = $1",
                [app.rows[0].user_id]
            );
        }
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Reject KYC
app.post('/api/admin/kyc/:id/reject', adminAuth, async (req, res) => {
    try {
        const { id } = req.params;
        const { reason } = req.body;
        
        await pg.query(
            "UPDATE kyc_applications SET status = 'rejected', reject_reason = $1, reviewed_at = NOW(), reviewer_id = $2 WHERE id = $3",
            [reason, req.user.userId, id]
        );
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Approve Deposit
app.post('/api/admin/deposit/:id/approve', adminAuth, async (req, res) => {
    try {
        const { id } = req.params;
        
        // Get transaction
        const tx = await pg.query('SELECT user_id, currency, amount FROM transactions WHERE id = $1', [id]);
        
        if (tx.rows.length === 0) {
            return res.status(404).json({ error: 'Transaction not found' });
        }
        
        // Update status
        await pg.query("UPDATE transactions SET status = 'completed', completed_at = NOW() WHERE id = $1", [id]);
        
        // Update balance
        await pg.query(
            'UPDATE accounts SET available_balance = available_balance + $1, balance = balance + $1 WHERE user_id = $2 AND currency = $3',
            [tx.rows[0].amount, tx.rows[0].user_id, tx.rows[0].currency]
        );
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Approve Withdrawal
app.post('/api/admin/withdraw/:id/approve', adminAuth, async (req, res) => {
    try {
        const { id } = req.params;
        
        await pg.query("UPDATE transactions SET status = 'processing', completed_at = NOW() WHERE id = $1", [id]);
        
        pubRedis.publish('withdrawals', JSON.stringify({ id, action: 'approve' }));
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Reject Withdrawal
app.post('/api/admin/withdraw/:id/reject', adminAuth, async (req, res) => {
    try {
        const { id } = req.params;
        const { reason } = req.body;
        
        const tx = await pg.query('SELECT user_id, currency, amount FROM transactions WHERE id = $1', [id]);
        
        await pg.query("UPDATE transactions SET status = 'failed' WHERE id = $1", [id]);
        
        // Refund balance
        if (tx.rows.length > 0) {
            await pg.query(
                'UPDATE accounts SET available_balance = available_balance + $1, locked_balance = locked_balance - $1 WHERE user_id = $2 AND currency = $3',
                [tx.rows[0].amount, tx.rows[0].user_id, tx.rows[0].currency]
            );
        }
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Manage Markets
app.post('/api/admin/market', adminAuth, async (req, res) => {
    try {
        const { symbol, baseAsset, quoteAsset, price, maxLeverage } = req.body;
        
        const result = await pg.query(
            `INSERT INTO markets (symbol, base_asset, quote_asset, price, max_leverage, status, created_at)
             VALUES ($1, $2, $3, $4, $5, 'trading', NOW()) RETURNING id`,
            [symbol, baseAsset, quoteAsset, price, maxLeverage]
        );
        
        // Clear cache
        await redis.del('markets:all');
        
        res.json({ success: true, marketId: result.rows[0].id });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Update Market
app.patch('/api/admin/market/:symbol', adminAuth, async (req, res) => {
    try {
        const { symbol } = req.params;
        const { price, status, maxLeverage } = req.body;
        
        let query = 'UPDATE markets SET ';
        const updates = [];
        const params = [];
        
        if (price !== undefined) {
            params.push(price);
            updates.push(`price = $${params.length}`);
        }
        if (status !== undefined) {
            params.push(status);
            updates.push(`status = $${params.length}`);
        }
        if (maxLeverage !== undefined) {
            params.push(maxLeverage);
            updates.push(`max_leverage = $${params.length}`);
        }
        
        params.push(symbol);
        query += updates.join(', ') + ' WHERE symbol = $' + params.length;
        
        await pg.query(query, params);
        
        // Clear cache
        await redis.del(`market:${symbol}`);
        await redis.del('markets:all');
        
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Audit Logs
app.get('/api/admin/audit', adminAuth, async (req, res) => {
    try {
        const { userId, action, limit = 100 } = req.query;
        
        let query = 'SELECT * FROM audit_logs WHERE 1=1';
        const params = [];
        
        if (userId) {
            params.push(userId);
            query += ` AND user_id = $${params.length}`;
        }
        if (action) {
            params.push(`%${action}%`);
            query += ` AND action LIKE $${params.length}`;
        }
        
        query += ` ORDER BY created_at DESC LIMIT $${params.length + 1}`;
        params.push(parseInt(limit));
        
        const result = await pg.query(query, params);
        res.json({ success: true, logs: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ==================== WEBOCKET ====================
wss.on('connection', (ws) => {
    ws.isAlive = true;
    ws.on('pong', () => { ws.isAlive = true; });
    
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            switch (data.type) {
                case 'subscribe':
                    if (data.channel === 'trades') {
                        pubRedis.subscribe('trades');
                    } else if (data.channel === 'orders') {
                        pubRedis.subscribe('orders');
                    }
                    break;
            }
        } catch (e) {}
    });
});

// Heartbeat
setInterval(() => {
    wss.clients.forEach((ws) => {
        if (!ws.isAlive) {
            return ws.terminate();
        }
        ws.isAlive = false;
        ws.ping();
    });
}, 30000);

// Redis subscriptions
pubRedis.on('message', (channel, message) => {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
});

// ==================== HEALTH CHECK ====================
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: Date.now() });
});

// ==================== START SERVER ====================
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║           TigerEx Complete Backend API                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                            ║
║  TPS Target:  500,000                                           ║
║  Database:    PostgreSQL                                        ║
║  Cache:       Redis                                             ║
║  Protocol:    REST + WebSocket                                  ║
╠═══════════════════════════════════════════════════════════════╣
║  Routes:                                                      ║
║    Auth:      /api/auth/*                                      ║
║    Markets:   /api/markets, /api/market/*                     ║
║    Orders:    /api/order, /api/orders                          ║
║    Wallet:    /api/wallet/*                                   ║
║    P2P:       /api/p2p/*                                       ║
║    Staking:   /api/staking/*                                   ║
║    Admin:     /api/admin/*                                     ║
╚═══════════════════════════════════════════════════════════════╝
    `);
});

module.exports = { app, server, pg, redis };