const winston = require('winston');
const EventEmitter = require('events');
const Payment = require('../models/Payment');

class ComplianceService extends EventEmitter {
  constructor() {
    super();
    this.isRunning = false;
    this.sanctionsList = new Set(); // In production, load from actual sanctions database
    this.highRiskCountries = new Set(['AF', 'IR', 'KP', 'SY']); // Example high-risk countries

    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'compliance-service' },
      transports: [
        new winston.transports.File({
          filename: 'logs/compliance-service.log',
        }),
        new winston.transports.Console(),
      ],
    });
  }

  async initialize() {
    try {
      this.logger.info('Initializing Compliance Service...');

      // Load sanctions lists and compliance rules
      await this.loadSanctionsList();
      await this.loadComplianceRules();

      this.isRunning = true;
      this.logger.info('Compliance Service initialized successfully');

      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Compliance Service:', error);
      throw error;
    }
  }

  async loadSanctionsList() {
    try {
      // In production, load from OFAC, UN, EU sanctions databases
      // This is a mock implementation
      const mockSanctionedEntities = [
        'sanctioned_entity_1',
        'sanctioned_entity_2',
        'sanctioned_entity_3',
      ];

      mockSanctionedEntities.forEach((entity) => {
        this.sanctionsList.add(entity.toLowerCase());
      });

      this.logger.info(`Loaded ${this.sanctionsList.size} sanctioned entities`);
    } catch (error) {
      this.logger.error('Error loading sanctions list:', error);
      throw error;
    }
  }

  async loadComplianceRules() {
    try {
      // Load compliance rules and thresholds
      this.complianceRules = {
        dailyTransactionLimit: {
          USD: 10000,
          EUR: 9000,
          GBP: 8000,
        },
        monthlyTransactionLimit: {
          USD: 50000,
          EUR: 45000,
          GBP: 40000,
        },
        suspiciousActivityThresholds: {
          rapidTransactions: 5, // 5 transactions within 1 hour
          roundAmountThreshold: 1000, // Amounts ending in 000
          velocityThreshold: 0.8, // 80% increase in transaction velocity
        },
        kycRequirements: {
          BASIC: { maxAmount: 1000, maxDaily: 2000 },
          INTERMEDIATE: { maxAmount: 5000, maxDaily: 10000 },
          ADVANCED: { maxAmount: 50000, maxDaily: 100000 },
        },
      };

      this.logger.info('Compliance rules loaded successfully');
    } catch (error) {
      this.logger.error('Error loading compliance rules:', error);
      throw error;
    }
  }

  async performAMLCheck(checkData) {
    try {
      const {
        userId,
        amount,
        currency,
        paymentMethod,
        userInfo = {},
      } = checkData;

      let amlStatus = 'APPROVED';
      let sanctionsCheck = 'CLEAR';
      const flags = [];

      // Sanctions screening
      const sanctionsResult = await this.performSanctionsCheck(userInfo);
      if (sanctionsResult.hit) {
        sanctionsCheck = 'HIT';
        amlStatus = 'REJECTED';
        flags.push('SANCTIONS_HIT');
      }

      // Transaction amount analysis
      const amountAnalysis = await this.analyzeTransactionAmount(
        userId,
        amount,
        currency
      );
      if (amountAnalysis.suspicious) {
        flags.push(...amountAnalysis.flags);
        if (amountAnalysis.severity === 'HIGH') {
          amlStatus = 'REVIEW_REQUIRED';
        }
      }

      // Transaction pattern analysis
      const patternAnalysis = await this.analyzeTransactionPatterns(userId);
      if (patternAnalysis.suspicious) {
        flags.push(...patternAnalysis.flags);
        if (patternAnalysis.severity === 'HIGH') {
          amlStatus = 'REVIEW_REQUIRED';
        }
      }

      // Geographic risk assessment
      const geoRisk = await this.assessGeographicRisk(userInfo);
      if (geoRisk.highRisk) {
        flags.push(...geoRisk.flags);
        if (geoRisk.severity === 'HIGH') {
          amlStatus = 'REVIEW_REQUIRED';
        }
      }

      // KYC level check
      const kycCheck = await this.checkKYCRequirements(
        userId,
        amount,
        currency
      );
      if (!kycCheck.sufficient) {
        flags.push('INSUFFICIENT_KYC');
        amlStatus = 'REVIEW_REQUIRED';
      }

      const result = {
        status: amlStatus,
        sanctionsCheck,
        flags,
        riskScore: this.calculateAMLRiskScore(flags),
        timestamp: new Date(),
      };

      this.logger.info(
        `AML check for user ${userId}: ${amlStatus} (${flags.length} flags)`
      );

      // Log high-risk transactions
      if (amlStatus === 'REVIEW_REQUIRED' || sanctionsCheck === 'HIT') {
        await this.logSuspiciousActivity(userId, checkData, result);
      }

      return result;
    } catch (error) {
      this.logger.error('Error performing AML check:', error);
      return {
        status: 'REVIEW_REQUIRED',
        sanctionsCheck: 'ERROR',
        flags: ['AML_CHECK_ERROR'],
        riskScore: 100,
        timestamp: new Date(),
      };
    }
  }

  async performSanctionsCheck(userInfo) {
    try {
      const { name, email, address } = userInfo;

      // Check name against sanctions list
      if (name && this.sanctionsList.has(name.toLowerCase())) {
        return { hit: true, matchType: 'NAME', matchValue: name };
      }

      // Check email domain against sanctions list
      if (email) {
        const domain = email.split('@')[1];
        if (domain && this.sanctionsList.has(domain.toLowerCase())) {
          return { hit: true, matchType: 'EMAIL_DOMAIN', matchValue: domain };
        }
      }

      // Check country against sanctions list
      if (
        address &&
        address.country &&
        this.sanctionsList.has(address.country.toLowerCase())
      ) {
        return { hit: true, matchType: 'COUNTRY', matchValue: address.country };
      }

      return { hit: false };
    } catch (error) {
      this.logger.error('Error performing sanctions check:', error);
      return { hit: false, error: error.message };
    }
  }

  async analyzeTransactionAmount(userId, amount, currency) {
    try {
      const flags = [];
      let suspicious = false;
      let severity = 'LOW';

      const numAmount = parseFloat(amount);

      // Check for round amounts (potential structuring)
      if (numAmount >= 1000 && numAmount % 1000 === 0) {
        flags.push('ROUND_AMOUNT');
        suspicious = true;
      }

      // Check daily transaction limits
      const dailyTotal = await this.getDailyTransactionTotal(userId, currency);
      const dailyLimit =
        this.complianceRules.dailyTransactionLimit[currency] || 10000;

      if (dailyTotal + numAmount > dailyLimit) {
        flags.push('DAILY_LIMIT_EXCEEDED');
        suspicious = true;
        severity = 'HIGH';
      }

      // Check monthly transaction limits
      const monthlyTotal = await this.getMonthlyTransactionTotal(
        userId,
        currency
      );
      const monthlyLimit =
        this.complianceRules.monthlyTransactionLimit[currency] || 50000;

      if (monthlyTotal + numAmount > monthlyLimit) {
        flags.push('MONTHLY_LIMIT_EXCEEDED');
        suspicious = true;
        severity = 'HIGH';
      }

      // Check for unusually large amounts for this user
      const userAverage = await this.getUserAverageTransactionAmount(
        userId,
        currency
      );
      if (userAverage > 0 && numAmount > userAverage * 5) {
        flags.push('UNUSUAL_AMOUNT');
        suspicious = true;
        severity = 'MEDIUM';
      }

      return { suspicious, flags, severity };
    } catch (error) {
      this.logger.error('Error analyzing transaction amount:', error);
      return {
        suspicious: true,
        flags: ['AMOUNT_ANALYSIS_ERROR'],
        severity: 'HIGH',
      };
    }
  }

  async analyzeTransactionPatterns(userId) {
    try {
      const flags = [];
      let suspicious = false;
      let severity = 'LOW';

      // Check for rapid transactions (velocity)
      const recentTransactions = await this.getRecentTransactions(userId, 1); // Last 1 hour
      if (
        recentTransactions.length >=
        this.complianceRules.suspiciousActivityThresholds.rapidTransactions
      ) {
        flags.push('RAPID_TRANSACTIONS');
        suspicious = true;
        severity = 'MEDIUM';
      }

      // Check for unusual transaction times
      const currentHour = new Date().getHours();
      if (currentHour >= 2 && currentHour <= 5) {
        // 2 AM - 5 AM
        const nightTransactions = await this.getNightTransactions(userId);
        if (nightTransactions.length > 3) {
          flags.push('UNUSUAL_TIMING');
          suspicious = true;
        }
      }

      // Check for transaction velocity changes
      const velocityChange = await this.calculateVelocityChange(userId);
      if (
        velocityChange >
        this.complianceRules.suspiciousActivityThresholds.velocityThreshold
      ) {
        flags.push('VELOCITY_INCREASE');
        suspicious = true;
        severity = 'MEDIUM';
      }

      return { suspicious, flags, severity };
    } catch (error) {
      this.logger.error('Error analyzing transaction patterns:', error);
      return {
        suspicious: true,
        flags: ['PATTERN_ANALYSIS_ERROR'],
        severity: 'HIGH',
      };
    }
  }

  async assessGeographicRisk(userInfo) {
    try {
      const flags = [];
      let highRisk = false;
      let severity = 'LOW';

      if (userInfo.country && this.highRiskCountries.has(userInfo.country)) {
        flags.push('HIGH_RISK_COUNTRY');
        highRisk = true;
        severity = 'HIGH';
      }

      // Check for VPN/proxy usage (mock implementation)
      if (userInfo.ipAddress && this.isVPNIP(userInfo.ipAddress)) {
        flags.push('VPN_USAGE');
        highRisk = true;
        severity = 'MEDIUM';
      }

      return { highRisk, flags, severity };
    } catch (error) {
      this.logger.error('Error assessing geographic risk:', error);
      return { highRisk: true, flags: ['GEO_RISK_ERROR'], severity: 'HIGH' };
    }
  }

  async checkKYCRequirements(userId, amount, currency) {
    try {
      // Mock KYC level retrieval - in production, get from user service
      const userKYCLevel = 'BASIC'; // Mock value

      const requirements = this.complianceRules.kycRequirements[userKYCLevel];
      if (!requirements) {
        return { sufficient: false, reason: 'UNKNOWN_KYC_LEVEL' };
      }

      const numAmount = parseFloat(amount);

      if (numAmount > requirements.maxAmount) {
        return { sufficient: false, reason: 'AMOUNT_EXCEEDS_KYC_LIMIT' };
      }

      const dailyTotal = await this.getDailyTransactionTotal(userId, currency);
      if (dailyTotal + numAmount > requirements.maxDaily) {
        return { sufficient: false, reason: 'DAILY_LIMIT_EXCEEDS_KYC' };
      }

      return { sufficient: true };
    } catch (error) {
      this.logger.error('Error checking KYC requirements:', error);
      return { sufficient: false, reason: 'KYC_CHECK_ERROR' };
    }
  }

  calculateAMLRiskScore(flags) {
    const flagScores = {
      SANCTIONS_HIT: 100,
      DAILY_LIMIT_EXCEEDED: 80,
      MONTHLY_LIMIT_EXCEEDED: 80,
      HIGH_RISK_COUNTRY: 60,
      RAPID_TRANSACTIONS: 40,
      UNUSUAL_AMOUNT: 30,
      ROUND_AMOUNT: 20,
      VPN_USAGE: 25,
      UNUSUAL_TIMING: 15,
      VELOCITY_INCREASE: 35,
      INSUFFICIENT_KYC: 50,
    };

    let totalScore = 0;
    flags.forEach((flag) => {
      totalScore += flagScores[flag] || 10;
    });

    return Math.min(100, totalScore);
  }

  async logSuspiciousActivity(userId, transactionData, amlResult) {
    try {
      const suspiciousActivity = {
        userId,
        transactionData,
        amlResult,
        timestamp: new Date(),
        status: 'REPORTED',
      };

      // In production, save to suspicious activity database
      this.logger.warn('Suspicious activity detected:', suspiciousActivity);

      this.emit('suspiciousActivity', suspiciousActivity);
    } catch (error) {
      this.logger.error('Error logging suspicious activity:', error);
    }
  }

  async performComplianceCheck() {
    try {
      this.logger.info('Performing periodic compliance check...');

      // Check for transactions requiring review
      const reviewRequired = await Payment.find({
        'compliance.amlStatus': 'REVIEW_REQUIRED',
        createdAt: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) },
      });

      this.logger.info(
        `Found ${reviewRequired.length} transactions requiring review`
      );

      // Check for expired pending transactions
      const expiredTransactions = await Payment.find({
        status: 'PENDING',
        expiresAt: { $lt: new Date() },
      });

      for (const transaction of expiredTransactions) {
        transaction.updateStatus('EXPIRED', 'SYSTEM', {
          reason: 'Transaction expired',
        });
        await transaction.save();
      }

      this.logger.info(
        `Expired ${expiredTransactions.length} pending transactions`
      );

      this.emit('complianceCheckCompleted', {
        reviewRequired: reviewRequired.length,
        expiredTransactions: expiredTransactions.length,
      });
    } catch (error) {
      this.logger.error('Error performing compliance check:', error);
    }
  }

  // Helper methods (mock implementations)
  async getDailyTransactionTotal(userId, currency) {
    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);

    const result = await Payment.aggregate([
      {
        $match: {
          userId,
          currency,
          status: { $in: ['COMPLETED', 'PROCESSING'] },
          createdAt: { $gte: startOfDay },
        },
      },
      {
        $group: {
          _id: null,
          total: { $sum: { $toDouble: '$amount' } },
        },
      },
    ]);

    return result.length > 0 ? result[0].total : 0;
  }

  async getMonthlyTransactionTotal(userId, currency) {
    const startOfMonth = new Date();
    startOfMonth.setDate(1);
    startOfMonth.setHours(0, 0, 0, 0);

    const result = await Payment.aggregate([
      {
        $match: {
          userId,
          currency,
          status: { $in: ['COMPLETED', 'PROCESSING'] },
          createdAt: { $gte: startOfMonth },
        },
      },
      {
        $group: {
          _id: null,
          total: { $sum: { $toDouble: '$amount' } },
        },
      },
    ]);

    return result.length > 0 ? result[0].total : 0;
  }

  async getUserAverageTransactionAmount(userId, currency) {
    const result = await Payment.aggregate([
      {
        $match: {
          userId,
          currency,
          status: 'COMPLETED',
        },
      },
      {
        $group: {
          _id: null,
          average: { $avg: { $toDouble: '$amount' } },
        },
      },
    ]);

    return result.length > 0 ? result[0].average : 0;
  }

  async getRecentTransactions(userId, hours) {
    const since = new Date(Date.now() - hours * 60 * 60 * 1000);

    return await Payment.find({
      userId,
      createdAt: { $gte: since },
    });
  }

  async getNightTransactions(userId) {
    const last30Days = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

    return await Payment.find({
      userId,
      createdAt: { $gte: last30Days },
      $expr: {
        $and: [
          { $gte: [{ $hour: '$createdAt' }, 2] },
          { $lte: [{ $hour: '$createdAt' }, 5] },
        ],
      },
    });
  }

  async calculateVelocityChange(userId) {
    // Mock implementation - calculate transaction velocity change
    return Math.random() * 0.5; // Random value between 0 and 0.5
  }

  isVPNIP(ipAddress) {
    // Mock implementation - in production, use actual VPN detection service
    return ipAddress.startsWith('10.') || ipAddress.startsWith('192.168.');
  }

  getHealthStatus() {
    return {
      isRunning: this.isRunning,
      sanctionsListSize: this.sanctionsList.size,
      highRiskCountries: this.highRiskCountries.size,
      uptime: process.uptime(),
    };
  }

  shutdown() {
    this.logger.info('Shutting down Compliance Service...');
    this.isRunning = false;
    this.emit('shutdown');
  }
}

module.exports = new ComplianceService();
