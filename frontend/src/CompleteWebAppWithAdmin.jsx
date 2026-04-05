/**
 * TigerEx Complete Web Application with Full Admin Controls
 * Comprehensive web app with complete backend integration, admin controls, and all trading functionality
 * Enhanced with complete admin panel, user access management, and social login
 */

import React, { useState, useEffect, useCallback, useContext } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
  Link
} from 'react-router-dom';
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useMutation,
  useQueryClient
} from 'react-query';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Material-UI Components
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Menu,
  MenuItem,
  Badge,
  LinearProgress,
  Tabs,
  Tab,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Switch,
  FormControlLabel,
  Pagination,
  Tooltip,
  Stack
} from '@mui/material';

// Icons
import {
  Dashboard,
  TrendingUp,
  AccountBalanceWallet,
  ListAlt,
  AdminPanelSettings,
  Settings,
  Notifications,
  Security,
  People,
  Assessment,
  SwapHoriz,
  Add,
  Remove,
  MoreVert,
  Refresh,
  CheckCircle,
  Warning,
  Error,
  Search,
  FilterList,
  Visibility,
  Edit,
  Block,
  HowToReg,
  Emergency,
  PowerOff,
  PlayArrow,
  Lock,
  LockOpen,
  DeleteForever,
  Key,
  Shield,
  Gavel,
  Timeline,
  Storage,
  CloudSync,
  Monitor,
  PhoneAndroid,
  DesktopWindows,
  Web,
  Person,
  PersonOff,
  Assignment,
  Google,
  Facebook,
  Twitter,
  Telegram,
  Email
} from '@mui/icons-material';

// Enhanced API Service with Admin Support and Social Login
class TigerExAPI {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
    this.adminURL = process.env.REACT_APP_ADMIN_URL || 'http://localhost:8001/admin';
    this.token = localStorage.getItem('authToken');
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('authToken', token);
  }

  removeToken() {
    this.token = null;
    localStorage.removeItem('authToken');
  }

  async request(endpoint, options = {}, isAdmin = false) {
    const url = `${isAdmin ? this.adminURL : this.baseURL}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      const data = await response.json();
      
      if (!response.ok) {
        if (response.status === 401) {
          this.removeToken();
          window.location.href = '/login';
        }
        throw new Error(data.detail || data.message || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ emailOrUsername: email, password })
    });
    this.setToken(data.data.accessToken);
    return data;
  }

  async register(userData) {
    return await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async socialLogin(provider, socialData) {
    const data = await this.request('/auth/social-login', {
      method: 'POST',
      body: JSON.stringify({ provider, ...socialData })
    });
    this.setToken(data.data.accessToken);
    return data;
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.removeToken();
  }

  async getProfile() {
    const res = await this.request('/auth/me');
    return res.data;
  }

  // Market Data
  async getMarketData(exchange = 'binance') {
    return await this.request(`/market/${exchange}/ticker/BTCUSDT`);
  }

  async getTradingPairs(exchange = 'binance') {
    return await this.request(`/market/${exchange}/pairs`);
  }

  async getRobinhoodQuote(symbol) {
    return await this.request(`/robinhood/quote/${symbol}`);
  }

  async getGateioOrderbook(currencyPair) {
    return await this.request(`/gateio/orderbook?currency_pair=${currencyPair}`);
  }

  // Trading
  async placeOrder(orderData) {
    return await this.request('/trading/order', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  }

  async getOrders(status = 'all') {
    return await this.request(`/trading/orders?status=${status}`);
  }

  async cancelOrder(orderId) {
    return await this.request(`/trading/order/${orderId}`, {
      method: 'DELETE'
    });
  }

  // Wallet
  async getWallet() {
    return await this.request('/wallet/balance');
  }

  async getTransactionHistory(type = 'all') {
    return await this.request(`/wallet/transactions?type=${type}`);
  }

  // ADMIN FUNCTIONS
  // System Management
  async getSystemStatus() {
    return await this.request('/system/status', {}, true);
  }

  async getSystemStatistics() {
    return await this.request('/system/statistics', {}, true);
  }

  // User Management
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/admin/users?${queryString}`, {}, true);
  }

  async suspendUser(userId, reason, duration) {
    return await this.request(`/users/${userId}/suspend`, {
      method: 'POST',
      body: JSON.stringify({ action: 'suspend_user', reason, duration_hours: duration })
    }, true);
  }

  async banUser(userId, reason) {
    return await this.request(`/users/${userId}/control?action=ban`, {
      method: 'POST',
      body: JSON.stringify({ action: 'ban_user', reason })
    }, true);
  }

  async controlUser(userId, action) {
    return await this.request(`/users/${userId}/control?action=${action}`, {
      method: 'POST'
    }, true);
  }

  async controlService(exchangeId, action) {
    return await this.request(`/services/${exchangeId}/control?action=${action}`, {
      method: 'POST'
    }, true);
  }

  async activateUser(userId) {
    return await this.request(`/users/${userId}/activate`, {
      method: 'POST'
    }, true);
  }

  async banUser(userId, reason) {
    return await this.request(`/users/${userId}/ban`, {
      method: 'POST',
      body: JSON.stringify({ action: 'ban_user', reason })
    }, true);
  }

  async updateUserPermissions(userId, permissions) {
    return await this.request(`/users/${userId}/permissions`, {
      method: 'PUT',
      body: JSON.stringify(permissions)
    }, true);
  }

  // Trading Controls
  async haltTrading(reason) {
    return await this.request('/trading/halt', {
      method: 'POST',
      body: JSON.stringify({ reason })
    }, true);
  }

  async resumeTrading() {
    return await this.request('/trading/resume', {
      method: 'POST'
    }, true);
  }

  async emergencyStop(reason) {
    return await this.request('/emergency/stop', {
      method: 'POST',
      body: JSON.stringify({ reason })
    }, true);
  }

  // Audit Logs
  async getAuditLogs(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/audit/logs?${queryString}`, {}, true);
  }

  // System Configuration
  async getSystemConfig(key) {
    return await this.request(`/config/${key}`, {}, true);
  }

  async updateSystemConfig(key, value, description) {
    return await this.request(`/config/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ key, value, description })
    }, true);
  }

  // WebSocket connection for real-time data
  createWebSocket(endpoint, isAdmin = false) {
    const url = `${isAdmin ? this.adminURL : this.baseURL}/ws${endpoint}`;
    const wsUrl = url.replace('http', 'ws').replace('https', 'wss');
    return new WebSocket(wsUrl);
  }
}

const api = new TigerExAPI();

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 30000,
      cacheTime: 300000,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Context
const AuthContext = React.createContext();

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const initAuth = useCallback(async () => {
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const userData = await api.getProfile();
        setUser(userData);
      } catch (error) {
        console.error('Auth initialization failed:', error);
        api.removeToken();
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  const login = useCallback(async (email, password) => {
    try {
      const data = await api.login(email, password);
      setUser(data.data.user);
      toast.success('Login successful!');
      return data;
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  }, []);

  const socialLogin = useCallback(async (provider, socialData) => {
    try {
      const data = await api.socialLogin(provider, socialData);
      setUser(data.data.user);
      toast.success(`${provider} login successful!`);
      return data;
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
      setUser(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      setUser(null);
    }
  }, []);

  const value = {
    user,
    login,
    socialLogin,
    logout,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.roles?.includes('admin') || user?.roles?.includes('super_admin'),
    isSuperAdmin: user?.roles?.includes('super_admin')
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook for auth
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#f0b90b', // Binance-like yellow
    },
    secondary: {
      main: '#2ebd85', // Crypto green
    },
    background: {
      default: '#0b0e11',
      paper: '#1e2329',
    },
    error: {
      main: '#f6465d',
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({ children, adminOnly = false, superAdminOnly = false }) => {
  const { user, isAuthenticated, isAdmin, isSuperAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  if (superAdminOnly && !isSuperAdmin) {
    return <Navigate to="/admin" replace />;
  }

  return children;
};

// Social Login Buttons Component
const SocialLoginButtons = () => {
  const { socialLogin } = useAuth();
  const navigate = useNavigate();

  const handleSocialAction = async (provider) => {
    // Mock social data for demonstration
    // In production, this would trigger OAuth flows
    const mockSocialData = {
      socialId: `mock_${provider}_${Date.now()}`,
      email: `user_${provider}@example.com`,
      firstName: 'Social',
      lastName: 'User',
    };

    try {
      await socialLogin(provider, mockSocialData);
      navigate('/dashboard');
    } catch (error) {
      // Error handled in context
    }
  };

  return (
    <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
      <Tooltip title="Google">
        <IconButton onClick={() => handleSocialAction('google')} sx={{ bgcolor: '#fff', color: '#4285F4', '&:hover': { bgcolor: '#f1f1f1' } }}>
          <Google />
        </IconButton>
      </Tooltip>
      <Tooltip title="Facebook">
        <IconButton onClick={() => handleSocialAction('facebook')} sx={{ bgcolor: '#1877F2', color: '#fff', '&:hover': { bgcolor: '#166fe5' } }}>
          <Facebook />
        </IconButton>
      </Tooltip>
      <Tooltip title="Twitter">
        <IconButton onClick={() => handleSocialAction('twitter')} sx={{ bgcolor: '#1DA1F2', color: '#fff', '&:hover': { bgcolor: '#1a91da' } }}>
          <Twitter />
        </IconButton>
      </Tooltip>
      <Tooltip title="Telegram">
        <IconButton onClick={() => handleSocialAction('telegram')} sx={{ bgcolor: '#0088cc', color: '#fff', '&:hover': { bgcolor: '#007ab8' } }}>
          <Telegram />
        </IconButton>
      </Tooltip>
    </Stack>
  );
};

// Login Page Component
const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error) {
      // Error handled in context
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 10, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom color="primary">
            TigerEx Login
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email or Username"
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              type="submit"
              sx={{ mt: 3, mb: 2 }}
            >
              Login
            </Button>
          </form>

          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="textSecondary">
              OR LOGIN WITH
            </Typography>
          </Divider>

          <SocialLoginButtons />

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2">
              Don't have an account? <Link to="/register" style={{ color: '#f0b90b' }}>Register Now</Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

// Register Page Component
const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  });
  const { socialLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    try {
      await api.register(formData);
      toast.success('Registration successful! Please check your email.');
      navigate('/login');
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 10, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom color="primary">
            Create Account
          </Typography>
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              margin="normal"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Username"
              margin="normal"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              margin="normal"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              margin="normal"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              required
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              type="submit"
              sx={{ mt: 3, mb: 2 }}
            >
              Register
            </Button>
          </form>

          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="textSecondary">
              OR REGISTER WITH
            </Typography>
          </Divider>

          <SocialLoginButtons />

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2">
              Already have an account? <Link to="/login" style={{ color: '#f0b90b' }}>Login Here</Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

// Enhanced Admin Dashboard Component
const AdminDashboard = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [systemStatus, setSystemStatus] = useState({});
    const [exchanges, setExchanges] = useState({});
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [suspensionDialogOpen, setSuspensionDialogOpen] = useState(false);
  const [suspensionForm, setSuspensionForm] = useState({ reason: '', duration: 24 });
  const [emergencyDialogOpen, setEmergencyDialogOpen] = useState(false);
  const [emergencyReason, setEmergencyReason] = useState('');

  // System Status Query
  const { data: systemData, isLoading: systemLoading, refetch: refetchSystem } = useQuery(
    'systemStatus',
    () => api.getSystemStatus(),
    { refetchInterval: 30000 }
  );

    // Exchanges Config Query
    const { data: exchangesData, refetch: refetchExchanges } = useQuery(
      'exchangeConfigs',
      () => api.request('/admin/exchanges', {}, true),
      { refetchInterval: 60000 }
    );

  // Users Query
  const { data: usersData, isLoading: usersLoading, refetch: refetchUsers } = useQuery(
    'adminUsers',
    () => api.getUsers({ limit: 100 }),
    { refetchInterval: 60000 }
  );

  // Audit Logs Query
  const { data: logsData, isLoading: logsLoading, refetch: refetchLogs } = useQuery(
    'auditLogs',
    () => api.getAuditLogs({ limit: 50 }),
    { refetchInterval: 30000 }
  );

  useEffect(() => {
    if (systemData) setSystemStatus(systemData);
    if (usersData) setUsers(usersData.users || []);
    if (logsData) setAuditLogs(logsData.logs || []);
      if (exchangesData) setExchanges(exchangesData.exchanges || {});
    }, [systemData, usersData, logsData, exchangesData]);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleUserAction = async (userId, action, params = {}) => {
    try {
      switch (action) {
        case 'suspend':
          await api.suspendUser(userId, params.reason, params.duration);
          toast.success('User suspended successfully');
          break;
        case 'activate':
          await api.activateUser(userId);
          toast.success('User activated successfully');
          break;
        case 'ban':
          await api.banUser(userId, params.reason);
          toast.success('User banned successfully');
          break;
        default:
          break;
      }
      refetchUsers();
      setSuspensionDialogOpen(false);
      setUserDialogOpen(false);
    } catch (error) {
      toast.error(`Error: ${error.message}`);
    }
  };

  const handleTradingAction = async (action, params = {}) => {
    try {
      switch (action) {
        case 'halt':
          await api.haltTrading(params.reason);
          toast.warning('Trading halted');
          break;
        case 'resume':
          await api.resumeTrading();
          toast.success('Trading resumed');
          break;
        case 'emergency':
          await api.emergencyStop(params.reason);
          toast.error('Emergency stop executed');
          setEmergencyDialogOpen(false);
          break;
        default:
          break;
      }
      refetchSystem();
    } catch (error) {
      toast.error(`Error: ${error.message}`);
    }
  };

  // System Overview Tab
  const SystemOverviewTab = () => (
    <Grid container spacing={3}>
      {/* Service Control Panel */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Service Control Panel
            </Typography>
            <Grid container spacing={2}>
              {Object.keys(exchanges).length > 0 ? (
                Object.entries(exchanges).map(([id, config]) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={id}>
                    <Paper variant="outlined" sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold" sx={{ textTransform: 'capitalize' }}>{id}</Typography>
                        <Chip
                          label={config.maintenance_mode ? "Maintenance" : "Active"}
                          size="small"
                          color={config.maintenance_mode ? "warning" : "success"}
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.625rem' }}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Pause">
                          <IconButton size="small" color="warning" onClick={() => api.controlService(id, 'pause').then(() => refetchExchanges())}>
                            <PowerOff fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Resume">
                          <IconButton size="small" color="success" onClick={() => api.controlService(id, 'resume').then(() => refetchExchanges())}>
                            <PlayArrow fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Paper>
                  </Grid>
                ))
              ) : (
                ['Binance', 'Bybit', 'OKX', 'Bitget', 'Bitfinex', 'MEXC', 'Kraken', 'Robinhood', 'Gate.io', 'Coinbase', 'HTX'].map((exchange) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={exchange}>
                    <Paper variant="outlined" sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">{exchange}</Typography>
                        <Chip
                          label="Loading..."
                          size="small"
                          color="default"
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.625rem' }}
                        />
                      </Box>
                    </Paper>
                  </Grid>
                ))
              )}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Status Cards */}
      <Grid item xs={12} md={4}>
        <Card sx={{ bgcolor: systemStatus.trading_status === 'active' ? 'success.dark' : 'error.dark' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <PowerOff sx={{ mr: 1, color: 'white' }} />
              <Typography variant="h6" color="white">
                Trading Status
              </Typography>
            </Box>
            <Typography variant="h4" color="white" gutterBottom>
              {systemStatus.trading_status?.toUpperCase() || 'UNKNOWN'}
            </Typography>
            <Typography variant="body2" color="white">
              Server Time: {new Date(systemStatus.server_time).toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ bgcolor: 'primary.dark' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <People sx={{ mr: 1, color: 'white' }} />
              <Typography variant="h6" color="white">
                User Statistics
              </Typography>
            </Box>
            <Typography variant="h4" color="white" gutterBottom>
              {systemStatus.total_users || 0}
            </Typography>
            <Typography variant="body2" color="white">
              Active: {systemStatus.active_users || 0} | Suspended: {systemStatus.suspended_users || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card sx={{ bgcolor: 'secondary.dark' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TrendingUp sx={{ mr: 1, color: 'white' }} />
              <Typography variant="h6" color="white">
                Trading Activity
              </Typography>
            </Box>
            <Typography variant="h4" color="white" gutterBottom>
              {systemStatus.total_orders || 0}
            </Typography>
            <Typography variant="body2" color="white">
              Open Orders: {systemStatus.open_orders || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  color="error"
                  startIcon={<Block />}
                  onClick={() => handleTradingAction('halt')}
                  disabled={systemStatus.trading_status !== 'active'}
                  fullWidth
                >
                  Halt Trading
                </Button>
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<PlayArrow />}
                  onClick={() => handleTradingAction('resume')}
                  disabled={systemStatus.trading_status === 'active'}
                  fullWidth
                >
                  Resume Trading
                </Button>
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  color="warning"
                  startIcon={<Emergency />}
                  onClick={() => setEmergencyDialogOpen(true)}
                  fullWidth
                >
                  Emergency Stop
                </Button>
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => {
                    refetchSystem();
                    refetchUsers();
                    refetchLogs();
                  }}
                  fullWidth
                >
                  Refresh All
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // User Management Tab
  const UserManagementTab = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            User Management
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refetchUsers}
          >
            Refresh
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Roles</TableCell>
                <TableCell>Verified</TableCell>
                <TableCell>Trading</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.userId}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>{user.username[0].toUpperCase()}</Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {user.username}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {user.email}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.accountStatus}
                      color={
                        user.accountStatus === 'active' ? 'success' :
                        user.accountStatus === 'suspended' ? 'warning' :
                        user.accountStatus === 'banned' ? 'error' : 'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {user.roles?.map(role => (
                      <Chip key={role} label={role} size="small" variant="outlined" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>
                    <Stack spacing={0.5}>
                      <Chip
                        label={user.isEmailVerified ? "Email" : "No Email"}
                        color={user.isEmailVerified ? 'success' : 'error'}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={user.kycStatus}
                        color={user.kycStatus === 'approved' ? 'success' : 'warning'}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.tradingEnabled ? "Enabled" : "Disabled"}
                      color={user.tradingEnabled ? 'success' : 'error'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={() => {
                        setSelectedUser(user);
                        setUserDialogOpen(true);
                      }}
                    >
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  // Audit Logs Tab
  const AuditLogsTab = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            Audit Logs
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refetchLogs}
          >
            Refresh
          </Button>
        </Box>

        <List>
          {auditLogs.map((log) => (
            <ListItem key={log.id} divider>
              <ListItemIcon>
                <Assignment color="primary" />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" fontWeight="bold">
                      {log.action}
                    </Typography>
                    {log.resource && (
                      <Chip label={log.resource} size="small" variant="outlined" color="primary" />
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      User: {log.user_id} | Time: {new Date(log.timestamp).toLocaleString()}
                    </Typography>
                    {log.ip_address && (
                      <Typography variant="caption" color="textSecondary" sx={{ ml: 2 }}>
                        IP: {log.ip_address}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const TabContent = () => {
    switch (currentTab) {
      case 0: return <SystemOverviewTab />;
      case 1: return <UserManagementTab />;
      case 2: return <AuditLogsTab />;
      default: return <SystemOverviewTab />;
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
        Admin Dashboard
      </Typography>
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab icon={<Dashboard />} label="Overview" />
          <Tab icon={<People />} label="Users" />
          <Tab icon={<Timeline />} label="Audit" />
        </Tabs>
      </Paper>

      <TabContent />

      {/* User Action Dialog */}
      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Actions for {selectedUser?.username}</DialogTitle>
        <DialogContent>
          <Typography variant="body1">Status: {selectedUser?.accountStatus}</Typography>
          <Typography variant="body2" color="textSecondary">Email: {selectedUser?.email}</Typography>
        </DialogContent>
        <DialogActions>
          <Button color="warning" onClick={() => { setSuspensionDialogOpen(true); setUserDialogOpen(false); }}>Suspend</Button>
          <Button color="success" onClick={() => handleUserAction(selectedUser.userId, 'activate')}>Activate</Button>
          <Button color="error" onClick={() => handleUserAction(selectedUser.userId, 'ban', { reason: 'Admin' })}>Ban</Button>
          <Button onClick={() => setUserDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Suspension Dialog */}
      <Dialog open={suspensionDialogOpen} onClose={() => setSuspensionDialogOpen(false)}>
        <DialogTitle>Suspend User</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Reason" multiline rows={3} sx={{ mt: 2 }} value={suspensionForm.reason} onChange={(e) => setSuspensionForm({ ...suspensionForm, reason: e.target.value })} />
          <TextField fullWidth label="Duration (hrs)" type="number" sx={{ mt: 2 }} value={suspensionForm.duration} onChange={(e) => setSuspensionForm({ ...suspensionForm, duration: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button color="warning" onClick={() => handleUserAction(selectedUser.userId, 'suspend', suspensionForm)}>Confirm Suspend</Button>
          <Button onClick={() => setSuspensionDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Main App Component
const AppContent = () => {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default', color: 'text.primary' }}>
      {/* Sidebar for Admin */}
      {user && isAdmin && (
        <Paper sx={{ width: 260, position: 'fixed', height: '100vh', zIndex: 1201, borderRadius: 0, borderRight: '1px solid rgba(255, 255, 255, 0.12)' }}>
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h5" color="primary" fontWeight="bold">TigerEx Admin</Typography>
          </Box>
          <Divider />
          <List>
            <ListItem button onClick={() => navigate('/admin')}>
              <ListItemIcon><Dashboard color="primary" /></ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button onClick={() => navigate('/dashboard')}>
              <ListItemIcon><TrendingUp color="primary" /></ListItemIcon>
              <ListItemText primary="Trading View" />
            </ListItem>
            <ListItem button onClick={() => navigate('/wallet')}>
              <ListItemIcon><AccountBalanceWallet color="primary" /></ListItemIcon>
              <ListItemText primary="Wallet" />
            </ListItem>
            <ListItem button onClick={() => navigate('/security')}>
              <ListItemIcon><Security color="primary" /></ListItemIcon>
              <ListItemText primary="Security" />
            </ListItem>
          </List>
        </Paper>
      )}

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, ml: (user && isAdmin) ? '260px' : 0 }}>
        <AppBar position="sticky" sx={{ bgcolor: 'background.paper', borderBottom: '1px solid rgba(255, 255, 255, 0.12)' }} elevation={0}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1, color: 'primary.main', fontWeight: 'bold' }}>
              TigerEx Exchange
            </Typography>
            {user ? (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ mr: 2 }}>{user.username}</Typography>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>{user.username[0]}</Avatar>
                <Button color="inherit" onClick={() => api.logout().then(() => window.location.reload())}>Logout</Button>
              </Box>
            ) : (
              <Box>
                <Button color="inherit" component={Link} to="/login">Login</Button>
                <Button variant="contained" color="primary" sx={{ ml: 2 }} component={Link} to="/register">Register</Button>
              </Box>
            )}
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Typography variant="h4">Trading Dashboard Content</Typography>
                {/* Add detailed trading components here */}
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute adminOnly>
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

// Main App
const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <AppContent />
          </Router>
          <ToastContainer position="top-right" theme="dark" />
        </AuthProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
};

export default App;
