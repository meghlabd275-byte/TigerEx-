const express = require('express');
const router = express.Router();
const { authenticateAdmin } = require('../middleware/auth');
const MultiChainDEXService = require('../services/MultiChainDEXService');
const DEXProtocol = require('../models/DEXProtocol');

// Get all liquidity pools
router.get('/pools', authenticateAdmin, async (req, res) => {
  try {
    const { blockchain, protocol, status } = req.query;
    
    // Query pools from database or blockchain
    const pools = []; // Implement pool fetching logic
    
    res.json({ pools });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create liquidity pool
router.post('/pools/create', authenticateAdmin, async (req, res) => {
  try {
    const { protocolId, token0, token1, amount0, amount1, userWallet } = req.body;
    
    const protocol = await DEXProtocol.findById(protocolId);
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    const result = await MultiChainDEXService.createLiquidityPool(
      protocol,
      token0,
      token1,
      amount0,
      amount1,
      userWallet
    );
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add liquidity
router.post('/pools/:poolAddress/add', authenticateAdmin, async (req, res) => {
  try {
    const { poolAddress } = req.params;
    const { protocolId, token0, token1, amount0, amount1, userWallet } = req.body;
    
    const protocol = await DEXProtocol.findById(protocolId);
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    const result = await MultiChainDEXService.addLiquidity(
      protocol,
      poolAddress,
      token0,
      token1,
      amount0,
      amount1,
      userWallet
    );
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Remove liquidity
router.post('/pools/:poolAddress/remove', authenticateAdmin, async (req, res) => {
  try {
    const { poolAddress } = req.params;
    const { protocolId, lpTokenAmount, userWallet } = req.body;
    
    const protocol = await DEXProtocol.findById(protocolId);
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    const result = await MultiChainDEXService.removeLiquidity(
      protocol,
      poolAddress,
      lpTokenAmount,
      userWallet
    );
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get pool info
router.get('/pools/:poolAddress', authenticateAdmin, async (req, res) => {
  try {
    const { poolAddress } = req.params;
    const { protocolId } = req.query;
    
    const protocol = await DEXProtocol.findById(protocolId);
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    const poolInfo = await MultiChainDEXService.getPoolInfo(protocol, poolAddress);
    
    res.json(poolInfo);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;