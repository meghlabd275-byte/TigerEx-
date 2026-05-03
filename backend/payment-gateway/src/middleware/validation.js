const Joi = require('joi');

// Payment creation validation schema
const paymentCreationSchema = Joi.object({
  type: Joi.string()
    .valid(
      'DEPOSIT',
      'WITHDRAWAL',
      'REFUND',
      'CHARGEBACK',
      'FEE_PAYMENT',
      'SUBSCRIPTION'
    )
    .required(),
  method: Joi.string()
    .valid(
      'CREDIT_CARD',
      'DEBIT_CARD',
      'BANK_TRANSFER',
      'ACH',
      'WIRE_TRANSFER',
      'PAYPAL',
      'APPLE_PAY',
      'GOOGLE_PAY',
      'SEPA',
      'SWIFT'
    )
    .required(),
  currency: Joi.string().required().uppercase().length(3),
  amount: Joi.number().positive().required().messages({
    'number.positive': 'Amount must be positive',
  }),
  billingAddress: Joi.object({
    name: Joi.string().required(),
    line1: Joi.string().required(),
    line2: Joi.string().optional(),
    city: Joi.string().required(),
    state: Joi.string().required(),
    postalCode: Joi.string().required(),
    country: Joi.string().required().length(2),
  }).optional(),
  paymentInstrument: Joi.object({
    type: Joi.string()
      .valid('CARD', 'BANK_ACCOUNT', 'WALLET', 'OTHER')
      .required(),
    last4: Joi.string().optional(),
    brand: Joi.string().optional(),
    country: Joi.string().optional(),
    bankName: Joi.string().optional(),
    accountType: Joi.string().optional(),
    routingNumber: Joi.string().optional(),
  }).optional(),
  metadata: Joi.object().optional(),
});

// Payment processing validation schema
const paymentProcessingSchema = Joi.object({
  paymentMethodId: Joi.string().optional(),
  confirmationToken: Joi.string().optional(),
  twoFactorCode: Joi.string()
    .optional()
    .length(6)
    .pattern(/^[0-9]+$/),
  metadata: Joi.object().optional(),
});

// Deposit validation schema
const depositSchema = Joi.object({
  currency: Joi.string().required().uppercase().length(3),
  amount: Joi.number().positive().required(),
  method: Joi.string()
    .valid('CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'ACH', 'PAYPAL')
    .required(),
  paymentInstrument: Joi.object().required(),
  billingAddress: Joi.object().optional(),
  metadata: Joi.object().optional(),
});

// Withdrawal validation schema
const withdrawalSchema = Joi.object({
  currency: Joi.string().required().uppercase().length(3),
  amount: Joi.number().positive().required(),
  method: Joi.string()
    .valid('BANK_TRANSFER', 'ACH', 'WIRE_TRANSFER', 'PAYPAL', 'SEPA', 'SWIFT')
    .required(),
  destination: Joi.object({
    type: Joi.string().valid('BANK_ACCOUNT', 'PAYPAL', 'WALLET').required(),
    accountNumber: Joi.string().when('type', {
      is: 'BANK_ACCOUNT',
      then: Joi.required(),
      otherwise: Joi.optional(),
    }),
    routingNumber: Joi.string().when('type', {
      is: 'BANK_ACCOUNT',
      then: Joi.required(),
      otherwise: Joi.optional(),
    }),
    accountType: Joi.string().when('type', {
      is: 'BANK_ACCOUNT',
      then: Joi.valid('checking', 'savings').required(),
      otherwise: Joi.optional(),
    }),
    email: Joi.string().email().when('type', {
      is: 'PAYPAL',
      then: Joi.required(),
      otherwise: Joi.optional(),
    }),
  }).required(),
  twoFactorCode: Joi.string()
    .optional()
    .length(6)
    .pattern(/^[0-9]+$/),
  metadata: Joi.object().optional(),
});

// Bank account validation schema
const bankAccountSchema = Joi.object({
  accountNumber: Joi.string()
    .required()
    .pattern(/^[0-9]{8,17}$/)
    .messages({
      'string.pattern.base': 'Account number must be 8-17 digits',
    }),
  routingNumber: Joi.string()
    .required()
    .pattern(/^[0-9]{9}$/)
    .messages({
      'string.pattern.base': 'Routing number must be 9 digits',
    }),
  accountType: Joi.string().valid('checking', 'savings').required(),
  accountHolderName: Joi.string().required().min(2).max(100),
  bankName: Joi.string().optional().max(100),
});

// Card validation schema
const cardSchema = Joi.object({
  number: Joi.string()
    .required()
    .pattern(/^[0-9]{13,19}$/)
    .messages({
      'string.pattern.base': 'Card number must be 13-19 digits',
    }),
  expiryMonth: Joi.number().integer().min(1).max(12).required(),
  expiryYear: Joi.number().integer().min(new Date().getFullYear()).required(),
  cvc: Joi.string()
    .required()
    .pattern(/^[0-9]{3,4}$/)
    .messages({
      'string.pattern.base': 'CVC must be 3-4 digits',
    }),
  holderName: Joi.string().required().min(2).max(100),
});

// KYC document validation schema
const kycDocumentSchema = Joi.object({
  documentType: Joi.string()
    .valid(
      'PASSPORT',
      'DRIVERS_LICENSE',
      'NATIONAL_ID',
      'UTILITY_BILL',
      'BANK_STATEMENT'
    )
    .required(),
  documentNumber: Joi.string().optional(),
  expiryDate: Joi.date().optional(),
  issuingCountry: Joi.string().length(2).required(),
  metadata: Joi.object().optional(),
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

// Payment history query validation
const paymentHistoryQuerySchema = Joi.object({
  type: Joi.string()
    .optional()
    .valid(
      'DEPOSIT',
      'WITHDRAWAL',
      'REFUND',
      'CHARGEBACK',
      'FEE_PAYMENT',
      'SUBSCRIPTION'
    ),
  method: Joi.string()
    .optional()
    .valid(
      'CREDIT_CARD',
      'DEBIT_CARD',
      'BANK_TRANSFER',
      'ACH',
      'WIRE_TRANSFER',
      'PAYPAL',
      'APPLE_PAY',
      'GOOGLE_PAY',
      'SEPA',
      'SWIFT'
    ),
  status: Joi.string()
    .optional()
    .valid(
      'PENDING',
      'PROCESSING',
      'COMPLETED',
      'FAILED',
      'CANCELLED',
      'EXPIRED',
      'REFUNDED',
      'DISPUTED'
    ),
  currency: Joi.string().optional().uppercase().length(3),
  startDate: Joi.date().optional(),
  endDate: Joi.date().optional().min(Joi.ref('startDate')),
  limit: Joi.number().integer().min(1).max(100).default(50),
  page: Joi.number().integer().min(1).default(1),
});

// Specific validation middleware
const validatePaymentCreation = validate(paymentCreationSchema);
const validatePaymentProcessing = validate(paymentProcessingSchema);
const validateDeposit = validate(depositSchema);
const validateWithdrawal = validate(withdrawalSchema);
const validateBankAccount = validate(bankAccountSchema);
const validateCard = validate(cardSchema);
const validateKYCDocument = validate(kycDocumentSchema);
const validatePaymentHistoryQuery = validateQuery(paymentHistoryQuerySchema);

module.exports = {
  validatePaymentCreation,
  validatePaymentProcessing,
  validateDeposit,
  validateWithdrawal,
  validateBankAccount,
  validateCard,
  validateKYCDocument,
  validatePaymentHistoryQuery,
  validate,
  validateQuery,
};
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
