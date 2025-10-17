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

// Alpha Token validation schema
const alphaTokenSchema = Joi.object({
  name: Joi.string().min(2).max(100).required(),
  symbol: Joi.string().min(2).max(10).uppercase().required(),
  description: Joi.string().min(10).max(1000).required(),
  blockchain: Joi.string()
    .valid(
      'ethereum',
      'bsc',
      'polygon',
      'arbitrum',
      'optimism',
      'avalanche',
      'fantom',
      'solana'
    )
    .required(),
  decimals: Joi.number().integer().min(0).max(18).default(18),

  // Alpha market specific data
  alphaStartDate: Joi.date().greater('now').required(),
  alphaEndDate: Joi.date().greater(Joi.ref('alphaStartDate')).required(),
  publicLaunchDate: Joi.date().greater(Joi.ref('alphaEndDate')).optional(),

  // Pricing and allocation
  alphaPrice: Joi.number().positive().required(),
  totalSupply: Joi.number().positive().required(),
  alphaAllocation: Joi.number()
    .positive()
    .max(Joi.ref('totalSupply'))
    .required(),
  minInvestment: Joi.number().positive().default(100),
  maxInvestment: Joi.number()
    .positive()
    .greater(Joi.ref('minInvestment'))
    .default(10000),

  // Investor requirements
  tierRequirements: Joi.object({
    bronze: Joi.object({
      minStake: Joi.number().positive().default(1000),
      allocation: Joi.number().min(0).max(1).default(0.1),
    }).default(),
    silver: Joi.object({
      minStake: Joi.number().positive().default(5000),
      allocation: Joi.number().min(0).max(1).default(0.3),
    }).default(),
    gold: Joi.object({
      minStake: Joi.number().positive().default(25000),
      allocation: Joi.number().min(0).max(1).default(0.6),
    }).default(),
    platinum: Joi.object({
      minStake: Joi.number().positive().default(100000),
      allocation: Joi.number().min(0).max(1).default(1.0),
    }).default(),
  }).default(),

  // Project information
  projectTeam: Joi.array()
    .items(
      Joi.object({
        name: Joi.string().required(),
        role: Joi.string().required(),
        linkedin: Joi.string().uri().optional(),
        experience: Joi.string().optional(),
      })
    )
    .min(1)
    .required(),

  whitepaper: Joi.object({
    url: Joi.string().uri().required(),
    hash: Joi.string().optional(),
  }).optional(),

  website: Joi.string().uri().optional(),

  socialLinks: Joi.object({
    twitter: Joi.string().uri().optional(),
    telegram: Joi.string().uri().optional(),
    discord: Joi.string().uri().optional(),
    medium: Joi.string().uri().optional(),
  }).optional(),

  // Vesting schedule
  vestingSchedule: Joi.array()
    .items(
      Joi.object({
        releaseDate: Joi.date().required(),
        percentage: Joi.number().min(0).max(100).required(),
        description: Joi.string().optional(),
      })
    )
    .min(1)
    .required(),

  // Status and flags
  isKYCRequired: Joi.boolean().default(true),
  isWhitelisted: Joi.boolean().default(false),
});

// Investment validation schema
const investmentSchema = Joi.object({
  investmentAmount: Joi.number().positive().required(),
  paymentMethod: Joi.string()
    .valid('USDT', 'USDC', 'ETH', 'BNB', 'MATIC', 'AVAX')
    .required(),
  referralCode: Joi.string().optional(),
  riskAcknowledged: Joi.boolean().valid(true).required(),
});

// User tier update schema
const tierUpdateSchema = Joi.object({
  tier: Joi.string().valid('bronze', 'silver', 'gold', 'platinum').required(),
  stakeAmount: Joi.number().positive().required(),
});

// Token status update schema
const tokenStatusSchema = Joi.object({
  status: Joi.string()
    .valid(
      'pending',
      'approved',
      'rejected',
      'active',
      'completed',
      'cancelled'
    )
    .required(),
  reason: Joi.string().when('status', {
    is: 'rejected',
    then: Joi.required(),
    otherwise: Joi.optional(),
  }),
});

// Investment status update schema
const investmentStatusSchema = Joi.object({
  status: Joi.string()
    .valid('pending', 'confirmed', 'failed', 'refunded', 'vested')
    .required(),
  confirmationBlocks: Joi.number().integer().min(0).optional(),
  transactionHash: Joi.string().optional(),
});

// Claim tokens schema
const claimTokensSchema = Joi.object({
  amount: Joi.number().positive().required(),
  transactionHash: Joi.string().required(),
});

// Validation middleware factory
const validate = (schema, property = 'body') => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], {
      abortEarly: false,
      allowUnknown: false,
      stripUnknown: true,
    });

    if (error) {
      const errorMessage = error.details
        .map((detail) => detail.message)
        .join(', ');
      return res.status(400).json({
        success: false,
        message: 'Validation error',
        errors: error.details.map((detail) => ({
          field: detail.path.join('.'),
          message: detail.message,
        })),
      });
    }

    // Replace the original data with validated and sanitized data
    req[property] = value;
    next();
  };
};

// Specific validation middlewares
const validateAlphaToken = validate(alphaTokenSchema);
const validateInvestment = validate(investmentSchema);
const validateTierUpdate = validate(tierUpdateSchema);
const validateTokenStatus = validate(tokenStatusSchema);
const validateInvestmentStatus = validate(investmentStatusSchema);
const validateClaimTokens = validate(claimTokensSchema);

// Query parameter validation
const validatePagination = (req, res, next) => {
  const schema = Joi.object({
    page: Joi.number().integer().min(1).default(1),
    limit: Joi.number().integer().min(1).max(100).default(20),
    sortBy: Joi.string().optional(),
    sortOrder: Joi.string().valid('asc', 'desc').default('desc'),
  });

  const { error, value } = schema.validate(req.query, { allowUnknown: true });

  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Invalid pagination parameters',
      errors: error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      })),
    });
  }

  // Update query with validated values
  Object.assign(req.query, value);
  next();
};

// Date range validation
const validateDateRange = (req, res, next) => {
  const schema = Joi.object({
    startDate: Joi.date().optional(),
    endDate: Joi.date().greater(Joi.ref('startDate')).optional(),
  });

  const { error, value } = schema.validate({
    startDate: req.query.startDate,
    endDate: req.query.endDate,
  });

  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Invalid date range',
      errors: error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      })),
    });
  }

  next();
};

// Amount range validation
const validateAmountRange = (req, res, next) => {
  const schema = Joi.object({
    minAmount: Joi.number().positive().optional(),
    maxAmount: Joi.number().positive().greater(Joi.ref('minAmount')).optional(),
  });

  const { error, value } = schema.validate({
    minAmount: req.query.minAmount
      ? parseFloat(req.query.minAmount)
      : undefined,
    maxAmount: req.query.maxAmount
      ? parseFloat(req.query.maxAmount)
      : undefined,
  });

  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Invalid amount range',
      errors: error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
      })),
    });
  }

  next();
};

// Custom validation for investment eligibility
const validateInvestmentEligibility = async (req, res, next) => {
  try {
    const { investmentAmount } = req.body;
    const userTier = req.user.tier;
    const userStakeAmount = req.user.stakeAmount;

    // Check if user meets tier requirements
    const tierRequirements = {
      bronze: { minStake: 1000 },
      silver: { minStake: 5000 },
      gold: { minStake: 25000 },
      platinum: { minStake: 100000 },
    };

    const requiredStake = tierRequirements[userTier]?.minStake || 0;
    if (userStakeAmount < requiredStake) {
      return res.status(400).json({
        success: false,
        message: `Insufficient stake amount for ${userTier} tier. Required: ${requiredStake}, Current: ${userStakeAmount}`,
      });
    }

    // Check KYC status for large investments
    if (investmentAmount > 1000 && req.user.kycStatus !== 'approved') {
      return res.status(400).json({
        success: false,
        message: 'KYC verification required for investments over $1000',
      });
    }

    next();
  } catch (error) {
    next(error);
  }
};

module.exports = {
  validate,
  validateAlphaToken,
  validateInvestment,
  validateTierUpdate,
  validateTokenStatus,
  validateInvestmentStatus,
  validateClaimTokens,
  validatePagination,
  validateDateRange,
  validateAmountRange,
  validateInvestmentEligibility,
};
