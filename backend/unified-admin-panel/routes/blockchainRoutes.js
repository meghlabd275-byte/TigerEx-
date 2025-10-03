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