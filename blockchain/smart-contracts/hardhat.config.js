require('@nomicfoundation/hardhat-toolbox');
require('@nomiclabs/hardhat-etherscan');
require('hardhat-gas-reporter');
require('solidity-coverage');
require('hardhat-deploy');
require('hardhat-contract-sizer');
require('@openzeppelin/hardhat-upgrades');
require('dotenv').config();

const PRIVATE_KEY =
  process.env.PRIVATE_KEY ||
  '0x0000000000000000000000000000000000000000000000000000000000000000';
const INFURA_API_KEY = process.env.INFURA_API_KEY || '';
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || '';
const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY || '';
const BSCSCAN_API_KEY = process.env.BSCSCAN_API_KEY || '';
const COINMARKETCAP_API_KEY = process.env.COINMARKETCAP_API_KEY || '';

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    compilers: [
      {
        version: '0.8.20',
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
          viaIR: true,
        },
      },
      {
        version: '0.8.19',
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    ],
  },

  networks: {
    hardhat: {
      chainId: 31337,
      gas: 12000000,
      blockGasLimit: 12000000,
      allowUnlimitedContractSize: true,
      forking: {
        url: `https://mainnet.infura.io/v3/${INFURA_API_KEY}`,
        enabled: false,
      },
    },

    localhost: {
      url: 'http://127.0.0.1:8545',
      chainId: 31337,
    },

    // Ethereum Networks
    mainnet: {
      url: `https://mainnet.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY],
      chainId: 1,
      gas: 'auto',
      gasPrice: 'auto',
    },

    goerli: {
      url: `https://goerli.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY],
      chainId: 5,
      gas: 'auto',
      gasPrice: 'auto',
    },

    sepolia: {
      url: `https://sepolia.infura.io/v3/${INFURA_API_KEY}`,
      accounts: [PRIVATE_KEY],
      chainId: 11155111,
      gas: 'auto',
      gasPrice: 'auto',
    },

    // Polygon Networks
    polygon: {
      url: 'https://polygon-rpc.com/',
      accounts: [PRIVATE_KEY],
      chainId: 137,
      gas: 'auto',
      gasPrice: 'auto',
    },

    mumbai: {
      url: 'https://rpc-mumbai.maticvigil.com/',
      accounts: [PRIVATE_KEY],
      chainId: 80001,
      gas: 'auto',
      gasPrice: 'auto',
    },

    // BSC Networks
    bsc: {
      url: 'https://bsc-dataseed.binance.org/',
      accounts: [PRIVATE_KEY],
      chainId: 56,
      gas: 'auto',
      gasPrice: 'auto',
    },

    bscTestnet: {
      url: 'https://data-seed-prebsc-1-s1.binance.org:8545/',
      accounts: [PRIVATE_KEY],
      chainId: 97,
      gas: 'auto',
      gasPrice: 'auto',
    },

    // Avalanche Networks
    avalanche: {
      url: 'https://api.avax.network/ext/bc/C/rpc',
      accounts: [PRIVATE_KEY],
      chainId: 43114,
      gas: 'auto',
      gasPrice: 'auto',
    },

    fuji: {
      url: 'https://api.avax-test.network/ext/bc/C/rpc',
      accounts: [PRIVATE_KEY],
      chainId: 43113,
      gas: 'auto',
      gasPrice: 'auto',
    },

    // Arbitrum Networks
    arbitrum: {
      url: 'https://arb1.arbitrum.io/rpc',
      accounts: [PRIVATE_KEY],
      chainId: 42161,
      gas: 'auto',
      gasPrice: 'auto',
    },

    arbitrumGoerli: {
      url: 'https://goerli-rollup.arbitrum.io/rpc',
      accounts: [PRIVATE_KEY],
      chainId: 421613,
      gas: 'auto',
      gasPrice: 'auto',
    },

    // Optimism Networks
    optimism: {
      url: 'https://mainnet.optimism.io',
      accounts: [PRIVATE_KEY],
      chainId: 10,
      gas: 'auto',
      gasPrice: 'auto',
    },

    optimismGoerli: {
      url: 'https://goerli.optimism.io',
      accounts: [PRIVATE_KEY],
      chainId: 420,
      gas: 'auto',
      gasPrice: 'auto',
    },
  },

  etherscan: {
    apiKey: {
      mainnet: ETHERSCAN_API_KEY,
      goerli: ETHERSCAN_API_KEY,
      sepolia: ETHERSCAN_API_KEY,
      polygon: POLYGONSCAN_API_KEY,
      polygonMumbai: POLYGONSCAN_API_KEY,
      bsc: BSCSCAN_API_KEY,
      bscTestnet: BSCSCAN_API_KEY,
    },
  },

  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: 'USD',
    coinmarketcap: COINMARKETCAP_API_KEY,
    gasPrice: 20,
    showTimeSpent: true,
    showMethodSig: true,
    maxMethodDiff: 10,
  },

  contractSizer: {
    alphaSort: true,
    disambiguatePaths: false,
    runOnCompile: true,
    strict: true,
  },

  namedAccounts: {
    deployer: {
      default: 0,
    },
    admin: {
      default: 1,
    },
    treasury: {
      default: 2,
    },
    user1: {
      default: 3,
    },
    user2: {
      default: 4,
    },
  },

  mocha: {
    timeout: 300000, // 5 minutes
  },

  paths: {
    sources: './contracts',
    tests: './test',
    cache: './cache',
    artifacts: './artifacts',
    deploy: './deploy',
  },
};
