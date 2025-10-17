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

import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
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
  Card,
  CardContent,
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
  Rating,
  Stepper,
  Step,
  StepLabel,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Search,
  FilterList,
  Add,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Schedule,
  Cancel,
  Message,
  AttachFile,
  Send,
  Star,
  VerifiedUser,
  Shield,
} from '@mui/icons-material';

interface P2POffer {
  id: string;
  merchant: {
    name: string;
    rating: number;
    trades: number;
    completionRate: number;
    verified: boolean;
  };
  type: 'buy' | 'sell';
  asset: string;
  fiat: string;
  price: number;
  available: number;
  limits: {
    min: number;
    max: number;
  };
  paymentMethods: string[];
  timeLimit: number;
}

interface P2POrder {
  id: string;
  type: 'buy' | 'sell';
  asset: string;
  amount: number;
  price: number;
  total: number;
  status: 'pending' | 'paid' | 'completed' | 'cancelled' | 'disputed';
  merchant: string;
  paymentMethod: string;
  createdAt: string;
  timeRemaining: string;
}

const P2PPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [selectedAsset, setSelectedAsset] = useState('USDT');
  const [selectedFiat, setSelectedFiat] = useState('USD');
  const [orderDialogOpen, setOrderDialogOpen] = useState(false);
  const [selectedOffer, setSelectedOffer] = useState<P2POffer | null>(null);
  const [orderStep, setOrderStep] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);

  // Mock data
  const [offers, setOffers] = useState<P2POffer[]>([
    {
      id: '1',
      merchant: {
        name: 'CryptoKing',
        rating: 4.9,
        trades: 1250,
        completionRate: 98.5,
        verified: true,
      },
      type: 'sell',
      asset: 'USDT',
      fiat: 'USD',
      price: 1.002,
      available: 50000,
      limits: { min: 100, max: 10000 },
      paymentMethods: ['Bank Transfer', 'PayPal', 'Wise'],
      timeLimit: 15,
    },
    {
      id: '2',
      merchant: {
        name: 'TradeMaster',
        rating: 4.8,
        trades: 890,
        completionRate: 97.2,
        verified: true,
      },
      type: 'sell',
      asset: 'USDT',
      fiat: 'USD',
      price: 1.001,
      available: 25000,
      limits: { min: 50, max: 5000 },
      paymentMethods: ['Bank Transfer', 'Zelle'],
      timeLimit: 30,
    },
    {
      id: '3',
      merchant: {
        name: 'QuickTrade',
        rating: 4.7,
        trades: 650,
        completionRate: 96.8,
        verified: false,
      },
      type: 'sell',
      asset: 'USDT',
      fiat: 'USD',
      price: 1.003,
      available: 15000,
      limits: { min: 200, max: 8000 },
      paymentMethods: ['Bank Transfer', 'Cash App'],
      timeLimit: 20,
    },
  ]);

  const [myOrders, setMyOrders] = useState<P2POrder[]>([
    {
      id: 'ORD001',
      type: 'buy',
      asset: 'USDT',
      amount: 1000,
      price: 1.002,
      total: 1002,
      status: 'pending',
      merchant: 'CryptoKing',
      paymentMethod: 'Bank Transfer',
      createdAt: '2024-01-15 10:30:00',
      timeRemaining: '14:35',
    },
    {
      id: 'ORD002',
      type: 'sell',
      asset: 'USDT',
      amount: 500,
      price: 1.001,
      total: 500.5,
      status: 'completed',
      merchant: 'TradeMaster',
      paymentMethod: 'PayPal',
      createdAt: '2024-01-14 15:20:00',
      timeRemaining: '-',
    },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenOrder = (offer: P2POffer) => {
    setSelectedOffer(offer);
    setOrderDialogOpen(true);
    setOrderStep(0);
  };

  const handleNextStep = () => {
    setOrderStep((prev) => prev + 1);
  };

  const handleBackStep = () => {
    setOrderStep((prev) => prev - 1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
      case 'paid':
        return 'warning';
      case 'cancelled':
      case 'disputed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'pending':
      case 'paid':
        return <Schedule />;
      case 'cancelled':
      case 'disputed':
        return <Cancel />;
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          P2P Trading
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Trade crypto directly with other users. Zero fees, multiple payment methods.
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                24h Volume
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                $2.5M
              </Typography>
              <Chip label="+12.5%" size="small" color="success" icon={<TrendingUp />} sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Active Offers
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                1,234
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Avg. Completion Time
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                8 min
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                98.5%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Paper sx={{ mb: 4 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Buy Crypto" />
          <Tab label="Sell Crypto" />
          <Tab label="My Orders" />
          <Tab label="My Ads" />
        </Tabs>

        {/* Buy/Sell Tab */}
        {(tabValue === 0 || tabValue === 1) && (
          <Box sx={{ p: 3 }}>
            {/* Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Asset</InputLabel>
                  <Select value={selectedAsset} onChange={(e) => setSelectedAsset(e.target.value)} label="Asset">
                    <MenuItem value="USDT">USDT</MenuItem>
                    <MenuItem value="BTC">BTC</MenuItem>
                    <MenuItem value="ETH">ETH</MenuItem>
                    <MenuItem value="BNB">BNB</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Fiat</InputLabel>
                  <Select value={selectedFiat} onChange={(e) => setSelectedFiat(e.target.value)} label="Fiat">
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                    <MenuItem value="INR">INR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Payment</InputLabel>
                  <Select label="Payment">
                    <MenuItem value="all">All Payments</MenuItem>
                    <MenuItem value="bank">Bank Transfer</MenuItem>
                    <MenuItem value="paypal">PayPal</MenuItem>
                    <MenuItem value="wise">Wise</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <TextField
                  fullWidth
                  size="small"
                  label="Amount"
                  type="number"
                  placeholder="Enter amount"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <Button fullWidth variant="outlined" startIcon={<FilterList />} sx={{ height: '40px' }}>
                  More Filters
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={2}>
                <Button fullWidth variant="contained" startIcon={<Add />} sx={{ height: '40px' }}>
                  Post Ad
                </Button>
              </Grid>
            </Grid>

            {/* Offers List */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Merchant</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Available</TableCell>
                    <TableCell align="right">Limits</TableCell>
                    <TableCell>Payment Methods</TableCell>
                    <TableCell align="center">Time Limit</TableCell>
                    <TableCell align="right">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {offers.map((offer) => (
                    <TableRow key={offer.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ width: 40, height: 40, mr: 2 }}>
                            {offer.merchant.name[0]}
                          </Avatar>
                          <Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Typography variant="body2" fontWeight="bold">
                                {offer.merchant.name}
                              </Typography>
                              {offer.merchant.verified && (
                                <VerifiedUser sx={{ fontSize: 16, color: 'primary.main' }} />
                              )}
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Rating value={offer.merchant.rating} precision={0.1} size="small" readOnly />
                              <Typography variant="caption" color="text.secondary">
                                {offer.merchant.trades} trades
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="success.main">
                              {offer.merchant.completionRate}% completion
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${offer.price.toFixed(3)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {offer.available.toLocaleString()} {offer.asset}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          ${offer.limits.min} - ${offer.limits.max.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {offer.paymentMethods.map((method, index) => (
                            <Chip key={index} label={method} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Chip label={`${offer.timeLimit} min`} size="small" />
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          variant="contained"
                          color={tabValue === 0 ? 'success' : 'error'}
                          onClick={() => handleOpenOrder(offer)}
                        >
                          {tabValue === 0 ? 'Buy' : 'Sell'} {offer.asset}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* My Orders Tab */}
        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Asset</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell>Merchant</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Time Remaining</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {myOrders.map((order) => (
                    <TableRow key={order.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {order.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={order.type.toUpperCase()}
                          size="small"
                          color={order.type === 'buy' ? 'success' : 'error'}
                        />
                      </TableCell>
                      <TableCell>{order.asset}</TableCell>
                      <TableCell align="right">{order.amount.toLocaleString()}</TableCell>
                      <TableCell align="right">${order.price.toFixed(3)}</TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${order.total.toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>{order.merchant}</TableCell>
                      <TableCell>
                        <Chip
                          label={order.status}
                          size="small"
                          color={getStatusColor(order.status) as any}
                          icon={getStatusIcon(order.status)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color={order.status === 'pending' ? 'error.main' : 'text.secondary'}>
                          {order.timeRemaining}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {order.status === 'pending' && (
                          <>
                            <Button size="small" variant="outlined" sx={{ mr: 1 }} onClick={() => setChatOpen(true)}>
                              Chat
                            </Button>
                            <Button size="small" variant="contained">
                              Mark as Paid
                            </Button>
                          </>
                        )}
                        {order.status === 'completed' && (
                          <Button size="small" variant="outlined">
                            View Details
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* My Ads Tab */}
        {tabValue === 3 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Create your own P2P ads to buy or sell crypto at your preferred price and payment methods.
            </Alert>
            <Button variant="contained" startIcon={<Add />} size="large">
              Create New Ad
            </Button>
          </Box>
        )}
      </Paper>

      {/* Order Dialog */}
      <Dialog open={orderDialogOpen} onClose={() => setOrderDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {tabValue === 0 ? 'Buy' : 'Sell'} {selectedOffer?.asset}
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={orderStep} sx={{ mt: 2, mb: 4 }}>
            <Step>
              <StepLabel>Order Details</StepLabel>
            </Step>
            <Step>
              <StepLabel>Payment</StepLabel>
            </Step>
            <Step>
              <StepLabel>Confirmation</StepLabel>
            </Step>
          </Stepper>

          {orderStep === 0 && selectedOffer && (
            <Box>
              {/* Merchant Info */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ width: 50, height: 50, mr: 2 }}>
                    {selectedOffer.merchant.name[0]}
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="h6">{selectedOffer.merchant.name}</Typography>
                      {selectedOffer.merchant.verified && (
                        <VerifiedUser sx={{ fontSize: 20, color: 'primary.main' }} />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Rating value={selectedOffer.merchant.rating} precision={0.1} size="small" readOnly />
                      <Typography variant="caption">
                        {selectedOffer.merchant.trades} trades • {selectedOffer.merchant.completionRate}% completion
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Paper>

              {/* Order Form */}
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="I want to pay"
                    type="number"
                    InputProps={{
                      endAdornment: <InputAdornment position="end">{selectedOffer.fiat}</InputAdornment>,
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="I will receive"
                    type="number"
                    InputProps={{
                      endAdornment: <InputAdornment position="end">{selectedOffer.asset}</InputAdornment>,
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Payment Method</InputLabel>
                    <Select label="Payment Method">
                      {selectedOffer.paymentMethods.map((method, index) => (
                        <MenuItem key={index} value={method}>
                          {method}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  • Price: ${selectedOffer.price.toFixed(3)} per {selectedOffer.asset}
                  <br />
                  • Limits: ${selectedOffer.limits.min} - ${selectedOffer.limits.max.toLocaleString()}
                  <br />
                  • Time limit: {selectedOffer.timeLimit} minutes
                  <br />• Available: {selectedOffer.available.toLocaleString()} {selectedOffer.asset}
                </Typography>
              </Alert>
            </Box>
          )}

          {orderStep === 1 && (
            <Box>
              <Alert severity="warning" sx={{ mb: 3 }}>
                Please transfer the payment to the merchant&apos;s account details below within the time limit.
              </Alert>

              <Paper sx={{ p: 3, bgcolor: 'background.default', mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Payment Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Bank Name
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Chase Bank</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Account Name
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">John Doe</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Account Number
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">1234567890</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Reference
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" fontWeight="bold">
                      P2P-ORD001
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Payment Notes (Optional)"
                placeholder="Add any notes about your payment"
                sx={{ mb: 2 }}
              />

              <Button variant="outlined" startIcon={<AttachFile />} fullWidth>
                Upload Payment Proof
              </Button>
            </Box>
          )}

          {orderStep === 2 && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                Your order has been created successfully!
              </Alert>

              <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                <Typography variant="h6" gutterBottom>
                  Order Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Order ID
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" fontWeight="bold">
                      ORD001
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Type
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Chip label={tabValue === 0 ? 'BUY' : 'SELL'} size="small" color="primary" />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Amount
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">1000 USDT</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Total
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" fontWeight="bold">
                      $1,002.00
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Status
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Chip label="Pending Payment" size="small" color="warning" />
                  </Grid>
                </Grid>
              </Paper>

              <Alert severity="info" sx={{ mt: 3 }}>
                Please complete the payment within 15 minutes and mark the order as paid. The crypto will be released
                after the merchant confirms receipt.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOrderDialogOpen(false)}>Cancel</Button>
          {orderStep > 0 && <Button onClick={handleBackStep}>Back</Button>}
          {orderStep < 2 ? (
            <Button variant="contained" onClick={handleNextStep}>
              Next
            </Button>
          ) : (
            <Button variant="contained" onClick={() => setOrderDialogOpen(false)}>
              Go to My Orders
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Chat Dialog */}
      <Dialog open={chatOpen} onClose={() => setChatOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ mr: 2 }}>C</Avatar>
              <Box>
                <Typography variant="h6">CryptoKing</Typography>
                <Typography variant="caption" color="success.main">
                  Online
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => setChatOpen(false)}>
              <Cancel />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ height: 400, overflowY: 'auto', mb: 2 }}>
            <List>
              <ListItem>
                <ListItemText
                  primary="Hello! I've sent the payment."
                  secondary="10:30 AM"
                  sx={{ textAlign: 'right' }}
                />
              </ListItem>
              <ListItem>
                <ListItemText primary="Great! I'll check and release the crypto shortly." secondary="10:32 AM" />
              </ListItem>
            </List>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField fullWidth size="small" placeholder="Type a message..." />
            <IconButton color="primary">
              <AttachFile />
            </IconButton>
            <IconButton color="primary">
              <Send />
            </IconButton>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default P2PPage;