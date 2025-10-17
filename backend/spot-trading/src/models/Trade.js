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

const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const tradeSchema = new mongoose.Schema(
  {
    // Trade Identification
    tradeId: {
      type: String,
      unique: true,
      required: true,
      default: () => `TRADE_${Date.now()}_${uuidv4().substr(0, 8)}`,
    },

    // Order References
    buyOrderId: {
      type: String,
      required: true,
      index: true,
    },
    sellOrderId: {
      type: String,
      required: true,
      index: true,
    },

    // User References
    buyUserId: {
      type: String,
      required: true,
      index: true,
    },
    sellUserId: {
      type: String,
      required: true,
      index: true,
    },

    // Trading Pair
    symbol: {
      type: String,
      required: true,
      uppercase: true,
      index: true,
    },
    baseAsset: {
      type: String,
      required: true,
      uppercase: true,
    },
    quoteAsset: {
      type: String,
      required: true,
      uppercase: true,
    },

    // Trade Details
    price: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },
    quantity: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },
    quoteQuantity: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },

    // Fees
    buyerCommission: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    buyerCommissionAsset: {
      type: String,
      uppercase: true,
    },
    sellerCommission: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    sellerCommissionAsset: {
      type: String,
      uppercase: true,
    },

    // Trade Classification
    isBuyerMaker: {
      type: Boolean,
      required: true,
    },

    // Timestamps
    tradeTime: {
      type: Date,
      default: Date.now,
      index: true,
    },

    // Market Data
    marketPrice: {
      type: mongoose.Schema.Types.Decimal128,
    },
    priceChange: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    priceChangePercent: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },

    // Settlement Status
    settlementStatus: {
      type: String,
      enum: ['PENDING', 'SETTLED', 'FAILED'],
      default: 'PENDING',
    },
    settlementTime: Date,

    // Metadata
    matchingEngine: {
      type: String,
      default: 'SPOT_ENGINE_V1',
    },

    // Risk and Compliance
    riskScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100,
    },
    flagged: {
      type: Boolean,
      default: false,
    },
    flagReason: String,
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Indexes
tradeSchema.index({ symbol: 1, tradeTime: -1 });
tradeSchema.index({ buyUserId: 1, tradeTime: -1 });
tradeSchema.index({ sellUserId: 1, tradeTime: -1 });
tradeSchema.index({ tradeTime: -1 });
tradeSchema.index({ symbol: 1, price: 1 });

// Virtual fields
tradeSchema.virtual('totalValue').get(function () {
  return parseFloat(this.price) * parseFloat(this.quantity);
});

tradeSchema.virtual('buyerTotal').get(function () {
  return parseFloat(this.quoteQuantity) + parseFloat(this.buyerCommission || 0);
});

tradeSchema.virtual('sellerTotal').get(function () {
  return (
    parseFloat(this.quoteQuantity) - parseFloat(this.sellerCommission || 0)
  );
});

// Pre-save middleware
tradeSchema.pre('save', function (next) {
  // Calculate quote quantity if not set
  if (!this.quoteQuantity) {
    this.quoteQuantity = parseFloat(this.price) * parseFloat(this.quantity);
  }

  next();
});

// Methods
tradeSchema.methods.settle = function () {
  this.settlementStatus = 'SETTLED';
  this.settlementTime = new Date();
};

tradeSchema.methods.flag = function (reason) {
  this.flagged = true;
  this.flagReason = reason;
};

tradeSchema.methods.toSafeObject = function () {
  const obj = this.toObject();
  delete obj._id;
  delete obj.__v;
  return obj;
};

// Static methods
tradeSchema.statics.getTradeHistory = function (userId, filters = {}) {
  const query = {
    $or: [{ buyUserId: userId }, { sellUserId: userId }],
  };

  if (filters.symbol) {
    query.symbol = filters.symbol;
  }

  if (filters.startTime && filters.endTime) {
    query.tradeTime = {
      $gte: new Date(filters.startTime),
      $lte: new Date(filters.endTime),
    };
  }

  return this.find(query)
    .sort({ tradeTime: -1 })
    .limit(filters.limit || 100);
};

tradeSchema.statics.getMarketTrades = function (symbol, limit = 50) {
  return this.find({ symbol: symbol })
    .sort({ tradeTime: -1 })
    .limit(limit)
    .select('tradeId price quantity quoteQuantity tradeTime isBuyerMaker');
};

tradeSchema.statics.get24hrStats = function (symbol) {
  const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);

  return this.aggregate([
    {
      $match: {
        symbol: symbol,
        tradeTime: { $gte: twentyFourHoursAgo },
      },
    },
    {
      $group: {
        _id: null,
        count: { $sum: 1 },
        volume: { $sum: { $toDouble: '$quantity' } },
        quoteVolume: { $sum: { $toDouble: '$quoteQuantity' } },
        high: { $max: { $toDouble: '$price' } },
        low: { $min: { $toDouble: '$price' } },
        open: { $first: { $toDouble: '$price' } },
        close: { $last: { $toDouble: '$price' } },
        weightedAvgPrice: {
          $divide: [
            {
              $sum: {
                $multiply: [
                  { $toDouble: '$price' },
                  { $toDouble: '$quantity' },
                ],
              },
            },
            { $sum: { $toDouble: '$quantity' } },
          ],
        },
      },
    },
  ]);
};

tradeSchema.statics.getVolumeStats = function (symbol, timeframe = '1h') {
  const timeframes = {
    '1m': 1 * 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
  };

  const interval = timeframes[timeframe] || timeframes['1h'];
  const startTime = new Date(Date.now() - interval);

  return this.aggregate([
    {
      $match: {
        symbol: symbol,
        tradeTime: { $gte: startTime },
      },
    },
    {
      $group: {
        _id: {
          $dateToString: {
            format: '%Y-%m-%d %H:%M',
            date: {
              $dateTrunc: {
                date: '$tradeTime',
                unit: 'minute',
                binSize: interval / (60 * 1000),
              },
            },
          },
        },
        volume: { $sum: { $toDouble: '$quantity' } },
        quoteVolume: { $sum: { $toDouble: '$quoteQuantity' } },
        trades: { $sum: 1 },
        avgPrice: { $avg: { $toDouble: '$price' } },
      },
    },
    {
      $sort: { _id: 1 },
    },
  ]);
};

module.exports = mongoose.model('Trade', tradeSchema);
