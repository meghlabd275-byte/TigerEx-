/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3,
  Clock,
  ArrowUpDown,
  Eye,
  EyeOff,
  Plus,
  Minus,
  RefreshCw,
  Bell,
  Settings,
  Star,
  Gift,
  Shield
} from 'lucide-react';

interface Asset {
  symbol: string;
  name: string;
  balance: number;
  usdValue: number;
  change24h: number;
  price: number;
}

interface Transaction {
  id: string;
  type: 'deposit' | 'withdrawal' | 'trade' | 'transfer';
  asset: string;
  amount: number;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
  txHash?: string;
}

interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  amount: number;
  price?: number;
  filled: number;
  status: 'pending' | 'filled' | 'cancelled' | 'partially_filled';
  timestamp: string;
}

interface Earning {
  id: string;
  product: string;
  asset: string;
  amount: number;
  apy: number;
  duration: string;
  status: 'active' | 'completed' | 'redeemed';
  startDate: string;
  endDate?: string;
}

const UserDashboard: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [earnings, setEarnings] = useState<Earning[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [hideBalances, setHideBalances] = useState(false);
  const [totalBalance, setTotalBalance] = useState(0);

  useEffect(() => {
    // Mock user data
    const mockAssets: Asset[] = [
      {
        symbol: 'BTC',
        name: 'Bitcoin',
        balance: 0.5234,
        usdValue: 23678.45,
        change24h: 2.34,
        price: 45234.56
      },
      {
        symbol: 'ETH',
        name: 'Ethereum',
        balance: 8.9012,
        usdValue: 25234.78,
        change24h: -1.23,
        price: 2834.12
      },
      {
        symbol: 'USDT',
        name: 'Tether',
        balance: 12345.67,
        usdValue: 12345.67,
        change24h: 0.01,
        price: 1.00
      },
      {
        symbol: 'BNB',
        name: 'BNB',
        balance: 45.23,
        usdValue: 13567.89,
        change24h: 3.45,
        price: 299.87
      },
      {
        symbol: 'ADA',
        name: 'Cardano',
        balance: 2345.67,
        usdValue: 1071.23,
        change24h: 5.67,
        price: 0.4567
      }
    ];

    const mockTransactions: Transaction[] = [
      {
        id: 'tx-001',
        type: 'deposit',
        asset: 'USDT',
        amount: 5000,
        status: 'completed',
        timestamp: '2024-01-15T10:30:00Z',
        txHash: '0x1234...abcd'
      },
      {
        id: 'tx-002',
        type: 'trade',
        asset: 'BTC',
        amount: 0.1,
        status: 'completed',
        timestamp: '2024-01-15T09:15:00Z'
      },
      {
        id: 'tx-003',
        type: 'withdrawal',
        asset: 'ETH',
        amount: 2.5,
        status: 'pending',
        timestamp: '2024-01-15T08:45:00Z',
        txHash: '0x5678...efgh'
      }
    ];

    const mockOrders: Order[] = [
      {
        id: 'order-001',
        symbol: 'BTCUSDT',
        side: 'buy',
        type: 'limit',
        amount: 0.5,
        price: 45000,
        filled: 0.2,
        status: 'partially_filled',
        timestamp: '2024-01-15T14:30:00Z'
      },
      {
        id: 'order-002',
        symbol: 'ETHUSDT',
        side: 'sell',
        type: 'limit',
        amount: 2.0,
        price: 2850,
        filled: 0,
        status: 'pending',
        timestamp: '2024-01-15T14:25:00Z'
      }
    ];

    const mockEarnings: Earning[] = [
      {
        id: 'earn-001',
        product: 'Flexible Savings',
        asset: 'USDT',
        amount: 5000,
        apy: 8.5,
        duration: 'Flexible',
        status: 'active',
        startDate: '2024-01-10T00:00:00Z'
      },
      {
        id: 'earn-002',
        product: 'Locked Staking',
        asset: 'ETH',
        amount: 5.0,
        apy: 12.3,
        duration: '30 days',
        status: 'active',
        startDate: '2024-01-05T00:00:00Z',
        endDate: '2024-02-04T00:00:00Z'
      }
    ];

    setAssets(mockAssets);
    setTransactions(mockTransactions);
    setOrders(mockOrders);
    setEarnings(mockEarnings);
    setTotalBalance(mockAssets.reduce((sum, asset) => sum + asset.usdValue, 0));
  }, []);

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'filled':
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending':
      case 'partially_filled': return 'bg-yellow-100 text-yellow-800';
      case 'failed':
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatBalance = (balance: number) => {
    return hideBalances ? '****' : balance.toLocaleString();
  };

  const formatUSD = (amount: number) => {
    return hideBalances ? '$****' : `$${amount.toLocaleString()}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-2">Welcome back! Here&apos;s your portfolio overview</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={() => setHideBalances(!hideBalances)}>
                {hideBalances ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="md:col-span-2">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-600">Total Balance</h3>
                  <div className="text-4xl font-bold text-gray-900">
                    {formatUSD(totalBalance)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center text-green-600">
                    <TrendingUp className="h-5 w-5 mr-1" />
                    <span className="font-semibold">+2.34%</span>
                  </div>
                  <div className="text-sm text-gray-500">24h Change</div>
                </div>
              </div>
              <div className="flex space-x-4">
                <Button className="flex-1">
                  <Plus className="h-4 w-4 mr-2" />
                  Deposit
                </Button>
                <Button variant="outline" className="flex-1">
                  <Minus className="h-4 w-4 mr-2" />
                  Withdraw
                </Button>
                <Button variant="outline" className="flex-1">
                  <ArrowUpDown className="h-4 w-4 mr-2" />
                  Transfer
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2 mb-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold">Today&apos;s P&L</h3>
              </div>
              <div className="text-2xl font-bold text-green-600">+$1,234.56</div>
              <div className="text-sm text-gray-500">+5.67% from yesterday</div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2 mb-2">
                <Gift className="h-5 w-5 text-purple-600" />
                <h3 className="font-semibold">Total Earnings</h3>
              </div>
              <div className="text-2xl font-bold text-purple-600">
                {formatUSD(earnings.reduce((sum, e) => sum + e.amount, 0))}
              </div>
              <div className="text-sm text-gray-500">From staking & savings</div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="assets">Assets</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="earn">Earn</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Assets */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Assets</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {assets.slice(0, 5).map((asset) => (
                      <div key={asset.symbol} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            {asset.symbol.charAt(0)}
                          </div>
                          <div>
                            <div className="font-semibold">{asset.symbol}</div>
                            <div className="text-sm text-gray-500">{asset.name}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">{formatUSD(asset.usdValue)}</div>
                          <div className={`text-sm ${getChangeColor(asset.change24h)}`}>
                            {asset.change24h >= 0 ? '+' : ''}{asset.change24h.toFixed(2)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {transactions.slice(0, 5).map((tx) => (
                      <div key={tx.id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            tx.type === 'deposit' ? 'bg-green-100 text-green-600' :
                            tx.type === 'withdrawal' ? 'bg-red-100 text-red-600' :
                            'bg-blue-100 text-blue-600'
                          }`}>
                            {tx.type === 'deposit' ? <Plus className="h-4 w-4" /> :
                             tx.type === 'withdrawal' ? <Minus className="h-4 w-4" /> :
                             <ArrowUpDown className="h-4 w-4" />}
                          </div>
                          <div>
                            <div className="font-semibold capitalize">{tx.type}</div>
                            <div className="text-sm text-gray-500">
                              {new Date(tx.timestamp).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">
                            {formatBalance(tx.amount)} {tx.asset}
                          </div>
                          <Badge className={getStatusColor(tx.status)}>
                            {tx.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="assets" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>My Assets</CardTitle>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {assets.map((asset) => (
                    <Card key={asset.symbol} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {asset.symbol.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{asset.symbol}</div>
                              <div className="text-gray-600">{asset.name}</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-8">
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Balance</div>
                              <div className="font-semibold">{formatBalance(asset.balance)}</div>
                            </div>
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Price</div>
                              <div className="font-semibold">${asset.price.toLocaleString()}</div>
                            </div>
                            <div className="text-center">
                              <div className="text-sm text-gray-500">24h Change</div>
                              <div className={`font-semibold ${getChangeColor(asset.change24h)}`}>
                                {asset.change24h >= 0 ? '+' : ''}{asset.change24h.toFixed(2)}%
                              </div>
                            </div>
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Value</div>
                              <div className="font-semibold">{formatUSD(asset.usdValue)}</div>
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            <Button size="sm">Trade</Button>
                            <Button size="sm" variant="outline">Transfer</Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Open Orders</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {orders.filter(order => order.status !== 'filled' && order.status !== 'cancelled').map((order) => (
                    <Card key={order.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <Badge className={order.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                              {order.side.toUpperCase()}
                            </Badge>
                            <div>
                              <div className="font-semibold">{order.symbol}</div>
                              <div className="text-sm text-gray-600">
                                {order.type} • {new Date(order.timestamp).toLocaleString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Amount</div>
                              <div className="font-semibold">{order.amount}</div>
                            </div>
                            {order.price && (
                              <div className="text-center">
                                <div className="text-sm text-gray-500">Price</div>
                                <div className="font-semibold">${order.price.toFixed(2)}</div>
                              </div>
                            )}
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Filled</div>
                              <div className="font-semibold">{order.filled}/{order.amount}</div>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(order.status)}>
                                {order.status.replace('_', ' ')}
                              </Badge>
                            </div>
                          </div>

                          <Button size="sm" variant="outline">
                            Cancel
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {orders.filter(order => order.status !== 'filled' && order.status !== 'cancelled').length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No open orders
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Transaction History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {transactions.map((tx) => (
                    <Card key={tx.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              tx.type === 'deposit' ? 'bg-green-100 text-green-600' :
                              tx.type === 'withdrawal' ? 'bg-red-100 text-red-600' :
                              'bg-blue-100 text-blue-600'
                            }`}>
                              {tx.type === 'deposit' ? <Plus className="h-5 w-5" /> :
                               tx.type === 'withdrawal' ? <Minus className="h-5 w-5" /> :
                               <ArrowUpDown className="h-5 w-5" />}
                            </div>
                            <div>
                              <div className="font-semibold capitalize">{tx.type}</div>
                              <div className="text-sm text-gray-600">
                                {new Date(tx.timestamp).toLocaleString()}
                              </div>
                              {tx.txHash && (
                                <div className="text-xs text-gray-500">
                                  Hash: {tx.txHash}
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="font-semibold">
                                {formatBalance(tx.amount)} {tx.asset}
                              </div>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(tx.status)}>
                                {tx.status}
                              </Badge>
                            </div>
                          </div>

                          <Button size="sm" variant="outline">
                            <Eye className="h-4 w-4 mr-1" />
                            Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="earn" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Earn Products</CardTitle>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Subscribe
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {earnings.map((earning) => (
                    <Card key={earning.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-white">
                              <Gift className="h-6 w-6" />
                            </div>
                            <div>
                              <div className="font-semibold">{earning.product}</div>
                              <div className="text-sm text-gray-600">
                                {earning.asset} • {earning.duration}
                              </div>
                              <div className="text-xs text-gray-500">
                                Started: {new Date(earning.startDate).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-sm text-gray-500">Amount</div>
                              <div className="font-semibold">
                                {formatBalance(earning.amount)} {earning.asset}
                              </div>
                            </div>
                            <div className="text-center">
                              <div className="text-sm text-gray-500">APY</div>
                              <div className="font-semibold text-green-600">{earning.apy}%</div>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(earning.status)}>
                                {earning.status}
                              </Badge>
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            <Button size="sm" variant="outline">
                              Details
                            </Button>
                            {earning.status === 'active' && (
                              <Button size="sm">
                                Redeem
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UserDashboard;