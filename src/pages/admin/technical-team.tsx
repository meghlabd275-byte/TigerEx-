import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  Server, 
  Database, 
  Code, 
  GitBranch,
  Search,
  Plus,
  Eye,
  Edit,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Cpu,
  HardDrive,
  Network,
  Shield,
  Zap,
  Settings,
  Terminal,
  Globe
} from 'lucide-react';

interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'active' | 'inactive' | 'maintenance';
  volume24h: number;
  price: number;
  change24h: number;
  createdAt: string;
  lastUpdated: string;
}

interface SystemService {
  id: string;
  name: string;
  type: 'microservice' | 'database' | 'cache' | 'queue' | 'gateway';
  status: 'running' | 'stopped' | 'error' | 'maintenance';
  port: number;
  cpu: number;
  memory: number;
  uptime: string;
  version: string;
  lastDeployment: string;
}

interface BlockchainNetwork {
  id: string;
  name: string;
  symbol: string;
  type: 'mainnet' | 'testnet';
  status: 'connected' | 'disconnected' | 'syncing' | 'error';
  blockHeight: number;
  nodeCount: number;
  gasPrice: number;
  lastSync: string;
  rpcEndpoint: string;
}

interface TokenListing {
  id: string;
  tokenName: string;
  symbol: string;
  contractAddress: string;
  blockchain: string;
  status: 'pending' | 'approved' | 'rejected' | 'deployed';
  submittedBy: string;
  submittedAt: string;
  reviewedBy?: string;
  reviewedAt?: string;
  deploymentTx?: string;
}

const TechnicalTeamDashboard: React.FC = () => {
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [services, setServices] = useState<SystemService[]>([]);
  const [blockchains, setBlockchains] = useState<BlockchainNetwork[]>([]);
  const [tokenListings, setTokenListings] = useState<TokenListing[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Mock trading pairs data
    const mockTradingPairs: TradingPair[] = [
      {
        id: 'pair-001',
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        status: 'active',
        volume24h: 1234567.89,
        price: 45234.56,
        change24h: 2.34,
        createdAt: '2023-01-15T00:00:00Z',
        lastUpdated: '2024-01-15T10:30:00Z'
      },
      {
        id: 'pair-002',
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        status: 'active',
        volume24h: 987654.32,
        price: 2834.12,
        change24h: -1.23,
        createdAt: '2023-01-15T00:00:00Z',
        lastUpdated: '2024-01-15T10:25:00Z'
      },
      {
        id: 'pair-003',
        symbol: 'ADAUSDT',
        baseAsset: 'ADA',
        quoteAsset: 'USDT',
        status: 'maintenance',
        volume24h: 456789.12,
        price: 0.4567,
        change24h: 5.67,
        createdAt: '2023-02-01T00:00:00Z',
        lastUpdated: '2024-01-15T09:15:00Z'
      }
    ];

    const mockServices: SystemService[] = [
      {
        id: 'service-001',
        name: 'API Gateway',
        type: 'gateway',
        status: 'running',
        port: 8080,
        cpu: 45.2,
        memory: 67.8,
        uptime: '15d 4h 23m',
        version: 'v2.1.3',
        lastDeployment: '2024-01-10T14:30:00Z'
      },
      {
        id: 'service-002',
        name: 'Matching Engine',
        type: 'microservice',
        status: 'running',
        port: 8081,
        cpu: 78.9,
        memory: 89.1,
        uptime: '12d 8h 45m',
        version: 'v3.2.1',
        lastDeployment: '2024-01-12T09:15:00Z'
      },
      {
        id: 'service-003',
        name: 'PostgreSQL Primary',
        type: 'database',
        status: 'running',
        port: 5432,
        cpu: 34.5,
        memory: 76.3,
        uptime: '25d 12h 18m',
        version: 'v14.9',
        lastDeployment: '2023-12-20T16:45:00Z'
      },
      {
        id: 'service-004',
        name: 'Redis Cache',
        type: 'cache',
        status: 'error',
        port: 6379,
        cpu: 12.3,
        memory: 45.6,
        uptime: '2h 15m',
        version: 'v7.0.5',
        lastDeployment: '2024-01-15T08:00:00Z'
      }
    ];

    const mockBlockchains: BlockchainNetwork[] = [
      {
        id: 'blockchain-001',
        name: 'Ethereum',
        symbol: 'ETH',
        type: 'mainnet',
        status: 'connected',
        blockHeight: 18750234,
        nodeCount: 3,
        gasPrice: 25.5,
        lastSync: '2024-01-15T10:30:00Z',
        rpcEndpoint: 'https://mainnet.infura.io/v3/...'
      },
      {
        id: 'blockchain-002',
        name: 'Binance Smart Chain',
        symbol: 'BNB',
        type: 'mainnet',
        status: 'connected',
        blockHeight: 34567890,
        nodeCount: 2,
        gasPrice: 5.2,
        lastSync: '2024-01-15T10:29:45Z',
        rpcEndpoint: 'https://bsc-dataseed.binance.org/'
      },
      {
        id: 'blockchain-003',
        name: 'Polygon',
        symbol: 'MATIC',
        type: 'mainnet',
        status: 'syncing',
        blockHeight: 51234567,
        nodeCount: 1,
        gasPrice: 30.8,
        lastSync: '2024-01-15T10:25:00Z',
        rpcEndpoint: 'https://polygon-rpc.com/'
      }
    ];

    const mockTokenListings: TokenListing[] = [
      {
        id: 'listing-001',
        tokenName: 'DeFi Protocol Token',
        symbol: 'DPT',
        contractAddress: '0x1234567890abcdef1234567890abcdef12345678',
        blockchain: 'Ethereum',
        status: 'pending',
        submittedBy: 'DeFi Team',
        submittedAt: '2024-01-14T15:30:00Z'
      },
      {
        id: 'listing-002',
        tokenName: 'Gaming Token',
        symbol: 'GAME',
        contractAddress: '0xabcdef1234567890abcdef1234567890abcdef12',
        blockchain: 'BSC',
        status: 'approved',
        submittedBy: 'Gaming Studio',
        submittedAt: '2024-01-13T10:15:00Z',
        reviewedBy: 'Tech Lead',
        reviewedAt: '2024-01-14T09:30:00Z'
      },
      {
        id: 'listing-003',
        tokenName: 'Utility Token',
        symbol: 'UTIL',
        contractAddress: '0x567890abcdef1234567890abcdef1234567890ab',
        blockchain: 'Polygon',
        status: 'deployed',
        submittedBy: 'Utility Corp',
        submittedAt: '2024-01-12T14:20:00Z',
        reviewedBy: 'Senior Dev',
        reviewedAt: '2024-01-13T11:45:00Z',
        deploymentTx: '0xdeployment123456789...'
      }
    ];

    setTradingPairs(mockTradingPairs);
    setServices(mockServices);
    setBlockchains(mockBlockchains);
    setTokenListings(mockTokenListings);
  }, []);

  const handleCreateTradingPair = () => {
    alert('Create new trading pair dialog would open here');
  };

  const handleTogglePairStatus = (pairId: string) => {
    setTradingPairs(prev => 
      prev.map(pair => 
        pair.id === pairId 
          ? { 
              ...pair, 
              status: pair.status === 'active' ? 'inactive' : 'active',
              lastUpdated: new Date().toISOString()
            }
          : pair
      )
    );
  };

  const handleRestartService = (serviceId: string) => {
    setServices(prev => 
      prev.map(service => 
        service.id === serviceId 
          ? { 
              ...service, 
              status: 'running',
              uptime: '0m',
              lastDeployment: new Date().toISOString()
            }
          : service
      )
    );
    alert(`Service ${serviceId} restarted successfully`);
  };

  const handleIntegrateBlockchain = () => {
    alert('Blockchain integration wizard would open here');
  };

  const handleApproveToken = (listingId: string) => {
    setTokenListings(prev => 
      prev.map(listing => 
        listing.id === listingId 
          ? { 
              ...listing, 
              status: 'approved',
              reviewedBy: 'Tech Admin',
              reviewedAt: new Date().toISOString()
            }
          : listing
      )
    );
    alert(`Token listing ${listingId} approved`);
  };

  const handleDeployToken = (listingId: string) => {
    setTokenListings(prev => 
      prev.map(listing => 
        listing.id === listingId 
          ? { 
              ...listing, 
              status: 'deployed',
              deploymentTx: `0x${Math.random().toString(16).substr(2, 40)}`
            }
          : listing
      )
    );
    alert(`Token ${listingId} deployed successfully`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'running':
      case 'connected':
      case 'approved':
      case 'deployed': return 'bg-green-100 text-green-800';
      case 'inactive':
      case 'stopped':
      case 'disconnected':
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'maintenance':
      case 'syncing':
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getServiceTypeIcon = (type: string) => {
    switch (type) {
      case 'gateway': return <Globe className="h-5 w-5" />;
      case 'microservice': return <Server className="h-5 w-5" />;
      case 'database': return <Database className="h-5 w-5" />;
      case 'cache': return <Zap className="h-5 w-5" />;
      case 'queue': return <Network className="h-5 w-5" />;
      default: return <Server className="h-5 w-5" />;
    }
  };

  const filteredTradingPairs = tradingPairs.filter(pair => 
    pair.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pair.baseAsset.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pair.quoteAsset.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalPairs: tradingPairs.length,
    activePairs: tradingPairs.filter(p => p.status === 'active').length,
    totalServices: services.length,
    runningServices: services.filter(s => s.status === 'running').length,
    connectedBlockchains: blockchains.filter(b => b.status === 'connected').length,
    pendingListings: tokenListings.filter(t => t.status === 'pending').length,
    avgCpuUsage: services.reduce((sum, s) => sum + s.cpu, 0) / services.length,
    avgMemoryUsage: services.reduce((sum, s) => sum + s.memory, 0) / services.length
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Technical Team Dashboard</h1>
          <p className="text-gray-600 mt-2">System management, trading pairs, and blockchain integration</p>
        </div>

        {/* Technical Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-8 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <GitBranch className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.activePairs}</div>
                  <div className="text-sm text-gray-600">Active Pairs</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Server className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">{stats.runningServices}</div>
                  <div className="text-sm text-gray-600">Services Up</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Network className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">{stats.connectedBlockchains}</div>
                  <div className="text-sm text-gray-600">Blockchains</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold text-orange-600">{stats.pendingListings}</div>
                  <div className="text-sm text-gray-600">Pending</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Cpu className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">{stats.avgCpuUsage.toFixed(1)}%</div>
                  <div className="text-sm text-gray-600">Avg CPU</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <HardDrive className="h-5 w-5 text-indigo-600" />
                <div>
                  <div className="text-2xl font-bold text-indigo-600">{stats.avgMemoryUsage.toFixed(1)}%</div>
                  <div className="text-sm text-gray-600">Avg Memory</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-teal-600" />
                <div>
                  <div className="text-2xl font-bold text-teal-600">99.9%</div>
                  <div className="text-sm text-gray-600">Uptime</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-pink-600" />
                <div>
                  <div className="text-2xl font-bold text-pink-600">0</div>
                  <div className="text-sm text-gray-600">Incidents</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="pairs">Trading Pairs ({stats.totalPairs})</TabsTrigger>
            <TabsTrigger value="services">Services ({stats.totalServices})</TabsTrigger>
            <TabsTrigger value="blockchains">Blockchains</TabsTrigger>
            <TabsTrigger value="listings">Token Listings</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Health</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {services.slice(0, 5).map((service) => (
                      <div key={service.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {getServiceTypeIcon(service.type)}
                          <div>
                            <div className="font-semibold">{service.name}</div>
                            <div className="text-sm text-gray-600">
                              Port {service.port} • {service.version}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getStatusColor(service.status)}>
                            {service.status}
                          </Badge>
                          <div className="text-xs text-gray-500 mt-1">
                            CPU: {service.cpu.toFixed(1)}% • RAM: {service.memory.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Activities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <div>
                        <div className="font-semibold">New trading pair deployed</div>
                        <div className="text-sm text-gray-600">SOLANA/USDT pair is now live</div>
                        <div className="text-xs text-gray-500">2 hours ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Code className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="font-semibold">System update completed</div>
                        <div className="text-sm text-gray-600">Matching engine v3.2.1 deployed</div>
                        <div className="text-xs text-gray-500">4 hours ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-yellow-600" />
                      <div>
                        <div className="font-semibold">Maintenance scheduled</div>
                        <div className="text-sm text-gray-600">Database maintenance at 2 AM UTC</div>
                        <div className="text-xs text-gray-500">6 hours ago</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="pairs" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Trading Pair Management</CardTitle>
                  <Button onClick={handleCreateTradingPair}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Pair
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search trading pairs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredTradingPairs.map((pair) => (
                    <Card key={pair.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {pair.baseAsset.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{pair.symbol}</div>
                              <div className="text-sm text-gray-600">
                                {pair.baseAsset} / {pair.quoteAsset}
                              </div>
                              <div className="text-xs text-gray-500">
                                Created: {new Date(pair.createdAt).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-lg font-bold">${pair.price.toLocaleString()}</div>
                              <div className="text-xs text-gray-500">Price</div>
                            </div>
                            <div className="text-center">
                              <div className={`text-lg font-bold ${pair.change24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {pair.change24h >= 0 ? '+' : ''}{pair.change24h.toFixed(2)}%
                              </div>
                              <div className="text-xs text-gray-500">24h Change</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold">${pair.volume24h.toLocaleString()}</div>
                              <div className="text-xs text-gray-500">24h Volume</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <Badge className={getStatusColor(pair.status)}>
                              {pair.status}
                            </Badge>

                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleTogglePairStatus(pair.id)}
                              >
                                {pair.status === 'active' ? (
                                  <Pause className="h-4 w-4 mr-1" />
                                ) : (
                                  <Play className="h-4 w-4 mr-1" />
                                )}
                                {pair.status === 'active' ? 'Pause' : 'Activate'}
                              </Button>
                              <Button size="sm" variant="outline">
                                <Edit className="h-4 w-4 mr-1" />
                                Edit
                              </Button>
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                Details
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="services" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Services</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {services.map((service) => (
                    <Card key={service.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white">
                              {getServiceTypeIcon(service.type)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{service.name}</div>
                              <div className="text-sm text-gray-600">
                                {service.type} • Port {service.port} • {service.version}
                              </div>
                              <div className="text-xs text-gray-500">
                                Uptime: {service.uptime} • Last deployed: {new Date(service.lastDeployment).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">{service.cpu.toFixed(1)}%</div>
                              <div className="text-xs text-gray-500">CPU</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-green-600">{service.memory.toFixed(1)}%</div>
                              <div className="text-xs text-gray-500">Memory</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <Badge className={getStatusColor(service.status)}>
                              {service.status}
                            </Badge>

                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleRestartService(service.id)}
                                disabled={service.status === 'running'}
                              >
                                <Play className="h-4 w-4 mr-1" />
                                Restart
                              </Button>
                              <Button size="sm" variant="outline">
                                <Terminal className="h-4 w-4 mr-1" />
                                Logs
                              </Button>
                              <Button size="sm" variant="outline">
                                <Settings className="h-4 w-4 mr-1" />
                                Config
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="blockchains" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Blockchain Networks</CardTitle>
                  <Button onClick={handleIntegrateBlockchain}>
                    <Plus className="h-4 w-4 mr-2" />
                    Integrate Blockchain
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {blockchains.map((blockchain) => (
                    <Card key={blockchain.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white font-bold">
                              {blockchain.symbol.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{blockchain.name}</div>
                              <div className="text-sm text-gray-600">
                                {blockchain.type} • {blockchain.nodeCount} nodes
                              </div>
                              <div className="text-xs text-gray-500">
                                Last sync: {new Date(blockchain.lastSync).toLocaleString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">{blockchain.blockHeight.toLocaleString()}</div>
                              <div className="text-xs text-gray-500">Block Height</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-green-600">{blockchain.gasPrice.toFixed(1)}</div>
                              <div className="text-xs text-gray-500">Gas Price (Gwei)</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <Badge className={getStatusColor(blockchain.status)}>
                              {blockchain.status}
                            </Badge>

                            <div className="flex space-x-2">
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                Monitor
                              </Button>
                              <Button size="sm" variant="outline">
                                <Settings className="h-4 w-4 mr-1" />
                                Configure
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="listings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Token Listing Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tokenListings.map((listing) => (
                    <Card key={listing.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-600 rounded-full flex items-center justify-center text-white font-bold">
                              {listing.symbol.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{listing.tokenName} ({listing.symbol})</div>
                              <div className="text-sm text-gray-600">
                                {listing.blockchain} • {listing.submittedBy}
                              </div>
                              <div className="text-xs text-gray-500">
                                Contract: {listing.contractAddress.substring(0, 20)}...
                              </div>
                              <div className="text-xs text-gray-500">
                                Submitted: {new Date(listing.submittedAt).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <Badge className={getStatusColor(listing.status)}>
                              {listing.status}
                            </Badge>

                            <div className="flex space-x-2">
                              {listing.status === 'pending' && (
                                <>
                                  <Button 
                                    size="sm"
                                    onClick={() => handleApproveToken(listing.id)}
                                    className="bg-green-600 hover:bg-green-700"
                                  >
                                    <CheckCircle className="h-4 w-4 mr-1" />
                                    Approve
                                  </Button>
                                  <Button size="sm" variant="destructive">
                                    <AlertTriangle className="h-4 w-4 mr-1" />
                                    Reject
                                  </Button>
                                </>
                              )}
                              {listing.status === 'approved' && (
                                <Button 
                                  size="sm"
                                  onClick={() => handleDeployToken(listing.id)}
                                  className="bg-blue-600 hover:bg-blue-700"
                                >
                                  <Play className="h-4 w-4 mr-1" />
                                  Deploy
                                </Button>
                              )}
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                Review
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">CPU Usage</span>
                        <span className="text-sm">{stats.avgCpuUsage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${stats.avgCpuUsage}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Memory Usage</span>
                        <span className="text-sm">{stats.avgMemoryUsage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${stats.avgMemoryUsage}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Network I/O</span>
                        <span className="text-sm">234 MB/s</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Disk Usage</span>
                        <span className="text-sm">67%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-orange-600 h-2 rounded-full" style={{ width: '67%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Alert Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                        <span className="font-semibold text-red-800">Critical</span>
                      </div>
                      <span className="text-red-600 font-bold">0</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-5 w-5 text-yellow-600" />
                        <span className="font-semibold text-yellow-800">Warning</span>
                      </div>
                      <span className="text-yellow-600 font-bold">2</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <Activity className="h-5 w-5 text-blue-600" />
                        <span className="font-semibold text-blue-800">Info</span>
                      </div>
                      <span className="text-blue-600 font-bold">5</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default TechnicalTeamDashboard;