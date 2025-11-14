const mongoose = require('mongoose');

const marketMakerBotSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    index: true
  },
  type: {
    type: String,
    required: true,
    enum: ['market_maker', 'grid', 'arbitrage', 'twap', 'vwap'],
    default: 'market_maker'
  },
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  strategy: {
    type: String,
    required: true,
    enum: ['static_spread', 'dynamic_spread', 'inventory_balanced', 'aggressive', 'conservative']
  },
  configuration: {
    orderBookDepth: {
      type: Number,
      default: 10,
      min: 1,
      max: 100
    },
    spreadPercentage: {
      type: Number,
      default: 0.001,
      min: 0,
      max: 1
    },
    minSpread: {
      type: Number,
      default: 0.0001,
      min: 0
    },
    maxSpread: {
      type: Number,
      default: 0.01,
      min: 0
    },
    inventoryTarget: {
      type: Number,
      default: 0,
      min: -1,
      max: 1
    },
    maxOrderSize: {
      type: Number,
      required: true,
      min: 0
    },
    minOrderSize: {
      type: Number,
      required: true,
      min: 0
    },
    rebalanceThreshold: {
      type: Number,
      default: 0.1,
      min: 0,
      max: 1
    },
    maxInventory: {
      type: Number,
      min: 0
    },
    minInventory: {
      type: Number,
      max: 0
    }
  },
  // Grid trading specific
  gridCount: {
    type: Number,
    default: 20,
    min: 2,
    max: 100
  },
  upperPrice: {
    type: Number,
    required: function() { return this.type === 'grid'; }
  },
  lowerPrice: {
    type: Number,
    required: function() { return this.type === 'grid'; }
  },
  gridMode: {
    type: String,
    enum: ['arithmetic', 'geometric'],
    default: 'geometric'
  },
  investmentAmount: {
    type: Number,
    required: function() { return this.type === 'grid'; },
    min: 0
  },
  orderType: {
    type: String,
    enum: ['limit', 'post_only'],
    default: 'limit'
  },
  // Status and control
  status: {
    type: String,
    enum: ['active', 'paused', 'stopped', 'error'],
    default: 'stopped'
  },
  isActive: {
    type: Boolean,
    default: false,
    index: true
  },
  isDeleted: {
    type: Boolean,
    default: false,
    index: true
  },
  // Performance metrics
  totalTrades: {
    type: Number,
    default: 0,
    min: 0
  },
  totalVolume: {
    type: Number,
    default: 0,
    min: 0
  },
  totalProfit: {
    type: Number,
    default: 0
  },
  totalLoss: {
    type: Number,
    default: 0
  },
  netPnL: {
    type: Number,
    default: 0
  },
  winRate: {
    type: Number,
    default: 0,
    min: 0,
    max: 1
  },
  // Current state
  currentInventory: {
    type: Number,
    default: 0
  },
  currentBid: {
    type: Number,
    default: 0
  },
  currentAsk: {
    type: Number,
    default: 0
  },
  lastTradeAt: {
    type: Date
  },
  lastUpdateAt: {
    type: Date,
    default: Date.now
  },
  startedAt: {
    type: Date
  },
  stoppedAt: {
    type: Date
  },
  error: {
    type: String
  },
  // Settings and metadata
  settings: {
    autoRestart: {
      type: Boolean,
      default: true
    },
    maxErrors: {
      type: Number,
      default: 5
    },
    errorCountdown: {
      type: Number,
      default: 60 * 1000 // 1 minute
    },
    updateInterval: {
      type: Number,
      default: 1000 // 1 second
    },
    dryRun: {
      type: Boolean,
      default: false
    }
  },
  description: {
    type: String
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed
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
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
marketMakerBotSchema.index({ type: 1, status: 1, isActive: 1 });
marketMakerBotSchema.index({ symbol: 1, status: 1 });
marketMakerBotSchema.index({ createdBy: 1, createdAt: -1 });
marketMakerBotSchema.index({ isActive: 1, lastUpdateAt: -1 });

// Virtuals
marketMakerBotSchema.virtual('isRunning').get(function() {
  return this.isActive && this.status === 'active';
});

marketMakerBotSchema.virtual('uptime').get(function() {
  if (!this.startedAt) return 0;
  const end = this.stoppedAt || new Date();
  return end - this.startedAt;
});

marketMakerBotSchema.virtual('profitability').get(function() {
  if (this.totalVolume === 0) return 0;
  return (this.netPnL / this.totalVolume) * 100;
});

marketMakerBotSchema.virtual('inventoryUtilization').get(function() {
  if (!this.configuration.maxInventory) return 0;
  return Math.abs(this.currentInventory) / this.configuration.maxInventory;
});

// Static methods
marketMakerBotSchema.statics.findBySymbol = function(symbol) {
  return this.find({ symbol: symbol.toUpperCase(), isDeleted: false })
    .sort({ createdAt: -1 })
    .populate('createdBy', 'username email')
    .populate('updatedBy', 'username email');
};

marketMakerBotSchema.statics.findByType = function(type, options = {}) {
  const query = { type, isDeleted: false };
  
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
    .populate('createdBy', 'username email');
};

marketMakerBotSchema.statics.findActiveBots = function() {
  return this.find({ isActive: true, status: 'active', isDeleted: false })
    .sort({ lastUpdateAt: -1 })
    .populate('createdBy', 'username email');
};

marketMakerBotSchema.statics.getBotsByUser = function(userId, options = {}) {
  const query = { createdBy: userId, isDeleted: false };
  
  if (options.type) {
    query.type = options.type;
  }
  
  if (options.status) {
    query.status = options.status;
  }

  return this.find(query)
    .sort({ createdAt: -1 })
    .limit(options.limit || 50)
    .skip(options.offset || 0);
};

marketMakerBotSchema.statics.getBotStats = function() {
  return this.aggregate([
    {
      $match: { isDeleted: false }
    },
    {
      $group: {
        _id: null,
        total: { $sum: 1 },
        active: { $sum: { $cond: ['$isActive', 1, 0] } },
        running: { $sum: { $cond: [{ $and: ['$isActive', { $eq: ['$status', 'active'] }] }, 1, 0] } },
        stopped: { $sum: { $cond: [{ $eq: ['$status', 'stopped'] }, 1, 0] } },
        marketMaker: { $sum: { $cond: [{ $eq: ['$type', 'market_maker'] }, 1, 0] } },
        grid: { $sum: { $cond: [{ $eq: ['$type', 'grid'] }, 1, 0] } },
        totalTrades: { $sum: '$totalTrades' },
        totalVolume: { $sum: '$totalVolume' },
        totalProfit: { $sum: '$totalProfit' },
        avgWinRate: { $avg: '$winRate' },
        avgNetPnL: { $avg: '$netPnL' }
      }
    }
  ]);
};

// Instance methods
marketMakerBotSchema.methods.start = function() {
  this.isActive = true;
  this.status = 'active';
  this.startedAt = new Date();
  this.stoppedAt = undefined;
  this.error = undefined;
  
  return this.save();
};

marketMakerBotSchema.methods.stop = function(reason) {
  this.isActive = false;
  this.status = 'stopped';
  this.stoppedAt = new Date();
  
  if (reason) {
    this.error = reason;
  }
  
  return this.save();
};

marketMakerBotSchema.methods.pause = function() {
  this.isActive = false;
  this.status = 'paused';
  
  return this.save();
};

marketMakerBotSchema.methods.resume = function() {
  this.isActive = true;
  this.status = 'active';
  
  return this.save();
};

marketMakerBotSchema.methods.softDelete = function() {
  this.isDeleted = true;
  this.isActive = false;
  this.status = 'stopped';
  this.deletedAt = new Date();
  
  return this.save();
};

marketMakerBotSchema.methods.updatePerformance = function(trade) {
  this.totalTrades += 1;
  this.totalVolume += trade.volume || 0;
  
  if (trade.profit) {
    this.totalProfit += trade.profit;
    this.netPnL += trade.profit;
  } else if (trade.loss) {
    this.totalLoss += trade.loss;
    this.netPnL -= trade.loss;
  }
  
  this.winRate = this.calculateWinRate();
  this.lastTradeAt = new Date();
  this.lastUpdateAt = new Date();
  
  return this.save();
};

marketMakerBotSchema.methods.updateInventory = function(inventoryChange) {
  this.currentInventory += inventoryChange;
  this.lastUpdateAt = new Date();
  
  return this.save();
};

marketMakerBotSchema.methods.updatePrices = function(bid, ask) {
  this.currentBid = bid;
  this.currentAsk = ask;
  this.lastUpdateAt = new Date();
  
  return this.save();
};

marketMakerBotSchema.methods.calculateWinRate = function() {
  const totalOutcome = this.totalProfit + this.totalLoss;
  if (totalOutcome === 0) return 0;
  
  return this.totalProfit / totalOutcome;
};

marketMakerBotSchema.methods.setError = function(error) {
  this.error = error;
  this.status = 'error';
  this.isActive = false;
  
  return this.save();
};

marketMakerBotSchema.methods.clearError = function() {
  this.error = undefined;
  this.status = 'stopped';
  
  return this.save();
};

marketMakerBotSchema.methods.getGridLevels = function() {
  if (this.type !== 'grid') {
    return [];
  }
  
  const levels = [];
  const { gridCount, upperPrice, lowerPrice, gridMode } = this;
  
  if (gridMode === 'arithmetic') {
    const step = (upperPrice - lowerPrice) / (gridCount - 1);
    for (let i = 0; i < gridCount; i++) {
      levels.push(lowerPrice + (i * step));
    }
  } else { // geometric
    const ratio = Math.pow(upperPrice / lowerPrice, 1 / (gridCount - 1));
    for (let i = 0; i < gridCount; i++) {
      levels.push(lowerPrice * Math.pow(ratio, i));
    }
  }
  
  return levels;
};

marketMakerBotSchema.methods.shouldRebalance = function() {
  const { currentInventory, configuration } = this;
  const deviation = Math.abs(currentInventory - configuration.inventoryTarget);
  
  return deviation > configuration.rebalanceThreshold;
};

marketMakerBotSchema.methods.getOptimalSpread = function(marketBid, marketAsk) {
  const { configuration, currentInventory } = this;
  const midPrice = (marketBid + marketAsk) / 2;
  
  // Adjust spread based on inventory imbalance
  let spreadAdjustment = 0;
  if (currentInventory > configuration.inventoryTarget) {
    // Too much inventory, increase ask price to sell
    spreadAdjustment = 0.0001 * (currentInventory - configuration.inventoryTarget);
  } else if (currentInventory < configuration.inventoryTarget) {
    // Too little inventory, decrease bid price to buy
    spreadAdjustment = -0.0001 * (configuration.inventoryTarget - currentInventory);
  }
  
  const baseSpread = midPrice * configuration.spreadPercentage;
  const adjustedSpread = baseSpread + spreadAdjustment;
  
  // Ensure spread is within min/max bounds
  const minSpread = configuration.minSpread || 0.0001;
  const maxSpread = configuration.maxSpread || 0.01;
  
  return Math.max(minSpread, Math.min(maxSpread, adjustedSpread));
};

// Pre-save middleware
marketMakerBotSchema.pre('save', function(next) {
  // Ensure symbol is uppercase
  if (this.symbol) {
    this.symbol = this.symbol.toUpperCase();
  }
  
  // Update timestamp
  this.lastUpdateAt = new Date();
  
  next();
});

// Pre-remove middleware
marketMakerBotSchema.pre('remove', async function(next) {
  // Log bot removal
  console.log(`Market maker bot ${this.name} (${this.symbol}) removed`);
  next();
});

module.exports = mongoose.model('MarketMakerBot', marketMakerBotSchema);