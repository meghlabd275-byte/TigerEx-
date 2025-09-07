const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const WebSocket = require('ws');
const http = require('http');
const { Pool } = require('pg');
const Redis = require('redis');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

// Initialize Express app
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware
app.use(helmet());
app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || [
      'http://localhost:3000',
    ],
    credentials: true,
  })
);
app.use(express.json({ limit: '10mb' }));

// Database connections
const db = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'tigerex',
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || 'tigerex',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

const redis = Redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
});

// Copy Trading Models
const COPY_TRADING_STATUS = {
  ACTIVE: 'active',
  PAUSED: 'paused',
  STOPPED: 'stopped',
};

const TRADE_SIGNAL_STATUS = {
  PENDING: 'pending',
  EXECUTED: 'executed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
};

const RISK_LEVELS = {
  CONSERVATIVE: 'conservative',
  MODERATE: 'moderate',
  AGGRESSIVE: 'aggressive',
  HIGH_RISK: 'high_risk',
};

// Authentication middleware
const authenticateUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await db.query('SELECT * FROM users WHERE id = $1', [
      decoded.userId,
    ]);

    if (user.rows.length === 0) {
      return res.status(403).json({ error: 'User not found' });
    }

    req.user = user.rows[0];
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'copy-trading-service' });
});

// Get all master traders
app.get('/api/v1/copy-trading/masters', authenticateUser, async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      sort_by = 'total_return',
      order = 'desc',
    } = req.query;
    const offset = (page - 1) * limit;

    const query = `
            SELECT 
                mt.*,
                u.username,
                u.first_name,
                u.last_name,
                COUNT(DISTINCT ct.id) as followers_count,
                AVG(ct.allocated_amount) as avg_allocation,
                SUM(ct.allocated_amount) as total_managed
            FROM master_traders mt
            JOIN users u ON mt.user_id = u.id
            LEFT JOIN copy_trading_subscriptions ct ON mt.id = ct.master_trader_id AND ct.status = 'active'
            WHERE mt.is_active = true AND mt.is_public = true
            GROUP BY mt.id, u.username, u.first_name, u.last_name
            ORDER BY ${sort_by} ${order}
            LIMIT $1 OFFSET $2
        `;

    const result = await db.query(query, [limit, offset]);

    // Get total count
    const countResult = await db.query(`
            SELECT COUNT(*) FROM master_traders mt
            WHERE mt.is_active = true AND mt.is_public = true
        `);

    const masters = result.rows.map((master) => ({
      ...master,
      performance_metrics: JSON.parse(master.performance_metrics || '{}'),
      trading_style: JSON.parse(master.trading_style || '{}'),
      risk_metrics: JSON.parse(master.risk_metrics || '{}'),
    }));

    res.json({
      masters,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: parseInt(countResult.rows[0].count),
        totalPages: Math.ceil(countResult.rows[0].count / limit),
      },
    });
  } catch (error) {
    console.error('Get masters error:', error);
    res.status(500).json({ error: 'Failed to fetch master traders' });
  }
});

// Get master trader details
app.get(
  '/api/v1/copy-trading/masters/:masterId',
  authenticateUser,
  async (req, res) => {
    try {
      const { masterId } = req.params;

      const masterQuery = `
            SELECT 
                mt.*,
                u.username,
                u.first_name,
                u.last_name,
                u.created_at as user_since,
                COUNT(DISTINCT ct.id) as followers_count,
                SUM(ct.allocated_amount) as total_managed,
                AVG(ct.profit_loss_percentage) as avg_follower_return
            FROM master_traders mt
            JOIN users u ON mt.user_id = u.id
            LEFT JOIN copy_trading_subscriptions ct ON mt.id = ct.master_trader_id AND ct.status = 'active'
            WHERE mt.id = $1 AND mt.is_active = true
            GROUP BY mt.id, u.username, u.first_name, u.last_name, u.created_at
        `;

      const masterResult = await db.query(masterQuery, [masterId]);

      if (masterResult.rows.length === 0) {
        return res.status(404).json({ error: 'Master trader not found' });
      }

      const master = masterResult.rows[0];

      // Get recent trades
      const tradesQuery = `
            SELECT 
                ts.*,
                tp.symbol as trading_pair_symbol
            FROM trade_signals ts
            JOIN trading_pairs tp ON ts.trading_pair_id = tp.id
            WHERE ts.master_trader_id = $1
            ORDER BY ts.created_at DESC
            LIMIT 20
        `;

      const tradesResult = await db.query(tradesQuery, [masterId]);

      // Get performance history
      const performanceQuery = `
            SELECT * FROM master_trader_performance
            WHERE master_trader_id = $1
            ORDER BY date DESC
            LIMIT 30
        `;

      const performanceResult = await db.query(performanceQuery, [masterId]);

      res.json({
        master: {
          ...master,
          performance_metrics: JSON.parse(master.performance_metrics || '{}'),
          trading_style: JSON.parse(master.trading_style || '{}'),
          risk_metrics: JSON.parse(master.risk_metrics || '{}'),
        },
        recent_trades: tradesResult.rows,
        performance_history: performanceResult.rows,
      });
    } catch (error) {
      console.error('Get master details error:', error);
      res.status(500).json({ error: 'Failed to fetch master trader details' });
    }
  }
);

// Subscribe to copy trading
app.post(
  '/api/v1/copy-trading/subscribe',
  authenticateUser,
  async (req, res) => {
    try {
      const {
        master_trader_id,
        allocated_amount,
        copy_percentage,
        max_trade_amount,
        stop_loss_percentage,
        take_profit_percentage,
        risk_management_settings,
      } = req.body;

      // Validate inputs
      if (!master_trader_id || !allocated_amount || allocated_amount <= 0) {
        return res
          .status(400)
          .json({ error: 'Invalid subscription parameters' });
      }

      // Check if master trader exists and is active
      const masterResult = await db.query(
        'SELECT * FROM master_traders WHERE id = $1 AND is_active = true',
        [master_trader_id]
      );

      if (masterResult.rows.length === 0) {
        return res
          .status(404)
          .json({ error: 'Master trader not found or inactive' });
      }

      // Check user balance
      const balanceResult = await db.query(
        `
            SELECT balance FROM wallets 
            WHERE user_id = $1 AND currency_id = (
                SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'
            )
        `,
        [req.user.id]
      );

      if (
        balanceResult.rows.length === 0 ||
        balanceResult.rows[0].balance < allocated_amount
      ) {
        return res.status(400).json({ error: 'Insufficient balance' });
      }

      // Check if already subscribed
      const existingSubscription = await db.query(
        'SELECT * FROM copy_trading_subscriptions WHERE follower_id = $1 AND master_trader_id = $2 AND status = $3',
        [req.user.id, master_trader_id, COPY_TRADING_STATUS.ACTIVE]
      );

      if (existingSubscription.rows.length > 0) {
        return res
          .status(400)
          .json({ error: 'Already subscribed to this master trader' });
      }

      const subscriptionId = uuidv4();

      await db.query('BEGIN');

      // Create subscription
      await db.query(
        `
            INSERT INTO copy_trading_subscriptions 
            (id, follower_id, master_trader_id, allocated_amount, copy_percentage, 
             max_trade_amount, stop_loss_percentage, take_profit_percentage, 
             risk_management_settings, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
        `,
        [
          subscriptionId,
          req.user.id,
          master_trader_id,
          allocated_amount,
          copy_percentage || 100,
          max_trade_amount,
          stop_loss_percentage,
          take_profit_percentage,
          JSON.stringify(risk_management_settings || {}),
          COPY_TRADING_STATUS.ACTIVE,
        ]
      );

      // Lock allocated funds
      await db.query(
        `
            UPDATE wallets 
            SET locked_balance = locked_balance + $1
            WHERE user_id = $2 AND currency_id = (
                SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'
            )
        `,
        [allocated_amount, req.user.id]
      );

      await db.query('COMMIT');

      // Send notification to master trader
      await sendNotification(masterResult.rows[0].user_id, {
        type: 'new_follower',
        title: 'New Follower',
        message: `${req.user.username} started copying your trades with $${allocated_amount}`,
        data: { subscription_id: subscriptionId },
      });

      res.json({
        subscription_id: subscriptionId,
        message: 'Successfully subscribed to copy trading',
      });
    } catch (error) {
      await db.query('ROLLBACK');
      console.error('Subscribe error:', error);
      res.status(500).json({ error: 'Failed to subscribe to copy trading' });
    }
  }
);

// Get user's copy trading subscriptions
app.get(
  '/api/v1/copy-trading/subscriptions',
  authenticateUser,
  async (req, res) => {
    try {
      const query = `
            SELECT 
                cts.*,
                mt.strategy_name,
                mt.total_return,
                mt.win_rate,
                mt.max_drawdown,
                u.username as master_username
            FROM copy_trading_subscriptions cts
            JOIN master_traders mt ON cts.master_trader_id = mt.id
            JOIN users u ON mt.user_id = u.id
            WHERE cts.follower_id = $1
            ORDER BY cts.created_at DESC
        `;

      const result = await db.query(query, [req.user.id]);

      const subscriptions = result.rows.map((sub) => ({
        ...sub,
        risk_management_settings: JSON.parse(
          sub.risk_management_settings || '{}'
        ),
      }));

      res.json({ subscriptions });
    } catch (error) {
      console.error('Get subscriptions error:', error);
      res.status(500).json({ error: 'Failed to fetch subscriptions' });
    }
  }
);

// Update subscription settings
app.put(
  '/api/v1/copy-trading/subscriptions/:subscriptionId',
  authenticateUser,
  async (req, res) => {
    try {
      const { subscriptionId } = req.params;
      const {
        allocated_amount,
        copy_percentage,
        max_trade_amount,
        stop_loss_percentage,
        take_profit_percentage,
        risk_management_settings,
        status,
      } = req.body;

      // Get current subscription
      const currentSub = await db.query(
        'SELECT * FROM copy_trading_subscriptions WHERE id = $1 AND follower_id = $2',
        [subscriptionId, req.user.id]
      );

      if (currentSub.rows.length === 0) {
        return res.status(404).json({ error: 'Subscription not found' });
      }

      const current = currentSub.rows[0];

      await db.query('BEGIN');

      // If changing allocated amount, adjust locked balance
      if (allocated_amount && allocated_amount !== current.allocated_amount) {
        const difference = allocated_amount - current.allocated_amount;

        if (difference > 0) {
          // Check if user has sufficient balance
          const balanceResult = await db.query(
            `
                    SELECT balance FROM wallets 
                    WHERE user_id = $1 AND currency_id = (
                        SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'
                    )
                `,
            [req.user.id]
          );

          if (
            balanceResult.rows.length === 0 ||
            balanceResult.rows[0].balance < difference
          ) {
            await db.query('ROLLBACK');
            return res
              .status(400)
              .json({ error: 'Insufficient balance for increased allocation' });
          }
        }

        // Update locked balance
        await db.query(
          `
                UPDATE wallets 
                SET locked_balance = locked_balance + $1
                WHERE user_id = $2 AND currency_id = (
                    SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'
                )
            `,
          [difference, req.user.id]
        );
      }

      // Update subscription
      const updateFields = [];
      const updateValues = [];
      let paramCount = 0;

      if (allocated_amount !== undefined) {
        updateFields.push(`allocated_amount = $${++paramCount}`);
        updateValues.push(allocated_amount);
      }
      if (copy_percentage !== undefined) {
        updateFields.push(`copy_percentage = $${++paramCount}`);
        updateValues.push(copy_percentage);
      }
      if (max_trade_amount !== undefined) {
        updateFields.push(`max_trade_amount = $${++paramCount}`);
        updateValues.push(max_trade_amount);
      }
      if (stop_loss_percentage !== undefined) {
        updateFields.push(`stop_loss_percentage = $${++paramCount}`);
        updateValues.push(stop_loss_percentage);
      }
      if (take_profit_percentage !== undefined) {
        updateFields.push(`take_profit_percentage = $${++paramCount}`);
        updateValues.push(take_profit_percentage);
      }
      if (risk_management_settings !== undefined) {
        updateFields.push(`risk_management_settings = $${++paramCount}`);
        updateValues.push(JSON.stringify(risk_management_settings));
      }
      if (status !== undefined) {
        updateFields.push(`status = $${++paramCount}`);
        updateValues.push(status);
      }

      updateFields.push(`updated_at = NOW()`);
      updateValues.push(subscriptionId, req.user.id);

      const updateQuery = `
            UPDATE copy_trading_subscriptions 
            SET ${updateFields.join(', ')}
            WHERE id = $${paramCount + 1} AND follower_id = $${paramCount + 2}
        `;

      await db.query(updateQuery, updateValues);

      await db.query('COMMIT');

      res.json({ message: 'Subscription updated successfully' });
    } catch (error) {
      await db.query('ROLLBACK');
      console.error('Update subscription error:', error);
      res.status(500).json({ error: 'Failed to update subscription' });
    }
  }
);

// Unsubscribe from copy trading
app.delete(
  '/api/v1/copy-trading/subscriptions/:subscriptionId',
  authenticateUser,
  async (req, res) => {
    try {
      const { subscriptionId } = req.params;

      // Get subscription details
      const subResult = await db.query(
        'SELECT * FROM copy_trading_subscriptions WHERE id = $1 AND follower_id = $2',
        [subscriptionId, req.user.id]
      );

      if (subResult.rows.length === 0) {
        return res.status(404).json({ error: 'Subscription not found' });
      }

      const subscription = subResult.rows[0];

      await db.query('BEGIN');

      // Update subscription status
      await db.query(
        'UPDATE copy_trading_subscriptions SET status = $1, updated_at = NOW() WHERE id = $2',
        [COPY_TRADING_STATUS.STOPPED, subscriptionId]
      );

      // Unlock allocated funds
      await db.query(
        `
            UPDATE wallets 
            SET locked_balance = locked_balance - $1
            WHERE user_id = $2 AND currency_id = (
                SELECT id FROM cryptocurrencies WHERE symbol = 'USDT'
            )
        `,
        [subscription.allocated_amount, req.user.id]
      );

      // Close any open copied positions
      await closeOpenPositions(subscriptionId);

      await db.query('COMMIT');

      res.json({ message: 'Successfully unsubscribed from copy trading' });
    } catch (error) {
      await db.query('ROLLBACK');
      console.error('Unsubscribe error:', error);
      res
        .status(500)
        .json({ error: 'Failed to unsubscribe from copy trading' });
    }
  }
);

// Apply to become a master trader
app.post(
  '/api/v1/copy-trading/apply-master',
  authenticateUser,
  async (req, res) => {
    try {
      const {
        strategy_name,
        strategy_description,
        trading_style,
        risk_level,
        minimum_followers,
        performance_fee_percentage,
        track_record,
      } = req.body;

      // Check if user already has an application or is already a master
      const existingResult = await db.query(
        'SELECT * FROM master_traders WHERE user_id = $1',
        [req.user.id]
      );

      if (existingResult.rows.length > 0) {
        return res
          .status(400)
          .json({ error: 'Already applied or approved as master trader' });
      }

      // Check user's trading history and KYC status
      if (req.user.kyc_level < 2) {
        return res
          .status(400)
          .json({ error: 'KYC level 2 required to become a master trader' });
      }

      const applicationId = uuidv4();

      await db.query(
        `
            INSERT INTO master_traders 
            (id, user_id, strategy_name, strategy_description, trading_style, 
             risk_level, minimum_followers, performance_fee_percentage, 
             track_record, is_active, is_public, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, false, false, 'pending', NOW(), NOW())
        `,
        [
          applicationId,
          req.user.id,
          strategy_name,
          strategy_description,
          JSON.stringify(trading_style),
          risk_level,
          minimum_followers || 0,
          performance_fee_percentage || 0,
          JSON.stringify(track_record || {}),
        ]
      );

      // Notify admin for review
      await notifyAdminMasterApplication(applicationId);

      res.json({
        application_id: applicationId,
        message: 'Master trader application submitted successfully',
      });
    } catch (error) {
      console.error('Apply master error:', error);
      res
        .status(500)
        .json({ error: 'Failed to submit master trader application' });
    }
  }
);

// Get copy trading analytics
app.get(
  '/api/v1/copy-trading/analytics',
  authenticateUser,
  async (req, res) => {
    try {
      const { timeframe = '30d' } = req.query;

      // Get user's copy trading performance
      const performanceQuery = `
            SELECT 
                cts.id,
                cts.allocated_amount,
                cts.profit_loss_amount,
                cts.profit_loss_percentage,
                mt.strategy_name,
                u.username as master_username
            FROM copy_trading_subscriptions cts
            JOIN master_traders mt ON cts.master_trader_id = mt.id
            JOIN users u ON mt.user_id = u.id
            WHERE cts.follower_id = $1 AND cts.status = 'active'
        `;

      const performanceResult = await db.query(performanceQuery, [req.user.id]);

      // Get trade history
      const tradesQuery = `
            SELECT 
                ct.*,
                tp.symbol as trading_pair_symbol,
                mt.strategy_name
            FROM copied_trades ct
            JOIN trade_signals ts ON ct.original_signal_id = ts.id
            JOIN trading_pairs tp ON ts.trading_pair_id = tp.id
            JOIN master_traders mt ON ts.master_trader_id = mt.id
            WHERE ct.follower_id = $1
            ORDER BY ct.created_at DESC
            LIMIT 50
        `;

      const tradesResult = await db.query(tradesQuery, [req.user.id]);

      // Calculate summary statistics
      const totalAllocated = performanceResult.rows.reduce(
        (sum, sub) => sum + parseFloat(sub.allocated_amount),
        0
      );
      const totalPnL = performanceResult.rows.reduce(
        (sum, sub) => sum + parseFloat(sub.profit_loss_amount || 0),
        0
      );
      const avgReturn =
        performanceResult.rows.length > 0
          ? performanceResult.rows.reduce(
              (sum, sub) => sum + parseFloat(sub.profit_loss_percentage || 0),
              0
            ) / performanceResult.rows.length
          : 0;

      res.json({
        summary: {
          total_allocated: totalAllocated,
          total_pnl: totalPnL,
          average_return: avgReturn,
          active_subscriptions: performanceResult.rows.length,
        },
        subscriptions: performanceResult.rows,
        recent_trades: tradesResult.rows,
      });
    } catch (error) {
      console.error('Get analytics error:', error);
      res.status(500).json({ error: 'Failed to fetch copy trading analytics' });
    }
  }
);

// WebSocket for real-time updates
wss.on('connection', (ws, req) => {
  console.log('Copy trading WebSocket connected');

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      handleCopyTradingWebSocketMessage(ws, data);
    } catch (error) {
      console.error('WebSocket message error:', error);
    }
  });

  ws.on('close', () => {
    console.log('Copy trading WebSocket disconnected');
  });
});

// Trade Signal Processing (Background Service)
class TradeSignalProcessor {
  constructor() {
    this.isProcessing = false;
  }

  async start() {
    if (this.isProcessing) return;

    this.isProcessing = true;
    console.log('Trade signal processor started');

    // Process signals every 5 seconds
    setInterval(async () => {
      await this.processTradeSignals();
    }, 5000);
  }

  async processTradeSignals() {
    try {
      // Get pending trade signals
      const signalsResult = await db.query(
        `
                SELECT ts.*, mt.user_id as master_user_id
                FROM trade_signals ts
                JOIN master_traders mt ON ts.master_trader_id = mt.id
                WHERE ts.status = $1 AND ts.created_at > NOW() - INTERVAL '1 hour'
                ORDER BY ts.created_at ASC
            `,
        [TRADE_SIGNAL_STATUS.PENDING]
      );

      for (const signal of signalsResult.rows) {
        await this.executeSignalForFollowers(signal);
      }
    } catch (error) {
      console.error('Process trade signals error:', error);
    }
  }

  async executeSignalForFollowers(signal) {
    try {
      // Get active followers of this master trader
      const followersResult = await db.query(
        `
                SELECT * FROM copy_trading_subscriptions
                WHERE master_trader_id = $1 AND status = $2
            `,
        [signal.master_trader_id, COPY_TRADING_STATUS.ACTIVE]
      );

      for (const follower of followersResult.rows) {
        await this.executeCopiedTrade(signal, follower);
      }

      // Mark signal as executed
      await db.query(
        'UPDATE trade_signals SET status = $1, updated_at = NOW() WHERE id = $2',
        [TRADE_SIGNAL_STATUS.EXECUTED, signal.id]
      );
    } catch (error) {
      console.error('Execute signal error:', error);

      // Mark signal as failed
      await db.query(
        'UPDATE trade_signals SET status = $1, updated_at = NOW() WHERE id = $2',
        [TRADE_SIGNAL_STATUS.FAILED, signal.id]
      );
    }
  }

  async executeCopiedTrade(signal, followerSubscription) {
    try {
      // Calculate trade size based on allocation and copy percentage
      const baseTradeSize = parseFloat(signal.quantity);
      const allocationRatio =
        parseFloat(followerSubscription.allocated_amount) / 10000; // Assuming master has $10k base
      const copyPercentage =
        parseFloat(followerSubscription.copy_percentage) / 100;

      let tradeSize = baseTradeSize * allocationRatio * copyPercentage;

      // Apply max trade amount limit
      if (
        followerSubscription.max_trade_amount &&
        tradeSize > followerSubscription.max_trade_amount
      ) {
        tradeSize = followerSubscription.max_trade_amount;
      }

      // Check if follower has sufficient balance
      const balanceResult = await db.query(
        `
                SELECT balance FROM wallets 
                WHERE user_id = $1 AND currency_id = (
                    SELECT quote_currency_id FROM trading_pairs WHERE id = $2
                )
            `,
        [followerSubscription.follower_id, signal.trading_pair_id]
      );

      if (
        balanceResult.rows.length === 0 ||
        balanceResult.rows[0].balance < tradeSize * signal.price
      ) {
        console.log(
          `Insufficient balance for follower ${followerSubscription.follower_id}`
        );
        return;
      }

      // Create copied trade order
      const copiedTradeId = uuidv4();

      await db.query(
        `
                INSERT INTO copied_trades 
                (id, follower_id, master_trader_id, original_signal_id, subscription_id,
                 trading_pair_id, order_type, side, quantity, price, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'pending', NOW(), NOW())
            `,
        [
          copiedTradeId,
          followerSubscription.follower_id,
          signal.master_trader_id,
          signal.id,
          followerSubscription.id,
          signal.trading_pair_id,
          signal.order_type,
          signal.side,
          tradeSize,
          signal.price,
        ]
      );

      // Execute the actual trade through trading engine
      await this.executeTradeOrder({
        id: copiedTradeId,
        user_id: followerSubscription.follower_id,
        trading_pair_id: signal.trading_pair_id,
        order_type: signal.order_type,
        side: signal.side,
        quantity: tradeSize,
        price: signal.price,
        is_copy_trade: true,
      });

      console.log(
        `Executed copied trade ${copiedTradeId} for follower ${followerSubscription.follower_id}`
      );
    } catch (error) {
      console.error('Execute copied trade error:', error);
    }
  }

  async executeTradeOrder(order) {
    try {
      // Call trading engine API to execute the order
      const response = await axios.post(
        `${process.env.TRADING_ENGINE_URL}/api/v1/orders`,
        {
          user_id: order.user_id,
          trading_pair_id: order.trading_pair_id,
          order_type: order.order_type,
          side: order.side,
          quantity: order.quantity,
          price: order.price,
          is_copy_trade: true,
          copy_trade_id: order.id,
        },
        {
          headers: {
            Authorization: `Bearer ${process.env.INTERNAL_API_TOKEN}`,
          },
        }
      );

      if (response.data.success) {
        // Update copied trade status
        await db.query(
          'UPDATE copied_trades SET status = $1, order_id = $2, updated_at = NOW() WHERE id = $3',
          ['executed', response.data.order_id, order.id]
        );
      } else {
        throw new Error(response.data.error || 'Trade execution failed');
      }
    } catch (error) {
      console.error('Execute trade order error:', error);

      // Mark copied trade as failed
      await db.query(
        'UPDATE copied_trades SET status = $1, error_message = $2, updated_at = NOW() WHERE id = $3',
        ['failed', error.message, order.id]
      );
    }
  }
}

// Helper functions
async function sendNotification(userId, notification) {
  try {
    await axios.post(
      `${process.env.NOTIFICATION_SERVICE_URL}/api/v1/notifications`,
      {
        user_id: userId,
        ...notification,
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.INTERNAL_API_TOKEN}`,
        },
      }
    );
  } catch (error) {
    console.error('Send notification error:', error);
  }
}

async function notifyAdminMasterApplication(applicationId) {
  // Implementation for notifying admin about new master trader application
  console.log(`New master trader application: ${applicationId}`);
}

async function closeOpenPositions(subscriptionId) {
  // Implementation for closing open positions when unsubscribing
  console.log(`Closing positions for subscription: ${subscriptionId}`);
}

function handleCopyTradingWebSocketMessage(ws, data) {
  // Handle real-time copy trading WebSocket messages
  switch (data.type) {
    case 'subscribe_signals':
      // Subscribe to trade signals
      break;
    case 'subscribe_performance':
      // Subscribe to performance updates
      break;
  }
}

// Start trade signal processor
const signalProcessor = new TradeSignalProcessor();
signalProcessor.start();

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Copy trading service error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 3010;
server.listen(PORT, () => {
  console.log(`Copy Trading Service running on port ${PORT}`);
});

module.exports = app;
