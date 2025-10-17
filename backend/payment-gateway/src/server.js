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

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const cron = require('node-cron');
const multer = require('multer');
const path = require('path');

// Import routes
const paymentRoutes = require('./routes/paymentRoutes');
const depositRoutes = require('./routes/depositRoutes');
const withdrawalRoutes = require('./routes/withdrawalRoutes');
const bankAccountRoutes = require('./routes/bankAccountRoutes');
const cardRoutes = require('./routes/cardRoutes');
const kycRoutes = require('./routes/kycRoutes');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');

// Import services
const PaymentService = require('./services/PaymentService');
const StripeService = require('./services/StripeService');
const PayPalService = require('./services/PayPalService');
const BankTransferService = require('./services/BankTransferService');
const KYCService = require('./services/KYCService');
const ComplianceService = require('./services/ComplianceService');

const app = express();
const PORT = process.env.PORT || 3005;

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'payment-gateway' },
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
  max: 300, // limit each IP to 300 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
});
app.use('/api/', limiter);

// Stricter rate limiting for sensitive operations
const sensitiveOperationsLimiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5 minutes
  max: 5, // limit each IP to 5 sensitive operations per 5 minutes
  message: 'Too many sensitive operations, please try again later.',
});
app.use('/api/withdrawals', sensitiveOperationsLimiter);
app.use('/api/kyc', sensitiveOperationsLimiter);

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/kyc/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(
      null,
      file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname)
    );
  },
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|pdf/;
    const extname = allowedTypes.test(
      path.extname(file.originalname).toLowerCase()
    );
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only images (JPEG, JPG, PNG) and PDF files are allowed'));
    }
  },
});

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve uploaded files
app.use('/uploads', express.static('uploads'));

// Database connection
mongoose
  .connect(
    process.env.MONGODB_URI || 'mongodb://localhost:27017/tigerex_payments',
    {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    }
  )
  .then(() => {
    logger.info('Connected to MongoDB - Payment Gateway Service');
  })
  .catch((error) => {
    logger.error('MongoDB connection error:', error);
    process.exit(1);
  });

// Routes
app.use('/api/payments', paymentRoutes);
app.use('/api/deposits', depositRoutes);
app.use('/api/withdrawals', withdrawalRoutes);
app.use('/api/bank-accounts', bankAccountRoutes);
app.use('/api/cards', cardRoutes);
app.use(
  '/api/kyc',
  upload.fields([
    { name: 'idDocument', maxCount: 2 },
    { name: 'proofOfAddress', maxCount: 2 },
    { name: 'selfie', maxCount: 1 },
  ]),
  kycRoutes
);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'payment-gateway',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    paymentService: PaymentService.getHealthStatus(),
    stripeService: StripeService.getHealthStatus(),
    paypalService: PayPalService.getHealthStatus(),
    kycService: KYCService.getHealthStatus(),
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
    logger.info('Initializing Payment Gateway Services...');

    // Initialize Payment Service
    await PaymentService.initialize();

    // Initialize Stripe Service
    await StripeService.initialize();

    // Initialize PayPal Service
    await PayPalService.initialize();

    // Initialize Bank Transfer Service
    await BankTransferService.initialize();

    // Initialize KYC Service
    await KYCService.initialize();

    // Initialize Compliance Service
    await ComplianceService.initialize();

    logger.info('All Payment Gateway Services initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize services:', error);
    process.exit(1);
  }
};

// Scheduled tasks
const initializeScheduledTasks = () => {
  // Process pending deposits every 2 minutes
  cron.schedule('*/2 * * * *', async () => {
    try {
      await PaymentService.processPendingDeposits();
    } catch (error) {
      logger.error('Error processing pending deposits:', error);
    }
  });

  // Process pending withdrawals every 5 minutes
  cron.schedule('*/5 * * * *', async () => {
    try {
      await PaymentService.processPendingWithdrawals();
    } catch (error) {
      logger.error('Error processing pending withdrawals:', error);
    }
  });

  // Update payment statuses every minute
  cron.schedule('* * * * *', async () => {
    try {
      await PaymentService.updatePaymentStatuses();
    } catch (error) {
      logger.error('Error updating payment statuses:', error);
    }
  });

  // Process KYC documents every 10 minutes
  cron.schedule('*/10 * * * *', async () => {
    try {
      await KYCService.processKYCDocuments();
    } catch (error) {
      logger.error('Error processing KYC documents:', error);
    }
  });

  // Compliance monitoring every hour
  cron.schedule('0 * * * *', async () => {
    try {
      await ComplianceService.performComplianceCheck();
    } catch (error) {
      logger.error('Error performing compliance check:', error);
    }
  });

  // Generate payment statistics every 6 hours
  cron.schedule('0 */6 * * *', async () => {
    try {
      await PaymentService.generateStatistics();
    } catch (error) {
      logger.error('Error generating payment statistics:', error);
    }
  });

  logger.info('Payment Gateway scheduled tasks initialized');
};

app.listen(PORT, async () => {
  logger.info(`Payment Gateway Service running on port ${PORT}`);
  await initializeServices();
  initializeScheduledTasks();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    mongoose.connection.close();
    PaymentService.shutdown();
    StripeService.shutdown();
    PayPalService.shutdown();
    BankTransferService.shutdown();
    KYCService.shutdown();
    ComplianceService.shutdown();
    process.exit(0);
  });
});

module.exports = { app };
