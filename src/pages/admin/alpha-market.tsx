import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Users,
  DollarSign,
  Activity,
} from 'lucide-react';

interface AlphaToken {
  tokenId: string;
  name: string;
  symbol: string;
  description: string;
  blockchain: string;
  status: 'pending' | 'approved' | 'active' | 'completed' | 'rejected';
  alphaPrice: number;
  totalSupply: number;
  alphaAllocation: number;
  soldAmount: number;
  totalInvestors: number;
  progressPercentage: number;
  riskScore: number;
  alphaStartDate: string;
  alphaEndDate: string;
  createdAt: string;
  createdBy: string;
}

interface AlphaInvestment {
  investmentId: string;
  userId: string;
  tokenId: string;
  investmentAmount: number;
  tokenAmount: number;
  userTier: string;
  status: 'pending' | 'confirmed' | 'failed' | 'refunded';
  investedAt: string;
  blockchain: string;
  paymentMethod: string;
}

interface CreateTokenForm {
  name: string;
  symbol: string;
  description: string;
  blockchain: string;
  decimals: number;
  alphaPrice: string;
  totalSupply: string;
  alphaAllocation: string;
  minInvestment: string;
  maxInvestment: string;
  alphaStartDate: string;
  alphaEndDate: string;
  publicLaunchDate: string;
  isKYCRequired: boolean;
  isWhitelisted: boolean;
  projectTeam: Array<{
    name: string;
    role: string;
    linkedin: string;
    experience: string;
  }>;
  whitepaper: {
    url: string;
    hash: string;
  };
  website: string;
  socialLinks: {
    twitter: string;
    telegram: string;
    discord: string;
    medium: string;
  };
  vestingSchedule: Array<{
    releaseDate: string;
    percentage: number;
    description: string;
  }>;
}

const AlphaMarketAdminPage: React.FC = () => {
  const [alphaTokens, setAlphaTokens] = useState<AlphaToken[]>([]);
  const [investments, setInvestments] = useState<AlphaInvestment[]>([]);
  const [filteredTokens, setFilteredTokens] = useState<AlphaToken[]>([]);
  const [selectedToken, setSelectedToken] = useState<AlphaToken | null>(null);

  // Filters and search
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [blockchainFilter, setBlockchainFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState<CreateTokenForm>({
    name: '',
    symbol: '',
    description: '',
    blockchain: 'ethereum',
    decimals: 18,
    alphaPrice: '',
    totalSupply: '',
    alphaAllocation: '',
    minInvestment: '100',
    maxInvestment: '10000',
    alphaStartDate: '',
    alphaEndDate: '',
    publicLaunchDate: '',
    isKYCRequired: true,
    isWhitelisted: false,
    projectTeam: [{ name: '', role: '', linkedin: '', experience: '' }],
    whitepaper: { url: '', hash: '' },
    website: '',
    socialLinks: { twitter: '', telegram: '', discord: '', medium: '' },
    vestingSchedule: [
      { releaseDate: '', percentage: 25, description: 'Initial release' },
      { releaseDate: '', percentage: 25, description: '3 months' },
      { releaseDate: '', percentage: 25, description: '6 months' },
      { releaseDate: '', percentage: 25, description: '12 months' },
    ],
  });

  // Loading states
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  // Statistics
  const [stats, setStats] = useState({
    totalTokens: 0,
    activeTokens: 0,
    totalRaised: 0,
    totalInvestors: 0,
    averageRiskScore: 0,
  });

  useEffect(() => {
    loadAlphaTokens();
    loadInvestments();
    loadStats();
  }, []);

  useEffect(() => {
    filterTokens();
  }, [alphaTokens, statusFilter, blockchainFilter, searchQuery]);

  const loadAlphaTokens = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/alpha/tokens');
      if (response.ok) {
        const tokens = await response.json();
        setAlphaTokens(tokens.data || []);
      }
    } catch (error) {
      console.error('Failed to load alpha tokens:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadInvestments = async () => {
    try {
      const response = await fetch('/api/alpha/investments');
      if (response.ok) {
        const data = await response.json();
        setInvestments(data.data || []);
      }
    } catch (error) {
      console.error('Failed to load investments:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/alpha/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data.data || stats);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const filterTokens = () => {
    let filtered = alphaTokens;

    if (statusFilter !== 'all') {
      filtered = filtered.filter((token) => token.status === statusFilter);
    }

    if (blockchainFilter !== 'all') {
      filtered = filtered.filter(
        (token) => token.blockchain === blockchainFilter
      );
    }

    if (searchQuery) {
      filtered = filtered.filter(
        (token) =>
          token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          token.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          token.tokenId.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredTokens(filtered);
  };

  const createAlphaToken = async () => {
    try {
      setCreating(true);

      const tokenData = {
        ...createForm,
        alphaPrice: parseFloat(createForm.alphaPrice),
        totalSupply: parseFloat(createForm.totalSupply),
        alphaAllocation: parseFloat(createForm.alphaAllocation),
        minInvestment: parseFloat(createForm.minInvestment),
        maxInvestment: parseFloat(createForm.maxInvestment),
        alphaStartDate: new Date(createForm.alphaStartDate),
        alphaEndDate: new Date(createForm.alphaEndDate),
        publicLaunchDate: createForm.publicLaunchDate
          ? new Date(createForm.publicLaunchDate)
          : null,
        vestingSchedule: createForm.vestingSchedule.map((vest) => ({
          ...vest,
          releaseDate: new Date(vest.releaseDate),
        })),
      };

      const response = await fetch('/api/alpha/tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(tokenData),
      });

      if (response.ok) {
        const newToken = await response.json();
        setAlphaTokens((prev) => [newToken.data, ...prev]);
        setIsCreateDialogOpen(false);
        resetCreateForm();
        loadStats();
      } else {
        const error = await response.json();
        alert(`Failed to create alpha token: ${error.message}`);
      }
    } catch (error) {
      console.error('Failed to create alpha token:', error);
      alert('Failed to create alpha token');
    } finally {
      setCreating(false);
    }
  };

  const approveToken = async (tokenId: string) => {
    try {
      const response = await fetch(`/api/alpha/tokens/${tokenId}/approve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const updatedToken = await response.json();
        setAlphaTokens((prev) =>
          prev.map((token) =>
            token.tokenId === tokenId ? updatedToken.data : token
          )
        );
        loadStats();
      } else {
        const error = await response.json();
        alert(`Failed to approve token: ${error.message}`);
      }
    } catch (error) {
      console.error('Failed to approve token:', error);
      alert('Failed to approve token');
    }
  };

  const activateToken = async (tokenId: string) => {
    try {
      const response = await fetch(`/api/alpha/tokens/${tokenId}/activate`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const updatedToken = await response.json();
        setAlphaTokens((prev) =>
          prev.map((token) =>
            token.tokenId === tokenId ? updatedToken.data : token
          )
        );
        loadStats();
      } else {
        const error = await response.json();
        alert(`Failed to activate token: ${error.message}`);
      }
    } catch (error) {
      console.error('Failed to activate token:', error);
      alert('Failed to activate token');
    }
  };

  const resetCreateForm = () => {
    setCreateForm({
      name: '',
      symbol: '',
      description: '',
      blockchain: 'ethereum',
      decimals: 18,
      alphaPrice: '',
      totalSupply: '',
      alphaAllocation: '',
      minInvestment: '100',
      maxInvestment: '10000',
      alphaStartDate: '',
      alphaEndDate: '',
      publicLaunchDate: '',
      isKYCRequired: true,
      isWhitelisted: false,
      projectTeam: [{ name: '', role: '', linkedin: '', experience: '' }],
      whitepaper: { url: '', hash: '' },
      website: '',
      socialLinks: { twitter: '', telegram: '', discord: '', medium: '' },
      vestingSchedule: [
        { releaseDate: '', percentage: 25, description: 'Initial release' },
        { releaseDate: '', percentage: 25, description: '3 months' },
        { releaseDate: '', percentage: 25, description: '6 months' },
        { releaseDate: '', percentage: 25, description: '12 months' },
      ],
    });
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: 'secondary',
      approved: 'default',
      active: 'default',
      completed: 'default',
      rejected: 'destructive',
    } as const;

    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      active: 'bg-green-100 text-green-800',
      completed: 'bg-gray-100 text-gray-800',
      rejected: 'bg-red-100 text-red-800',
    };

    return (
      <Badge
        variant={variants[status as keyof typeof variants]}
        className={colors[status as keyof typeof colors]}
      >
        {status.toUpperCase()}
      </Badge>
    );
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Alpha Market Administration</h1>
          <p className="text-muted-foreground">
            Manage pre-launch token access and early investor mechanisms
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Alpha Token
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Alpha Token</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              <Tabs defaultValue="basic" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="basic">Basic Info</TabsTrigger>
                  <TabsTrigger value="economics">Economics</TabsTrigger>
                  <TabsTrigger value="team">Team & Links</TabsTrigger>
                  <TabsTrigger value="vesting">Vesting</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="name">Token Name</Label>
                      <Input
                        id="name"
                        value={createForm.name}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            name: e.target.value,
                          }))
                        }
                        placeholder="Alpha Protocol"
                      />
                    </div>
                    <div>
                      <Label htmlFor="symbol">Symbol</Label>
                      <Input
                        id="symbol"
                        value={createForm.symbol}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            symbol: e.target.value.toUpperCase(),
                          }))
                        }
                        placeholder="ALPHA"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={createForm.description}
                      onChange={(e) =>
                        setCreateForm((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Describe the project and its value proposition..."
                      rows={4}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="blockchain">Blockchain</Label>
                      <Select
                        value={createForm.blockchain}
                        onValueChange={(value) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            blockchain: value,
                          }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ethereum">Ethereum</SelectItem>
                          <SelectItem value="bsc">BSC</SelectItem>
                          <SelectItem value="polygon">Polygon</SelectItem>
                          <SelectItem value="arbitrum">Arbitrum</SelectItem>
                          <SelectItem value="optimism">Optimism</SelectItem>
                          <SelectItem value="avalanche">Avalanche</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="decimals">Decimals</Label>
                      <Input
                        id="decimals"
                        type="number"
                        value={createForm.decimals}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            decimals: parseInt(e.target.value),
                          }))
                        }
                      />
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="kyc"
                        checked={createForm.isKYCRequired}
                        onCheckedChange={(checked) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            isKYCRequired: checked,
                          }))
                        }
                      />
                      <Label htmlFor="kyc">Require KYC</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="whitelist"
                        checked={createForm.isWhitelisted}
                        onCheckedChange={(checked) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            isWhitelisted: checked,
                          }))
                        }
                      />
                      <Label htmlFor="whitelist">Whitelist Only</Label>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="economics" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="alphaPrice">Alpha Price (USD)</Label>
                      <Input
                        id="alphaPrice"
                        type="number"
                        step="0.01"
                        value={createForm.alphaPrice}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            alphaPrice: e.target.value,
                          }))
                        }
                        placeholder="0.10"
                      />
                    </div>
                    <div>
                      <Label htmlFor="totalSupply">Total Supply</Label>
                      <Input
                        id="totalSupply"
                        type="number"
                        value={createForm.totalSupply}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            totalSupply: e.target.value,
                          }))
                        }
                        placeholder="1000000000"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="alphaAllocation">Alpha Allocation</Label>
                      <Input
                        id="alphaAllocation"
                        type="number"
                        value={createForm.alphaAllocation}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            alphaAllocation: e.target.value,
                          }))
                        }
                        placeholder="50000000"
                      />
                    </div>
                    <div>
                      <Label htmlFor="minInvestment">
                        Min Investment (USD)
                      </Label>
                      <Input
                        id="minInvestment"
                        type="number"
                        value={createForm.minInvestment}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            minInvestment: e.target.value,
                          }))
                        }
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="alphaStartDate">Alpha Start Date</Label>
                      <Input
                        id="alphaStartDate"
                        type="datetime-local"
                        value={createForm.alphaStartDate}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            alphaStartDate: e.target.value,
                          }))
                        }
                      />
                    </div>
                    <div>
                      <Label htmlFor="alphaEndDate">Alpha End Date</Label>
                      <Input
                        id="alphaEndDate"
                        type="datetime-local"
                        value={createForm.alphaEndDate}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            alphaEndDate: e.target.value,
                          }))
                        }
                      />
                    </div>
                    <div>
                      <Label htmlFor="publicLaunchDate">
                        Public Launch Date
                      </Label>
                      <Input
                        id="publicLaunchDate"
                        type="datetime-local"
                        value={createForm.publicLaunchDate}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            publicLaunchDate: e.target.value,
                          }))
                        }
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="team" className="space-y-4">
                  <div>
                    <Label>Project Team</Label>
                    {createForm.projectTeam.map((member, index) => (
                      <div
                        key={index}
                        className="grid grid-cols-2 gap-4 p-4 border rounded-lg mt-2"
                      >
                        <div>
                          <Label>Name</Label>
                          <Input
                            value={member.name}
                            onChange={(e) => {
                              const newTeam = [...createForm.projectTeam];
                              newTeam[index].name = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                projectTeam: newTeam,
                              }));
                            }}
                            placeholder="John Doe"
                          />
                        </div>
                        <div>
                          <Label>Role</Label>
                          <Input
                            value={member.role}
                            onChange={(e) => {
                              const newTeam = [...createForm.projectTeam];
                              newTeam[index].role = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                projectTeam: newTeam,
                              }));
                            }}
                            placeholder="CEO"
                          />
                        </div>
                        <div>
                          <Label>LinkedIn</Label>
                          <Input
                            value={member.linkedin}
                            onChange={(e) => {
                              const newTeam = [...createForm.projectTeam];
                              newTeam[index].linkedin = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                projectTeam: newTeam,
                              }));
                            }}
                            placeholder="https://linkedin.com/in/johndoe"
                          />
                        </div>
                        <div>
                          <Label>Experience</Label>
                          <Textarea
                            value={member.experience}
                            onChange={(e) => {
                              const newTeam = [...createForm.projectTeam];
                              newTeam[index].experience = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                projectTeam: newTeam,
                              }));
                            }}
                            placeholder="10+ years in blockchain..."
                            rows={2}
                          />
                        </div>
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() =>
                        setCreateForm((prev) => ({
                          ...prev,
                          projectTeam: [
                            ...prev.projectTeam,
                            {
                              name: '',
                              role: '',
                              linkedin: '',
                              experience: '',
                            },
                          ],
                        }))
                      }
                      className="mt-2"
                    >
                      Add Team Member
                    </Button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        value={createForm.website}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            website: e.target.value,
                          }))
                        }
                        placeholder="https://alphaprotocol.com"
                      />
                    </div>
                    <div>
                      <Label htmlFor="whitepaper">Whitepaper URL</Label>
                      <Input
                        id="whitepaper"
                        value={createForm.whitepaper.url}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            whitepaper: {
                              ...prev.whitepaper,
                              url: e.target.value,
                            },
                          }))
                        }
                        placeholder="https://docs.alphaprotocol.com/whitepaper.pdf"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="twitter">Twitter</Label>
                      <Input
                        id="twitter"
                        value={createForm.socialLinks.twitter}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            socialLinks: {
                              ...prev.socialLinks,
                              twitter: e.target.value,
                            },
                          }))
                        }
                        placeholder="https://twitter.com/alphaprotocol"
                      />
                    </div>
                    <div>
                      <Label htmlFor="telegram">Telegram</Label>
                      <Input
                        id="telegram"
                        value={createForm.socialLinks.telegram}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            socialLinks: {
                              ...prev.socialLinks,
                              telegram: e.target.value,
                            },
                          }))
                        }
                        placeholder="https://t.me/alphaprotocol"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="vesting" className="space-y-4">
                  <div>
                    <Label>Vesting Schedule</Label>
                    {createForm.vestingSchedule.map((vest, index) => (
                      <div
                        key={index}
                        className="grid grid-cols-3 gap-4 p-4 border rounded-lg mt-2"
                      >
                        <div>
                          <Label>Release Date</Label>
                          <Input
                            type="datetime-local"
                            value={vest.releaseDate}
                            onChange={(e) => {
                              const newSchedule = [
                                ...createForm.vestingSchedule,
                              ];
                              newSchedule[index].releaseDate = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                vestingSchedule: newSchedule,
                              }));
                            }}
                          />
                        </div>
                        <div>
                          <Label>Percentage (%)</Label>
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            value={vest.percentage}
                            onChange={(e) => {
                              const newSchedule = [
                                ...createForm.vestingSchedule,
                              ];
                              newSchedule[index].percentage = parseInt(
                                e.target.value
                              );
                              setCreateForm((prev) => ({
                                ...prev,
                                vestingSchedule: newSchedule,
                              }));
                            }}
                          />
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Input
                            value={vest.description}
                            onChange={(e) => {
                              const newSchedule = [
                                ...createForm.vestingSchedule,
                              ];
                              newSchedule[index].description = e.target.value;
                              setCreateForm((prev) => ({
                                ...prev,
                                vestingSchedule: newSchedule,
                              }));
                            }}
                            placeholder="Initial release"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>

              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button onClick={createAlphaToken} disabled={creating}>
                  {creating ? 'Creating...' : 'Create Alpha Token'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTokens}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tokens</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeTokens}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Raised</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${stats.totalRaised.toLocaleString()}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Investors
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalInvestors}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Avg Risk Score
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.averageRiskScore.toFixed(1)}
            </div>
          </CardContent>
        </Card>
      </div>

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
              <Label htmlFor="status">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
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
          </div>
        </CardContent>
      </Card>

      {/* Alpha Tokens Table */}
      <Card>
        <CardHeader>
          <CardTitle>Alpha Tokens</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Blockchain</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Investors</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTokens.map((token) => (
                <TableRow key={token.tokenId}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{token.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {token.symbol}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(token.status)}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {token.blockchain.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>${token.alphaPrice}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${token.progressPercentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm">
                        {token.progressPercentage.toFixed(1)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>{getRiskBadge(token.riskScore)}</TableCell>
                  <TableCell>{token.totalInvestors}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      {token.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => approveToken(token.tokenId)}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                      {token.status === 'approved' && (
                        <Button
                          size="sm"
                          onClick={() => activateToken(token.tokenId)}
                        >
                          <Activity className="h-4 w-4" />
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default AlphaMarketAdminPage;
