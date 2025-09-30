import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  TrendingUp, 
  DollarSign, 
  Activity, 
  Shield, 
  Settings,
  AlertTriangle,
  BarChart3,
  Database,
  Server,
  Globe,
  Zap
} from 'lucide-react';

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalVolume: string;
  totalRevenue: string;
  systemUptime: string;
  activeServices: number;
  totalServices: number;
}

interface SecurityAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  message: string;
  timestamp: string;
}

const SuperAdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalUsers: 0,
    activeUsers: 0,
    totalVolume: '$0',
    totalRevenue: '$0',
    systemUptime: '99.99%',
    activeServices: 0,
    totalServices: 25
  });

  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalUsers: Math.floor(Math.random() * 100000) + 50000,
        activeUsers: Math.floor(Math.random() * 10000) + 5000,
        totalVolume: `$${(Math.random() * 1000000000 + 500000000).toFixed(0)}`,
        totalRevenue: `$${(Math.random() * 10000000 + 5000000).toFixed(0)}`,
        activeServices: Math.floor(Math.random() * 3) + 23
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleEmergencyStop = () => {
    alert('Emergency stop initiated. All trading activities will be halted.');
  };

  const handleSystemMaintenance = () => {
    alert('System maintenance mode activated.');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Super Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Complete system oversight and control</p>
        </div>

        {/* Emergency Controls */}
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="font-semibold text-red-800">Emergency Controls</span>
            </div>
            <div className="space-x-2">
              <Button variant="destructive" size="sm" onClick={handleEmergencyStop}>
                Emergency Stop
              </Button>
              <Button variant="outline" size="sm" onClick={handleSystemMaintenance}>
                Maintenance Mode
              </Button>
            </div>
          </div>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="trading">Trading</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalUsers.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.activeUsers.toLocaleString()} active now
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Trading Volume</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalVolume}</div>
                  <p className="text-xs text-muted-foreground">24h volume</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalRevenue}</div>
                  <p className="text-xs text-muted-foreground">Total revenue</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">System Health</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.systemUptime}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.activeServices}/{metrics.totalServices} services active
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Service Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'API Gateway', status: 'active', port: '8080' },
                      { name: 'Matching Engine', status: 'active', port: '8081' },
                      { name: 'Transaction Engine', status: 'active', port: '8082' },
                      { name: 'Risk Management', status: 'warning', port: '8083' },
                      { name: 'Spot Trading', status: 'active', port: '8091' },
                      { name: 'Derivatives Engine', status: 'active', port: '8094' },
                      { name: 'P2P Trading', status: 'active', port: '8097' },
                      { name: 'Block Explorer', status: 'active', port: '8110' }
                    ].map((service) => (
                      <div key={service.name} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            service.status === 'active' ? 'bg-green-500' : 
                            service.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                          }`} />
                          <span className="text-sm font-medium">{service.name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={service.status === 'active' ? 'default' : 'secondary'}>
                            {service.status}
                          </Badge>
                          <span className="text-xs text-gray-500">:{service.port}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Activities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { action: 'New user registration spike', time: '2 minutes ago', type: 'info' },
                      { action: 'High volume trading detected', time: '5 minutes ago', type: 'warning' },
                      { action: 'System backup completed', time: '1 hour ago', type: 'success' },
                      { action: 'New trading pair added: SOL/USDT', time: '2 hours ago', type: 'info' },
                      { action: 'Security scan completed', time: '4 hours ago', type: 'success' }
                    ].map((activity, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          activity.type === 'success' ? 'bg-green-500' :
                          activity.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                        }`} />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{activity.action}</p>
                          <p className="text-xs text-gray-500">{activity.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>User Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">156,789</div>
                    <div className="text-sm text-blue-800">Total Users</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">12,345</div>
                    <div className="text-sm text-green-800">Verified Users</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">2,456</div>
                    <div className="text-sm text-yellow-800">Pending KYC</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <Button className="w-full">View All Users</Button>
                  <Button variant="outline" className="w-full">Export User Data</Button>
                  <Button variant="outline" className="w-full">Bulk User Actions</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trading" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trading Controls</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full">Halt All Trading</Button>
                  <Button variant="outline" className="w-full">Pause Derivatives</Button>
                  <Button variant="outline" className="w-full">Emergency Liquidation</Button>
                  <Button variant="outline" className="w-full">Adjust Risk Parameters</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Market Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span>Active Trading Pairs</span>
                      <span className="font-semibold">2,156</span>
                    </div>
                    <div className="flex justify-between">
                      <span>24h Volume</span>
                      <span className="font-semibold">$2.4B</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active Orders</span>
                      <span className="font-semibold">45,678</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Completed Trades</span>
                      <span className="font-semibold">123,456</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Security Dashboard</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Security Metrics</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Failed Login Attempts</span>
                        <span className="text-red-600 font-semibold">234</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Suspicious Activities</span>
                        <span className="text-yellow-600 font-semibold">12</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Blocked IPs</span>
                        <span className="font-semibold">45</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Active 2FA Users</span>
                        <span className="text-green-600 font-semibold">89.5%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-3">Quick Actions</h3>
                    <div className="space-y-2">
                      <Button variant="outline" className="w-full">Run Security Scan</Button>
                      <Button variant="outline" className="w-full">View Audit Logs</Button>
                      <Button variant="outline" className="w-full">Manage IP Whitelist</Button>
                      <Button variant="destructive" className="w-full">Lock User Account</Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Resources</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">CPU Usage</span>
                        <span className="text-sm">45%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Memory Usage</span>
                        <span className="text-sm">67%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{ width: '67%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Disk Usage</span>
                        <span className="text-sm">23%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '23%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Database Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'PostgreSQL Primary', status: 'healthy', connections: 45 },
                      { name: 'PostgreSQL Replica', status: 'healthy', connections: 23 },
                      { name: 'Redis Cache', status: 'healthy', connections: 156 },
                      { name: 'MongoDB', status: 'warning', connections: 12 }
                    ].map((db) => (
                      <div key={db.name} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            db.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
                          }`} />
                          <span className="text-sm font-medium">{db.name}</span>
                        </div>
                        <span className="text-xs text-gray-500">{db.connections} connections</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="outline">Trading Parameters</Button>
                  <Button variant="outline">Fee Structure</Button>
                  <Button variant="outline">Risk Limits</Button>
                  <Button variant="outline">API Rate Limits</Button>
                  <Button variant="outline">Maintenance Windows</Button>
                  <Button variant="outline">Notification Settings</Button>
                  <Button variant="outline">Backup Configuration</Button>
                  <Button variant="outline">Security Policies</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SuperAdminDashboard;