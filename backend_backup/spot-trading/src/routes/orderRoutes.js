const express = require('express');
const router = express.Router();
const Order = require('../models/Order');
const TradingEngine = require('../services/TradingEngine');
const authMiddleware = require('../middleware/auth');
const {
  validateOrder,
  validateCancelOrder,
} = require('../middleware/validation');
const { asyncHandler } = require('../middleware/errorHandler');

// Place new order
router.post(
  '/',
  authMiddleware,
  validateOrder,
  asyncHandler(async (req, res) => {
    const {
      symbol,
      side,
      type,
      quantity,
      price,
      stopPrice,
      timeInForce,
      clientOrderId,
    } = req.body;

    // Create order object
    const orderData = {
      userId: req.user.userId,
      symbol: symbol.toUpperCase(),
      baseAsset: symbol.substring(0, symbol.length - 4), // Assuming USDT pairs
      quoteAsset: 'USDT',
      side: side.toUpperCase(),
      type: type.toUpperCase(),
      quantity,
      timeInForce: timeInForce || 'GTC',
      source: 'API',
      ipAddress: req.ip,
      userAgent: req.get('User-Agent'),
    };

    if (price) orderData.price = price;
    if (stopPrice) orderData.stopPrice = stopPrice;
    if (clientOrderId) orderData.clientOrderId = clientOrderId;

    // Create order in database
    const order = new Order(orderData);
    await order.save();

    // Process order through trading engine
    const result = await TradingEngine.processOrder(order);

    res.status(201).json({
      success: true,
      message: 'Order placed successfully',
      data: {
        orderId: order.orderId,
        clientOrderId: order.clientOrderId,
        symbol: order.symbol,
        side: order.side,
        type: order.type,
        quantity: order.quantity.toString(),
        price: order.price?.toString(),
        status: order.status,
        fills: order.fills,
        executedQuantity: order.executedQuantity.toString(),
        cumulativeQuoteQuantity: order.cumulativeQuoteQuantity.toString(),
        orderTime: order.orderTime,
        result,
      },
    });
  })
);

// Get user's active orders
router.get(
  '/active',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { symbol, limit = 50 } = req.query;

    const query = {
      userId: req.user.userId,
      status: { $in: ['NEW', 'PARTIALLY_FILLED'] },
      isWorking: true,
    };

    if (symbol) {
      query.symbol = symbol.toUpperCase();
    }

    const orders = await Order.find(query)
      .sort({ orderTime: -1 })
      .limit(parseInt(limit))
      .select('-fills');

    res.json({
      success: true,
      data: orders.map((order) => order.toSafeObject()),
    });
  })
);

// Get order by ID
router.get(
  '/:orderId',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { orderId } = req.params;

    const order = await Order.findOne({
      orderId: orderId,
      userId: req.user.userId,
    });

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }

    res.json({
      success: true,
      data: order.toSafeObject(),
    });
  })
);

// Cancel order
router.delete(
  '/:orderId',
  authMiddleware,
  validateCancelOrder,
  asyncHandler(async (req, res) => {
    const { orderId } = req.params;
    const { reason = 'USER_CANCELED' } = req.body;

    const order = await Order.findOne({
      orderId: orderId,
      userId: req.user.userId,
    });

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }

    if (!['NEW', 'PARTIALLY_FILLED'].includes(order.status)) {
      return res.status(400).json({
        success: false,
        message: 'Order cannot be canceled',
      });
    }

    // Cancel through trading engine
    const result = await TradingEngine.cancelOrder(orderId, reason);

    if (!result.success) {
      return res.status(400).json({
        success: false,
        message: result.reason || result.error,
      });
    }

    res.json({
      success: true,
      message: 'Order canceled successfully',
      data: {
        orderId: order.orderId,
        status: 'CANCELED',
        cancelTime: new Date(),
      },
    });
  })
);

// Get order history
router.get(
  '/history/all',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const {
      symbol,
      status,
      side,
      startTime,
      endTime,
      limit = 100,
      page = 1,
    } = req.query;

    const filters = {
      symbol: symbol?.toUpperCase(),
      status,
      side: side?.toUpperCase(),
      startTime,
      endTime,
      limit: parseInt(limit),
    };

    const orders = await Order.getOrderHistory(req.user.userId, filters);
    const total = await Order.countDocuments({
      userId: req.user.userId,
      ...(symbol && { symbol: symbol.toUpperCase() }),
      ...(status && { status }),
      ...(side && { side: side.toUpperCase() }),
      ...(startTime &&
        endTime && {
          orderTime: {
            $gte: new Date(startTime),
            $lte: new Date(endTime),
          },
        }),
    });

    res.json({
      success: true,
      data: {
        orders: orders.map((order) => order.toSafeObject()),
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

// Cancel all orders
router.delete(
  '/cancel/all',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { symbol } = req.body;

    const query = {
      userId: req.user.userId,
      status: { $in: ['NEW', 'PARTIALLY_FILLED'] },
      isWorking: true,
    };

    if (symbol) {
      query.symbol = symbol.toUpperCase();
    }

    const activeOrders = await Order.find(query);
    const cancelResults = [];

    for (const order of activeOrders) {
      const result = await TradingEngine.cancelOrder(
        order.orderId,
        'BULK_CANCEL'
      );
      cancelResults.push({
        orderId: order.orderId,
        success: result.success,
        reason: result.reason || result.error,
      });
    }

    const successCount = cancelResults.filter((r) => r.success).length;

    res.json({
      success: true,
      message: `${successCount} orders canceled successfully`,
      data: {
        totalOrders: activeOrders.length,
        successfulCancellations: successCount,
        results: cancelResults,
      },
    });
  })
);

// Get order fills
router.get(
  '/:orderId/fills',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { orderId } = req.params;

    const order = await Order.findOne({
      orderId: orderId,
      userId: req.user.userId,
    });

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }

    res.json({
      success: true,
      data: {
        orderId: order.orderId,
        fills: order.fills,
        executedQuantity: order.executedQuantity.toString(),
        cumulativeQuoteQuantity: order.cumulativeQuoteQuantity.toString(),
        averagePrice: order.averagePrice?.toString() || '0',
      },
    });
  })
);

module.exports = router;
