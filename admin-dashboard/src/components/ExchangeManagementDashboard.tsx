import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Container, Typography, Button, Card, CardContent, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Select, MenuItem, FormControl, InputLabel, Switch,
  FormControlLabel, Tabs, Tab, AppBar, Toolbar, IconButton,
  Alert, Snackbar, LinearProgress, Avatar, ListItemAvatar,
  List, ListItem, ListItemText, Divider, Tooltip, Badge
} from '@mui/material';
import {
  Dashboard as DashboardIcon, People as PeopleIcon,
  ShowChart as ShowChartIcon, Settings as SettingsIcon,
  Security as SecurityIcon, Notifications as NotificationsIcon,
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon,
  Pause as PauseIcon, PlayArrow as PlayArrowIcon,
  Block as BlockIcon, CheckCircle as CheckCircleIcon,
  Warning as WarningIcon, Error as ErrorIcon,
  Refresh as RefreshIcon, Search as SearchIcon,
  FilterList as FilterIcon, Download as DownloadIcon,
  CloudUpload as CloudUploadIcon, VpnKey as VpnKeyIcon,
  AccountBalance as AccountBalanceIcon, Receipt as ReceiptIcon
} from '@mui/icons-material';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
);

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

interface Exchange {
  exchange_id: string;
  exchange_name: string;
  exchange_type: 'main' | 'white_label' | 'partner' | 'regional' | 'institutional';
  status: 'active' | 'maintenance' | 'halted' | 'suspended' | 'demo' | 'setup';
  mode: 'production' | 'staging' | 'development' | 'sandbox' | 'demo';
  deployment_type: 'cloud' | 'on_premise' | 'hybrid';
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  domain?: string;
  subdomain?: string;
  support_email?: string;
  max_users: number;
  max_trading_pairs: number;
  max_daily_volume: string;
  enabled_modules: string[];
  kyc_required: boolean;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

interface FeeTier {
  role: string;
  trading_maker_fee: number;
  trading_taker_fee: number;
  withdrawal_fee_percent: number;
  withdrawal_fee_min: number;
  withdrawal_fee_max: number;
  discount_percent: number;
}

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  status: 'active' | 'suspended' | 'banned' | 'frozen';
  kyc_status: string;
  created_at: string;
  last_login: string;
  total_volume: string;
  total_trades: number;
}

interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const ExchangeManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchange, setSelectedExchange] = useState<Exchange | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [feeTiers, setFeeTiers] = useState<FeeTier[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Dialog states
  const [createExchangeOpen, setCreateExchangeOpen] = useState(false);
  const [editExchangeOpen, setEditExchangeOpen] = useState(false);
  const [feeConfigOpen, setFeeConfigOpen] = useState(false);
  const [confirmActionOpen, setConfirmActionOpen] = useState(false);
  const [actionType, setActionType] = useState<'halt' | 'suspend' | 'delete' | null>(null);
  
  // Form states
  const [exchangeForm, setExchangeForm] = useState({
    exchange_name: '',
    exchange_type: 'white_label',
    mode: 'sandbox',
    deployment_type: 'cloud',
    primary_color: '#FF6B00',
    secondary_color: '#1A1A2E',
    max_users: 10000,
    max_trading_pairs: 50,
    max_daily_volume: '1000000',
    kyc_required: true,
    enabled_modules: ['spot_trading']
  });

  // Stats
  const [stats, setStats] = useState({
    totalExchanges: 15,
    activeExchanges: 12,
    totalUsers: 125000,
    totalVolume24h: 15000000,
    totalFees24h: 75000,
    pendingWithdrawals: 45,
    openTickets: 125,
    systemHealth: 99.9
  });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    // In production, fetch from API
    // Mock data for demonstration
    setExchanges([
      {
        exchange_id: 'TEX_12345678',
        exchange_name: 'TigerEx Main',
        exchange_type: 'main',
        status: 'active',
        mode: 'production',
        deployment_type: 'cloud',
        primary_color: '#FF6B00',
        secondary_color: '#1A1A2E',
        max_users: 1000000,
        max_trading_pairs: 500,
        max_daily_volume: '100000000',
        enabled_modules: ['spot_trading', 'margin_trading', 'futures_trading', 'nft_marketplace'],
        kyc_required: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T12:00:00Z'
      },
      {
        exchange_id: 'TEX_87654321',
        exchange_name: 'Partner Exchange 1',
        exchange_type: 'white_label',
        status: 'active',
        mode: 'production',
        deployment_type: 'cloud',
        primary_color: '#4CAF50',
        secondary_color: '#1B5E20',
        max_users: 50000,
        max_trading_pairs: 100,
        max_daily_volume: '5000000',
        enabled_modules: ['spot_trading', 'p2p_trading'],
        kyc_required: true,
        created_at: '2024-02-01T00:00:00Z',
        updated_at: '2024-02-15T12:00:00Z'
      }
    ]);

    setFeeTiers([
      { role: 'user', trading_maker_fee: 0.001, trading_taker_fee: 0.001, withdrawal_fee_percent: 0.001, withdrawal_fee_min: 0.0001, withdrawal_fee_max: 0.1, discount_percent: 0 },
      { role: 'vip_bronze', trading_maker_fee: 0.0009, trading_taker_fee: 0.001, withdrawal_fee_percent: 0.0009, withdrawal_fee_min: 0.00009, withdrawal_fee_max: 0.09, discount_percent: 10 },
      { role: 'vip_silver', trading_maker_fee: 0.0008, trading_taker_fee: 0.0009, withdrawal_fee_percent: 0.0008, withdrawal_fee_min: 0.00008, withdrawal_fee_max: 0.08, discount_percent: 20 },
      { role: 'vip_gold', trading_maker_fee: 0.0006, trading_taker_fee: 0.0008, withdrawal_fee_percent: 0.0006, withdrawal_fee_min: 0.00006, withdrawal_fee_max: 0.06, discount_percent: 35 },
      { role: 'vip_platinum', trading_maker_fee: 0.0004, trading_taker_fee: 0.0006, withdrawal_fee_percent: 0.0004, withdrawal_fee_min: 0.00004, withdrawal_fee_max: 0.04, discount_percent: 50 },
      { role: 'institutional', trading_maker_fee: 0.0002, trading_taker_fee: 0.0004, withdrawal_fee_percent: 0.0002, withdrawal_fee_min: 0.00002, withdrawal_fee_max: 0.02, discount_percent: 75 },
    ]);

    setAlerts([
      { id: '1', type: 'warning', message: 'High API latency detected on TEX_12345678', timestamp: '2024-01-15T12:00:00Z', acknowledged: false },
      { id: '2', type: 'info', message: 'Scheduled maintenance completed', timestamp: '2024-01-15T11:00:00Z', acknowledged: true },
    ]);

    setLoading(false);
  };

  const handleExchangeAction = async () => {
    if (!selectedExchange || !actionType) return;
    
    setLoading(true);
    // In production, call API
    console.log(`Performing ${actionType} on ${selectedExchange.exchange_id}`);
    
    setConfirmActionOpen(false);
    setActionType(null);
    setLoading(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'maintenance': return 'warning';
      case 'halted': return 'error';
      case 'suspended': return 'error';
      default: return 'default';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <CheckCircleIcon color="info" />;
    }
  };

  // Chart data
  const volumeChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Trading Volume (USD)',
        data: [12000000, 15000000, 18000000, 14000000, 22000000, 25000000, 28000000],
        borderColor: '#FF6B00',
        backgroundColor: 'rgba(255, 107, 0, 0.1)',
        fill: true,
      },
    ],
  };

  const feeRevenueData = {
    labels: ['Spot', 'Futures', 'Margin', 'Withdrawal', 'Other'],
    datasets: [
      {
        label: 'Fee Revenue (USD)',
        data: [45000, 30000, 15000, 20000, 10000],
        backgroundColor: ['#FF6B00', '#4CAF50', '#2196F3', '#9C27B0', '#FF9800'],
      },
    ],
  };

  // ============================================================================
  // RENDER COMPONENTS
  // ============================================================================

  const renderOverview = () => (
    <Grid container spacing={3}>
      {/* Stats Cards */}
      <Grid item xs={12} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>Total Exchanges</Typography>
            <Typography variant="h4">{stats.totalExchanges}</Typography>
            <Typography variant="body2" color="success.main">
              {stats.activeExchanges} active
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>Total Users</Typography>
            <Typography variant="h4">{stats.totalUsers.toLocaleString()}</Typography>
            <Typography variant="body2" color="textSecondary">
              Across all exchanges
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>24h Volume</Typography>
            <Typography variant="h4">${(stats.totalVolume24h / 1000000).toFixed(1)}M</Typography>
            <Typography variant="body2" color="success.main">
              +15.3% from yesterday
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={3}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>24h Fee Revenue</Typography>
            <Typography variant="h4">${stats.totalFees24h.toLocaleString()}</Typography>
            <Typography variant="body2" color="success.main">
              +8.5% from yesterday
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Charts */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Trading Volume Trend</Typography>
            <Line data={volumeChartData} height={100} />
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Fee Revenue Distribution</Typography>
            <Doughnut data={feeRevenueData} />
          </CardContent>
        </Card>
      </Grid>

      {/* Recent Alerts */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recent System Alerts</Typography>
            <List>
              {alerts.map((alert) => (
                <React.Fragment key={alert.id}>
                  <ListItem>
                    <ListItemAvatar>{getAlertIcon(alert.type)}</ListItemAvatar>
                    <ListItemText
                      primary={alert.message}
                      secondary={new Date(alert.timestamp).toLocaleString()}
                    />
                    {!alert.acknowledged && (
                      <Button size="small" variant="outlined">Acknowledge</Button>
                    )}
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderExchanges = () => (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <TextField
          placeholder="Search exchanges..."
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateExchangeOpen(true)}
        >
          Create Exchange
        </Button>
      </Box>

      {/* Exchanges Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Exchange ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Mode</TableCell>
              <TableCell>Users</TableCell>
              <TableCell>Modules</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {exchanges.map((exchange) => (
              <TableRow key={exchange.exchange_id}>
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {exchange.exchange_id}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar
                      sx={{ bgcolor: exchange.primary_color, width: 32, height: 32 }}
                    >
                      {exchange.exchange_name[0]}
                    </Avatar>
                    {exchange.exchange_name}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip label={exchange.exchange_type} size="small" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={exchange.status.toUpperCase()}
                    color={getStatusColor(exchange.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{exchange.mode}</TableCell>
                <TableCell>{exchange.max_users.toLocaleString()}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {exchange.enabled_modules.slice(0, 3).map((m) => (
                      <Chip key={m} label={m.replace('_', ' ')} size="small" variant="outlined" />
                    ))}
                    {exchange.enabled_modules.length > 3 && (
                      <Chip label={`+${exchange.enabled_modules.length - 3}`} size="small" />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedExchange(exchange);
                          setEditExchangeOpen(true);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Halt">
                      <IconButton
                        size="small"
                        color="warning"
                        onClick={() => {
                          setSelectedExchange(exchange);
                          setActionType('halt');
                          setConfirmActionOpen(true);
                        }}
                      >
                        <PauseIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => {
                          setSelectedExchange(exchange);
                          setActionType('delete');
                          setConfirmActionOpen(true);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderFeeManagement = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">Fee Tier Configuration</Typography>
        <Button variant="contained" startIcon={<EditIcon />} onClick={() => setFeeConfigOpen(true)}>
          Edit Fee Tiers
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Role</TableCell>
              <TableCell>Maker Fee</TableCell>
              <TableCell>Taker Fee</TableCell>
              <TableCell>Withdrawal Fee %</TableCell>
              <TableCell>Min Withdrawal Fee</TableCell>
              <TableCell>Max Withdrawal Fee</TableCell>
              <TableCell>Discount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {feeTiers.map((tier) => (
              <TableRow key={tier.role}>
                <TableCell>
                  <Chip label={tier.role.toUpperCase()} color="primary" variant="outlined" />
                </TableCell>
                <TableCell>{(tier.trading_maker_fee * 100).toFixed(2)}%</TableCell>
                <TableCell>{(tier.trading_taker_fee * 100).toFixed(2)}%</TableCell>
                <TableCell>{(tier.withdrawal_fee_percent * 100).toFixed(2)}%</TableCell>
                <TableCell>{tier.withdrawal_fee_min}</TableCell>
                <TableCell>{tier.withdrawal_fee_max}</TableCell>
                <TableCell>
                  {tier.discount_percent > 0 ? (
                    <Chip label={`${tier.discount_percent}% OFF`} color="success" size="small" />
                  ) : '-'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Fee Analytics */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Fee Collection by Type</Typography>
              <Bar data={feeRevenueData} height={150} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>User Fee Tier Distribution</Typography>
              <Pie
                data={{
                  labels: ['Regular', 'VIP Bronze', 'VIP Silver', 'VIP Gold', 'VIP Platinum', 'Institutional'],
                  datasets: [{
                    data: [65, 15, 10, 5, 3, 2],
                    backgroundColor: ['#9E9E9E', '#CD7F32', '#C0C0C0', '#FFD700', '#E5E4E2', '#2196F3'],
                  }],
                }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderUserManagement = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <TextField
          placeholder="Search users..."
          size="small"
          InputProps={{ startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} /> }}
        />
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<FilterIcon />}>Filter</Button>
          <Button variant="outlined" startIcon={<DownloadIcon />}>Export</Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>KYC Status</TableCell>
              <TableCell>Volume</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {/* User rows would go here */}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ bgcolor: '#1A1A2E' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#FF6B00' }}>
            🐅 TigerEx Admin Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={alerts.filter(a => !a.acknowledged).length} color="error">
              <NotificationsIcon />
            </Badge>
            <Avatar sx={{ bgcolor: '#FF6B00' }}>A</Avatar>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab icon={<DashboardIcon />} label="Overview" />
          <Tab icon={<AccountBalanceIcon />} label="Exchanges" />
          <Tab icon={<ReceiptIcon />} label="Fee Management" />
          <Tab icon={<PeopleIcon />} label="Users" />
          <Tab icon={<VpnKeyIcon />} label="API Keys" />
          <Tab icon={<SettingsIcon />} label="Settings" />
        </Tabs>
      </Box>

      {/* Content */}
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {loading && <LinearProgress />}
        
        {activeTab === 0 && renderOverview()}
        {activeTab === 1 && renderExchanges()}
        {activeTab === 2 && renderFeeManagement()}
        {activeTab === 3 && renderUserManagement()}
      </Container>

      {/* Create Exchange Dialog */}
      <Dialog open={createExchangeOpen} onClose={() => setCreateExchangeOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Exchange</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Exchange Name"
                value={exchangeForm.exchange_name}
                onChange={(e) => setExchangeForm({ ...exchangeForm, exchange_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Exchange Type</InputLabel>
                <Select
                  value={exchangeForm.exchange_type}
                  label="Exchange Type"
                  onChange={(e) => setExchangeForm({ ...exchangeForm, exchange_type: e.target.value })}
                >
                  <MenuItem value="white_label">White Label</MenuItem>
                  <MenuItem value="partner">Partner</MenuItem>
                  <MenuItem value="regional">Regional</MenuItem>
                  <MenuItem value="institutional">Institutional</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Mode</InputLabel>
                <Select
                  value={exchangeForm.mode}
                  label="Mode"
                  onChange={(e) => setExchangeForm({ ...exchangeForm, mode: e.target.value })}
                >
                  <MenuItem value="sandbox">Sandbox</MenuItem>
                  <MenuItem value="development">Development</MenuItem>
                  <MenuItem value="staging">Staging</MenuItem>
                  <MenuItem value="production">Production</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Deployment Type</InputLabel>
                <Select
                  value={exchangeForm.deployment_type}
                  label="Deployment Type"
                  onChange={(e) => setExchangeForm({ ...exchangeForm, deployment_type: e.target.value })}
                >
                  <MenuItem value="cloud">Cloud</MenuItem>
                  <MenuItem value="on_premise">On Premise</MenuItem>
                  <MenuItem value="hybrid">Hybrid</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Max Users"
                value={exchangeForm.max_users}
                onChange={(e) => setExchangeForm({ ...exchangeForm, max_users: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Max Trading Pairs"
                value={exchangeForm.max_trading_pairs}
                onChange={(e) => setExchangeForm({ ...exchangeForm, max_trading_pairs: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={exchangeForm.kyc_required}
                    onChange={(e) => setExchangeForm({ ...exchangeForm, kyc_required: e.target.checked })}
                  />
                }
                label="KYC Required"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateExchangeOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setCreateExchangeOpen(false)}>
            Create Exchange
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirm Action Dialog */}
      <Dialog open={confirmActionOpen} onClose={() => setConfirmActionOpen(false)}>
        <DialogTitle>
          {actionType === 'halt' && 'Halt Exchange'}
          {actionType === 'suspend' && 'Suspend Exchange'}
          {actionType === 'delete' && 'Delete Exchange'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {actionType} {selectedExchange?.exchange_name}?
          </Typography>
          {actionType === 'halt' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This will immediately stop all trading activity on this exchange.
            </Alert>
          )}
          {actionType === 'delete' && (
            <Alert severity="error" sx={{ mt: 2 }}>
              This action cannot be undone. All data will be permanently deleted.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmActionOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            color={actionType === 'delete' ? 'error' : 'warning'}
            onClick={handleExchangeAction}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExchangeManagementDashboard;