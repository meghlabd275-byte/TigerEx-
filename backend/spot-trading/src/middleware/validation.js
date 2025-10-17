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

// Order validation schema
const orderSchema = Joi.object({
  symbol: Joi.string().required().uppercase().messages({
    'any.required': 'Symbol is required',
    'string.empty': 'Symbol cannot be empty',
  }),
  side: Joi.string().valid('BUY', 'SELL').required().messages({
    'any.required': 'Side is required',
    'any.only': 'Side must be either BUY or SELL',
  }),
  type: Joi.string()
    .valid('MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LIMIT', 'TAKE_PROFIT')
    .required()
    .messages({
      'any.required': 'Order type is required',
      'any.only': 'Invalid order type',
    }),
  quantity: Joi.number().positive().required().messages({
    'any.required': 'Quantity is required',
    'number.positive': 'Quantity must be positive',
  }),
  price: Joi.number()
    .positive()
    .when('type', {
      is: Joi.string().valid('LIMIT', 'STOP_LIMIT'),
      then: Joi.required(),
      otherwise: Joi.optional(),
    })
    .messages({
      'any.required': 'Price is required for limit orders',
      'number.positive': 'Price must be positive',
    }),
  stopPrice: Joi.number()
    .positive()
    .when('type', {
      is: Joi.string().valid('STOP_LOSS', 'STOP_LIMIT', 'TAKE_PROFIT'),
      then: Joi.required(),
      otherwise: Joi.optional(),
    })
    .messages({
      'any.required': 'Stop price is required for stop orders',
      'number.positive': 'Stop price must be positive',
    }),
  timeInForce: Joi.string()
    .valid('GTC', 'IOC', 'FOK')
    .optional()
    .default('GTC'),
  clientOrderId: Joi.string().max(36).optional(),
});

// Cancel order validation schema
const cancelOrderSchema = Joi.object({
  reason: Joi.string().max(100).optional().default('USER_CANCELED'),
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

// Specific validation middleware
const validateOrder = validate(orderSchema);
const validateCancelOrder = validate(cancelOrderSchema);

module.exports = {
  validateOrder,
  validateCancelOrder,
  validate,
};
