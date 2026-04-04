const express = require('express');
const router = express.Router();
const PaymentService = require('../services/PaymentService');
const StripeService = require('../services/StripeService');
const authMiddleware = require('../middleware/auth');
const {
  validatePaymentCreation,
  validatePaymentProcessing,
} = require('../middleware/validation');
const { asyncHandler } = require('../middleware/errorHandler');

// Create new payment
router.post(
  '/',
  authMiddleware,
  validatePaymentCreation,
  asyncHandler(async (req, res) => {
    const paymentData = {
      ...req.body,
      userId: req.user.userId,
      metadata: {
        ...req.body.metadata,
        ipAddress: req.ip,
        userAgent: req.get('User-Agent'),
        source: 'API',
      },
    };

    const payment = await PaymentService.createPayment(paymentData);

    res.status(201).json({
      success: true,
      message: 'Payment created successfully',
      data: payment.toSafeObject(),
    });
  })
);

// Process payment
router.post(
  '/:paymentId/process',
  authMiddleware,
  validatePaymentProcessing,
  asyncHandler(async (req, res) => {
    const { paymentId } = req.params;

    // Verify payment belongs to user
    const existingPayment = await Payment.findOne({
      paymentId,
      userId: req.user.userId,
    });

    if (!existingPayment) {
      return res.status(404).json({
        success: false,
        message: 'Payment not found',
      });
    }

    const payment = await PaymentService.processPayment(paymentId);

    res.json({
      success: true,
      message: 'Payment processing initiated',
      data: payment.toSafeObject(),
    });
  })
);

// Get payment details
router.get(
  '/:paymentId',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { paymentId } = req.params;

    const payment = await Payment.findOne({
      paymentId,
      userId: req.user.userId,
    });

    if (!payment) {
      return res.status(404).json({
        success: false,
        message: 'Payment not found',
      });
    }

    res.json({
      success: true,
      data: payment.toSafeObject(),
    });
  })
);

// Get user's payment history
router.get(
  '/',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const {
      type,
      method,
      status,
      currency,
      startDate,
      endDate,
      limit = 50,
      page = 1,
    } = req.query;

    const filters = {
      userId: req.user.userId,
    };

    if (type) filters.type = type;
    if (method) filters.method = method;
    if (status) filters.status = status;
    if (currency) filters.currency = currency.toUpperCase();

    if (startDate || endDate) {
      filters.createdAt = {};
      if (startDate) filters.createdAt.$gte = new Date(startDate);
      if (endDate) filters.createdAt.$lte = new Date(endDate);
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const payments = await Payment.find(filters)
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip(skip);

    const total = await Payment.countDocuments(filters);

    res.json({
      success: true,
      data: {
        payments: payments.map((payment) => payment.toSafeObject()),
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

// Cancel payment
router.post(
  '/:paymentId/cancel',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { paymentId } = req.params;
    const { reason } = req.body;

    const payment = await Payment.findOne({
      paymentId,
      userId: req.user.userId,
    });

    if (!payment) {
      return res.status(404).json({
        success: false,
        message: 'Payment not found',
      });
    }

    if (!['PENDING', 'PROCESSING'].includes(payment.status)) {
      return res.status(400).json({
        success: false,
        message: 'Payment cannot be cancelled in current status',
      });
    }

    payment.updateStatus('CANCELLED', req.user.userId, {
      reason: reason || 'User requested cancellation',
    });
    await payment.save();

    res.json({
      success: true,
      message: 'Payment cancelled successfully',
      data: payment.toSafeObject(),
    });
  })
);

// Get payment statistics
router.get(
  '/stats/summary',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { period = '30d' } = req.query;

    const stats = await Payment.getPaymentStats(req.user.userId, period);

    res.json({
      success: true,
      data: {
        period,
        statistics: stats,
      },
    });
  })
);

// Stripe webhook endpoint
router.post(
  '/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  asyncHandler(async (req, res) => {
    const signature = req.headers['stripe-signature'];

    try {
      const result = await StripeService.handleWebhook(req.body, signature);
      res.json(result);
    } catch (error) {
      console.error('Stripe webhook error:', error);
      res.status(400).json({ error: 'Webhook signature verification failed' });
    }
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
      type,
      method,
      status,
      currency,
      startDate,
      endDate,
      limit = 100,
      page = 1,
    } = req.query;

    const filters = {};
    if (userId) filters.userId = userId;
    if (type) filters.type = type;
    if (method) filters.method = method;
    if (status) filters.status = status;
    if (currency) filters.currency = currency.toUpperCase();

    if (startDate || endDate) {
      filters.createdAt = {};
      if (startDate) filters.createdAt.$gte = new Date(startDate);
      if (endDate) filters.createdAt.$lte = new Date(endDate);
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const payments = await Payment.find(filters)
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip(skip);

    const total = await Payment.countDocuments(filters);

    res.json({
      success: true,
      data: {
        payments: payments.map((payment) => payment.toSafeObject()),
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

// Admin: Update payment status
router.patch(
  '/admin/:paymentId/status',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const { paymentId } = req.params;
    const { status, reason } = req.body;

    const payment = await Payment.findOne({ paymentId });
    if (!payment) {
      return res.status(404).json({
        success: false,
        message: 'Payment not found',
      });
    }

    payment.updateStatus(status, req.user.userId, { reason });
    await payment.save();

    res.json({
      success: true,
      message: 'Payment status updated successfully',
      data: payment.toSafeObject(),
    });
  })
);

// Admin: Get payment statistics
router.get(
  '/admin/statistics',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const statistics = await PaymentService.generateStatistics();

    res.json({
      success: true,
      data: statistics,
    });
  })
);

module.exports = router;
