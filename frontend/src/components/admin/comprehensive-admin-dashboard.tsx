import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
import {
  TrendingUp,
  TrendingDown,
  Pause,
  Play,
  Square,
  Settings,
  Plus,
  Edit,
  Trash2,
  Eye,
  Download,
  Upload,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  DollarSign,
  Activity,
  Zap,
  Shield,
  Globe,
  Coins,
  Layers,
  Network,
  Lock,
  Unlock,
  Smartphone,
  Monitor,
  Tablet,
} from 'lucide-react';

// Types for comprehensive admin system
interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'active' | 'paused' | 'suspended';
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
}

interface FuturesContract {
  id: string;
  symbol: string;
  contractType: 'perpetual' | 'deliverable';
  marginMode: 'isolated' | 'cross';
  leverage: number;
  fundingRate: number;
  openInterest: number;
  markPrice: number;
  indexPrice: number;
  status: 'active' | 'paused' | 'suspended';
  settlementDate?: string;
}

interface GridBot {
  id: string;
  userId: string;
  pairSymbol: string;
  gridType: 'arithmetic' | 'geometric' | 'linear';
  upperPrice: number;
  lowerPrice: number;
  gridCount: number;
  totalInvestment: number;
  currentProfit: number;
  status: 'active' | 'paused' | 'stopped' | 'completed';
  winRate: number;
  completedGrids: number;
  runningTime: string;
  aiOptimized: boolean;
}

interface CopyTrader {
  id: string;
  masterTraderId: string;
  followerId: string;
  copyMode: 'fixed_amount' | 'percentage' | 'ratio';
  copyAmount: number;
  status: 'active' | 'paused' | 'terminated';
  totalProfit: number;
  totalTrades: number;
  winRate: number;
  commissionEarned: number;
  followersCount: number;
}

interface BlockchainNetwork {
  id: string;
  name: string;
  chainId: number;
  rpcUrl: string;
  blockTime: number;
  status: 'active' | 'inactive' | 'maintenance';
  currentBlock: number;
  gasPrice: number;
  networkType: 'EVM' | 'Non-EVM';
  supportedTokens: string[];
}

interface IOUContract {
  id: string;
  issuerId: string;
  recipientId: string;
  iouType: 'payment' | 'loan' | 'deposit';
  amount: number;
  currency: string;
  status: 'pending' | 'active' | 'settled' | 'expired';
  maturityDate?: string;
  interestRate?: number;
}

interface VirtualCoin {
  id: string;
  symbol: string;
  name: string;
  coinType: 'utility' | 'security' | 'stablecoin';
  totalSupply: string;
  circulatingSupply: string;
  currentPrice: number;
  status: 'pending' | 'active' | 'delisted';
  tradingPairs: string[];
  isVirtual: boolean;
}

const ComprehensiveAdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // State for all trading components
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [futuresContracts, setFuturesContracts] = useState<FuturesContract[]>([]);
  const [gridBots, setGridBots] = useState<GridBot[]>([]);
  const [copyTraders, setCopyTraders] = useState<CopyTrader[]>([]);
  const [blockchainNetworks, setBlockchainNetworks] = useState<BlockchainNetwork[]>([]);
  const [iouContracts, setIOUContracts] = useState<IOUContract[]>([]);
  const [virtualCoins, setVirtualCoins] = useState<VirtualCoin[]>([]);

  // Mock comprehensive data
  useEffect(() => {
    // Initialize with comprehensive mock data
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
      },
    ]);

    setFuturesContracts([
      {
        id: 'f1',
        symbol: 'BTCUSDT-PERP',
        contractType: 'perpetual',
        marginMode: 'cross',
        leverage: 125,
        fundingRate: 0.0001,
        openInterest: 250000000,
        markPrice: 43245.25,
        indexPrice: 43250.00,
        status: 'active',
      },
      {
        id: 'f2',
        symbol: 'ETHUSDT-PERP',
        contractType: 'perpetual',
        marginMode: 'isolated',
        leverage: 75,
        fundingRate: 0.0002,
        openInterest: 180000000,
        markPrice: 2279.50,
        indexPrice: 2280.75,
        status: 'active',
      },
      {
        id: 'f3',
        symbol: 'BTCUSDT-Q1-24',
        contractType: 'deliverable',
        marginMode: 'cross',
        leverage: 50,
        fundingRate: 0,
        openInterest: 50000000,
        markPrice: 43100.00,
        indexPrice: 43250.00,
        status: 'active',
        settlementDate: '2024-03-29T08:00:00Z',
      },
    ]);

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
        status: 'active',
        winRate: 68.5,
        completedGrids: 125,
        runningTime: '72h 35m',
        aiOptimized: true,
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
        status: 'active',
        winRate: 72.3,
        completedGrids: 89,
        runningTime: '48h 12m',
        aiOptimized: true,
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
        status: 'paused',
        winRate: 45.2,
        completedGrids: 34,
        runningTime: '24h 45m',
        aiOptimized: false,
      },
    ]);

    setCopyTraders([
      {
        id: 'c1',
        masterTraderId: 'master001',
        followerId: 'follower001',
        copyMode: 'percentage',
        copyAmount: 1000,
        status: 'active',
        totalProfit: 1250.75,
        totalTrades: 245,
        winRate: 72.3,
        commissionEarned: 125.08,
        followersCount: 156,
      },
      {
        id: 'c2',
        masterTraderId: 'master002',
        followerId: 'follower002',
        copyMode: 'fixed_amount',
        copyAmount: 500,
        status: 'active',
        totalProfit: 875.50,
        totalTrades: 189,
        winRate: 68.9,
        commissionEarned: 87.55,
        followersCount: 89,
      },
    ]);

    setBlockchainNetworks([
      {
        id: 'eth',
        name: 'Ethereum Mainnet',
        chainId: 1,
        rpcUrl: 'https://mainnet.infura.io/v3/...',
        blockTime: 12,
        status: 'active',
        currentBlock: 18543210,
        gasPrice: 25.5,
        networkType: 'EVM',
        supportedTokens: ['ETH', 'USDT', 'USDC', 'WBTC'],
      },
      {
        id: 'bsc',
        name: 'Binance Smart Chain',
        chainId: 56,
        rpcUrl: 'https://bsc-dataseed1.binance.org/',
        blockTime: 3,
        status: 'active',
        currentBlock: 32456789,
        gasPrice: 5.2,
        networkType: 'EVM',
        supportedTokens: ['BNB', 'BUSD', 'USDT', 'USDC'],
      },
      {
        id: 'polygon',
        name: 'Polygon Mainnet',
        chainId: 137,
        rpcUrl: 'https://polygon-rpc.com',
        blockTime: 2,
        status: 'active',
        currentBlock: 45678901,
        gasPrice: 30.1,
        networkType: 'EVM',
        supportedTokens: ['MATIC', 'USDT', 'USDC', 'WMATIC'],
      },
    ]);

    setIOUContracts([
      {
        id: 'iou1',
        issuerId: 'issuer001',
        recipientId: 'recipient001',
        iouType: 'payment',
        amount: 10000,
        currency: 'USDT',
        status: 'active',
        maturityDate: '2024-02-15T00:00:00Z',
      },
      {
        id: 'iou2',
        issuerId: 'issuer002',
        recipientId: 'recipient002',
        iouType: 'loan',
        amount: 50000,
        currency: 'USDC',
        status: 'active',
        maturityDate: '2024-04-15T00:00:00Z',
        interestRate: 0.05,
      },
    ]);

    setVirtualCoins([
      {
        id: 'vc1',
        symbol: 'VTIGER',
        name: 'Virtual Tiger Token',
        coinType: 'utility',
        totalSupply: '1000000000',
        circulatingSupply: '500000000',
        currentPrice: 1.25,
        status: 'active',
        tradingPairs: ['VTIGER/USDT', 'VTIGER/USDC'],
        isVirtual: true,
      },
      {
        id: 'vc2',
        symbol: 'VSTABLE',
        name: 'Virtual Stablecoin',
        coinType: 'stablecoin',
        totalSupply: '100000000',
        circulatingSupply: '75000000',
        currentPrice: 1.00,
        status: 'active',
        tradingPairs: ['VSTABLE/USDT'],
        isVirtual: true,
      },
    ]);
  }, []);

  // Action handlers
  const handlePairAction = async (pairId: string, action: 'pause' | 'resume' | 'suspend' | 'delete') => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTradingPairs(prev =>
        prev.map(pair =>
          pair.id === pairId
            ? { ...pair, status: action === 'pause' ? 'paused' : action === 'resume' ? 'active' : action === 'suspend' ? 'suspended' : pair.status }
            : pair
        )
      );
      
      // Remove if delete action
      if (action === 'delete') {
        setTradingPairs(prev => prev.filter(pair => pair.id !== pairId));
      }
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContractAction = async (contractId: string, action: string) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setFuturesContracts(prev =>
        prev.map(contract =>
          contract.id === contractId
            ? { ...contract, status: action as any }
            : contract
        )
      );
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGridBotAction = async (botId: string, action: string) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setGridBots(prev =>
        prev.map(bot =>
          bot.id === botId
            ? { ...bot, status: action as any }
            : bot
        )
      );
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Chart data generators
  const generateVolumeData = () => ({
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [{
      label: 'Trading Volume',
      data: [120, 190, 300, 500, 200, 300],
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
    }],
  });

  const generateProfitData = () => ({
    labels: ['Spot', 'Futures', 'Grid', 'Copy', 'Options', 'Others'],
    datasets: [{
      data: [30, 25, 20, 15, 7, 3],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#6B7280'],
    }],
  });

  // Render methods
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Volume</p>
                <p className="text-2xl font-bold">$2.4B</p>
                <p className="text-sm text-green-600">+12.5%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold">125.4K</p>
                <p className="text-sm text-green-600">+8.2%</p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Open Positions</p>
                <p className="text-2xl font-bold">45.7K</p>
                <p className="text-sm text-red-600">-3.1%</p>
              </div>
              <Activity className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-2xl font-bold">99.9%</p>
                <p className="text-sm text-green-600">Optimal</p>
              </div>
              <Shield className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Volume Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateVolumeData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="labels" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="volume" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Profit Distribution</CardTitle>
          </CardHeader>
          <CardContent>
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
                  dataKey="data"
                >
                  {generateProfitData().datasets[0].data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={generateProfitData().datasets[0].backgroundColor[index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Platform Status */}
      <Card>
        <CardHeader>
          <CardTitle>Platform Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Smartphone className="h-5 w-5 text-green-600" />
              <span className="text-sm">Mobile App: Operational</span>
            </div>
            <div className="flex items-center space-x-2">
              <Monitor className="h-5 w-5 text-green-600" />
              <span className="text-sm">Desktop App: Operational</span>
            </div>
            <div className="flex items-center space-x-2">
              <Tablet className="h-5 w-5 text-green-600" />
              <span className="text-sm">Web App: Operational</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSpotTrading = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Spot Trading Pairs</h2>
        <div className="flex space-x-2">
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Pair
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>24h Change</TableHead>
                <TableHead>Volume</TableHead>
                <TableHead>Leverage</TableHead>
                <TableHead>Features</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tradingPairs.map((pair) => (
                <TableRow key={pair.id}>
                  <TableCell className="font-medium">{pair.symbol}</TableCell>
                  <TableCell>${pair.price.toLocaleString()}</TableCell>
                  <TableCell className={pair.change24h >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {pair.change24h >= 0 ? '+' : ''}{pair.change24h}%
                  </TableCell>
                  <TableCell>${(pair.volume24h / 1000000).toFixed(1)}M</TableCell>
                  <TableCell>{pair.leverage}x</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {pair.futuresEnabled && <Badge variant="secondary">F</Badge>}
                      {pair.marginEnabled && <Badge variant="secondary">M</Badge>}
                      {pair.optionsEnabled && <Badge variant="secondary">O</Badge>}
                      {pair.gridEnabled && <Badge variant="secondary">G</Badge>}
                      {pair.copyEnabled && <Badge variant="secondary">C</Badge>}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        pair.status === 'active' ? 'default' :
                        pair.status === 'paused' ? 'secondary' : 'destructive'
                      }
                    >
                      {pair.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {pair.status === 'active' && (
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handlePairAction(pair.id, 'pause')}
                        >
                          <Pause className="h-3 w-3" />
                        </Button>
                      )}
                      {pair.status === 'paused' && (
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handlePairAction(pair.id, 'resume')}
                        >
                          <Play className="h-3 w-3" />
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        onClick={() => handlePairAction(pair.id, 'delete')}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderFuturesTrading = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Futures Contracts</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Contract
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Margin Mode</TableHead>
                <TableHead>Leverage</TableHead>
                <TableHead>Funding Rate</TableHead>
                <TableHead>Open Interest</TableHead>
                <TableHead>Mark Price</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {futuresContracts.map((contract) => (
                <TableRow key={contract.id}>
                  <TableCell className="font-medium">{contract.symbol}</TableCell>
                  <TableCell>{contract.contractType}</TableCell>
                  <TableCell>{contract.marginMode}</TableCell>
                  <TableCell>{contract.leverage}x</TableCell>
                  <TableCell>{(contract.fundingRate * 100).toFixed(4)}%</TableCell>
                  <TableCell>${(contract.openInterest / 1000000).toFixed(1)}M</TableCell>
                  <TableCell>${contract.markPrice.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        contract.status === 'active' ? 'default' :
                        contract.status === 'paused' ? 'secondary' : 'destructive'
                      }
                    >
                      {contract.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        onClick={() => handleContractAction(contract.id, 'suspend')}
                      >
                        <Square className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderGridTrading = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Grid Trading Bots</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Bot
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Bot ID</TableHead>
                <TableHead>Pair</TableHead>
                <TableHead>Grid Type</TableHead>
                <TableHead>Investment</TableHead>
                <TableHead>Profit</TableHead>
                <TableHead>Win Rate</TableHead>
                <TableHead>Grids</TableHead>
                <TableHead>AI</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {gridBots.map((bot) => (
                <TableRow key={bot.id}>
                  <TableCell className="font-medium">{bot.id}</TableCell>
                  <TableCell>{bot.pairSymbol}</TableCell>
                  <TableCell>{bot.gridType}</TableCell>
                  <TableCell>${bot.totalInvestment.toLocaleString()}</TableCell>
                  <TableCell className={bot.currentProfit >= 0 ? 'text-green-600' : 'text-red-600'}>
                    ${bot.currentProfit.toFixed(2)}
                  </TableCell>
                  <TableCell>{bot.winRate}%</TableCell>
                  <TableCell>{bot.completedGrids}</TableCell>
                  <TableCell>
                    {bot.aiOptimized ? (
                      <Zap className="h-4 w-4 text-yellow-600" />
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        bot.status === 'active' ? 'default' :
                        bot.status === 'paused' ? 'secondary' : 
                        bot.status === 'completed' ? 'default' : 'destructive'
                      }
                    >
                      {bot.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleGridBotAction(bot.id, bot.status === 'active' ? 'pause' : 'resume')}
                      >
                        {bot.status === 'active' ? (
                          <Pause className="h-3 w-3" />
                        ) : (
                          <Play className="h-3 w-3" />
                        )}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderCopyTrading = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Copy Trading</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Master Trader
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Master Trader</TableHead>
                <TableHead>Followers</TableHead>
                <TableHead>Copy Mode</TableHead>
                <TableHead>Copy Amount</TableHead>
                <TableHead>Total Profit</TableHead>
                <TableHead>Win Rate</TableHead>
                <TableHead>Commission</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {copyTraders.map((trader) => (
                <TableRow key={trader.id}>
                  <TableCell className="font-medium">{trader.masterTraderId}</TableCell>
                  <TableCell>{trader.followersCount}</TableCell>
                  <TableCell>{trader.copyMode}</TableCell>
                  <TableCell>${trader.copyAmount.toLocaleString()}</TableCell>
                  <TableCell className="text-green-600">
                    ${trader.totalProfit.toFixed(2)}
                  </TableCell>
                  <TableCell>{trader.winRate}%</TableCell>
                  <TableCell>${trader.commissionEarned.toFixed(2)}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        trader.status === 'active' ? 'default' :
                        trader.status === 'paused' ? 'secondary' : 'destructive'
                      }
                    >
                      {trader.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderBlockchain = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Blockchain Networks</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Network
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Network</TableHead>
                <TableHead>Chain ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Current Block</TableHead>
                <TableHead>Gas Price</TableHead>
                <TableHead>Block Time</TableHead>
                <TableHead>Supported Tokens</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {blockchainNetworks.map((network) => (
                <TableRow key={network.id}>
                  <TableCell className="font-medium">{network.name}</TableCell>
                  <TableCell>{network.chainId}</TableCell>
                  <TableCell>{network.networkType}</TableCell>
                  <TableCell>{network.currentBlock.toLocaleString()}</TableCell>
                  <TableCell>{network.gasPrice} Gwei</TableCell>
                  <TableCell>{network.blockTime}s</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {network.supportedTokens.slice(0, 3).map((token, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {token}
                        </Badge>
                      ))}
                      {network.supportedTokens.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{network.supportedTokens.length - 3}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        network.status === 'active' ? 'default' :
                        network.status === 'inactive' ? 'secondary' : 'destructive'
                      }
                    >
                      {network.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderIOUSystem = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">IOU Contracts</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create IOU
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>IOU ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Currency</TableHead>
                <TableHead>Issuer</TableHead>
                <TableHead>Recipient</TableHead>
                <TableHead>Maturity Date</TableHead>
                <TableHead>Interest Rate</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {iouContracts.map((iou) => (
                <TableRow key={iou.id}>
                  <TableCell className="font-medium">{iou.id}</TableCell>
                  <TableCell>{iou.iouType}</TableCell>
                  <TableCell>${iou.amount.toLocaleString()}</TableCell>
                  <TableCell>{iou.currency}</TableCell>
                  <TableCell>{iou.issuerId}</TableCell>
                  <TableCell>{iou.recipientId}</TableCell>
                  <TableCell>{iou.maturityDate ? new Date(iou.maturityDate).toLocaleDateString() : '-'}</TableCell>
                  <TableCell>{iou.interestRate ? `${(iou.interestRate * 100).toFixed(2)}%` : '-'}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        iou.status === 'active' ? 'default' :
                        iou.status === 'pending' ? 'secondary' : 
                        iou.status === 'settled' ? 'default' : 'destructive'
                      }
                    >
                      {iou.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  const renderVirtualCoins = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Virtual Coins</h2>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Virtual Coin
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Current Price</TableHead>
                <TableHead>Total Supply</TableHead>
                <TableHead>Circulating Supply</TableHead>
                <TableHead>Trading Pairs</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {virtualCoins.map((coin) => (
                <TableRow key={coin.id}>
                  <TableCell className="font-medium">{coin.symbol}</TableCell>
                  <TableCell>{coin.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{coin.coinType}</Badge>
                  </TableCell>
                  <TableCell>${coin.currentPrice.toFixed(2)}</TableCell>
                  <TableCell>{parseInt(coin.totalSupply).toLocaleString()}</TableCell>
                  <TableCell>{parseInt(coin.circulatingSupply).toLocaleString()}</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {coin.tradingPairs.slice(0, 2).map((pair, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {pair}
                        </Badge>
                      ))}
                      {coin.tradingPairs.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{coin.tradingPairs.length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        coin.status === 'active' ? 'default' :
                        coin.status === 'pending' ? 'secondary' : 'destructive'
                      }
                    >
                      {coin.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button size="sm" variant="outline">
                        <Settings className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            TigerEx Comprehensive Admin Dashboard
          </h1>
          <p className="text-gray-600">
            Complete management for all trading systems and blockchain integration
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="spot">Spot Trading</TabsTrigger>
            <TabsTrigger value="futures">Futures</TabsTrigger>
            <TabsTrigger value="grid">Grid Trading</TabsTrigger>
            <TabsTrigger value="copy">Copy Trading</TabsTrigger>
            <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
            <TabsTrigger value="iou">IOU System</TabsTrigger>
            <TabsTrigger value="virtual">Virtual Coins</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            {renderOverview()}
          </TabsContent>

          <TabsContent value="spot">
            {renderSpotTrading()}
          </TabsContent>

          <TabsContent value="futures">
            {renderFuturesTrading()}
          </TabsContent>

          <TabsContent value="grid">
            {renderGridTrading()}
          </TabsContent>

          <TabsContent value="copy">
            {renderCopyTrading()}
          </TabsContent>

          <TabsContent value="blockchain">
            {renderBlockchain()}
          </TabsContent>

          <TabsContent value="iou">
            {renderIOUSystem()}
          </TabsContent>

          <TabsContent value="virtual">
            {renderVirtualCoins()}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ComprehensiveAdminDashboard;