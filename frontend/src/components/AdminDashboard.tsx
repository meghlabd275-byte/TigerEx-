import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton,
  Tooltip,
  Divider,
  Avatar,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Fab,
  Menu,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
} from '@mui/material';
import {
  Dashboard,
  People,
  TrendingUp,
  AccountBalance,
  Security,
  Settings,
  Assessment,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Add,
  Edit,
  Delete,
  Block,
  VerifiedUser,
  ExpandMore,
  FilterList,
  Download,
  Upload,
  Visibility,
  VisibilityOff,
  Lock,
  LockOpen,
  Notifications,
  Email,
  Phone,
  LocationOn,
  AccessTime,
  CalendarToday,
  AttachMoney,
  CurrencyBitcoin,
  Speed,
  Timeline,
  PieChart,
  BarChart,
  Storage,
  Cloud,
  NetworkCheck,
  Code,
  Api,
  IntegrationInstructions,
  ManageAccounts,
  AdminPanelSettings,
  PowerSettingsNew,
  Tune,
  Policy,
  Gavel,
  RequestQuote,
  AccountTree,
  Report,
  Analytics,
  Group,
  Work,
  Business,
  Storefront,
  Receipt,
  Inventory,
  Category,
  LocalOffer,
  PriceChange,
  SwapHoriz,
  AccountBalanceWallet,
  CreditCard,
  Savings,
  ShowChart,
  CandlestickChart,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ComposedChart,
} from 'recharts';

interface User {
  id: string;
  username: string;
  email: string;
  phone: string;
  role: 'USER' | 'TRADER' | 'VIP' | 'ADMIN' | 'SUPER_ADMIN';
  status: 'ACTIVE' | 'SUSPENDED' | 'BANNED' | 'PENDING_VERIFICATION';
  kycStatus: 'NOT_STARTED' | 'PENDING' | 'VERIFIED' | 'REJECTED';
  balance: number;
  totalVolume: number;
  registrationDate: string;
  lastLogin: string;
  country: string;
  referralCode: string;
  referralCount: number;
  tradingLevel: number;
  ip: string;
  deviceInfo: string;
}

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  status: 'ACTIVE' | 'SUSPENDED' | 'MAINTENANCE';
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  tradingEnabled: boolean;
  futuresEnabled: boolean;
  marginEnabled: boolean;
  optionsEnabled: boolean;
  makerFee: number;
  takerFee: number;
  minOrderAmount: number;
  maxOrderAmount: number;
  pricePrecision: number;
  quantityPrecision: number;
}

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalTrades24h: number;
  volume24h: number;
  systemLoad: number;
  memoryUsage: number;
  cpuUsage: number;
  networkLatency: number;
  errorRate: number;
  uptime: number;
  apiRequests: number;
  databaseConnections: number;
  cacheHitRate: number;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedPair, setSelectedPair] = useState<TradingPair | null>(null);
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [showPairDialog, setShowPairDialog] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notification, setNotification] = useState<{ message: string; severity: 'success' | 'error' | 'warning' | 'info' } | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [filterRole, setFilterRole] = useState<string>('ALL');
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    const mockUsers: User[] = [
      {
        id: 'user_1',
        username: 'trader1',
        email: 'trader1@example.com',
        phone: '+1234567890',
        role: 'TRADER',
        status: 'ACTIVE',
        kycStatus: 'VERIFIED',
        balance: 50000,
        totalVolume: 1250000,
        registrationDate: '2023-01-15',
        lastLogin: '2024-11-14 10:30:00',
        country: 'US',
        referralCode: 'TRADER001',
        referralCount: 5,
        tradingLevel: 3,
        ip: '192.168.1.100',
        deviceInfo: 'Chrome on Windows',
      },
      {
        id: 'user_2',
        username: 'vip_user',
        email: 'vip@example.com',
        phone: '+1234567891',
        role: 'VIP',
        status: 'ACTIVE',
        kycStatus: 'VERIFIED',
        balance: 250000,
        totalVolume: 5000000,
        registrationDate: '2023-02-20',
        lastLogin: '2024-11-14 09:15:00',
        country: 'UK',
        referralCode: 'VIP001',
        referralCount: 12,
        tradingLevel: 8,
        ip: '192.168.1.101',
        deviceInfo: 'Safari on iPhone',
      },
    ];

    const mockPairs: TradingPair[] = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        status: 'ACTIVE',
        price: 43250.50,
        change24h: 2.34,
        volume24h: 1250000000,
        high24h: 44500.00,
        low24h: 42100.00,
        tradingEnabled: true,
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: true,
        makerFee: 0.001,
        takerFee: 0.001,
        minOrderAmount: 0.00001,
        maxOrderAmount: 9000,
        pricePrecision: 8,
        quantityPrecision: 8,
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        status: 'ACTIVE',
        price: 2280.75,
        change24h: -1.23,
        volume24h: 850000000,
        high24h: 2350.00,
        low24h: 2250.00,
        tradingEnabled: true,
        futuresEnabled: true,
        marginEnabled: true,
        optionsEnabled: false,
        makerFee: 0.001,
        takerFee: 0.001,
        minOrderAmount: 0.001,
        maxOrderAmount: 1000000,
        pricePrecision: 8,
        quantityPrecision: 8,
      },
    ];

    const mockMetrics: SystemMetrics = {
      totalUsers: 15420,
      activeUsers: 3420,
      totalTrades24h: 125000,
      volume24h: 85000000,
      systemLoad: 45.5,
      memoryUsage: 67.3,
      cpuUsage: 23.8,
      networkLatency: 12.5,
      errorRate: 0.01,
      uptime: 99.99,
      apiRequests: 5420,
      databaseConnections: 15,
      cacheHitRate: 94.5,
    };

    setUsers(mockUsers);
    setTradingPairs(mockPairs);
    setSystemMetrics(mockMetrics);
  };

  const handleUserAction = async (userId: string, action: string) => {
    setNotification({
      message: `User ${action} successfully`,
      severity: 'success',
    });
    loadAdminData();
  };

  const handleTradingPairAction = async (symbol: string, action: string) => {
    setNotification({
      message: `Trading pair ${action} successfully`,
      severity: 'success',
    });
    loadAdminData();
  };

  const filteredUsers = users.filter(user => {
    const roleMatch = filterRole === 'ALL' || user.role === filterRole;
    const statusMatch = filterStatus === 'ALL' || user.status === filterStatus;
    return roleMatch && statusMatch;
  });

  const chartData = [
    { name: 'Mon', users: 4000, trades: 2400, volume: 2400 },
    { name: 'Tue', users: 3000, trades: 1398, volume: 2210 },
    { name: 'Wed', users: 2000, trades: 9800, volume: 2290 },
    { name: 'Thu', users: 2780, trades: 3908, volume: 2000 },
    { name: 'Fri', users: 1890, trades: 4800, volume: 2181 },
    { name: 'Sat', users: 2390, trades: 3800, volume: 2500 },
    { name: 'Sun', users: 3490, trades: 4300, volume: 2100 },
  ];

  const pieData = [
    { name: 'Active Users', value: systemMetrics?.activeUsers || 0, color: '#00C49F' },
    { name: 'Inactive Users', value: (systemMetrics?.totalUsers || 0) - (systemMetrics?.activeUsers || 0), color: '#FFBB28' },
    { name: 'Suspended', value: users.filter(u => u.status === 'SUSPENDED').length, color: '#FF8042' },
    { name: 'Banned', value: users.filter(u => u.status === 'BANNED').length, color: '#0088FE' },
  ];

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#f5f5f5' }}>
      {/* Admin Header */}
      <Paper sx={{ p: 2, mb: 1, bgcolor: '#1e1e1e', color: 'white' }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="h4" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
              <AdminPanelSettings sx={{ mr: 1 }} />
              TigerEx Admin Panel
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body1" color="text.secondary">
              System Status: <Chip label="Operational" color="success" size="small" />
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
              <Button variant="contained" startIcon={<Refresh />} onClick={loadAdminData}>
                Refresh
              </Button>
              <Button variant="outlined" startIcon={<Download />}>
                Export Report
              </Button>
              <Button variant="outlined" startIcon={<Settings />}>
                Settings
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Main Admin Interface */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ bgcolor: 'white', borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Dashboard" icon={<Dashboard />} />
          <Tab label="Users" icon={<People />} />
          <Tab label="Trading Pairs" icon={<CurrencyBitcoin />} />
          <Tab label="Security" icon={<Security />} />
          <Tab label="Analytics" icon={<Analytics />} />
          <Tab label="System" icon={<Settings />} />
          <Tab label="Compliance" icon={<Gavel />} />
        </Tabs>

        {/* Dashboard Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 2 }}>
            {/* Key Metrics */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <People color="primary" />
                      <Box sx={{ ml: 1 }}>
                        <Typography color="text.secondary" gutterBottom>
                          Total Users
                        </Typography>
                        <Typography variant="h4">
                          {systemMetrics?.totalUsers?.toLocaleString() || 0}
                        </Typography>
                        <Typography color="success.main" variant="body2">
                          +12% from last month
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <TrendingUp color="success" />
                      <Box sx={{ ml: 1 }}>
                        <Typography color="text.secondary" gutterBottom>
                          24h Volume
                        </Typography>
                        <Typography variant="h4">
                          ${(systemMetrics?.volume24h || 0).toLocaleString()}
                        </Typography>
                        <Typography color="success.main" variant="body2">
                          +8% from yesterday
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <AccountBalance color="warning" />
                      <Box sx={{ ml: 1 }}>
                        <Typography color="text.secondary" gutterBottom>
                          Total Trades
                        </Typography>
                        <Typography variant="h4">
                          {systemMetrics?.totalTrades24h?.toLocaleString() || 0}
                        </Typography>
                        <Typography color="success.main" variant="body2">
                          +15% from yesterday
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Speed color="error" />
                      <Box sx={{ ml: 1 }}>
                        <Typography color="text.secondary" gutterBottom>
                          System Load
                        </Typography>
                        <Typography variant="h4">
                          {(systemMetrics?.systemLoad || 0).toFixed(1)}%
                        </Typography>
                        <Typography color="success.main" variant="body2">
                          Normal operation
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Charts */}
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Weekly Overview
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <RechartsTooltip />
                        <Line type="monotone" dataKey="users" stroke="#8884d8" name="Users" />
                        <Line type="monotone" dataKey="trades" stroke="#82ca9d" name="Trades" />
                        <Line type="monotone" dataKey="volume" stroke="#ffc658" name="Volume" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      User Distribution
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Users Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 2 }}>
            {/* User Management Controls */}
            <Paper sx={{ p: 2, mb: 2 }}>
              <Grid container alignItems="center" spacing={2}>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Filter by Role</InputLabel>
                    <Select
                      value={filterRole}
                      onChange={(e) => setFilterRole(e.target.value)}
                      label="Filter by Role"
                    >
                      <MenuItem value="ALL">All Roles</MenuItem>
                      <MenuItem value="USER">User</MenuItem>
                      <MenuItem value="TRADER">Trader</MenuItem>
                      <MenuItem value="VIP">VIP</MenuItem>
                      <MenuItem value="ADMIN">Admin</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Filter by Status</InputLabel>
                    <Select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      label="Filter by Status"
                    >
                      <MenuItem value="ALL">All Status</MenuItem>
                      <MenuItem value="ACTIVE">Active</MenuItem>
                      <MenuItem value="SUSPENDED">Suspended</MenuItem>
                      <MenuItem value="BANNED">Banned</MenuItem>
                      <MenuItem value="PENDING_VERIFICATION">Pending</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Search Users"
                    placeholder="Email, username, or ID"
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button variant="contained" startIcon={<Add />} onClick={() => setShowUserDialog(true)}>
                      Add User
                    </Button>
                    <Button variant="outlined" startIcon={<Download />}>
                      Export
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>

            {/* Users Table */}
            <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>User</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>KYC</TableCell>
                    <TableCell>Balance</TableCell>
                    <TableCell>Volume</TableCell>
                    <TableCell>Registration</TableCell>
                    <TableCell>Last Login</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 1 }}>
                            {user.username.substring(0, 2).toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {user.username}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {user.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.role}
                          color={
                            user.role === 'ADMIN' || user.role === 'SUPER_ADMIN'
                              ? 'secondary'
                              : user.role === 'VIP'
                              ? 'warning'
                              : 'default'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.status}
                          color={
                            user.status === 'ACTIVE'
                              ? 'success'
                              : user.status === 'SUSPENDED'
                              ? 'warning'
                              : 'error'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.kycStatus}
                          color={
                            user.kycStatus === 'VERIFIED'
                              ? 'success'
                              : user.kycStatus === 'PENDING'
                              ? 'warning'
                              : 'default'
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>${user.balance.toLocaleString()}</TableCell>
                      <TableCell>${user.totalVolume.toLocaleString()}</TableCell>
                      <TableCell>
                        {new Date(user.registrationDate).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {new Date(user.lastLogin).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton
                            size="small"
                            onClick={() => setSelectedUser(user)}
                          >
                            <Visibility />
                          </IconButton>
                          {user.status === 'ACTIVE' ? (
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => handleUserAction(user.id, 'suspend')}
                            >
                              <Block />
                            </IconButton>
                          ) : (
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleUserAction(user.id, 'activate')}
                            >
                              <CheckCircle />
                            </IconButton>
                          )}
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleUserAction(user.id, 'ban')}
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
        )}

        {/* Trading Pairs Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">Trading Pair Management</Typography>
                    <Button variant="contained" startIcon={<Add />} onClick={() => setShowPairDialog(true)}>
                      Add Trading Pair
                    </Button>
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Price</TableCell>
                        <TableCell>24h Change</TableCell>
                        <TableCell>24h Volume</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Trading</TableCell>
                        <TableCell>Futures</TableCell>
                        <TableCell>Margin</TableCell>
                        <TableCell>Maker Fee</TableCell>
                        <TableCell>Taker Fee</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tradingPairs.map((pair) => (
                        <TableRow key={pair.symbol}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                                {pair.baseAsset.substring(0, 2)}
                              </Avatar>
                              {pair.symbol}
                            </Box>
                          </TableCell>
                          <TableCell>${pair.price.toFixed(2)}</TableCell>
                          <TableCell>
                            <Typography
                              color={pair.change24h >= 0 ? 'success.main' : 'error.main'}
                            >
                              {pair.change24h >= 0 ? '+' : ''}
                              {pair.change24h.toFixed(2)}%
                            </Typography>
                          </TableCell>
                          <TableCell>{(pair.volume24h / 1000000).toFixed(2)}M</TableCell>
                          <TableCell>
                            <Chip
                              label={pair.status}
                              color={pair.status === 'ACTIVE' ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Switch
                              checked={pair.tradingEnabled}
                              onChange={() => handleTradingPairAction(pair.symbol, 'toggle-trading')}
                            />
                          </TableCell>
                          <TableCell>
                            <Switch
                              checked={pair.futuresEnabled}
                              onChange={() => handleTradingPairAction(pair.symbol, 'toggle-futures')}
                            />
                          </TableCell>
                          <TableCell>
                            <Switch
                              checked={pair.marginEnabled}
                              onChange={() => handleTradingPairAction(pair.symbol, 'toggle-margin')}
                            />
                          </TableCell>
                          <TableCell>{(pair.makerFee * 100).toFixed(3)}%</TableCell>
                          <TableCell>{(pair.takerFee * 100).toFixed(3)}%</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              <IconButton size="small">
                                <Edit />
                              </IconButton>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleTradingPairAction(pair.symbol, 'suspend')}
                              >
                                <Block />
                              </IconButton>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>

      {/* Notification Snackbar */}
      <Snackbar
        open={!!notification}
        autoHideDuration={6000}
        onClose={() => setNotification(null)}
      >
        {notification ? (
          <Alert
            severity={notification.severity}
            onClose={() => setNotification(null)}
          >
            {notification.message}
          </Alert>
        ) : undefined}
      </Snackbar>
    </Box>
  );
};

export default AdminDashboard;