/**
 * TigerEx Admin Node.js Server
 * High-performance admin panel backend with Express
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');
const { createServer } = require('http');
const { Server } = require('socket.io');
const { v4: uuidv4 } = require('uuid');
const winston = require('winston');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

// ============ Configuration ============
const config = {
  port: process.env.PORT || 8002,
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: 5432,
    database: 'tigerex',
    user: process.env.DB_USER || 'tigerex_user',
    password: process.env.DB_PASSWORD
  }
};

// ============ Logging ============
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  transports: [new winston.transports.Console()]
});

// ============ Database ============
const pool = new Pool(config.db);

// ============ Middleware ============
app.use(helmet());
app.use(cors({
  origin: ['https://admin.tigerex.com', 'http://localhost:3000'],
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));
app.use(rateLimit({
  windowMs: 60 * 1000,
  max: 100,
  message: { error: 'Too many requests' }
}));

// ============ Auth Middleware ============
const adminAuth = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'No token' });
    
    const decoded = jwt.verify(token, config.jwtSecret);
    if (!['admin', 'super_admin'].includes(decoded.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    req.admin = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// ============ Routes ============

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: Date.now() });
});

// Login
app.post('/api/v1/admin/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const result = await pool.query(
      'SELECT * FROM admins WHERE email = $1',
      [email]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const admin = result.rows[0];
    const validPassword = await bcrypt.compare(password, admin.password_hash);
    
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const accessToken = jwt.sign(
      { id: admin.id, email: admin.email, role: admin.role },
      config.jwtSecret,
      { expiresIn: '30m' }
    );
    
    const refreshToken = jwt.sign(
      { id: admin.id },
      config.jwtSecret,
      { expiresIn: '7d' }
    );
    
    logger.info(`Admin login: ${email}`);
    
    res.json({ accessToken, refreshToken, admin: { id: admin.id, email: admin.email, role: admin.role } });
  } catch (error) {
    logger.error('Login error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Dashboard Stats
app.get('/api/v1/admin/dashboard/stats', adminAuth, async (req, res) => {
  try {
    const [usersCount, activeUsers, volume24h, pendingKYCs] = await Promise.all([
      pool.query('SELECT COUNT(*) FROM users'),
      pool.query("SELECT COUNT(*) FROM users WHERE last_login > NOW() - INTERVAL '24 hours'"),
      pool.query("SELECT SUM(volume) FROM trades WHERE created_at > NOW() - INTERVAL '24 hours'"),
      pool.query("SELECT COUNT(*) FROM users WHERE kyc_status = 'pending'")
    ]);
    
    res.json({
      totalUsers: parseInt(usersCount.rows[0].count),
      activeUsers: parseInt(activeUsers.rows[0].count),
      volume24h: parseFloat(volume24h.rows[0].sum) || 0,
      pendingKYCs: parseInt(pendingKYCs.rows[0].count)
    });
  } catch (error) {
    logger.error('Dashboard error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Users Management
app.get('/api/v1/admin/users', adminAuth, async (req, res) => {
  try {
    const { page = 1, limit = 50, role, status } = req.query;
    const offset = (page - 1) * limit;
    
    let query = 'SELECT id, email, role, status, kyc_status, created_at FROM users';
    const params = [];
    const conditions = [];
    
    if (role) {
      params.push(role);
      conditions.push(`role = $${params.length}`);
    }
    if (status) {
      params.push(status);
      conditions.push(`status = $${params.length}`);
    }
    
    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }
    
    query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(limit, offset);
    
    const result = await pool.query(query, params);
    const count = await pool.query('SELECT COUNT(*) FROM users');
    
    res.json({
      items: result.rows,
      total: parseInt(count.rows[0].count),
      page: parseInt(page),
      limit: parseInt(limit)
    });
  } catch (error) {
    logger.error('Users error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Update User Status
app.put('/api/v1/admin/users/:userId/status', adminAuth, async (req, res) => {
  try {
    const { userId } = req.params;
    const { status, reason } = req.body;
    
    await pool.query(
      'UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2',
      [status, userId]
    );
    
    // Audit log
    await pool.query(
      'INSERT INTO audit_logs (admin_id, action, target_user, reason, created_at) VALUES ($1, $2, $3, $4, NOW())',
      [req.admin.id, 'update_user_status', userId, reason]
    );
    
    logger.info(`Admin ${req.admin.email} updated user ${userId} status to ${status}`);
    
    res.json({ success: true });
  } catch (error) {
    logger.error('Update status error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Approve KYC
app.post('/api/v1/admin/users/:userId/kyc/approve', adminAuth, async (req, res) => {
  try {
    const { userId } = req.params;
    
    await pool.query(
      "UPDATE users SET kyc_status = 'verified', kyc_verified_at = NOW() WHERE id = $1",
      [userId]
    );
    
    await pool.query(
      'INSERT INTO audit_logs (admin_id, action, target_user, created_at) VALUES ($1, $2, $3, NOW())',
      [req.admin.id, 'approve_kyc', userId]
    );
    
    logger.info(`KYC approved for user ${userId} by ${req.admin.email}`);
    
    res.json({ success: true });
  } catch (error) {
    logger.error('KYC approve error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Trading Pairs Management
app.get('/api/v1/admin/trading/pairs', adminAuth, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM trading_pairs ORDER BY base_asset, quote_asset'
    );
    res.json(result.rows);
  } catch (error) {
    logger.error('Pairs error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create Trading Pair
app.post('/api/v1/admin/trading/pairs', adminAuth, async (req, res) => {
  try {
    const { baseAsset, quoteAsset, pricePrecision, quantityPrecision, minQuantity, makerFee, takerFee } = req.body;
    
    if (req.admin.role !== 'super_admin' && req.admin.role !== 'admin') {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    const id = uuidv4();
    await pool.query(
      `INSERT INTO trading_pairs (id, base_asset, quote_asset, price_precision, quantity_precision, min_quantity, maker_fee, taker_fee, status, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'trading', NOW())`,
      [id, baseAsset, quoteAsset, pricePrecision, quantityPrecision, minQuantity, makerFee, takerFee]
    );
    
    logger.info(`Trading pair ${baseAsset}/${quoteAsset} created by ${req.admin.email}`);
    
    res.json({ id, baseAsset, quoteAsset, status: 'trading' });
  } catch (error) {
    logger.error('Create pair error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Wallet Deposits
app.get('/api/v1/admin/wallet/deposits', adminAuth, async (req, res) => {
  try {
    const { page = 1, limit = 50, status } = req.query;
    const offset = (page - 1) * limit;
    
    let query = `
      SELECT d.id, d.user_id, d.asset, d.amount, d.hash, d.status, d.created_at,
             u.email
      FROM deposits d
      JOIN users u ON d.user_id = u.id
    `;
    const params = [limit, offset];
    
    if (status) {
      query = `SELECT d.id, d.user_id, d.asset, d.amount, d.hash, d.status, d.created_at, u.email
              FROM deposits d JOIN users u ON d.user_id = u.id
              WHERE d.status = $3
              ORDER BY d.created_at DESC LIMIT $1 OFFSET $2`;
      params.unshift(status);
    } else {
      query += ` ORDER BY d.created_at DESC LIMIT $1 OFFSET $2`;
    }
    
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    logger.error('Deposits error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Approve Withdrawal
app.post('/api/v1/admin/wallet/withdrawals/:withdrawalId/approve', adminAuth, async (req, res) => {
  try {
    const { withdrawalId } = req.params;
    
    if (req.admin.role !== 'super_admin' && req.admin.role !== 'liquidity_manager') {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    await pool.query(
      "UPDATE withdrawals SET status = 'processing', approved_by = $1, approved_at = NOW() WHERE id = $2",
      [req.admin.id, withdrawalId]
    );
    
    logger.info(`Withdrawal ${withdrawalId} approved by ${req.admin.email}`);
    
    res.json({ success: true });
  } catch (error) {
    logger.error('Approve withdrawal error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Audit Logs
app.get('/api/v1/admin/audit-logs', adminAuth, async (req, res) => {
  try {
    const { page = 1, limit = 50 } = req.query;
    const offset = (page - 1) * limit;
    
    const result = await pool.query(`
      SELECT a.*, ad.email as admin_email
      FROM audit_logs a
      JOIN admins ad ON a.admin_id = ad.id
      ORDER BY a.created_at DESC
      LIMIT $1 OFFSET $2
    `, [limit, offset]);
    
    res.json(result.rows);
  } catch (error) {
    logger.error('Audit logs error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// ============ WebSocket ============
io.on('connection', (socket) => {
  logger.info(`Admin connected: ${socket.id}`);
  
  socket.on('auth', async (token) => {
    try {
      const decoded = jwt.verify(token, config.jwtSecret);
      if (['admin', 'super_admin'].includes(decoded.role)) {
        socket.data.admin = decoded;
        socket.join('admins');
        socket.emit('authenticated');
      }
    } catch (error) {
      socket.emit('error', 'Invalid token');
    }
  });
  
  socket.on('disconnect', () => {
    logger.info(`Admin disconnected: ${socket.id}`);
  });
});

// Broadcast updates
const broadcastUpdate = (event, data) => {
  io.to('admins').emit(event, data);
};

// ============ Error Handler ============
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// ============ Start Server ============
httpServer.listen(config.port, () => {
  logger.info(`TigerEx Admin Server running on port ${config.port}`);
});

module.exports = { app, httpServer };