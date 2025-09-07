const express = require('express');
const router = express.Router();
const AlphaToken = require('../models/AlphaToken');
const AlphaInvestment = require('../models/AlphaInvestment');
const authMiddleware = require('../middleware/auth');
const {
  validateAlphaToken,
  validateInvestment,
} = require('../middleware/validation');

// Get all active alpha tokens
router.get('/tokens', async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      blockchain,
      riskScore,
      sortBy = 'alphaStartDate',
      sortOrder = 'desc',
    } = req.query;

    const query = { status: 'active' };

    if (blockchain) query.blockchain = blockchain;
    if (riskScore) {
      const [min, max] = riskScore.split('-').map(Number);
      query.riskScore = { $gte: min, $lte: max };
    }

    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;

    const tokens = await AlphaToken.find(query)
      .sort(sort)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .populate('createdBy', 'username email')
      .populate('approvedBy', 'username email');

    const total = await AlphaToken.countDocuments(query);

    res.json({
      success: true,
      data: {
        tokens,
        pagination: {
          current: page,
          pages: Math.ceil(total / limit),
          total,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching alpha tokens',
      error: error.message,
    });
  }
});

// Get specific alpha token details
router.get('/tokens/:tokenId', async (req, res) => {
  try {
    const { tokenId } = req.params;

    const token = await AlphaToken.findOne({ tokenId })
      .populate('createdBy', 'username email')
      .populate('approvedBy', 'username email');

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Alpha token not found',
      });
    }

    // Get investment statistics
    const stats = await AlphaInvestment.getInvestmentStats(tokenId);

    res.json({
      success: true,
      data: {
        token,
        stats: stats[0] || {
          totalInvestments: 0,
          totalAmount: 0,
          totalTokens: 0,
          averageInvestment: 0,
          uniqueInvestors: 0,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching token details',
      error: error.message,
    });
  }
});

// Create new alpha token (Admin only)
router.post('/tokens', authMiddleware, validateAlphaToken, async (req, res) => {
  try {
    const tokenData = {
      ...req.body,
      createdBy: req.user.id,
      tokenId: `ALPHA_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    const token = new AlphaToken(tokenData);
    await token.save();

    res.status(201).json({
      success: true,
      message: 'Alpha token created successfully',
      data: token,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error creating alpha token',
      error: error.message,
    });
  }
});

// Update alpha token (Admin only)
router.put('/tokens/:tokenId', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;
    const updates = req.body;

    const token = await AlphaToken.findOneAndUpdate(
      { tokenId },
      { ...updates, updatedAt: new Date() },
      { new: true, runValidators: true }
    );

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Alpha token not found',
      });
    }

    // Emit real-time update
    const io = req.app.get('io');
    io.to(`alpha_${tokenId}`).emit('token_updated', token);

    res.json({
      success: true,
      message: 'Alpha token updated successfully',
      data: token,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error updating alpha token',
      error: error.message,
    });
  }
});

// Approve alpha token (Super Admin only)
router.post('/tokens/:tokenId/approve', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;

    // Check if user has admin privileges
    if (!req.user.isAdmin && !req.user.isSuperAdmin) {
      return res.status(403).json({
        success: false,
        message: 'Insufficient privileges',
      });
    }

    const token = await AlphaToken.findOneAndUpdate(
      { tokenId },
      {
        status: 'approved',
        approvedBy: req.user.id,
        approvedAt: new Date(),
      },
      { new: true }
    );

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Alpha token not found',
      });
    }

    res.json({
      success: true,
      message: 'Alpha token approved successfully',
      data: token,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error approving alpha token',
      error: error.message,
    });
  }
});

// Activate alpha token for trading
router.post('/tokens/:tokenId/activate', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;

    const token = await AlphaToken.findOne({ tokenId });

    if (!token) {
      return res.status(404).json({
        success: false,
        message: 'Alpha token not found',
      });
    }

    if (token.status !== 'approved') {
      return res.status(400).json({
        success: false,
        message: 'Token must be approved before activation',
      });
    }

    const now = new Date();
    if (now < token.alphaStartDate) {
      return res.status(400).json({
        success: false,
        message: 'Alpha period has not started yet',
      });
    }

    token.status = 'active';
    await token.save();

    // Emit real-time notification
    const io = req.app.get('io');
    io.emit('alpha_activated', { tokenId, token });

    res.json({
      success: true,
      message: 'Alpha token activated successfully',
      data: token,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error activating alpha token',
      error: error.message,
    });
  }
});

// Get alpha token investments
router.get('/tokens/:tokenId/investments', authMiddleware, async (req, res) => {
  try {
    const { tokenId } = req.params;
    const { page = 1, limit = 50, status } = req.query;

    const investments = await AlphaInvestment.getTokenInvestments(tokenId, {
      status,
      limit: parseInt(limit),
      skip: (page - 1) * limit,
    });

    res.json({
      success: true,
      data: investments,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching token investments',
      error: error.message,
    });
  }
});

// Create investment in alpha token
router.post(
  '/tokens/:tokenId/invest',
  authMiddleware,
  validateInvestment,
  async (req, res) => {
    try {
      const { tokenId } = req.params;
      const { investmentAmount, paymentMethod, referralCode } = req.body;

      const token = await AlphaToken.findOne({ tokenId });

      if (!token) {
        return res.status(404).json({
          success: false,
          message: 'Alpha token not found',
        });
      }

      // Check if user can invest
      const userTier = req.user.tier || 'bronze';
      if (!token.canInvest(investmentAmount, userTier)) {
        return res.status(400).json({
          success: false,
          message: 'Investment not allowed for current user tier or amount',
        });
      }

      // Calculate token amount
      const tokenAmount = investmentAmount / token.alphaPrice;

      // Create investment record
      const investment = new AlphaInvestment({
        investmentId: `INV_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        userId: req.user.id,
        tokenId,
        investmentAmount,
        tokenAmount,
        pricePerToken: token.alphaPrice,
        userTier,
        userStakeAmount: req.user.stakeAmount || 0,
        blockchain: token.blockchain,
        paymentMethod,
        referralCode,
        riskScore: token.riskScore,
        investmentSource: 'web',
        ipAddress: req.ip,
        userAgent: req.get('User-Agent'),
      });

      await investment.save();

      // Update token sold amount
      await token.updateSoldAmount(tokenAmount);

      // Emit real-time update
      const io = req.app.get('io');
      io.to(`alpha_${tokenId}`).emit('new_investment', {
        tokenId,
        investment: {
          amount: investmentAmount,
          tokenAmount,
          investor: req.user.username,
        },
      });

      res.status(201).json({
        success: true,
        message: 'Investment created successfully',
        data: investment,
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Error creating investment',
        error: error.message,
      });
    }
  }
);

// Get trending alpha tokens
router.get('/trending', async (req, res) => {
  try {
    const { limit = 10 } = req.query;

    const trending = await AlphaToken.aggregate([
      { $match: { status: 'active' } },
      {
        $addFields: {
          trendingScore: {
            $add: [
              { $multiply: ['$totalInvestors', 10] },
              { $multiply: ['$progressPercentage', 5] },
              { $subtract: [100, '$riskScore'] },
            ],
          },
        },
      },
      { $sort: { trendingScore: -1 } },
      { $limit: parseInt(limit) },
    ]);

    res.json({
      success: true,
      data: trending,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching trending tokens',
      error: error.message,
    });
  }
});

// Get alpha market statistics
router.get('/stats', async (req, res) => {
  try {
    const stats = await AlphaToken.aggregate([
      {
        $group: {
          _id: null,
          totalTokens: { $sum: 1 },
          activeTokens: {
            $sum: { $cond: [{ $eq: ['$status', 'active'] }, 1, 0] },
          },
          totalRaised: { $sum: { $multiply: ['$soldAmount', '$alphaPrice'] } },
          totalInvestors: { $sum: '$totalInvestors' },
          averageRiskScore: { $avg: '$riskScore' },
        },
      },
    ]);

    const blockchainStats = await AlphaToken.aggregate([
      { $match: { status: 'active' } },
      {
        $group: {
          _id: '$blockchain',
          count: { $sum: 1 },
          totalRaised: { $sum: { $multiply: ['$soldAmount', '$alphaPrice'] } },
        },
      },
      { $sort: { count: -1 } },
    ]);

    res.json({
      success: true,
      data: {
        overview: stats[0] || {
          totalTokens: 0,
          activeTokens: 0,
          totalRaised: 0,
          totalInvestors: 0,
          averageRiskScore: 0,
        },
        blockchainDistribution: blockchainStats,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching alpha market statistics',
      error: error.message,
    });
  }
});

module.exports = router;
