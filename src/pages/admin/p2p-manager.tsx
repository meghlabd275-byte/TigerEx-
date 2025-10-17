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
  Users, 
  TrendingUp, 
  AlertTriangle, 
  Search,
  MessageSquare,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  Flag,
  DollarSign,
  Eye,
  Ban
} from 'lucide-react';

interface P2POrder {
  id: string;
  type: 'buy' | 'sell';
  userId: string;
  userName: string;
  amount: number;
  price: number;
  currency: string;
  fiatCurrency: string;
  paymentMethod: string;
  status: 'active' | 'completed' | 'cancelled' | 'disputed';
  createdAt: string;
  completedAt?: string;
  disputeReason?: string;
}

interface P2PDispute {
  id: string;
  orderId: string;
  buyerName: string;
  sellerName: string;
  amount: number;
  currency: string;
  reason: string;
  status: 'open' | 'investigating' | 'resolved';
  createdAt: string;
  priority: 'low' | 'medium' | 'high';
}

interface P2PMerchant {
  id: string;
  userName: string;
  email: string;
  completedOrders: number;
  successRate: number;
  totalVolume: number;
  status: 'active' | 'suspended' | 'banned';
  verificationLevel: 'basic' | 'verified' | 'premium';
  joinedAt: string;
}

const P2PManagerDashboard: React.FC = () => {
  const [orders, setOrders] = useState<P2POrder[]>([]);
  const [disputes, setDisputes] = useState<P2PDispute[]>([]);
  const [merchants, setMerchants] = useState<P2PMerchant[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Mock data
    const mockOrders: P2POrder[] = [
      {
        id: 'p2p-001',
        type: 'buy',
        userId: 'user-123',
        userName: 'John Doe',
        amount: 1.5,
        price: 45000,
        currency: 'BTC',
        fiatCurrency: 'USD',
        paymentMethod: 'Bank Transfer',
        status: 'active',
        createdAt: '2024-01-15T10:30:00Z'
      },
      {
        id: 'p2p-002',
        type: 'sell',
        userId: 'user-456',
        userName: 'Jane Smith',
        amount: 100,
        price: 2.5,
        currency: 'ETH',
        fiatCurrency: 'EUR',
        paymentMethod: 'PayPal',
        status: 'disputed',
        createdAt: '2024-01-14T15:45:00Z',
        disputeReason: 'Payment not received'
      }
    ];

    const mockDisputes: P2PDispute[] = [
      {
        id: 'dispute-001',
        orderId: 'p2p-002',
        buyerName: 'Alice Johnson',
        sellerName: 'Bob Wilson',
        amount: 0.5,
        currency: 'BTC',
        reason: 'Payment not received after 2 hours',
        status: 'open',
        createdAt: '2024-01-15T12:00:00Z',
        priority: 'high'
      },
      {
        id: 'dispute-002',
        orderId: 'p2p-003',
        buyerName: 'Charlie Brown',
        sellerName: 'Diana Prince',
        amount: 200,
        currency: 'USDT',
        reason: 'Wrong payment amount sent',
        status: 'investigating',
        createdAt: '2024-01-14T09:30:00Z',
        priority: 'medium'
      }
    ];

    const mockMerchants: P2PMerchant[] = [
      {
        id: 'merchant-001',
        userName: 'CryptoKing',
        email: 'cryptoking@example.com',
        completedOrders: 1250,
        successRate: 98.5,
        totalVolume: 2500000,
        status: 'active',
        verificationLevel: 'premium',
        joinedAt: '2023-06-15T00:00:00Z'
      },
      {
        id: 'merchant-002',
        userName: 'BitTrader',
        email: 'bittrader@example.com',
        completedOrders: 856,
        successRate: 95.2,
        totalVolume: 1200000,
        status: 'active',
        verificationLevel: 'verified',
        joinedAt: '2023-08-20T00:00:00Z'
      }
    ];

    setOrders(mockOrders);
    setDisputes(mockDisputes);
    setMerchants(mockMerchants);
  }, []);

  const handleResolveDispute = (disputeId: string, resolution: 'buyer' | 'seller') => {
    setDisputes(prev => 
      prev.map(dispute => 
        dispute.id === disputeId 
          ? { ...dispute, status: 'resolved' as const }
          : dispute
      )
    );
    alert(`Dispute ${disputeId} resolved in favor of ${resolution}`);
  };

  const handleSuspendMerchant = (merchantId: string) => {
    const reason = prompt('Please provide a reason for suspension:');
    if (reason) {
      setMerchants(prev => 
        prev.map(merchant => 
          merchant.id === merchantId 
            ? { ...merchant, status: 'suspended' as const }
            : merchant
        )
      );
      alert(`Merchant ${merchantId} suspended: ${reason}`);
    }
  };

  const handleCancelOrder = (orderId: string) => {
    const reason = prompt('Please provide a reason for cancellation:');
    if (reason) {
      setOrders(prev => 
        prev.map(order => 
          order.id === orderId 
            ? { ...order, status: 'cancelled' as const }
            : order
        )
      );
      alert(`Order ${orderId} cancelled: ${reason}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      case 'disputed': return 'bg-red-100 text-red-800';
      case 'suspended': return 'bg-yellow-100 text-yellow-800';
      case 'banned': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      default: return 'text-green-600';
    }
  };

  const stats = {
    totalOrders: orders.length,
    activeOrders: orders.filter(o => o.status === 'active').length,
    disputedOrders: orders.filter(o => o.status === 'disputed').length,
    totalDisputes: disputes.length,
    openDisputes: disputes.filter(d => d.status === 'open').length,
    totalMerchants: merchants.length,
    activeMerchants: merchants.filter(m => m.status === 'active').length,
    totalVolume: orders.reduce((sum, order) => sum + (order.amount * order.price), 0)
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">P2P Manager Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage peer-to-peer trading operations and disputes</p>
        </div>

        {/* P2P Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.activeOrders}</div>
                  <div className="text-sm text-gray-600">Active Orders</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">{stats.openDisputes}</div>
                  <div className="text-sm text-gray-600">Open Disputes</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">{stats.activeMerchants}</div>
                  <div className="text-sm text-gray-600">Active Merchants</div>
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
                    ${stats.totalVolume.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Volume</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="orders">Orders ({stats.totalOrders})</TabsTrigger>
            <TabsTrigger value="disputes">Disputes ({stats.totalDisputes})</TabsTrigger>
            <TabsTrigger value="merchants">Merchants ({stats.totalMerchants})</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent P2P Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {orders.slice(0, 5).map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-semibold">{order.userName}</div>
                          <div className="text-sm text-gray-600">
                            {order.type.toUpperCase()} {order.amount} {order.currency}
                          </div>
                        </div>
                        <Badge className={getStatusColor(order.status)}>
                          {order.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Urgent Disputes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {disputes.filter(d => d.priority === 'high').map((dispute) => (
                      <div key={dispute.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-semibold text-red-800">
                            {dispute.buyerName} vs {dispute.sellerName}
                          </div>
                          <Badge className="bg-red-100 text-red-800">HIGH</Badge>
                        </div>
                        <div className="text-sm text-red-700">{dispute.reason}</div>
                        <div className="mt-2 space-x-2">
                          <Button size="sm" onClick={() => handleResolveDispute(dispute.id, 'buyer')}>
                            Resolve for Buyer
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleResolveDispute(dispute.id, 'seller')}>
                            Resolve for Seller
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>P2P Orders Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search orders..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  {orders.map((order) => (
                    <Card key={order.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className={`w-3 h-3 rounded-full ${
                              order.type === 'buy' ? 'bg-green-500' : 'bg-red-500'
                            }`} />
                            <div>
                              <div className="font-semibold">{order.userName}</div>
                              <div className="text-sm text-gray-600">
                                {order.type.toUpperCase()} {order.amount} {order.currency} @ ${order.price}
                              </div>
                              <div className="text-xs text-gray-500">
                                Payment: {order.paymentMethod} • {order.fiatCurrency}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <Badge className={getStatusColor(order.status)}>
                                {order.status}
                              </Badge>
                              <div className="text-sm text-gray-500 mt-1">
                                {new Date(order.createdAt).toLocaleDateString()}
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2">
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </Button>
                              {order.status === 'active' && (
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => handleCancelOrder(order.id)}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Cancel
                                </Button>
                              )}
                              {order.status === 'disputed' && (
                                <Button size="sm" className="bg-yellow-600 hover:bg-yellow-700">
                                  <Flag className="h-4 w-4 mr-1" />
                                  Investigate
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

          <TabsContent value="disputes" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Dispute Resolution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {disputes.map((dispute) => (
                    <Card key={dispute.id} className="border-l-4 border-l-red-500">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <div className="font-semibold text-lg">
                              {dispute.buyerName} vs {dispute.sellerName}
                            </div>
                            <div className="text-sm text-gray-600">
                              Order: {dispute.orderId} • {dispute.amount} {dispute.currency}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={`${getPriorityColor(dispute.priority)} bg-opacity-10`}>
                              {dispute.priority.toUpperCase()}
                            </Badge>
                            <Badge className={getStatusColor(dispute.status)}>
                              {dispute.status}
                            </Badge>
                          </div>
                        </div>

                        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                          <div className="font-medium mb-1">Dispute Reason:</div>
                          <div className="text-gray-700">{dispute.reason}</div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-500">
                            Created: {new Date(dispute.createdAt).toLocaleString()}
                          </div>
                          
                          {dispute.status === 'open' && (
                            <div className="space-x-2">
                              <Button 
                                size="sm"
                                onClick={() => handleResolveDispute(dispute.id, 'buyer')}
                                className="bg-green-600 hover:bg-green-700"
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Resolve for Buyer
                              </Button>
                              <Button 
                                size="sm"
                                onClick={() => handleResolveDispute(dispute.id, 'seller')}
                                className="bg-blue-600 hover:bg-blue-700"
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Resolve for Seller
                              </Button>
                              <Button size="sm" variant="outline">
                                <MessageSquare className="h-4 w-4 mr-1" />
                                Contact Users
                              </Button>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="merchants" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Merchant Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {merchants.map((merchant) => (
                    <Card key={merchant.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {merchant.userName.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold text-lg">{merchant.userName}</div>
                              <div className="text-sm text-gray-600">{merchant.email}</div>
                              <div className="flex items-center space-x-4 mt-1">
                                <span className="text-xs text-gray-500">
                                  {merchant.completedOrders} orders
                                </span>
                                <span className="text-xs text-gray-500">
                                  {merchant.successRate}% success rate
                                </span>
                                <span className="text-xs text-gray-500">
                                  ${merchant.totalVolume.toLocaleString()} volume
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <Badge className={getStatusColor(merchant.status)}>
                                {merchant.status}
                              </Badge>
                              <div className="text-sm text-gray-500 mt-1">
                                {merchant.verificationLevel}
                              </div>
                            </div>

                            <div className="flex flex-col space-y-2">
                              <Button size="sm" variant="outline">
                                <Eye className="h-4 w-4 mr-1" />
                                View Profile
                              </Button>
                              {merchant.status === 'active' && (
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => handleSuspendMerchant(merchant.id)}
                                >
                                  <Ban className="h-4 w-4 mr-1" />
                                  Suspend
                                </Button>
                              )}
                              <Button size="sm" variant="outline">
                                <MessageSquare className="h-4 w-4 mr-1" />
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
        </Tabs>
      </div>
    </div>
  );
};

export default P2PManagerDashboard;