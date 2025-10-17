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
const WalletService = require('../services/WalletService');
const authMiddleware = require('../middleware/auth');
const {
  validateWalletCreation,
  validateBalanceUpdate,
} = require('../middleware/validation');
const { asyncHandler } = require('../middleware/errorHandler');

// Get user's wallets
router.get(
  '/',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const wallets = await WalletService.getUserWallets(req.user.userId);

    res.json({
      success: true,
      data: wallets,
    });
  })
);

// Get user's portfolio
router.get(
  '/portfolio',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const portfolio = await WalletService.getUserPortfolio(req.user.userId);

    res.json({
      success: true,
      data: portfolio,
    });
  })
);

// Create new wallet
router.post(
  '/',
  authMiddleware,
  validateWalletCreation,
  asyncHandler(async (req, res) => {
    const { currency, network } = req.body;

    const wallet = await WalletService.createWallet(
      req.user.userId,
      currency,
      network
    );

    res.status(201).json({
      success: true,
      message: 'Wallet created successfully',
      data: wallet.toSafeObject(),
    });
  })
);

// Get specific wallet
router.get(
  '/:currency',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { currency } = req.params;

    const wallet = await WalletService.getOrCreateWallet(
      req.user.userId,
      currency
    );

    res.json({
      success: true,
      data: wallet.toSafeObject(),
    });
  })
);

// Update wallet balance (admin only)
router.patch(
  '/:currency/balance',
  authMiddleware,
  validateBalanceUpdate,
  asyncHandler(async (req, res) => {
    // Check if user has admin privileges
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const { currency } = req.params;
    const { amount, type, reason } = req.body;

    const wallet = await WalletService.updateBalance(
      req.user.userId,
      currency,
      amount,
      type,
      `ADMIN_ADJUSTMENT: ${reason}`
    );

    res.json({
      success: true,
      message: 'Balance updated successfully',
      data: wallet.toSafeObject(),
    });
  })
);

// Lock balance
router.post(
  '/:currency/lock',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { currency } = req.params;
    const { amount, reason } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid amount',
      });
    }

    const wallet = await WalletService.lockBalance(
      req.user.userId,
      currency,
      amount,
      reason || 'USER_REQUEST'
    );

    res.json({
      success: true,
      message: 'Balance locked successfully',
      data: wallet.toSafeObject(),
    });
  })
);

// Unlock balance
router.post(
  '/:currency/unlock',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { currency } = req.params;
    const { amount, reason } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid amount',
      });
    }

    const wallet = await WalletService.unlockBalance(
      req.user.userId,
      currency,
      amount,
      reason || 'USER_REQUEST'
    );

    res.json({
      success: true,
      message: 'Balance unlocked successfully',
      data: wallet.toSafeObject(),
    });
  })
);

// Transfer balance to another user
router.post(
  '/:currency/transfer',
  authMiddleware,
  asyncHandler(async (req, res) => {
    const { currency } = req.params;
    const { toUserId, amount, reason } = req.body;

    if (!toUserId || !amount || amount <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid transfer parameters',
      });
    }

    const result = await WalletService.transferBalance(
      req.user.userId,
      toUserId,
      currency,
      amount,
      reason || 'USER_TRANSFER'
    );

    res.json({
      success: true,
      message: 'Transfer completed successfully',
      data: {
        fromWallet: result.fromWallet.toSafeObject(),
        toWallet: result.toWallet.toSafeObject(),
      },
    });
  })
);

// Get wallet statistics (admin only)
router.get(
  '/admin/statistics',
  authMiddleware,
  asyncHandler(async (req, res) => {
    if (!req.user.roles.includes('admin')) {
      return res.status(403).json({
        success: false,
        message: 'Admin privileges required',
      });
    }

    const statistics = await WalletService.generateStatistics();

    res.json({
      success: true,
      data: statistics,
    });
  })
);

module.exports = router;
