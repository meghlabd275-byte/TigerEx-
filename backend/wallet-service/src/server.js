const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const cron = require('node-cron');

// Import routes
const walletRoutes = require('./routes/walletRoutes');
const transactionRoutes = require('./routes/transactionRoutes');
const depositRoutes = require('./routes/depositRoutes');
const withdrawalRoutes = require('./routes/withdrawalRoutes');
const addressRoutes = require('./routes/addressRoutes');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

// Import services
const WalletService = require('./services/WalletService');
const TransactionService = require('./services/TransactionService');
const BlockchainService = require('./services/BlockchainService');
const SecurityService = require('./services/SecurityService');

const app = express();
const PORT = process.env.PORT || 3004;

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'wallet-service' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple(),
    }),
  ],
});

// Security middleware
app.use(helmet());
app.use(
  cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  })
);

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 500, // limit each IP to 500 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
});
app.use('/api/', limiter);

// Stricter rate limiting for sensitive operations
const sensitiveOperationsLimiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5 minutes
  max: 10, // limit each IP to 10 sensitive operations per 5 minutes
  message: 'Too many sensitive operations, please try again later.',
});
app.use('/api/withdrawals', sensitiveOperationsLimiter);
app.use('/api/addresses/generate', sensitiveOperationsLimiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Database connection
mongoose
  .connect(
    process.env.MONGODB_URI || 'mongodb://localhost:27017/tigerex_wallet',
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => {
    logger.info('Connected to MongoDB - Wallet Service');
  })
  .catch((error) => {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  });

// Routes
app.use('/api/wallets', walletRoutes);
app.use('/api/transactions', transactionRoutes);
app.use('/api/deposits', depositRoutes);
app.use('/api/withdrawals', withdrawalRoutes);
app.use('/api/addresses', addressRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'wallet-service',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    walletService: WalletService.getHealthStatus(),
    blockchainService: BlockchainService.getHealthStatus(),
  });
});

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found',
  });
});

// Initialize services
const initializeServices = async () => {
  try {
    logger.info('Initializing Wallet Services...');

    // Initialize Wallet Service
    await WalletService.initialize();

    // Initialize Transaction Service
    await TransactionService.initialize();

    // Initialize Blockchain Service
    await BlockchainService.initialize();

    // Initialize Security Service
    await SecurityService.initialize();

    logger.info('All Wallet Services initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize services:', error);
    process.exit(1);
  }
};

// Scheduled tasks
const initializeScheduledTasks = () => {
  // Process pending deposits every minute
  cron.schedule('* * * * *', async () => {
    try {
      await TransactionService.processPendingDeposits();
    } catch (error) {
      logger.error('Error processing pending deposits:', error);
    }
  });

  // Process pending withdrawals every 2 minutes
  cron.schedule('*/2 * * * *', async () => {
    try {
      await TransactionService.processPendingWithdrawals();
    } catch (error) {
      logger.error('Error processing pending withdrawals:', error);
    }
  });

  // Update blockchain confirmations every 30 seconds
  cron.schedule('*/30 * * * * *', async () => {
    try {
      await BlockchainService.updateConfirmations();
    } catch (error) {
      logger.error('Error updating confirmations:', error);
    }
  });

  // Generate wallet statistics every hour
  cron.schedule('0 * * * *', async () => {
    try {
      await WalletService.generateStatistics();
    } catch (error) {
      logger.error('Error generating wallet statistics:', error);
    }
  });

  // Security audit every 6 hours
  cron.schedule('0 */6 * * *', async () => {
    try {
      await SecurityService.performSecurityAudit();
    } catch (error) {
      logger.error('Error performing security audit:', error);
    }
  });

  logger.info('Scheduled tasks initialized');
};

app.listen(PORT, async () => {
  logger.info(`Wallet Service running on port ${PORT}`);
  await initializeServices();
  initializeScheduledTasks();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    WalletService.shutdown();
    TransactionService.shutdown();
    BlockchainService.shutdown();
    process.exit(0);
  });
});

module.exports = { app };
