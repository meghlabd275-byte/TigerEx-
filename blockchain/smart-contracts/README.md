# TigerEx Smart Contracts

Hardhat project for TigerEx smart contracts.

## Networks

- `localhost` - Local hardhat node
- `mainnet` - Ethereum mainnet
- `sepolia` - Sepolia testnet
- `polygon` - Polygon mainnet
- `bsc` - Binance Smart Chain

## Commands

```bash
# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to localhost
npx hardhat run scripts/deploy.js --network localhost

# Deploy to testnet
npx hardhat run scripts/deploy.js --network sepolia

# Verify on Etherscan
npx hardhat verify --network sepolia <address>
```

## Contracts

- `TigerExTrading` - Main trading contract
- `TradingEngine` - Order processing engine
- `AdminController` - Admin functions

## Security

This project uses:
- OpenZeppelin contracts
- ReentrancyGuard
- Pausable
- AccessControl