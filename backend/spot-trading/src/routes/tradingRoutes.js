const express = require('express');
const router = express.Router();
const TradingEngine = require('../services/TradingEngine');
const OrderBookService = require('../services/OrderBookService');
const authMiddleware = require('../middleware/auth');
const { optionalAuth } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');

// Get order book for a symbol
router.get(
  '/orderbook/:symbol',
  optionalAuth,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;
    const { depth = 20 } = req.query;

    const orderBook = OrderBookService.getOrderBook(
      symbol.toUpperCase(),
      parseInt(depth)
    );

    res.json({
      success: true,
      data: orderBook,
    });
  })
);

// Get order book statistics
router.get(
  '/orderbook/:symbol/stats',
  optionalAuth,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    const stats = OrderBookService.getOrderBookStats(symbol.toUpperCase());

    if (!stats) {
      return res.status(404).json({
        success: false,
        message: 'Order book not found for symbol',
      });
    }

    res.json({
      success: true,
      data: stats,
    });
  })
);

// Get all order book statistics
router.get(
  '/orderbook/stats/all',
  optionalAuth,
  asyncHandler(async (req, res) => {
    const allStats = OrderBookService.getAllOrderBookStats();

    res.json({
      success: true,
      data: allStats,
    });
  })
);

// Get trading pairs
router.get(
  '/pairs',
  optionalAuth,
  asyncHandler(async (req, res) => {
    // This would typically come from a trading pairs configuration
    const tradingPairs = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        status: 'TRADING',
        minQuantity: '0.00001',
        maxQuantity: '1000',
        stepSize: '0.00001',
        minPrice: '0.01',
        maxPrice: '1000000',
        tickSize: '0.01',
        minNotional: '10',
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        status: 'TRADING',
        minQuantity: '0.0001',
        maxQuantity: '10000',
        stepSize: '0.0001',
        minPrice: '0.01',
        maxPrice: '100000',
        tickSize: '0.01',
        minNotional: '10',
      },
      {
        symbol: 'BNBUSDT',
        baseAsset: 'BNB',
        quoteAsset: 'USDT',
        status: 'TRADING',
        minQuantity: '0.001',
        maxQuantity: '100000',
        stepSize: '0.001',
        minPrice: '0.01',
        maxPrice: '10000',
        tickSize: '0.01',
        minNotional: '10',
      },
    ];

    res.json({
      success: true,
      data: tradingPairs,
    });
  })
);

// Get trading pair info
router.get(
  '/pairs/:symbol',
  optionalAuth,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    // This would typically query a trading pairs database
    const mockPairInfo = {
      symbol: symbol.toUpperCase(),
      baseAsset: symbol.substring(0, symbol.length - 4),
      quoteAsset: 'USDT',
      status: 'TRADING',
      minQuantity: '0.00001',
      maxQuantity: '1000',
      stepSize: '0.00001',
      minPrice: '0.01',
      maxPrice: '1000000',
      tickSize: '0.01',
      minNotional: '10',
      fees: {
        maker: '0.001',
        taker: '0.001',
      },
    };

    res.json({
      success: true,
      data: mockPairInfo,
    });
  })
);

// Get trading engine status
router.get(
  '/engine/status',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const engineStatus = TradingEngine.getHealthStatus();
    const orderBookStatus = OrderBookService.getHealthStatus();

    res.json({
      success: true,
      data: {
        tradingEngine: engineStatus,
        orderBookService: orderBookStatus,
        timestamp: new Date(),
      },
    });
  })
);

// Test order (paper trading)
router.post(
  '/test-order',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { symbol, side, type, quantity, price, timeInForce } = req.body;

    // Validate order parameters without actually placing it
    const mockOrder = {
      symbol: symbol.toUpperCase(),
      side: side.toUpperCase(),
      type: type.toUpperCase(),
      quantity: parseFloat(quantity),
      price: price ? parseFloat(price) : null,
      timeInForce: timeInForce || 'GTC',
    };

    // Basic validation
    if (
      !mockOrder.symbol ||
      !mockOrder.side ||
      !mockOrder.type ||
      !mockOrder.quantity
    ) {
      return res.status(400).json({
        success: false,
        message: 'Missing required order parameters',
      });
    }

    if (mockOrder.quantity <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid quantity',
      });
    }

    if (
      ['LIMIT'].includes(mockOrder.type) &&
      (!mockOrder.price || mockOrder.price <= 0)
    ) {
      return res.status(400).json({
        success: false,
        message: 'Invalid price for limit order',
      });
    }

    // Get current order book to estimate execution
    const orderBook = OrderBookService.getOrderBook(mockOrder.symbol, 10);
    let estimatedPrice = mockOrder.price;
    let estimatedFills = [];

    if (mockOrder.type === 'MARKET') {
      const oppositeOrders =
        mockOrder.side === 'BUY' ? orderBook.asks : orderBook.bids;
      if (oppositeOrders.length > 0) {
        estimatedPrice = parseFloat(oppositeOrders[0].price);

        let remainingQuantity = mockOrder.quantity;
        for (const level of oppositeOrders) {
          if (remainingQuantity <= 0) break;

          const fillQuantity = Math.min(
            remainingQuantity,
            parseFloat(level.quantity)
          );
          estimatedFills.push({
            price: parseFloat(level.price),
            quantity: fillQuantity,
          });
          remainingQuantity -= fillQuantity;
        }
      }
    }

    res.json({
      success: true,
      message: 'Test order validated successfully',
      data: {
        order: mockOrder,
        estimatedPrice,
        estimatedFills,
        commission: (
          mockOrder.quantity *
          (estimatedPrice || 0) *
          0.001
        ).toFixed(8),
        wouldExecute:
          mockOrder.type === 'MARKET' ||
          (mockOrder.type === 'LIMIT' && estimatedFills.length > 0),
      },
    });
  })
);

module.exports = router;
