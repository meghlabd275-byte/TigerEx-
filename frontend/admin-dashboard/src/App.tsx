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
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SnackbarProvider } from 'notistack';

// Components
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import LoginPage from './pages/Auth/LoginPage';
import LoadingScreen from './components/Common/LoadingScreen';

// Pages
import Dashboard from './pages/Dashboard/Dashboard';
import UserManagement from './pages/Users/UserManagement';
import KYCManagement from './pages/KYC/KYCManagement';
import TradingOverview from './pages/Trading/TradingOverview';
import P2PManagement from './pages/P2P/P2PManagement';
import BlockchainManagement from './pages/Blockchain/BlockchainManagement';
import WhiteLabelManagement from './pages/WhiteLabel/WhiteLabelManagement';
import SystemSettings from './pages/Settings/SystemSettings';
import Analytics from './pages/Analytics/Analytics';
import AffiliateManagement from './pages/Affiliate/AffiliateManagement';
import CustomerSupport from './pages/Support/CustomerSupport';
import TechnicalDashboard from './pages/Technical/TechnicalDashboard';
import ListingManagement from './pages/Listing/ListingManagement';

// Contexts
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Types
import { AdminRole } from './types/auth';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#f7931a', // Bitcoin orange
      light: '#ffb74d',
      dark: '#e65100',
    },
    secondary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    background: {
      default: '#0a0e1a',
      paper: '#1a1d29',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Route configuration based on admin roles
const getRoutesByRole = (role: AdminRole) => {
  const baseRoutes = [
    { path: '/dashboard', component: Dashboard, roles: ['*'] },
  ];

  const roleRoutes = {
    super_admin: [
      { path: '/users', component: UserManagement },
      { path: '/kyc', component: KYCManagement },
      { path: '/trading', component: TradingOverview },
      { path: '/p2p', component: P2PManagement },
      { path: '/blockchain', component: BlockchainManagement },
      { path: '/white-label', component: WhiteLabelManagement },
      { path: '/settings', component: SystemSettings },
      { path: '/analytics', component: Analytics },
      { path: '/affiliates', component: AffiliateManagement },
      { path: '/support', component: CustomerSupport },
      { path: '/technical', component: TechnicalDashboard },
      { path: '/listing', component: ListingManagement },
    ],
    kyc_admin: [
      { path: '/users', component: UserManagement },
      { path: '/kyc', component: KYCManagement },
    ],
    customer_support: [
      { path: '/users', component: UserManagement },
      { path: '/support', component: CustomerSupport },
      { path: '/trading', component: TradingOverview },
    ],
    p2p_manager: [
      { path: '/p2p', component: P2PManagement },
      { path: '/users', component: UserManagement },
    ],
    affiliate_manager: [
      { path: '/affiliates', component: AffiliateManagement },
      { path: '/analytics', component: Analytics },
    ],
    bdm: [
      { path: '/analytics', component: Analytics },
      { path: '/white-label', component: WhiteLabelManagement },
    ],
    technical_team: [
      { path: '/technical', component: TechnicalDashboard },
      { path: '/blockchain', component: BlockchainManagement },
      { path: '/settings', component: SystemSettings },
    ],
    listing_manager: [
      { path: '/listing', component: ListingManagement },
      { path: '/analytics', component: Analytics },
    ],
  };

  return [...baseRoutes, ...(roleRoutes[role] || [])];
};

// Protected Route Component
const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  requiredRole?: AdminRole;
}> = ({ children, requiredRole }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole && user?.role !== 'super_admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Main Layout Component
const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user } = useAuth();

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar open={sidebarOpen} onToggle={handleSidebarToggle} userRole={user?.role} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          transition: 'margin-left 0.3s',
          marginLeft: sidebarOpen ? '280px' : '80px',
        }}
      >
        <Header onSidebarToggle={handleSidebarToggle} />
        <Box
          sx={{
            flexGrow: 1,
            p: 3,
            backgroundColor: 'background.default',
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

// App Router Component
const AppRouter: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  const availableRoutes = getRoutesByRole(user?.role as AdminRole);

  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        {availableRoutes.map(({ path, component: Component }) => (
          <Route
            key={path}
            path={path}
            element={
              <ProtectedRoute>
                <Component />
              </ProtectedRoute>
            }
          />
        ))}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </MainLayout>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <AuthProvider>
            <WebSocketProvider>
              <NotificationProvider>
                <Router>
                  <AppRouter />
                </Router>
              </NotificationProvider>
            </WebSocketProvider>
          </AuthProvider>
        </SnackbarProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;