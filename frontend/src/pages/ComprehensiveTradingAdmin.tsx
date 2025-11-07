/**
 * Comprehensive Trading Admin Dashboard
 * Complete admin interface for all trading types
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  LineChart,
  Line,
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
  Activity,
  AlertTriangle,
  Pause,
  Play,
  Settings,
  Users,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Shield,
  FileText,
  Power,
  PowerOff,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  EyeOff,
} from 'lucide-react';

// Types
interface TradingType {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'suspended' | 'emergency_stop';
  enabled: boolean;
  volume24h: number;
  orders24h: number;
  users: number;
  contracts: number;
  errors: number;
}

interface Contract {
  id: string;
  symbol: string;
  tradingType: string;
  status: 'active' | 'paused' | 'suspended';
  leverage: number;
  volume24h: number;
  openInterest: number;
  fundingRate?: number;
  markPrice: number;
}

interface UserLimits {
  userId: string;
  tradingType: string;
  maxLeverage: number;
  maxPositionSize: number;
  maxOrderSize: number;
  dailyVolumeLimit: number;
  apiRateLimit: number;
}

interface AdminAction {
  id: string;
  adminId: string;
  action: string;
  tradingType: string;
  symbol?: string;
  userId?: string;
  reason: string;
  timestamp: string;
  result: any;
}

const ComprehensiveTradingAdmin: React.FC = () => {
  // State management
  const [tradingTypes, setTradingTypes] = useState<TradingType[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [userLimits, setUserLimits] = useState<UserLimits[]>([]);
  const [adminActions, setAdminActions] = useState<AdminAction[]>([]);
  const [selectedTradingType, setSelectedTradingType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Mock data initialization
  useEffect(() => {
    const mockTradingTypes: TradingType[] = [
      {
        id: 'spot',
        name: 'Spot Trading',
        status: 'active',
        enabled: true,
        volume24h: 1250000000,
        orders24h: 45000,
        users: 125000,
        contracts: 250,
        errors: 12,
      },
      {
        id: 'future_perpetual',
        name: 'Future Perpetual',
        status: 'active',
        enabled: true,
        volume24h: 2500000000,
        orders24h: 67000,
        users: 45000,
        contracts: 180,
        errors: 8,
      },
      {
        id: 'future_cross',
        name: 'Future Cross',
        status: 'paused',
        enabled: true,
        volume24h: 850000000,
        orders24h: 23000,
        users: 22000,
        contracts: 95,
        errors: 5,
      },
      {
        id: 'margin',
        name: 'Margin Trading',
        status: 'active',
        enabled: true,
        volume24h: 420000000,
        orders24h: 15000,
        users: 18000,
        contracts: 120,
        errors: 3,
      },
      {
        id: 'grid',
        name: 'Grid Trading',
        status: 'active',
        enabled: true,
        volume24h: 180000000,
        orders24h: 8500,
        users: 8500,
        contracts: 45,
        errors: 2,
      },
      {
        id: 'copy',
        name: 'Copy Trading',
        status: 'active',
        enabled: true,
        volume24h: 95000000,
        orders24h: 4200,
        users: 12000,
        contracts: 30,
        errors: 1,
      },
      {
        id: 'option',
        name: 'Option Trading',
        status: 'suspended',
        enabled: false,
        volume24h: 0,
        orders24h: 0,
        users: 0,
        contracts: 25,
        errors: 0,
      },
    ];

    setTradingTypes(mockTradingTypes);
  }, []);

  // Trading control functions
  const handleTradingControl = async (
    tradingType: string,
    action: 'pause' | 'resume' | 'suspend' | 'emergency_stop',
    reason: string
  ) => {
    setIsLoading(true);
    try {
      // API call would go here
      setTradingTypes(prev =>
        prev.map(tt =>
          tt.id === tradingType
            ? { ...tt, status: action === 'resume' ? 'active' : action === 'pause' ? 'paused' : action }
            : tt
        )
      );
      setAlert({ type: 'success', message: `Successfully ${action}d ${tradingType}` });
    } catch (error) {
      setAlert({ type: 'error', message: `Failed to ${action} ${tradingType}` });
    }
    setIsLoading(false);
  };

  // Contract management functions
  const handleContractAction = async (
    contractId: string,
    action: 'pause' | 'resume' | 'delete',
    reason: string
  ) => {
    setIsLoading(true);
    try {
      // API call would go here
      setContracts(prev =>
        prev.map(c =>
          c.id === contractId
            ? action === 'delete'
              ? null
              : { ...c, status: action === 'resume' ? 'active' : 'paused' }
            : c
        ).filter(Boolean) as Contract[]
      );
      setAlert({ type: 'success', message: `Successfully ${action}d contract` });
    } catch (error) {
      setAlert({ type: 'error', message: `Failed to ${action} contract` });
    }
    setIsLoading(false);
  };

  // Chart data preparation
  const volumeData = tradingTypes.map(tt => ({
    name: tt.name,
    volume: tt.volume24h / 1000000, // Convert to millions
    orders: tt.orders24h,
  }));

  const statusDistribution = tradingTypes.reduce((acc, tt) => {
    acc[tt.status] = (acc[tt.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(statusDistribution).map(([status, count]) => ({
    name: status.replace('_', ' ').toUpperCase(),
    value: count,
  }));

  const COLORS = {
    ACTIVE: '#10b981',
    PAUSED: '#f59e0b',
    SUSPENDED: '#ef4444',
    'EMERGENCY STOP': '#dc2626',
  };

  // Render trading type cards
  const renderTradingTypeCards = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6">
      {tradingTypes.map((type) => (
        <Card key={type.id} className="relative">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{type.name}</CardTitle>
              <Badge
                variant={type.status === 'active' ? 'default' : 
                        type.status === 'paused' ? 'secondary' : 'destructive'}
              >
                {type.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Status</span>
              <div className="flex items-center gap-1">
                {type.status === 'active' ? (
                  <Play className="h-3 w-3 text-green-500" />
                ) : (
                  <Pause className="h-3 w-3 text-yellow-500" />
                )}
                <span className="capitalize">{type.status.replace('_', ' ')}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-600">Volume 24h</span>
                <p className="font-semibold">${(type.volume24h / 1000000).toFixed(1)}M</p>
              </div>
              <div>
                <span className="text-gray-600">Orders 24h</span>
                <p className="font-semibold">{type.orders24h.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-600">Users</span>
                <p className="font-semibold">{type.users.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-600">Contracts</span>
                <p className="font-semibold">{type.contracts}</p>
              </div>
            </div>

            {type.errors > 0 && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  {type.errors} errors in the last 24 hours
                </AlertDescription>
              </Alert>
            )}

            <div className="flex gap-2 pt-2">
              {type.status === 'active' ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleTradingControl(type.id, 'pause', 'Manual pause')}
                  disabled={isLoading}
                >
                  <Pause className="h-3 w-3 mr-1" />
                  Pause
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={() => handleTradingControl(type.id, 'resume', 'Manual resume')}
                  disabled={isLoading}
                >
                  <Play className="h-3 w-3 mr-1" />
                  Resume
                </Button>
              )}
              
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleTradingControl(type.id, 'emergency_stop', 'Emergency stop')}
                disabled={isLoading}
              >
                <PowerOff className="h-3 w-3 mr-1" />
                Stop
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Comprehensive Trading Admin</h1>
          <p className="text-gray-600">Manage all trading types and operations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {alert && (
        <Alert variant={alert.type === 'success' ? 'default' : 'destructive'}>
          <AlertDescription>{alert.message}</AlertDescription>
        </Alert>
      )}

      {/* Overview Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Trading Volume (24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="volume" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Trading Type Controls */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trading-control">Trading Control</TabsTrigger>
          <TabsTrigger value="contracts">Contracts</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="risk">Risk Management</TabsTrigger>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {renderTradingTypeCards()}
        </TabsContent>

        <TabsContent value="trading-control" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Trading System Controls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {tradingTypes.map((type) => (
                    <div key={type.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">{type.name}</h3>
                        <Badge variant={type.enabled ? 'default' : 'secondary'}>
                          {type.enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Status:</span>
                          <span className="capitalize">{type.status.replace('_', ' ')}</span>
                        </div>
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleTradingControl(type.id, 'pause', 'Admin control')}
                          >
                            <Pause className="h-3 w-3 mr-1" />
                            Pause
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleTradingControl(type.id, 'resume', 'Admin control')}
                          >
                            <Play className="h-3 w-3 mr-1" />
                            Resume
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleTradingControl(type.id, 'emergency_stop', 'Emergency stop')}
                          >
                            <PowerOff className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contracts" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Contract Management</CardTitle>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Contract
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-4">
                <Input
                  placeholder="Search contracts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
                <Select>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="spot">Spot</SelectItem>
                    <SelectItem value="future_perpetual">Future Perpetual</SelectItem>
                    <SelectItem value="future_cross">Future Cross</SelectItem>
                    <SelectItem value="margin">Margin</SelectItem>
                    <SelectItem value="option">Options</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Leverage</TableHead>
                    <TableHead>Volume 24h</TableHead>
                    <TableHead>Open Interest</TableHead>
                    <TableHead>Mark Price</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contracts.map((contract) => (
                    <TableRow key={contract.id}>
                      <TableCell className="font-medium">{contract.symbol}</TableCell>
                      <TableCell>{contract.tradingType}</TableCell>
                      <TableCell>
                        <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
                          {contract.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{contract.leverage}x</TableCell>
                      <TableCell>${(contract.volume24h / 1000000).toFixed(1)}M</TableCell>
                      <TableCell>${(contract.openInterest / 1000000).toFixed(1)}M</TableCell>
                      <TableCell>${contract.markPrice.toFixed(2)}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            <Edit className="h-3 w-3" />
                          </Button>
                          {contract.status === 'active' ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleContractAction(contract.id, 'pause', 'Admin pause')}
                            >
                              <Pause className="h-3 w-3" />
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleContractAction(contract.id, 'resume', 'Admin resume')}
                            >
                              <Play className="h-3 w-3" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleContractAction(contract.id, 'delete', 'Admin deletion')}
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
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Users className="h-8 w-8 text-blue-500" />
                      <div>
                        <p className="text-sm text-gray-600">Total Users</p>
                        <p className="text-2xl font-bold">234,567</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Activity className="h-8 w-8 text-green-500" />
                      <div>
                        <p className="text-sm text-gray-600">Active Today</p>
                        <p className="text-2xl font-bold">45,678</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-8 w-8 text-purple-500" />
                      <div>
                        <p className="text-sm text-gray-600">New Users</p>
                        <p className="text-2xl font-bold">+1,234</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Shield className="h-8 w-8 text-orange-500" />
                      <div>
                        <p className="text-sm text-gray-600">Verified</p>
                        <p className="text-2xl font-bold">89.5%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">User Limits Management</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User ID</TableHead>
                      <TableHead>Trading Type</TableHead>
                      <TableHead>Max Leverage</TableHead>
                      <TableHead>Max Position</TableHead>
                      <TableHead>Daily Volume Limit</TableHead>
                      <TableHead>API Rate Limit</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {userLimits.map((limit) => (
                      <TableRow key={`${limit.userId}-${limit.tradingType}`}>
                        <TableCell className="font-medium">{limit.userId}</TableCell>
                        <TableCell>{limit.tradingType}</TableCell>
                        <TableCell>{limit.maxLeverage}x</TableCell>
                        <TableCell>${(limit.maxPositionSize / 1000000).toFixed(1)}M</TableCell>
                        <TableCell>${(limit.dailyVolumeLimit / 1000000).toFixed(1)}M</TableCell>
                        <TableCell>{limit.apiRateLimit}/min</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Edit className="h-3 w-3" />
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
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Risk Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-8 w-8 text-red-500" />
                      <div>
                        <p className="text-sm text-gray-600">Risk Level</p>
                        <p className="text-2xl font-bold text-red-500">High</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="h-8 w-8 text-orange-500" />
                      <div>
                        <p className="text-sm text-gray-600">Total Exposure</p>
                        <p className="text-2xl font-bold">$1.2B</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-8 w-8 text-green-500" />
                      <div>
                        <p className="text-sm text-gray-600">Insurance Fund</p>
                        <p className="text-2xl font-bold">$50M</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Emergency Controls</h3>
                  <Button variant="destructive">
                    <PowerOff className="h-4 w-4 mr-2" />
                    Trigger Circuit Breaker
                  </Button>
                </div>
                
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    Circuit breaker will pause all trading activities for 60 minutes. 
                    Use this only in extreme market conditions or security emergencies.
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Log</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-4">
                <Input placeholder="Search by admin ID..." className="max-w-sm" />
                <Select>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Action type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Actions</SelectItem>
                    <SelectItem value="pause">Pause</SelectItem>
                    <SelectItem value="resume">Resume</SelectItem>
                    <SelectItem value="emergency_stop">Emergency Stop</SelectItem>
                    <SelectItem value="create_contract">Create Contract</SelectItem>
                    <SelectItem value="delete_contract">Delete Contract</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Admin ID</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Trading Type</TableHead>
                    <TableHead>Symbol/User</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {adminActions.map((action) => (
                    <TableRow key={action.id}>
                      <TableCell>{new Date(action.timestamp).toLocaleString()}</TableCell>
                      <TableCell className="font-medium">{action.adminId}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{action.action.replace('_', ' ')}</Badge>
                      </TableCell>
                      <TableCell>{action.tradingType}</TableCell>
                      <TableCell>{action.symbol || action.userId || '-'}</TableCell>
                      <TableCell className="max-w-xs truncate">{action.reason}</TableCell>
                      <TableCell>
                        <Badge variant={action.result?.success ? 'default' : 'destructive'}>
                          {action.result?.success ? 'Success' : 'Failed'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ComprehensiveTradingAdmin;