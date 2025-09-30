import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Tabs,
  Tab,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  AccountBalanceWallet,
  ShowChart,
  PieChart,
  Timeline,
  Refresh,
  Download,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { Line, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement
);

interface Asset {
  id: string;
  symbol: string;
  name: string;
  balance: number;
  value: number;
  price: number;
  change24h: number;
  allocation: number;
  icon: string;
}

interface PortfolioStats {
  totalValue: number;
  totalChange24h: number;
  totalChangePercent: number;
  availableBalance: number;
  inOrders: number;
  totalPnL: number;
  totalPnLPercent: number;
}

const PortfolioPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [hideBalance, setHideBalance] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [timeRange, setTimeRange] = useState('24h');

  // Mock data - replace with actual API calls
  const [portfolioStats, setPortfolioStats] = useState<PortfolioStats>({
    totalValue: 125430.50,
    totalChange24h: 3245.20,
    totalChangePercent: 2.65,
    availableBalance: 98234.30,
    inOrders: 27196.20,
    totalPnL: 15430.50,
    totalPnLPercent: 14.05,
  });

  const [assets, setAssets] = useState<Asset[]>([
    {
      id: '1',
      symbol: 'BTC',
      name: 'Bitcoin',
      balance: 2.5,
      value: 105000,
      price: 42000,
      change24h: 2.5,
      allocation: 45,
      icon: '/icons/btc.png',
    },
    {
      id: '2',
      symbol: 'ETH',
      name: 'Ethereum',
      balance: 15.8,
      value: 35640,
      price: 2255,
      change24h: 3.2,
      allocation: 28,
      icon: '/icons/eth.png',
    },
    {
      id: '3',
      symbol: 'USDT',
      name: 'Tether',
      balance: 25000,
      value: 25000,
      price: 1.0,
      change24h: 0.01,
      allocation: 20,
      icon: '/icons/usdt.png',
    },
    {
      id: '4',
      symbol: 'BNB',
      name: 'Binance Coin',
      balance: 50,
      value: 15000,
      price: 300,
      change24h: 1.8,
      allocation: 7,
      icon: '/icons/bnb.png',
    },
  ]);

  const portfolioChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [95000, 98000, 102000, 108000, 115000, 118000, 120000, 122000, 125430],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const allocationChartData = {
    labels: assets.map(asset => asset.symbol),
    datasets: [
      {
        data: assets.map(asset => asset.allocation),
        backgroundColor: [
          'rgba(255, 159, 64, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(255, 206, 86, 0.8)',
        ],
        borderColor: [
          'rgba(255, 159, 64, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const formatCurrency = (value: number) => {
    if (hideBalance) return '****';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Portfolio Overview */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" fontWeight="bold">
            Portfolio Overview
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title={hideBalance ? 'Show Balance' : 'Hide Balance'}>
              <IconButton onClick={() => setHideBalance(!hideBalance)}>
                {hideBalance ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </Tooltip>
            <IconButton>
              <Refresh />
            </IconButton>
            <IconButton onClick={handleMenuOpen}>
              <MoreVert />
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
              <MenuItem onClick={handleMenuClose}>
                <Download sx={{ mr: 1 }} /> Export Report
              </MenuItem>
              <MenuItem onClick={handleMenuClose}>Settings</MenuItem>
            </Menu>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Total Portfolio Value */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccountBalanceWallet sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" color="text.secondary">
                    Total Portfolio Value
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {formatCurrency(portfolioStats.totalValue)}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  {portfolioStats.totalChangePercent >= 0 ? (
                    <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                  ) : (
                    <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                  )}
                  <Typography
                    variant="body2"
                    color={portfolioStats.totalChangePercent >= 0 ? 'success.main' : 'error.main'}
                  >
                    {formatPercent(portfolioStats.totalChangePercent)} (24h)
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Available Balance */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Available Balance
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {formatCurrency(portfolioStats.availableBalance)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {((portfolioStats.availableBalance / portfolioStats.totalValue) * 100).toFixed(1)}% of total
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* In Orders */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  In Orders
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {formatCurrency(portfolioStats.inOrders)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {((portfolioStats.inOrders / portfolioStats.totalValue) * 100).toFixed(1)}% of total
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Total P&L */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total P&L
                </Typography>
                <Typography
                  variant="h5"
                  fontWeight="bold"
                  color={portfolioStats.totalPnL >= 0 ? 'success.main' : 'error.main'}
                >
                  {formatCurrency(portfolioStats.totalPnL)}
                </Typography>
                <Typography
                  variant="caption"
                  color={portfolioStats.totalPnLPercent >= 0 ? 'success.main' : 'error.main'}
                >
                  {formatPercent(portfolioStats.totalPnLPercent)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="bold">
                Portfolio Performance
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {['24h', '7d', '1M', '3M', '1Y', 'All'].map((range) => (
                  <Button
                    key={range}
                    size="small"
                    variant={timeRange === range ? 'contained' : 'outlined'}
                    onClick={() => setTimeRange(range)}
                  >
                    {range}
                  </Button>
                ))}
              </Box>
            </Box>
            <Line data={portfolioChartData} options={{ responsive: true, maintainAspectRatio: true }} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Asset Allocation
            </Typography>
            <Doughnut data={allocationChartData} options={{ responsive: true, maintainAspectRatio: true }} />
          </Paper>
        </Grid>
      </Grid>

      {/* Assets Table */}
      <Paper sx={{ p: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="All Assets" />
          <Tab label="Spot" />
          <Tab label="Futures" />
          <Tab label="Earn" />
          <Tab label="Staking" />
        </Tabs>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Asset</TableCell>
                <TableCell align="right">Balance</TableCell>
                <TableCell align="right">Value</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right">24h Change</TableCell>
                <TableCell align="right">Allocation</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assets.map((asset) => (
                <TableRow key={asset.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar src={asset.icon} sx={{ width: 32, height: 32, mr: 2 }}>
                        {asset.symbol[0]}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {asset.symbol}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {asset.name}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {hideBalance ? '****' : asset.balance.toFixed(4)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(asset.value)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      {formatCurrency(asset.price)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={formatPercent(asset.change24h)}
                      size="small"
                      color={asset.change24h >= 0 ? 'success' : 'error'}
                      icon={asset.change24h >= 0 ? <TrendingUp /> : <TrendingDown />}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                      <Typography variant="body2" sx={{ mr: 1 }}>
                        {asset.allocation}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={asset.allocation}
                        sx={{ width: 60, height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Button size="small" variant="outlined" sx={{ mr: 1 }}>
                      Trade
                    </Button>
                    <Button size="small" variant="outlined">
                      Transfer
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default PortfolioPage;