import React, { useState } from 'react';
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
  Button,
  Tabs,
  Tab,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  InputAdornment,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
} from '@mui/material';
import {
  AccountBalanceWallet,
  Send,
  CallReceived,
  SwapHoriz,
  ContentCopy,
  QrCode2,
  History,
  Security,
  Add,
  Remove,
  TrendingUp,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import { QRCodeSVG } from 'qrcode.react';

interface WalletAsset {
  id: string;
  symbol: string;
  name: string;
  balance: number;
  availableBalance: number;
  inOrders: number;
  btcValue: number;
  usdValue: number;
  network: string;
}

interface Transaction {
  id: string;
  type: 'deposit' | 'withdrawal' | 'transfer';
  asset: string;
  amount: number;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
  txHash?: string;
  fee: number;
}

const WalletPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [depositDialogOpen, setDepositDialogOpen] = useState(false);
  const [withdrawDialogOpen, setWithdrawDialogOpen] = useState(false);
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState('BTC');
  const [selectedNetwork, setSelectedNetwork] = useState('Bitcoin');
  const [withdrawStep, setWithdrawStep] = useState(0);

  // Mock data
  const [walletAssets, setWalletAssets] = useState<WalletAsset[]>([
    {
      id: '1',
      symbol: 'BTC',
      name: 'Bitcoin',
      balance: 2.5,
      availableBalance: 2.3,
      inOrders: 0.2,
      btcValue: 2.5,
      usdValue: 105000,
      network: 'Bitcoin',
    },
    {
      id: '2',
      symbol: 'ETH',
      name: 'Ethereum',
      balance: 15.8,
      availableBalance: 14.5,
      inOrders: 1.3,
      btcValue: 0.85,
      usdValue: 35640,
      network: 'Ethereum',
    },
    {
      id: '3',
      symbol: 'USDT',
      name: 'Tether',
      balance: 25000,
      availableBalance: 23500,
      inOrders: 1500,
      btcValue: 0.595,
      usdValue: 25000,
      network: 'ERC20',
    },
  ]);

  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: '1',
      type: 'deposit',
      asset: 'BTC',
      amount: 0.5,
      status: 'completed',
      timestamp: '2024-01-15 10:30:00',
      txHash: '0x1234...5678',
      fee: 0.0001,
    },
    {
      id: '2',
      type: 'withdrawal',
      asset: 'ETH',
      amount: 2.0,
      status: 'pending',
      timestamp: '2024-01-15 09:15:00',
      txHash: '0xabcd...efgh',
      fee: 0.005,
    },
    {
      id: '3',
      type: 'transfer',
      asset: 'USDT',
      amount: 1000,
      status: 'completed',
      timestamp: '2024-01-14 18:45:00',
      fee: 1,
    },
  ]);

  const depositAddress = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa';

  const networks = [
    { value: 'Bitcoin', label: 'Bitcoin (BTC)', fee: '0.0005 BTC' },
    { value: 'ERC20', label: 'Ethereum (ERC20)', fee: '0.005 ETH' },
    { value: 'TRC20', label: 'Tron (TRC20)', fee: '1 USDT' },
    { value: 'BSC', label: 'BNB Smart Chain (BEP20)', fee: '0.0005 BNB' },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCopyAddress = () => {
    navigator.clipboard.writeText(depositAddress);
    // Show success message
  };

  const handleWithdrawNext = () => {
    setWithdrawStep((prev) => prev + 1);
  };

  const handleWithdrawBack = () => {
    setWithdrawStep((prev) => prev - 1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'deposit':
        return <CallReceived color="success" />;
      case 'withdrawal':
        return <Send color="error" />;
      case 'transfer':
        return <SwapHoriz color="primary" />;
      default:
        return <History />;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Wallet Overview */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Wallet Management
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AccountBalanceWallet sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" color="text.secondary">
                    Total Balance
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  $165,640.00
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  ≈ 3.95 BTC
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Available Balance
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  $140,300.00
                </Typography>
                <Typography variant="caption" color="success.main">
                  84.7% of total
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  In Orders
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  $25,340.00
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  15.3% of total
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<CallReceived />}
              onClick={() => setDepositDialogOpen(true)}
              sx={{ py: 2 }}
            >
              Deposit
            </Button>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<Send />}
              onClick={() => setWithdrawDialogOpen(true)}
              sx={{ py: 2 }}
            >
              Withdraw
            </Button>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<SwapHoriz />}
              onClick={() => setTransferDialogOpen(true)}
              sx={{ py: 2 }}
            >
              Transfer
            </Button>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<History />}
              sx={{ py: 2 }}
            >
              History
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Assets Table */}
      <Paper sx={{ mb: 4 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Spot Wallet" />
          <Tab label="Funding Wallet" />
          <Tab label="Futures Wallet" />
          <Tab label="Earn Wallet" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Asset</TableCell>
                  <TableCell align="right">Total Balance</TableCell>
                  <TableCell align="right">Available</TableCell>
                  <TableCell align="right">In Orders</TableCell>
                  <TableCell align="right">BTC Value</TableCell>
                  <TableCell align="right">USD Value</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {walletAssets.map((asset) => (
                  <TableRow key={asset.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ width: 32, height: 32, mr: 2 }}>
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
                      <Typography variant="body2" fontWeight="bold">
                        {asset.balance.toFixed(4)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {asset.availableBalance.toFixed(4)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="text.secondary">
                        {asset.inOrders.toFixed(4)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {asset.btcValue.toFixed(6)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        ${asset.usdValue.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small" variant="outlined" sx={{ mr: 1 }}>
                        Deposit
                      </Button>
                      <Button size="small" variant="outlined">
                        Withdraw
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Paper>

      {/* Recent Transactions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Recent Transactions
        </Typography>
        <List>
          {transactions.map((tx, index) => (
            <React.Fragment key={tx.id}>
              <ListItem>
                <ListItemAvatar>
                  <Avatar>{getTransactionIcon(tx.type)}</Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body1" sx={{ mr: 1 }}>
                        {tx.type.charAt(0).toUpperCase() + tx.type.slice(1)}
                      </Typography>
                      <Chip
                        label={tx.status}
                        size="small"
                        color={getStatusColor(tx.status) as any}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {tx.amount} {tx.asset} • Fee: {tx.fee} {tx.asset}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {tx.timestamp}
                      </Typography>
                    </Box>
                  }
                />
                <Box sx={{ textAlign: 'right' }}>
                  {tx.txHash && (
                    <Button size="small" endIcon={<ContentCopy />}>
                      Copy TxHash
                    </Button>
                  )}
                </Box>
              </ListItem>
              {index < transactions.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Paper>

      {/* Deposit Dialog */}
      <Dialog open={depositDialogOpen} onClose={() => setDepositDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Deposit Crypto</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Select Asset</InputLabel>
              <Select
                value={selectedAsset}
                onChange={(e) => setSelectedAsset(e.target.value)}
                label="Select Asset"
              >
                <MenuItem value="BTC">Bitcoin (BTC)</MenuItem>
                <MenuItem value="ETH">Ethereum (ETH)</MenuItem>
                <MenuItem value="USDT">Tether (USDT)</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Select Network</InputLabel>
              <Select
                value={selectedNetwork}
                onChange={(e) => setSelectedNetwork(e.target.value)}
                label="Select Network"
              >
                {networks.map((network) => (
                  <MenuItem key={network.value} value={network.value}>
                    {network.label} - Fee: {network.fee}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Alert severity="warning" sx={{ mb: 3 }}>
              Send only {selectedAsset} to this address. Sending any other asset may result in permanent loss.
            </Alert>

            <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'background.default' }}>
              <QRCodeSVG value={depositAddress} size={200} />
              <Typography variant="body2" sx={{ mt: 2, wordBreak: 'break-all' }}>
                {depositAddress}
              </Typography>
              <Button
                startIcon={<ContentCopy />}
                onClick={handleCopyAddress}
                sx={{ mt: 2 }}
              >
                Copy Address
              </Button>
            </Paper>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                • Minimum deposit: 0.0001 {selectedAsset}
                <br />
                • Network confirmations required: 3
                <br />
                • Estimated arrival time: 10-30 minutes
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDepositDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Withdraw Dialog */}
      <Dialog open={withdrawDialogOpen} onClose={() => setWithdrawDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Withdraw Crypto</DialogTitle>
        <DialogContent>
          <Stepper activeStep={withdrawStep} sx={{ mt: 2, mb: 4 }}>
            <Step>
              <StepLabel>Details</StepLabel>
            </Step>
            <Step>
              <StepLabel>Verification</StepLabel>
            </Step>
            <Step>
              <StepLabel>Confirm</StepLabel>
            </Step>
          </Stepper>

          {withdrawStep === 0 && (
            <Box>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Asset</InputLabel>
                <Select value={selectedAsset} onChange={(e) => setSelectedAsset(e.target.value)} label="Select Asset">
                  <MenuItem value="BTC">Bitcoin (BTC)</MenuItem>
                  <MenuItem value="ETH">Ethereum (ETH)</MenuItem>
                  <MenuItem value="USDT">Tether (USDT)</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Network</InputLabel>
                <Select value={selectedNetwork} onChange={(e) => setSelectedNetwork(e.target.value)} label="Select Network">
                  {networks.map((network) => (
                    <MenuItem key={network.value} value={network.value}>
                      {network.label} - Fee: {network.fee}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Withdrawal Address"
                placeholder="Enter withdrawal address"
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Amount"
                type="number"
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button size="small">Max</Button>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Available: 2.5 BTC
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Fee: 0.0005 BTC
                </Typography>
              </Box>

              <Alert severity="warning">
                Please double-check the withdrawal address. Transactions cannot be reversed.
              </Alert>
            </Box>
          )}

          {withdrawStep === 1 && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                For security, please complete the verification steps below.
              </Alert>

              <TextField
                fullWidth
                label="Email Verification Code"
                placeholder="Enter 6-digit code"
                sx={{ mb: 3 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button size="small">Send Code</Button>
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="2FA Code"
                placeholder="Enter 6-digit code"
                sx={{ mb: 3 }}
              />
            </Box>
          )}

          {withdrawStep === 2 && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                Please review your withdrawal details carefully.
              </Alert>

              <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Asset
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" align="right">
                      Bitcoin (BTC)
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Network
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" align="right">
                      Bitcoin
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Address
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" align="right" sx={{ wordBreak: 'break-all' }}>
                      1A1z...DivfNa
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Amount
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" align="right" fontWeight="bold">
                      1.5 BTC
                    </Typography>
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Fee
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" align="right">
                      0.0005 BTC
                    </Typography>
                  </Grid>

                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                  </Grid>

                  <Grid item xs={6}>
                    <Typography variant="body1" fontWeight="bold">
                      You will receive
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" align="right" fontWeight="bold">
                      1.4995 BTC
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWithdrawDialogOpen(false)}>Cancel</Button>
          {withdrawStep > 0 && (
            <Button onClick={handleWithdrawBack}>Back</Button>
          )}
          {withdrawStep < 2 ? (
            <Button variant="contained" onClick={handleWithdrawNext}>
              Next
            </Button>
          ) : (
            <Button variant="contained" color="primary">
              Confirm Withdrawal
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Transfer Dialog */}
      <Dialog open={transferDialogOpen} onClose={() => setTransferDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Internal Transfer</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>From</InputLabel>
              <Select label="From">
                <MenuItem value="spot">Spot Wallet</MenuItem>
                <MenuItem value="funding">Funding Wallet</MenuItem>
                <MenuItem value="futures">Futures Wallet</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>To</InputLabel>
              <Select label="To">
                <MenuItem value="spot">Spot Wallet</MenuItem>
                <MenuItem value="funding">Funding Wallet</MenuItem>
                <MenuItem value="futures">Futures Wallet</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Asset</InputLabel>
              <Select label="Asset">
                <MenuItem value="BTC">Bitcoin (BTC)</MenuItem>
                <MenuItem value="ETH">Ethereum (ETH)</MenuItem>
                <MenuItem value="USDT">Tether (USDT)</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Amount"
              type="number"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Button size="small">Max</Button>
                  </InputAdornment>
                ),
              }}
            />

            <Alert severity="info" sx={{ mt: 3 }}>
              Internal transfers are instant and free of charge.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTransferDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Confirm Transfer</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default WalletPage;