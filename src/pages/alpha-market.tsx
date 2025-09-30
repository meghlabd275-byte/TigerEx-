import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  TrendingUp,
  Clock,
  Shield,
  Users,
  DollarSign,
  AlertCircle,
  CheckCircle,
  ExternalLink,
  Star,
} from 'lucide-react';

interface AlphaToken {
  tokenId: string;
  name: string;
  symbol: string;
  description: string;
  blockchain: string;
  alphaPrice: number;
  totalSupply: number;
  alphaAllocation: number;
  soldAmount: number;
  totalInvestors: number;
  progressPercentage: number;
  riskScore: number;
  alphaStartDate: string;
  alphaEndDate: string;
  minInvestment: number;
  maxInvestment: number;
  isKYCRequired: boolean;
  projectTeam: Array<{
    name: string;
    role: string;
    linkedin?: string;
    experience?: string;
  }>;
  website?: string;
  socialLinks?: {
    twitter?: string;
    telegram?: string;
    discord?: string;
    medium?: string;
  };
  vestingSchedule: Array<{
    releaseDate: string;
    percentage: number;
    description: string;
  }>;
}

interface UserInvestment {
  investmentId: string;
  tokenId: string;
  investmentAmount: number;
  tokenAmount: number;
  status: 'pending' | 'confirmed' | 'failed' | 'refunded';
  investedAt: string;
  userTier: string;
  totalVested: number;
  totalClaimed: number;
}

interface InvestmentForm {
  tokenId: string;
  investmentAmount: string;
  paymentMethod: string;
  referralCode: string;
  riskAcknowledged: boolean;
}

const AlphaMarketPage: React.FC = () => {
  const [alphaTokens, setAlphaTokens] = useState<AlphaToken[]>([]);
  const [userInvestments, setUserInvestments] = useState<UserInvestment[]>([]);
  const [filteredTokens, setFilteredTokens] = useState<AlphaToken[]>([]);
  const [selectedToken, setSelectedToken] = useState<AlphaToken | null>(null);

  // Filters
  const [blockchainFilter, setBlockchainFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string>('trending');

  // Investment form
  const [isInvestDialogOpen, setIsInvestDialogOpen] = useState(false);
  const [investmentForm, setInvestmentForm] = useState<InvestmentForm>({
    tokenId: '',
    investmentAmount: '',
    paymentMethod: 'USDT',
    referralCode: '',
    riskAcknowledged: false,
  });

  // Loading states
  const [loading, setLoading] = useState(false);
  const [investing, setInvesting] = useState(false);

  // User data
  const [userTier, setUserTier] = useState('bronze');
  const [userStakeAmount, setUserStakeAmount] = useState(0);
  const [userKYCStatus, setUserKYCStatus] = useState('pending');

  useEffect(() => {
    loadAlphaTokens();
    loadUserInvestments();
    loadUserProfile();
  }, []);

  useEffect(() => {
    filterAndSortTokens();
  }, [alphaTokens, blockchainFilter, riskFilter, searchQuery, sortBy]);

  const loadAlphaTokens = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/alpha/tokens?status=active');
      if (response.ok) {
        const data = await response.json();
        setAlphaTokens(data.data || []);
      }
    } catch (error) {
      console.error('Failed to load alpha tokens:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserInvestments = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('/api/investors/investments', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setUserInvestments(data.data || []);
      }
    } catch (error) {
      console.error('Failed to load user investments:', error);
    }
  };

  const loadUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('/api/users/profile', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setUserTier(data.tier || 'bronze');
        setUserStakeAmount(data.stakeAmount || 0);
        setUserKYCStatus(data.kycStatus || 'pending');
      }
    } catch (error) {
      console.error('Failed to load user profile:', error);
    }
  };

  const filterAndSortTokens = () => {
    let filtered = alphaTokens;

    // Apply filters
    if (blockchainFilter !== 'all') {
      filtered = filtered.filter(
        (token) => token.blockchain === blockchainFilter
      );
    }

    if (riskFilter !== 'all') {
      if (riskFilter === 'low') {
        filtered = filtered.filter((token) => token.riskScore >= 80);
      } else if (riskFilter === 'medium') {
        filtered = filtered.filter(
          (token) => token.riskScore >= 60 && token.riskScore < 80
        );
      } else if (riskFilter === 'high') {
        filtered = filtered.filter((token) => token.riskScore < 60);
      }
    }

    if (searchQuery) {
      filtered = filtered.filter(
        (token) =>
          token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          token.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          token.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply sorting
    if (sortBy === 'trending') {
      filtered.sort((a, b) => b.totalInvestors - a.totalInvestors);
    } else if (sortBy === 'price_low') {
      filtered.sort((a, b) => a.alphaPrice - b.alphaPrice);
    } else if (sortBy === 'price_high') {
      filtered.sort((a, b) => b.alphaPrice - a.alphaPrice);
    } else if (sortBy === 'risk_low') {
      filtered.sort((a, b) => b.riskScore - a.riskScore);
    } else if (sortBy === 'ending_soon') {
      filtered.sort(
        (a, b) =>
          new Date(a.alphaEndDate).getTime() -
          new Date(b.alphaEndDate).getTime()
      );
    }

    setFilteredTokens(filtered);
  };

  const openInvestDialog = (token: AlphaToken) => {
    setSelectedToken(token);
    setInvestmentForm({
      tokenId: token.tokenId,
      investmentAmount: token.minInvestment.toString(),
      paymentMethod: 'USDT',
      referralCode: '',
      riskAcknowledged: false,
    });
    setIsInvestDialogOpen(true);
  };

  const submitInvestment = async () => {
    if (!selectedToken || !investmentForm.riskAcknowledged) return;

    try {
      setInvesting(true);

      const response = await fetch(
        `/api/alpha/tokens/${selectedToken.tokenId}/invest`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            investmentAmount: parseFloat(investmentForm.investmentAmount),
            paymentMethod: investmentForm.paymentMethod,
            referralCode: investmentForm.referralCode,
            riskAcknowledged: investmentForm.riskAcknowledged,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert('Investment submitted successfully!');
        setIsInvestDialogOpen(false);
        loadUserInvestments();
        loadAlphaTokens();
      } else {
        const error = await response.json();
        alert(`Investment failed: ${error.message}`);
      }
    } catch (error) {
      console.error('Failed to submit investment:', error);
      alert('Failed to submit investment');
    } finally {
      setInvesting(false);
    }
  };

  const getRiskBadge = (riskScore: number) => {
    if (riskScore >= 80) {
      return <Badge className="bg-green-100 text-green-800">LOW RISK</Badge>;
    } else if (riskScore >= 60) {
      return (
        <Badge className="bg-yellow-100 text-yellow-800">MEDIUM RISK</Badge>
      );
    } else {
      return <Badge className="bg-red-100 text-red-800">HIGH RISK</Badge>;
    }
  };

  const getTierBadge = (tier: string) => {
    const colors = {
      bronze: 'bg-orange-100 text-orange-800',
      silver: 'bg-gray-100 text-gray-800',
      gold: 'bg-yellow-100 text-yellow-800',
      platinum: 'bg-purple-100 text-purple-800',
    };

    return (
      <Badge className={colors[tier as keyof typeof colors]}>
        {tier.toUpperCase()}
      </Badge>
    );
  };

  const formatTimeRemaining = (endDate: string) => {
    const now = new Date();
    const end = new Date(endDate);
    const diff = end.getTime() - now.getTime();

    if (diff <= 0) return 'Ended';

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h`;
  };

  const canInvest = (token: AlphaToken) => {
    if (token.isKYCRequired && userKYCStatus !== 'approved') return false;

    const tierRequirements = {
      bronze: 1000,
      silver: 5000,
      gold: 25000,
      platinum: 100000,
    };

    return (
      userStakeAmount >=
      tierRequirements[userTier as keyof typeof tierRequirements]
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Alpha Market</h1>
          <p className="text-muted-foreground">
            Get early access to promising tokens before public launch
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Your Tier</div>
            <div>{getTierBadge(userTier)}</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Stake Amount</div>
            <div className="font-semibold">
              ${userStakeAmount.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* User KYC Warning */}
      {userKYCStatus !== 'approved' && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <div>
                <div className="font-medium text-yellow-800">
                  KYC Verification Required
                </div>
                <div className="text-sm text-yellow-700">
                  Complete your KYC verification to access high-value
                  investments and unlock all features.
                </div>
              </div>
              <Button variant="outline" size="sm">
                Complete KYC
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="discover" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="discover">Discover</TabsTrigger>
          <TabsTrigger value="portfolio">My Portfolio</TabsTrigger>
          <TabsTrigger value="trending">Trending</TabsTrigger>
        </TabsList>

        <TabsContent value="discover" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Label htmlFor="search">Search</Label>
                  <Input
                    id="search"
                    placeholder="Search tokens..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="min-w-[150px]">
                  <Label htmlFor="blockchain">Blockchain</Label>
                  <Select
                    value={blockchainFilter}
                    onValueChange={setBlockchainFilter}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Blockchains</SelectItem>
                      <SelectItem value="ethereum">Ethereum</SelectItem>
                      <SelectItem value="bsc">BSC</SelectItem>
                      <SelectItem value="polygon">Polygon</SelectItem>
                      <SelectItem value="arbitrum">Arbitrum</SelectItem>
                      <SelectItem value="optimism">Optimism</SelectItem>
                      <SelectItem value="avalanche">Avalanche</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="min-w-[150px]">
                  <Label htmlFor="risk">Risk Level</Label>
                  <Select value={riskFilter} onValueChange={setRiskFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Risk Levels</SelectItem>
                      <SelectItem value="low">Low Risk</SelectItem>
                      <SelectItem value="medium">Medium Risk</SelectItem>
                      <SelectItem value="high">High Risk</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="min-w-[150px]">
                  <Label htmlFor="sort">Sort By</Label>
                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="trending">Trending</SelectItem>
                      <SelectItem value="price_low">
                        Price: Low to High
                      </SelectItem>
                      <SelectItem value="price_high">
                        Price: High to Low
                      </SelectItem>
                      <SelectItem value="risk_low">Lowest Risk</SelectItem>
                      <SelectItem value="ending_soon">Ending Soon</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alpha Tokens Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTokens.map((token) => (
              <Card
                key={token.tokenId}
                className="hover:shadow-lg transition-shadow"
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{token.name}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline">{token.symbol}</Badge>
                        <Badge variant="outline">
                          {token.blockchain.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold">
                        ${token.alphaPrice}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        per token
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {token.description}
                  </p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>{token.progressPercentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${token.progressPercentage}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">
                        {token.totalInvestors} investors
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">
                        {formatTimeRemaining(token.alphaEndDate)}
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    {getRiskBadge(token.riskScore)}
                    {token.isKYCRequired && (
                      <div className="flex items-center space-x-1">
                        <Shield className="h-4 w-4 text-blue-600" />
                        <span className="text-xs text-blue-600">
                          KYC Required
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <Button
                      className="flex-1"
                      onClick={() => openInvestDialog(token)}
                      disabled={!canInvest(token)}
                    >
                      {canInvest(token)
                        ? 'Invest Now'
                        : 'Tier Upgrade Required'}
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>My Alpha Investments</CardTitle>
            </CardHeader>
            <CardContent>
              {userInvestments.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-muted-foreground">
                    No investments yet
                  </div>
                  <Button
                    className="mt-4"
                    onClick={() =>
                      document.querySelector('[value="discover"]')?.click()
                    }
                  >
                    Discover Alpha Tokens
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {userInvestments.map((investment) => {
                    const token = alphaTokens.find(
                      (t) => t.tokenId === investment.tokenId
                    );
                    return (
                      <Card key={investment.investmentId}>
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">
                                {token?.name || 'Unknown Token'}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {token?.symbol} •{' '}
                                {investment.userTier.toUpperCase()} Tier
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-medium">
                                ${investment.investmentAmount}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {investment.tokenAmount.toFixed(2)} tokens
                              </div>
                            </div>
                          </div>
                          <div className="mt-4 flex justify-between items-center">
                            <Badge
                              variant={
                                investment.status === 'confirmed'
                                  ? 'default'
                                  : 'secondary'
                              }
                            >
                              {investment.status.toUpperCase()}
                            </Badge>
                            <div className="text-sm text-muted-foreground">
                              Invested:{' '}
                              {new Date(
                                investment.investedAt
                              ).toLocaleDateString()}
                            </div>
                          </div>
                          {investment.status === 'confirmed' && (
                            <div className="mt-4 space-y-2">
                              <div className="flex justify-between text-sm">
                                <span>Vested</span>
                                <span>
                                  {investment.totalVested.toFixed(2)} tokens
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Claimed</span>
                                <span>
                                  {investment.totalClaimed.toFixed(2)} tokens
                                </span>
                              </div>
                              <div className="flex justify-between text-sm font-medium">
                                <span>Available to Claim</span>
                                <span>
                                  {(
                                    investment.totalVested -
                                    investment.totalClaimed
                                  ).toFixed(2)}{' '}
                                  tokens
                                </span>
                              </div>
                              {investment.totalVested >
                                investment.totalClaimed && (
                                <Button size="sm" className="w-full mt-2">
                                  Claim Tokens
                                </Button>
                              )}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trending" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {alphaTokens
              .sort((a, b) => b.totalInvestors - a.totalInvestors)
              .slice(0, 6)
              .map((token, index) => (
                <Card key={token.tokenId} className="relative">
                  {index < 3 && (
                    <div className="absolute top-2 right-2">
                      <Badge className="bg-yellow-100 text-yellow-800">
                        <Star className="h-3 w-3 mr-1" />#{index + 1}
                      </Badge>
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle className="text-lg">{token.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{token.symbol}</Badge>
                      <Badge variant="outline">
                        {token.blockchain.toUpperCase()}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold">
                        ${token.alphaPrice}
                      </span>
                      {getRiskBadge(token.riskScore)}
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Investors: {token.totalInvestors}</span>
                      <span>
                        Progress: {token.progressPercentage.toFixed(1)}%
                      </span>
                    </div>
                    <Button
                      className="w-full"
                      onClick={() => openInvestDialog(token)}
                      disabled={!canInvest(token)}
                    >
                      {canInvest(token)
                        ? 'Invest Now'
                        : 'Tier Upgrade Required'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Investment Dialog */}
      <Dialog open={isInvestDialogOpen} onOpenChange={setIsInvestDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Invest in {selectedToken?.name}</DialogTitle>
          </DialogHeader>
          {selectedToken && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Token Price</Label>
                  <div className="text-2xl font-bold">
                    ${selectedToken.alphaPrice}
                  </div>
                </div>
                <div>
                  <Label>Your Tier</Label>
                  <div>{getTierBadge(userTier)}</div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="investmentAmount">
                    Investment Amount (USD)
                  </Label>
                  <Input
                    id="investmentAmount"
                    type="number"
                    min={selectedToken.minInvestment}
                    max={selectedToken.maxInvestment}
                    value={investmentForm.investmentAmount}
                    onChange={(e) =>
                      setInvestmentForm((prev) => ({
                        ...prev,
                        investmentAmount: e.target.value,
                      }))
                    }
                    placeholder={`Min: $${selectedToken.minInvestment}`}
                  />
                  <div className="text-sm text-muted-foreground mt-1">
                    Min: ${selectedToken.minInvestment} • Max: $
                    {selectedToken.maxInvestment}
                  </div>
                </div>

                <div>
                  <Label htmlFor="paymentMethod">Payment Method</Label>
                  <Select
                    value={investmentForm.paymentMethod}
                    onValueChange={(value) =>
                      setInvestmentForm((prev) => ({
                        ...prev,
                        paymentMethod: value,
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USDT">USDT</SelectItem>
                      <SelectItem value="USDC">USDC</SelectItem>
                      <SelectItem value="ETH">ETH</SelectItem>
                      <SelectItem value="BNB">BNB</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="referralCode">Referral Code (Optional)</Label>
                  <Input
                    id="referralCode"
                    value={investmentForm.referralCode}
                    onChange={(e) =>
                      setInvestmentForm((prev) => ({
                        ...prev,
                        referralCode: e.target.value,
                      }))
                    }
                    placeholder="Enter referral code"
                  />
                </div>

                {investmentForm.investmentAmount && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm font-medium mb-2">
                      Investment Summary
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Investment Amount:</span>
                        <span>${investmentForm.investmentAmount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Token Amount:</span>
                        <span>
                          {(
                            parseFloat(investmentForm.investmentAmount) /
                            selectedToken.alphaPrice
                          ).toFixed(2)}{' '}
                          {selectedToken.symbol}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Payment Method:</span>
                        <span>{investmentForm.paymentMethod}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    id="riskAcknowledged"
                    checked={investmentForm.riskAcknowledged}
                    onChange={(e) =>
                      setInvestmentForm((prev) => ({
                        ...prev,
                        riskAcknowledged: e.target.checked,
                      }))
                    }
                    className="mt-1"
                  />
                  <Label htmlFor="riskAcknowledged" className="text-sm">
                    I acknowledge that this is a high-risk investment and I
                    understand the risks involved. I have read and agree to the
                    terms and conditions.
                  </Label>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setIsInvestDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={submitInvestment}
                  disabled={
                    investing ||
                    !investmentForm.riskAcknowledged ||
                    !investmentForm.investmentAmount
                  }
                >
                  {investing ? 'Processing...' : 'Confirm Investment'}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AlphaMarketPage;
