const express = require('express');
const router = express.Router();
const AlphaToken = require('../models/AlphaToken');
const authMiddleware = require('../middleware/auth');
const RiskAssessmentService = require('../services/RiskAssessmentService');

// Get risk assessment for a specific token
router.get('/tokens/:tokenId', async (req, res) => {
  try {
    const { tokenId } = req.params;

    const token = await AlphaToken.findOne({ tokenId });
    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Token not found',
      });
    }

    // Return existing risk assessment or generate new one
    let riskAssessment;
    if (token.riskScore && token.riskFactors && token.riskFactors.length > 0) {
      riskAssessment = {
        overallScore: token.riskScore,
        riskLevel: RiskAssessmentService.determineRiskLevel(token.riskScore),
        factors: token.riskFactors,
        lastAssessed: token.updatedAt,
      };
    } else {
      riskAssessment = await RiskAssessmentService.assessTokenRisk(token);
    }

    res.json({
      success: true,
      data: riskAssessment,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching risk assessment',
      error: error.message,
    });
  }
});

// Generate new risk assessment for a token (Admin only)
router.post('/tokens/:tokenId/assess', authMiddleware, async (req, res) => {
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
      message: 'Risk assessment completed successfully',
      data: riskAssessment,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error generating risk assessment',
      error: error.message,
    });
  }
});

// Get risk distribution across all tokens
router.get('/distribution', async (req, res) => {
  try {
    const distribution = await AlphaToken.aggregate([
      { $match: { status: { $in: ['active', 'completed'] } } },
      {
        $bucket: {
          groupBy: '$riskScore',
          boundaries: [0, 25, 50, 75, 100],
          default: 'Unknown',
          output: {
            count: { $sum: 1 },
            tokens: {
              $push: {
                tokenId: '$tokenId',
                name: '$name',
                riskScore: '$riskScore',
              },
            },
          },
        },
      },
    ]);

    const riskLevels = distribution.map((bucket) => {
      let level;
      if (bucket._id === 'Unknown') {
        level = 'Unknown';
      } else if (bucket._id >= 75) {
        level = 'Low Risk';
      } else if (bucket._id >= 50) {
        level = 'Medium Risk';
      } else if (bucket._id >= 25) {
        level = 'High Risk';
      } else {
        level = 'Very High Risk';
      }

      return {
        riskLevel: level,
        scoreRange:
          bucket._id === 'Unknown' ? 'N/A' : `${bucket._id}-${bucket._id + 24}`,
        count: bucket.count,
        tokens: bucket.tokens,
      };
    });

    res.json({
      success: true,
      data: {
        distribution: riskLevels,
        totalTokens: riskLevels.reduce((sum, level) => sum + level.count, 0),
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching risk distribution',
      error: error.message,
    });
  }
});

// Get risk factors analysis
router.get('/factors', async (req, res) => {
  try {
    const { limit = 10 } = req.query;

    const factorAnalysis = await AlphaToken.aggregate([
      { $match: { riskFactors: { $exists: true, $ne: [] } } },
      { $unwind: '$riskFactors' },
      {
        $group: {
          _id: '$riskFactors.factor',
          count: { $sum: 1 },
          averageScore: { $avg: '$riskFactors.score' },
          tokens: { $addToSet: { tokenId: '$tokenId', name: '$name' } },
        },
      },
      { $sort: { count: -1 } },
      { $limit: parseInt(limit) },
    ]);

    res.json({
      success: true,
      data: factorAnalysis,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching risk factors analysis',
      error: error.message,
    });
  }
});

// Get risk trends over time
router.get('/trends', async (req, res) => {
  try {
    const { days = 30 } = req.query;
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

    const trends = await AlphaToken.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate },
          riskScore: { $exists: true },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: {
              format: '%Y-%m-%d',
              date: '$createdAt',
            },
          },
          averageRiskScore: { $avg: '$riskScore' },
          tokenCount: { $sum: 1 },
          lowRiskCount: {
            $sum: { $cond: [{ $gte: ['$riskScore', 75] }, 1, 0] },
          },
          mediumRiskCount: {
            $sum: {
              $cond: [
                {
                  $and: [
                    { $gte: ['$riskScore', 50] },
                    { $lt: ['$riskScore', 75] },
                  ],
                },
                1,
                0,
              ],
            },
          },
          highRiskCount: {
            $sum: { $cond: [{ $lt: ['$riskScore', 50] }, 1, 0] },
          },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    res.json({
      success: true,
      data: {
        timeframe: `${days} days`,
        trends,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching risk trends',
      error: error.message,
    });
  }
});

// Get risk comparison between tokens
router.post('/compare', async (req, res) => {
  try {
    const { tokenIds } = req.body;

    if (
      !Array.isArray(tokenIds) ||
      tokenIds.length < 2 ||
      tokenIds.length > 5
    ) {
      return res.status(400).json({
        success: false,
        message: 'Please provide 2-5 token IDs for comparison',
      });
    }

    const tokens = await AlphaToken.find({
      tokenId: { $in: tokenIds },
    }).select(
      'tokenId name symbol riskScore riskFactors blockchain totalInvestors progressPercentage'
    );

    if (tokens.length !== tokenIds.length) {
      return res.status(404).json({
        success: false,
        message: 'One or more tokens not found',
      });
    }

    const comparison = tokens.map((token) => ({
      tokenId: token.tokenId,
      name: token.name,
      symbol: token.symbol,
      riskScore: token.riskScore,
      riskLevel: RiskAssessmentService.determineRiskLevel(token.riskScore),
      blockchain: token.blockchain,
      totalInvestors: token.totalInvestors,
      progressPercentage: token.progressPercentage,
      riskFactors: token.riskFactors || [],
    }));

    // Calculate relative risk ranking
    const sortedByRisk = [...comparison].sort(
      (a, b) => b.riskScore - a.riskScore
    );
    sortedByRisk.forEach((token, index) => {
      token.riskRanking = index + 1;
    });

    res.json({
      success: true,
      data: {
        comparison,
        summary: {
          lowestRisk: sortedByRisk[0],
          highestRisk: sortedByRisk[sortedByRisk.length - 1],
          averageRiskScore:
            comparison.reduce((sum, token) => sum + token.riskScore, 0) /
            comparison.length,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error comparing token risks',
      error: error.message,
    });
  }
});

// Get risk alerts (Admin only)
router.get('/alerts', authMiddleware, async (req, res) => {
  try {
    if (!req.user.isAdmin && !req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const { severity = 'all' } = req.query;

    // Find tokens with high risk scores or concerning factors
    const query = { status: 'active' };

    if (severity === 'high') {
      query.riskScore = { $lt: 40 };
    } else if (severity === 'medium') {
      query.riskScore = { $gte: 40, $lt: 60 };
    }

    const riskAlerts = await AlphaToken.find(query)
      .select(
        'tokenId name symbol riskScore riskFactors totalInvestors progressPercentage'
      )
      .sort({ riskScore: 1 });

    const alerts = riskAlerts.map((token) => {
      const criticalFactors =
        token.riskFactors?.filter((factor) => factor.score < 50) || [];

      return {
        tokenId: token.tokenId,
        name: token.name,
        symbol: token.symbol,
        riskScore: token.riskScore,
        riskLevel: RiskAssessmentService.determineRiskLevel(token.riskScore),
        totalInvestors: token.totalInvestors,
        progressPercentage: token.progressPercentage,
        criticalFactors,
        alertLevel:
          token.riskScore < 30
            ? 'critical'
            : token.riskScore < 50
              ? 'high'
              : 'medium',
      };
    });

    res.json({
      success: true,
      data: {
        alerts,
        summary: {
          total: alerts.length,
          critical: alerts.filter((alert) => alert.alertLevel === 'critical')
            .length,
          high: alerts.filter((alert) => alert.alertLevel === 'high').length,
          medium: alerts.filter((alert) => alert.alertLevel === 'medium')
            .length,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching risk alerts',
      error: error.message,
    });
  }
});

// Update risk assessment settings (Super Admin only)
router.put('/settings', authMiddleware, async (req, res) => {
  try {
    if (!req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Super admin privileges required',
      });
    }

    const { riskFactorWeights, alertThresholds } = req.body;

    // Update risk factor weights
    if (riskFactorWeights) {
      RiskAssessmentService.riskFactors = {
        ...RiskAssessmentService.riskFactors,
        ...riskFactorWeights,
      };
    }

    // Update alert thresholds
    if (alertThresholds) {
      RiskAssessmentService.alertThresholds = {
        ...RiskAssessmentService.alertThresholds,
        ...alertThresholds,
      };
    }

    res.json({
      success: true,
      message: 'Risk assessment settings updated successfully',
      data: {
        riskFactorWeights: RiskAssessmentService.riskFactors,
        alertThresholds: RiskAssessmentService.alertThresholds,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error updating risk assessment settings',
      error: error.message,
    });
  }
});

module.exports = router;
