const AlphaToken = require('../models/AlphaToken');
const AlphaInvestment = require('../models/AlphaInvestment');
const cron = require('cron');
const winston = require('winston');

class AlphaMarketService {
  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'alpha-market-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/alpha-market.log' }),
        new winston.transports.Console(),
      ],
    });

    this.cronJobs = [];
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      this.logger.info('Initializing Alpha Market Service...');

      // Start cron jobs
      this.startCronJobs();

      // Process any pending vesting schedules
      await this.processAllVestingSchedules();

      // Update token statuses
      await this.updateTokenStatuses();

      this.isInitialized = true;
      this.logger.info('Alpha Market Service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Alpha Market Service:', error);
      throw error;
    }
  }

  startCronJobs() {
    // Process vesting schedules every hour
    const vestingJob = new cron.CronJob('0 * * * *', async () => {
      await this.processAllVestingSchedules();
    });

    // Update token statuses every 30 minutes
    const statusJob = new cron.CronJob('*/30 * * * *', async () => {
      await this.updateTokenStatuses();
    });

    // Generate daily reports at midnight
    const reportJob = new cron.CronJob('0 0 * * *', async () => {
      await this.generateDailyReport();
    });

    // Clean up expired tokens weekly
    const cleanupJob = new cron.CronJob('0 0 * * 0', async () => {
      await this.cleanupExpiredTokens();
    });

    vestingJob.start();
    statusJob.start();
    reportJob.start();
    cleanupJob.start();

    this.cronJobs = [vestingJob, statusJob, reportJob, cleanupJob];
    this.logger.info('Cron jobs started successfully');
  }

  async processAllVestingSchedules() {
    try {
      this.logger.info('Processing vesting schedules...');

      const investments = await AlphaInvestment.find({
        status: 'confirmed',
        totalVested: { $lt: '$tokenAmount' },
      });

      let processedCount = 0;
      for (const investment of investments) {
        const wasUpdated = await investment.processVesting();
        if (wasUpdated !== investment) {
          processedCount++;
        }
      }

      this.logger.info(`Processed ${processedCount} vesting schedules`);
      return processedCount;
    } catch (error) {
      this.logger.error('Error processing vesting schedules:', error);
      throw error;
    }
  }

  async updateTokenStatuses() {
    try {
      this.logger.info('Updating token statuses...');

      const now = new Date();
      let updatedCount = 0;

      // Activate tokens that should start
      const tokensToActivate = await AlphaToken.find({
        status: 'approved',
        alphaStartDate: { $lte: now },
        alphaEndDate: { $gt: now },
      });

      for (const token of tokensToActivate) {
        token.status = 'active';
        await token.save();
        updatedCount++;
        this.logger.info(`Activated token: ${token.tokenId}`);
      }

      // Complete tokens that have ended
      const tokensToComplete = await AlphaToken.find({
        status: 'active',
        alphaEndDate: { $lte: now },
      });

      for (const token of tokensToComplete) {
        token.status = 'completed';
        await token.save();
        updatedCount++;
        this.logger.info(`Completed token: ${token.tokenId}`);
      }

      this.logger.info(`Updated ${updatedCount} token statuses`);
      return updatedCount;
    } catch (error) {
      this.logger.error('Error updating token statuses:', error);
      throw error;
    }
  }

  async generateDailyReport() {
    try {
      this.logger.info('Generating daily report...');

      const today = new Date();
      const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);

      // Get daily statistics
      const dailyStats = await this.getDailyStatistics(yesterday, today);

      // Get top performing tokens
      const topTokens = await this.getTopPerformingTokens(5);

      // Get investment trends
      const investmentTrends = await this.getInvestmentTrends(7);

      const report = {
        date: yesterday.toISOString().split('T')[0],
        statistics: dailyStats,
        topTokens,
        investmentTrends,
        generatedAt: new Date(),
      };

      // Store report (you might want to save this to database or send via email)
      this.logger.info('Daily report generated:', report);

      return report;
    } catch (error) {
      this.logger.error('Error generating daily report:', error);
      throw error;
    }
  }

  async getDailyStatistics(startDate, endDate) {
    const [tokenStats, investmentStats] = await Promise.all([
      AlphaToken.aggregate([
        {
          $match: {
            createdAt: { $gte: startDate, $lt: endDate },
          },
        },
        {
          $group: {
            _id: null,
            newTokens: { $sum: 1 },
            totalAllocation: { $sum: '$alphaAllocation' },
            averageRiskScore: { $avg: '$riskScore' },
          },
        },
      ]),
      AlphaInvestment.aggregate([
        {
          $match: {
            investedAt: { $gte: startDate, $lt: endDate },
          },
        },
        {
          $group: {
            _id: null,
            newInvestments: { $sum: 1 },
            totalInvested: { $sum: '$investmentAmount' },
            uniqueInvestors: { $addToSet: '$userId' },
            averageInvestment: { $avg: '$investmentAmount' },
          },
        },
      ]),
    ]);

    return {
      tokens: tokenStats[0] || {
        newTokens: 0,
        totalAllocation: 0,
        averageRiskScore: 0,
      },
      investments: investmentStats[0]
        ? {
            ...investmentStats[0],
            uniqueInvestors: investmentStats[0].uniqueInvestors.length,
          }
        : {
            newInvestments: 0,
            totalInvested: 0,
            uniqueInvestors: 0,
            averageInvestment: 0,
          },
    };
  }

  async getTopPerformingTokens(limit = 10) {
    return await AlphaToken.aggregate([
      { $match: { status: { $in: ['active', 'completed'] } } },
      {
        $addFields: {
          performanceScore: {
            $add: [
              { $multiply: ['$progressPercentage', 0.4] },
              { $multiply: ['$totalInvestors', 0.3] },
              { $multiply: [{ $subtract: [100, '$riskScore'] }, 0.2] },
              { $multiply: ['$averageInvestment', 0.1] },
            ],
          },
        },
      },
      { $sort: { performanceScore: -1 } },
      { $limit: limit },
      {
        $project: {
          tokenId: 1,
          name: 1,
          symbol: 1,
          progressPercentage: 1,
          totalInvestors: 1,
          riskScore: 1,
          performanceScore: 1,
        },
      },
    ]);
  }

  async getInvestmentTrends(days = 7) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - days * 24 * 60 * 60 * 1000);

    return await AlphaInvestment.aggregate([
      {
        $match: {
          investedAt: { $gte: startDate, $lte: endDate },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: {
              format: '%Y-%m-%d',
              date: '$investedAt',
            },
          },
          totalInvestments: { $sum: 1 },
          totalAmount: { $sum: '$investmentAmount' },
          uniqueInvestors: { $addToSet: '$userId' },
        },
      },
      {
        $project: {
          date: '$_id',
          totalInvestments: 1,
          totalAmount: 1,
          uniqueInvestors: { $size: '$uniqueInvestors' },
        },
      },
      { $sort: { date: 1 } },
    ]);
  }

  async cleanupExpiredTokens() {
    try {
      this.logger.info('Cleaning up expired tokens...');

      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

      // Archive completed tokens older than 30 days
      const expiredTokens = await AlphaToken.find({
        status: 'completed',
        alphaEndDate: { $lt: thirtyDaysAgo },
      });

      let archivedCount = 0;
      for (const token of expiredTokens) {
        // You might want to move these to an archive collection
        // For now, we'll just update their status
        token.status = 'archived';
        await token.save();
        archivedCount++;
      }

      this.logger.info(`Archived ${archivedCount} expired tokens`);
      return archivedCount;
    } catch (error) {
      this.logger.error('Error cleaning up expired tokens:', error);
      throw error;
    }
  }

  async calculateTokenMetrics(tokenId) {
    try {
      const token = await AlphaToken.findOne({ tokenId });
      if (!token) {
        throw new Error('Token not found');
      }

      const investments = await AlphaInvestment.find({
        tokenId,
        status: 'confirmed',
      });

      const metrics = {
        totalRaised: investments.reduce(
          (sum, inv) => sum + inv.investmentAmount,
          0
        ),
        totalInvestors: investments.length,
        averageInvestment:
          investments.length > 0
            ? investments.reduce((sum, inv) => sum + inv.investmentAmount, 0) /
              investments.length
            : 0,
        progressPercentage: (token.soldAmount / token.alphaAllocation) * 100,
        timeRemaining: Math.max(0, token.alphaEndDate.getTime() - Date.now()),
        investorTierDistribution: this.calculateTierDistribution(investments),
        dailyInvestmentTrend: await this.getDailyInvestmentTrend(tokenId, 7),
      };

      return metrics;
    } catch (error) {
      this.logger.error(
        `Error calculating metrics for token ${tokenId}:`,
        error
      );
      throw error;
    }
  }

  calculateTierDistribution(investments) {
    const distribution = { bronze: 0, silver: 0, gold: 0, platinum: 0 };

    investments.forEach((investment) => {
      if (distribution.hasOwnProperty(investment.userTier)) {
        distribution[investment.userTier]++;
      }
    });

    return distribution;
  }

  async getDailyInvestmentTrend(tokenId, days = 7) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - days * 24 * 60 * 60 * 1000);

    return await AlphaInvestment.aggregate([
      {
        $match: {
          tokenId,
          investedAt: { $gte: startDate, $lte: endDate },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: {
              format: '%Y-%m-%d',
              date: '$investedAt',
            },
          },
          investments: { $sum: 1 },
          amount: { $sum: '$investmentAmount' },
        },
      },
      { $sort: { _id: 1 } },
    ]);
  }

  async validateInvestment(tokenId, userId, amount, userTier) {
    try {
      const token = await AlphaToken.findOne({ tokenId });
      if (!token) {
        return { valid: false, reason: 'Token not found' };
      }

      if (!token.isAlphaActive()) {
        return { valid: false, reason: 'Alpha period is not active' };
      }

      if (!token.canInvest(amount, userTier)) {
        return {
          valid: false,
          reason: 'Investment not allowed for current tier or amount',
        };
      }

      // Check if user has already invested (if there's a limit)
      const existingInvestment = await AlphaInvestment.findOne({
        tokenId,
        userId,
        status: { $in: ['pending', 'confirmed'] },
      });

      if (existingInvestment && token.maxInvestmentPerUser) {
        const totalInvested = existingInvestment.investmentAmount + amount;
        if (totalInvested > token.maxInvestmentPerUser) {
          return {
            valid: false,
            reason: `Maximum investment per user exceeded. Current: ${existingInvestment.investmentAmount}, Limit: ${token.maxInvestmentPerUser}`,
          };
        }
      }

      return { valid: true };
    } catch (error) {
      this.logger.error('Error validating investment:', error);
      return { valid: false, reason: 'Validation error occurred' };
    }
  }

  async shutdown() {
    this.logger.info('Shutting down Alpha Market Service...');

    // Stop all cron jobs
    this.cronJobs.forEach((job) => job.stop());

    this.isInitialized = false;
    this.logger.info('Alpha Market Service shut down successfully');
  }
}

module.exports = new AlphaMarketService();
