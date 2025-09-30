const express = require('express');
const router = express.Router();
const AlphaToken = require('../models/AlphaToken');
const authMiddleware = require('../middleware/auth');
const { validateTokenStatus } = require('../middleware/validation');
const RiskAssessmentService = require('../services/RiskAssessmentService');

// Get token by ID (public endpoint)
router.get('/:tokenId', async (req, res) => {
  try {
    const { tokenId } = req.params;

    const token = await AlphaToken.findOne({ tokenId })
      .populate('createdBy', 'username email')
      .populate('approvedBy', 'username email');

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    // Only show approved/active tokens to public
    if (!['approved', 'active', 'completed'].includes(token.status)) {
      return res.status(404).json({
        success: false,
        message: 'Token not available',
      });
    }

    res.json({
      success: true,
      data: token,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching token',
      error: error.message,
    });
  }
});

// Get token metrics
router.get('/:tokenId/metrics', async (req, res) => {
  try {
    const { tokenId } = req.params;

    const token = await AlphaToken.findOne({ tokenId });
    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    const AlphaMarketService = require('../services/AlphaMarketService');
    const metrics = await AlphaMarketService.calculateTokenMetrics(tokenId);

    res.json({
      success: true,
      data: metrics,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching token metrics',
      error: error.message,
    });
  }
});

// Update token status (Admin only)
router.put(
  '/:tokenId/status',
  authMiddleware,
  validateTokenStatus,
  async (req, res) => {
    try {
      const { tokenId } = req.params;
      const { status, reason } = req.body;

      // Check admin privileges
      if (!req.user.isAdmin && !req.user.isSuperAdmin) {
        return res.status(403).json({
          success: false,
          message: 'Admin privileges required',
        });
      }

      const token = await AlphaToken.findOne({ tokenId });
      if (!token) {
        return res.status(404).json({
          success: false,
          message: 'Token not found',
        });
      }

      // Validate status transitions
      const validTransitions = {
        pending: ['approved', 'rejected'],
        approved: ['active', 'cancelled'],
        active: ['completed', 'cancelled'],
        completed: ['archived'],
        rejected: ['pending'],
        cancelled: ['pending'],
      };

      if (!validTransitions[token.status]?.includes(status)) {
        return res.status(400).json({
          success: false,
          message: `Invalid status transition from ${token.status} to ${status}`,
        });
      }

      // Update token status
      token.status = status;
      if (status === 'approved') {
        token.approvedBy = req.user.id;
        token.approvedAt = new Date();
      }

      // Add status change to history
      if (!token.statusHistory) {
        token.statusHistory = [];
      }
      token.statusHistory.push({
        status,
        changedBy: req.user.id,
        changedAt: new Date(),
        reason,
      });

      await token.save();

      // Emit real-time update
      const io = req.app.get('io');
      io.emit('token_status_changed', {
        tokenId,
        status,
        changedBy: req.user.username,
      });

      res.json({
        success: true,
        message: `Token status updated to ${status}`,
        data: token,
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Error updating token status',
        error: error.message,
      });
    }
  }
);

// Get token status history (Admin only)
router.get('/:tokenId/status-history', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;

    if (!req.user.isAdmin && !req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const token = await AlphaToken.findOne({ tokenId }).populate(
      'statusHistory.changedBy',
      'username email'
    );

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    res.json({
      success: true,
      data: {
        tokenId,
        currentStatus: token.status,
        statusHistory: token.statusHistory || [],
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching status history',
      error: error.message,
    });
  }
});

// Get token analytics
router.get('/:tokenId/analytics', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;
    const { timeframe = '7d' } = req.query;

    const token = await AlphaToken.findOne({ tokenId });
    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    // Check if user has access to analytics
    const hasAccess =
      req.user.isAdmin ||
      req.user.isSuperAdmin ||
      token.createdBy.toString() === req.user.id;

    if (!hasAccess) {
      return res.status(403).json({
        success: false,
        message: 'Access denied to token analytics',
      });
    }

    const AlphaInvestment = require('../models/AlphaInvestment');

    // Calculate timeframe
    const timeframes = {
      '1d': 1,
      '7d': 7,
      '30d': 30,
      '90d': 90,
    };

    const days = timeframes[timeframe] || 7;
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

    // Get investment analytics
    const analytics = await AlphaInvestment.aggregate([
      {
        $match: {
          tokenId,
          investedAt: { $gte: startDate },
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
          totalAmount: { $sum: '$investmentAmount' },
          uniqueInvestors: { $addToSet: '$userId' },
        },
      },
      {
        $project: {
          date: '$_id',
          investments: 1,
          totalAmount: 1,
          uniqueInvestors: { $size: '$uniqueInvestors' },
        },
      },
      { $sort: { date: 1 } },
    ]);

    // Get tier distribution
    const tierDistribution = await AlphaInvestment.aggregate([
      { $match: { tokenId, status: 'confirmed' } },
      {
        $group: {
          _id: '$userTier',
          count: { $sum: 1 },
          totalAmount: { $sum: '$investmentAmount' },
        },
      },
    ]);

    res.json({
      success: true,
      data: {
        timeframe,
        dailyAnalytics: analytics,
        tierDistribution,
        summary: {
          totalInvestments: analytics.reduce(
            (sum, day) => sum + day.investments,
            0
          ),
          totalAmount: analytics.reduce((sum, day) => sum + day.totalAmount, 0),
          uniqueInvestors: [
            ...new Set(analytics.flatMap((day) => day.uniqueInvestors)),
          ].length,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching token analytics',
      error: error.message,
    });
  }
});

// Refresh token risk assessment (Admin only)
router.post('/:tokenId/refresh-risk', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;

    if (!req.user.isAdmin && !req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const riskAssessment =
      await RiskAssessmentService.updateTokenRiskScore(tokenId);

    res.json({
      success: true,
      message: 'Risk assessment updated successfully',
      data: riskAssessment,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error refreshing risk assessment',
      error: error.message,
    });
  }
});

// Get similar tokens (recommendation engine)
router.get('/:tokenId/similar', async (req, res) => {
  try {
    const { tokenId } = req.params;
    const { limit = 5 } = req.query;

    const token = await AlphaToken.findOne({ tokenId });
    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    // Find similar tokens based on blockchain, risk score, and category
    const similarTokens = await AlphaToken.find({
      tokenId: { $ne: tokenId },
      status: 'active',
      blockchain: token.blockchain,
      riskScore: {
        $gte: token.riskScore - 20,
        $lte: token.riskScore + 20,
      },
    })
      .sort({ totalInvestors: -1, progressPercentage: -1 })
      .limit(parseInt(limit))
      .select(
        'tokenId name symbol blockchain riskScore progressPercentage totalInvestors alphaPrice'
      );

    res.json({
      success: true,
      data: similarTokens,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching similar tokens',
      error: error.message,
    });
  }
});

// Export token data (Admin only)
router.get('/:tokenId/export', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;
    const { format = 'json' } = req.query;

    if (!req.user.isAdmin && !req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const token = await AlphaToken.findOne({ tokenId })
      .populate('createdBy', 'username email')
      .populate('approvedBy', 'username email');

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    const AlphaInvestment = require('../models/AlphaInvestment');
    const investments = await AlphaInvestment.find({ tokenId }).populate(
      'userId',
      'username email'
    );

    const exportData = {
      token,
      investments,
      exportedAt: new Date(),
      exportedBy: req.user.username,
    };

    if (format === 'csv') {
      // Convert to CSV format (simplified)
      const csv = this.convertToCSV(exportData);
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="${tokenId}_export.csv"`
      );
      res.send(csv);
    } else {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="${tokenId}_export.json"`
      );
      res.json(exportData);
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error exporting token data',
      error: error.message,
    });
  }
});

module.exports = router;
