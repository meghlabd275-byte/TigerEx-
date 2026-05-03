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

module.exports = app;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
