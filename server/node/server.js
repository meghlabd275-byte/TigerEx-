/**
 * TigerEx Backend Server - Node.js
 * Test Code: 727752
 */
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'tigerex-jwt-secret-key';

// TEST CODES
const TEST_CODE = '727752';
const TOTP_SECRET = 'JBSWY3DPEHPK3PXP';

app.use(cors({ origin: '*', credentials: true }));
app.use(express.json());

// In-memory database
const db = {
    users: new Map(),
    tokens: new Map()
};

const markets = {
    'BTCUSDT': { symbol: 'BTCUSDT', price: 67234.50, change24h: 2.34 },
    'ETHUSDT': { symbol: 'ETHUSDT', price: 3456.78, change24h: 1.56 }
};

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

// Routes
app.post('/api/auth/register', (req, res) => {
    const { identifier, password } = req.body;
    const userId = crypto.randomUUID();
    db.users.set(userId, {
        id: userId,
        identifier,
        passwordHash: crypto.createHash('sha256').update(password).digest('hex'),
        email_verified: false,
        phone_verified: false,
        kyc_verified: false
    });
    res.json({ success: true, message: 'Registered', test_code: TEST_CODE });
});

app.post('/api/auth/login', (req, res) => {
    const { identifier, password } = req.body;
    const user = [...db.users.values()].find(u => u.identifier === identifier);
    if (!user) return res.status(401).json({ success: false, message: 'Invalid' });
    const token = jwt.sign({ sub: user.id }, JWT_SECRET, { expiresIn: '7d' });
    res.json({ success: true, token, user: { id: user.id, identifier: user.identifier }, test_code: TEST_CODE });
});

// Email Verification
app.post('/api/auth/send-email-code', (req, res) => {
    res.json({ success: true, message: 'Code sent', test_code: TEST_CODE });
});

app.post('/api/auth/verify-email', (req, res) => {
    const { code } = req.body;
    if (code === TEST_CODE) return res.json({ success: true, message: 'Email verified', test_code: TEST_CODE });
    res.status(400).json({ success: false, message: 'Invalid code' });
});

// Phone Verification
app.post('/api/auth/send-phone-code', (req, res) => {
    res.json({ success: true, message: 'Code sent', test_code: TEST_CODE });
});

app.post('/api/auth/verify-phone', (req, res) => {
    const { code } = req.body;
    if (code === TEST_CODE) return res.json({ success: true, message: 'Phone verified', test_code: TEST_CODE });
    res.status(400).json({ success: false, message: 'Invalid code' });
});

// 2FA/TOTP
app.post('/api/auth/enable-2fa', auth, (req, res) => {
    res.json({ success: true, secret: TOTP_SECRET, test_code: TEST_CODE });
});

app.post('/api/auth/verify-2fa', (req, res) => {
    const { code } = req.body;
    if (code === TEST_CODE) return res.json({ success: true, message: '2FA verified', test_code: TEST_CODE });
    res.status(400).json({ success: false, message: 'Invalid 2FA code' });
});

// KYC
app.post('/api/kyc/submit', auth, (req, res) => {
    const user = db.users.get(req.userId);
    if (user) user.kyc_verified = true;
    res.json({ success: true, reference: 'KYC-' + crypto.randomUUID().hex(3).toUpperCase() });
});

// Trading
app.get('/api/trading/markets', (req, res) => {
    res.json({ success: true, markets: Object.values(markets) });
});

app.get('/api/wallet/balance', auth, (req, res) => {
    res.json({ success: true, balance: { BTC: 1.5, USDT: 10000 } });
});

// Root
app.get('/', (req, res) => {
    res.json({ message: 'TigerEx API - TEST MODE', test_code: TEST_CODE });
});

app.listen(PORT, () => console.log(`TigerEx server on ${PORT} - Test code: ${TEST_CODE}`));
