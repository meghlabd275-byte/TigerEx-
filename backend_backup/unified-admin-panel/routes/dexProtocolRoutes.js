const express = require('express');
const router = express.Router();
const DEXProtocol = require('../models/DEXProtocol');
const { authenticateAdmin } = require('../middleware/auth');

// Get all DEX protocols
router.get('/', authenticateAdmin, async (req, res) => {
  try {
    const { blockchain, status } = req.query;
    
    const query = {};
    if (blockchain) query.blockchain = blockchain;
    if (status) query.status = status;
    
    const protocols = await DEXProtocol.find(query).sort({ blockchain: 1, name: 1 });
    res.json(protocols);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get single protocol
router.get('/:id', authenticateAdmin, async (req, res) => {
  try {
    const protocol = await DEXProtocol.findById(req.params.id);
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    res.json(protocol);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create new protocol
router.post('/', authenticateAdmin, async (req, res) => {
  try {
    const protocol = new DEXProtocol(req.body);
    await protocol.save();
    res.status(201).json(protocol);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Update protocol
router.put('/:id', authenticateAdmin, async (req, res) => {
  try {
    const protocol = await DEXProtocol.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    res.json(protocol);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Update protocol status
router.patch('/:id/status', authenticateAdmin, async (req, res) => {
  try {
    const { status } = req.body;
    
    if (!['ACTIVE', 'INACTIVE', 'MAINTENANCE'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }
    
    const protocol = await DEXProtocol.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true }
    );
    
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    res.json(protocol);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete protocol
router.delete('/:id', authenticateAdmin, async (req, res) => {
  try {
    const protocol = await DEXProtocol.findByIdAndDelete(req.params.id);
    
    if (!protocol) {
      return res.status(404).json({ error: 'Protocol not found' });
    }
    
    res.json({ message: 'Protocol deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Initialize default protocols
router.post('/initialize-defaults', authenticateAdmin, async (req, res) => {
  try {
    const defaultProtocols = [
      // Ethereum
      {
        name: 'uniswap-v2',
        displayName: 'Uniswap V2',
        version: 'v2',
        blockchain: 'ethereum',
        chainId: 1,
        contracts: {
          router: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
          factory: '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
          weth: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        },
        api: {
          graphqlEndpoint: 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
        },
        status: 'ACTIVE'
      },
      {
        name: 'uniswap-v3',
        displayName: 'Uniswap V3',
        version: 'v3',
        blockchain: 'ethereum',
        chainId: 1,
        contracts: {
          router: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
          factory: '0x1F98431c8aD98523631AE4a59f267346ea31F984',
          weth: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
        },
        config: {
          feeTiers: [500, 3000, 10000]
        },
        features: {
          supportsV3: true
        },
        status: 'ACTIVE'
      },
      // BSC
      {
        name: 'pancakeswap-v2',
        displayName: 'PancakeSwap V2',
        version: 'v2',
        blockchain: 'bsc',
        chainId: 56,
        contracts: {
          router: '0x10ED43C718714eb63d5aA57B78B54704E256024E',
          factory: '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
          weth: '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'
        },
        api: {
          graphqlEndpoint: 'https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2'
        },
        status: 'ACTIVE'
      },
      // Polygon
      {
        name: 'quickswap',
        displayName: 'QuickSwap',
        version: 'v2',
        blockchain: 'polygon',
        chainId: 137,
        contracts: {
          router: '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
          factory: '0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
          weth: '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
        },
        status: 'ACTIVE'
      },
      // Avalanche
      {
        name: 'traderjoe',
        displayName: 'Trader Joe',
        version: 'v2',
        blockchain: 'avalanche',
        chainId: 43114,
        contracts: {
          router: '0x60aE616a2155Ee3d9A68541Ba4544862310933d4',
          factory: '0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10',
          weth: '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7'
        },
        status: 'ACTIVE'
      },
      // Fantom
      {
        name: 'spookyswap',
        displayName: 'SpookySwap',
        version: 'v2',
        blockchain: 'fantom',
        chainId: 250,
        contracts: {
          router: '0xF491e7B69E4244ad4002BC14e878a34207E38c29',
          factory: '0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3',
          weth: '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83'
        },
        status: 'ACTIVE'
      },
      // Solana
      {
        name: 'raydium',
        displayName: 'Raydium',
        version: 'v4',
        blockchain: 'solana',
        chainId: 101,
        contracts: {
          router: '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',
          factory: '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1'
        },
        status: 'ACTIVE'
      },
      // Tron
      {
        name: 'tronswap',
        displayName: 'TronSwap',
        version: 'v2',
        blockchain: 'tron',
        chainId: 728126428,
        contracts: {
          router: 'TKzxdSv2FZKQrEqkKVgp5DcwEXBEKMg2Ax',
          factory: 'TXk8rQSAvPvBBNtqSoY6nCfsXWCSSpTVQF'
        },
        status: 'ACTIVE'
      }
    ];
    
    const results = [];
    for (const protocolData of defaultProtocols) {
      const existing = await DEXProtocol.findOne({ 
        name: protocolData.name, 
        blockchain: protocolData.blockchain 
      });
      
      if (!existing) {
        const protocol = new DEXProtocol(protocolData);
        await protocol.save();
        results.push(protocol);
      }
    }
    
    res.json({ 
      message: 'Default protocols initialized', 
      count: results.length,
      protocols: results 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;