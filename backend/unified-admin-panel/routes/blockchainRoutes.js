const express = require('express');
const router = express.Router();
const { authenticateAdmin } = require('../middleware/auth');
const MultiChainDEXService = require('../services/MultiChainDEXService');

// Get supported blockchains
router.get('/', authenticateAdmin, async (req, res) => {
  try {
    const blockchains = [
      { id: 'ethereum', name: 'Ethereum', chainId: 1, type: 'EVM', status: 'ACTIVE' },
      { id: 'bsc', name: 'Binance Smart Chain', chainId: 56, type: 'EVM', status: 'ACTIVE' },
      { id: 'polygon', name: 'Polygon', chainId: 137, type: 'EVM', status: 'ACTIVE' },
      { id: 'avalanche', name: 'Avalanche', chainId: 43114, type: 'EVM', status: 'ACTIVE' },
      { id: 'fantom', name: 'Fantom', chainId: 250, type: 'EVM', status: 'ACTIVE' },
      { id: 'arbitrum', name: 'Arbitrum', chainId: 42161, type: 'EVM', status: 'ACTIVE' },
      { id: 'optimism', name: 'Optimism', chainId: 10, type: 'EVM', status: 'ACTIVE' },
      { id: 'solana', name: 'Solana', chainId: 101, type: 'Non-EVM', status: 'ACTIVE' },
      { id: 'tron', name: 'Tron', chainId: 728126428, type: 'Non-EVM', status: 'ACTIVE' }
    ];
    
    res.json({ blockchains });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Verify token contract
router.post('/verify-token', authenticateAdmin, async (req, res) => {
  try {
    const { blockchain, tokenAddress } = req.body;
    
    const result = await MultiChainDEXService.verifyTokenContract(blockchain, tokenAddress);
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get token balance
router.get('/token-balance', authenticateAdmin, async (req, res) => {
  try {
    const { blockchain, tokenAddress, walletAddress } = req.query;
    
    const balance = await MultiChainDEXService.getTokenBalance(
      blockchain,
      tokenAddress,
      walletAddress
    );
    
    res.json({ balance });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
// TigerEx Wallet API
function createWallet(userId, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';
  return { address, seed: seed.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId };
}
