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
const router = express.Router();
const AlphaInvestment = require('../models/AlphaInvestment');
const authMiddleware = require('../middleware/auth');

// Get user's alpha investments
router.get('/investments', authMiddleware, async (req, res) => {
  try {
    const { page = 1, limit = 20, status, tokenId } = req.query;

    const investments = await AlphaInvestment.getUserInvestments(req.user.id, {
      status,
      tokenId,
      limit: parseInt(limit),
      skip: (page - 1) * limit,
    });

    const total = await AlphaInvestment.countDocuments({
      userId: req.user.id,
      ...(status && { status }),
      ...(tokenId && { tokenId }),
    });

    res.json({
      success: true,
      data: {
        investments,
        pagination: {
          current: parseInt(page),
          pages: Math.ceil(total / limit),
          total,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching user investments',
      error: error.message,
    });
  }
});

// Get specific investment details
router.get('/investments/:investmentId', authMiddleware, async (req, res) => {
  try {
    const { investmentId } = req.params;

    const investment = await AlphaInvestment.findOne({
      investmentId,
      userId: req.user.id,
    }).populate('tokenId');

    if (!investment) {
      return res.status(404).json({
        success: false,
        message: 'Investment not found',
      });
    }

    res.json({
      success: true,
      data: investment,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching investment details',
      error: error.message,
    });
  }
});

// Get user's investment portfolio summary
router.get('/portfolio', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;

    const portfolio = await AlphaInvestment.aggregate([
      { $match: { userId: mongoose.Types.ObjectId(userId) } },
      {
        $group: {
          _id: null,
          totalInvestments: { $sum: 1 },
          totalInvested: { $sum: '$investmentAmount' },
          totalTokens: { $sum: '$tokenAmount' },
          totalVested: { $sum: '$totalVested' },
          totalClaimed: { $sum: '$totalClaimed' },
          pendingInvestments: {
            $sum: { $cond: [{ $eq: ['$status', 'pending'] }, 1, 0] },
          },
          confirmedInvestments: {
            $sum: { $cond: [{ $eq: ['$status', 'confirmed'] }, 1, 0] },
          },
        },
      },
    ]);

    const tokenDistribution = await AlphaInvestment.aggregate([
      {
        $match: {
          userId: mongoose.Types.ObjectId(userId),
          status: 'confirmed',
        },
      },
      {
        $group: {
          _id: '$tokenId',
          totalInvested: { $sum: '$investmentAmount' },
          totalTokens: { $sum: '$tokenAmount' },
          investments: { $sum: 1 },
        },
      },
      {
        $lookup: {
          from: 'alphatokens',
          localField: '_id',
          foreignField: 'tokenId',
          as: 'tokenInfo',
        },
      },
      { $sort: { totalInvested: -1 } },
    ]);

    const claimableTokens = await AlphaInvestment.find({
      userId,
      status: 'confirmed',
    }).then((investments) => {
      return investments.reduce((total, investment) => {
        return total + investment.getClaimableAmount();
      }, 0);
    });

    res.json({
      success: true,
      data: {
        summary: portfolio[0] || {
          totalInvestments: 0,
          totalInvested: 0,
          totalTokens: 0,
          totalVested: 0,
          totalClaimed: 0,
          pendingInvestments: 0,
          confirmedInvestments: 0,
        },
        tokenDistribution,
        claimableTokens,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching portfolio summary',
      error: error.message,
    });
  }
});

// Claim vested tokens
router.post(
  '/investments/:investmentId/claim',
  authMiddleware,
  async (req, res) => {
    try {
      const { investmentId } = req.params;
      const { amount, transactionHash } = req.body;

      if (!amount || !transactionHash) {
        return res.status(400).json({
          success: false,
          message: 'Amount and transaction hash are required',
        });
      }

      const investment = await AlphaInvestment.findOne({
        investmentId,
        userId: req.user.id,
      });

      if (!investment) {
        return res.status(404).json({
          success: false,
          message: 'Investment not found',
        });
      }

      if (!investment.canClaim()) {
        return res.status(400).json({
          success: false,
          message: 'No tokens available for claiming',
        });
      }

      const claimableAmount = investment.getClaimableAmount();
      if (amount > claimableAmount) {
        return res.status(400).json({
          success: false,
          message: `Only ${claimableAmount} tokens are available for claiming`,
        });
      }

      await investment.claimTokens(amount, transactionHash);

      // Emit real-time update
      const io = req.app.get('io');
      io.to(`user_${req.user.id}`).emit('tokens_claimed', {
        investmentId,
        amount,
        transactionHash,
      });

      res.json({
        success: true,
        message: 'Tokens claimed successfully',
        data: {
          claimedAmount: amount,
          remainingClaimable: investment.getClaimableAmount() - amount,
          transactionHash,
        },
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Error claiming tokens',
        error: error.message,
      });
    }
  }
);

// Get vesting schedule for investment
router.get(
  '/investments/:investmentId/vesting',
  authMiddleware,
  async (req, res) => {
    try {
      const { investmentId } = req.params;

      const investment = await AlphaInvestment.findOne({
        investmentId,
        userId: req.user.id,
      }).populate('tokenId');

      if (!investment) {
        return res.status(404).json({
          success: false,
          message: 'Investment not found',
        });
      }

      // Process any pending vesting
      await investment.processVesting();

      const vestingSchedule = investment.vestingSchedule.map((vest) => ({
        releaseDate: vest.releaseDate,
        percentage: vest.percentage,
        tokenAmount: vest.tokenAmount,
        status: vest.status,
        claimedAt: vest.claimedAt,
        transactionHash: vest.transactionHash,
      }));

      res.json({
        success: true,
        data: {
          investmentId,
          totalTokens: investment.tokenAmount,
          totalVested: investment.totalVested,
          totalClaimed: investment.totalClaimed,
          claimableAmount: investment.getClaimableAmount(),
          vestingSchedule,
        },
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Error fetching vesting schedule',
        error: error.message,
      });
    }
  }
);

// Update investment status (for blockchain confirmations)
router.put(
  '/investments/:investmentId/status',
  authMiddleware,
  async (req, res) => {
    try {
      const { investmentId } = req.params;
      const { status, confirmationBlocks, transactionHash } = req.body;

      const investment = await AlphaInvestment.findOne({
        investmentId,
        userId: req.user.id,
      });

      if (!investment) {
        return res.status(404).json({
          success: false,
          message: 'Investment not found',
        });
      }

      const updates = {};
      if (status) updates.status = status;
      if (confirmationBlocks !== undefined)
        updates.confirmationBlocks = confirmationBlocks;
      if (transactionHash) updates.transactionHash = transactionHash;

      if (status === 'confirmed' && !investment.confirmedAt) {
        updates.confirmedAt = new Date();
      }

      Object.assign(investment, updates);
      await investment.save();

      // Emit real-time update
      const io = req.app.get('io');
      io.to(`user_${req.user.id}`).emit('investment_updated', {
        investmentId,
        status: investment.status,
        confirmationBlocks: investment.confirmationBlocks,
      });

      res.json({
        success: true,
        message: 'Investment status updated successfully',
        data: investment,
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: 'Error updating investment status',
        error: error.message,
      });
    }
  }
);

// Get user's referral information
router.get('/referrals', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;

    const referralStats = await AlphaInvestment.aggregate([
      { $match: { referredBy: mongoose.Types.ObjectId(userId) } },
      {
        $group: {
          _id: null,
          totalReferrals: { $sum: 1 },
          totalReferralBonus: { $sum: '$referralBonus' },
          totalReferredAmount: { $sum: '$investmentAmount' },
        },
      },
    ]);

    const recentReferrals = await AlphaInvestment.find({
      referredBy: userId,
    })
      .populate('userId', 'username email')
      .populate('tokenId')
      .sort({ investedAt: -1 })
      .limit(10);

    res.json({
      success: true,
      data: {
        stats: referralStats[0] || {
          totalReferrals: 0,
          totalReferralBonus: 0,
          totalReferredAmount: 0,
        },
        recentReferrals,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching referral information',
      error: error.message,
    });
  }
});

// Get investment history with filters
router.get('/history', authMiddleware, async (req, res) => {
  try {
    const {
      startDate,
      endDate,
      status,
      blockchain,
      minAmount,
      maxAmount,
      page = 1,
      limit = 20,
    } = req.query;

    const query = { userId: req.user.id };

    if (startDate || endDate) {
      query.investedAt = {};
      if (startDate) query.investedAt.$gte = new Date(startDate);
      if (endDate) query.investedAt.$lte = new Date(endDate);
    }

    if (status) query.status = status;
    if (blockchain) query.blockchain = blockchain;

    if (minAmount || maxAmount) {
      query.investmentAmount = {};
      if (minAmount) query.investmentAmount.$gte = parseFloat(minAmount);
      if (maxAmount) query.investmentAmount.$lte = parseFloat(maxAmount);
    }

    const investments = await AlphaInvestment.find(query)
      .populate('tokenId')
      .sort({ investedAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit);

    const total = await AlphaInvestment.countDocuments(query);

    res.json({
      success: true,
      data: {
        investments,
        pagination: {
          current: parseInt(page),
          pages: Math.ceil(total / limit),
          total,
        },
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error fetching investment history',
      error: error.message,
    });
  }
});

module.exports = router;
