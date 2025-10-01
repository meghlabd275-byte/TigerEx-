import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  AppBar,
  Toolbar,
  Drawer,
  CssBaseline,
  ThemeProvider,
  createTheme,
  useTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  ExitToApp as ExitToAppIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  AccountCircle,
  Notifications,
  Language,
  Security,
  Analytics,
  Storage,
  Cloud,
  Speed,
} from '@mui/icons-material';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
  { text: 'Users', icon: <PeopleIcon />, path: '/admin/users' },
  { text: 'Trading', icon: <TrendingUpIcon />, path: '/admin/trading' },
  { text: 'Finance', icon: <AccountBalanceIcon />, path: '/admin/finance' },
  { text: 'Security', icon: <Security />, path: '/admin/security' },
  { text: 'Analytics', icon: <Analytics />, path: '/admin/analytics' },
  { text: 'System', icon: <Storage />, path: '/admin/system' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/admin/settings' },
];

const AdminDashboard: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [userProfile, setUserProfile] = useState({
    name: 'Admin User',
    email: 'admin@tigerex.com',
    role: 'Super Admin',
    avatar: '',
  });

  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
    },
  });

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // Implement logout logic
    console.log('Logging out...');
    handleMenuClose();
  };

  const drawer = (
    <Box sx={{ overflow: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
          <Speed />
        </Avatar>
        <Typography variant="h6" noWrap>
          TigerEx Admin
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text}>
            <ListItemIcon sx={{ color: 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  // Mock data for charts
  const tradingVolumeData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Trading Volume (USD)',
        data: [1200000, 1900000, 3000000, 5000000, 2000000, 3000000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  };

  const userGrowthData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'New Users',
        data: [120, 190, 300, 500, 200, 300],
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };

  const assetDistributionData = {
    labels: ['BTC', 'ETH', 'USDT', 'BNB', 'Others'],
    datasets: [
      {
        data: [30, 25, 20, 15, 10],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ],
      },
    ],
  };

  const statsCards = [
    { title: 'Total Users', value: '45,234', change: '+12%', icon: <PeopleIcon /> },
    { title: '24h Volume', value: '$2.3M', change: '+8%', icon: <TrendingUpIcon /> },
    { title: 'Total Assets', value: '$156M', change: '+15%', icon: <AccountBalanceIcon /> },
    { title: 'Active Traders', value: '12,456', change: '+5%', icon: <Speed /> },
  ];

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` },
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Admin Dashboard
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton color="inherit">
                <Notifications />
              </IconButton>
              <IconButton color="inherit">
                <Language />
              </IconButton>
              <IconButton
                size="large"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleMenuOpen}
                color="inherit"
              >
                <AccountCircle />
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
                <MenuItem onClick={handleMenuClose}>Account</MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </Box>
          </Toolbar>
        </AppBar>
        <Box
          component="nav"
          sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          aria-label="mailbox folders"
        >
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${drawerWidth}px)` },
          }}
        >
          <Toolbar />
          <Container maxWidth="xl">
            <Grid container spacing={3}>
              {/* Stats Cards */}
              {statsCards.map((stat, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flex: '1 0 auto' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                          {stat.icon}
                        </Avatar>
                        <Typography gutterBottom variant="h5" component="div">
                          {stat.value}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {stat.title}
                      </Typography>
                      <Typography variant="body2" color="success.main">
                        {stat.change}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}

              {/* Trading Volume Chart */}
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Trading Volume
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <Line data={tradingVolumeData} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Asset Distribution */}
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Asset Distribution
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <Doughnut data={assetDistributionData} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* User Growth */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      User Growth
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <Bar data={userGrowthData} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Recent Activity */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Recent Activity
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUpIcon color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="New user registration"
                          secondary="John Doe - 2 minutes ago"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <AccountBalanceIcon color="info" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Large trade executed"
                          secondary="BTC/USDT - $50,000 - 5 minutes ago"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Security color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Security alert"
                          secondary="Unusual login attempt - 10 minutes ago"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              {/* System Status */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      System Status
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Chip
                          label="API Gateway: Online"
                          color="success"
                          variant="outlined"
                          sx={{ width: '100%', mb: 1 }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Chip
                          label="Trading Engine: Online"
                          color="success"
                          variant="outlined"
                          sx={{ width: '100%', mb: 1 }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Chip
                          label="Database: Online"
                          color="success"
                          variant="outlined"
                          sx={{ width: '100%', mb: 1 }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Chip
                          label="Blockchain: Online"
                          color="success"
                          variant="outlined"
                          sx={{ width: '100%', mb: 1 }}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default AdminDashboard;