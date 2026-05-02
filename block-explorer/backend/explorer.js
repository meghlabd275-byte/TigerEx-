/**
 * TigerChain Explorer - Dynamic API Connector
 * Connects to backend block-explorer service
 */
const EXPLORER_API = window.location.port === '3000' || window.location.port === '5173'
  ? 'http://localhost:8000'
  : '/api';

// Block Explorer Service
const ExplorerService = {
  baseURL: EXPLORER_API,

  // Get all blocks
  async getBlocks(limit = 20, offset = 0) {
    const res = await fetch(`${this.baseURL}/api/v1/blocks?limit=${limit}&offset=${offset}`);
    return res.json();
  },

  // Get block by number
  async getBlock(blockNum) {
    const res = await fetch(`${this.baseURL}/api/v1/blocks/${blockNum}`);
    return res.json();
  },

  // Get block by hash
  async getBlockByHash(hash) {
    const res = await fetch(`${this.baseURL}/api/v1/blocks/hash/${hash}`);
    return res.json();
  },

  // Get transactions for block
  async getBlockTransactions(blockNum) {
    const res = await fetch(`${this.baseURL}/api/v1/blocks/${blockNum}/transactions`);
    return res.json();
  },

  // Get transaction by hash
  async getTransaction(txHash) {
    const res = await fetch(`${this.baseURL}/api/v1/transactions/${txHash}`);
    return res.json();
  },

  // Get transactions (paginated)
  async getTransactions(limit = 20, offset = 0) {
    const res = await fetch(`${this.baseURL}/api/v1/transactions?limit=${limit}&offset=${offset}`);
    return res.json();
  },

  // Search (address, tx, block)
  async search(query) {
    const res = await fetch(`${this.baseURL}/api/v1/search?q=${encodeURIComponent(query)}`);
    return res.json();
  },

  // Get address info
  async getAddress(address) {
    const res = await fetch(`${this.baseURL}/api/v1/addresses/${address}`);
    return res.json();
  },

  // Get address transactions
  async getAddressTransactions(address, limit = 20) {
    const res = await fetch(`${this.baseURL}/api/v1/addresses/${address}/transactions?limit=${limit}`);
    return res.json();
  },

  // Get tokens
  async getTokens(limit = 50) {
    const res = await fetch(`${this.baseURL}/api/v1/tokens?limit=${limit}`);
    return res.json();
  },

  // Get token holders
  async getTokenHolders(tokenAddress, limit = 100) {
    const res = await fetch(`${this.baseURL}/api/v1/tokens/${tokenAddress}/holders?limit=${limit}`);
    return res.json();
  },

  // Get NFTs
  async getNFTs(limit = 20) {
    const res = await fetch(`${this.baseURL}/api/v1/nfts?limit=${limit}`);
    return res.json();
  },

  // Get validators
  async getValidators() {
    const res = await fetch(`${this.baseURL}/api/v1/validators`);
    return res.json();
  },

  // Get stats
  async getStats() {
    const res = await fetch(`${this.baseURL}/api/v1/stats`);
    return res.json();
  }
};

// Export
window.ExplorerService = ExplorerService;
console.log('Explorer API connected to backend');
