/**
 * TigerEx Backend Server (Node.js/Express)
 */
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'tigerex-jwt-secret-key';

// Middleware
app.use(cors({ origin: '*', credentials: true }));
app.use(bodyParser.json());

// In-memory database
const db = {
    users: new Map(),
    tokens: new Map(),
    orders: new Map(),
    wallets: new Map(),
    staking: new Map()
};

// Markets data
const markets = {
    'BTCUSDT': { symbol: 'BTCUSDT', price: 67234.50, change24h: 2.34, volume24h: 1250000000 },
    'ETHUSDT': { symbol: 'ETHUSDT', price: 3456.78, change24h: 1.56, volume24h: 890000000 },
    'BNBUSDT': { symbol: 'BNBUSDT', price: 567.89, change24h: -0.45, volume24h: 234000000 },
    'SOLUSDT': { symbol: 'SOLUSDT', price: 145.67, change24h: 5.67, volume24h: 456000000 },
    'XRPUSDT': { symbol: 'XRPUSDT', price: 0.5678, change24h: 2.34, volume24h: 678000000 }
};

// Helpers
const hashPassword = (pwd) => crypto.createHash('sha256').update(pwd).digest('hex');
const generateId = () => crypto.randomUUID();

// Auth Middleware
const auth = (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ success: false, message: 'No token' });
    
    try {
        req.userId = jwt.verify(token, JWT_SECRET).sub;
        next();
    } catch(e) {
        res.status(401).json({ success: false, message: 'Invalid token' });
    }
};

// ==================== AUTH ROUTES ====================

app.post('/api/auth/register', (req, res) => {
    const { identifier, password, referral } = req.body;
    if (!identifier || !password) {
        return res.status(400).json({ success: false, message: 'Missing fields' });
    }
    
    const userId = generateId();
    db.users.set(userId, {
        id: userId,
        identifier,
        passwordHash: hashPassword(password),
        email: identifier.includes('@') ? identifier : null,
        phone: !identifier.includes('@') ? identifier : null,
        referral,
        createdAt: new Date().toISOString()
    });
    
    db.wallets.set(userId, { BTC: 0, USDT: 1000 });
    db.staking.set(userId, []);
    
    res.json({ success: true, user: { id: userId, identifier } });
});

app.post('/api/auth/login', (req, res) => {
    const { identifier, password } = req.body;
    const user = [...db.users.values()].find(u => u.identifier === identifier);
    
    if (!user || user.passwordHash !== hashPassword(password)) {
        return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    
    const token = jwt.sign({ sub: user.id }, JWT_SECRET, { expiresIn: '7d' });
    db.tokens.set(token, user.id);
    
    res.json({ success: true, token, user: { id: user.id, identifier: user.identifier } });
});

app.post('/api/auth/logout', auth, (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    db.tokens.delete(token);
    res.json({ success: true });
});

app.get('/api/auth/session', auth, (req, res) => {
    const user = db.users.get(req.userId);
    res.json({ success: true, user: { id: user.id, identifier: user.identifier } });
});

// ==================== USER ROUTES ====================

app.get('/api/user/profile', auth, (req, res) => {
    const user = db.users.get(req.userId);
    const wallet = db.wallets.get(req.userId);
    const staking = db.staking.get(req.userId);
    res.json({ success: true, profile: user, wallet, staking });
});

// ==================== TRADING ROUTES ====================

app.get('/api/trading/markets', (req, res) => {
    res.json({ success: true, markets: Object.values(markets) });
});

app.get('/api/trading/orderbook/:symbol', (req, res) => {
    const { symbol } = req.params;
    const market = markets[symbol.toUpperCase()];
    if (!market) return res.status(404).json({ success: false, message: 'Not found' });
    
    res.json({
        success: true,
        symbol: symbol.toUpperCase(),
        bids: [[market.price * 0.999, 10], [market.price * 0.998, 20]],
        asks: [[market.price * 1.001, 15], [market.price * 1.002, 25]]
    });
});

app.post('/api/trading/order', auth, (req, res) => {
    const { symbol, side, type, price, amount } = req.body;
    const orderId = generateId();
    const order = {
        id: orderId,
        userId: req.userId,
        symbol,
        side,
        type,
        price,
        amount,
        status: 'pending',
        createdAt: new Date().toISOString()
    };
    db.orders.set(orderId, order);
    res.json({ success: true, order });
});

app.get('/api/trading/orders', auth, (req, res) => {
    const orders = [...db.orders.values()].filter(o => o.userId === req.userId);
    res.json({ success: true, orders });
});

// ==================== WALLET ROUTES ====================

app.get('/api/wallet/balance', auth, (req, res) => {
    const balance = db.wallets.get(req.userId);
    res.json({ success: true, balance });
});

app.get('/api/wallet/addresses', auth, (req, res) => {
    const addresses = {
        BTC: `bc1q${req.userId.replace(/-/g, '').substring(0, 40)}`,
        ETH: `0x${req.userId.replace(/-/g, '').substring(0, 40)}`
    };
    res.json({ success: true, addresses });
});

app.get('/api/wallet/transactions', auth, (req, res) => {
    const transactions = [
        { id: 'tx1', type: 'deposit', amount: 1000, currency: 'USDT', status: 'completed', date: new Date().toISOString() }
    ];
    res.json({ success: true, transactions });
});

// ==================== EARN ROUTES ====================

app.get('/api/earn/products', (req, res) => {
    const products = [
        { id: 'staking-btc', name: 'BTC Staking', apy: 4.5, minAmount: 0.001, lockPeriod: 30 },
        { id: 'staking-eth', name: 'ETH Staking', apy: 3.2, minAmount: 0.01, lockPeriod: 15 }
    ];
    res.json({ success: true, products });
});

app.get('/api/earn/staking', auth, (req, res) => {
    const staking = db.staking.get(req.userId);
    res.json({ success: true, staking });
});

// Root
app.get('/', (req, res) => {
    res.json({ message: 'TigerEx API Server', version: '1.0.0' });
});

app.listen(PORT, () => {
    console.log(`TigerEx server running on port ${PORT}`);
});
