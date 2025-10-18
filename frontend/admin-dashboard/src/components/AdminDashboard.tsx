import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Button,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Badge,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Alert,
  AlertDescription,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Switch,
  Label
} from '@/components/ui';
import { 
  Plus, 
  Play, 
  Pause, 
  Square, 
  Edit, 
  Trash2, 
  Users, 
  Activity, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Settings,
  Shield,
  Eye,
  UserPlus,
  UserMinus,
  Power,
  PowerOff
} from 'lucide-react';

// Types
interface TradingContract {
  contract_id: string;
  exchange: string;
  trading_type: string;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  status: 'pending' | 'active' | 'paused' | 'suspended' | 'delisted';
  leverage_available: number[];
  min_order_size: number;
  max_order_size: number;
  maker_fee: number;
  taker_fee: number;
  created_at: string;
  created_by: string;
}

interface User {
  user_id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'super_admin' | 'admin' | 'moderator' | 'trader' | 'viewer' | 'suspended';
  status: 'active' | 'suspended' | 'banned' | 'pending_verification';
  kyc_status: string;
  kyc_level: number;
  trading_enabled: boolean;
  withdrawal_enabled: boolean;
  deposit_enabled: boolean;
  created_at: string;
  last_login: string;
  permissions: string[];
}

interface SystemStats {
  users: {
    total: number;
    active: number;
    suspended: number;
  };
  contracts: {
    total: number;
    active: number;
    paused: number;
  };
  audit: {
    total_logs: number;
    recent_actions_24h: number;
  };
}

// API Service
class AdminAPIService {
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8005';
  private token = localStorage.getItem('admin_token');

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Contract Management
  async createContract(data: any) {
    return this.request('/api/admin/contracts/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async launchContract(contractId: string) {
    return this.request(`/api/admin/contracts/${contractId}/launch`, {
      method: 'POST',
    });
  }

  async pauseContract(contractId: string, reason: string) {
    return this.request(`/api/admin/contracts/${contractId}/pause`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async resumeContract(contractId: string) {
    return this.request(`/api/admin/contracts/${contractId}/resume`, {
      method: 'POST',
    });
  }

  async deleteContract(contractId: string, reason: string) {
    return this.request(`/api/admin/contracts/${contractId}`, {
      method: 'DELETE',
      body: JSON.stringify({ reason }),
    });
  }

  async updateContract(contractId: string, data: any) {
    return this.request(`/api/admin/contracts/${contractId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getContracts(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/contracts?${params}`);
  }

  // User Management
  async createUser(data: any) {
    return this.request('/api/admin/users/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUsers(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/users?${params}`);
  }

  async updateUser(userId: string, data: any) {
    return this.request(`/api/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async suspendUser(userId: string, reason: string) {
    return this.request(`/api/admin/users/${userId}/suspend`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async activateUser(userId: string) {
    return this.request(`/api/admin/users/${userId}/activate`, {
      method: 'POST',
    });
  }

  // Emergency Controls
  async emergencyHaltTrading(reason: string) {
    return this.request('/api/admin/emergency/halt-trading', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async emergencyResumeTrading() {
    return this.request('/api/admin/emergency/resume-trading', {
      method: 'POST',
    });
  }

  // Analytics
  async getSystemStats() {
    return this.request('/api/admin/statistics');
  }

  async getAuditLogs(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/audit-logs?${params}`);
  }
}

const apiService = new AdminAPIService();

// Main Admin Dashboard Component
export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [contracts, setContracts] = useState<TradingContract[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadSystemStats();
    loadContracts();
    loadUsers();
  }, []);

  const loadSystemStats = async () => {
    try {
      const stats = await apiService.getSystemStats();
      setSystemStats(stats);
    } catch (err) {
      setError('Failed to load system statistics');
    }
  };

  const loadContracts = async () => {
    try {
      const response = await apiService.getContracts();
      setContracts(response.contracts);
    } catch (err) {
      setError('Failed to load contracts');
    }
  };

  const loadUsers = async () => {
    try {
      const response = await apiService.getUsers();
      setUsers(response.users);
    } catch (err) {
      setError('Failed to load users');
    }
  };

  // Contract Actions
  const handleContractAction = async (action: string, contractId: string, data?: any) => {
    setLoading(true);
    try {
      switch (action) {
        case 'launch':
          await apiService.launchContract(contractId);
          break;
        case 'pause':
          await apiService.pauseContract(contractId, data.reason);
          break;
        case 'resume':
          await apiService.resumeContract(contractId);
          break;
        case 'delete':
          await apiService.deleteContract(contractId, data.reason);
          break;
      }
      await loadContracts();
      setError(null);
    } catch (err) {
      setError(`Failed to ${action} contract`);
    } finally {
      setLoading(false);
    }
  };

  // User Actions
  const handleUserAction = async (action: string, userId: string, data?: any) => {
    setLoading(true);
    try {
      switch (action) {
        case 'suspend':
          await apiService.suspendUser(userId, data.reason);
          break;
        case 'activate':
          await apiService.activateUser(userId);
          break;
        case 'update':
          await apiService.updateUser(userId, data);
          break;
      }
      await loadUsers();
      setError(null);
    } catch (err) {
      setError(`Failed to ${action} user`);
    } finally {
      setLoading(false);
    }
  };

  // Emergency Actions
  const handleEmergencyAction = async (action: string, reason?: string) => {
    setLoading(true);
    try {
      if (action === 'halt') {
        await apiService.emergencyHaltTrading(reason!);
      } else if (action === 'resume') {
        await apiService.emergencyResumeTrading();
      }
      await loadSystemStats();
      setError(null);
    } catch (err) {
      setError(`Failed to ${action} trading`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      paused: 'bg-orange-100 text-orange-800',
      suspended: 'bg-red-100 text-red-800',
      delisted: 'bg-gray-100 text-gray-800',
    };

    return (
      <Badge className={variants[status] || 'bg-gray-100 text-gray-800'}>
        {status.toUpperCase()}
      </Badge>
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'paused':
        return <Pause className="h-4 w-4 text-orange-500" />;
      case 'suspended':
      case 'delisted':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">TigerEx Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Complete control over all trading operations</p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {/* System Stats Overview */}
        {systemStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats.users.total}</div>
                <p className="text-xs text-muted-foreground">
                  {systemStats.users.active} active, {systemStats.users.suspended} suspended
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Trading Contracts</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats.contracts.total}</div>
                <p className="text-xs text-muted-foreground">
                  {systemStats.contracts.active} active, {systemStats.contracts.paused} paused
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Audit Logs</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStats.audit.total_logs}</div>
                <p className="text-xs text-muted-foreground">
                  {systemStats.audit.recent_actions_24h} actions in 24h
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Status</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Healthy</div>
                <p className="text-xs text-muted-foreground">All systems operational</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Emergency Controls */}
        <Card className="mb-8 border-red-200">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Emergency Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="destructive" className="flex items-center gap-2">
                    <PowerOff className="h-4 w-4" />
                    Halt All Trading
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Emergency Halt Trading</DialogTitle>
                  </DialogHeader>
                  <EmergencyHaltForm onSubmit={(reason) => handleEmergencyAction('halt', reason)} />
                </DialogContent>
              </Dialog>

              <Button 
                variant="outline" 
                className="flex items-center gap-2"
                onClick={() => handleEmergencyAction('resume')}
              >
                <Power className="h-4 w-4" />
                Resume Trading
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="contracts">Trading Contracts</TabsTrigger>
            <TabsTrigger value="users">User Management</TabsTrigger>
            <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <OverviewTab systemStats={systemStats} />
          </TabsContent>

          <TabsContent value="contracts" className="mt-6">
            <ContractsTab 
              contracts={contracts} 
              onAction={handleContractAction}
              onRefresh={loadContracts}
            />
          </TabsContent>

          <TabsContent value="users" className="mt-6">
            <UsersTab 
              users={users} 
              onAction={handleUserAction}
              onRefresh={loadUsers}
            />
          </TabsContent>

          <TabsContent value="audit" className="mt-6">
            <AuditLogsTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab: React.FC<{ systemStats: SystemStats | null }> = ({ systemStats }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Database Connection</span>
              <Badge className="bg-green-100 text-green-800">Connected</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Redis Cache</span>
              <Badge className="bg-green-100 text-green-800">Connected</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>API Gateway</span>
              <Badge className="bg-green-100 text-green-800">Healthy</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Trading Engine</span>
              <Badge className="bg-green-100 text-green-800">Running</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">Contract BTC/USDT launched</span>
              <span className="text-xs text-gray-500 ml-auto">2 min ago</span>
            </div>
            <div className="flex items-center gap-3">
              <UserPlus className="h-4 w-4 text-blue-500" />
              <span className="text-sm">New user registered</span>
              <span className="text-xs text-gray-500 ml-auto">5 min ago</span>
            </div>
            <div className="flex items-center gap-3">
              <Pause className="h-4 w-4 text-orange-500" />
              <span className="text-sm">Contract ETH/USDT paused</span>
              <span className="text-xs text-gray-500 ml-auto">10 min ago</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Contracts Tab Component
const ContractsTab: React.FC<{
  contracts: TradingContract[];
  onAction: (action: string, contractId: string, data?: any) => void;
  onRefresh: () => void;
}> = ({ contracts, onAction, onRefresh }) => {
  return (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Trading Contracts</h2>
        <div className="flex gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Create Contract
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Trading Contract</DialogTitle>
              </DialogHeader>
              <CreateContractForm onSubmit={onRefresh} />
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={onRefresh}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Contracts Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Exchange</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Fees</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {contracts.map((contract) => (
                <TableRow key={contract.contract_id}>
                  <TableCell className="font-medium">
                    {contract.symbol}
                  </TableCell>
                  <TableCell>{contract.exchange.toUpperCase()}</TableCell>
                  <TableCell>{contract.trading_type.replace('_', ' ').toUpperCase()}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(contract.status)}
                      {getStatusBadge(contract.status)}
                    </div>
                  </TableCell>
                  <TableCell>
                    {contract.maker_fee}% / {contract.taker_fee}%
                  </TableCell>
                  <TableCell>
                    {new Date(contract.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <ContractActions contract={contract} onAction={onAction} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Users Tab Component
const UsersTab: React.FC<{
  users: User[];
  onAction: (action: string, userId: string, data?: any) => void;
  onRefresh: () => void;
}> = ({ users, onAction, onRefresh }) => {
  return (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">User Management</h2>
        <div className="flex gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <UserPlus className="h-4 w-4" />
                Create User
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
              </DialogHeader>
              <CreateUserForm onSubmit={onRefresh} />
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={onRefresh}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Users Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Username</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>KYC</TableHead>
                <TableHead>Trading</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.user_id}>
                  <TableCell className="font-medium">
                    {user.username}
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role.replace('_', ' ').toUpperCase()}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(user.status)}
                      {getStatusBadge(user.status)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      Level {user.kyc_level}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Switch 
                      checked={user.trading_enabled} 
                      onCheckedChange={(enabled) => 
                        onAction('update', user.user_id, { trading_enabled: enabled })
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <UserActions user={user} onAction={onAction} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Audit Logs Tab Component
const AuditLogsTab: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    try {
      const response = await apiService.getAuditLogs();
      setAuditLogs(response.audit_logs);
    } catch (err) {
      console.error('Failed to load audit logs');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Audit Logs</h2>
        <Button variant="outline" onClick={loadAuditLogs}>
          Refresh
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Admin</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Details</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {auditLogs.map((log: any) => (
                <TableRow key={log.log_id}>
                  <TableCell>
                    {new Date(log.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>{log.admin_username}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{log.action}</Badge>
                  </TableCell>
                  <TableCell>
                    {log.target_type}: {log.target_id}
                  </TableCell>
                  <TableCell>
                    <pre className="text-xs">
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Helper Components
const ContractActions: React.FC<{
  contract: TradingContract;
  onAction: (action: string, contractId: string, data?: any) => void;
}> = ({ contract, onAction }) => {
  return (
    <div className="flex gap-1">
      {contract.status === 'pending' && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction('launch', contract.contract_id)}
        >
          <Play className="h-3 w-3" />
        </Button>
      )}
      {contract.status === 'active' && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction('pause', contract.contract_id, { reason: 'Admin pause' })}
        >
          <Pause className="h-3 w-3" />
        </Button>
      )}
      {contract.status === 'paused' && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction('resume', contract.contract_id)}
        >
          <Play className="h-3 w-3" />
        </Button>
      )}
      <Button
        size="sm"
        variant="outline"
        onClick={() => onAction('delete', contract.contract_id, { reason: 'Admin deletion' })}
      >
        <Trash2 className="h-3 w-3" />
      </Button>
    </div>
  );
};

const UserActions: React.FC<{
  user: User;
  onAction: (action: string, userId: string, data?: any) => void;
}> = ({ user, onAction }) => {
  return (
    <div className="flex gap-1">
      {user.status === 'active' && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction('suspend', user.user_id, { reason: 'Admin suspension' })}
        >
          <UserMinus className="h-3 w-3" />
        </Button>
      )}
      {user.status === 'suspended' && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction('activate', user.user_id)}
        >
          <UserPlus className="h-3 w-3" />
        </Button>
      )}
      <Button size="sm" variant="outline">
        <Edit className="h-3 w-3" />
      </Button>
    </div>
  );
};

// Form Components
const CreateContractForm: React.FC<{ onSubmit: () => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    exchange: '',
    trading_type: '',
    symbol: '',
    base_asset: '',
    quote_asset: '',
    maker_fee: 0.001,
    taker_fee: 0.001,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createContract(formData);
      onSubmit();
    } catch (err) {
      console.error('Failed to create contract');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="exchange">Exchange</Label>
          <Select 
            value={formData.exchange} 
            onValueChange={(value) => setFormData({...formData, exchange: value})}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select exchange" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="binance">Binance</SelectItem>
              <SelectItem value="kucoin">KuCoin</SelectItem>
              <SelectItem value="bybit">Bybit</SelectItem>
              <SelectItem value="okx">OKX</SelectItem>
              <SelectItem value="mexc">MEXC</SelectItem>
              <SelectItem value="bitget">Bitget</SelectItem>
              <SelectItem value="bitfinex">Bitfinex</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="trading_type">Trading Type</Label>
          <Select 
            value={formData.trading_type} 
            onValueChange={(value) => setFormData({...formData, trading_type: value})}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="spot">Spot</SelectItem>
              <SelectItem value="futures_perpetual">Futures Perpetual</SelectItem>
              <SelectItem value="futures_cross">Futures Cross</SelectItem>
              <SelectItem value="margin">Margin</SelectItem>
              <SelectItem value="options">Options</SelectItem>
              <SelectItem value="derivatives">Derivatives</SelectItem>
              <SelectItem value="copy_trading">Copy Trading</SelectItem>
              <SelectItem value="etf">ETF</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label htmlFor="symbol">Symbol</Label>
          <Input
            id="symbol"
            value={formData.symbol}
            onChange={(e) => setFormData({...formData, symbol: e.target.value})}
            placeholder="BTC/USDT"
          />
        </div>
        <div>
          <Label htmlFor="base_asset">Base Asset</Label>
          <Input
            id="base_asset"
            value={formData.base_asset}
            onChange={(e) => setFormData({...formData, base_asset: e.target.value})}
            placeholder="BTC"
          />
        </div>
        <div>
          <Label htmlFor="quote_asset">Quote Asset</Label>
          <Input
            id="quote_asset"
            value={formData.quote_asset}
            onChange={(e) => setFormData({...formData, quote_asset: e.target.value})}
            placeholder="USDT"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="maker_fee">Maker Fee (%)</Label>
          <Input
            id="maker_fee"
            type="number"
            step="0.0001"
            value={formData.maker_fee}
            onChange={(e) => setFormData({...formData, maker_fee: parseFloat(e.target.value)})}
          />
        </div>
        <div>
          <Label htmlFor="taker_fee">Taker Fee (%)</Label>
          <Input
            id="taker_fee"
            type="number"
            step="0.0001"
            value={formData.taker_fee}
            onChange={(e) => setFormData({...formData, taker_fee: parseFloat(e.target.value)})}
          />
        </div>
      </div>

      <Button type="submit" className="w-full">
        Create Contract
      </Button>
    </form>
  );
};

const CreateUserForm: React.FC<{ onSubmit: () => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    role: 'trader',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createUser(formData);
      onSubmit();
    } catch (err) {
      console.error('Failed to create user');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
      </div>

      <div>
        <Label htmlFor="username">Username</Label>
        <Input
          id="username"
          value={formData.username}
          onChange={(e) => setFormData({...formData, username: e.target.value})}
          required
        />
      </div>

      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
      </div>

      <div>
        <Label htmlFor="full_name">Full Name</Label>
        <Input
          id="full_name"
          value={formData.full_name}
          onChange={(e) => setFormData({...formData, full_name: e.target.value})}
        />
      </div>

      <div>
        <Label htmlFor="role">Role</Label>
        <Select 
          value={formData.role} 
          onValueChange={(value) => setFormData({...formData, role: value})}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="trader">Trader</SelectItem>
            <SelectItem value="moderator">Moderator</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="viewer">Viewer</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full">
        Create User
      </Button>
    </form>
  );
};

const EmergencyHaltForm: React.FC<{ onSubmit: (reason: string) => void }> = ({ onSubmit }) => {
  const [reason, setReason] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(reason);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="reason">Reason for Emergency Halt</Label>
        <Input
          id="reason"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Enter reason for emergency halt"
          required
        />
      </div>
      <div className="flex gap-2">
        <Button type="submit" variant="destructive" className="flex-1">
          Confirm Halt
        </Button>
      </div>
    </form>
  );
};

export default AdminDashboard;