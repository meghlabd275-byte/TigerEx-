/**
 * TigerEx Advanced Web Application v11.0.0
 * Modern responsive web trading platform with comprehensive features
 * Built with React, Redux, and Material-UI for optimal user experience
 */

import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Container, Snackbar, Alert } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';

// Redux Store
import { store } from './store';
import { checkAuth, logout, setUser } from './store/slices/authSlice';

// Components
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import Footer from './components/Layout/Footer';
import Dashboard from './pages/Dashboard';
import TradingInterface from './pages/TradingInterface';
import Portfolio from './pages/Portfolio';
import Markets from './pages/Markets';
import TradingBots from './pages/TradingBots';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import KYCVerification from './pages/KYCVerification';
import AdminDashboard from './pages/Admin/Dashboard';
import UserManagement from './pages/Admin/UserManagement';
import TradingControls from './pages/Admin/TradingControls';
import SystemMonitoring from './pages/Admin/SystemMonitoring';

// Services
import { apiService } from './services/api';
import { websocketService } from './services/websocket';
import { notificationService } from './services/notifications';
import { priceAlertService } from './services/priceAlerts';

// Hooks
import { useWebSocket } from './hooks/useWebSocket';
import { useNotification } from './hooks/useNotification';
import { useThemeMode } from './hooks/useThemeMode';

// Utils
import { themeConfig } from './utils/theme';
import ProtectedRoute from './utils/ProtectedRoute';

const queryClient = new QueryClient();

// Theme configuration
const createAppTheme = (mode) => createTheme({
  palette: {
    mode,
    primary: {
      main: '#FF6B00',
      light: '#FF8A33',
      dark: '#CC5500',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#1E88E5',
      light: '#42A5F5',
      dark: '#1565C0',
      contrastText: '#ffffff',
    },
    background: {
      default: mode === 'dark' ? '#0A0E1A' : '#FAFAFA',
      paper: mode === 'dark' ? '#1A1F2E' : '#FFFFFF',
    },
    text: {
      primary: mode === 'dark' ? '#FFFFFF' : '#212121',
      secondary: mode === 'dark' ? '#B0B0B0' : '#666666',
    },
    success: {
      main: '#4CAF50',
      light: '#66BB6A',
      dark: '#388E3C',
    },
    error: {
      main: '#F44336',
      light: '#EF5350',
      dark: '#D32F2F',
    },
    warning: {
      main: '#FF9800',
      light: '#FFA726',
      dark: '#F57C00',
    },
    info: {
      main: '#2196F3',
      light: '#42A5F5',
      dark: '#1976D2',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.6,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
  ...themeConfig,
});

// Main App Component
const App = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user, token } = useSelector((state) => state.auth);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  const { darkMode, toggleTheme } = useThemeMode();
  const { notification } = useNotification();
  
  const theme = createAppTheme(darkMode ? 'dark' : 'light');
  
  // WebSocket connection for real-time data
  const { isConnected, lastMessage } = useWebSocket({
    url: process.env.REACT_APP_WS_URL,
    token: token,
    onConnect: () => {
      console.log('WebSocket connected');
      setSnackbar({
        open: true,
        message: 'Connected to real-time data',
        severity: 'success'
      });
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected');
      setSnackbar({
        open: true,
        message: 'Disconnected from real-time data',
        severity: 'warning'
      });
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setSnackbar({
        open: true,
        message: 'Connection error',
        severity: 'error'
      });
    }
  });

  // Check authentication on app load
  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        const storedToken = localStorage.getItem('tigerex_token');
        if (storedToken) {
          const response = await apiService.validateToken(storedToken);
          dispatch(setUser(response.data.user));
          dispatch(checkAuth.fulfilled());
        } else {
          dispatch(checkAuth.rejected());
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        dispatch(checkAuth.rejected());
        localStorage.removeItem('tigerex_token');
      }
    };

    checkAuthentication();
  }, [dispatch]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        
        switch (data.type) {
          case 'price_update':
            // Update price data in Redux store
            store.dispatch({
              type: 'prices/updatePrice',
              payload: data.payload
            });
            break;
            
          case 'order_update':
            // Update order status
            store.dispatch({
              type: 'orders/updateOrder',
              payload: data.payload
            });
            
            // Show notification
            setSnackbar({
              open: true,
              message: `Order ${data.payload.status}: ${data.payload.symbol}`,
              severity: data.payload.status === 'filled' ? 'success' : 'info'
            });
            break;
            
          case 'balance_update':
            // Update user balance
            store.dispatch({
              type: 'user/updateBalance',
              payload: data.payload
            });
            break;
            
          case 'alert':
            // Handle price alerts
            setSnackbar({
              open: true,
              message: data.payload.message,
              severity: data.payload.severity
            });
            break;
            
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  // Handle notifications
  useEffect(() => {
    if (notification) {
      setSnackbar({
        open: true,
        message: notification.message,
        severity: notification.type
      });
    }
  }, [notification]);

  // Initialize services when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      // Initialize notification service
      notificationService.initialize(user.user_id);
      
      // Initialize price alerts
      priceAlertService.initialize(user.user_id);
      
      // Request notification permission
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }
    }
  }, [isAuthenticated, user]);

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const MainLayout = ({ children }) => (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar 
        onMenuClick={handleDrawerToggle}
        darkMode={darkMode}
        toggleTheme={toggleTheme}
      />
      <Sidebar 
        open={sidebarOpen}
        onClose={handleDrawerToggle}
        userRole={user?.role}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: 8, // Navbar height
          pb: 8, // Footer height
          bgcolor: theme.palette.background.default,
          minHeight: '100vh'
        }}
      >
        <Container maxWidth="xl" sx={{ py: 3 }}>
          {children}
        </Container>
        <Footer />
      </Box>
    </Box>
  );

  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected Routes */}
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/trading" element={<TradingInterface />} />
                        <Route path="/portfolio" element={<Portfolio />} />
                        <Route path="/markets" element={<Markets />} />
                        <Route path="/bots" element={<TradingBots />} />
                        <Route path="/kyc" element={<KYCVerification />} />
                        
                        {/* Admin Routes */}
                        <Route
                          path="/admin/*"
                          element={
                            <ProtectedRoute requiredRole="admin">
                              <Routes>
                                <Route path="/dashboard" element={<AdminDashboard />} />
                                <Route path="/users" element={<UserManagement />} />
                                <Route path="/trading" element={<TradingControls />} />
                                <Route path="/monitoring" element={<SystemMonitoring />} />
                              </Routes>
                            </ProtectedRoute>
                          }
                        />
                      </Routes>
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Router>
          
          {/* Global Snackbar */}
          <Snackbar
            open={snackbar.open}
            autoHideDuration={6000}
            onClose={handleCloseSnackbar}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Alert
              onClose={handleCloseSnackbar}
              severity={snackbar.severity}
              sx={{ width: '100%' }}
            >
              {snackbar.message}
            </Alert>
          </Snackbar>
          
          {/* Connection Status Indicator */}
          <Box
            sx={{
              position: 'fixed',
              top: 80,
              right: 20,
              zIndex: 1000,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                backgroundColor: theme.palette.background.paper,
                padding: 1,
                borderRadius: 1,
                boxShadow: theme.shadows[2],
              }}
            >
              <Box
                sx={{
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  backgroundColor: isConnected ? theme.palette.success.main : theme.palette.error.main,
                }}
              />
              <Typography variant="caption">
                {isConnected ? 'Connected' : 'Disconnected'}
              </Typography>
            </Box>
          </Box>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  );
};

export default App;