const mongoose = require('mongoose');

const tradingContractSchema = new mongoose.Schema({
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    unique: true,
    index: true
  },
  type: {
    type: String,
    required: true,
    enum: ['spot', 'futures', 'margin', 'options', 'trading_pair', 'copy_trading'],
    index: true
  },
  // For futures contracts
  contractType: {
    type: String,
    enum: ['perpetual', 'cross', 'delivery']
  },
  // For margin contracts
  marginType: {
    type: String,
    enum: ['isolated', 'cross']
  },
  // For options contracts
  optionType: {
    type: String,
    enum: ['call', 'put']
  },
  // Basic contract info
  name: {
    type: String,
    required: true
  },
  description: {
    type: String
  },
  baseAsset: {
    type: String,
    required: true,
    uppercase: true
  },
  quoteAsset: {
    type: String,
    required: true,
    uppercase: true
  },
  // Token references for trading pairs
  baseTokenId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'CustomToken'
  },
  quoteTokenId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'CustomToken'
  },
  // Precision and limits
  baseAssetPrecision: {
    type: Number,
    default: 8,
    min: 0,
    max: 18
  },
  quoteAssetPrecision: {
    type: Number,
    default: 8,
    min: 0,
    max: 18
  },
  minNotional: {
    type: Number,
    required: true,
    min: 0
  },
  minQty: {
    type: Number,
    required: true,
    min: 0
  },
  maxQty: {
    type: Number,
    required: true,
    min: 0
  },
  tickSize: {
    type: Number,
    required: true,
    min: 0
  },
  stepSize: {
    type: Number,
    required: true,
    min: 0
  },
  // Price limits
  minPrice: {
    type: Number,
    min: 0
  },
  maxPrice: {
    type: Number,
    min: 0
  },
  // Futures specific
  contractSize: {
    type: Number,
    min: 0
  },
  settlementType: {
    type: String,
    enum: ['linear', 'inverse', 'quanto']
  },
  maxLeverage: {
    type: Number,
    default: 1,
    min: 1,
    max: 100
  },
  minLeverage: {
    type: Number,
    default: 1,
    min: 1,
    max: 100
  },
  maintenanceMarginRatio: {
    type: Number,
    default: 0.005,
    min: 0,
    max: 1
  },
  initialMarginRatio: {
    type: Number,
    default: 0.01,
    min: 0,
    max: 1
  },
  fundingRateInterval: {
    type: Number,
    default: 8 * 60 * 60 * 1000, // 8 hours in milliseconds
    min: 0
  },
  // Options specific
  underlyingAsset: {
    type: String,
    uppercase: true
  },
  strikePrice: {
    type: Number,
    min: 0
  },
  expirationDate: {
    type: Date
  },
  exerciseType: {
    type: String,
    enum: ['european', 'american']
  },
  // Margin specific
  interestRate: {
    type: Number,
    default: 0
  },
  marginRatio: {
    type: Number,
    default: 0.1,
    min: 0,
    max: 1
  },
  liquidationThreshold: {
    type: Number,
    default: 0.8,
    min: 0,
    max: 1
  },
  // Status and control
  status: {
    type: String,
    enum: ['active', 'paused', 'suspended', 'maintenance', 'delisted'],
    default: 'active'
  },
  isActive: {
    type: Boolean,
    default: true,
    index: true
  },
  isDeleted: {
    type: Boolean,
    default: false,
    index: true
  },
  // Trading rules and restrictions
  tradingRules: {
    maxOrdersPerSecond: {
      type: Number,
      default: 10
    },
    maxOrdersPerMinute: {
      type: Number,
      default: 100
    },
    maxOrderSize: {
      type: Number
    },
    circuitBreakerThreshold: {
      type: Number,
      default: 0.1 // 10%
    },
    coolingOffPeriod: {
      type: Number,
      default: 60 * 1000 // 1 minute
    }
  },
  // Audit fields
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  deletedAt: {
    type: Date
  },
  // Market data
  lastPrice: {
    type: Number,
    default: 0,
    min: 0
  },
  change24h: {
    type: Number,
    default: 0
  },
  volume24h: {
    type: Number,
    default: 0,
    min: 0
  },
  high24h: {
    type: Number,
    default: 0,
    min: 0
  },
  low24h: {
    type: Number,
    default: 0,
    min: 0
  },
  // Metadata
  metadata: {
    type: mongoose.Schema.Types.Mixed
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
tradingContractSchema.index({ type: 1, status: 1, isActive: 1 });
tradingContractSchema.index({ baseAsset: 1, quoteAsset: 1 });
tradingContractSchema.index({ createdBy: 1, createdAt: -1 });
tradingContractSchema.index({ symbol: 'text', name: 'text', description: 'text' });

// Virtuals
tradingContractSchema.virtual('isPerpetual').get(function() {
  return this.type === 'futures' && this.contractType === 'perpetual';
});

tradingContractSchema.virtual('isCrossMargin').get(function() {
  return this.type === 'futures' && this.contractType === 'cross';
});

tradingContractSchema.virtual('isExpiringSoon').get(function() {
  if (!this.expirationDate) return false;
  const daysUntilExpiry = (this.expirationDate - new Date()) / (1000 * 60 * 60 * 24);
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
});

// Static methods
tradingContractSchema.statics.findBySymbol = function(symbol) {
  return this.findOne({ symbol, isDeleted: false })
    .populate('createdBy', 'username email')
    .populate('updatedBy', 'username email')
    .populate('baseTokenId', 'symbol name logoUrl')
    .populate('quoteTokenId', 'symbol name logoUrl');
};

tradingContractSchema.statics.findByType = function(type, options = {}) {
  const query = { type, isDeleted: false };
  
  if (options.contractType) {
    query.contractType = options.contractType;
  }
  
  if (options.status) {
    query.status = options.status;
  }
  
  if (options.isActive !== undefined) {
    query.isActive = options.isActive;
  }

  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0)
    .populate('createdBy', 'username email')
    .populate('baseTokenId', 'symbol name')
    .populate('quoteTokenId', 'symbol name');
};

tradingContractSchema.statics.findActiveContracts = function() {
  return this.find({ isActive: true, isDeleted: false })
    .sort({ createdAt: -1 })
    .populate('createdBy', 'username email');
};

tradingContractSchema.statics.findByAssets = function(baseAsset, quoteAsset) {
  return this.find({ 
    baseAsset: baseAsset.toUpperCase(), 
    quoteAsset: quoteAsset.toUpperCase(),
    isDeleted: false 
  })
  .sort({ createdAt: -1 });
};

tradingContractSchema.statics.getContractStats = function() {
  return this.aggregate([
    {
      $match: { isDeleted: false }
    },
    {
      $group: {
        _id: null,
        total: { $sum: 1 },
        active: { $sum: { $cond: ['$isActive', 1, 0] } },
        spot: { $sum: { $cond: [{ $eq: ['$type', 'spot'] }, 1, 0] } },
        futures: { $sum: { $cond: [{ $eq: ['$type', 'futures'] }, 1, 0] } },
        margin: { $sum: { $cond: [{ $eq: ['$type', 'margin'] }, 1, 0] } },
        options: { $sum: { $cond: [{ $eq: ['$type', 'options'] }, 1, 0] } },
        tradingPairs: { $sum: { $cond: [{ $eq: ['$type', 'trading_pair'] }, 1, 0] } },
        totalVolume24h: { $sum: '$volume24h' }
      }
    }
  ]);
};

// Instance methods
tradingContractSchema.methods.activate = function() {
  this.isActive = true;
  this.status = 'active';
  return this.save();
};

tradingContractSchema.methods.pause = function() {
  this.isActive = false;
  this.status = 'paused';
  return this.save();
};

tradingContractSchema.methods.suspend = function() {
  this.isActive = false;
  this.status = 'suspended';
  return this.save();
};

tradingContractSchema.methods.delist = function() {
  this.isActive = false;
  this.status = 'delisted';
  return this.save();
};

tradingContractSchema.methods.softDelete = function() {
  this.isDeleted = true;
  this.isActive = false;
  this.status = 'delisted';
  this.deletedAt = new Date();
  return this.save();
};

tradingContractSchema.methods.updateMarketData = function(marketData) {
  if (marketData.lastPrice !== undefined) this.lastPrice = marketData.lastPrice;
  if (marketData.change24h !== undefined) this.change24h = marketData.change24h;
  if (marketData.volume24h !== undefined) this.volume24h = marketData.volume24h;
  if (marketData.high24h !== undefined) this.high24h = marketData.high24h;
  if (marketData.low24h !== undefined) this.low24h = marketData.low24h;
  
  return this.save();
};

tradingContractSchema.methods.validateOrder = function(order) {
  const errors = [];
  
  if (order.quantity < this.minQty) {
    errors.push(`Quantity must be at least ${this.minQty}`);
  }
  
  if (order.quantity > this.maxQty) {
    errors.push(`Quantity cannot exceed ${this.maxQty}`);
  }
  
  if (order.price) {
    if (this.minPrice && order.price < this.minPrice) {
      errors.push(`Price must be at least ${this.minPrice}`);
    }
    
    if (this.maxPrice && order.price > this.maxPrice) {
      errors.push(`Price cannot exceed ${this.maxPrice}`);
    }
  }
  
  const notional = order.quantity * (order.price || this.lastPrice || 0);
  if (notional < this.minNotional) {
    errors.push(`Notional value must be at least ${this.minNotional}`);
  }
  
  return errors;
};

tradingContractSchema.methods.calculateFee = function(order, feeRate = 0.001) {
  const notional = order.quantity * (order.price || this.lastPrice || 0);
  return notional * feeRate;
};

// Pre-save middleware
tradingContractSchema.pre('save', function(next) {
  // Ensure symbol is uppercase
  if (this.symbol) {
    this.symbol = this.symbol.toUpperCase();
  }
  
  // Ensure assets are uppercase
  if (this.baseAsset) {
    this.baseAsset = this.baseAsset.toUpperCase();
  }
  
  if (this.quoteAsset) {
    this.quoteAsset = this.quoteAsset.toUpperCase();
  }
  
  // Update status based on isActive flag
  if (this.isActive && this.status === 'paused') {
    this.status = 'active';
  } else if (!this.isActive && this.status === 'active') {
    this.status = 'paused';
  }
  
  next();
});

// Pre-remove middleware
tradingContractSchema.pre('remove', async function(next) {
  // Log contract removal
  console.log(`Trading contract ${this.symbol} removed`);
  next();
});

module.exports = mongoose.model('TradingContract', tradingContractSchema);