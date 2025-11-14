const mongoose = require('mongoose');

const liquidityPoolSchema = new mongoose.Schema({
  symbol: {
    type: String,
    required: true,
    uppercase: true,
    index: true
  },
  totalBidLiquidity: {
    type: Number,
    default: 0,
    min: 0
  },
  totalAskLiquidity: {
    type: Number,
    default: 0,
    min: 0
  },
  totalLiquidity: {
    type: Number,
    default: 0,
    min: 0
  },
  spread: {
    type: Number,
    default: 0,
    min: 0
  },
  spreadPercent: {
    type: Number,
    default: 0,
    min: 0
  },
  midPrice: {
    type: Number,
    default: 0,
    min: 0
  },
  bestBid: {
    type: Number,
    default: 0,
    min: 0
  },
  bestAsk: {
    type: Number,
    default: 0,
    min: 0
  },
  exchangeCount: {
    type: Number,
    default: 0,
    min: 0
  },
  exchangeData: [{
    exchangeId: {
      type: String,
      required: true
    },
    exchangeName: {
      type: String,
      required: true
    },
    bidLiquidity: {
      type: Number,
      default: 0,
      min: 0
    },
    askLiquidity: {
      type: Number,
      default: 0,
      min: 0
    },
    totalLiquidity: {
      type: Number,
      default: 0,
      min: 0
    },
    percentage: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    bestBid: {
      type: Number,
      default: 0,
      min: 0
    },
    bestAsk: {
      type: Number,
      default: 0,
      min: 0
    },
    connected: {
      type: Boolean,
      default: false
    },
    lastUpdate: {
      type: Date,
      default: Date.now
    }
  }],
  orderBook: {
    bids: [{
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
      exchange: {
        type: String,
        required: true
      },
      cumulativeQuantity: {
        type: Number,
        default: 0,
        min: 0
      },
      cumulativeDepth: {
        type: Number,
        default: 0,
        min: 0
      }
    }],
    asks: [{
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
      exchange: {
        type: String,
        required: true
      },
      cumulativeQuantity: {
        type: Number,
        default: 0,
        min: 0
      },
      cumulativeDepth: {
        type: Number,
        default: 0,
        min: 0
      }
    }]
  },
  volume24h: {
    type: Number,
    default: 0,
    min: 0
  },
  change24h: {
    type: Number,
    default: 0
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
  isActive: {
    type: Boolean,
    default: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  updatedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  lastUpdate: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes for performance
liquidityPoolSchema.index({ symbol: 1, isActive: 1 });
liquidityPoolSchema.index({ lastUpdate: 1 });
liquidityPoolSchema.index({ 'exchangeData.exchangeId': 1 });

// Virtuals
liquidityPoolSchema.virtual('spreadValue').get(function() {
  return this.bestAsk - this.bestBid;
});

liquidityPoolSchema.virtual('isLiquid').get(function() {
  return this.totalLiquidity > 1000000; // Consider liquid if > $1M
});

// Static methods
liquidityPoolSchema.statics.findBySymbol = function(symbol) {
  return this.findOne({ symbol, isActive: true })
    .sort({ lastUpdate: -1 })
    .populate('createdBy', 'username email')
    .populate('updatedBy', 'username email');
};

liquidityPoolSchema.statics.findActivePools = function() {
  return this.find({ isActive: true })
    .sort({ totalLiquidity: -1 })
    .populate('createdBy', 'username email');
};

liquidityPoolSchema.statics.findPoolsByExchange = function(exchangeId) {
  return this.find({ 
    isActive: true,
    'exchangeData.exchangeId': exchangeId 
  })
  .sort({ lastUpdate: -1 });
};

// Instance methods
liquidityPoolSchema.methods.updateLiquidity = function(liquidityData) {
  this.totalBidLiquidity = liquidityData.totalBidLiquidity || this.totalBidLiquidity;
  this.totalAskLiquidity = liquidityData.totalAskLiquidity || this.totalAskLiquidity;
  this.totalLiquidity = liquidityData.totalLiquidity || this.totalLiquidity;
  this.spread = liquidityData.spread || this.spread;
  this.spreadPercent = liquidityData.spreadPercent || this.spreadPercent;
  this.midPrice = liquidityData.midPrice || this.midPrice;
  this.bestBid = liquidityData.bestBid || this.bestBid;
  this.bestAsk = liquidityData.bestAsk || this.bestAsk;
  this.exchangeCount = liquidityData.exchangeCount || this.exchangeCount;
  this.lastUpdate = new Date();
  
  if (liquidityData.exchangeData) {
    this.exchangeData = liquidityData.exchangeData;
  }
  
  if (liquidityData.orderBook) {
    this.orderBook = liquidityData.orderBook;
  }
  
  return this.save();
};

liquidityPoolSchema.methods.addExchangeData = function(exchangeData) {
  const existingIndex = this.exchangeData.findIndex(
    data => data.exchangeId === exchangeData.exchangeId
  );
  
  if (existingIndex >= 0) {
    this.exchangeData[existingIndex] = { ...this.exchangeData[existingIndex], ...exchangeData };
  } else {
    this.exchangeData.push(exchangeData);
  }
  
  this.lastUpdate = new Date();
  return this.save();
};

liquidityPoolSchema.methods.removeExchangeData = function(exchangeId) {
  this.exchangeData = this.exchangeData.filter(data => data.exchangeId !== exchangeId);
  this.lastUpdate = new Date();
  return this.save();
};

liquidityPoolSchema.methods.deactivate = function() {
  this.isActive = false;
  this.lastUpdate = new Date();
  return this.save();
};

liquidityPoolSchema.methods.activate = function() {
  this.isActive = true;
  this.lastUpdate = new Date();
  return this.save();
};

// Pre-save middleware
liquidityPoolSchema.pre('save', function(next) {
  // Calculate spread if not provided
  if (this.bestBid && this.bestAsk && !this.spread) {
    this.spread = this.bestAsk - this.bestBid;
    this.spreadPercent = (this.spread / this.midPrice) * 100;
  }
  
  // Update timestamp
  this.lastUpdate = new Date();
  
  next();
});

module.exports = mongoose.model('LiquidityPool', liquidityPoolSchema);