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
  Chip,
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
  Alert,
  LinearProgress,
  Avatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Lock,
  LockOpen,
  Info,
  Add,
  Remove,
  History,
  Calculate,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';

interface StakingProduct {
  id: string;
  asset: string;
  type: 'flexible' | 'locked';
  apy: number;
  duration?: number;
  minAmount: number;
  totalStaked: number;
  available: number;
  icon: string;
}

interface UserStaking {
  id: string;
  asset: string;
  amount: number;
  apy: number;
  type: 'flexible' | 'locked';
  startDate: string;
  endDate?: string;
  earned: number;
  status: 'active' | 'completed' | 'pending';
}

const EarnPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [stakeDialogOpen, setStakeDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<StakingProduct | null>(null);
  const [stakeAmount, setStakeAmount] = useState('');
  const [calculatedReward, setCalculatedReward] = useState(0);

  // Mock data
  const [stakingProducts, setStakingProducts] = useState<StakingProduct[]>([
    {
      id: '1',
      asset: 'BTC',
      type: 'flexible',
      apy: 5.2,
      minAmount: 0.001,
      totalStaked: 1250.5,
      available: 500,
      icon: '/icons/btc.png',
    },
    {
      id: '2',
      asset: 'BTC',
      type: 'locked',
      apy: 8.5,
      duration: 30,
      minAmount: 0.01,
      totalStaked: 850.3,
      available: 300,
      icon: '/icons/btc.png',
    },
    {
      id: '3',
      asset: 'ETH',
      type: 'flexible',
      apy: 4.8,
      minAmount: 0.01,
      totalStaked: 8500.2,
      available: 3000,
      icon: '/icons/eth.png',
    },
    {
      id: '4',
      asset: 'ETH',
      type: 'locked',
      apy: 12.5,
      duration: 90,
      minAmount: 0.1,
      totalStaked: 5200.8,
      available: 2000,
      icon: '/icons/eth.png',
    },
    {
      id: '5',
      asset: 'USDT',
      type: 'flexible',
      apy: 8.0,
      minAmount: 10,
      totalStaked: 2500000,
      available: 1000000,
      icon: '/icons/usdt.png',
    },
    {
      id: '6',
      asset: 'USDT',
      type: 'locked',
      apy: 15.0,
      duration: 60,
      minAmount: 100,
      totalStaked: 1800000,
      available: 500000,
      icon: '/icons/usdt.png',
    },
  ]);

  const [userStakings, setUserStakings] = useState<UserStaking[]>([
    {
      id: '1',
      asset: 'BTC',
      amount: 0.5,
      apy: 5.2,
      type: 'flexible',
      startDate: '2024-01-01',
      earned: 0.0026,
      status: 'active',
    },
    {
      id: '2',
      asset: 'ETH',
      amount: 5.0,
      apy: 12.5,
      type: 'locked',
      startDate: '2024-01-15',
      endDate: '2024-04-15',
      earned: 0.156,
      status: 'active',
    },
    {
      id: '3',
      asset: 'USDT',
      amount: 10000,
      apy: 8.0,
      type: 'flexible',
      startDate: '2024-02-01',
      earned: 65.75,
      status: 'active',
    },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleStake = (product: StakingProduct) => {
    setSelectedProduct(product);
    setStakeDialogOpen(true);
    setStakeAmount('');
    setCalculatedReward(0);
  };

  const calculateReward = (amount: number, apy: number, days: number = 365) => {
    return (amount * apy * days) / (100 * 365);
  };

  const handleAmountChange = (value: string) => {
    setStakeAmount(value);
    if (selectedProduct && value) {
      const amount = parseFloat(value);
      const days = selectedProduct.duration || 365;
      const reward = calculateReward(amount, selectedProduct.apy, days);
      setCalculatedReward(reward);
    } else {
      setCalculatedReward(0);
    }
  };

  const totalStaked = userStakings.reduce((sum, stake) => sum + stake.amount, 0);
  const totalEarned = userStakings.reduce((sum, stake) => sum + stake.earned, 0);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Earn & Staking
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Stake your crypto and earn passive income with competitive APY rates.
        </Typography>
      </Box>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Total Staked Value
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                $45,230.50
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Across 3 assets
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Total Earned
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="success.main">
                $2,156.80
              </Typography>
              <Typography variant="caption" color="success.main">
                +4.77% return
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Calculate sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Avg. APY
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                8.57%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Weighted average
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Flexible Staking" />
          <Tab label="Locked Staking" />
          <Tab label="My Stakings" />
          <Tab label="DeFi Yield" />
          <Tab label="Launchpad" />
        </Tabs>

        {/* Flexible Staking Tab */}
        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Flexible staking allows you to stake and unstake anytime without lock-up periods. Rewards are
              distributed daily.
            </Alert>

            <Grid container spacing={3}>
              {stakingProducts
                .filter((p) => p.type === 'flexible')
                .map((product) => (
                  <Grid item xs={12} md={6} lg={4} key={product.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar src={product.icon} sx={{ width: 50, height: 50, mr: 2 }}>
                            {product.asset}
                          </Avatar>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="h6">{product.asset}</Typography>
                            <Chip label="Flexible" size="small" icon={<LockOpen />} color="success" />
                          </Box>
                        </Box>

                        <Box sx={{ mb: 2 }}>
                          <Typography variant="h4" color="primary.main" fontWeight="bold">
                            {product.apy}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Est. APY
                          </Typography>
                        </Box>

                        <Divider sx={{ my: 2 }} />

                        <Grid container spacing={1} sx={{ mb: 2 }}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Min. Amount
                            </Typography>
                            <Typography variant="body2">
                              {product.minAmount} {product.asset}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Available
                            </Typography>
                            <Typography variant="body2">
                              {product.available.toLocaleString()} {product.asset}
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary">
                              Total Staked
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                              <LinearProgress
                                variant="determinate"
                                value={(product.totalStaked / (product.totalStaked + product.available)) * 100}
                                sx={{ flex: 1, mr: 1, height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption">
                                {product.totalStaked.toLocaleString()} {product.asset}
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>

                        <Button fullWidth variant="contained" onClick={() => handleStake(product)}>
                          Stake Now
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          </Box>
        )}

        {/* Locked Staking Tab */}
        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Locked staking offers higher APY but requires you to lock your assets for a fixed period. Early
              withdrawal may result in penalty fees.
            </Alert>

            <Grid container spacing={3}>
              {stakingProducts
                .filter((p) => p.type === 'locked')
                .map((product) => (
                  <Grid item xs={12} md={6} lg={4} key={product.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar src={product.icon} sx={{ width: 50, height: 50, mr: 2 }}>
                            {product.asset}
                          </Avatar>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="h6">{product.asset}</Typography>
                            <Chip label={`${product.duration} Days`} size="small" icon={<Lock />} color="warning" />
                          </Box>
                        </Box>

                        <Box sx={{ mb: 2 }}>
                          <Typography variant="h4" color="primary.main" fontWeight="bold">
                            {product.apy}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Est. APY
                          </Typography>
                        </Box>

                        <Divider sx={{ my: 2 }} />

                        <Grid container spacing={1} sx={{ mb: 2 }}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Min. Amount
                            </Typography>
                            <Typography variant="body2">
                              {product.minAmount} {product.asset}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Duration
                            </Typography>
                            <Typography variant="body2">{product.duration} Days</Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary">
                              Total Staked
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                              <LinearProgress
                                variant="determinate"
                                value={(product.totalStaked / (product.totalStaked + product.available)) * 100}
                                sx={{ flex: 1, mr: 1, height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption">
                                {product.totalStaked.toLocaleString()} {product.asset}
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>

                        <Button fullWidth variant="contained" onClick={() => handleStake(product)}>
                          Stake Now
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
            </Grid>
          </Box>
        )}

        {/* My Stakings Tab */}
        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Asset</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="right">APY</TableCell>
                    <TableCell align="right">Earned</TableCell>
                    <TableCell>Start Date</TableCell>
                    <TableCell>End Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {userStakings.map((staking) => (
                    <TableRow key={staking.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ width: 32, height: 32, mr: 2 }}>{staking.asset[0]}</Avatar>
                          <Typography variant="body2" fontWeight="bold">
                            {staking.asset}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={staking.type}
                          size="small"
                          icon={staking.type === 'flexible' ? <LockOpen /> : <Lock />}
                          color={staking.type === 'flexible' ? 'success' : 'warning'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {staking.amount.toLocaleString()} {staking.asset}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="primary.main" fontWeight="bold">
                          {staking.apy}%
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main" fontWeight="bold">
                          +{staking.earned.toFixed(4)} {staking.asset}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{staking.startDate}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{staking.endDate || 'Flexible'}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={staking.status}
                          size="small"
                          color={staking.status === 'active' ? 'success' : 'default'}
                          icon={staking.status === 'active' ? <CheckCircle /> : <Schedule />}
                        />
                      </TableCell>
                      <TableCell align="right">
                        {staking.type === 'flexible' && (
                          <Button size="small" variant="outlined">
                            Unstake
                          </Button>
                        )}
                        {staking.type === 'locked' && (
                          <Button size="small" variant="outlined" disabled>
                            Locked
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

        {/* DeFi Yield Tab */}
        {tabValue === 3 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              DeFi yield farming allows you to provide liquidity to decentralized protocols and earn rewards. Higher
              APY comes with higher risk.
            </Alert>
            <Typography variant="h6" color="text.secondary" align="center" sx={{ py: 8 }}>
              DeFi Yield Farming Coming Soon
            </Typography>
          </Box>
        )}

        {/* Launchpad Tab */}
        {tabValue === 4 && (
          <Box sx={{ p: 3 }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Stake tokens to participate in new token launches and get early access to promising projects.
            </Alert>
            <Typography variant="h6" color="text.secondary" align="center" sx={{ py: 8 }}>
              Launchpad Staking Coming Soon
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Stake Dialog */}
      <Dialog open={stakeDialogOpen} onClose={() => setStakeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Stake {selectedProduct?.asset} - {selectedProduct?.type === 'flexible' ? 'Flexible' : 'Locked'}
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Box sx={{ mt: 2 }}>
              {/* Product Info */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      APY
                    </Typography>
                    <Typography variant="h6" color="primary.main">
                      {selectedProduct.apy}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      {selectedProduct.type === 'locked' ? 'Duration' : 'Type'}
                    </Typography>
                    <Typography variant="h6">
                      {selectedProduct.type === 'locked' ? `${selectedProduct.duration} Days` : 'Flexible'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Min. Amount
                    </Typography>
                    <Typography variant="body2">
                      {selectedProduct.minAmount} {selectedProduct.asset}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Available
                    </Typography>
                    <Typography variant="body2">
                      {selectedProduct.available.toLocaleString()} {selectedProduct.asset}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Stake Amount */}
              <TextField
                fullWidth
                label="Stake Amount"
                type="number"
                value={stakeAmount}
                onChange={(e) => handleAmountChange(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Typography>{selectedProduct.asset}</Typography>
                      <Button size="small" sx={{ ml: 1 }}>
                        Max
                      </Button>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Available Balance:
                </Typography>
                <Typography variant="body2">
                  2.5 {selectedProduct.asset}
                </Typography>
              </Box>

              {/* Reward Calculation */}
              {calculatedReward > 0 && (
                <Paper sx={{ p: 2, mb: 3, bgcolor: 'success.light' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Estimated Rewards
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {calculatedReward.toFixed(6)} {selectedProduct.asset}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedProduct.type === 'locked'
                      ? `After ${selectedProduct.duration} days`
                      : 'Per year (flexible)'}
                  </Typography>
                </Paper>
              )}

              {/* Terms */}
              <Alert severity="warning">
                <Typography variant="body2">
                  {selectedProduct.type === 'flexible' ? (
                    <>
                      • You can unstake anytime
                      <br />
                      • Rewards are distributed daily
                      <br />• No lock-up period
                    </>
                  ) : (
                    <>
                      • Assets will be locked for {selectedProduct.duration} days
                      <br />
                      • Early withdrawal incurs 10% penalty
                      <br />• Rewards are paid at maturity
                    </>
                  )}
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStakeDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!stakeAmount || parseFloat(stakeAmount) < (selectedProduct?.minAmount || 0)}>
            Confirm Stake
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EarnPage;