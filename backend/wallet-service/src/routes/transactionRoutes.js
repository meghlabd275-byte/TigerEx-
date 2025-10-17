/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

const express = require('express');
const router = express.Router();
const Transaction = require('../models/Transaction');
const authMiddleware = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');

// Get user's transaction history
router.get(
  '/',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const {
      currency,
      type,
      status,
      startDate,
      endDate,
      limit = 50,
      page = 1,
    } = req.query;

    const filters = {
      currency,
      type,
      status,
      startDate,
      endDate,
      limit: parseInt(limit),
      skip: (parseInt(page) - 1) * parseInt(limit),
    };

    const transactions = await Transaction.getTransactionHistory(
      req.user.userId,
      filters
    );

    // Get total count for pagination
    const totalQuery = { userId: req.user.userId };
    if (currency) totalQuery.currency = currency.toUpperCase();
    if (type) totalQuery.type = type;
    if (status) totalQuery.status = status;
    if (startDate || endDate) {
      totalQuery.createdAt = {};
      if (startDate) totalQuery.createdAt.$gte = new Date(startDate);
      if (endDate) totalQuery.createdAt.$lte = new Date(endDate);
    }

    const total = await Transaction.countDocuments(totalQuery);

    res.json({
      success: true,
      data: {
        transactions: transactions.map((tx) => tx.toSafeObject()),
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit)),
        },
      },
    });
  })
);

// Get specific transaction
router.get(
  '/:transactionId',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { transactionId } = req.params;

    const transaction = await Transaction.findOne({
      transactionId: transactionId,
      userId: req.user.userId,
    });

    if (!transaction) {
      return res.status(404).json({
        success: false,
        message: 'Transaction not found',
      });
    }

    res.json({
      success: true,
      data: transaction.toSafeObject(),
    });
  })
);

// Get transaction statistics
router.get(
  '/stats/summary',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { period = '24h' } = req.query;

    const stats = await Transaction.getTransactionStats(
      req.user.userId,
      period
    );

    res.json({
      success: true,
      data: {
        period,
        statistics: stats,
      },
    });
  })
);

// Get pending transactions
router.get(
  '/status/pending',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const pendingTransactions = await Transaction.find({
      userId: req.user.userId,
      status: { $in: ['PENDING', 'PROCESSING'] },
    }).sort({ createdAt: -1 });

    res.json({
      success: true,
      data: pendingTransactions.map((tx) => tx.toSafeObject()),
    });
  })
);

// Admin routes
router.get(
  '/admin/all',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const {
      userId,
      currency,
      type,
      status,
      startDate,
      endDate,
      limit = 100,
      page = 1,
    } = req.query;

    const query = {};
    if (userId) query.userId = userId;
    if (currency) query.currency = currency.toUpperCase();
    if (type) query.type = type;
    if (status) query.status = status;
    if (startDate || endDate) {
      query.createdAt = {};
      if (startDate) query.createdAt.$gte = new Date(startDate);
      if (endDate) query.createdAt.$lte = new Date(endDate);
    }

    const transactions = await Transaction.find(query)
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await Transaction.countDocuments(query);

    res.json({
      success: true,
      data: {
        transactions: transactions.map((tx) => tx.toSafeObject()),
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit)),
        },
      },
    });
  })
);

// Update transaction status (admin only)
router.patch(
  '/:transactionId/status',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const { transactionId } = req.params;
    const { status, reason } = req.body;

    const transaction = await Transaction.findOne({ transactionId });
    if (!transaction) {
      return res.status(404).json({
        success: false,
        message: 'Transaction not found',
      });
    }

    transaction.updateStatus(status, req.user.userId, { reason });
    await transaction.save();

    res.json({
      success: true,
      message: 'Transaction status updated successfully',
      data: transaction.toSafeObject(),
    });
  })
);

// Flag transaction (admin only)
router.post(
  '/:transactionId/flag',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const { transactionId } = req.params;
    const { reason } = req.body;

    const transaction = await Transaction.findOne({ transactionId });
    if (!transaction) {
      return res.status(404).json({
        success: false,
        message: 'Transaction not found',
      });
    }

    transaction.flag(reason, req.user.userId);
    await transaction.save();

    res.json({
      success: true,
      message: 'Transaction flagged successfully',
      data: transaction.toSafeObject(),
    });
  })
);

module.exports = router;
