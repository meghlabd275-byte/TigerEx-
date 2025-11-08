import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Dashboard,
  TrendingUp,
  Timeline,
  ContentCopy,
  Link,
  AccountBalance,
  Settings,
  PlayArrow,
  Pause,
  Stop,
  Delete,
  Edit,
  Visibility,
  Add,
  Refresh,
  Download,
  Upload,
  Security,
  Speed,
  People,
  Assessment,
  Notifications,
  Search,
  FilterList,
  MoreVert,
  CheckCircle,
  Warning,
  Error,
  Info,
  Computer,
  Smartphone,
  Tablet,
  Cloud,
  Storage,
  Memory,
  NetworkCheck,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Types for comprehensive desktop admin
interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'active' | 'paused' | 'suspended' | 'delisted';
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  leverage: number;
  marginMode: 'isolated' | 'cross';
  createdAt: string;
  futuresEnabled: boolean;
  marginEnabled: boolean;
  optionsEnabled: boolean;
  gridEnabled: boolean;
  copyEnabled: boolean;
  makerFee: number;
  takerFee: number;
}

interface FuturesContract {
  id: string;
  symbol: string;
  contractType: 'perpetual' | 'deliverable' | 'quarterly' | 'bi_quarterly';
  marginMode: 'isolated' | 'cross';
  leverage: number;
  fundingRate: number;
  nextFundingTime: string;
  openInterest: number;
  markPrice: number;
  indexPrice: number;
  settlementPrice?: number;
  status: 'active' | 'paused' | 'suspended' | 'settling' | 'settled';
  settlementDate?: string;
  maintenanceMargin: number;
  initialMargin: number;
}

interface GridBot {
  id: string;
  userId: string;
  pairSymbol: string;
  gridType: 'arithmetic' | 'geometric' | 'linear' | 'infinite';
  upperPrice: number;
  lowerPrice: number;
  gridCount: number;
  totalInvestment: number;
  currentProfit: number;
  profitPercentage: number;
  status: 'active' | 'paused' | 'stopped' | 'completed' | 'error';
  winRate: number;
  completedGrids: number;
  totalGrids: number;
  runningTime: string;
  lastActivity: string;
  aiOptimized: boolean;
  riskLevel: 'low' | 'medium' | 'high';
}

interface CopyTrader {
  id: string;
  masterTraderId: string;
  masterTraderName: string;
  followerId: string;
  copyMode: 'fixed_amount' | 'percentage' | 'ratio';
  copyAmount: number;
  copyPercentage?: number;
  status: 'active' | 'paused' | 'terminated';
  totalProfit: number;
  totalTrades: number;
  winRate: number;
  profitFactor: number;
  maxDrawdown: number;
  sharpeRatio: number;
  commissionEarned: number;
  followersCount: number;
  avgTradeDuration: string;
  riskScore: 'low' | 'medium' | 'high';
}

interface BlockchainNetwork {
  id: string;
  name: string;
  displayName: string;
  chainId: number;
  rpcUrl: string;
  wsUrl: string;
  blockExplorer: string;
  blockTime: number;
  confirmationBlocks: number;
  status: 'active' | 'inactive' | 'maintenance' | 'deprecated';
  currentBlock: number;
  gasPrice: number;
  networkType: 'EVM' | 'Non-EVM' | 'Layer1' | 'Layer2';
  supportedTokens: string[];
  totalTransactions: number;
  networkHashrate?: number;
  stakingApy?: number;
}

interface SmartContract {
  id: string;
  networkId: string;
  name: string;
  address: string;
  contractType: 'token' | 'dex' | 'bridge' | 'staking' | 'governance' | 'nft';
  version: string;
  deploymentTx: string;
  deploymentBlock: number;
  verified: boolean;
  audited: boolean;
  upgradeable: boolean;
  proxyAddress?: string;
  abiHash: string;
  sourceCodeVerified: boolean;
}

interface IOUContract {
  id: string;
  contractId: string;
  issuerId: string;
  issuerName: string;
  recipientId: string;
  recipientName: string;
  iouType: 'payment' | 'loan' | 'deposit' | 'collateral' | 'escrow';
  amount: number;
  currency: string;
  status: 'pending' | 'active' | 'settled' | 'expired' | 'defaulted' | 'cancelled';
  createdAt: string;
  maturityDate?: string;
  interestRate?: number;
  collateralRequired: boolean;
  collateralAmount?: number;
  collateralCurrency?: string;
  autoSettlement: boolean;
  earlySettlementAllowed: boolean;
  penaltyRate?: number;
  settlementHistory: SettlementRecord[];
}

interface SettlementRecord {
  timestamp: string;
  amount: number;
  type: 'partial' | 'full' | 'penalty';
  transactionHash: string;
}

interface VirtualCoin {
  id: string;
  symbol: string;
  name: string;
  coinType: 'utility' | 'security' | 'stablecoin' | 'governance' | 'nft_backed' | 'asset_backed';
  totalSupply: string;
  circulatingSupply: string;
  maxSupply?: string;
  currentPrice: number;
  marketCap: number;
  status: 'pending' | 'active' | 'suspended' | 'delisted';
  createdAt: string;
  tradingPairs: string[];
  isVirtual: boolean;
  contractAddress?: string;
  decimals: number;
  mintable: boolean;
  burnable: boolean;
  holderCount: number;
  transferEnabled: boolean;
  tradingEnabled: boolean;
  pegAsset?: string;
  backingRatio?: number;
}

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkIn: number;
  networkOut: number;
  activeConnections: number;
  requestRate: number;
  errorRate: number;
  responseTime: number;
  uptime: number;
  lastUpdate: string;
}

interface PlatformStatus {
  webApp: 'operational' | 'degraded' | 'down';
  mobileApp: 'operational' | 'degraded' | 'down';
  desktopApp: 'operational' | 'degraded' | 'down';
  api: 'operational' | 'degraded' | 'down';
  blockchain: 'operational' | 'degraded' | 'down';
  database: 'operational' | 'degraded' | 'down';
  cache: 'operational' | 'degraded' | 'down';
  queue: 'operational' | 'degraded' | 'down';
}

const ComprehensiveDesktopAdminApp: React.FC = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'create' | 'edit' | 'view' | 'delete'>('create');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus | null>(null);

  // State for all components
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [futuresContracts, setFuturesContracts] = useState<FuturesContract[]>([]);
  const [gridBots, setGridBots] = useState<GridBot[]>([]);
  const [copyTraders, setCopyTraders] = useState<CopyTrader[]>([]);
  const [blockchainNetworks, setBlockchainNetworks] = useState<BlockchainNetwork[]>([]);
  const [smartContracts, setSmartContracts] = useState<SmartContract[]>([]);
  const [iouContracts, setIOUContracts] = useState<IOUContract[]>([]);
  const [virtualCoins, setVirtualCoins] = useState<VirtualCoin[]>([]);

  // Form data
  const [formData, setFormData] = useState({
    symbol: '',
    baseAsset: '',
    quoteAsset: 'USDT',
    minPrice: '',
    maxPrice: '',
    tickSize: '',
    stepSize: '',
    minQuantity: '',
    maxQuantity: '',
    leverage: '10',
    makerFee: '0.001',
    takerFee: '0.001',
    enableMargin: false,
    enableFutures: false,
    enableOptions: false,
    enableGrid: false,
    enableCopy: false,
  });

  // Initialize with comprehensive mock data
  useEffect(() => {
    loadComprehensiveData();
    const interval = setInterval(updateMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadComprehensiveData = () => {
    // Trading Pairs
    setTradingPairs([
      {
        id: '1',
        symbol: 'BTC/USDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        status: 'active',
        price: 43250.50,
        change24h: 2.5,
        volume24h: 125000000,
        high24h: 43800,
        low24h: 42500,
        leverage: 125,
        marginMode: 'cross',
        createdAt: '2024-01-15T10:30:00Z',
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: true,
        gridEnabled: true,
        copyEnabled: true,
        makerFee: 0.0005,
        takerFee: 0.001,
      },
      {
        id: '2',
        symbol: 'ETH/USDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        status: 'active',
        price: 2280.75,
        change24h: -1.2,
        volume24h: 87500000,
        high24h: 2350,
        low24h: 2250,
        leverage: 75,
        marginMode: 'isolated',
        createdAt: '2024-01-15T09:45:00Z',
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: true,
        gridEnabled: true,
        copyEnabled: true,
        makerFee: 0.0005,
        takerFee: 0.001,
      },
      {
        id: '3',
        symbol: 'SOL/USDT',
        baseAsset: 'SOL',
        quoteAsset: 'USDT',
        status: 'paused',
        price: 98.45,
        change24h: -3.8,
        volume24h: 45000000,
        high24h: 105,
        low24h: 95,
        leverage: 50,
        marginMode: 'cross',
        createdAt: '2024-01-14T15:20:00Z',
        futuresEnabled: true,
        marginEnabled: false,
        optionsEnabled: false,
        gridEnabled: true,
        copyEnabled: false,
        makerFee: 0.001,
        takerFee: 0.0015,
      },
    ]);

    // Futures Contracts
    setFuturesContracts([
      {
        id: 'f1',
        symbol: 'BTCUSDT-PERP',
        contractType: 'perpetual',
        marginMode: 'cross',
        leverage: 125,
        fundingRate: 0.0001,
        nextFundingTime: '2024-01-15T16:00:00Z',
        openInterest: 250000000,
        markPrice: 43245.25,
        indexPrice: 43250.00,
        status: 'active',
        maintenanceMargin: 0.005,
        initialMargin: 0.01,
      },
      {
        id: 'f2',
        symbol: 'ETHUSDT-PERP',
        contractType: 'perpetual',
        marginMode: 'isolated',
        leverage: 75,
        fundingRate: 0.0002,
        nextFundingTime: '2024-01-15T16:00:00Z',
        openInterest: 180000000,
        markPrice: 2279.50,
        indexPrice: 2280.75,
        status: 'active',
        maintenanceMargin: 0.008,
        initialMargin: 0.015,
      },
      {
        id: 'f3',
        symbol: 'BTCUSDT-Q1-24',
        contractType: 'quarterly',
        marginMode: 'cross',
        leverage: 50,
        fundingRate: 0,
        nextFundingTime: '',
        openInterest: 50000000,
        markPrice: 43100.00,
        indexPrice: 43250.00,
        settlementPrice: 43000.00,
        status: 'active',
        settlementDate: '2024-03-29T08:00:00Z',
        maintenanceMargin: 0.01,
        initialMargin: 0.02,
      },
    ]);

    // Grid Bots
    setGridBots([
      {
        id: 'g1',
        userId: 'user123',
        pairSymbol: 'BTC/USDT',
        gridType: 'arithmetic',
        upperPrice: 45000,
        lowerPrice: 40000,
        gridCount: 50,
        totalInvestment: 10000,
        currentProfit: 450.50,
        profitPercentage: 4.505,
        status: 'active',
        winRate: 68.5,
        completedGrids: 125,
        totalGrids: 50,
        runningTime: '72h 35m',
        lastActivity: '2024-01-15T10:25:00Z',
        aiOptimized: true,
        riskLevel: 'medium',
      },
      {
        id: 'g2',
        userId: 'user456',
        pairSymbol: 'ETH/USDT',
        gridType: 'geometric',
        upperPrice: 2500,
        lowerPrice: 2000,
        gridCount: 25,
        totalInvestment: 5000,
        currentProfit: 225.75,
        profitPercentage: 4.515,
        status: 'active',
        winRate: 72.3,
        completedGrids: 89,
        totalGrids: 25,
        runningTime: '48h 12m',
        lastActivity: '2024-01-15T10:22:00Z',
        aiOptimized: true,
        riskLevel: 'low',
      },
      {
        id: 'g3',
        userId: 'user789',
        pairSymbol: 'SOL/USDT',
        gridType: 'linear',
        upperPrice: 110,
        lowerPrice: 85,
        gridCount: 20,
        totalInvestment: 2500,
        currentProfit: -50.25,
        profitPercentage: -2.01,
        status: 'paused',
        winRate: 45.2,
        completedGrids: 34,
        totalGrids: 20,
        runningTime: '24h 45m',
        lastActivity: '2024-01-15T08:15:00Z',
        aiOptimized: false,
        riskLevel: 'high',
      },
    ]);

    // Copy Traders
    setCopyTraders([
      {
        id: 'c1',
        masterTraderId: 'master001',
        masterTraderName: 'Alpha Trader',
        followerId: 'follower001',
        copyMode: 'percentage',
        copyAmount: 1000,
        copyPercentage: 10,
        status: 'active',
        totalProfit: 1250.75,
        totalTrades: 245,
        winRate: 72.3,
        profitFactor: 1.85,
        maxDrawdown: 15.5,
        sharpeRatio: 2.45,
        commissionEarned: 125.08,
        followersCount: 156,
        avgTradeDuration: '4h 25m',
        riskScore: 'medium',
      },
      {
        id: 'c2',
        masterTraderId: 'master002',
        masterTraderName: 'Beta Master',
        followerId: 'follower002',
        copyMode: 'fixed_amount',
        copyAmount: 500,
        status: 'active',
        totalProfit: 875.50,
        totalTrades: 189,
        winRate: 68.9,
        profitFactor: 1.65,
        maxDrawdown: 12.3,
        sharpeRatio: 1.95,
        commissionEarned: 87.55,
        followersCount: 89,
        avgTradeDuration: '3h 15m',
        riskScore: 'low',
      },
    ]);

    // Blockchain Networks
    setBlockchainNetworks([
      {
        id: 'eth',
        name: 'ethereum',
        displayName: 'Ethereum Mainnet',
        chainId: 1,
        rpcUrl: 'https://mainnet.infura.io/v3/...',
        wsUrl: 'wss://mainnet.infura.io/ws/v3/...',
        blockExplorer: 'https://etherscan.io',
        blockTime: 12,
        confirmationBlocks: 12,
        status: 'active',
        currentBlock: 18543210,
        gasPrice: 25.5,
        networkType: 'EVM',
        supportedTokens: ['ETH', 'USDT', 'USDC', 'WBTC', 'DAI'],
        totalTransactions: 2154321098,
        networkHashrate: 987654321,
      },
      {
        id: 'bsc',
        name: 'bsc',
        displayName: 'Binance Smart Chain',
        chainId: 56,
        rpcUrl: 'https://bsc-dataseed1.binance.org/',
        wsUrl: 'wss://bsc-ws-node.nariox.org:443',
        blockExplorer: 'https://bscscan.com',
        blockTime: 3,
        confirmationBlocks: 10,
        status: 'active',
        currentBlock: 32456789,
        gasPrice: 5.2,
        networkType: 'EVM',
        supportedTokens: ['BNB', 'BUSD', 'USDT', 'USDC', 'CAKE'],
        totalTransactions: 3456789012,
      },
      {
        id: 'polygon',
        name: 'polygon',
        displayName: 'Polygon Mainnet',
        chainId: 137,
        rpcUrl: 'https://polygon-rpc.com',
        wsUrl: 'wss://polygon-rpc.com',
        blockExplorer: 'https://polygonscan.com',
        blockTime: 2,
        confirmationBlocks: 20,
        status: 'active',
        currentBlock: 45678901,
        gasPrice: 30.1,
        networkType: 'Layer2',
        supportedTokens: ['MATIC', 'USDT', 'USDC', 'WMATIC'],
        totalTransactions: 1234567890,
      },
    ]);

    // Smart Contracts
    setSmartContracts([
      {
        id: 'sc1',
        networkId: 'eth',
        name: 'Token Factory',
        address: '0x1234567890123456789012345678901234567890',
        contractType: 'token',
        version: '1.0.0',
        deploymentTx: '0xabcdef...',
        deploymentBlock: 18543000,
        verified: true,
        audited: true,
        upgradeable: true,
        proxyAddress: '0x0987654321098765432109876543210987654321',
        abiHash: 'hash123',
        sourceCodeVerified: true,
      },
    ]);

    // IOU Contracts
    setIOUContracts([
      {
        id: 'iou1',
        contractId: 'iou_contract_001',
        issuerId: 'issuer001',
        issuerName: 'Company A',
        recipientId: 'recipient001',
        recipientName: 'Company B',
        iouType: 'payment',
        amount: 10000,
        currency: 'USDT',
        status: 'active',
        createdAt: '2024-01-01T00:00:00Z',
        maturityDate: '2024-02-15T00:00:00Z',
        collateralRequired: false,
        autoSettlement: true,
        earlySettlementAllowed: true,
        settlementHistory: [],
      },
      {
        id: 'iou2',
        contractId: 'iou_contract_002',
        issuerId: 'issuer002',
        issuerName: 'Company C',
        recipientId: 'recipient002',
        recipientName: 'Company D',
        iouType: 'loan',
        amount: 50000,
        currency: 'USDC',
        status: 'active',
        createdAt: '2024-01-05T00:00:00Z',
        maturityDate: '2024-04-15T00:00:00Z',
        interestRate: 0.05,
        collateralRequired: true,
        collateralAmount: 75000,
        collateralCurrency: 'USDT',
        autoSettlement: true,
        earlySettlementAllowed: true,
        penaltyRate: 0.02,
        settlementHistory: [],
      },
    ]);

    // Virtual Coins
    setVirtualCoins([
      {
        id: 'vc1',
        symbol: 'VTIGER',
        name: 'Virtual Tiger Token',
        coinType: 'utility',
        totalSupply: '1000000000',
        circulatingSupply: '500000000',
        maxSupply: '2000000000',
        currentPrice: 1.25,
        marketCap: 625000000,
        status: 'active',
        createdAt: '2024-01-01T00:00:00Z',
        tradingPairs: ['VTIGER/USDT', 'VTIGER/USDC', 'VTIGER/ETH'],
        isVirtual: true,
        contractAddress: '0xabcdef...',
        decimals: 18,
        mintable: true,
        burnable: true,
        holderCount: 15420,
        transferEnabled: true,
        tradingEnabled: true,
      },
      {
        id: 'vc2',
        symbol: 'VSTABLE',
        name: 'Virtual Stablecoin',
        coinType: 'stablecoin',
        totalSupply: '100000000',
        circulatingSupply: '75000000',
        maxSupply: '500000000',
        currentPrice: 1.00,
        marketCap: 75000000,
        status: 'active',
        createdAt: '2024-01-01T00:00:00Z',
        tradingPairs: ['VSTABLE/USDT', 'VSTABLE/USDC'],
        isVirtual: true,
        contractAddress: '0x123456...',
        decimals: 6,
        mintable: true,
        burnable: false,
        holderCount: 8750,
        transferEnabled: true,
        tradingEnabled: true,
        pegAsset: 'USDT',
        backingRatio: 1.0,
      },
    ]);

    // System Metrics
    setSystemMetrics({
      cpuUsage: 45.2,
      memoryUsage: 62.8,
      diskUsage: 78.5,
      networkIn: 1024.5,
      networkOut: 856.3,
      activeConnections: 1254,
      requestRate: 845.2,
      errorRate: 0.02,
      responseTime: 125.5,
      uptime: 2592000,
      lastUpdate: new Date().toISOString(),
    });

    // Platform Status
    setPlatformStatus({
      webApp: 'operational',
      mobileApp: 'operational',
      desktopApp: 'operational',
      api: 'operational',
      blockchain: 'operational',
      database: 'operational',
      cache: 'operational',
      queue: 'operational',
    });
  };

  const updateMetrics = () => {
    setSystemMetrics(prev => prev ? {
      ...prev,
      cpuUsage: 40 + Math.random() * 20,
      memoryUsage: 55 + Math.random() * 20,
      networkIn: 800 + Math.random() * 400,
      networkOut: 600 + Math.random() * 400,
      requestRate: 700 + Math.random() * 300,
      lastUpdate: new Date().toISOString(),
    } : null);
  };

  // Action handlers
  const handlePairAction = async (pairId: string, action: 'pause' | 'resume' | 'suspend' | 'delete') => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTradingPairs(prev => {
        if (action === 'delete') {
          return prev.filter(pair => pair.id !== pairId);
        }
        return prev.map(pair =>
          pair.id === pairId
            ? { ...pair, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : 'suspended' }
            : pair
        );
      });
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGridBotAction = async (botId: string, action: 'pause' | 'resume' | 'stop' | 'delete') => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setGridBots(prev => {
        if (action === 'delete') {
          return prev.filter(bot => bot.id !== botId);
        }
        return prev.map(bot =>
          bot.id === botId
            ? { ...bot, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : action === 'stop' ? 'stopped' : bot.status }
            : bot
        );
      });
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyTraderAction = async (traderId: string, action: 'pause' | 'resume' | 'terminate') => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setCopyTraders(prev =>
        prev.map(trader =>
          trader.id === traderId
            ? { ...trader, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : 'terminated' }
            : trader
        )
      );
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockchainAction = async (networkId: string, action: 'activate' | 'deactivate' | 'maintenance') => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setBlockchainNetworks(prev =>
        prev.map(network =>
          network.id === networkId
            ? { ...network, status: action === 'activate' ? 'active' : action === 'deactivate' ? 'inactive' : 'maintenance' }
            : network
        )
      );
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTradingPair = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newPair: TradingPair = {
        id: Date.now().toString(),
        symbol: `${formData.baseAsset}/${formData.quoteAsset}`,
        baseAsset: formData.baseAsset,
        quoteAsset: formData.quoteAsset,
        status: 'pending',
        price: 0,
        change24h: 0,
        volume24h: 0,
        high24h: parseFloat(formData.maxPrice),
        low24h: parseFloat(formData.minPrice),
        leverage: parseInt(formData.leverage),
        marginMode: 'isolated',
        createdAt: new Date().toISOString(),
        futuresEnabled: formData.enableFutures,
        marginEnabled: formData.enableMargin,
        optionsEnabled: formData.enableOptions,
        gridEnabled: formData.enableGrid,
        copyEnabled: formData.enableCopy,
        makerFee: parseFloat(formData.makerFee),
        takerFee: parseFloat(formData.takerFee),
      };
      
      setTradingPairs(prev => [newPair, ...prev]);
      setShowDialog(false);
    } catch (error) {
      console.error('Creation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart data generators
  const generateVolumeData = () => [
    { name: '00:00', volume: 120 },
    { name: '04:00', volume: 190 },
    { name: '08:00', volume: 300 },
    { name: '12:00', volume: 500 },
    { name: '16:00', volume: 400 },
    { name: '20:00', volume: 280 },
  ];

  const generateProfitData = () => [
    { name: 'Spot', value: 30, color: '#3B82F6' },
    { name: 'Futures', value: 25, color: '#10B981' },
    { name: 'Grid', value: 20, color: '#F59E0B' },
    { name: 'Copy', value: 15, color: '#8B5CF6' },
    { name: 'Options', value: 7, color: '#EF4444' },
    { name: 'Others', value: 3, color: '#6B7280' },
  ];

  const generatePerformanceData = () => [
    { name: 'CPU', usage: systemMetrics?.cpuUsage || 0 },
    { name: 'Memory', usage: systemMetrics?.memoryUsage || 0 },
    { name: 'Disk', usage: systemMetrics?.diskUsage || 0 },
  ];

  // Navigation items
  const navigationItems = [
    { key: 'overview', label: 'Overview', icon: <Dashboard /> },
    { key: 'spot', label: 'Spot Trading', icon: <TrendingUp /> },
    { key: 'futures', label: 'Futures Trading', icon: <Timeline /> },
    { key: 'grid', label: 'Grid Trading', icon: <AccountBalance /> },
    { key: 'copy', label: 'Copy Trading', icon: <ContentCopy /> },
    { key: 'blockchain', label: 'Blockchain', icon: <Link /> },
    { key: 'smart-contracts', label: 'Smart Contracts', icon: <Security /> },
    { key: 'iou', label: 'IOU System', icon: <AccountBalance /> },
    { key: 'virtual-coins', label: 'Virtual Coins', icon: <AccountBalance /> },
    { key: 'settings', label: 'Settings', icon: <Settings /> },
  ];

  // Render methods
  const renderOverview = () => (
    <Box sx={{ p: 3 }}>
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="overline">
                    Total Volume
                  </Typography>
                  <Typography variant="h4" component="div">
                    $2.4B
                  </Typography>
                  <Typography color="success.main" variant="body2">
                    +12.5%
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: '#3B82F6' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="overline">
                    Active Users
                  </Typography>
                  <Typography variant="h4" component="div">
                    125.4K
                  </Typography>
                  <Typography color="success.main" variant="body2">
                    +8.2%
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, color: '#10B981' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="overline">
                    Open Positions
                  </Typography>
                  <Typography variant="h4" component="div">
                    45.7K
                  </Typography>
                  <Typography color="error.main" variant="body2">
                    -3.1%
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, color: '#F59E0B' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="overline">
                    System Health
                  </Typography>
                  <Typography variant="h4" component="div">
                    99.9%
                  </Typography>
                  <Typography color="success.main" variant="body2">
                    Optimal
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, color: '#8B5CF6' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Volume Chart
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={generateVolumeData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="volume" stroke="#3B82F6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profit Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={generateProfitData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {generateProfitData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Platform Status */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Platform Status
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Computer sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">Desktop App: Operational</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Smartphone sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">Mobile App: Operational</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Tablet sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">Web App: Operational</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Cloud sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">API: Operational</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Storage sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">Database: Operational</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <NetworkCheck sx={{ mr: 1, color: '#10B981' }} />
                    <Typography variant="body2">Network: Operational</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Performance
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={generatePerformanceData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="usage" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderSpotTrading = () => (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Spot Trading Pairs</Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {
              setDialogType('create');
              setShowDialog(true);
            }}
          >
            Create Pair
          </Button>
          <Button startIcon={<Refresh />}>Refresh</Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>24h Change</TableCell>
              <TableCell>Volume</TableCell>
              <TableCell>Leverage</TableCell>
              <TableCell>Features</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tradingPairs.map((pair) => (
              <TableRow key={pair.id}>
                <TableCell>
                  <Typography fontWeight="bold">{pair.symbol}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {pair.baseAsset}/{pair.quoteAsset}
                  </Typography>
                </TableCell>
                <TableCell>${pair.price.toLocaleString()}</TableCell>
                <TableCell>
                  <Chip
                    label={`${pair.change24h >= 0 ? '+' : ''}${pair.change24h}%`}
                    color={pair.change24h >= 0 ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>${(pair.volume24h / 1000000).toFixed(1)}M</TableCell>
                <TableCell>{pair.leverage}x</TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5}>
                    {pair.futuresEnabled && <Chip label="F" size="small" />}
                    {pair.marginEnabled && <Chip label="M" size="small" />}
                    {pair.optionsEnabled && <Chip label="O" size="small" />}
                    {pair.gridEnabled && <Chip label="G" size="small" />}
                    {pair.copyEnabled && <Chip label="C" size="small" />}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={pair.status.toUpperCase()}
                    color={
                      pair.status === 'active' ? 'success' :
                      pair.status === 'paused' ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    {pair.status === 'active' && (
                      <IconButton
                        size="small"
                        onClick={() => handlePairAction(pair.id, 'pause')}
                      >
                        <Pause />
                      </IconButton>
                    )}
                    {pair.status === 'paused' && (
                      <IconButton
                        size="small"
                        onClick={() => handlePairAction(pair.id, 'resume')}
                      >
                        <PlayArrow />
                      </IconButton>
                    )}
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handlePairAction(pair.id, 'delete')}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderGridTrading = () => (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Grid Trading Bots</Typography>
        <Box display="flex" gap={2}>
          <Button variant="contained" startIcon={<Add />}>
            Create Bot
          </Button>
          <Button startIcon={<Refresh />}>Refresh</Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Bot ID</TableCell>
              <TableCell>Pair</TableCell>
              <TableCell>Grid Type</TableCell>
              <TableCell>Investment</TableCell>
              <TableCell>Profit</TableCell>
              <TableCell>Profit %</TableCell>
              <TableCell>Win Rate</TableCell>
              <TableCell>Completed/Total</TableCell>
              <TableCell>AI</TableCell>
              <TableCell>Risk</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {gridBots.map((bot) => (
              <TableRow key={bot.id}>
                <TableCell>
                  <Typography fontWeight="bold">{bot.id}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {bot.runningTime}
                  </Typography>
                </TableCell>
                <TableCell>{bot.pairSymbol}</TableCell>
                <TableCell>
                  <Chip label={bot.gridType} size="small" variant="outlined" />
                </TableCell>
                <TableCell>${bot.totalInvestment.toLocaleString()}</TableCell>
                <TableCell>
                  <Typography
                    color={bot.currentProfit >= 0 ? 'success.main' : 'error.main'}
                    fontWeight="bold"
                  >
                    ${bot.currentProfit.toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${bot.profitPercentage.toFixed(2)}%`}
                    color={bot.profitPercentage >= 0 ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{bot.winRate}%</TableCell>
                <TableCell>
                  {bot.completedGrids}/{bot.totalGrids}
                </TableCell>
                <TableCell>
                  {bot.aiOptimized ? (
                    <Chip
                      label="AI"
                      color="primary"
                      size="small"
                      icon={<Assessment />}
                    />
                  ) : (
                    <Typography variant="caption" color="textSecondary">
                      Manual
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={bot.riskLevel}
                    color={
                      bot.riskLevel === 'low' ? 'success' :
                      bot.riskLevel === 'medium' ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={bot.status.toUpperCase()}
                    color={
                      bot.status === 'active' ? 'success' :
                      bot.status === 'paused' ? 'warning' :
                      bot.status === 'completed' ? 'info' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <IconButton
                      size="small"
                      onClick={() => handleGridBotAction(
                        bot.id,
                        bot.status === 'active' ? 'pause' : 'resume'
                      )}
                    >
                      {bot.status === 'active' ? <Pause /> : <PlayArrow />}
                    </IconButton>
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleGridBotAction(bot.id, 'delete')}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderCreateDialog = () => (
    <Dialog open={showDialog} onClose={() => setShowDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>Create Trading Pair</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Base Asset"
              value={formData.baseAsset}
              onChange={(e) => setFormData({...formData, baseAsset: e.target.value})}
              placeholder="e.g., BTC"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Quote Asset"
              value={formData.quoteAsset}
              onChange={(e) => setFormData({...formData, quoteAsset: e.target.value})}
              placeholder="e.g., USDT"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Minimum Price"
              type="number"
              value={formData.minPrice}
              onChange={(e) => setFormData({...formData, minPrice: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Maximum Price"
              type="number"
              value={formData.maxPrice}
              onChange={(e) => setFormData({...formData, maxPrice: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Leverage"
              type="number"
              value={formData.leverage}
              onChange={(e) => setFormData({...formData, leverage: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Maker Fee"
              type="number"
              value={formData.makerFee}
              onChange={(e) => setFormData({...formData, makerFee: e.target.value})}
            />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Enable Features
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableMargin}
                      onChange={(e) => setFormData({...formData, enableMargin: e.target.checked})}
                    />
                  }
                  label="Margin Trading"
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableFutures}
                      onChange={(e) => setFormData({...formData, enableFutures: e.target.checked})}
                    />
                  }
                  label="Futures Trading"
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableOptions}
                      onChange={(e) => setFormData({...formData, enableOptions: e.target.checked})}
                    />
                  }
                  label="Options Trading"
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableGrid}
                      onChange={(e) => setFormData({...formData, enableGrid: e.target.checked})}
                    />
                  }
                  label="Grid Trading"
                />
              </Grid>
              <Grid item xs={6} sm={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.enableCopy}
                      onChange={(e) => setFormData({...formData, enableCopy: e.target.checked})}
                    />
                  }
                  label="Copy Trading"
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowDialog(false)}>Cancel</Button>
        <Button onClick={handleCreateTradingPair} variant="contained">
          Create Pair
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: 240, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {navigationItems.map((item) => (
              <ListItem
                button
                key={item.key}
                selected={activeSection === item.key}
                onClick={() => setActiveSection(item.key)}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 0 }}>
        {/* AppBar */}
        <AppBar position="static" sx={{ zIndex: 1201 }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              TigerEx Desktop Admin Dashboard
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <IconButton color="inherit">
                <Notifications />
              </IconButton>
              <IconButton color="inherit">
                <Settings />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Content */}
        {activeSection === 'overview' && renderOverview()}
        {activeSection === 'spot' && renderSpotTrading()}
        {activeSection === 'grid' && renderGridTrading()}

        {/* Dialog */}
        {renderCreateDialog()}
      </Box>
    </Box>
  );
};

export default ComprehensiveDesktopAdminApp;