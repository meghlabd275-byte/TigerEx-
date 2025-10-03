const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/tigerex-admin', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Routes
app.use('/api/admin/listings', require('./routes/listingRoutes'));
app.use('/api/admin/liquidity', require('./routes/liquidityRoutes'));
app.use('/api/admin/users', require('./routes/userRoutes'));
app.use('/api/admin/trading-pairs', require('./routes/tradingPairRoutes'));
app.use('/api/admin/dex-protocols', require('./routes/dexProtocolRoutes'));
app.use('/api/admin/blockchain', require('./routes/blockchainRoutes'));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'unified-admin-panel' });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Unified Admin Panel running on port ${PORT}`);
});

module.exports = app;