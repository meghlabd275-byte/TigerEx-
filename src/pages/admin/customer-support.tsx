import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  MessageSquare,
  Clock,
  CheckCircle,
  AlertTriangle,
  Search,
  User,
  Phone,
  Mail,
  FileText,
  Send,
  Archive,
  Star,
  Filter,
  BarChart3,
} from 'lucide-react';

interface SupportTicket {
  id: string;
  userId: string;
  userName: string;
  email: string;
  subject: string;
  category: 'trading' | 'account' | 'kyc' | 'technical' | 'billing' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  createdAt: string;
  updatedAt: string;
  assignedTo?: string;
  messages: TicketMessage[];
}

interface TicketMessage {
  id: string;
  sender: 'user' | 'support';
  senderName: string;
  message: string;
  timestamp: string;
  attachments?: string[];
}

interface SupportAgent {
  id: string;
  name: string;
  email: string;
  status: 'online' | 'offline' | 'busy';
  activeTickets: number;
  resolvedToday: number;
  avgResponseTime: number;
}

const CustomerSupportDashboard: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [agents, setAgents] = useState<SupportAgent[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(
    null
  );
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    // Mock support tickets data
    const mockTickets: SupportTicket[] = [
      {
        id: 'ticket-001',
        userId: 'user-123',
        userName: 'John Doe',
        email: 'john.doe@example.com',
        subject: 'Unable to withdraw funds',
        category: 'trading',
        priority: 'high',
        status: 'open',
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-15T10:30:00Z',
        messages: [
          {
            id: 'msg-001',
            sender: 'user',
            senderName: 'John Doe',
            message:
              'I am unable to withdraw my BTC. The transaction keeps failing.',
            timestamp: '2024-01-15T10:30:00Z',
          },
        ],
      },
      {
        id: 'ticket-002',
        userId: 'user-456',
        userName: 'Jane Smith',
        email: 'jane.smith@example.com',
        subject: 'KYC verification stuck',
        category: 'kyc',
        priority: 'medium',
        status: 'in_progress',
        createdAt: '2024-01-14T15:45:00Z',
        updatedAt: '2024-01-15T09:20:00Z',
        assignedTo: 'agent-001',
        messages: [
          {
            id: 'msg-002',
            sender: 'user',
            senderName: 'Jane Smith',
            message:
              'My KYC has been pending for 3 days. Can you please check?',
            timestamp: '2024-01-14T15:45:00Z',
          },
          {
            id: 'msg-003',
            sender: 'support',
            senderName: 'Support Agent',
            message:
              'We are reviewing your documents. You will receive an update within 24 hours.',
            timestamp: '2024-01-15T09:20:00Z',
          },
        ],
      },
      {
        id: 'ticket-003',
        userId: 'user-789',
        userName: 'Bob Johnson',
        email: 'bob.johnson@example.com',
        subject: 'API key not working',
        category: 'technical',
        priority: 'low',
        status: 'resolved',
        createdAt: '2024-01-13T09:15:00Z',
        updatedAt: '2024-01-13T14:30:00Z',
        assignedTo: 'agent-002',
        messages: [
          {
            id: 'msg-004',
            sender: 'user',
            senderName: 'Bob Johnson',
            message: 'My API key is returning 401 errors.',
            timestamp: '2024-01-13T09:15:00Z',
          },
          {
            id: 'msg-005',
            sender: 'support',
            senderName: 'Tech Support',
            message:
              'Please regenerate your API key and ensure you have the correct permissions.',
            timestamp: '2024-01-13T14:30:00Z',
          },
        ],
      },
    ];

    const mockAgents: SupportAgent[] = [
      {
        id: 'agent-001',
        name: 'Alice Cooper',
        email: 'alice@tigerex.com',
        status: 'online',
        activeTickets: 5,
        resolvedToday: 12,
        avgResponseTime: 15,
      },
      {
        id: 'agent-002',
        name: 'Bob Wilson',
        email: 'bob@tigerex.com',
        status: 'online',
        activeTickets: 3,
        resolvedToday: 8,
        avgResponseTime: 22,
      },
      {
        id: 'agent-003',
        name: 'Carol Davis',
        email: 'carol@tigerex.com',
        status: 'busy',
        activeTickets: 7,
        resolvedToday: 15,
        avgResponseTime: 18,
      },
    ];

    setTickets(mockTickets);
    setAgents(mockAgents);
  }, []);

  const handleAssignTicket = (ticketId: string, agentId: string) => {
    setTickets((prev) =>
      prev.map((ticket) =>
        ticket.id === ticketId
          ? { ...ticket, assignedTo: agentId, status: 'in_progress' as const }
          : ticket
      )
    );
    alert(`Ticket ${ticketId} assigned to agent ${agentId}`);
  };

  const handleResolveTicket = (ticketId: string) => {
    setTickets((prev) =>
      prev.map((ticket) =>
        ticket.id === ticketId
          ? {
              ...ticket,
              status: 'resolved' as const,
              updatedAt: new Date().toISOString(),
            }
          : ticket
      )
    );
    alert(`Ticket ${ticketId} marked as resolved`);
  };

  const handleSendMessage = () => {
    if (!selectedTicket || !newMessage.trim()) return;

    const message: TicketMessage = {
      id: `msg-${Date.now()}`,
      sender: 'support',
      senderName: 'Support Agent',
      message: newMessage,
      timestamp: new Date().toISOString(),
    };

    setTickets((prev) =>
      prev.map((ticket) =>
        ticket.id === selectedTicket.id
          ? {
              ...ticket,
              messages: [...ticket.messages, message],
              updatedAt: new Date().toISOString(),
            }
          : ticket
      )
    );

    setNewMessage('');
    alert('Message sent successfully');
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'trading':
        return 'bg-purple-100 text-purple-800';
      case 'account':
        return 'bg-blue-100 text-blue-800';
      case 'kyc':
        return 'bg-orange-100 text-orange-800';
      case 'technical':
        return 'bg-green-100 text-green-800';
      case 'billing':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500';
      case 'busy':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredTickets = tickets.filter(
    (ticket) =>
      ticket.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalTickets: tickets.length,
    openTickets: tickets.filter((t) => t.status === 'open').length,
    inProgressTickets: tickets.filter((t) => t.status === 'in_progress').length,
    resolvedTickets: tickets.filter((t) => t.status === 'resolved').length,
    urgentTickets: tickets.filter((t) => t.priority === 'urgent').length,
    avgResponseTime:
      agents.reduce((sum, agent) => sum + agent.avgResponseTime, 0) /
      agents.length,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Customer Support Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Manage customer inquiries and support tickets
          </p>
        </div>

        {/* Support Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {stats.totalTickets}
                  </div>
                  <div className="text-sm text-gray-600">Total Tickets</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-orange-600" />
                <div>
                  <div className="text-2xl font-bold text-orange-600">
                    {stats.openTickets}
                  </div>
                  <div className="text-sm text-gray-600">Open</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-yellow-600" />
                <div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {stats.inProgressTickets}
                  </div>
                  <div className="text-sm text-gray-600">In Progress</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {stats.resolvedTickets}
                  </div>
                  <div className="text-sm text-gray-600">Resolved</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div>
                  <div className="text-2xl font-bold text-red-600">
                    {stats.urgentTickets}
                  </div>
                  <div className="text-sm text-gray-600">Urgent</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {stats.avgResponseTime}m
                  </div>
                  <div className="text-sm text-gray-600">Avg Response</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs
          value={selectedTab}
          onValueChange={setSelectedTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tickets">
              Tickets ({stats.totalTickets})
            </TabsTrigger>
            <TabsTrigger value="agents">Agents ({agents.length})</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Tickets</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tickets.slice(0, 5).map((ticket) => (
                      <div
                        key={ticket.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <div className="font-semibold">{ticket.subject}</div>
                          <div className="text-sm text-gray-600">
                            {ticket.userName}
                          </div>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge
                              className={getPriorityColor(ticket.priority)}
                            >
                              {ticket.priority}
                            </Badge>
                            <Badge
                              className={getCategoryColor(ticket.category)}
                            >
                              {ticket.category}
                            </Badge>
                          </div>
                        </div>
                        <Badge className={getStatusColor(ticket.status)}>
                          {ticket.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Agent Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {agents.map((agent) => (
                      <div
                        key={agent.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="relative">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {agent.name.charAt(0)}
                            </div>
                            <div
                              className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getAgentStatusColor(agent.status)}`}
                            ></div>
                          </div>
                          <div>
                            <div className="font-semibold">{agent.name}</div>
                            <div className="text-sm text-gray-600">
                              {agent.email}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold">
                            {agent.activeTickets} active
                          </div>
                          <div className="text-xs text-gray-500">
                            {agent.resolvedToday} resolved today
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="tickets" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Support Tickets</CardTitle>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filter
                    </Button>
                    <Button size="sm">
                      <MessageSquare className="h-4 w-4 mr-2" />
                      New Ticket
                    </Button>
                  </div>
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search tickets..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredTickets.map((ticket) => (
                    <Card
                      key={ticket.id}
                      className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => setSelectedTicket(ticket)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {ticket.userName.charAt(0)}
                            </div>
                            <div>
                              <div className="font-semibold">
                                {ticket.subject}
                              </div>
                              <div className="text-sm text-gray-600">
                                {ticket.userName} • {ticket.email}
                              </div>
                              <div className="text-xs text-gray-500">
                                Created:{' '}
                                {new Date(
                                  ticket.createdAt
                                ).toLocaleDateString()}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <Badge
                                className={getPriorityColor(ticket.priority)}
                              >
                                {ticket.priority}
                              </Badge>
                            </div>
                            <div className="text-center">
                              <Badge
                                className={getCategoryColor(ticket.category)}
                              >
                                {ticket.category}
                              </Badge>
                            </div>
                            <div className="text-center">
                              <Badge className={getStatusColor(ticket.status)}>
                                {ticket.status.replace('_', ' ')}
                              </Badge>
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            {ticket.status === 'open' && (
                              <Button
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAssignTicket(ticket.id, 'agent-001');
                                }}
                              >
                                Assign
                              </Button>
                            )}
                            {ticket.status === 'in_progress' && (
                              <Button
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleResolveTicket(ticket.id);
                                }}
                                className="bg-green-600 hover:bg-green-700"
                              >
                                Resolve
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="agents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Support Agents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {agents.map((agent) => (
                    <Card
                      key={agent.id}
                      className="hover:shadow-md transition-shadow"
                    >
                      <CardContent className="p-6">
                        <div className="flex items-center space-x-4 mb-4">
                          <div className="relative">
                            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                              {agent.name.charAt(0)}
                            </div>
                            <div
                              className={`absolute -bottom-1 -right-1 w-6 h-6 rounded-full border-4 border-white ${getAgentStatusColor(agent.status)}`}
                            ></div>
                          </div>
                          <div>
                            <div className="font-semibold text-lg">
                              {agent.name}
                            </div>
                            <div className="text-gray-600">{agent.email}</div>
                            <div className="text-sm text-gray-500 capitalize">
                              {agent.status}
                            </div>
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-gray-600">
                              Active Tickets:
                            </span>
                            <span className="font-semibold">
                              {agent.activeTickets}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">
                              Resolved Today:
                            </span>
                            <span className="font-semibold text-green-600">
                              {agent.resolvedToday}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Avg Response:</span>
                            <span className="font-semibold">
                              {agent.avgResponseTime}m
                            </span>
                          </div>
                        </div>

                        <div className="mt-4 flex space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                          >
                            <Mail className="h-4 w-4 mr-1" />
                            Message
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                          >
                            <Phone className="h-4 w-4 mr-1" />
                            Call
                          </Button>
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
                  <CardTitle>Ticket Categories</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      'trading',
                      'account',
                      'kyc',
                      'technical',
                      'billing',
                      'other',
                    ].map((category) => {
                      const count = tickets.filter(
                        (t) => t.category === category
                      ).length;
                      const percentage = (count / tickets.length) * 100;
                      return (
                        <div
                          key={category}
                          className="flex items-center justify-between"
                        >
                          <div className="flex items-center space-x-2">
                            <Badge className={getCategoryColor(category)}>
                              {category}
                            </Badge>
                            <span className="text-sm text-gray-600">
                              {count} tickets
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-20 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-semibold">
                              {percentage.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Response Time Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        Average Response Time:
                      </span>
                      <span className="font-semibold">
                        {stats.avgResponseTime.toFixed(1)} minutes
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">First Response SLA:</span>
                      <span className="font-semibold text-green-600">
                        95.2%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Resolution SLA:</span>
                      <span className="font-semibold text-green-600">
                        87.8%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">
                        Customer Satisfaction:
                      </span>
                      <span className="font-semibold text-green-600">
                        4.7/5.0
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Ticket Detail Modal */}
        {selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-y-auto w-full mx-4">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Ticket Details</h2>
                <Button
                  variant="outline"
                  onClick={() => setSelectedTicket(null)}
                >
                  Close
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-2">Ticket Information</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <strong>ID:</strong> {selectedTicket.id}
                    </div>
                    <div>
                      <strong>Subject:</strong> {selectedTicket.subject}
                    </div>
                    <div>
                      <strong>Category:</strong>
                      <Badge
                        className={`ml-2 ${getCategoryColor(selectedTicket.category)}`}
                      >
                        {selectedTicket.category}
                      </Badge>
                    </div>
                    <div>
                      <strong>Priority:</strong>
                      <Badge
                        className={`ml-2 ${getPriorityColor(selectedTicket.priority)}`}
                      >
                        {selectedTicket.priority}
                      </Badge>
                    </div>
                    <div>
                      <strong>Status:</strong>
                      <Badge
                        className={`ml-2 ${getStatusColor(selectedTicket.status)}`}
                      >
                        {selectedTicket.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Customer Information</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <strong>Name:</strong> {selectedTicket.userName}
                    </div>
                    <div>
                      <strong>Email:</strong> {selectedTicket.email}
                    </div>
                    <div>
                      <strong>User ID:</strong> {selectedTicket.userId}
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Timeline</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <strong>Created:</strong>{' '}
                      {new Date(selectedTicket.createdAt).toLocaleString()}
                    </div>
                    <div>
                      <strong>Updated:</strong>{' '}
                      {new Date(selectedTicket.updatedAt).toLocaleString()}
                    </div>
                    {selectedTicket.assignedTo && (
                      <div>
                        <strong>Assigned to:</strong>{' '}
                        {selectedTicket.assignedTo}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold mb-4">Conversation</h3>
                <div className="space-y-4 max-h-96 overflow-y-auto border rounded-lg p-4">
                  {selectedTicket.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'support' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.sender === 'support'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-800'
                        }`}
                      >
                        <div className="font-semibold text-sm">
                          {message.senderName}
                        </div>
                        <div className="mt-1">{message.message}</div>
                        <div className="text-xs mt-2 opacity-75">
                          {new Date(message.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <Textarea
                  placeholder="Type your response..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  rows={3}
                />
                <div className="flex justify-between">
                  <div className="space-x-2">
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-1" />
                      Attach File
                    </Button>
                    <Button variant="outline" size="sm">
                      <Archive className="h-4 w-4 mr-1" />
                      Archive
                    </Button>
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim()}
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send Reply
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerSupportDashboard;
