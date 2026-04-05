const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const winston = require('winston');
const EventEmitter = require('events');

class StripeService extends EventEmitter {
  constructor() {
    super();
    this.isRunning = false;
    this.webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'stripe-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/stripe-service.log' }),
        new winston.transports.Console(),
      ],
    });
  }

  async initialize() {
    try {
      this.logger.info('Initializing Stripe Service...');

      // Test Stripe connection
      await this.testConnection();

      this.isRunning = true;
      this.logger.info('Stripe Service initialized successfully');

      this.emit('initialized');
    } catch (error) {
      this.logger.error('Failed to initialize Stripe Service:', error);
      throw error;
    }
  }

  async testConnection() {
    try {
      await stripe.balance.retrieve();
      this.logger.info('Stripe connection test successful');
    } catch (error) {
      this.logger.error('Stripe connection test failed:', error);
      throw error;
    }
  }

  async createCustomer(customerData) {
    try {
      const { userId, email, name, phone, address } = customerData;

      const customer = await stripe.customers.create({
        email,
        name,
        phone,
        address,
        metadata: {
          userId: userId,
          platform: 'TigerEx',
        },
      });

      this.logger.info(
        `Created Stripe customer: ${customer.id} for user: ${userId}`
      );
      return customer;
    } catch (error) {
      this.logger.error('Error creating Stripe customer:', error);
      throw error;
    }
  }

  async createPaymentMethod(paymentMethodData) {
    try {
      const { type, card, billing_details } = paymentMethodData;

      const paymentMethod = await stripe.paymentMethods.create({
        type,
        card,
        billing_details,
      });

      this.logger.info(`Created payment method: ${paymentMethod.id}`);
      return paymentMethod;
    } catch (error) {
      this.logger.error('Error creating payment method:', error);
      throw error;
    }
  }

  async processPayment(paymentData) {
    try {
      const {
        amount,
        currency,
        paymentMethod,
        customerId,
        billingAddress,
        metadata = {},
      } = paymentData;

      // Convert amount to cents for Stripe
      const amountInCents = Math.round(parseFloat(amount) * 100);

      // Create payment intent
      const paymentIntent = await stripe.paymentIntents.create({
        amount: amountInCents,
        currency: currency.toLowerCase(),
        customer: customerId,
        payment_method: paymentMethod.id || paymentMethod,
        confirmation_method: 'manual',
        confirm: true,
        return_url: `${process.env.FRONTEND_URL}/payment/return`,
        metadata: {
          ...metadata,
          platform: 'TigerEx',
        },
      });

      this.logger.info(`Created payment intent: ${paymentIntent.id}`);

      // Handle different payment intent statuses
      if (paymentIntent.status === 'requires_action') {
        return {
          requiresAction: true,
          clientSecret: paymentIntent.client_secret,
          paymentIntent,
        };
      } else if (paymentIntent.status === 'succeeded') {
        return {
          success: true,
          paymentIntent,
        };
      } else {
        throw new Error(
          `Unexpected payment intent status: ${paymentIntent.status}`
        );
      }
    } catch (error) {
      this.logger.error('Error processing Stripe payment:', error);
      throw error;
    }
  }

  async confirmPayment(paymentIntentId) {
    try {
      const paymentIntent =
        await stripe.paymentIntents.confirm(paymentIntentId);

      this.logger.info(`Confirmed payment intent: ${paymentIntentId}`);
      return paymentIntent;
    } catch (error) {
      this.logger.error(
        `Error confirming payment intent ${paymentIntentId}:`,
        error
      );
      throw error;
    }
  }

  async getPaymentStatus(paymentIntentId) {
    try {
      const paymentIntent =
        await stripe.paymentIntents.retrieve(paymentIntentId);

      return {
        status: paymentIntent.status,
        amount: paymentIntent.amount / 100,
        currency: paymentIntent.currency,
        charges: paymentIntent.charges.data,
        failure_reason: paymentIntent.last_payment_error?.message,
      };
    } catch (error) {
      this.logger.error(
        `Error getting payment status ${paymentIntentId}:`,
        error
      );
      throw error;
    }
  }

  async createRefund(refundData) {
    try {
      const { chargeId, amount, reason, metadata = {} } = refundData;

      const refundParams = {
        charge: chargeId,
        reason: reason || 'requested_by_customer',
        metadata: {
          ...metadata,
          platform: 'TigerEx',
        },
      };

      if (amount) {
        refundParams.amount = Math.round(parseFloat(amount) * 100);
      }

      const refund = await stripe.refunds.create(refundParams);

      this.logger.info(`Created refund: ${refund.id} for charge: ${chargeId}`);
      return refund;
    } catch (error) {
      this.logger.error('Error creating refund:', error);
      throw error;
    }
  }

  async handleWebhook(payload, signature) {
    try {
      const event = stripe.webhooks.constructEvent(
        payload,
        signature,
        this.webhookSecret
      );

      this.logger.info(`Received Stripe webhook: ${event.type}`);

      switch (event.type) {
        case 'payment_intent.succeeded':
          await this.handlePaymentSucceeded(event.data.object);
          break;
        case 'payment_intent.payment_failed':
          await this.handlePaymentFailed(event.data.object);
          break;
        case 'charge.dispute.created':
          await this.handleChargeDispute(event.data.object);
          break;
        case 'invoice.payment_succeeded':
          await this.handleInvoicePaymentSucceeded(event.data.object);
          break;
        case 'customer.subscription.created':
          await this.handleSubscriptionCreated(event.data.object);
          break;
        default:
          this.logger.info(`Unhandled webhook event type: ${event.type}`);
      }

      return { received: true };
    } catch (error) {
      this.logger.error('Error handling Stripe webhook:', error);
      throw error;
    }
  }

  async handlePaymentSucceeded(paymentIntent) {
    try {
      this.emit('paymentSucceeded', {
        paymentIntentId: paymentIntent.id,
        amount: paymentIntent.amount / 100,
        currency: paymentIntent.currency,
        metadata: paymentIntent.metadata,
      });
    } catch (error) {
      this.logger.error('Error handling payment succeeded:', error);
    }
  }

  async handlePaymentFailed(paymentIntent) {
    try {
      this.emit('paymentFailed', {
        paymentIntentId: paymentIntent.id,
        error: paymentIntent.last_payment_error,
        metadata: paymentIntent.metadata,
      });
    } catch (error) {
      this.logger.error('Error handling payment failed:', error);
    }
  }

  async handleChargeDispute(dispute) {
    try {
      this.emit('chargeDisputed', {
        disputeId: dispute.id,
        chargeId: dispute.charge,
        amount: dispute.amount / 100,
        currency: dispute.currency,
        reason: dispute.reason,
        status: dispute.status,
      });
    } catch (error) {
      this.logger.error('Error handling charge dispute:', error);
    }
  }

  async handleInvoicePaymentSucceeded(invoice) {
    try {
      this.emit('invoicePaymentSucceeded', {
        invoiceId: invoice.id,
        subscriptionId: invoice.subscription,
        amount: invoice.amount_paid / 100,
        currency: invoice.currency,
      });
    } catch (error) {
      this.logger.error('Error handling invoice payment succeeded:', error);
    }
  }

  async handleSubscriptionCreated(subscription) {
    try {
      this.emit('subscriptionCreated', {
        subscriptionId: subscription.id,
        customerId: subscription.customer,
        status: subscription.status,
        currentPeriodStart: new Date(subscription.current_period_start * 1000),
        currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      });
    } catch (error) {
      this.logger.error('Error handling subscription created:', error);
    }
  }

  async createSetupIntent(customerId, paymentMethodTypes = ['card']) {
    try {
      const setupIntent = await stripe.setupIntents.create({
        customer: customerId,
        payment_method_types: paymentMethodTypes,
        usage: 'off_session',
      });

      this.logger.info(`Created setup intent: ${setupIntent.id}`);
      return setupIntent;
    } catch (error) {
      this.logger.error('Error creating setup intent:', error);
      throw error;
    }
  }

  async attachPaymentMethod(paymentMethodId, customerId) {
    try {
      const paymentMethod = await stripe.paymentMethods.attach(
        paymentMethodId,
        {
          customer: customerId,
        }
      );

      this.logger.info(
        `Attached payment method ${paymentMethodId} to customer ${customerId}`
      );
      return paymentMethod;
    } catch (error) {
      this.logger.error('Error attaching payment method:', error);
      throw error;
    }
  }

  async listCustomerPaymentMethods(customerId, type = 'card') {
    try {
      const paymentMethods = await stripe.paymentMethods.list({
        customer: customerId,
        type: type,
      });

      return paymentMethods.data;
    } catch (error) {
      this.logger.error('Error listing customer payment methods:', error);
      throw error;
    }
  }

  async createPayout(payoutData) {
    try {
      const { amount, currency, destination, metadata = {} } = payoutData;

      const payout = await stripe.payouts.create({
        amount: Math.round(parseFloat(amount) * 100),
        currency: currency.toLowerCase(),
        destination,
        metadata: {
          ...metadata,
          platform: 'TigerEx',
        },
      });

      this.logger.info(`Created payout: ${payout.id}`);
      return payout;
    } catch (error) {
      this.logger.error('Error creating payout:', error);
      throw error;
    }
  }

  async getBalance() {
    try {
      const balance = await stripe.balance.retrieve();
      return balance;
    } catch (error) {
      this.logger.error('Error getting Stripe balance:', error);
      throw error;
    }
  }

  async getTransactions(limit = 100) {
    try {
      const transactions = await stripe.balanceTransactions.list({
        limit: limit,
      });

      return transactions.data;
    } catch (error) {
      this.logger.error('Error getting Stripe transactions:', error);
      throw error;
    }
  }

  getHealthStatus() {
    return {
      isRunning: this.isRunning,
      provider: 'Stripe',
      webhookConfigured: !!this.webhookSecret,
      uptime: process.uptime(),
    };
  }

  shutdown() {
    this.logger.info('Shutting down Stripe Service...');
    this.isRunning = false;
    this.emit('shutdown');
  }
}

module.exports = new StripeService();
