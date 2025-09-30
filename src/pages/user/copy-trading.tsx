import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Switch,
  FormControlLabel,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Rating,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Star,
  ContentCopy,
  Share,
  Info,
  CheckCircle,
  Cancel,
  BarChart,
  Timeline,
  People,
  AttachMoney,
  Settings,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { Line, Doughnut } from 'react-chartjs-2';

interface Trader {
  id: string;
  name: string;
  avatar: string;
  verified: boolean;
  rating: number;
  followers: number;
  copiers: number;
  totalPnL: number;
  totalPnLPercent: number;
  roi30d: number;
  roi90d: number;
  roi1y: number;
  winRate: number;
  totalTrades: number;
  avgHoldTime: string;
  maxDrawdown: number;
  sharpeRatio: number;
  aum: number;
  minCopyAmount: number;
  copyFee: number;
  tradingPairs: string[];
  strategy: string;
  riskLevel: 'Low' | 'Medium' | 'High';
}

interface CopyPosition {
  id: string;
  trader: string;
  amount: number;
  currentValue: number;
  pnl: number;
  pnlPercent: number;
  startDate: string;
  status: 'active' | 'paused' | 'stopped';
  copyRatio: number;
}

const CopyTradingPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedTrader, setSelectedTrader] = useState<Trader | null>(null);
  const [copyDialogOpen, setCopyDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [copyAmount, setCopyAmount] = useState(1000);
  const [copyRatio, setCopyRatio] = useState(1);
  const [stopLoss, setStopLoss] = useState(20);
  const [takeProfit, setTakeProfit] = useState(50);
  const [autoCopy, setAutoCopy] = useState(true);

  // Mock data
  const [topTraders, setTopTraders] = useState<Trader[]>([
    {
      id: '1',
      name: 'CryptoMaster',
      avatar: '/avatars/trader1.jpg',
      verified: true,
      rating: 4.9,
      followers: 15420,
      copiers: 3250,
      totalPnL: 125000,
      totalPnLPercent: 245.5,
      roi30d: 15.2,
      roi90d: 42.8,
      roi1y: 156.3,
      winRate: 78.5,
      totalTrades: 1250,
      avgHoldTime: '2.5 days',
      maxDrawdown: 12.5,
      sharpeRatio: 2.8,
      aum: 2500000,
      minCopyAmount: 100,
      copyFee: 10,
      tradingPairs: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
      strategy: 'Swing Trading',
      riskLevel: 'Medium',
    },
    {
      id: '2',
      name: 'AlgoTrader Pro',
      avatar: '/avatars/trader2.jpg',
      verified: true,
      rating: 4.8,
      followers: 12350,
      copiers: 2890,
      totalPnL: 98500,
      totalPnLPercent: 198.7,
      roi30d: 12.8,
      roi90d: 38.5,
      roi1y: 142.1,
      winRate: 75.2,
      totalTrades: 2150,
      avgHoldTime: '1.2 days',
      maxDrawdown: 15.3,
      sharpeRatio: 2.5,
      aum: 1850000,
      minCopyAmount: 200,
      copyFee: 12,
      tradingPairs: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT'],
      strategy: 'Algorithmic Trading',
      riskLevel: 'High',
    },
    {
      id: '3',
      name: 'SafeTrader',
      avatar: '/avatars/trader3.jpg',
      verified: true,
      rating: 4.7,
      followers: 9850,
      copiers: 2150,
      totalPnL: 65000,
      totalPnLPercent: 132.5,
      roi30d: 8.5,
      roi90d: 25.3,
      roi1y: 98.2,
      winRate: 82.1,
      totalTrades: 850,
      avgHoldTime: '5.8 days',
      maxDrawdown: 8.2,
      sharpeRatio: 3.2,
      aum: 1250000,
      minCopyAmount: 50,
      copyFee: 8,
      tradingPairs: ['BTC/USDT', 'ETH/USDT'],
      strategy: 'Conservative Growth',
      riskLevel: 'Low',
    },
  ]);

  const [myCopyPositions, setMyCopyPositions] = useState<CopyPosition[]>([
    {
      id: '1',
      trader: 'CryptoMaster',
      amount: 5000,
      currentValue: 5750,
      pnl: 750,
      pnlPercent: 15,
      startDate: '2024-01-01',
      status: 'active',
      copyRatio: 1,
    },
    {
      id: '2',
      trader: 'AlgoTrader Pro',
      amount: 3000,
      currentValue: 3240,
      pnl: 240,
      pnlPercent: 8,
      startDate: '2024-01-10',
      status: 'active',
      copyRatio: 0.5,
    },
  ]);

  const performanceChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [10000, 10500, 11200, 10800, 11500, 12000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const allocationChartData = {
    labels: myCopyPositions.map((pos) => pos.trader),
    datasets: [
      {
        data: myCopyPositions.map((pos) => pos.amount),
        backgroundColor: ['rgba(255, 159, 64, 0.8)', 'rgba(54, 162, 235, 0.8)', 'rgba(75, 192, 192, 0.8)'],
      },
    ],
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCopyTrader = (trader: Trader) => {
    setSelectedTrader(trader);
    setCopyDialogOpen(true);
  };

  const handleViewDetails = (trader: Trader) => {
    setSelectedTrader(trader);
    setDetailsDialogOpen(true);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low':
        return 'success';
      case 'Medium':
        return 'warning';
      case 'High':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'paused':
        return 'warning';
      case 'stopped':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Copy Trading
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Follow and copy successful traders automatically. Earn while you learn.
        </Typography>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AttachMoney sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Total Copy Value
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                $12,000
              </Typography>
              <Chip label="+15.2%" size="small" color="success" icon={<TrendingUp />} sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <People sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Active Copies
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                3
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Total P&L
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="success.main">
                +$1,820
              </Typography>
              <Typography variant="caption" color="success.main">
                +15.2%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BarChart sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Avg. ROI (30d)
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                12.5%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Discover Traders" />
          <Tab label="My Copies" />
          <Tab label="Performance" />
          <Tab label="Leaderboard" />
        </Tabs>

        {/* Discover Traders Tab */}
        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            {/* Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Sort By</InputLabel>
                  <Select label="Sort By" defaultValue="roi">
                    <MenuItem value="roi">Highest ROI</MenuItem>
                    <MenuItem value="followers">Most Followers</MenuItem>
                    <MenuItem value="winrate">Win Rate</MenuItem>
                    <MenuItem value="sharpe">Sharpe Ratio</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Risk Level</InputLabel>
                  <Select label="Risk Level" defaultValue="all">
                    <MenuItem value="all">All Levels</MenuItem>
                    <MenuItem value="low">Low Risk</MenuItem>
                    <MenuItem value="medium">Medium Risk</MenuItem>
                    <MenuItem value="high">High Risk</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Strategy</InputLabel>
                  <Select label="Strategy" defaultValue="all">
                    <MenuItem value="all">All Strategies</MenuItem>
                    <MenuItem value="swing">Swing Trading</MenuItem>
                    <MenuItem value="day">Day Trading</MenuItem>
                    <MenuItem value="scalping">Scalping</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField fullWidth size="small" label="Min ROI %" type="number" />
              </Grid>
            </Grid>

            {/* Traders Grid */}
            <Grid container spacing={3}>
              {topTraders.map((trader) => (
                <Grid item xs={12} md={6} lg={4} key={trader.id}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      {/* Trader Header */}
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Avatar src={trader.avatar} sx={{ width: 60, height: 60, mr: 2 }}>
                          {trader.name[0]}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Typography variant="h6">{trader.name}</Typography>
                            {trader.verified && <CheckCircle sx={{ fontSize: 18, color: 'primary.main' }} />}
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Rating value={trader.rating} precision={0.1} size="small" readOnly />
                            <Typography variant="caption" color="text.secondary">
                              ({trader.rating})
                            </Typography>
                          </Box>
                        </Box>
                        <Chip label={trader.riskLevel} size="small" color={getRiskColor(trader.riskLevel) as any} />
                      </Box>

                      {/* Stats */}
                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            30d ROI
                          </Typography>
                          <Typography variant="h6" color="success.main">
                            +{trader.roi30d}%
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Win Rate
                          </Typography>
                          <Typography variant="h6">{trader.winRate}%</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Followers
                          </Typography>
                          <Typography variant="body2">{trader.followers.toLocaleString()}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Copiers
                          </Typography>
                          <Typography variant="body2">{trader.copiers.toLocaleString()}</Typography>
                        </Grid>
                      </Grid>

                      {/* Trading Info */}
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          Strategy: {trader.strategy}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                          Min. Copy: ${trader.minCopyAmount} • Fee: {trader.copyFee}%
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                          {trader.tradingPairs.slice(0, 3).map((pair, index) => (
                            <Chip key={index} label={pair} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Box>

                      {/* Actions */}
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button fullWidth variant="contained" onClick={() => handleCopyTrader(trader)}>
                          Copy Trader
                        </Button>
                        <Button variant="outlined" onClick={() => handleViewDetails(trader)}>
                          Details
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* My Copies Tab */}
        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Trader</TableCell>
                    <TableCell align="right">Copy Amount</TableCell>
                    <TableCell align="right">Current Value</TableCell>
                    <TableCell align="right">P&L</TableCell>
                    <TableCell align="right">Copy Ratio</TableCell>
                    <TableCell>Start Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {myCopyPositions.map((position) => (
                    <TableRow key={position.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ width: 40, height: 40, mr: 2 }}>{position.trader[0]}</Avatar>
                          <Typography variant="body2" fontWeight="bold">
                            {position.trader}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">${position.amount.toLocaleString()}</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${position.currentValue.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box>
                          <Typography
                            variant="body2"
                            fontWeight="bold"
                            color={position.pnl >= 0 ? 'success.main' : 'error.main'}
                          >
                            {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()}
                          </Typography>
                          <Typography
                            variant="caption"
                            color={position.pnlPercent >= 0 ? 'success.main' : 'error.main'}
                          >
                            {position.pnlPercent >= 0 ? '+' : ''}
                            {position.pnlPercent}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{position.copyRatio}x</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{position.startDate}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={position.status} size="small" color={getStatusColor(position.status) as any} />
                      </TableCell>
                      <TableCell align="right">
                        <Button size="small" variant="outlined" sx={{ mr: 1 }}>
                          Settings
                        </Button>
                        <Button size="small" variant="outlined" color="error">
                          Stop
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Performance Tab */}
        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Portfolio Performance
                  </Typography>
                  <Line data={performanceChartData} options={{ responsive: true, maintainAspectRatio: true }} />
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Allocation
                  </Typography>
                  <Doughnut data={allocationChartData} options={{ responsive: true, maintainAspectRatio: true }} />
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Leaderboard Tab */}
        {tabValue === 3 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Trader</TableCell>
                    <TableCell align="right">30d ROI</TableCell>
                    <TableCell align="right">90d ROI</TableCell>
                    <TableCell align="right">1Y ROI</TableCell>
                    <TableCell align="right">Win Rate</TableCell>
                    <TableCell align="right">Copiers</TableCell>
                    <TableCell align="right">AUM</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topTraders.map((trader, index) => (
                    <TableRow key={trader.id} hover>
                      <TableCell>
                        <Chip label={`#${index + 1}`} size="small" color={index === 0 ? 'primary' : 'default'} />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar src={trader.avatar} sx={{ width: 40, height: 40, mr: 2 }}>
                            {trader.name[0]}
                          </Avatar>
                          <Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Typography variant="body2" fontWeight="bold">
                                {trader.name}
                              </Typography>
                              {trader.verified && <CheckCircle sx={{ fontSize: 16, color: 'primary.main' }} />}
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {trader.strategy}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main" fontWeight="bold">
                          +{trader.roi30d}%
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +{trader.roi90d}%
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +{trader.roi1y}%
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{trader.winRate}%</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{trader.copiers.toLocaleString()}</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">${(trader.aum / 1000000).toFixed(2)}M</Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>

      {/* Copy Trader Dialog */}
      <Dialog open={copyDialogOpen} onClose={() => setCopyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Copy {selectedTrader?.name}</DialogTitle>
        <DialogContent>
          {selectedTrader && (
            <Box sx={{ mt: 2 }}>
              {/* Trader Summary */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      30d ROI
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      +{selectedTrader.roi30d}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Win Rate
                    </Typography>
                    <Typography variant="h6">{selectedTrader.winRate}%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Copy Fee
                    </Typography>
                    <Typography variant="body2">{selectedTrader.copyFee}%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Min. Amount
                    </Typography>
                    <Typography variant="body2">${selectedTrader.minCopyAmount}</Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Copy Settings */}
              <Typography variant="subtitle2" gutterBottom>
                Copy Amount
              </Typography>
              <TextField
                fullWidth
                type="number"
                value={copyAmount}
                onChange={(e) => setCopyAmount(Number(e.target.value))}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                }}
              />

              <Typography variant="subtitle2" gutterBottom>
                Copy Ratio: {copyRatio}x
              </Typography>
              <Slider
                value={copyRatio}
                onChange={(e, value) => setCopyRatio(value as number)}
                min={0.1}
                max={2}
                step={0.1}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 3 }}
              />

              <Typography variant="subtitle2" gutterBottom>
                Stop Loss: {stopLoss}%
              </Typography>
              <Slider
                value={stopLoss}
                onChange={(e, value) => setStopLoss(value as number)}
                min={5}
                max={50}
                step={5}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 3 }}
              />

              <Typography variant="subtitle2" gutterBottom>
                Take Profit: {takeProfit}%
              </Typography>
              <Slider
                value={takeProfit}
                onChange={(e, value) => setTakeProfit(value as number)}
                min={10}
                max={100}
                step={10}
                marks
                valueLabelDisplay="auto"
                sx={{ mb: 3 }}
              />

              <FormControlLabel
                control={<Switch checked={autoCopy} onChange={(e) => setAutoCopy(e.target.checked)} />}
                label="Auto-copy new trades"
              />

              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  • You will copy all trades from {selectedTrader.name}
                  <br />
                  • Copy ratio determines the proportion of your capital used
                  <br />
                  • Stop loss and take profit will be applied automatically
                  <br />• You can stop copying at any time
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCopyDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Start Copying</Button>
        </DialogActions>
      </Dialog>

      {/* Trader Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar src={selectedTrader?.avatar} sx={{ width: 50, height: 50, mr: 2 }}>
                {selectedTrader?.name[0]}
              </Avatar>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="h6">{selectedTrader?.name}</Typography>
                  {selectedTrader?.verified && <CheckCircle sx={{ fontSize: 20, color: 'primary.main' }} />}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {selectedTrader?.strategy}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton>
                <Share />
              </IconButton>
              <IconButton>
                <Star />
              </IconButton>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedTrader && (
            <Box>
              {/* Performance Metrics */}
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      30d ROI
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      +{selectedTrader.roi30d}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      90d ROI
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      +{selectedTrader.roi90d}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      1Y ROI
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      +{selectedTrader.roi1y}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      Win Rate
                    </Typography>
                    <Typography variant="h6">{selectedTrader.winRate}%</Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Risk Metrics */}
              <Typography variant="h6" gutterBottom>
                Risk Metrics
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Max Drawdown
                  </Typography>
                  <Typography variant="body1">{selectedTrader.maxDrawdown}%</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Sharpe Ratio
                  </Typography>
                  <Typography variant="body1">{selectedTrader.sharpeRatio}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Hold Time
                  </Typography>
                  <Typography variant="body1">{selectedTrader.avgHoldTime}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Trades
                  </Typography>
                  <Typography variant="body1">{selectedTrader.totalTrades.toLocaleString()}</Typography>
                </Grid>
              </Grid>

              {/* Trading Pairs */}
              <Typography variant="h6" gutterBottom>
                Trading Pairs
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                {selectedTrader.tradingPairs.map((pair, index) => (
                  <Chip key={index} label={pair} variant="outlined" />
                ))}
              </Box>

              {/* Copy Info */}
              <Alert severity="info">
                <Typography variant="body2">
                  • Minimum copy amount: ${selectedTrader.minCopyAmount}
                  <br />
                  • Copy fee: {selectedTrader.copyFee}% of profits
                  <br />
                  • Current copiers: {selectedTrader.copiers.toLocaleString()}
                  <br />• Assets under management: ${(selectedTrader.aum / 1000000).toFixed(2)}M
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              setDetailsDialogOpen(false);
              setCopyDialogOpen(true);
            }}
          >
            Copy Trader
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CopyTradingPage;