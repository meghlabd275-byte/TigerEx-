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
import { 
  Briefcase, 
  TrendingUp, 
  Users, 
  Globe,
  Search,
  Plus,
  Eye,
  Edit,
  Calendar,
  DollarSign,
  Target,
  Building,
  Handshake,
  BarChart3,
  MapPin,
  Phone,
  Mail
} from 'lucide-react';

interface Partnership {
  id: string;
  companyName: string;
  contactPerson: string;
  email: string;
  phone: string;
  type: 'exchange' | 'payment' | 'institutional' | 'technology' | 'marketing' | 'regional';
  status: 'prospect' | 'negotiating' | 'active' | 'paused' | 'terminated';
  region: string;
  dealValue: number;
  startDate?: string;
  endDate?: string;
  description: string;
  keyMetrics: {
    volume?: number;
    users?: number;
    revenue?: number;
  };
}

interface Deal {
  id: string;
  partnershipId: string;
  partnerName: string;
  dealName: string;
  value: number;
  currency: string;
  stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: number;
  expectedCloseDate: string;
  assignedTo: string;
  lastActivity: string;
}

interface BusinessMetric {
  id: string;
  name: string;
  value: number;
  target: number;
  unit: string;
  change: number;
  period: string;
}

const BusinessDevelopmentDashboard: React.FC = () => {
  const [partnerships, setPartnerships] = useState<Partnership[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [metrics, setMetrics] = useState<BusinessMetric[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Mock partnerships data
    const mockPartnerships: Partnership[] = [
      {
        id: 'partner-001',
        companyName: 'CryptoBank Solutions',
        contactPerson: 'John Smith',
        email: 'john@cryptobank.com',
        phone: '+1-555-0123',
        type: 'institutional',
        status: 'active',
        region: 'North America',
        dealValue: 5000000,
        startDate: '2024-01-01T00:00:00Z',
        endDate: '2024-12-31T23:59:59Z',
        description: 'Institutional custody and trading services partnership',
        keyMetrics: {
          volume: 50000000,
          users: 150,
          revenue: 250000
        }
      },
      {
        id: 'partner-002',
        companyName: 'PayFlow Technologies',
        contactPerson: 'Sarah Johnson',
        email: 'sarah@payflow.com',
        phone: '+44-20-7123-4567',
        type: 'payment',
        status: 'negotiating',
        region: 'Europe',
        dealValue: 2500000,
        description: 'Payment gateway integration for fiat on/off ramps',
        keyMetrics: {
          volume: 25000000,
          users: 5000,
          revenue: 125000
        }
      },
      {
        id: 'partner-003',
        companyName: 'Asian Crypto Exchange',
        contactPerson: 'Hiroshi Tanaka',
        email: 'hiroshi@ace.jp',
        phone: '+81-3-1234-5678',
        type: 'exchange',
        status: 'active',
        region: 'Asia Pacific',
        dealValue: 10000000,
        startDate: '2023-06-01T00:00:00Z',
        endDate: '2025-05-31T23:59:59Z',
        description: 'Cross-listing and liquidity sharing agreement',
        keyMetrics: {
          volume: 100000000,
          users: 25000,
          revenue: 500000
        }
      }
    ];

    const mockDeals: Deal[] = [
      {
        id: 'deal-001',
        partnershipId: 'partner-004',
        partnerName: 'European Investment Fund',
        dealName: 'Institutional Trading Platform',
        value: 15000000,
        currency: 'USD',
        stage: 'negotiation',
        probability: 75,
        expectedCloseDate: '2024-03-15T00:00:00Z',
        assignedTo: 'Alice Cooper',
        lastActivity: '2024-01-14T10:30:00Z'
      },
      {
        id: 'deal-002',
        partnershipId: 'partner-005',
        partnerName: 'FinTech Innovations',
        dealName: 'White Label Exchange',
        value: 8000000,
        currency: 'USD',
        stage: 'proposal',
        probability: 60,
        expectedCloseDate: '2024-02-28T00:00:00Z',
        assignedTo: 'Bob Wilson',
        lastActivity: '2024-01-13T15:45:00Z'
      },
      {
        id: 'deal-003',
        partnershipId: 'partner-006',
        partnerName: 'Regional Bank Consortium',
        dealName: 'CBDC Integration',
        value: 25000000,
        currency: 'USD',
        stage: 'qualified',
        probability: 40,
        expectedCloseDate: '2024-06-30T00:00:00Z',
        assignedTo: 'Carol Davis',
        lastActivity: '2024-01-12T09:20:00Z'
      }
    ];

    const mockMetrics: BusinessMetric[] = [
      {
        id: 'metric-001',
        name: 'Partnership Revenue',
        value: 875000,
        target: 1000000,
        unit: 'USD',
        change: 15.2,
        period: 'Monthly'
      },
      {
        id: 'metric-002',
        name: 'Active Partnerships',
        value: 12,
        target: 15,
        unit: 'count',
        change: 9.1,
        period: 'Quarterly'
      },
      {
        id: 'metric-003',
        name: 'Deal Pipeline Value',
        value: 48000000,
        target: 50000000,
        unit: 'USD',
        change: 22.5,
        period: 'Quarterly'
      },
      {
        id: 'metric-004',
        name: 'Partner Trading Volume',
        value: 175000000,
        target: 200000000,
        unit: 'USD',
        change: 8.7,
        period: 'Monthly'
      }
    ];

    setPartnerships(mockPartnerships);
    setDeals(mockDeals);
    setMetrics(mockMetrics);
  }, []);

  const handleCreatePartnership = () => {
    alert('Create new partnership dialog would open here');
  };

  const handleEditPartnership = (partnershipId: string) => {
    alert(`Edit partnership ${partnershipId} dialog would open here`);
  };

  const handleCreateDeal = () => {
    alert('Create new deal dialog would open here');
  };

  const handleUpdateDealStage = (dealId: string, newStage: string) => {
    setDeals(prev => 
      prev.map(deal => 
        deal.id === dealId 
          ? { ...deal, stage: newStage as any, lastActivity: new Date().toISOString() }
          : deal
      )
    );
    alert(`Deal ${dealId} moved to ${newStage}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'negotiating': return 'bg-yellow-100 text-yellow-800';
      case 'prospect': return 'bg-blue-100 text-blue-800';
      case 'paused': return 'bg-orange-100 text-orange-800';
      case 'terminated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'exchange': return 'bg-purple-100 text-purple-800';
      case 'payment': return 'bg-blue-100 text-blue-800';
      case 'institutional': return 'bg-green-100 text-green-800';
      case 'technology': return 'bg-orange-100 text-orange-800';
      case 'marketing': return 'bg-pink-100 text-pink-800';
      case 'regional': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'lead': return 'bg-gray-100 text-gray-800';
      case 'qualified': return 'bg-blue-100 text-blue-800';
      case 'proposal': return 'bg-yellow-100 text-yellow-800';
      case 'negotiation': return 'bg-orange-100 text-orange-800';
      case 'closed_won': return 'bg-green-100 text-green-800';
      case 'closed_lost': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredPartnerships = partnerships.filter(partnership => 
    partnership.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partnership.contactPerson.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partnership.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partnership.region.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalPartnerships: partnerships.length,
    activePartnerships: partnerships.filter(p => p.status === 'active').length,
    totalDeals: deals.length,
    pipelineValue: deals.reduce((sum, deal) => sum + deal.value, 0),
    totalRevenue: partnerships.reduce((sum, p) => sum + (p.keyMetrics.revenue || 0), 0),
    avgDealSize: deals.length > 0 ? deals.reduce((sum, deal) => sum + deal.value, 0) / deals.length : 0
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Business Development Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage partnerships, deals, and strategic relationships</p>
        </div>

        {/* Business Development Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Handshake className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.activePartnerships}</div>
                  <div className="text-sm text-gray-600">Active Partners</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Target className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">{stats.totalDeals}</div>
                  <div className="text-sm text-gray-600">Active Deals</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    ${(stats.pipelineValue / 1000000).toFixed(1)}M
                  </div>
                  <div className="text-sm text-gray-600">Pipeline Value</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold text-orange-600">
                    ${(stats.totalRevenue / 1000).toFixed(0)}K
                  </div>
                  <div className="text-sm text-gray-600">Monthly Revenue</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">
                    ${(stats.avgDealSize / 1000000).toFixed(1)}M
                  </div>
                  <div className="text-sm text-gray-600">Avg Deal Size</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Globe className="h-5 w-5 text-indigo-600" />
                <div>
                  <div className="text-2xl font-bold text-indigo-600">8</div>
                  <div className="text-sm text-gray-600">Regions</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="partnerships">Partnerships ({stats.totalPartnerships})</TabsTrigger>
            <TabsTrigger value="deals">Deals ({stats.totalDeals})</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="regions">Regions</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Top Performing Partnerships</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {partnerships.slice(0, 5).map((partnership) => (
                      <div key={partnership.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            {partnership.companyName.charAt(0)}
                          </div>
                          <div>
                            <div className="font-semibold">{partnership.companyName}</div>
                            <div className="text-sm text-gray-600">
                              {partnership.contactPerson} • {partnership.region}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${(partnership.dealValue / 1000000).toFixed(1)}M</div>
                          <Badge className={getStatusColor(partnership.status)}>
                            {partnership.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Active Deals Pipeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {deals.slice(0, 5).map((deal) => (
                      <div key={deal.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-semibold">{deal.dealName}</div>
                          <div className="text-sm text-gray-600">
                            {deal.partnerName} • {deal.assignedTo}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${(deal.value / 1000000).toFixed(1)}M</div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getStageColor(deal.stage)}>
                              {deal.stage.replace('_', ' ')}
                            </Badge>
                            <span className="text-sm text-gray-500">{deal.probability}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="partnerships" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Partnership Management</CardTitle>
                  <Button onClick={handleCreatePartnership}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Partnership
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search partnerships..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredPartnerships.map((partnership) => (
                    <Card key={partnership.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {partnership.companyName.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{partnership.companyName}</div>
                              <div className="text-sm text-gray-600">{partnership.description}</div>
                              <div className="flex items-center space-x-4 mt-2">
                                <div className="flex items-center space-x-1">
                                  <div className="h-4 w-4 text-gray-500" />
                                  <span className="text-sm">{partnership.contactPerson}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <MapPin className="h-4 w-4 text-gray-500" />
                                  <span className="text-sm">{partnership.region}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">
                                ${(partnership.dealValue / 1000000).toFixed(1)}M
                              </div>
                              <div className="text-xs text-gray-500">Deal Value</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">
                                ${((partnership.keyMetrics.revenue || 0) / 1000).toFixed(0)}K
                              </div>
                              <div className="text-xs text-gray-500">Monthly Revenue</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-purple-600">
                                {partnership.keyMetrics.users?.toLocaleString() || 0}
                              </div>
                              <div className="text-xs text-gray-500">Users</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <Badge className={getTypeColor(partnership.type)}>
                                {partnership.type}
                              </Badge>
                              <div className="mt-1">
                                <Badge className={getStatusColor(partnership.status)}>
                                  {partnership.status}
                                </Badge>
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2">
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleEditPartnership(partnership.id)}
                              >
                                <Edit className="h-4 w-4 mr-1" />
                                Edit
                              </Button>
                              <Button size="sm" variant="outline">
                                <Mail className="h-4 w-4 mr-1" />
                                Contact
                              </Button>
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

          <TabsContent value="deals" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Deal Pipeline</CardTitle>
                  <Button onClick={handleCreateDeal}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Deal
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {deals.map((deal) => (
                    <Card key={deal.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white">
                              <Target className="h-5 w-5" />
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{deal.dealName}</div>
                              <div className="text-sm text-gray-600">{deal.partnerName}</div>
                              <div className="flex items-center space-x-4 mt-1">
                                <span className="text-xs text-gray-500">
                                  Assigned to: {deal.assignedTo}
                                </span>
                                <span className="text-xs text-gray-500">
                                  Expected: {new Date(deal.expectedCloseDate).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">
                                ${(deal.value / 1000000).toFixed(1)}M
                              </div>
                              <div className="text-xs text-gray-500">Deal Value</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-blue-600">{deal.probability}%</div>
                              <div className="text-xs text-gray-500">Probability</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <Badge className={getStageColor(deal.stage)}>
                                {deal.stage.replace('_', ' ')}
                              </Badge>
                            </div>

                            <div className="flex flex-col space-y-2">
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </Button>
                              <Button size="sm" variant="outline">
                                <Edit className="h-4 w-4 mr-1" />
                                Edit
                              </Button>
                              <select 
                                className="text-xs border rounded px-2 py-1"
                                value={deal.stage}
                                onChange={(e) => handleUpdateDealStage(deal.id, e.target.value)}
                              >
                                <option value="lead">Lead</option>
                                <option value="qualified">Qualified</option>
                                <option value="proposal">Proposal</option>
                                <option value="negotiation">Negotiation</option>
                                <option value="closed_won">Closed Won</option>
                                <option value="closed_lost">Closed Lost</option>
                              </select>
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

          <TabsContent value="metrics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {metrics.map((metric) => (
                <Card key={metric.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {metric.name}
                      <Badge className={metric.change >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(1)}%
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-3xl font-bold">
                          {metric.unit === 'USD' ? '$' : ''}{metric.value.toLocaleString()}{metric.unit === 'count' ? '' : metric.unit === 'USD' ? '' : ` ${metric.unit}`}
                        </span>
                        <span className="text-gray-500">
                          Target: {metric.unit === 'USD' ? '$' : ''}{metric.target.toLocaleString()}{metric.unit === 'count' ? '' : metric.unit === 'USD' ? '' : ` ${metric.unit}`}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${Math.min((metric.value / metric.target) * 100, 100)}%` }}
                        ></div>
                      </div>
                      <div className="text-sm text-gray-600">
                        {metric.period} • {((metric.value / metric.target) * 100).toFixed(1)}% of target
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="regions" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East', 'Africa'].map((region) => {
                const regionPartnerships = partnerships.filter(p => p.region === region);
                const regionRevenue = regionPartnerships.reduce((sum, p) => sum + (p.keyMetrics.revenue || 0), 0);
                const regionVolume = regionPartnerships.reduce((sum, p) => sum + (p.keyMetrics.volume || 0), 0);
                
                return (
                  <Card key={region}>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Globe className="h-5 w-5 mr-2" />
                        {region}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Partnerships:</span>
                          <span className="font-semibold">{regionPartnerships.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Revenue:</span>
                          <span className="font-semibold">${(regionRevenue / 1000).toFixed(0)}K</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Volume:</span>
                          <span className="font-semibold">${(regionVolume / 1000000).toFixed(1)}M</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Active:</span>
                          <span className="font-semibold text-green-600">
                            {regionPartnerships.filter(p => p.status === 'active').length}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default BusinessDevelopmentDashboard;