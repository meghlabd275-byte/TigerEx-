import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Search,
  UserPlus,
  Gift,
  BarChart3,
  Eye,
  Edit,
  Ban,
  CheckCircle,
  Star,
  Globe
} from 'lucide-react';

interface Affiliate {
  id: string;
  userName: string;
  email: string;
  referralCode: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  totalReferrals: number;
  activeReferrals: number;
  totalCommission: number;
  monthlyCommission: number;
  commissionRate: number;
  status: 'active' | 'suspended' | 'pending';
  joinedAt: string;
  region: string;
}

interface Commission {
  id: string;
  affiliateId: string;
  affiliateName: string;
  referralName: string;
  amount: number;
  currency: string;
  type: 'trading' | 'deposit' | 'referral_bonus';
  status: 'pending' | 'paid' | 'cancelled';
  createdAt: string;
}

interface ReferralProgram {
  id: string;
  name: string;
  description: string;
  commissionRate: number;
  tier: string;
  minReferrals: number;
  bonusAmount: number;
  status: 'active' | 'inactive';
}

const AffiliateManagerDashboard: React.FC = () => {
  const [affiliates, setAffiliates] = useState<Affiliate[]>([]);
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [programs, setPrograms] = useState<ReferralProgram[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Mock data
    const mockAffiliates: Affiliate[] = [
      {
        id: 'aff-001',
        userName: 'CryptoInfluencer',
        email: 'crypto@example.com',
        referralCode: 'CRYPTO2024',
        tier: 'platinum',
        totalReferrals: 1250,
        activeReferrals: 890,
        totalCommission: 125000,
        monthlyCommission: 15000,
        commissionRate: 25,
        status: 'active',
        joinedAt: '2023-01-15T00:00:00Z',
        region: 'North America'
      },
      {
        id: 'aff-002',
        userName: 'BlockchainExpert',
        email: 'blockchain@example.com',
        referralCode: 'BLOCKCHAIN',
        tier: 'gold',
        totalReferrals: 756,
        activeReferrals: 523,
        totalCommission: 67500,
        monthlyCommission: 8500,
        commissionRate: 20,
        status: 'active',
        joinedAt: '2023-03-20T00:00:00Z',
        region: 'Europe'
      },
      {
        id: 'aff-003',
        userName: 'TradingGuru',
        email: 'trading@example.com',
        referralCode: 'TRADING123',
        tier: 'silver',
        totalReferrals: 342,
        activeReferrals: 234,
        totalCommission: 28500,
        monthlyCommission: 4200,
        commissionRate: 15,
        status: 'active',
        joinedAt: '2023-06-10T00:00:00Z',
        region: 'Asia Pacific'
      }
    ];

    const mockCommissions: Commission[] = [
      {
        id: 'comm-001',
        affiliateId: 'aff-001',
        affiliateName: 'CryptoInfluencer',
        referralName: 'John Doe',
        amount: 125.50,
        currency: 'USDT',
        type: 'trading',
        status: 'pending',
        createdAt: '2024-01-15T10:30:00Z'
      },
      {
        id: 'comm-002',
        affiliateId: 'aff-002',
        affiliateName: 'BlockchainExpert',
        referralName: 'Jane Smith',
        amount: 75.25,
        currency: 'USDT',
        type: 'deposit',
        status: 'paid',
        createdAt: '2024-01-14T15:45:00Z'
      }
    ];

    const mockPrograms: ReferralProgram[] = [
      {
        id: 'prog-001',
        name: 'Standard Referral',
        description: 'Basic referral program for all users',
        commissionRate: 10,
        tier: 'bronze',
        minReferrals: 0,
        bonusAmount: 0,
        status: 'active'
      },
      {
        id: 'prog-002',
        name: 'Premium Partner',
        description: 'Enhanced program for high-volume affiliates',
        commissionRate: 25,
        tier: 'platinum',
        minReferrals: 1000,
        bonusAmount: 5000,
        status: 'active'
      }
    ];

    setAffiliates(mockAffiliates);
    setCommissions(mockCommissions);
    setPrograms(mockPrograms);
  }, []);

  const handleApproveAffiliate = (affiliateId: string) => {
    setAffiliates(prev => 
      prev.map(affiliate => 
        affiliate.id === affiliateId 
          ? { ...affiliate, status: 'active' as const }
          : affiliate
      )
    );
    alert(`Affiliate ${affiliateId} approved successfully`);
  };

  const handleSuspendAffiliate = (affiliateId: string) => {
    const reason = prompt('Please provide a reason for suspension:');
    if (reason) {
      setAffiliates(prev => 
        prev.map(affiliate => 
          affiliate.id === affiliateId 
            ? { ...affiliate, status: 'suspended' as const }
            : affiliate
        )
      );
      alert(`Affiliate ${affiliateId} suspended: ${reason}`);
    }
  };

  const handlePayCommission = (commissionId: string) => {
    setCommissions(prev => 
      prev.map(commission => 
        commission.id === commissionId 
          ? { ...commission, status: 'paid' as const }
          : commission
      )
    );
    alert(`Commission ${commissionId} paid successfully`);
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'platinum': return 'bg-purple-100 text-purple-800';
      case 'gold': return 'bg-yellow-100 text-yellow-800';
      case 'silver': return 'bg-gray-100 text-gray-800';
      default: return 'bg-orange-100 text-orange-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'suspended': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'paid': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAffiliates = affiliates.filter(affiliate => 
    affiliate.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    affiliate.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    affiliate.referralCode.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalAffiliates: affiliates.length,
    activeAffiliates: affiliates.filter(a => a.status === 'active').length,
    totalCommissions: commissions.reduce((sum, c) => sum + c.amount, 0),
    pendingCommissions: commissions.filter(c => c.status === 'pending').length,
    totalReferrals: affiliates.reduce((sum, a) => sum + a.totalReferrals, 0),
    monthlyCommissions: affiliates.reduce((sum, a) => sum + a.monthlyCommission, 0)
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Affiliate Manager Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage affiliate programs and commissions</p>
        </div>

        {/* Affiliate Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.activeAffiliates}</div>
                  <div className="text-sm text-gray-600">Active Affiliates</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <UserPlus className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">{stats.totalReferrals}</div>
                  <div className="text-sm text-gray-600">Total Referrals</div>
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
                    ${stats.totalCommissions.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Commissions</div>
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
                    ${stats.monthlyCommissions.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Monthly Commissions</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Gift className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">{stats.pendingCommissions}</div>
                  <div className="text-sm text-gray-600">Pending Payments</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-indigo-600" />
                <div>
                  <div className="text-2xl font-bold text-indigo-600">{programs.length}</div>
                  <div className="text-sm text-gray-600">Active Programs</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="affiliates">Affiliates ({stats.totalAffiliates})</TabsTrigger>
            <TabsTrigger value="commissions">Commissions</TabsTrigger>
            <TabsTrigger value="programs">Programs</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Top Performing Affiliates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {affiliates.slice(0, 5).map((affiliate, index) => (
                      <div key={affiliate.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                            {index + 1}
                          </div>
                          <div>
                            <div className="font-semibold">{affiliate.userName}</div>
                            <div className="text-sm text-gray-600">
                              {affiliate.totalReferrals} referrals
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${affiliate.totalCommission.toLocaleString()}</div>
                          <Badge className={getTierColor(affiliate.tier)}>
                            {affiliate.tier}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Commission Payments</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {commissions.slice(0, 5).map((commission) => (
                      <div key={commission.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-semibold">{commission.affiliateName}</div>
                          <div className="text-sm text-gray-600">
                            {commission.type} • {commission.referralName}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">${commission.amount}</div>
                          <Badge className={getStatusColor(commission.status)}>
                            {commission.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="affiliates" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Affiliate Management</CardTitle>
                  <Button>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Add Affiliate
                  </Button>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search affiliates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredAffiliates.map((affiliate) => (
                    <Card key={affiliate.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {affiliate.userName.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{affiliate.userName}</div>
                              <div className="text-sm text-gray-600">{affiliate.email}</div>
                              <div className="flex items-center space-x-4 mt-1">
                                <span className="text-xs text-gray-500">
                                  Code: {affiliate.referralCode}
                                </span>
                                <span className="text-xs text-gray-500">
                                  <Globe className="h-3 w-3 inline mr-1" />
                                  {affiliate.region}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-6">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">{affiliate.totalReferrals}</div>
                              <div className="text-xs text-gray-500">Total Referrals</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">{affiliate.activeReferrals}</div>
                              <div className="text-xs text-gray-500">Active</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-purple-600">
                                ${affiliate.totalCommission.toLocaleString()}
                              </div>
                              <div className="text-xs text-gray-500">Total Commission</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold text-orange-600">{affiliate.commissionRate}%</div>
                              <div className="text-xs text-gray-500">Rate</div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <Badge className={getTierColor(affiliate.tier)}>
                                {affiliate.tier}
                              </Badge>
                              <div className="mt-1">
                                <Badge className={getStatusColor(affiliate.status)}>
                                  {affiliate.status}
                                </Badge>
                              </div>
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
                              {affiliate.status === 'pending' && (
                                <Button 
                                  size="sm"
                                  onClick={() => handleApproveAffiliate(affiliate.id)}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Approve
                                </Button>
                              )}
                              {affiliate.status === 'active' && (
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => handleSuspendAffiliate(affiliate.id)}
                                >
                                  <Ban className="h-4 w-4 mr-1" />
                                  Suspend
                                </Button>
                              )}
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

          <TabsContent value="commissions" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Commission Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {commissions.map((commission) => (
                    <Card key={commission.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center text-white">
                              <DollarSign className="h-5 w-5" />
                            </div>
                            <div>
                              <div className="font-semibold">{commission.affiliateName}</div>
                              <div className="text-sm text-gray-600">
                                Referral: {commission.referralName}
                              </div>
                              <div className="text-xs text-gray-500">
                                {new Date(commission.createdAt).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <div className="text-xl font-bold text-green-600">
                                ${commission.amount}
                              </div>
                              <div className="text-xs text-gray-500">{commission.currency}</div>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(commission.type)}>
                                {commission.type}
                              </Badge>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(commission.status)}>
                                {commission.status}
                              </Badge>
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            {commission.status === 'pending' && (
                              <Button 
                                size="sm"
                                onClick={() => handlePayCommission(commission.id)}
                                className="bg-green-600 hover:bg-green-700"
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Pay
                              </Button>
                            )}
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4 mr-1" />
                              Details
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

          <TabsContent value="programs" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Referral Programs</CardTitle>
                  <Button>
                    <Gift className="h-4 w-4 mr-2" />
                    Create Program
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {programs.map((program) => (
                    <Card key={program.id} className="border-2 border-dashed border-gray-200 hover:border-blue-300 transition-colors">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold">{program.name}</h3>
                          <Badge className={getStatusColor(program.status)}>
                            {program.status}
                          </Badge>
                        </div>
                        <p className="text-gray-600 mb-4">{program.description}</p>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500">Commission Rate:</span>
                            <span className="font-semibold">{program.commissionRate}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500">Tier:</span>
                            <Badge className={getTierColor(program.tier)}>
                              {program.tier}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500">Min Referrals:</span>
                            <span className="font-semibold">{program.minReferrals}</span>
                          </div>
                          {program.bonusAmount > 0 && (
                            <div className="flex justify-between">
                              <span className="text-sm text-gray-500">Bonus:</span>
                              <span className="font-semibold text-green-600">
                                ${program.bonusAmount}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="mt-4 flex space-x-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button size="sm" variant="outline" className="flex-1">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AffiliateManagerDashboard;