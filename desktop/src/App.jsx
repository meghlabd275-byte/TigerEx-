/**
 * TigerEx Advanced Desktop Application v11.0.0
 * Professional trading desktop app with advanced features and modern UI
 * Built with Electron + React for cross-platform desktop support
 */

import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, IconButton, Badge, Menu, MenuItem } from '@mui/material';
import { 
  Dashboard, 
  TrendingUp, 
  AccountBalanceWallet, 
  SmartToy, 
  Settings, 
  Notifications,
  ExitToApp,
  Brightness4,
  Brightness7
} from '@mui/icons-material';

// Redux Store
import { store } from './store';
import { logout, setUser } from './store/slices/authSlice';

// Components
import Sidebar from './components/Layout/Sidebar';
import DashboardPage from './pages/DashboardPage';
import TradingPage from './pages/TradingPage';
import PortfolioPage from './pages/PortfolioPage';
import BotsPage from './pages/BotsPage';
import SettingsPage from './pages/SettingsPage';
import LoginScreen from './components/Auth/LoginScreen';

// Services
import { apiService } from './services/api';
import { websocketService } from './services/websocket';
import { electronService } from './services/electron';

// Utils
import { themeConfig } from './utils/theme';

const queryClient = new QueryClient();

const createAppTheme = (mode) => createTheme({
  ...themeConfig,
  palette: {
    mode,
    ...themeConfig.palette,
    primary: {
      main: '#FF6B00',
      light: '#FF8A33',
      dark: '#CC5500',
    },
    secondary: {
      main: '#1E88E5',
      light: '#42A5F5',
      dark: '#1565C0',
    },
    background: {
      default: mode === 'dark' ? '#0A0E1A' : '#F5F5F5',
      paper: mode === 'dark' ? '#1A1F2E' : '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
});

const AppLayout = ({ children, darkMode, toggleDarkMode }) => {
  const [notifications, setNotifications] = useState([]);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [profileAnchor, setProfileAnchor] = useState(null);
  
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    // Initialize desktop services
    electronService.initialize();
    
    // Setup IPC listeners
    electronService.on('update-available', (updateInfo) => {
      setNotifications(prev => [...prev, {
        id: Date.now(),
        type: 'info',
        title: 'Update Available',
        message: `Version ${updateInfo.version} is available`,
      }]);
    });

    return () => {
      electronService.cleanup();
    };
  }, []);

  const handleNotificationClick = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleProfileClick = (event) => {
    setProfileAnchor(event.currentTarget);
  };

  const handleLogout = () => {
    dispatch(logout());
    electronService.logout();
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <AppBar 
          position="fixed" 
          sx={{ 
            zIndex: theme.zIndex.drawer + 1,
            backgroundColor: darkMode ? '#1A1F2E' : '#FFFFFF',
            color: darkMode ? '#FFFFFF' : '#000000',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}
        >
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              TigerEx Pro
            </Typography>
            
            {/* Window Controls */}
            {electronService.isElectron() && (
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                <IconButton 
                  size="small" 
                  onClick={() => electronService.minimizeWindow()}
                >
                  <Typography variant="body2">─</Typography>
                </IconButton>
                <IconButton 
                  size="small" 
                  onClick={() => electronService.maximizeWindow()}
                >
                  <Typography variant="body2">□</Typography>
                </IconButton>
                <IconButton 
                  size="small" 
                  onClick={() => electronService.closeWindow()}
                >
                  <Typography variant="body2">×</Typography>
                </IconButton>
              </Box>
            )}
            
            <IconButton color="inherit" onClick={toggleDarkMode}>
              {darkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
            
            <IconButton color="inherit" onClick={handleNotificationClick}>
              <Badge badgeContent={notifications.length} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <IconButton color="inherit" onClick={handleProfileClick}>
              <AccountBalanceWallet />
            </IconButton>
            
            <Menu
              anchorEl={notificationAnchor}
              open={Boolean(notificationAnchor)}
              onClose={() => setNotificationAnchor(null)}
            >
              {notifications.map((notification) => (
                <MenuItem key={notification.id}>
                  <Box>
                    <Typography variant="subtitle2">{notification.title}</Typography>
                    <Typography variant="body2">{notification.message}</Typography>
                  </Box>
                </MenuItem>
              ))}
              {notifications.length === 0 && (
                <MenuItem>No new notifications</MenuItem>
              )}
            </Menu>
            
            <Menu
              anchorEl={profileAnchor}
              open={Boolean(profileAnchor)}
              onClose={() => setProfileAnchor(null)}
            >
              <MenuItem onClick={() => {}}>
                <Typography variant="body2">Profile</Typography>
              </MenuItem>
              <MenuItem onClick={() => {}}>
                <Typography variant="body2">Settings</Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <Typography variant="body2">Logout</Typography>
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        
        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App = () => {
  const [darkMode, setDarkMode] = useState(() => {
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const theme = createAppTheme(darkMode ? 'dark' : 'light');

  useEffect(() => {
    // Check for existing authentication
    const checkAuth = async () => {
      try {
        const token = await apiService.getStoredToken();
        if (token) {
          const user = await apiService.validateToken(token);
          store.dispatch(setUser(user));
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    };

    checkAuth();
  }, []);

  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Routes>
              <Route path="/login" element={<LoginScreen />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <AppLayout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
                      <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/trading" element={<TradingPage />} />
                        <Route path="/portfolio" element={<PortfolioPage />} />
                        <Route path="/bots" element={<BotsPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                      </Routes>
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Router>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  );
};

export default App;