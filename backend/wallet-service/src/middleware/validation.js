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

const Joi = require('joi');

// Wallet creation validation schema
const walletCreationSchema = Joi.object({
  currency: Joi.string().required().uppercase().min(2).max(10).messages({
    'any.required': 'Currency is required',
    'string.empty': 'Currency cannot be empty',
    'string.min': 'Currency must be at least 2 characters',
    'string.max': 'Currency must not exceed 10 characters',
  }),
  network: Joi.string().optional().uppercase().min(2).max(20),
});

// Balance update validation schema
const balanceUpdateSchema = Joi.object({
  amount: Joi.number().required().messages({
    'any.required': 'Amount is required',
    'number.base': 'Amount must be a number',
  }),
  type: Joi.string()
    .valid('available', 'locked', 'staked')
    .default('available'),
  reason: Joi.string().required().min(5).max(200).messages({
    'any.required': 'Reason is required',
    'string.min': 'Reason must be at least 5 characters',
    'string.max': 'Reason must not exceed 200 characters',
  }),
});

// Deposit validation schema
const depositSchema = Joi.object({
  currency: Joi.string().required().uppercase(),
  amount: Joi.number().positive().required().messages({
    'any.required': 'Amount is required',
    'number.positive': 'Amount must be positive',
  }),
  txHash: Joi.string().required().min(10).messages({
    'any.required': 'Transaction hash is required',
    'string.min': 'Invalid transaction hash format',
  }),
  fromAddress: Joi.string().required(),
  toAddress: Joi.string().required(),
  network: Joi.string().optional().uppercase(),
  confirmations: Joi.number().integer().min(0).default(0),
});

// Withdrawal validation schema
const withdrawalSchema = Joi.object({
  currency: Joi.string().required().uppercase(),
  amount: Joi.number().positive().required().messages({
    'any.required': 'Amount is required',
    'number.positive': 'Amount must be positive',
  }),
  address: Joi.string().required().min(10).messages({
    'any.required': 'Withdrawal address is required',
    'string.min': 'Invalid address format',
  }),
  network: Joi.string().optional().uppercase(),
  memo: Joi.string().optional().max(100),
  twoFactorCode: Joi.string()
    .optional()
    .length(6)
    .pattern(/^[0-9]+$/)
    .messages({
      'string.length': '2FA code must be 6 digits',
      'string.pattern.base': '2FA code must contain only numbers',
    }),
});

// Address generation validation schema
const addressGenerationSchema = Joi.object({
  currency: Joi.string().required().uppercase(),
  network: Joi.string().optional().uppercase(),
  type: Joi.string().valid('DEPOSIT', 'WITHDRAWAL').default('DEPOSIT'),
});

// Transfer validation schema
const transferSchema = Joi.object({
  toUserId: Joi.string().required().messages({
    'any.required': 'Recipient user ID is required',
  }),
  currency: Joi.string().required().uppercase(),
  amount: Joi.number().positive().required().messages({
    'any.required': 'Amount is required',
    'number.positive': 'Amount must be positive',
  }),
  reason: Joi.string().optional().max(200),
  twoFactorCode: Joi.string()
    .optional()
    .length(6)
    .pattern(/^[0-9]+$/),
});

// Validation middleware factory
const validate = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      }));

      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors,
      });
    }

    req.body = value;
    next();
  };
};

// Query validation for pagination and filtering
const validateQuery = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.query, {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      }));

      return res.status(400).json({
        success: false,
        message: 'Query validation failed',
        errors,
      });
    }

    req.query = value;
    next();
  };
};

// Transaction history query validation
const transactionHistoryQuerySchema = Joi.object({
  currency: Joi.string().optional().uppercase(),
  type: Joi.string()
    .optional()
    .valid(
      'DEPOSIT',
      'WITHDRAWAL',
      'TRADE_BUY',
      'TRADE_SELL',
      'TRANSFER_IN',
      'TRANSFER_OUT',
      'STAKING_REWARD',
      'REFERRAL_BONUS',
      'AIRDROP',
      'FEE_DEDUCTION',
      'ADJUSTMENT'
    ),
  status: Joi.string()
    .optional()
    .valid(
      'PENDING',
      'PROCESSING',
      'COMPLETED',
      'FAILED',
      'CANCELLED',
      'EXPIRED'
    ),
  startDate: Joi.date().optional(),
  endDate: Joi.date().optional().min(Joi.ref('startDate')),
  limit: Joi.number().integer().min(1).max(100).default(50),
  page: Joi.number().integer().min(1).default(1),
});

// Specific validation middleware
const validateWalletCreation = validate(walletCreationSchema);
const validateBalanceUpdate = validate(balanceUpdateSchema);
const validateDeposit = validate(depositSchema);
const validateWithdrawal = validate(withdrawalSchema);
const validateAddressGeneration = validate(addressGenerationSchema);
const validateTransfer = validate(transferSchema);
const validateTransactionHistoryQuery = validateQuery(
  transactionHistoryQuerySchema
);

module.exports = {
  validateWalletCreation,
  validateBalanceUpdate,
  validateDeposit,
  validateWithdrawal,
  validateAddressGeneration,
  validateTransfer,
  validateTransactionHistoryQuery,
  validate,
  validateQuery,
};
