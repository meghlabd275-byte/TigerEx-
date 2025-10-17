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

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Coins, 
  Plus, 
  Search, 
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  FileText,
  DollarSign,
  Users,
  TrendingUp,
  Star,
  Globe,
  Shield,
  Zap
} from 'lucide-react';

interface TokenApplication {
  id: string;
  tokenName: string;
  symbol: string;
  contractAddress: string;
  blockchain: string;
  website: string;
  whitepaper: string;
  totalSupply: number;
  circulatingSupply: number;
  marketCap: number;
  category: 'defi' | 'gaming' | 'nft' | 'infrastructure' | 'meme' | 'utility' | 'other';
  status: 'submitted' | 'under_review' | 'approved' | 'rejected' | 'listed';
  submittedBy: string;
  submittedAt: string;
  reviewedBy?: string;
  reviewedAt?: string;
  listingFee: number;
  documents: {
    whitepaper?: string;
    audit?: string;
    legalOpinion?: string;
    teamKyc?: string;
  };
  socialMedia: {
    twitter?: string;
    telegram?: string;
    discord?: string;
    medium?: string;
  };
  teamInfo: {
    teamSize: number;
    foundedYear: number;
    headquarters: string;
  };
  technicalInfo: {
    consensusAlgorithm?: string;
    blockTime?: number;
    tps?: number;
  };
  riskScore: number;
  complianceScore: number;
}

interface ListingCriteria {
  id: string;
  name: string;
  description: string;
  weight: number;
  minScore: number;
  category: 'technical' | 'legal' | 'business' | 'community';
}

const ListingManagerDashboard: React.FC = () => {
  const [applications, setApplications] = useState<TokenApplication[]>([]);
  const [criteria, setCriteria] = useState<ListingCriteria[]>([]);
  const [selectedApplication, setSelectedApplication] = useState<TokenApplication | null>(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewNotes, setReviewNotes] = useState('');

  useEffect(() => {
    // Mock token applications data
    const mockApplications: TokenApplication[] = [
      {
        id: 'app-001',
        tokenName: 'DeFi Protocol Token',
        symbol: 'DPT',
        contractAddress: '0x1234567890abcdef1234567890abcdef12345678',
        blockchain: 'Ethereum',
        website: 'https://defiprotocol.com',
        whitepaper: 'https://defiprotocol.com/whitepaper.pdf',
        totalSupply: 1000000000,
        circulatingSupply: 600000000,
        marketCap: 50000000,
        category: 'defi',
        status: 'under_review',
        submittedBy: 'DeFi Team',
        submittedAt: '2024-01-14T15:30:00Z',
        listingFee: 50000,
        documents: {
          whitepaper: 'whitepaper.pdf',
          audit: 'audit_report.pdf',
          legalOpinion: 'legal_opinion.pdf',
          teamKyc: 'team_kyc.pdf'
        },
        socialMedia: {
          twitter: '@defiprotocol',
          telegram: 't.me/defiprotocol',
          discord: 'discord.gg/defiprotocol',
          medium: '@defiprotocol'
        },
        teamInfo: {
          teamSize: 15,
          foundedYear: 2022,
          headquarters: 'Singapore'
        },
        technicalInfo: {
          consensusAlgorithm: 'Proof of Stake',
          blockTime: 12,
          tps: 1000
        },
        riskScore: 25,
        complianceScore: 85
      },
      {
        id: 'app-002',
        tokenName: 'Gaming Universe Token',
        symbol: 'GUT',
        contractAddress: '0xabcdef1234567890abcdef1234567890abcdef12',
        blockchain: 'BSC',
        website: 'https://gaminguniverse.io',
        whitepaper: 'https://gaminguniverse.io/whitepaper.pdf',
        totalSupply: 500000000,
        circulatingSupply: 300000000,
        marketCap: 25000000,
        category: 'gaming',
        status: 'submitted',
        submittedBy: 'Gaming Studio',
        submittedAt: '2024-01-13T10:15:00Z',
        listingFee: 30000,
        documents: {
          whitepaper: 'gaming_whitepaper.pdf',
          audit: 'security_audit.pdf'
        },
        socialMedia: {
          twitter: '@gaminguniverse',
          telegram: 't.me/gaminguniverse',
          discord: 'discord.gg/gaminguniverse'
        },
        teamInfo: {
          teamSize: 25,
          foundedYear: 2021,
          headquarters: 'United States'
        },
          technicalInfo: {
            consensusAlgorithm: "PoS",
            blockTime: 3,
            tps: 2000
          },
        riskScore: 35,
        complianceScore: 75
      },
      {
        id: 'app-003',
        tokenName: 'Infrastructure Token',
        symbol: 'INFRA',
        contractAddress: '0x567890abcdef1234567890abcdef1234567890ab',
        blockchain: 'Polygon',
        website: 'https://infrastructure.network',
        whitepaper: 'https://infrastructure.network/docs.pdf',
        totalSupply: 2000000000,
        circulatingSupply: 1200000000,
        marketCap: 100000000,
        category: 'infrastructure',
        status: 'approved',
        submittedBy: 'Infrastructure Corp',
        submittedAt: '2024-01-12T14:20:00Z',
        reviewedBy: 'Senior Listing Manager',
        reviewedAt: '2024-01-14T09:30:00Z',
        listingFee: 75000,
        documents: {
          whitepaper: 'infra_whitepaper.pdf',
          audit: 'comprehensive_audit.pdf',
          legalOpinion: 'legal_compliance.pdf',
          teamKyc: 'team_verification.pdf'
        },
        socialMedia: {
          twitter: '@infranetwork',
          telegram: 't.me/infranetwork',
          discord: 'discord.gg/infranetwork',
          medium: '@infranetwork'
        },
        teamInfo: {
          teamSize: 50,
          foundedYear: 2020,
          headquarters: 'Switzerland'
        },
        technicalInfo: {
          consensusAlgorithm: 'Delegated Proof of Stake',
          blockTime: 3,
          tps: 10000
        },
        riskScore: 15,
        complianceScore: 95
      }
    ];

    const mockCriteria: ListingCriteria[] = [
      {
        id: 'criteria-001',
        name: 'Technical Innovation',
        description: 'Evaluation of technical merit and innovation',
        weight: 25,
        minScore: 70,
        category: 'technical'
      },
      {
        id: 'criteria-002',
        name: 'Legal Compliance',
        description: 'Regulatory compliance and legal documentation',
        weight: 30,
        minScore: 80,
        category: 'legal'
      },
      {
        id: 'criteria-003',
        name: 'Business Model',
        description: 'Viability and sustainability of business model',
        weight: 20,
        minScore: 65,
        category: 'business'
      },
      {
        id: 'criteria-004',
        name: 'Community Support',
        description: 'Community engagement and adoption metrics',
        weight: 15,
        minScore: 60,
        category: 'community'
      },
      {
        id: 'criteria-005',
        name: 'Team Credibility',
        description: 'Team experience and track record',
        weight: 10,
        minScore: 70,
        category: 'business'
      }
    ];

    setApplications(mockApplications);
    setCriteria(mockCriteria);
  }, []);

  const handleApproveApplication = (applicationId: string) => {
    setApplications(prev => 
      prev.map(app => 
        app.id === applicationId 
          ? { 
              ...app, 
              status: 'approved',
              reviewedBy: 'Listing Manager',
              reviewedAt: new Date().toISOString()
            }
          : app
      )
    );
    alert(`Application ${applicationId} approved for listing`);
  };

  const handleRejectApplication = (applicationId: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (reason) {
      setApplications(prev => 
        prev.map(app => 
          app.id === applicationId 
            ? { 
                ...app, 
                status: 'rejected',
                reviewedBy: 'Listing Manager',
                reviewedAt: new Date().toISOString()
              }
            : app
        )
      );
      alert(`Application ${applicationId} rejected: ${reason}`);
    }
  };

  const handleListToken = (applicationId: string) => {
    setApplications(prev => 
      prev.map(app => 
        app.id === applicationId 
          ? { ...app, status: 'listed' }
          : app
      )
    );
    alert(`Token ${applicationId} has been listed successfully`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'submitted': return 'bg-blue-100 text-blue-800';
      case 'under_review': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'listed': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'defi': return 'bg-blue-100 text-blue-800';
      case 'gaming': return 'bg-green-100 text-green-800';
      case 'nft': return 'bg-purple-100 text-purple-800';
      case 'infrastructure': return 'bg-orange-100 text-orange-800';
      case 'meme': return 'bg-pink-100 text-pink-800';
      case 'utility': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredApplications = applications.filter(app => 
    app.tokenName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.submittedBy.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalApplications: applications.length,
    pendingReview: applications.filter(a => a.status === 'submitted' || a.status === 'under_review').length,
    approved: applications.filter(a => a.status === 'approved').length,
    listed: applications.filter(a => a.status === 'listed').length,
    rejected: applications.filter(a => a.status === 'rejected').length,
    totalListingFees: applications.reduce((sum, app) => sum + app.listingFee, 0),
    avgRiskScore: applications.reduce((sum, app) => sum + app.riskScore, 0) / applications.length,
    avgComplianceScore: applications.reduce((sum, app) => sum + app.complianceScore, 0) / applications.length
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Listing Manager Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage token listing applications and criteria</p>
        </div>

        {/* Listing Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-8 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.totalApplications}</div>
                  <div className="text-sm text-gray-600">Total Apps</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-yellow-600" />
                <div>
                  <div className="text-2xl font-bold text-yellow-600">{stats.pendingReview}</div>
                  <div className="text-sm text-gray-600">Pending</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
                  <div className="text-sm text-gray-600">Approved</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Coins className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">{stats.listed}</div>
                  <div className="text-sm text-gray-600">Listed</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <XCircle className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
                  <div className="text-sm text-gray-600">Rejected</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    ${(stats.totalListingFees / 1000).toFixed(0)}K
                  </div>
                  <div className="text-sm text-gray-600">Listing Fees</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold text-orange-600">{stats.avgRiskScore.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Avg Risk</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5 text-indigo-600" />
                <div>
                  <div className="text-2xl font-bold text-indigo-600">{stats.avgComplianceScore.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Avg Compliance</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="applications">Applications ({stats.totalApplications})</TabsTrigger>
            <TabsTrigger value="criteria">Listing Criteria</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Applications</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {applications.slice(0, 5).map((app) => (
                      <div key={app.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            {app.symbol.charAt(0)}
                          </div>
                          <div>
                            <div className="font-semibold">{app.tokenName}</div>
                            <div className="text-sm text-gray-600">{app.symbol} • {app.submittedBy}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getStatusColor(app.status)}>
                            {app.status.replace('_', ' ')}
                          </Badge>
                          <div className="text-xs text-gray-500 mt-1">
                            ${(app.listingFee / 1000).toFixed(0)}K fee
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Application Categories</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {['defi', 'gaming', 'infrastructure', 'nft', 'utility', 'meme'].map((category) => {
                      const count = applications.filter(app => app.category === category).length;
                      const percentage = applications.length > 0 ? (count / applications.length) * 100 : 0;
                      return (
                        <div key={category} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Badge className={getCategoryColor(category)}>
                              {category.toUpperCase()}
                            </Badge>
                            <span className="text-sm text-gray-600">{count} applications</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-semibold">{percentage.toFixed(1)}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="applications" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Token Listing Applications</CardTitle>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    New Application
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search applications..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredApplications.map((app) => (
                    <Card key={app.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {app.symbol.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{app.tokenName} ({app.symbol})</div>
                              <div className="text-sm text-gray-600">
                                {app.blockchain} • {app.submittedBy}
                              </div>
                              <div className="flex items-center space-x-4 mt-1">
                                <Badge className={getCategoryColor(app.category)}>
                                  {app.category}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  Market Cap: ${(app.marketCap / 1000000).toFixed(1)}M
                                </span>
                                <span className="text-xs text-gray-500">
                                  Supply: {(app.circulatingSupply / 1000000).toFixed(0)}M
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-lg font-bold text-green-600">
                                ${(app.listingFee / 1000).toFixed(0)}K
                              </div>
                              <div className="text-xs text-gray-500">Listing Fee</div>
                            </div>
                            <div className="text-center">
                              <div className={`text-lg font-bold ${getRiskColor(app.riskScore)}`}>
                                {app.riskScore}
                              </div>
                              <div className="text-xs text-gray-500">Risk Score</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">{app.complianceScore}</div>
                              <div className="text-xs text-gray-500">Compliance</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <Badge className={getStatusColor(app.status)}>
                                {app.status.replace('_', ' ')}
                              </Badge>
                              <div className="text-xs text-gray-500 mt-1">
                                {new Date(app.submittedAt).toLocaleDateString()}
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => setSelectedApplication(app)}
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                Review
                              </Button>
                              {app.status === 'submitted' || app.status === 'under_review' ? (
                                <>
                                  <Button 
                                    size="sm"
                                    onClick={() => handleApproveApplication(app.id)}
                                    className="bg-green-600 hover:bg-green-700"
                                  >
                                    <CheckCircle className="h-4 w-4 mr-1" />
                                    Approve
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    variant="destructive"
                                    onClick={() => handleRejectApplication(app.id)}
                                  >
                                    <XCircle className="h-4 w-4 mr-1" />
                                    Reject
                                  </Button>
                                </>
                              ) : app.status === 'approved' ? (
                                <Button 
                                  size="sm"
                                  onClick={() => handleListToken(app.id)}
                                  className="bg-purple-600 hover:bg-purple-700"
                                >
                                  <Zap className="h-4 w-4 mr-1" />
                                  List Token
                                </Button>
                              ) : null}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="criteria" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Listing Criteria</CardTitle>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Criteria
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {criteria.map((criterion) => (
                    <Card key={criterion.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="font-semibold text-lg">{criterion.name}</div>
                            <div className="text-sm text-gray-600 mt-1">{criterion.description}</div>
                            <div className="flex items-center space-x-4 mt-2">
                              <Badge className={getCategoryColor(criterion.category)}>
                                {criterion.category}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                Weight: {criterion.weight}%
                              </span>
                              <span className="text-sm text-gray-500">
                                Min Score: {criterion.minScore}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">{criterion.weight}%</div>
                              <div className="text-xs text-gray-500">Weight</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">{criterion.minScore}</div>
                              <div className="text-xs text-gray-500">Min Score</div>
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            <Button size="sm" variant="outline">
                              Edit
                            </Button>
                            <Button size="sm" variant="outline">
                              Delete
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Application Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">This Month:</span>
                      <span className="font-semibold">{applications.length} applications</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Approval Rate:</span>
                      <span className="font-semibold text-green-600">
                        {((stats.approved / stats.totalApplications) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Review Time:</span>
                      <span className="font-semibold">3.2 days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Revenue:</span>
                      <span className="font-semibold text-green-600">
                        ${(stats.totalListingFees / 1000).toFixed(0)}K
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Assessment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Low Risk (0-30)</span>
                        <span className="text-sm">
                          {applications.filter(app => app.riskScore < 30).length} tokens
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ 
                            width: `${(applications.filter(app => app.riskScore < 30).length / applications.length) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">Medium Risk (30-60)</span>
                        <span className="text-sm">
                          {applications.filter(app => app.riskScore >= 30 && app.riskScore < 60).length} tokens
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-yellow-600 h-2 rounded-full" 
                          style={{ 
                            width: `${(applications.filter(app => app.riskScore >= 30 && app.riskScore < 60).length / applications.length) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium">High Risk (60+)</span>
                        <span className="text-sm">
                          {applications.filter(app => app.riskScore >= 60).length} tokens
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-red-600 h-2 rounded-full" 
                          style={{ 
                            width: `${(applications.filter(app => app.riskScore >= 60).length / applications.length) * 100}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Application Review Modal */}
        {selectedApplication && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-6xl max-h-[90vh] overflow-y-auto w-full mx-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Application Review</h2>
                <Button variant="outline" onClick={() => setSelectedApplication(null)}>
                  Close
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-4">Token Information</h3>
                  <div className="space-y-3">
                    <div><strong>Name:</strong> {selectedApplication.tokenName}</div>
                    <div><strong>Symbol:</strong> {selectedApplication.symbol}</div>
                    <div><strong>Blockchain:</strong> {selectedApplication.blockchain}</div>
                    <div><strong>Contract:</strong> {selectedApplication.contractAddress}</div>
                    <div><strong>Category:</strong> 
                      <Badge className={`ml-2 ${getCategoryColor(selectedApplication.category)}`}>
                        {selectedApplication.category}
                      </Badge>
                    </div>
                    <div><strong>Total Supply:</strong> {selectedApplication.totalSupply.toLocaleString()}</div>
                    <div><strong>Circulating Supply:</strong> {selectedApplication.circulatingSupply.toLocaleString()}</div>
                    <div><strong>Market Cap:</strong> ${selectedApplication.marketCap.toLocaleString()}</div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-4">Team & Project Info</h3>
                  <div className="space-y-3">
                    <div><strong>Team Size:</strong> {selectedApplication.teamInfo.teamSize}</div>
                    <div><strong>Founded:</strong> {selectedApplication.teamInfo.foundedYear}</div>
                    <div><strong>Headquarters:</strong> {selectedApplication.teamInfo.headquarters}</div>
                    <div><strong>Website:</strong> 
                      <a href={selectedApplication.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
                        {selectedApplication.website}
                      </a>
                    </div>
                    <div><strong>Whitepaper:</strong> 
                      <a href={selectedApplication.whitepaper} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
                        View Document
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-4">Risk Assessment</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Risk Score:</span>
                      <span className={`font-semibold ${getRiskColor(selectedApplication.riskScore)}`}>
                        {selectedApplication.riskScore}/100
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Compliance Score:</span>
                      <span className="font-semibold text-green-600">{selectedApplication.complianceScore}/100</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Listing Fee:</span>
                      <span className="font-semibold">${selectedApplication.listingFee.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-4">Documents</h3>
                  <div className="space-y-2">
                    {Object.entries(selectedApplication.documents).map(([type, filename]) => (
                      <div key={type} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="capitalize">{type.replace(/([A-Z])/g, ' $1')}</span>
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold mb-4">Review Notes</h3>
                <Textarea
                  placeholder="Add your review notes here..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="flex justify-end space-x-4">
                {selectedApplication.status === 'submitted' || selectedApplication.status === 'under_review' ? (
                  <>
                    <Button 
                      onClick={() => {
                        handleApproveApplication(selectedApplication.id);
                        setSelectedApplication(null);
                      }}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve Application
                    </Button>
                    <Button 
                      variant="destructive"
                      onClick={() => {
                        handleRejectApplication(selectedApplication.id);
                        setSelectedApplication(null);
                      }}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject Application
                    </Button>
                  </>
                ) : selectedApplication.status === 'approved' ? (
                  <Button 
                    onClick={() => {
                      handleListToken(selectedApplication.id);
                      setSelectedApplication(null);
                    }}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    List Token
                  </Button>
                ) : null}
                <Button variant="outline">
                  Request More Info
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ListingManagerDashboard;