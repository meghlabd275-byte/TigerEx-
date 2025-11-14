const mongoose = require('mongoose');

const tradeExecutionSchema = new mongoose.Schema({
  requestId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  side: {
    type: String,
    required: true,
    enum: ['buy', 'sell'],
    index: true
  },
  type: {
    type: String,
    required: true,
    enum: ['market', 'limit', 'stop', 'stop_limit'],
    default: 'market'
  },
  quantity: {
    type: Number,
    required: true,
    min: 0
  },
  filledQuantity: {
    type: Number,
    default: 0,
    min: 0
  },
  remainingQuantity: {
    type: Number,
    default: 0,
    min: 0
  },
  price: {
    type: Number,
    min: 0
  },
  averagePrice: {
    type: Number,
    default: 0,
    min: 0
  },
  totalCost: {
    type: Number,
    default: 0,
    min: 0
  },
  status: {
    type: String,
    required: true,
    enum: ['pending', 'processing', 'partially_filled', 'completed', 'failed', 'cancelled'],
    default: 'pending',
    index: true
  },
  filledOrders: [{
    exchangeId: {
      type: String,
      required: true
    },
    exchangeName: {
      type: String,
      required: true
    },
    orderId: {
      type: String,
      required: true
    },
    price: {
      type: Number,
      required: true,
      min: 0
    },
    quantity: {
      type: Number,
      required: true,
      min: 0
    },
    cost: {
      type: Number,
      required: true,
      min: 0
    },
    fee: {
      type: Number,
      default: 0,
      min: 0
    },
    status: {
      type: String,
      enum: ['pending', 'filled', 'failed', 'cancelled'],
      default: 'pending'
    },
    createdAt: {
      type: Date,
      default: Date.now
    },
    filledAt: {
      type: Date
    }
  }],
  executionStrategy: {
    type: String,
    enum: ['best_price', 'fastest_execution', 'distributed'],
    default: 'best_price'
  },
  exchanges: [{
    type: String,
    enum: ['binance', 'kucoin', 'okx', 'bybit', 'kraken']
  }],
  maxSlippage: {
    type: Number,
    default: 0.01, // 1%
    min: 0,
    max: 1
  },
  leverage: {
    type: Number,
    default: 1,
    min: 1,
    max: 100
  },
  marginType: {
    type: String,
    enum: ['isolated', 'cross'],
    default: 'isolated'
  },
  error: {
    type: String
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  completedAt: {
    type: Date,
    index: true
  },
  failedAt: {
    type: Date,
    index: true
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
tradeExecutionSchema.index({ userId: 1, symbol: 1, createdAt: -1 });
tradeExecutionSchema.index({ symbol: 1, status: 1, createdAt: -1 });
tradeExecutionSchema.index({ status: 1, createdAt: -1 });
tradeExecutionSchema.index({ 'filledOrders.exchangeId': 1 });

// Virtuals
tradeExecutionSchema.virtual('isCompleted').get(function() {
  return this.status === 'completed';
});

tradeExecutionSchema.virtual('isFailed').get(function() {
  return this.status === 'failed';
});

tradeExecutionSchema.virtual('isProcessing').get(function() {
  return ['pending', 'processing', 'partially_filled'].includes(this.status);
});

tradeExecutionSchema.virtual('fillPercentage').get(function() {
  if (this.quantity === 0) return 0;
  return (this.filledQuantity / this.quantity) * 100;
});

tradeExecutionSchema.virtual('remaining').get(function() {
  return this.quantity - this.filledQuantity;
});

// Static methods
tradeExecutionSchema.statics.findByUser = function(userId, options = {}) {
  const query = { userId };
  
  if (options.status) {
    query.status = options.status;
  }
  
  if (options.symbol) {
    query.symbol = options.symbol;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0)
    .populate('userId', 'username email');
};

tradeExecutionSchema.statics.findBySymbol = function(symbol, options = {}) {
  const query = { symbol };
  
  if (options.status) {
    query.status = options.status;
  }
  
  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0)
    .populate('userId', 'username email');
};

tradeExecutionSchema.statics.findActiveExecutions = function() {
  return this.find({
    status: { $in: ['pending', 'processing', 'partially_filled'] }
  })
  .sort({ createdAt: -1 })
  .populate('userId', 'username email');
};

tradeExecutionSchema.statics.getExecutionStats = function(userId, timeframe = '24h') {
  const dateLimit = new Date();
  
  switch (timeframe) {
    case '1h':
      dateLimit.setHours(dateLimit.getHours() - 1);
      break;
    case '24h':
      dateLimit.setDate(dateLimit.getDate() - 1);
      break;
    case '7d':
      dateLimit.setDate(dateLimit.getDate() - 7);
      break;
    case '30d':
      dateLimit.setDate(dateLimit.getDate() - 30);
      break;
    default:
      dateLimit.setDate(dateLimit.getDate() - 1);
  }
  
  return this.aggregate([
    {
      $match: {
        userId: new mongoose.Types.ObjectId(userId),
        createdAt: { $gte: dateLimit }
      }
    },
    {
      $group: {
        _id: null,
        totalExecutions: { $sum: 1 },
        completedExecutions: {
          $sum: { $cond: [{ $eq: ['$status', 'completed'] }, 1, 0] }
        },
        failedExecutions: {
          $sum: { $cond: [{ $eq: ['$status', 'failed'] }, 1, 0] }
        },
        totalVolume: { $sum: '$totalCost' },
        averageExecutionSize: { $avg: '$totalCost' },
        successRate: {
          $avg: { $cond: [{ $eq: ['$status', 'completed'] }, 1, 0] }
        }
      }
    }
  ]);
};

// Instance methods
tradeExecutionSchema.methods.addFilledOrder = function(orderData) {
  this.filledOrders.push(orderData);
  
  // Update totals
  this.filledQuantity += orderData.quantity;
  this.totalCost += orderData.cost;
  
  // Calculate average price
  if (this.filledQuantity > 0) {
    this.averagePrice = this.totalCost / this.filledQuantity;
  }
  
  // Update remaining quantity
  this.remainingQuantity = this.quantity - this.filledQuantity;
  
  // Update status
  if (this.remainingQuantity === 0) {
    this.status = 'completed';
    this.completedAt = new Date();
  } else if (this.filledQuantity > 0) {
    this.status = 'partially_filled';
  }
  
  return this.save();
};

tradeExecutionSchema.methods.markAsCompleted = function() {
  this.status = 'completed';
  this.completedAt = new Date();
  this.remainingQuantity = 0;
  
  return this.save();
};

tradeExecutionSchema.methods.markAsFailed = function(error) {
  this.status = 'failed';
  this.error = error;
  this.failedAt = new Date();
  
  return this.save();
};

tradeExecutionSchema.methods.cancel = function(reason) {
  if (['completed', 'failed'].includes(this.status)) {
    throw new Error('Cannot cancel completed or failed execution');
  }
  
  this.status = 'cancelled';
  this.error = reason || 'Cancelled by user';
  
  return this.save();
};

tradeExecutionSchema.methods.getExchangeDistribution = function() {
  const distribution = {};
  
  this.filledOrders.forEach(order => {
    if (!distribution[order.exchangeId]) {
      distribution[order.exchangeId] = {
        exchangeName: order.exchangeName,
        totalCost: 0,
        totalQuantity: 0,
        orderCount: 0,
        fees: 0
      };
    }
    
    distribution[order.exchangeId].totalCost += order.cost;
    distribution[order.exchangeId].totalQuantity += order.quantity;
    distribution[order.exchangeId].orderCount += 1;
    distribution[order.exchangeId].fees += order.fee;
  });
  
  // Calculate percentages
  Object.keys(distribution).forEach(exchangeId => {
    distribution[exchangeId].costPercentage = 
      (distribution[exchangeId].totalCost / this.totalCost) * 100;
    distribution[exchangeId].quantityPercentage = 
      (distribution[exchangeId].totalQuantity / this.filledQuantity) * 100;
  });
  
  return distribution;
};

tradeExecutionSchema.methods.validateExecution = function() {
  const errors = [];
  
  if (!this.symbol) {
    errors.push('Symbol is required');
  }
  
  if (!this.side) {
    errors.push('Side is required');
  }
  
  if (!this.quantity || this.quantity <= 0) {
    errors.push('Quantity must be greater than 0');
  }
  
  if (this.type === 'limit' && (!this.price || this.price <= 0)) {
    errors.push('Price is required for limit orders');
  }
  
  if (this.exchanges.length === 0) {
    errors.push('At least one exchange must be specified');
  }
  
  if (this.leverage && (this.leverage < 1 || this.leverage > 100)) {
    errors.push('Leverage must be between 1 and 100');
  }
  
  return errors;
};

// Pre-save middleware
tradeExecutionSchema.pre('save', function(next) {
  // Update remaining quantity
  this.remainingQuantity = this.quantity - this.filledQuantity;
  
  // Update timestamps
  if (this.isModified('status')) {
    if (this.status === 'completed') {
      this.completedAt = new Date();
    } else if (this.status === 'failed') {
      this.failedAt = new Date();
    }
  }
  
  next();
});

// Pre-remove middleware
tradeExecutionSchema.pre('remove', async function(next) {
  // Log execution removal
  console.log(`Trade execution ${this.requestId} removed`);
  next();
});

module.exports = mongoose.model('TradeExecution', tradeExecutionSchema);