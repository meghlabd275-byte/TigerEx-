import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
  ToggleButton,
  ToggleButtonGroup,
  Slider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  AccountBalance,
  Settings,
  Notifications,
  Security,
  Help,
  Refresh,
  FullscreenExit,
  Fullscreen,
  Star,
  StarBorder,
  ExpandMore,
  Timeline,
  CandlestickChart,
  BarChart,
  PieChart,
  Assessment,
  Speed,
  Add,
  Remove,
  ArrowUpward,
  ArrowDownward,
  SwapVert,
  Lock,
  LockOpen,
  Visibility,
  VisibilityOff,
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

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  marketCap: number;
  favorite: boolean;
  sparkline: number[];
}

interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'STOP_LIMIT' | 'TAKE_PROFIT' | 'OCO' | 'ICEBERG' | 'TRAILING_STOP';
  quantity: number;
  price?: number;
  stopPrice?: number;
  limitPrice?: number;
  status: 'NEW' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELED' | 'REJECTED' | 'EXPIRED';
  createdAt: string;
  updatedAt: string;
  filledQuantity: number;
  remainingQuantity: number;
  avgPrice: number;
  fee: number;
  feeAsset: string;
  timeInForce: 'GTC' | 'IOC' | 'FOK';
  leverage: number;
  marginMode: 'CROSS' | 'ISOLATED';
}

interface Balance {
  asset: string;
  available: number;
  locked: number;
  total: number;
  usdValue: number;
  change24h: number;
}

interface Position {
  symbol: string;
  side: 'LONG' | 'SHORT';
  size: number;
  entryPrice: number;
  markPrice: number;
  unrealizedPnl: number;
  realizedPnl: number;
  leverage: number;
  margin: number;
  marginRatio: number;
  liquidationPrice: number;
  notional: number;
}

const AdvancedTradingDashboard: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<string>('BTCUSDT');
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [balances, setBalances] = useState<Balance[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [chartType, setChartType] = useState<'line' | 'candlestick' | 'area'>('candlestick');
  const [timeframe, setTimeframe] = useState('1h');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'OCO'>('LIMIT');
  const [orderSide, setOrderSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderQuantity, setOrderQuantity] = useState<string>('');
  const [orderPrice, setOrderPrice] = useState<string>('');
  const [stopPrice, setStopPrice] = useState<string>('');
  const [limitPrice, setLimitPrice] = useState<string>('');
  const [leverage, setLeverage] = useState<number>(1);
  const [marginMode, setMarginMode] = useState<'CROSS' | 'ISOLATED'>('CROSS');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showOrderConfirm, setShowOrderConfirm] = useState(false);
  const [notification, setNotification] = useState<{ message: string; severity: 'success' | 'error' | 'warning' | 'info' } | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [favoriteSymbols, setFavoriteSymbols] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadTradingData();
  }, []);

  const loadTradingData = async () => {
    const mockPairs: TradingPair[] = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        price: 43250.50,
        change24h: 2.34,
        volume24h: 1250000000,
        high24h: 44500.00,
        low24h: 42100.00,
        marketCap: 845000000000,
        favorite: true,
        sparkline: [42000, 42500, 43000, 43250, 43100, 43300, 43250],
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        price: 2280.75,
        change24h: -1.23,
        volume24h: 850000000,
        high24h: 2350.00,
        low24h: 2250.00,
        marketCap: 274000000000,
        favorite: true,
        sparkline: [2300, 2285, 2270, 2280, 2290, 2285, 2280],
      },
    ];

    const mockBalances: Balance[] = [
      { asset: 'BTC', available: 0.125, locked: 0.0, total: 0.125, usdValue: 5406.31, change24h: 2.34 },
      { asset: 'ETH', available: 2.5, locked: 0.5, total: 3.0, usdValue: 6842.25, change24h: -1.23 },
      { asset: 'USDT', available: 10000, locked: 2500, total: 12500, usdValue: 12500, change24h: 0 },
    ];

    const mockOrders: Order[] = [
      {
        id: '1',
        symbol: 'BTCUSDT',
        side: 'BUY',
        type: 'LIMIT',
        quantity: 0.01,
        price: 42000,
        status: 'NEW',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        filledQuantity: 0,
        remainingQuantity: 0.01,
        avgPrice: 0,
        fee: 0,
        feeAsset: 'USDT',
        timeInForce: 'GTC',
        leverage: 1,
        marginMode: 'CROSS',
      },
    ];

    setTradingPairs(mockPairs);
    setBalances(mockBalances);
    setOrders(mockOrders);
  };

  const handlePlaceOrder = async () => {
    setNotification({
      message: 'Order placed successfully',
      severity: 'success',
    });
    setOrderQuantity('');
    setOrderPrice('');
    setStopPrice('');
    setLimitPrice('');
    setShowOrderConfirm(false);
  };

  const selectedPairData = useMemo(() => {
    return tradingPairs.find((pair) => pair.symbol === selectedPair);
  }, [tradingPairs, selectedPair]);

  const currentBalance = useMemo(() => {
    if (!selectedPairData) return null;
    const baseBalance = balances.find((b) => b.asset === selectedPairData.baseAsset);
    const quoteBalance = balances.find((b) => b.asset === selectedPairData.quoteAsset);
    return { base: baseBalance, quote: quoteBalance };
  }, [balances, selectedPairData]);

  const totalPortfolioValue = useMemo(() => {
    return balances.reduce((total, balance) => total + balance.usdValue, 0);
  }, [balances]);

  const chartData = useMemo(() => {
    const dataPoints = timeframe === '1m' ? 60 : timeframe === '5m' ? 288 : timeframe === '1h' ? 168 : 30;
    return Array.from({ length: dataPoints }, (_, i) => ({
      time: new Date(Date.now() - (dataPoints - i) * (timeframe === '1m' ? 60000 : timeframe === '5m' ? 300000 : timeframe === '1h' ? 3600000 : 86400000)),
      open: selectedPairData?.price * (0.98 + Math.random() * 0.04) || 0,
      high: selectedPairData?.price * (1.01 + Math.random() * 0.02) || 0,
      low: selectedPairData?.price * (0.97 + Math.random() * 0.02) || 0,
      close: selectedPairData?.price * (0.98 + Math.random() * 0.04) || 0,
      volume: Math.random() * 1000000,
    }));
  }, [selectedPairData, timeframe]);

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: isDarkMode ? '#0a0a0a' : '#fafafa' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 1, bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff' }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Trading Pair</InputLabel>
              <Select
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                label="Trading Pair"
              >
                {tradingPairs.map((pair) => (
                  <MenuItem key={pair.symbol} value={pair.symbol}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                        }}
                      >
                        {pair.favorite ? (
                          <Star color="primary" />
                        ) : (
                          <StarBorder />
                        )}
                      </IconButton>
                      <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                        {pair.baseAsset.substring(0, 2)}
                      </Avatar>
                      <Typography variant="body2" sx={{ ml: 1, flexGrow: 1 }}>
                        {pair.symbol}
                      </Typography>
                      <Box sx={{ textAlign: 'right' }}>
                        <Typography variant="body2" fontWeight="bold">
                          ${pair.price.toFixed(2)}
                        </Typography>
                        <Typography
                          variant="caption"
                          color={pair.change24h >= 0 ? 'success.main' : 'error.main'}
                        >
                          {pair.change24h >= 0 ? '+' : ''}
                          {pair.change24h.toFixed(2)}%
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            {selectedPairData && (
              <Grid container spacing={2}>
                <Grid item>
                  <Typography variant="h6" fontWeight="bold">
                    ${selectedPairData.price.toFixed(2)}
                  </Typography>
                  <Typography
                    variant="body2"
                    color={selectedPairData.change24h >= 0 ? 'success.main' : 'error.main'}
                  >
                    {selectedPairData.change24h >= 0 ? <TrendingUp /> : <TrendingDown />}
                    {selectedPairData.change24h >= 0 ? '+' : ''}
                    {selectedPairData.change24h.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    24h High
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${selectedPairData.high24h.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    24h Low
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${selectedPairData.low24h.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    24h Volume
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {(selectedPairData.volume24h / 1000000).toFixed(2)}M
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="body2" color="text.secondary">
                    Market Cap
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(selectedPairData.marketCap / 1000000000).toFixed(2)}B
                  </Typography>
                </Grid>
              </Grid>
            )}
          </Grid>

          <Grid item xs={12} md={3}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(_, value) => value && setChartType(value)}
                size="small"
              >
                <ToggleButton value="line">
                  <Timeline />
                </ToggleButton>
                <ToggleButton value="candlestick">
                  <CandlestickChart />
                </ToggleButton>
                <ToggleButton value="area">
                  <BarChart />
                </ToggleButton>
              </ToggleButtonGroup>

              <ToggleButtonGroup
                value={timeframe}
                exclusive
                onChange={(_, value) => value && setTimeframe(value)}
                size="small"
              >
                {['1m', '5m', '1h', '4h', '1d'].map((tf) => (
                  <ToggleButton key={tf} value={tf}>
                    {tf}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>

              <FormControlLabel
                control={
                  <Switch
                    checked={isDarkMode}
                    onChange={(e) => setIsDarkMode(e.target.checked)}
                  />
                }
                label="Dark"
              />
              <IconButton onClick={() => setIsFullscreen(!isFullscreen)}>
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
              <IconButton>
                <Badge badgeContent={5} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
              <IconButton>
                <Settings />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Main Trading Interface */}
      <Grid container spacing={1} sx={{ flex: 1, overflow: 'hidden' }}>
        {/* Left Panel - Order Book & Recent Trades */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff' }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Order Book" />
              <Tab label="Recent Trades" />
              <Tab label="Depth Chart" />
            </Tabs>
            <Box sx={{ flex: 1, overflow: 'hidden', p: 1 }}>
              <Typography variant="h6" gutterBottom>
                Order Book - {selectedPair}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Real-time order book visualization
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Center Panel - Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ height: '100%', p: 1, bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff' }}>
            <Typography variant="h6" gutterBottom>
              Price Chart - {selectedPair}
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              {chartType === 'candlestick' ? (
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Brush dataKey="time" height={30} stroke="#8884d8" />
                </ComposedChart>
              ) : chartType === 'line' ? (
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="close" stroke="#8884d8" strokeWidth={2} />
                  <Brush dataKey="time" height={30} stroke="#8884d8" />
                </LineChart>
              ) : (
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <RechartsTooltip />
                  <Area type="monotone" dataKey="close" stroke="#8884d8" fill="#8884d8" />
                  <Brush dataKey="time" height={30} stroke="#8884d8" />
                </AreaChart>
              )}
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Right Panel - Trading Form */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ height: '100%', p: 2, bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff' }}>
            <Typography variant="h6" gutterBottom>
              Place Order
            </Typography>

            {/* Balance Overview */}
            <Box sx={{ mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Total Portfolio Value
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                ${totalPortfolioValue.toFixed(2)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                24h Change: <span style={{ color: 'success.main' }}>+2.34%</span>
              </Typography>
            </Box>

            {/* Order Type Tabs */}
            <Tabs
              value={orderType}
              onChange={(e, v) => setOrderType(v)}
              variant="fullWidth"
              sx={{ mb: 2 }}
            >
              <Tab label="Limit" value="LIMIT" />
              <Tab label="Market" value="MARKET" />
              <Tab label="Stop" value="STOP_LOSS" />
              <Tab label="OCO" value="OCO" />
            </Tabs>

            {/* Buy/Sell Toggle */}
            <Grid container spacing={1} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant={orderSide === 'BUY' ? 'contained' : 'outlined'}
                  color="success"
                  onClick={() => setOrderSide('BUY')}
                >
                  Buy
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant={orderSide === 'SELL' ? 'contained' : 'outlined'}
                  color="error"
                  onClick={() => setOrderSide('SELL')}
                >
                  Sell
                </Button>
              </Grid>
            </Grid>

            {/* Order Form */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {orderType !== 'MARKET' && (
                <TextField
                  label="Price"
                  type="number"
                  value={orderPrice}
                  onChange={(e) => setOrderPrice(e.target.value)}
                  fullWidth
                  size="small"
                  InputProps={{
                    endAdornment: selectedPairData?.quoteAsset,
                  }}
                />
              )}

              {orderType === 'STOP_LOSS' && (
                <TextField
                  label="Stop Price"
                  type="number"
                  value={stopPrice}
                  onChange={(e) => setStopPrice(e.target.value)}
                  fullWidth
                  size="small"
                  InputProps={{
                    endAdornment: selectedPairData?.quoteAsset,
                  }}
                />
              )}

              {orderType === 'STOP_LIMIT' && (
                <TextField
                  label="Limit Price"
                  type="number"
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(e.target.value)}
                  fullWidth
                  size="small"
                  InputProps={{
                    endAdornment: selectedPairData?.quoteAsset,
                  }}
                />
              )}

              <TextField
                label="Quantity"
                type="number"
                value={orderQuantity}
                onChange={(e) => setOrderQuantity(e.target.value)}
                fullWidth
                size="small"
                InputProps={{
                  endAdornment: selectedPairData?.baseAsset,
                }}
              />

              {/* Leverage Controls */}
              <Box>
                <Typography variant="body2" gutterBottom>
                  Leverage: {leverage}x
                </Typography>
                <Slider
                  value={leverage}
                  onChange={(_, value) => setLeverage(value as number)}
                  min={1}
                  max={125}
                  marks
                  valueLabelDisplay="auto"
                />
                <ToggleButtonGroup
                  value={marginMode}
                  exclusive
                  onChange={(_, value) => value && setMarginMode(value)}
                  size="small"
                  sx={{ mt: 1 }}
                >
                  <ToggleButton value="CROSS">Cross</ToggleButton>
                  <ToggleButton value="ISOLATED">Isolated</ToggleButton>
                </ToggleButtonGroup>
              </Box>

              {/* Balance Display */}
              {currentBalance && (
                <Box sx={{ p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Available Balance:
                  </Typography>
                  <Typography variant="body2">
                    {orderSide === 'BUY'
                      ? `${currentBalance.quote?.available.toFixed(4) || '0'} ${selectedPairData?.quoteAsset}`
                      : `${currentBalance.base?.available.toFixed(4) || '0'} ${selectedPairData?.baseAsset}`}
                  </Typography>
                </Box>
              )}

              {/* Quick Amount Buttons */}
              <Grid container spacing={1}>
                {[25, 50, 75, 100].map((percentage) => (
                  <Grid item xs={3} key={percentage}>
                    <Button
                      size="small"
                      variant="outlined"
                      fullWidth
                      onClick={() => {
                        if (currentBalance) {
                          const balance =
                            orderSide === 'BUY'
                              ? currentBalance.quote?.available || 0
                              : currentBalance.base?.available || 0;
                          const percent = percentage / 100;
                          let quantity: number;

                          if (orderSide === 'BUY' && orderType !== 'MARKET') {
                            quantity = (balance * percent) / parseFloat(orderPrice || '1');
                          } else {
                            quantity = balance * percent;
                          }

                          setOrderQuantity(quantity.toFixed(6));
                        }
                      }}
                    >
                      {percentage}%
                    </Button>
                  </Grid>
                ))}
              </Grid>

              <Button
                variant="contained"
                color={orderSide === 'BUY' ? 'success' : 'error'}
                fullWidth
                size="large"
                onClick={() => setShowOrderConfirm(true)}
                disabled={!orderQuantity || (orderType !== 'MARKET' && !orderPrice)}
              >
                {orderSide === 'BUY' ? 'Buy' : 'Sell'} {selectedPairData?.baseAsset}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Bottom Panel - Orders and Positions */}
      <Paper sx={{ mt: 1, height: '300px', bgcolor: isDarkMode ? '#1a1a1a' : '#ffffff' }}>
        <Tabs value={0}>
          <Tab label="Open Orders" />
          <Tab label="Order History" />
          <Tab label="Trade History" />
          <Tab label="Positions" />
          <Tab label="Assets" />
        </Tabs>

        <TableContainer sx={{ height: '250px' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Filled</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.symbol}</TableCell>
                  <TableCell>{order.type}</TableCell>
                  <TableCell>
                    <Chip
                      label={order.side}
                      color={order.side === 'BUY' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{order.quantity}</TableCell>
                  <TableCell>{order.price || 'Market'}</TableCell>
                  <TableCell>
                    {((order.filledQuantity / order.quantity) * 100).toFixed(1)}%
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={order.status}
                      color={order.status === 'FILLED' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(order.createdAt).toLocaleTimeString()}
                  </TableCell>
                  <TableCell>
                    {order.status === 'NEW' && (
                      <Button size="small" color="error">
                        Cancel
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Order Confirmation Dialog */}
      <Dialog open={showOrderConfirm} onClose={() => setShowOrderConfirm(false)}>
        <DialogTitle>Confirm Order</DialogTitle>
        <DialogContent>
          <Typography>
            {orderSide} {orderQuantity} {selectedPairData?.baseAsset}
            {orderType !== 'MARKET' && ` at ${orderPrice} ${selectedPairData?.quoteAsset}`}
          </Typography>
          {orderType === 'STOP_LOSS' && (
            <Typography>
              Stop Price: {stopPrice} {selectedPairData?.quoteAsset}
            </Typography>
          )}
          {leverage > 1 && (
            <Typography>Leverage: {leverage}x ({marginMode} margin)</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowOrderConfirm(false)}>Cancel</Button>
          <Button onClick={handlePlaceOrder} variant="contained">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

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

export default AdvancedTradingDashboard;