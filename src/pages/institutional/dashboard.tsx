import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Avatar,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  MoreVert as MoreVertIcon,
  AccountBalance as AccountBalanceIcon,
  ShowChart as ShowChartIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const InstitutionalDashboard = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedAccount, setSelectedAccount] = useState('main');

  const accountStats = {
    totalAUM: 125000000,
    dailyVolume: 15000000,
    activeUsers: 45,
    openPositions: 128,
    dailyPnL: 250000,
    dailyPnLPercent: 2.5,
  };

  const chartData = [
    { date: 'Jan', value: 100000000 },
    { date: 'Feb', value: 105000000 },
    { date: 'Mar', value: 110000000 },
    { date: 'Apr', value: 115000000 },
    { date: 'May', value: 120000000 },
    { date: 'Jun', value: 125000000 },
  ];

  const recentTrades = [
    {
      id: 1,
      pair: 'BTC/USDT',
      type: 'Buy',
      amount: 10.5,
      price: 35000,
      total: 367500,
      time: '2 mins ago',
      status: 'Completed',
      trader: 'John Doe',
    },
    {
      id: 2,
      pair: 'ETH/USDT',
      type: 'Sell',
      amount: 50.2,
      price: 2000,
      total: 100400,
      time: '5 mins ago',
      status: 'Completed',
      trader: 'Jane Smith',
    },
    {
      id: 3,
      pair: 'BNB/USDT',
      type: 'Buy',
      amount: 200,
      price: 300,
      total: 60000,
      time: '10 mins ago',
      status: 'Pending',
      trader: 'Mike Johnson',
    },
  ];

  const topTraders = [
    { name: 'John Doe', pnl: 125000, trades: 45, winRate: 78, avatar: 'JD' },
    { name: 'Jane Smith', pnl: 98000, trades: 38, winRate: 72, avatar: 'JS' },
    { name: 'Mike Johnson', pnl: 87000, trades: 52, winRate: 68, avatar: 'MJ' },
    { name: 'Sarah Williams', pnl: 76000, trades: 41, winRate: 75, avatar: 'SW' },
  ];

  const riskMetrics = [
    { label: 'Value at Risk (VaR)', value: '$2.5M', status: 'normal', percentage: 2.0 },
    { label: 'Leverage Ratio', value: '3.2x', status: 'warning', percentage: 64 },
    { label: 'Margin Usage', value: '45%', status: 'normal', percentage: 45 },
    { label: 'Liquidation Risk', value: 'Low', status: 'good', percentage: 15 },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            Institutional Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Corporate Account Overview
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<ShowChartIcon />}>
            OTC Trading
          </Button>
          <Button variant="contained" startIcon={<AccountBalanceIcon />}>
            Bulk Orders
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccountBalanceIcon sx={{ fontSize: 40, color: '#2196F3', mr: 2 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total AUM
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    ${(accountStats.totalAUM / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 16, color: '#4CAF50', mr: 0.5 }} />
                <Typography variant="body2" color="#4CAF50">
                  +12.5% this month
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ShowChartIcon sx={{ fontSize: 40, color: '#FF6B00', mr: 2 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Daily Volume
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    ${(accountStats.dailyVolume / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 16, color: '#4CAF50', mr: 0.5 }} />
                <Typography variant="body2" color="#4CAF50">
                  +8.3% vs yesterday
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PeopleIcon sx={{ fontSize: 40, color: '#9C27B0', mr: 2 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active Users
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {accountStats.activeUsers}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  {accountStats.openPositions} open positions
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon sx={{ fontSize: 40, color: '#4CAF50', mr: 2 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Daily P&L
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="#4CAF50">
                    +${(accountStats.dailyPnL / 1000).toFixed(0)}K
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 16, color: '#4CAF50', mr: 0.5 }} />
                <Typography variant="body2" color="#4CAF50">
                  +{accountStats.dailyPnLPercent}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Assets Under Management
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2196F3" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#2196F3" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#2196F3"
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Risk Metrics
              </Typography>
              {riskMetrics.map((metric, index) => (
                <Box key={index} sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{metric.label}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {metric.value}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={metric.percentage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#E0E0E0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor:
                          metric.status === 'good'
                            ? '#4CAF50'
                            : metric.status === 'warning'
                            ? '#FF9800'
                            : '#2196F3',
                      },
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Trades */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              Recent Trades
            </Typography>
            <Button size="small">View All</Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pair</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Price</TableCell>
                  <TableCell>Total</TableCell>
                  <TableCell>Trader</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentTrades.map((trade) => (
                  <TableRow key={trade.id}>
                    <TableCell>
                      <Typography fontWeight="bold">{trade.pair}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={trade.type}
                        size="small"
                        color={trade.type === 'Buy' ? 'success' : 'error'}
                      />
                    </TableCell>
                    <TableCell>{trade.amount}</TableCell>
                    <TableCell>${trade.price.toLocaleString()}</TableCell>
                    <TableCell>${trade.total.toLocaleString()}</TableCell>
                    <TableCell>{trade.trader}</TableCell>
                    <TableCell>{trade.time}</TableCell>
                    <TableCell>
                      <Chip
                        label={trade.status}
                        size="small"
                        color={trade.status === 'Completed' ? 'success' : 'warning'}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Top Traders */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Top Traders
          </Typography>
          <Grid container spacing={2}>
            {topTraders.map((trader, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: '#FF6B00', mr: 2 }}>
                        {trader.avatar}
                      </Avatar>
                      <Box>
                        <Typography variant="body1" fontWeight="bold">
                          {trader.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {trader.trades} trades
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        P&L
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="#4CAF50">
                        +${(trader.pnl / 1000).toFixed(0)}K
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        Win Rate
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {trader.winRate}%
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default InstitutionalDashboard;