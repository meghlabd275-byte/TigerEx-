const Payment = require('../models/Payment');
const winston = require('winston');
const EventEmitter = require('events');
const Decimal = require('decimal.js');

// Import payment providers
const StripeService = require('./StripeService');
const PayPalService = require('./PayPalService');
const BankTransferService = require('./BankTransferService');
const ComplianceService = require('./ComplianceService');

class PaymentService extends EventEmitter {
  constructor() {
    super();
    this.isRunning = false;
    this.statistics = {
      paymentsProcessed: 0,
      totalVolume: new Map(),
      successRate: 0,
      averageProcessingTime: 0,
    };

    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'payment-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/payment-service.log' }),
        new winston.transports.Console(),
      ],
    });
  }

  async initialize() {
    try {
      this.logger.info('Initializing Payment Service...');

      // Load existing statistics
      await this.loadStatistics();

      this.isRunning = true;
      this.logger.info('Payment Service initialized successfully');

      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Payment Service:', error);
      throw error;
    }
  }

  async createPayment(paymentData) {
    try {
      const {
        userId,
        type,
        method,
        currency,
        amount,
        billingAddress,
        paymentInstrument,
        metadata = {},
      } = paymentData;

      // Calculate fees
      const fee = this.calculateFee(method, currency, amount);
      const netAmount = new Decimal(amount).minus(fee);

      // Create payment record
      const payment = new Payment({
        userId,
        type,
        method,
        currency: currency.toUpperCase(),
        amount,
        fee,
        netAmount: netAmount.toNumber(),
        billingAddress,
        paymentInstrument,
        metadata: {
          ...metadata,
          source: metadata.source || 'WEB',
          userAgent: metadata.userAgent,
          ipAddress: metadata.ipAddress,
        },
        status: 'PENDING',
      });

      // Perform risk assessment
      await this.performRiskAssessment(payment, metadata);

      // Check compliance
      await this.performComplianceCheck(payment);

      await payment.save();

      this.logger.info(`Created payment: ${payment.paymentId}`);
      this.emit('paymentCreated', payment);

      return payment;
    } catch (error) {
      this.logger.error('Error creating payment:', error);
      throw error;
    }
  }

  async processPayment(paymentId) {
    try {
      const payment = await Payment.findOne({ paymentId });
      if (!payment) {
        throw new Error('Payment not found');
      }

      if (payment.status !== 'PENDING') {
        throw new Error(`Payment is not in pending status: ${payment.status}`);
      }

      // Check if payment is high risk
      if (payment.isHighRisk) {
        payment.updateStatus('PROCESSING', 'SYSTEM', {
          reason: 'High risk payment requires manual review',
        });
        await payment.save();

        this.emit('paymentRequiresReview', payment);
        return payment;
      }

      // Process based on payment method
      let result;
      switch (payment.method) {
        case 'CREDIT_CARD':
        case 'DEBIT_CARD':
          result = await this.processCardPayment(payment);
          break;
        case 'BANK_TRANSFER':
        case 'ACH':
          result = await this.processBankTransfer(payment);
          break;
        case 'PAYPAL':
          result = await this.processPayPalPayment(payment);
          break;
        default:
          throw new Error(`Unsupported payment method: ${payment.method}`);
      }

      // Update payment with provider response
      payment.provider = {
        name: result.provider,
        transactionId: result.transactionId,
        paymentIntentId: result.paymentIntentId,
        metadata: result.metadata,
      };

      payment.updateStatus('PROCESSING', 'SYSTEM', {
        provider: result.provider,
        transactionId: result.transactionId,
      });

      await payment.save();

      this.logger.info(`Processing payment: ${payment.paymentId}`);
      this.emit('paymentProcessing', payment);

      return payment;
    } catch (error) {
      this.logger.error(`Error processing payment ${paymentId}:`, error);

      // Update payment status to failed
      const payment = await Payment.findOne({ paymentId });
      if (payment) {
        payment.updateStatus('FAILED', 'SYSTEM', { error: error.message });
        await payment.save();
        this.emit('paymentFailed', payment);
      }

      throw error;
    }
  }

  async processCardPayment(payment) {
    try {
      const result = await StripeService.processPayment({
        amount: payment.amount,
        currency: payment.currency,
        paymentMethod: payment.paymentInstrument,
        billingAddress: payment.billingAddress,
        metadata: {
          paymentId: payment.paymentId,
          userId: payment.userId,
        },
      });

      return {
        provider: 'STRIPE',
        transactionId: result.id,
        paymentIntentId: result.payment_intent,
        metadata: result,
      };
    } catch (error) {
      this.logger.error('Error processing card payment:', error);
      throw error;
    }
  }

  async processBankTransfer(payment) {
    try {
      const result = await BankTransferService.initiateTransfer({
        amount: payment.amount,
        currency: payment.currency,
        bankAccount: payment.paymentInstrument,
        metadata: {
          paymentId: payment.paymentId,
          userId: payment.userId,
        },
      });

      return {
        provider: 'BANK',
        transactionId: result.transferId,
        metadata: result,
      };
    } catch (error) {
      this.logger.error('Error processing bank transfer:', error);
      throw error;
    }
  }

  async processPayPalPayment(payment) {
    try {
      const result = await PayPalService.processPayment({
        amount: payment.amount,
        currency: payment.currency,
        metadata: {
          paymentId: payment.paymentId,
          userId: payment.userId,
        },
      });

      return {
        provider: 'PAYPAL',
        transactionId: result.id,
        metadata: result,
      };
    } catch (error) {
      this.logger.error('Error processing PayPal payment:', error);
      throw error;
    }
  }

  async completePayment(paymentId, providerData) {
    try {
      const payment = await Payment.findOne({ paymentId });
      if (!payment) {
        throw new Error('Payment not found');
      }

      // Update payment with completion data
      payment.status = 'COMPLETED';
      payment.completedAt = new Date();
      payment.processing.webhookReceived = true;
      payment.processing.webhookTimestamp = new Date();

      // Update provider information
      if (providerData) {
        payment.provider = {
          ...payment.provider,
          ...providerData,
        };
      }

      payment.addAuditEntry('PAYMENT_COMPLETED', 'SYSTEM', {
        provider: payment.provider.name,
        transactionId: payment.provider.transactionId,
      });

      await payment.save();

      this.statistics.paymentsProcessed++;
      this.updateVolumeStatistics(payment.currency, payment.amount);

      this.logger.info(`Completed payment: ${payment.paymentId}`);
      this.emit('paymentCompleted', payment);

      return payment;
    } catch (error) {
      this.logger.error(`Error completing payment ${paymentId}:`, error);
      throw error;
    }
  }

  async performRiskAssessment(payment, metadata) {
    try {
      let riskScore = 0;
      const riskFactors = [];

      // Amount-based risk
      const amount = parseFloat(payment.amount);
      if (amount > 10000) {
        riskScore += 30;
        riskFactors.push('HIGH_AMOUNT');
      } else if (amount > 5000) {
        riskScore += 15;
        riskFactors.push('MEDIUM_AMOUNT');
      }

      // New user risk
      const userPaymentHistory = await Payment.countDocuments({
        userId: payment.userId,
        status: 'COMPLETED',
      });

      if (userPaymentHistory === 0) {
        riskScore += 20;
        riskFactors.push('NEW_USER');
      } else if (userPaymentHistory < 5) {
        riskScore += 10;
        riskFactors.push('LIMITED_HISTORY');
      }

      // Geographic risk (mock implementation)
      if (metadata.ipAddress) {
        const geoRisk = await this.assessGeographicRisk(metadata.ipAddress);
        riskScore += geoRisk.score;
        if (geoRisk.factors.length > 0) {
          riskFactors.push(...geoRisk.factors);
        }
      }

      // Payment method risk
      if (['CREDIT_CARD', 'DEBIT_CARD'].includes(payment.method)) {
        riskScore += 5;
        riskFactors.push('CARD_PAYMENT');
      }

      // Update payment with risk assessment
      payment.updateRiskScore(riskScore, riskFactors);

      if (metadata.ipAddress) {
        payment.riskAssessment.ipAddress = metadata.ipAddress;
      }

      this.logger.info(
        `Risk assessment for payment ${payment.paymentId}: ${riskScore} (${payment.riskAssessment.level})`
      );
    } catch (error) {
      this.logger.error('Error performing risk assessment:', error);
      // Don't throw error, just log it
    }
  }

  async assessGeographicRisk(ipAddress) {
    // Mock implementation - in production, use actual IP geolocation service
    const highRiskCountries = ['XX', 'YY', 'ZZ']; // Mock country codes
    const mockCountry = 'US'; // Mock detected country

    let score = 0;
    const factors = [];

    if (highRiskCountries.includes(mockCountry)) {
      score += 25;
      factors.push('HIGH_RISK_COUNTRY');
    }

    return { score, factors };
  }

  async performComplianceCheck(payment) {
    try {
      // Basic AML check
      const amlResult = await ComplianceService.performAMLCheck({
        userId: payment.userId,
        amount: payment.amount,
        currency: payment.currency,
        paymentMethod: payment.method,
      });

      payment.compliance.amlStatus = amlResult.status;
      payment.compliance.sanctionsCheck = amlResult.sanctionsCheck;

      // If high risk or sanctions hit, require manual review
      if (
        amlResult.status === 'REVIEW_REQUIRED' ||
        amlResult.sanctionsCheck === 'HIT'
      ) {
        payment.updateRiskScore(payment.riskAssessment.score + 50, [
          ...payment.riskAssessment.factors,
          'AML_REVIEW_REQUIRED',
        ]);
      }

      this.logger.info(
        `Compliance check for payment ${payment.paymentId}: AML=${amlResult.status}, Sanctions=${amlResult.sanctionsCheck}`
      );
    } catch (error) {
      this.logger.error('Error performing compliance check:', error);
      // Set to review required on error
      payment.compliance.amlStatus = 'REVIEW_REQUIRED';
    }
  }

  calculateFee(method, currency, amount) {
    const feeStructure = {
      CREDIT_CARD: { percentage: 0.029, fixed: 0.3 },
      DEBIT_CARD: { percentage: 0.029, fixed: 0.3 },
      BANK_TRANSFER: { percentage: 0.008, fixed: 0 },
      ACH: { percentage: 0.008, fixed: 0 },
      PAYPAL: { percentage: 0.034, fixed: 0.3 },
      WIRE_TRANSFER: { percentage: 0, fixed: 25 },
    };

    const fees = feeStructure[method] || { percentage: 0.01, fixed: 0 };
    const percentageFee = new Decimal(amount).mul(fees.percentage);
    const totalFee = percentageFee.plus(fees.fixed);

    return totalFee.toNumber();
  }

  async processPendingDeposits() {
    try {
      const pendingDeposits = await Payment.findPendingPayments('DEPOSIT');

      for (const deposit of pendingDeposits) {
        try {
          await this.processPayment(deposit.paymentId);
        } catch (error) {
          this.logger.error(
            `Error processing pending deposit ${deposit.paymentId}:`,
            error
          );
          deposit.scheduleRetry();
          await deposit.save();
        }
      }
    } catch (error) {
      this.logger.error('Error processing pending deposits:', error);
    }
  }

  async processPendingWithdrawals() {
    try {
      const pendingWithdrawals =
        await Payment.findPendingPayments('WITHDRAWAL');

      for (const withdrawal of pendingWithdrawals) {
        try {
          await this.processPayment(withdrawal.paymentId);
        } catch (error) {
          this.logger.error(
            `Error processing pending withdrawal ${withdrawal.paymentId}:`,
            error
          );
          withdrawal.scheduleRetry();
          await withdrawal.save();
        }
      }
    } catch (error) {
      this.logger.error('Error processing pending withdrawals:', error);
    }
  }

  async updatePaymentStatuses() {
    try {
      const processingPayments = await Payment.find({
        status: 'PROCESSING',
        'provider.name': { $exists: true },
      });

      for (const payment of processingPayments) {
        try {
          let status;
          switch (payment.provider.name) {
            case 'STRIPE':
              status = await StripeService.getPaymentStatus(
                payment.provider.transactionId
              );
              break;
            case 'PAYPAL':
              status = await PayPalService.getPaymentStatus(
                payment.provider.transactionId
              );
              break;
            case 'BANK':
              status = await BankTransferService.getTransferStatus(
                payment.provider.transactionId
              );
              break;
            default:
              continue;
          }

          if (status.status === 'succeeded' || status.status === 'completed') {
            await this.completePayment(payment.paymentId, status);
          } else if (
            status.status === 'failed' ||
            status.status === 'cancelled'
          ) {
            payment.updateStatus('FAILED', 'SYSTEM', {
              reason: status.failure_reason || 'Payment failed at provider',
            });
            await payment.save();
            this.emit('paymentFailed', payment);
          }
        } catch (error) {
          this.logger.error(
            `Error updating payment status ${payment.paymentId}:`,
            error
          );
        }
      }
    } catch (error) {
      this.logger.error('Error updating payment statuses:', error);
    }
  }

  updateVolumeStatistics(currency, amount) {
    const current = this.statistics.totalVolume.get(currency) || 0;
    this.statistics.totalVolume.set(currency, current + parseFloat(amount));
  }

  async loadStatistics() {
    try {
      const paymentCount = await Payment.countDocuments({
        status: 'COMPLETED',
      });
      this.statistics.paymentsProcessed = paymentCount;

      // Load volume statistics
      const volumeStats = await Payment.aggregate([
        { $match: { status: 'COMPLETED' } },
        {
          $group: {
            _id: '$currency',
            totalVolume: { $sum: { $toDouble: '$amount' } },
            count: { $sum: 1 },
          },
        },
      ]);

      volumeStats.forEach((stat) => {
        this.statistics.totalVolume.set(stat._id, stat.totalVolume);
      });

      this.logger.info('Payment statistics loaded successfully');
    } catch (error) {
      this.logger.error('Error loading payment statistics:', error);
    }
  }

  async generateStatistics() {
    try {
      await this.loadStatistics();

      const stats = {
        timestamp: new Date(),
        payments: {
          total: this.statistics.paymentsProcessed,
          pending: await Payment.countDocuments({
            status: { $in: ['PENDING', 'PROCESSING'] },
          }),
          completed: await Payment.countDocuments({ status: 'COMPLETED' }),
          failed: await Payment.countDocuments({
            status: { $in: ['FAILED', 'CANCELLED'] },
          }),
        },
        volume: Object.fromEntries(this.statistics.totalVolume),
        methods: await this.getMethodStatistics(),
        riskDistribution: await this.getRiskDistribution(),
      };

      this.emit('statisticsGenerated', stats);
      return stats;
    } catch (error) {
      this.logger.error('Error generating statistics:', error);
      throw error;
    }
  }

  async getMethodStatistics() {
    return await Payment.aggregate([
      { $match: { status: 'COMPLETED' } },
      {
        $group: {
          _id: '$method',
          count: { $sum: 1 },
          totalVolume: { $sum: { $toDouble: '$amount' } },
        },
      },
    ]);
  }

  async getRiskDistribution() {
    return await Payment.aggregate([
      {
        $group: {
          _id: '$riskAssessment.level',
          count: { $sum: 1 },
        },
      },
    ]);
  }

  getHealthStatus() {
    return {
      isRunning: this.isRunning,
      statistics: {
        paymentsProcessed: this.statistics.paymentsProcessed,
        supportedCurrencies: Array.from(this.statistics.totalVolume.keys()),
        totalVolume: Object.fromEntries(this.statistics.totalVolume),
      },
      uptime: process.uptime(),
    };
  }

  shutdown() {
    this.logger.info('Shutting down Payment Service...');
    this.isRunning = false;
    this.emit('shutdown');
  }
}

module.exports = new PaymentService();
