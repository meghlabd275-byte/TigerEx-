/**
 * TigerEx Notification Service
 * Handles all notification delivery across multiple channels
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const nodemailer = require('nodemailer');
const twilio = require('twilio');
const admin = require('firebase-admin');

const app = express();
const PORT = process.env.PORT || 3006;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Initialize Firebase Admin for push notifications
if (process.env.FIREBASE_SERVICE_ACCOUNT) {
  const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

// Initialize email transporter
const emailTransporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port: process.env.SMTP_PORT || 587,
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
});

// Initialize Twilio for SMS
const twilioClient = process.env.TWILIO_ACCOUNT_SID && process.env.TWILIO_AUTH_TOKEN
  ? twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN)
  : null;

// Notification templates
const templates = {
  email: {
    welcome: {
      subject: 'Welcome to TigerEx',
      html: '<h1>Welcome to TigerEx!</h1><p>Thank you for joining our platform.</p>'
    },
    deposit: {
      subject: 'Deposit Confirmed',
      html: '<h1>Deposit Confirmed</h1><p>Your deposit of {{amount}} {{currency}} has been confirmed.</p>'
    },
    withdrawal: {
      subject: 'Withdrawal Processed',
      html: '<h1>Withdrawal Processed</h1><p>Your withdrawal of {{amount}} {{currency}} has been processed.</p>'
    },
    trade: {
      subject: 'Trade Executed',
      html: '<h1>Trade Executed</h1><p>Your {{type}} order for {{amount}} {{pair}} has been executed.</p>'
    },
    security: {
      subject: 'Security Alert',
      html: '<h1>Security Alert</h1><p>{{message}}</p>'
    }
  },
  sms: {
    welcome: 'Welcome to TigerEx! Your account is now active.',
    deposit: 'Deposit confirmed: {{amount}} {{currency}}',
    withdrawal: 'Withdrawal processed: {{amount}} {{currency}}',
    trade: 'Trade executed: {{type}} {{amount}} {{pair}}',
    security: 'Security alert: {{message}}'
  },
  push: {
    welcome: {
      title: 'Welcome to TigerEx',
      body: 'Your account is now active'
    },
    deposit: {
      title: 'Deposit Confirmed',
      body: 'Your deposit has been confirmed'
    },
    withdrawal: {
      title: 'Withdrawal Processed',
      body: 'Your withdrawal has been processed'
    },
    trade: {
      title: 'Trade Executed',
      body: 'Your order has been executed'
    },
    security: {
      title: 'Security Alert',
      body: 'Important security notification'
    }
  }
};

// Helper function to replace template variables
function replaceTemplateVars(template, data) {
  let result = template;
  for (const [key, value] of Object.entries(data)) {
    result = result.replace(new RegExp(`{{${key}}}`, 'g'), value);
  }
  return result;
}

// Send email notification
async function sendEmail(to, templateName, data = {}) {
  try {
    const template = templates.email[templateName];
    if (!template) {
      throw new Error(`Email template '${templateName}' not found`);
    }

    const mailOptions = {
      from: process.env.SMTP_FROM || 'noreply@tigerex.com',
      to,
      subject: replaceTemplateVars(template.subject, data),
      html: replaceTemplateVars(template.html, data)
    };

    const info = await emailTransporter.sendMail(mailOptions);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error('Email send error:', error);
    return { success: false, error: error.message };
  }
}

// Send SMS notification
async function sendSMS(to, templateName, data = {}) {
  try {
    if (!twilioClient) {
      throw new Error('Twilio not configured');
    }

    const template = templates.sms[templateName];
    if (!template) {
      throw new Error(`SMS template '${templateName}' not found`);
    }

    const message = await twilioClient.messages.create({
      body: replaceTemplateVars(template, data),
      from: process.env.TWILIO_PHONE_NUMBER,
      to
    });

    return { success: true, messageId: message.sid };
  } catch (error) {
    console.error('SMS send error:', error);
    return { success: false, error: error.message };
  }
}

// Send push notification
async function sendPushNotification(token, templateName, data = {}) {
  try {
    if (!admin.apps.length) {
      throw new Error('Firebase not configured');
    }

    const template = templates.push[templateName];
    if (!template) {
      throw new Error(`Push template '${templateName}' not found`);
    }

    const message = {
      notification: {
        title: replaceTemplateVars(template.title, data),
        body: replaceTemplateVars(template.body, data)
      },
      token
    };

    const response = await admin.messaging().send(message);
    return { success: true, messageId: response };
  } catch (error) {
    console.error('Push notification error:', error);
    return { success: false, error: error.message };
  }
}

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'notification-service' });
});

// Send notification (multi-channel)
app.post('/api/notifications/send', async (req, res) => {
  try {
    const { channels, recipient, template, data } = req.body;

    if (!channels || !recipient || !template) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const results = {};

    // Send email
    if (channels.includes('email') && recipient.email) {
      results.email = await sendEmail(recipient.email, template, data);
    }

    // Send SMS
    if (channels.includes('sms') && recipient.phone) {
      results.sms = await sendSMS(recipient.phone, template, data);
    }

    // Send push notification
    if (channels.includes('push') && recipient.pushToken) {
      results.push = await sendPushNotification(recipient.pushToken, template, data);
    }

    res.json({ success: true, results });
  } catch (error) {
    console.error('Notification send error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Send email only
app.post('/api/notifications/email', async (req, res) => {
  try {
    const { to, template, data } = req.body;

    if (!to || !template) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const result = await sendEmail(to, template, data);
    res.json(result);
  } catch (error) {
    console.error('Email notification error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Send SMS only
app.post('/api/notifications/sms', async (req, res) => {
  try {
    const { to, template, data } = req.body;

    if (!to || !template) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const result = await sendSMS(to, template, data);
    res.json(result);
  } catch (error) {
    console.error('SMS notification error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Send push notification only
app.post('/api/notifications/push', async (req, res) => {
  try {
    const { token, template, data } = req.body;

    if (!token || !template) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const result = await sendPushNotification(token, template, data);
    res.json(result);
  } catch (error) {
    console.error('Push notification error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get available templates
app.get('/api/notifications/templates', (req, res) => {
  res.json({
    email: Object.keys(templates.email),
    sms: Object.keys(templates.sms),
    push: Object.keys(templates.push)
  });
});

// Bulk notification
app.post('/api/notifications/bulk', async (req, res) => {
  try {
    const { notifications } = req.body;

    if (!Array.isArray(notifications)) {
      return res.status(400).json({ error: 'notifications must be an array' });
    }

    const results = await Promise.all(
      notifications.map(async (notification) => {
        const { channels, recipient, template, data } = notification;
        const notificationResults = {};

        if (channels.includes('email') && recipient.email) {
          notificationResults.email = await sendEmail(recipient.email, template, data);
        }

        if (channels.includes('sms') && recipient.phone) {
          notificationResults.sms = await sendSMS(recipient.phone, template, data);
        }

        if (channels.includes('push') && recipient.pushToken) {
          notificationResults.push = await sendPushNotification(recipient.pushToken, template, data);
        }

        return notificationResults;
      })
    );

    res.json({ success: true, results });
  } catch (error) {
    console.error('Bulk notification error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Notification Service running on port ${PORT}`);
  console.log(`Email configured: ${!!process.env.SMTP_USER}`);
  console.log(`SMS configured: ${!!twilioClient}`);
  console.log(`Push notifications configured: ${!!admin.apps.length}`);
});

module.exports = app;