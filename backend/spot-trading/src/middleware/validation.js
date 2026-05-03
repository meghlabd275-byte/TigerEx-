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
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
