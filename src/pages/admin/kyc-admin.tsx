import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  Users, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Search,
  FileText,
  Camera,
  Shield,
  AlertTriangle,
  Download,
  Eye
} from 'lucide-react';

interface KYCApplication {
  id: string;
  userId: string;
  userName: string;
  email: string;
  status: 'pending' | 'approved' | 'rejected' | 'under_review';
  submittedAt: string;
  documents: {
    passport?: string;
    drivingLicense?: string;
    utilityBill?: string;
    selfie?: string;
  };
  riskScore: number;
  country: string;
  tier: 1 | 2 | 3;
}

const KYCAdminDashboard: React.FC = () => {
  const [applications, setApplications] = useState<KYCApplication[]>([]);
  const [selectedTab, setSelectedTab] = useState('pending');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedApplication, setSelectedApplication] = useState<KYCApplication | null>(null);

  useEffect(() => {
    // Simulate KYC applications data
    const mockApplications: KYCApplication[] = [
      {
        id: 'kyc-001',
        userId: 'user-123',
        userName: 'John Doe',
        email: 'john.doe@example.com',
        status: 'pending',
        submittedAt: '2024-01-15T10:30:00Z',
        documents: {
          passport: 'passport-001.jpg',
          utilityBill: 'bill-001.pdf',
          selfie: 'selfie-001.jpg'
        },
        riskScore: 25,
        country: 'United States',
        tier: 2
      },
      {
        id: 'kyc-002',
        userId: 'user-456',
        userName: 'Jane Smith',
        email: 'jane.smith@example.com',
        status: 'under_review',
        submittedAt: '2024-01-14T15:45:00Z',
        documents: {
          drivingLicense: 'license-002.jpg',
          utilityBill: 'bill-002.pdf',
          selfie: 'selfie-002.jpg'
        },
        riskScore: 45,
        country: 'Canada',
        tier: 3
      },
      {
        id: 'kyc-003',
        userId: 'user-789',
        userName: 'Bob Johnson',
        email: 'bob.johnson@example.com',
        status: 'approved',
        submittedAt: '2024-01-13T09:15:00Z',
        documents: {
          passport: 'passport-003.jpg',
          utilityBill: 'bill-003.pdf',
          selfie: 'selfie-003.jpg'
        },
        riskScore: 15,
        country: 'United Kingdom',
        tier: 2
      }
    ];
    setApplications(mockApplications);
  }, []);

  const handleApprove = (applicationId: string) => {
    setApplications(prev => 
      prev.map(app => 
        app.id === applicationId 
          ? { ...app, status: 'approved' as const }
          : app
      )
    );
    alert(`Application ${applicationId} approved successfully`);
  };

  const handleReject = (applicationId: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (reason) {
      setApplications(prev => 
        prev.map(app => 
          app.id === applicationId 
            ? { ...app, status: 'rejected' as const }
            : app
        )
      );
      alert(`Application ${applicationId} rejected: ${reason}`);
    }
  };

  const handleRequestMoreInfo = (applicationId: string) => {
    const info = prompt('What additional information is required?');
    if (info) {
      alert(`Additional information requested for ${applicationId}: ${info}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'under_review': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (selectedTab === 'all') return matchesSearch;
    return matchesSearch && app.status === selectedTab;
  });

  const stats = {
    pending: applications.filter(app => app.status === 'pending').length,
    under_review: applications.filter(app => app.status === 'under_review').length,
    approved: applications.filter(app => app.status === 'approved').length,
    rejected: applications.filter(app => app.status === 'rejected').length,
    total: applications.length
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">KYC Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage user identity verification and compliance</p>
        </div>

        {/* KYC Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.pending}</div>
                  <div className="text-sm text-gray-600">Pending</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Eye className="h-5 w-5 text-yellow-600" />
                <div>
                  <div className="text-2xl font-bold text-yellow-600">{stats.under_review}</div>
                  <div className="text-sm text-gray-600">Under Review</div>
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
                <Users className="h-5 w-5 text-gray-600" />
                <div>
                  <div className="text-2xl font-bold text-gray-600">{stats.total}</div>
                  <div className="text-sm text-gray-600">Total</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by name, email, or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardContent>
        </Card>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="pending">Pending ({stats.pending})</TabsTrigger>
            <TabsTrigger value="under_review">Under Review ({stats.under_review})</TabsTrigger>
            <TabsTrigger value="approved">Approved ({stats.approved})</TabsTrigger>
            <TabsTrigger value="rejected">Rejected ({stats.rejected})</TabsTrigger>
            <TabsTrigger value="all">All ({stats.total})</TabsTrigger>
          </TabsList>

          <TabsContent value={selectedTab} className="space-y-4">
            {filteredApplications.map((application) => (
              <Card key={application.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                        <Users className="h-6 w-6 text-gray-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{application.userName}</h3>
                        <p className="text-gray-600">{application.email}</p>
                        <p className="text-sm text-gray-500">ID: {application.id}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <Badge className={getStatusColor(application.status)}>
                          {application.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                        <p className="text-sm text-gray-500 mt-1">
                          Tier {application.tier} • {application.country}
                        </p>
                        <p className={`text-sm font-semibold ${getRiskColor(application.riskScore)}`}>
                          Risk Score: {application.riskScore}%
                        </p>
                      </div>

                      <div className="flex flex-col space-y-2">
                        {application.status === 'pending' && (
                          <>
                            <Button 
                              size="sm" 
                              onClick={() => handleApprove(application.id)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleReject(application.id)}
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                          </>
                        )}
                        {application.status === 'under_review' && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleRequestMoreInfo(application.id)}
                          >
                            <AlertTriangle className="h-4 w-4 mr-1" />
                            Request Info
                          </Button>
                        )}
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setSelectedApplication(application)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <FileText className="h-4 w-4 text-gray-500" />
                          <span className="text-sm text-gray-600">
                            {Object.keys(application.documents).length} documents
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Camera className="h-4 w-4 text-gray-500" />
                          <span className="text-sm text-gray-600">
                            {application.documents.selfie ? 'Selfie verified' : 'No selfie'}
                          </span>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        Submitted: {new Date(application.submittedAt).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {filteredApplications.length === 0 && (
              <Card>
                <CardContent className="p-8 text-center">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No applications found</h3>
                  <p className="text-gray-500">
                    {searchTerm ? 'Try adjusting your search criteria' : 'No KYC applications in this category'}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Document Viewer Modal */}
        {selectedApplication && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">KYC Application Details</h2>
                <Button variant="outline" onClick={() => setSelectedApplication(null)}>
                  Close
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-4">User Information</h3>
                  <div className="space-y-2">
                    <div><strong>Name:</strong> {selectedApplication.userName}</div>
                    <div><strong>Email:</strong> {selectedApplication.email}</div>
                    <div><strong>Country:</strong> {selectedApplication.country}</div>
                    <div><strong>Tier:</strong> {selectedApplication.tier}</div>
                    <div><strong>Risk Score:</strong> 
                      <span className={getRiskColor(selectedApplication.riskScore)}>
                        {selectedApplication.riskScore}%
                      </span>
                    </div>
                    <div><strong>Status:</strong> 
                      <Badge className={`ml-2 ${getStatusColor(selectedApplication.status)}`}>
                        {selectedApplication.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-4">Submitted Documents</h3>
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

              <div className="mt-6 pt-6 border-t flex justify-end space-x-4">
                {selectedApplication.status === 'pending' && (
                  <>
                    <Button 
                      onClick={() => {
                        handleApprove(selectedApplication.id);
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
                        handleReject(selectedApplication.id);
                        setSelectedApplication(null);
                      }}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject Application
                    </Button>
                  </>
                )}
                <Button 
                  variant="outline"
                  onClick={() => handleRequestMoreInfo(selectedApplication.id)}
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
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

export default KYCAdminDashboard;