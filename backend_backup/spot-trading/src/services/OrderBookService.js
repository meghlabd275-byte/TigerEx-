const EventEmitter = require('events');
const winston = require('winston');
const TradingEngine = require('./TradingEngine');

class OrderBookService extends EventEmitter {
  constructor() {
    super();
    this.orderBooks = new Map(); // symbol -> order book data
    this.subscribers = new Map(); // symbol -> Set of subscriber callbacks
    this.isRunning = false;

    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'orderbook-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/orderbook.log' }),
        new winston.transports.Console(),
      ],
    });
  }

  async initialize() {
    try {
      this.logger.info('Initializing Order Book Service...');

      // Listen to trading engine events
      TradingEngine.on('orderProcessed', this.handleOrderProcessed.bind(this));
      TradingEngine.on('orderCanceled', this.handleOrderCanceled.bind(this));
      TradingEngine.on('tradeExecuted', this.handleTradeExecuted.bind(this));

      this.isRunning = true;
      this.logger.info('Order Book Service initialized successfully');

      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Order Book Service:', error);
      throw error;
    }
  }

  handleOrderProcessed(order, result) {
    this.updateOrderBook(order.symbol);
    this.notifySubscribers(order.symbol, 'orderProcessed', { order, result });
  }

  handleOrderCanceled(order, reason) {
    this.updateOrderBook(order.symbol);
    this.notifySubscribers(order.symbol, 'orderCanceled', { order, reason });
  }

  handleTradeExecuted(trade) {
    this.updateOrderBook(trade.symbol);
    this.notifySubscribers(trade.symbol, 'tradeExecuted', trade);
  }

  async updateOrderBook(symbol) {
    try {
      // Get fresh order book data from trading engine
      const orderBookData = TradingEngine.getOrderBook(symbol, 50);

      // Calculate aggregated levels
      const aggregatedBids = this.aggregateOrders(orderBookData.bids);
      const aggregatedAsks = this.aggregateOrders(orderBookData.asks);

      // Calculate spread
      const bestBid =
        aggregatedBids.length > 0 ? parseFloat(aggregatedBids[0].price) : 0;
      const bestAsk =
        aggregatedAsks.length > 0 ? parseFloat(aggregatedAsks[0].price) : 0;
      const spread = bestAsk > 0 && bestBid > 0 ? bestAsk - bestBid : 0;
      const spreadPercent = bestAsk > 0 ? (spread / bestAsk) * 100 : 0;

      const orderBook = {
        symbol,
        bids: aggregatedBids,
        asks: aggregatedAsks,
        spread: {
          absolute: spread,
          percent: spreadPercent,
        },
        timestamp: new Date(),
        lastUpdateId: Date.now(),
      };

      this.orderBooks.set(symbol, orderBook);

      // Notify all subscribers
      this.notifySubscribers(symbol, 'orderBookUpdate', orderBook);
    } catch (error) {
      this.logger.error(`Error updating order book for ${symbol}:`, error);
    }
  }

  aggregateOrders(orders) {
    const priceMap = new Map();

    orders.forEach((order) => {
      const price = order.price;
      const quantity = parseFloat(order.quantity);

      if (priceMap.has(price)) {
        priceMap.set(price, priceMap.get(price) + quantity);
      } else {
        priceMap.set(price, quantity);
      }
    });

    return Array.from(priceMap.entries())
      .map(([price, quantity]) => ({
        price: price,
        quantity: quantity.toString(),
        total: (parseFloat(price) * quantity).toString(),
      }))
      .sort((a, b) => parseFloat(b.price) - parseFloat(a.price)); // Descending for bids
  }

  getOrderBook(symbol, depth = 20) {
    const orderBook = this.orderBooks.get(symbol);

    if (!orderBook) {
      return {
        symbol,
        bids: [],
        asks: [],
        spread: { absolute: 0, percent: 0 },
        timestamp: new Date(),
        lastUpdateId: 0,
      };
    }

    return {
      ...orderBook,
      bids: orderBook.bids.slice(0, depth),
      asks: orderBook.asks.slice(0, depth),
    };
  }

  subscribe(symbol, callback) {
    if (!this.subscribers.has(symbol)) {
      this.subscribers.set(symbol, new Set());
    }

    this.subscribers.get(symbol).add(callback);

    // Send current order book immediately
    const orderBook = this.getOrderBook(symbol);
    callback('orderBookSnapshot', orderBook);

    // Return unsubscribe function
    return () => {
      const symbolSubscribers = this.subscribers.get(symbol);
      if (symbolSubscribers) {
        symbolSubscribers.delete(callback);
        if (symbolSubscribers.size === 0) {
          this.subscribers.delete(symbol);
        }
      }
    };
  }

  notifySubscribers(symbol, event, data) {
    const symbolSubscribers = this.subscribers.get(symbol);
    if (symbolSubscribers) {
      symbolSubscribers.forEach((callback) => {
        try {
          callback(event, data);
        } catch (error) {
          this.logger.error('Error notifying subscriber:', error);
        }
      });
    }
  }

  getActiveSymbols() {
    return Array.from(this.orderBooks.keys());
  }

  getOrderBookStats(symbol) {
    const orderBook = this.orderBooks.get(symbol);
    if (!orderBook) {
      return null;
    }

    const bidDepth = orderBook.bids.reduce(
      (sum, bid) => sum + parseFloat(bid.quantity),
      0
    );
    const askDepth = orderBook.asks.reduce(
      (sum, ask) => sum + parseFloat(ask.quantity),
      0
    );
    const bidValue = orderBook.bids.reduce(
      (sum, bid) => sum + parseFloat(bid.total),
      0
    );
    const askValue = orderBook.asks.reduce(
      (sum, ask) => sum + parseFloat(ask.total),
      0
    );

    return {
      symbol,
      bidDepth,
      askDepth,
      bidValue,
      askValue,
      spread: orderBook.spread,
      levels: {
        bids: orderBook.bids.length,
        asks: orderBook.asks.length,
      },
      lastUpdate: orderBook.timestamp,
    };
  }

  getAllOrderBookStats() {
    const stats = {};

    for (const symbol of this.orderBooks.keys()) {
      stats[symbol] = this.getOrderBookStats(symbol);
    }

    return stats;
  }

  getHealthStatus() {
    return {
      isRunning: this.isRunning,
      activeOrderBooks: this.orderBooks.size,
      totalSubscribers: Array.from(this.subscribers.values()).reduce(
        (sum, subscribers) => sum + subscribers.size,
        0
      ),
      symbols: this.getActiveSymbols(),
    };
  }

  shutdown() {
    this.logger.info('Shutting down Order Book Service...');
    this.isRunning = false;
    this.orderBooks.clear();
    this.subscribers.clear();
    this.emit('shutdown');
  }
}

module.exports = new OrderBookService();
