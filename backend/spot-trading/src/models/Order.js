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

const orderSchema = new mongoose.Schema(
  {
    // Order Identification
    orderId: {
      type: String,
      unique: true,
      required: true,
      default: () => `ORDER_${Date.now()}_${uuidv4().substr(0, 8)}`,
    },
    userId: {
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

    // Order Details
    side: {
      type: String,
      enum: ['BUY', 'SELL'],
      required: true,
    },
    type: {
      type: String,
      enum: ['MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LIMIT', 'TAKE_PROFIT'],
      required: true,
    },
    timeInForce: {
      type: String,
      enum: ['GTC', 'IOC', 'FOK'], // Good Till Cancel, Immediate or Cancel, Fill or Kill
      default: 'GTC',
    },

    // Quantities and Prices
    quantity: {
      type: mongoose.Schema.Types.Decimal128,
      required: true,
      min: 0,
    },
    price: {
      type: mongoose.Schema.Types.Decimal128,
      required: function () {
        return ['LIMIT', 'STOP_LIMIT'].includes(this.type);
      },
    },
    stopPrice: {
      type: mongoose.Schema.Types.Decimal128,
      required: function () {
        return ['STOP_LOSS', 'STOP_LIMIT', 'TAKE_PROFIT'].includes(this.type);
      },
    },

    // Execution Details
    executedQuantity: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
      min: 0,
    },
    cumulativeQuoteQuantity: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
      min: 0,
    },
    averagePrice: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },

    // Order Status
    status: {
      type: String,
      enum: [
        'NEW',
        'PARTIALLY_FILLED',
        'FILLED',
        'CANCELED',
        'PENDING_CANCEL',
        'REJECTED',
        'EXPIRED',
      ],
      default: 'NEW',
    },

    // Fees
    commission: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    commissionAsset: {
      type: String,
      uppercase: true,
    },

    // Timestamps
    orderTime: {
      type: Date,
      default: Date.now,
    },
    updateTime: {
      type: Date,
      default: Date.now,
    },

    // Additional Fields
    clientOrderId: {
      type: String,
      sparse: true,
    },
    icebergQuantity: {
      type: mongoose.Schema.Types.Decimal128,
      default: 0,
    },
    isWorking: {
      type: Boolean,
      default: true,
    },

    // Risk Management
    riskScore: {
      type: Number,
      default: 0,
      min: 0,
      max: 100,
    },

    // Metadata
    source: {
      type: String,
      enum: ['WEB', 'API', 'MOBILE', 'ALGORITHM'],
      default: 'WEB',
    },
    ipAddress: String,
    userAgent: String,

    // Fills (sub-documents for partial fills)
    fills: [
      {
        tradeId: {
          type: String,
          required: true,
        },
        price: {
          type: mongoose.Schema.Types.Decimal128,
          required: true,
        },
        quantity: {
          type: mongoose.Schema.Types.Decimal128,
          required: true,
        },
        commission: {
          type: mongoose.Schema.Types.Decimal128,
          default: 0,
        },
        commissionAsset: {
          type: String,
          uppercase: true,
        },
        timestamp: {
          type: Date,
          default: Date.now,
        },
      },
    ],
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// Indexes
orderSchema.index({ userId: 1, symbol: 1 });
orderSchema.index({ symbol: 1, status: 1 });
orderSchema.index({ userId: 1, status: 1 });
orderSchema.index({ orderTime: -1 });
orderSchema.index({ status: 1, type: 1 });
orderSchema.index({ symbol: 1, side: 1, price: 1 }); // For order book queries

// Virtual fields
orderSchema.virtual('remainingQuantity').get(function () {
  return parseFloat(this.quantity) - parseFloat(this.executedQuantity || 0);
});

orderSchema.virtual('fillPercentage').get(function () {
  const quantity = parseFloat(this.quantity);
  const executed = parseFloat(this.executedQuantity || 0);
  return quantity > 0 ? (executed / quantity) * 100 : 0;
});

orderSchema.virtual('totalValue').get(function () {
  if (this.type === 'MARKET') {
    return parseFloat(this.cumulativeQuoteQuantity || 0);
  }
  return parseFloat(this.quantity) * parseFloat(this.price || 0);
});

// Pre-save middleware
orderSchema.pre('save', function (next) {
  this.updateTime = new Date();

  // Calculate average price if there are fills
  if (this.fills && this.fills.length > 0) {
    let totalQuantity = 0;
    let totalValue = 0;

    this.fills.forEach((fill) => {
      const qty = parseFloat(fill.quantity);
      const price = parseFloat(fill.price);
      totalQuantity += qty;
      totalValue += qty * price;
    });

    if (totalQuantity > 0) {
      this.averagePrice = totalValue / totalQuantity;
      this.executedQuantity = totalQuantity;
    }
  }

  next();
});

// Methods
orderSchema.methods.addFill = function (fill) {
  this.fills.push(fill);

  // Update executed quantity and cumulative quote quantity
  const fillQty = parseFloat(fill.quantity);
  const fillPrice = parseFloat(fill.price);

  this.executedQuantity = parseFloat(this.executedQuantity || 0) + fillQty;
  this.cumulativeQuoteQuantity =
    parseFloat(this.cumulativeQuoteQuantity || 0) + fillQty * fillPrice;

  // Update status based on execution
  const totalQty = parseFloat(this.quantity);
  const executedQty = parseFloat(this.executedQuantity);

  if (executedQty >= totalQty) {
    this.status = 'FILLED';
    this.isWorking = false;
  } else if (executedQty > 0) {
    this.status = 'PARTIALLY_FILLED';
  }

  this.updateTime = new Date();
};

orderSchema.methods.cancel = function (reason = 'USER_CANCELED') {
  if (['NEW', 'PARTIALLY_FILLED'].includes(this.status)) {
    this.status = 'CANCELED';
    this.isWorking = false;
    this.updateTime = new Date();
    this.cancelReason = reason;
    return true;
  }
  return false;
};

orderSchema.methods.reject = function (reason) {
  this.status = 'REJECTED';
  this.isWorking = false;
  this.rejectionReason = reason;
  this.updateTime = new Date();
};

orderSchema.methods.toSafeObject = function () {
  const obj = this.toObject();
  delete obj._id;
  delete obj.__v;
  return obj;
};

// Static methods
orderSchema.statics.getActiveOrders = function (userId, symbol = null) {
  const query = {
    userId: userId,
    status: { $in: ['NEW', 'PARTIALLY_FILLED'] },
    isWorking: true,
  };

  if (symbol) {
    query.symbol = symbol;
  }

  return this.find(query).sort({ orderTime: -1 });
};

orderSchema.statics.getOrderHistory = function (userId, filters = {}) {
  const query = { userId: userId };

  if (filters.symbol) {
    query.symbol = filters.symbol;
  }

  if (filters.status) {
    query.status = filters.status;
  }

  if (filters.side) {
    query.side = filters.side;
  }

  if (filters.startTime && filters.endTime) {
    query.orderTime = {
      $gte: new Date(filters.startTime),
      $lte: new Date(filters.endTime),
    };
  }

  return this.find(query)
    .sort({ orderTime: -1 })
    .limit(filters.limit || 100);
};

orderSchema.statics.getOrderBookData = function (symbol, depth = 20) {
  return Promise.all([
    // Get buy orders (bids) - highest price first
    this.find({
      symbol: symbol,
      side: 'BUY',
      status: { $in: ['NEW', 'PARTIALLY_FILLED'] },
      isWorking: true,
    })
      .sort({ price: -1 })
      .limit(depth),

    // Get sell orders (asks) - lowest price first
    this.find({
      symbol: symbol,
      side: 'SELL',
      status: { $in: ['NEW', 'PARTIALLY_FILLED'] },
      isWorking: true,
    })
      .sort({ price: 1 })
      .limit(depth),
  ]);
};

module.exports = mongoose.model('Order', orderSchema);
