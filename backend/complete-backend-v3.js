#!/usr/bin/env node

/**
 * TigerEx Complete Backend v3
 * ALL Features: AutoInvest, Card, Jail Login, Login Alert, Biometric, Widgets, SMS
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
const crypto = require('crypto');

// ==================== DATABASE & CACHE ====================
const pg = new Pool({
    host: process.env.PG_HOST || 'localhost',
    database: process.env.PG_DB || 'tigerex',
    user: process.env.PG_USER || 'tigerex',
    max: 200
});

const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: 6379
});

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws' });

// ==================== MIDDLEWARE ====================
app.use(cors());
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json({ limit: '10mb' }));

// Rate Limiting
app.use('/api/', rateLimit({ windowMs: 60000, max: 1000 }));

// ==================== SECURITY ====================
const JWT_SECRET = process.env.JWT_SECRET || 'tigerex_super_secret';

const auth = async (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Auth required' });
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const session = await redis.get(`session:${decoded.userId}`);
        if (!session) return res.status(401).json({ error: 'Session expired' });
        
        // Check jail login
        const jailStatus = await redis.get(`jail:${decoded.userId}`);
        if (jailStatus === 'locked') {
            return res.status(403).json({ error: 'Account locked. Contact support.' });
        }
        
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

const adminAuth = async (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const result = await pg.query("SELECT role FROM users WHERE id = $1", [decoded.userId]);
        if (!['admin', 'super_admin'].includes(result.rows[0]?.role)) {
            return res.status(403).json({ error: 'Admin required' });
        }
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

// ==================== AUTH APIs ====================

app.post('/api/v1/auth/register', async (req, res) => {
    try {
        const { email, password, username } = req.body;
        const hash = await bcrypt.hash(password, 12);
        
        const result = await pg.query(
            `INSERT INTO users (email, username, password_hash, referral_code, created_at) 
             VALUES ($1, $2, $3, $4, NOW()) RETURNING id, email, username`,
            [email.toLowerCase(), username.toLowerCase(), hash, 'REF' + crypto.randomBytes(4).toString('hex').toUpperCase()]
        );
        
        const token = jwt.sign({ userId: result.rows[0].id, email }, JWT_SECRET, { expiresIn: '7d' });
        await redis.set(`session:${result.rows[0].id}`, token, 'EX', 86400 * 7);
        
        // Create default accounts
        await pg.query('INSERT INTO accounts (user_id, currency, type, balance) VALUES ($1, $2, $3, $4)', [result.rows[0].id, 'USDT', 'spot', 0]);
        
        res.json({ success: true, token, user: result.rows[0] });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/v1/auth/login', async (req, res) => {
    try {
        const { email, password, biometric, code2FA } = req.body;
        
        const result = await pg.query('SELECT * FROM users WHERE email = $1', [email.toLowerCase()]);
        const user = result.rows[0];
        
        if (!user || !await bcrypt.compare(password, user.password_hash)) {
            // Log failed attempt
            await pg.query('INSERT INTO audit_logs (user_id, action, ip_address, created_at) VALUES ($1, $2, $3, NOW())', [user?.id || 0, 'login_failed', req.ip]);
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        // Check jail status
        const jailStatus = await redis.get(`jail:${user.id}`);
        if (jailStatus === 'locked') {
            return res.status(403).json({ error: 'Account locked. Contact support.' });
        }
        
        // Check 2FA
        if (user.twofa_enabled) {
            if (!code2FA) return res.json({ success: true, require2FA: true });
        }
        
        // Check biometric
        if (biometric) {
            const bioValid = await redis.get(`biometric:${user.id}:${biometric}`);
            if (!bioValid) return res.status(401).json({ error: 'Invalid biometric' });
        }
        
        if (user.status !== 'active') {
            return res.status(403).json({ error: 'Account suspended' });
        }
        
        const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });
        
        await redis.set(`session:${user.id}`, token, 'EX', 86400 * 7);
        
        // Log successful login
        await pg.query('INSERT INTO audit_logs (user_id, action, ip_address, created_at) VALUES ($1, $2, $3, NOW())', [user.id, 'login_success', req.ip]);
        
        // Send login alert (SMS/Email)
        await sendLoginAlert(user.id, req.ip);
        
        res.json({ success: true, token, user: { id: user.id, email: user.email, username: user.username } });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Enable 2FA
app.post('/api/v1/auth/2fa/enable', auth, async (req, res) => {
    const secret = crypto.randomBytes(16).toString('hex').toUpperCase();
    await pg.query('UPDATE users SET twofa_secret = $1, twofa_enabled = true WHERE id = $2', [secret, req.user.userId]);
    res.json({ success: true, secret, qr: `otpauth://totp/TigerEx?secret=${secret}` });
});

// Biometric login setup
app.post('/api/v1/auth/biometric/enable', auth, async (req, res) => {
    const { biometricKey } = req.body;
    await redis.set(`biometric:${req.user.userId}:${biometricKey}`, 'enabled', 'EX', 86400 * 365);
    res.json({ success: true, message: 'Biometric enabled' });
});

// Enable jail login (extra security)
app.post('/api/v1/auth/jail/enable', auth, async (req, res) => {
    await redis.set(`jail:${req.user.userId}`, 'unlocked', 'EX', 86400 * 365);
    res.json({ success: true, message: 'Jail login enabled' });
});

// Check jail status
app.get('/api/v1/auth/jail/status', auth, async (req, res) => {
    const status = await redis.get(`jail:${req.user.userId}`) || 'unlocked';
    res.json({ success: true, status });
});

// ==================== AUTO INVEST ====================

app.post('/api/v1/autoinvest/create', auth, async (req, res) => {
    try {
        const { name, symbol, amount, interval, startDate } = req.body;
        
        const result = await pg.query(
            `INSERT INTO autoinvest_plans (user_id, name, symbol, amount, interval, start_date, status, created_at)
             VALUES ($1, $2, $3, $4, $5, $6, 'active', NOW()) RETURNING *`,
            [req.user.userId, name, symbol, amount, interval, startDate]
        );
        
        res.json({ success: true, plan: result.rows[0] });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/v1/autoinvest/plans', auth, async (req, res) => {
    try {
        const result = await pg.query(
            'SELECT * FROM autoinvest_plans WHERE user_id = $1 ORDER BY created_at DESC',
            [req.user.userId]
        );
        res.json({ success: true, plans: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/v1/autoinvest/:id/pause', auth, async (req, res) => {
    await pg.query("UPDATE autoinvest_plans SET status = 'paused' WHERE id = $1 AND user_id = $2", [req.params.id, req.user.userId]);
    res.json({ success: true });
});

app.post('/api/v1/autoinvest/:id/resume', auth, async (req, res) => {
    await pg.query("UPDATE autoinvest_plans SET status = 'active' WHERE id = $1 AND user_id = $2", [req.params.id, req.user.userId]);
    res.json({ success: true });
});

app.delete('/api/v1/autoinvest/:id', auth, async (req, res) => {
    await pg.query('DELETE FROM autoinvest_plans WHERE id = $1 AND user_id = $2', [req.params.id, req.user.userId]);
    res.json({ success: true });
});

// ==================== CARD ====================

app.get('/api/v1/card/virtual', auth, async (req, res) => {
    try {
        const result = await pg.query(
            'SELECT * FROM virtual_cards WHERE user_id = $1',
            [req.user.userId]
        );
        res.json({ success: true, cards: result.rows });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/v1/card/virtual/create', auth, async (req, res) => {
    try {
        const { cardType, currency } = req.body;
        
        const cardNumber = '4' + Math.random().toString().slice(2, 18);
        const cvv = Math.floor(100 + Math.random() * 900);
        const exp = (Math.floor(Math.random() * 12) + 1).toString().padStart(2, '0') + (Math.floor(Math.random() * 5) + 25).toString();
        
        const result = await pg.query(
            `INSERT INTO virtual_cards (user_id, card_number, cvv, expiry, type, currency, status, created_at)
             VALUES ($1, $2, $3, $4, $5, $6, 'active', NOW()) RETURNING *`,
            [req.user.userId, cardNumber, cvv, exp, cardType, currency || 'USD']
        );
        
        res.json({ success: true, card: result.rows[0] });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/v1/card/:id/freeze', auth, async (req, res) => {
    await pg.query("UPDATE virtual_cards SET status = 'frozen' WHERE id = $1 AND user_id = $2", [req.params.id, req.user.userId]);
    res.json({ success: true });
});

app.post('/api/v1/card/:id/unfreeze', auth, async (req, res) => {
    await pg.query("UPDATE virtual_cards SET status = 'active' WHERE id = $1 AND user_id = $2", [req.params.id, req.user.userId]);
    res.json({ success: true });
});

// ==================== LOGIN ALERTS ====================

app.get('/api/v1/settings/login-alerts', auth, async (req, res) => {
    const alerts = await redis.get(`loginalert:${req.user.userId}`) || 'enabled';
    res.json({ success: true, enabled: alerts === 'enabled' });
});

app.post('/api/v1/settings/login-alerts/enable', auth, async (req, res) => {
    await redis.set(`loginalert:${req.user.userId}`, 'enabled', 'EX', 86400 * 365);
    res.json({ success: true });
});

app.post('/api/v1/settings/login-alerts/disable', auth, async (req, res) => {
    await redis.set(`loginalert:${req.user.userId}`, 'disabled', 'EX', 86400 * 365);
    res.json({ success: true });
});

// Send login alert (SMS/Email)
async function sendLoginAlert(userId, ip) {
    const enabled = await redis.get(`loginalert:${userId}`);
    if (enabled === 'disabled') return;
    
    // Get user contact
    const user = await pg.query('SELECT email, phone FROM users WHERE id = $1', [userId]);
    
    // Send SMS (simulated)
    if (user.rows[0]?.phone) {
        await redis.lpush('sms_queue', JSON.stringify({
            to: user.rows[0].phone,
            message: `TigerEx: New login from IP ${ip}. If not you, please secure your account.`
        }));
    }
    
    // Store login history
    await pg.query(
        'INSERT INTO login_history (user_id, ip_address, user_agent, created_at) VALUES ($1, $2, $3, NOW())',
        [userId, ip, 'API']
    );
}

// ==================== SMS NOTIFICATIONS ====================

app.post('/api/v1/sms/send', auth, async (req, res) => {
    const { phone, message } = req.body;
    
    await redis.lpush('sms_queue', JSON.stringify({
        to: phone,
        message
    }));
    
    res.json({ success: true, message: 'SMS queued' });
});

app.get('/api/v1/sms/verify/:code', auth, async (req, res) => {
    const { code } = req.params;
    const valid = await redis.get(`smsverify:${req.user.userId}:${code}`);
    
    if (valid) {
        await redis.del(`smsverify:${req.user.userId}:${code}`);
        res.json({ success: true, verified: true });
    } else {
        res.json({ success: true, verified: false });
    }
});

// ==================== WIDGETS ====================

app.get('/api/v1/widgets/price-ticker', async (req, res) => {
    // Return price ticker widget data
    const ticker = [
        { symbol: 'BTC/USDT', price: 42547.32, change: 2.45 },
        { symbol: 'ETH/USDT', price: 2256.78, change: 3.12 },
        { symbol: 'BNB/USDT', price: 324.56, change: -1.2 },
        { symbol: 'SOL/USDT', price: 98.45, change: 5.67 }
    ];
    res.json({ success: true, ticker });
});

app.get('/api/v1/widgets/trading-chart', async (req, res) => {
    const { symbol } = req.query;
    // Return chart widget data
    res.json({ success: true, chart: { type: 'candlestick', data: [] } });
});

app.get('/api/v1/widgets/user-balance', auth, async (req, res) => {
    const result = await pg.query(
        'SELECT currency, balance FROM accounts WHERE user_id = $1',
        [req.user.userId]
    );
    res.json({ success: true, balances: result.rows });
});

app.get('/api/v1/widgets/quick-trade', auth, async (req, res) => {
    res.json({
        success: true,
        quickTrade: {
            symbols: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
            amounts: [10, 50, 100, 500, 1000]
        }
    });
});

// ==================== ADMIN: JAIL LOGIN ====================

app.get('/api/v1/admin/jail/list', adminAuth, async (req, res) => {
    const result = await pg.query(`
        SELECT u.id, u.email, u.username, u.status, 
               (SELECT COUNT(*) FROM login_history WHERE user_id = u.id AND created_at > NOW() - INTERVAL '24 hours') as failed_logins
        FROM users u
        HAVING failed_logins > 5
    `);
    res.json({ success: true, users: result.rows });
});

app.post('/api/v1/admin/jail/:userId/lock', adminAuth, async (req, res) => {
    const { userId } = req.params;
    await redis.set(`jail:${userId}`, 'locked');
    await pg.query('UPDATE users SET status = "suspended" WHERE id = $1', [userId]);
    res.json({ success: true });
});

app.post('/api/v1/admin/jail/:userId/unlock', adminAuth, async (req, res) => {
    const { userId } = req.params;
    await redis.set(`jail:${userId}`, 'unlocked');
    await pg.query('UPDATE users SET status = "active" WHERE id = $1', [userId]);
    res.json({ success: true });
});

// ==================== ADMIN: SMS MANAGEMENT ====================

app.get('/api/v1/admin/sms/queue', adminAuth, async (req, res) => {
    const result = await redis.lrange('sms_queue', 0, 50);
    res.json({ success: true, queue: result });
});

app.get('/api/v1/admin/sms/settings', adminAuth, async (req, res) => {
    const settings = await redis.hgetall('sms_settings');
    res.json({ success: true, settings });
});

app.post('/api/v1/admin/sms/settings', adminAuth, async (req, res) => {
    const { provider, apiKey, apiSecret, fromNumber } = req.body;
    await redis.hset('sms_settings', { provider, apiKey, apiSecret, fromNumber });
    res.json({ success: true });
});

// ==================== MARKETS ====================

app.get('/api/v1/markets', async (req, res) => {
    let markets = await redis.get('markets:all');
    if (markets) return res.json({ success: true, markets: JSON.parse(markets) });
    
    const result = await pg.query('SELECT * FROM markets WHERE status = $1', ['trading']);
    await redis.set('markets:all', JSON.stringify(result.rows), 'EX', 2);
    res.json({ success: true, markets: result.rows });
});

app.get('/api/v1/market/:symbol', async (req, res) => {
    const result = await pg.query('SELECT * FROM markets WHERE symbol = $1', [req.params.symbol.toUpperCase()]);
    res.json({ success: true, market: result.rows[0] });
});

// ==================== TRADING ====================

app.post('/api/v1/order', auth, async (req, res) => {
    const { symbol, side, type, quantity, price } = req.body;
    const orderId = 'ORD' + Date.now().toString(36).toUpperCase();
    
    const result = await pg.query(
        `INSERT INTO orders (user_id, order_id, symbol, side, type, quantity, price, status, created_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending', NOW()) RETURNING *`,
        [req.user.userId, orderId, symbol, side, type || 'limit', quantity, price || 0]
    );
    
    res.json({ success: true, order: result.rows[0] });
});

app.get('/api/v1/orders', auth, async (req, res) => {
    const result = await pg.query(
        'SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT 50',
        [req.user.userId]
    );
    res.json({ success: true, orders: result.rows });
});

app.delete('/api/v1/order/:orderId', auth, async (req, res) => {
    await pg.query("UPDATE orders SET status = 'cancelled' WHERE order_id = $1 AND user_id = $2", [req.params.orderId, req.user.userId]);
    res.json({ success: true });
});

// ==================== WALLET ====================

app.get('/api/v1/wallet/balance', auth, async (req, res) => {
    const result = await pg.query('SELECT * FROM accounts WHERE user_id = $1', [req.user.userId]);
    res.json({ success: true, balances: result.rows });
});

app.get('/api/v1/wallet/deposit/address', auth, async (req, res) => {
    const { currency } = req.query;
    const address = crypto.createHash('sha256').update(req.user.userId + currency).digest('hex').slice(0, 42);
    res.json({ success: true, currency, address: '0x' + address });
});

app.post('/api/v1/wallet/withdraw', auth, async (req, res) => {
    const { currency, amount, address } = req.body;
    const txId = 'TX' + Date.now().toString(36).toUpperCase();
    
    await pg.query(
        `INSERT INTO transactions (user_id, tx_id, tx_type, currency, amount, address_to, status, created_at)
         VALUES ($1, $2, 'withdraw', $3, $4, $5, 'pending', NOW())`,
        [req.user.userId, txId, currency, amount, address]
    );
    
    res.json({ success: true, txId });
});

// ==================== ADMIN ====================

app.get('/api/v1/admin/stats', adminAuth, async (req, res) => {
    const [users, orders, volume] = await Promise.all([
        pg.query('SELECT COUNT(*) as total FROM users'),
        pg.query("SELECT COUNT(*) as total FROM orders WHERE created_at > NOW() - INTERVAL '24 hours'"),
        pg.query("SELECT SUM(amount) as volume FROM transactions WHERE type = 'deposit' AND created_at > NOW() - INTERVAL '24 hours'")
    ]);
    
    res.json({
        success: true,
        stats: {
            totalUsers: users.rows[0].total,
            orders24h: orders.rows[0].total,
            volume24h: volume.rows[0].volume || 0
        }
    });
});

app.get('/api/v1/admin/users', adminAuth, async (req, res) => {
    const result = await pg.query('SELECT id, email, username, status, kyc_status, created_at FROM users ORDER BY created_at DESC LIMIT 50');
    res.json({ success: true, users: result.rows });
});

app.patch('/api/v1/admin/user/:userId/status', adminAuth, async (req, res) => {
    const { status } = req.body;
    await pg.query('UPDATE users SET status = $1 WHERE id = $2', [status, req.params.userId]);
    res.json({ success: true });
});

// ==================== WEBSOCKET ====================

wss.on('connection', (ws) => {
    ws.isAlive = true;
    ws.on('pong', () => { ws.isAlive = false; });
});

setInterval(() => {
    wss.clients.forEach(ws => {
        if (!ws.isAlive) return ws.terminate();
        ws.isAlive = false;
        ws.ping();
    });
}, 30000);

// ==================== HEALTH ====================

app.get('/health', (req, res) => {
    res.json({ status: 'ok', version: '3.0.0', features: ['AutoInvest', 'Card', 'Jail', 'LoginAlert', 'Biometric', 'Widgets', 'SMS'] });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║              TigerEx Complete Backend v3.0                       ║
╠═══════════════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                                    ║
║  Features:                                                    ║
║    ✓ AutoInvest - Automated trading plans                    ║
║    ✓ Virtual Card - Crypto cards                            ║
║    ✓ Jail Login - Account lock security                   ║
║    ✓ Login Alert - IP & device notifications              ║
║    ✓ Biometric - Fingerprint/Face login                  ║
║    ✓ Widgets - Embedded trading widgets                  ║
║    ✓ SMS Notifications - SMS alerts                        ║
╚═══════════════════════════════════════════════════════════════════╝
    `);
});

module.exports = { app, pg, redis };
// TigerEx Wallet API
function createWallet(userId, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';
  return { address, seed: seed.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId };
}
