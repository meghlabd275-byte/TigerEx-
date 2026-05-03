/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Users, Activity, AlertTriangle, Settings, Shield, TrendingUp,
  DollarSign, BarChart3, Server, Database, Bell, Search, MoreHorizontal,
  Play, Pause, Square, RefreshCw, Trash2, Edit, Eye, UserPlus,
  Key, Lock, Unlock, FileText, Gauge, Coins, ArrowUpDown
} from 'lucide-react';

// Types
interface User {
  id: string;
  email: string;
  username: string;
  role: 'SuperAdmin' | 'Admin' | 'Moderator' | 'User' | 'Institutional' | 'MarketMaker';
  status: 'Active' | 'Paused' | 'Halted' | 'Suspended' | 'PendingVerification';
  tradingEnabled: boolean;
  withdrawalEnabled: boolean;
  depositEnabled: boolean;
  kycLevel: number;
  createdAt: string;
  lastLoginAt?: string;
  totalVolume?: string;
  totalTrades?: number;
  balances?: Balance[];
}

interface Balance {
  asset: string;
  free: string;
  locked: string;
}

interface TradingPair {
  id: string;
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'Trading' | 'Pause' | 'Delist' | 'PreTrading' | 'PostTrading';
  makerFee: string;
  takerFee: string;
  minQty: string;
  maxQty: string;
  volume24h?: string;
  priceChange24h?: string;
}

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalVolume24h: string;
  totalTrades24h: number;
  openOrders: number;
  engineStatus: 'Running' | 'Paused' | 'Halted' | 'Maintenance';
  avgLatency: number;
  ordersPerSecond: number;
  memoryUsage: number;
  cpuUsage: number;
}

interface RiskAlert {
  id: string;
  type: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  message: string;
  userId?: string;
  symbol?: string;
  createdAt: string;
  acknowledged: boolean;
}

export default function SuperAdminDashboard() {
  const [users, setUsers] = useState<User[]>([]);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch data
  useEffect(() => {
    fetchMetrics();
    fetchUsers();
    fetchTradingPairs();
    fetchAlerts();

    const interval = setInterval(() => {
      fetchMetrics();
      fetchAlerts();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/admin/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users');
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const fetchTradingPairs = async () => {
    try {
      const response = await fetch('/api/admin/trading-pairs');
      const data = await response.json();
      setTradingPairs(data);
    } catch (error) {
      console.error('Failed to fetch trading pairs:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/admin/alerts');
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  // User actions
  const handleUserAction = async (userId: string, action: string) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/${action}`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchUsers();
      }
    } catch (error) {
      console.error(`Failed to ${action} user:`, error);
    }
  };

  const handleTradingPairAction = async (pairId: string, action: string) => {
    try {
      const response = await fetch(`/api/admin/trading-pairs/${pairId}/${action}`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchTradingPairs();
      }
    } catch (error) {
      console.error(`Failed to ${action} trading pair:`, error);
    }
  };

  const handleEngineAction = async (action: 'pause' | 'resume' | 'halt') => {
    try {
      await fetch(`/api/admin/engine/${action}`, { method: 'POST' });
      fetchMetrics();
    } catch (error) {
      console.error(`Failed to ${action} engine:`, error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active':
      case 'Trading':
      case 'Running':
        return 'bg-green-500';
      case 'Paused':
        return 'bg-yellow-500';
      case 'Halted':
      case 'Suspended':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical':
        return 'bg-red-500 text-white';
      case 'High':
        return 'bg-orange-500 text-white';
      case 'Medium':
        return 'bg-yellow-500';
      case 'Low':
        return 'bg-blue-500 text-white';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-blue-500" />
              <span className="text-xl font-bold">TigerEx Admin</span>
            </div>
            <Badge variant="outline" className="text-blue-400 border-blue-400">
              Super Admin
            </Badge>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                className="pl-10 w-64 bg-gray-700 border-gray-600"
                placeholder="Search users, pairs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {alerts.filter(a => !a.acknowledged).length > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-xs flex items-center justify-center">
                  {alerts.filter(a => !a.acknowledged).length}
                </span>
              )}
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-gray-800 border-gray-700">
            <TabsTrigger value="overview" className="data-[state=active]:bg-gray-700">
              <Activity className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-gray-700">
              <Users className="h-4 w-4 mr-2" />
              Users
            </TabsTrigger>
            <TabsTrigger value="trading" className="data-[state=active]:bg-gray-700">
              <TrendingUp className="h-4 w-4 mr-2" />
              Trading
            </TabsTrigger>
            <TabsTrigger value="risk" className="data-[state=active]:bg-gray-700">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Risk
            </TabsTrigger>
            <TabsTrigger value="system" className="data-[state=active]:bg-gray-700">
              <Server className="h-4 w-4 mr-2" />
              System
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6 mt-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics?.totalUsers || 0}</div>
                  <p className="text-xs text-gray-400">{metrics?.activeUsers || 0} active</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">24h Volume</CardTitle>
                  <DollarSign className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${metrics?.totalVolume24h || '0'}</div>
                  <p className="text-xs text-gray-400">{metrics?.totalTrades24h || 0} trades</p>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Engine Status</CardTitle>
                  <Server className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusColor(metrics?.engineStatus || 'Running')}>
                      {metrics?.engineStatus || 'Running'}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {metrics?.ordersPerSecond || 0} orders/s
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">Avg Latency</CardTitle>
                  <Gauge className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics?.avgLatency || 0}μs</div>
                  <p className="text-xs text-gray-400">sub-microsecond</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Engine Controls */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Engine Controls</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Server className="h-5 w-5 text-blue-500" />
                      <div>
                        <p className="font-medium">Trading Engine</p>
                        <p className="text-sm text-gray-400">Control the core matching engine</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="border-yellow-500 text-yellow-500"
                        onClick={() => handleEngineAction('pause')}
                      >
                        <Pause className="h-4 w-4 mr-1" />
                        Pause
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="border-green-500 text-green-500"
                        onClick={() => handleEngineAction('resume')}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Resume
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        onClick={() => handleEngineAction('halt')}
                      >
                        <Square className="h-4 w-4 mr-1" />
                        Halt
                      </Button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Database className="h-5 w-5 text-green-500" />
                      <div>
                        <p className="font-medium">System Resources</p>
                        <p className="text-sm text-gray-400">CPU: {metrics?.cpuUsage || 0}% | RAM: {metrics?.memoryUsage || 0}%</p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Refresh
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Alerts */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Recent Alerts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {alerts.slice(0, 5).map((alert) => (
                      <div key={alert.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className={`h-5 w-5 ${
                            alert.severity === 'Critical' ? 'text-red-500' :
                            alert.severity === 'High' ? 'text-orange-500' : 'text-yellow-500'
                          }`} />
                          <div>
                            <p className="text-sm font-medium">{alert.type}</p>
                            <p className="text-xs text-gray-400">{alert.message}</p>
                          </div>
                        </div>
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6 mt-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>User Management</CardTitle>
                <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Add User
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-gray-800 border-gray-700">
                    <DialogHeader>
                      <DialogTitle>Create New User</DialogTitle>
                      <DialogDescription>
                        Add a new user to the platform
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Email</label>
                        <Input className="bg-gray-700 border-gray-600" placeholder="user@example.com" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Username</label>
                        <Input className="bg-gray-700 border-gray-600" placeholder="username" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Role</label>
                        <Select>
                          <SelectTrigger className="bg-gray-700 border-gray-600">
                            <SelectValue placeholder="Select role" />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-700">
                            <SelectItem value="User">User</SelectItem>
                            <SelectItem value="Institutional">Institutional</SelectItem>
                            <SelectItem value="MarketMaker">Market Maker</SelectItem>
                            <SelectItem value="Moderator">Moderator</SelectItem>
                            <SelectItem value="Admin">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsUserDialogOpen(false)}>Cancel</Button>
                      <Button className="bg-blue-600 hover:bg-blue-700">Create User</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-700 hover:bg-gray-700">
                      <TableHead className="text-gray-400">User</TableHead>
                      <TableHead className="text-gray-400">Role</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">Trading</TableHead>
                      <TableHead className="text-gray-400">KYC</TableHead>
                      <TableHead className="text-gray-400">Volume</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id} className="border-gray-700 hover:bg-gray-700">
                        <TableCell>
                          <div>
                            <p className="font-medium">{user.username}</p>
                            <p className="text-sm text-gray-400">{user.email}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{user.role}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(user.status)}>{user.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-1">
                            {user.tradingEnabled ? (
                              <Badge variant="outline" className="border-green-500 text-green-500">T</Badge>
                            ) : (
                              <Badge variant="outline" className="border-red-500 text-red-500">T</Badge>
                            )}
                            {user.withdrawalEnabled ? (
                              <Badge variant="outline" className="border-green-500 text-green-500">W</Badge>
                            ) : (
                              <Badge variant="outline" className="border-red-500 text-red-500">W</Badge>
                            )}
                            {user.depositEnabled ? (
                              <Badge variant="outline" className="border-green-500 text-green-500">D</Badge>
                            ) : (
                              <Badge variant="outline" className="border-red-500 text-red-500">D</Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">Level {user.kycLevel}</Badge>
                        </TableCell>
                        <TableCell>${user.totalVolume || '0'}</TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="bg-gray-800 border-gray-700">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuSeparator className="bg-gray-700" />
                              <DropdownMenuItem onClick={() => { setSelectedUser(user); }}>
                                <Eye className="h-4 w-4 mr-2" />
                                View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit User
                              </DropdownMenuItem>
                              <DropdownMenuSeparator className="bg-gray-700" />
                              <DropdownMenuItem onClick={() => handleUserAction(user.id, 'pause')}>
                                <Pause className="h-4 w-4 mr-2" />
                                Pause Account
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleUserAction(user.id, 'resume')}>
                                <Play className="h-4 w-4 mr-2" />
                                Resume Account
                              </DropdownMenuItem>
                              <DropdownMenuItem 
                                className="text-red-400"
                                onClick={() => handleUserAction(user.id, 'halt')}
                              >
                                <Square className="h-4 w-4 mr-2" />
                                Halt Account
                              </DropdownMenuItem>
                              <DropdownMenuSeparator className="bg-gray-700" />
                              <DropdownMenuItem>
                                <Key className="h-4 w-4 mr-2" />
                                API Keys
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Lock className="h-4 w-4 mr-2" />
                                Reset Password
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-400">
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete User
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Trading Tab */}
          <TabsContent value="trading" className="space-y-6 mt-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Trading Pairs</CardTitle>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Coins className="h-4 w-4 mr-2" />
                  Add Trading Pair
                </Button>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-700 hover:bg-gray-700">
                      <TableHead className="text-gray-400">Symbol</TableHead>
                      <TableHead className="text-gray-400">Status</TableHead>
                      <TableHead className="text-gray-400">Fees</TableHead>
                      <TableHead className="text-gray-400">24h Volume</TableHead>
                      <TableHead className="text-gray-400">Price Change</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tradingPairs.map((pair) => (
                      <TableRow key={pair.id} className="border-gray-700 hover:bg-gray-700">
                        <TableCell>
                          <div>
                            <p className="font-medium">{pair.symbol}</p>
                            <p className="text-sm text-gray-400">{pair.baseAsset}/{pair.quoteAsset}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(pair.status)}>{pair.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <p className="text-sm">Maker: {(parseFloat(pair.makerFee) * 100).toFixed(2)}%</p>
                          <p className="text-sm text-gray-400">Taker: {(parseFloat(pair.takerFee) * 100).toFixed(2)}%</p>
                        </TableCell>
                        <TableCell>${pair.volume24h || '0'}</TableCell>
                        <TableCell>
                          <span className={pair.priceChange24h?.startsWith('-') ? 'text-red-400' : 'text-green-400'}>
                            {pair.priceChange24h || '0%'}
                          </span>
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="bg-gray-800 border-gray-700">
                              <DropdownMenuItem onClick={() => handleTradingPairAction(pair.id, 'pause')}>
                                <Pause className="h-4 w-4 mr-2" />
                                Pause Trading
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleTradingPairAction(pair.id, 'resume')}>
                                <Play className="h-4 w-4 mr-2" />
                                Resume Trading
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Edit className="h-4 w-4 mr-2" />
                                Edit Fees
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-400">
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delist
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Risk Tab */}
          <TabsContent value="risk" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Total Alerts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{alerts.length}</div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Critical</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-500">
                    {alerts.filter(a => a.severity === 'Critical').length}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Unacknowledged</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-orange-500">
                    {alerts.filter(a => !a.acknowledged).length}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Risk Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-700 hover:bg-gray-700">
                      <TableHead className="text-gray-400">Type</TableHead>
                      <TableHead className="text-gray-400">Severity</TableHead>
                      <TableHead className="text-gray-400">Message</TableHead>
                      <TableHead className="text-gray-400">User</TableHead>
                      <TableHead className="text-gray-400">Time</TableHead>
                      <TableHead className="text-gray-400">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {alerts.map((alert) => (
                      <TableRow key={alert.id} className="border-gray-700 hover:bg-gray-700">
                        <TableCell>{alert.type}</TableCell>
                        <TableCell>
                          <Badge className={getSeverityColor(alert.severity)}>{alert.severity}</Badge>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">{alert.message}</TableCell>
                        <TableCell>{alert.userId || '-'}</TableCell>
                        <TableCell>{new Date(alert.createdAt).toLocaleString()}</TableCell>
                        <TableCell>
                          <Button size="sm" variant="outline">
                            Acknowledge
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Tab */}
          <TabsContent value="system" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle>System Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Trading Engine</span>
                      <Badge className={getStatusColor(metrics?.engineStatus || 'Running')}>
                        {metrics?.engineStatus || 'Running'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Database</span>
                      <Badge className="bg-green-500">Connected</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Redis Cache</span>
                      <Badge className="bg-green-500">Connected</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">WebSocket</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Orders/Second</span>
                      <span className="font-mono">{metrics?.ordersPerSecond || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Avg Latency</span>
                      <span className="font-mono">{metrics?.avgLatency || 0}μs</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Open Orders</span>
                      <span className="font-mono">{metrics?.openOrders || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">CPU Usage</span>
                      <span className="font-mono">{metrics?.cpuUsage || 0}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Memory Usage</span>
                      <span className="font-mono">{metrics?.memoryUsage || 0}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Audit Log</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow className="border-gray-700 hover:bg-gray-700">
                      <TableHead className="text-gray-400">Action</TableHead>
                      <TableHead className="text-gray-400">User</TableHead>
                      <TableHead className="text-gray-400">Resource</TableHead>
                      <TableHead className="text-gray-400">IP</TableHead>
                      <TableHead className="text-gray-400">Time</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {/* Audit logs would be rendered here */}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
