/**
 * TigerEx Enhanced Admin Dashboard
 * Complete admin control interface with comprehensive user management
 */

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Space,
  Statistic,
  Row,
  Col,
  Alert,
  Tag,
  Tabs,
  DatePicker,
  InputNumber,
  message,
  Popconfirm,
  Tooltip,
  Badge,
  Progress,
  Timeline,
  Descriptions,
  Drawer,
  Tree,
  Menu,
  Avatar,
  Dropdown
} from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  SettingOutlined,
  SecurityScanOutlined,
  BarChartOutlined,
  LogoutOutlined,
  BellOutlined,
  SearchOutlined,
  ExportOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  LockOutlined,
  UnlockOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  BankOutlined,
  RocketOutlined,
  TrophyOutlined,
  GiftOutlined,
  CrownOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import moment from 'moment';

const { Header, Sider, Content } = Layout;
const { TabPane } = Tabs;
const { RangePicker } = DatePicker;
const { TextArea } = Input;

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  kyc_status: string;
  kyc_level: number;
  is_active: boolean;
  is_admin: boolean;
  is_superadmin: boolean;
  trading_enabled: boolean;
  withdrawal_enabled: boolean;
  deposit_enabled: boolean;
  created_at: string;
  last_login?: string;
  risk_score: number;
  wallets: Array<{
    currency: string;
    balance: number;
    locked_balance: number;
  }>;
}

interface DashboardStats {
  users: {
    total: number;
    active: number;
    admin: number;
    verified: number;
    new_today: number;
    active_today: number;
  };
  trading: {
    total_orders: number;
    orders_today: number;
    volume_today: number;
    pending_orders: number;
    filled_orders: number;
  };
  financial: {
    total_transactions: number;
    deposits: number;
    withdrawals: number;
    pending_transactions: number;
    total_deposits: number;
    total_withdrawals: number;
  };
  system: {
    database: string;
    redis: string;
    services: Record<string, string>;
  };
}

const EnhancedAdminDashboard: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [userDetailsVisible, setUserDetailsVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [form] = Form.useForm();
  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState({});

  // Simulated API calls - replace with actual API calls
  useEffect(() => {
    loadDashboardData();
    loadUsers();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      const mockStats: DashboardStats = {
        users: {
          total: 15420,
          active: 14850,
          admin: 25,
          verified: 12300,
          new_today: 45,
          active_today: 3200
        },
        trading: {
          total_orders: 125000,
          orders_today: 2100,
          volume_today: 45600000,
          pending_orders: 125,
          filled_orders: 124875
        },
        financial: {
          total_transactions: 98000,
          deposits: 65000,
          withdrawals: 33000,
          pending_transactions: 89,
          total_deposits: 125000000,
          total_withdrawals: 98000000
        },
        system: {
          database: 'healthy',
          redis: 'healthy',
          services: {
            trading_engine: 'healthy',
            wallet_service: 'healthy',
            notification_service: 'healthy',
            market_data: 'healthy'
          }
        }
      };
      setStats(mockStats);
    } catch (error) {
      message.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      // Simulate API call
      const mockUsers: User[] = [
        {
          id: 1,
          email: 'john@example.com',
          username: 'johntrader',
          full_name: 'John Trader',
          phone: '+1234567890',
          kyc_status: 'approved',
          kyc_level: 2,
          is_active: true,
          is_admin: false,
          is_superadmin: false,
          trading_enabled: true,
          withdrawal_enabled: true,
          deposit_enabled: true,
          created_at: '2024-01-15T10:30:00Z',
          last_login: '2025-01-07T14:25:00Z',
          risk_score: 15,
          wallets: [
            { currency: 'BTC', balance: 0.5, locked_balance: 0 },
            { currency: 'USDT', balance: 10000, locked_balance: 500 }
          ]
        },
        {
          id: 2,
          email: 'jane@example.com',
          username: 'janetrader',
          full_name: 'Jane Trader',
          kyc_status: 'pending',
          kyc_level: 0,
          is_active: true,
          is_admin: false,
          is_superadmin: false,
          trading_enabled: true,
          withdrawal_enabled: false,
          deposit_enabled: true,
          created_at: '2024-02-20T09:15:00Z',
          last_login: '2025-01-07T12:10:00Z',
          risk_score: 45,
          wallets: [
            { currency: 'ETH', balance: 2.5, locked_balance: 0 },
            { currency: 'USDT', balance: 5000, locked_balance: 0 }
          ]
        }
      ];
      setUsers(mockUsers);
    } catch (error) {
      message.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (action: string, userId: number, data?: any) => {
    try {
      setLoading(true);
      
      switch (action) {
        case 'freeze':
          // API call to freeze user
          message.success('User account frozen successfully');
          break;
        case 'unfreeze':
          // API call to unfreeze user
          message.success('User account unfrozen successfully');
          break;
        case 'update_permissions':
          // API call to update user permissions
          message.success('User permissions updated successfully');
          break;
        case 'update_kyc':
          // API call to update KYC status
          message.success('KYC status updated successfully');
          break;
        default:
          break;
      }
      
      loadUsers();
    } catch (error) {
      message.error(`Failed to ${action} user`);
    } finally {
      setLoading(false);
    }
  };

  const userColumns: ColumnsType<User> = [
    {
      title: 'User',
      dataIndex: 'full_name',
      key: 'user',
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 'bold' }}>{record.full_name}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{record.email}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'KYC Status',
      dataIndex: 'kyc_status',
      key: 'kyc_status',
      render: (status, record) => (
        <Space direction="vertical" size="small">
          <Tag color={status === 'approved' ? 'green' : status === 'pending' ? 'orange' : 'red'}>
            {status.toUpperCase()}
          </Tag>
          <span style={{ fontSize: '12px' }}>Level {record.kyc_level}</span>
        </Space>
      ),
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Tag color={record.is_active ? 'green' : 'red'}>
            {record.is_active ? 'Active' : 'Inactive'}
          </Tag>
          {record.is_admin && <Tag color="blue">Admin</Tag>}
          {record.is_superadmin && <Tag color="purple">Super Admin</Tag>}
        </Space>
      ),
    },
    {
      title: 'Trading',
      key: 'trading',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Tag color={record.trading_enabled ? 'green' : 'red'}>
            Trading: {record.trading_enabled ? 'Enabled' : 'Disabled'}
          </Tag>
          <Tag color={record.withdrawal_enabled ? 'green' : 'red'}>
            Withdrawals: {record.withdrawal_enabled ? 'Enabled' : 'Disabled'}
          </Tag>
          <Tag color={record.deposit_enabled ? 'green' : 'red'}>
            Deposits: {record.deposit_enabled ? 'Enabled' : 'Disabled'}
          </Tag>
        </Space>
      ),
    },
    {
      title: 'Risk Score',
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score) => (
        <Progress
          percent={score}
          size="small"
          status={score > 70 ? 'exception' : score > 40 ? 'active' : 'success'}
          format={() => score}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="View Details">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => {
                setSelectedUser(record);
                setUserDetailsVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="Edit User">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => {
                setSelectedUser(record);
                form.setFieldsValue(record);
                setUserModalVisible(true);
              }}
            />
          </Tooltip>
          {record.is_active ? (
            <Popconfirm
              title="Are you sure you want to freeze this user?"
              onConfirm={() => handleUserAction('freeze', record.id)}
            >
              <Tooltip title="Freeze User">
                <Button type="text" danger icon={<LockOutlined />} />
              </Tooltip>
            </Popconfirm>
          ) : (
            <Popconfirm
              title="Are you sure you want to unfreeze this user?"
              onConfirm={() => handleUserAction('unfreeze', record.id)}
            >
              <Tooltip title="Unfreeze User">
                <Button type="text" icon={<UnlockOutlined />} />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  const menuItems = [
    {
      key: 'overview',
      icon: <BarChartOutlined />,
      label: 'Overview',
    },
    {
      key: 'users',
      icon: <UserOutlined />,
      label: 'User Management',
    },
    {
      key: 'trading',
      icon: <ShoppingCartOutlined />,
      label: 'Trading',
    },
    {
      key: 'financial',
      icon: <DollarOutlined />,
      label: 'Financial',
    },
    {
      key: 'security',
      icon: <SecurityScanOutlined />,
      label: 'Security',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  const renderOverview = () => (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Users"
              value={stats?.users.total}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <span style={{ color: '#52c41a' }}>+{stats?.users.new_today}</span> new today
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Active Users"
              value={stats?.users.active}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              <span style={{ color: '#1890ff' }}>{stats?.users.active_today} active today</span>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Orders"
              value={stats?.trading.total_orders}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: 8 }}>
              <span style={{ color: '#52c41a' }}>+{stats?.trading.orders_today}</span> today
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Volume"
              value={stats?.trading.volume_today}
              prefix={<DollarOutlined />}
              precision={2}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8 }}>
              <span style={{ color: '#666' }}>USDT (24h)</span>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="System Health" extra={<Button icon={<ReloadOutlined />} />}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <strong>Database:</strong>
                <Badge status={stats?.system.database === 'healthy' ? 'success' : 'error'} 
                       text={stats?.system.database} />
              </div>
              <div>
                <strong>Redis:</strong>
                <Badge status={stats?.system.redis === 'healthy' ? 'success' : 'error'} 
                       text={stats?.system.redis} />
              </div>
              <div>
                <strong>Services:</strong>
                {Object.entries(stats?.system.services || {}).map(([service, status]) => (
                  <div key={service}>
                    {service}: <Badge status={status === 'healthy' ? 'success' : 'error'} text={status} />
                  </div>
                ))}
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Recent Activities" extra={<Button icon={<ExportOutlined />} />}>
            <Timeline>
              <Timeline.Item color="green">New user registration spike detected</Timeline.Item>
              <Timeline.Item color="blue">Trading volume increased by 25%</Timeline.Item>
              <Timeline.Item color="orange">System maintenance completed</Timeline.Item>
              <Timeline.Item>KYC verification queue processed</Timeline.Item>
            </Timeline>
          </Card>
        </Col>
      </Row>
    </div>
  );

  const renderUserManagement = () => (
    <div>
      <Card
        title="User Management"
        extra={
          <Space>
            <Input
              placeholder="Search users..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
            />
            <Button type="primary" onClick={() => setUserModalVisible(true)}>
              Add User
            </Button>
            <Button icon={<ExportOutlined />}>
              Export
            </Button>
          </Space>
        }
      >
        <Table
          columns={userColumns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            total: users.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>
    </div>
  );

  const renderTrading = () => (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Trading Overview">
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Statistic
                  title="Pending Orders"
                  value={stats?.trading.pending_orders}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Filled Orders"
                  value={stats?.trading.filled_orders}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="Fill Rate"
                  value={((stats?.trading.filled_orders || 0) / (stats?.trading.total_orders || 1)) * 100}
                  precision={2}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.3)' }} />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[activeTab]}
          items={menuItems}
          onClick={({ key }) => setActiveTab(key)}
        />
      </Sider>
      
      <Layout>
        <Header style={{ background: '#fff', padding: '0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0 }}>TigerEx Admin Dashboard</h1>
          </div>
          <Space>
            <Badge count={5}>
              <Button type="text" icon={<BellOutlined />} />
            </Badge>
            <Dropdown
              menu={{
                items: [
                  { key: 'profile', label: 'Profile' },
                  { key: 'settings', label: 'Settings' },
                  { key: 'logout', label: 'Logout', icon: <LogoutOutlined /> },
                ]
              }}
            >
              <Button type="text">
                <Avatar icon={<UserOutlined />} /> Admin
              </Button>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="Overview" key="overview">
              {renderOverview()}
            </TabPane>
            <TabPane tab="User Management" key="users">
              {renderUserManagement()}
            </TabPane>
            <TabPane tab="Trading" key="trading">
              {renderTrading()}
            </TabPane>
            <TabPane tab="Financial" key="financial">
              <div>Financial operations coming soon...</div>
            </TabPane>
            <TabPane tab="Security" key="security">
              <div>Security monitoring coming soon...</div>
            </TabPane>
            <TabPane tab="Settings" key="settings">
              <div>System settings coming soon...</div>
            </TabPane>
          </Tabs>
        </Content>
      </Layout>

      {/* User Edit Modal */}
      <Modal
        title="Edit User"
        open={userModalVisible}
        onCancel={() => setUserModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setUserModalVisible(false)}>
            Cancel
          </Button>,
          <Button key="save" type="primary" loading={loading} onClick={() => {
            form.validateFields().then(values => {
              handleUserAction('update_permissions', selectedUser?.id || 0, values);
              setUserModalVisible(false);
            });
          }}>
            Save Changes
          </Button>
        ]}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="trading_enabled" label="Trading Enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="withdrawal_enabled" label="Withdrawal Enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="deposit_enabled" label="Deposit Enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="kyc_status" label="KYC Status">
            <Select>
              <Select.Option value="pending">Pending</Select.Option>
              <Select.Option value="approved">Approved</Select.Option>
              <Select.Option value="rejected">Rejected</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="kyc_level" label="KYC Level">
            <InputNumber min={0} max={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* User Details Drawer */}
      <Drawer
        title="User Details"
        placement="right"
        onClose={() => setUserDetailsVisible(false)}
        open={userDetailsVisible}
        width={600}
      >
        {selectedUser && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="Full Name">{selectedUser.full_name}</Descriptions.Item>
            <Descriptions.Item label="Email">{selectedUser.email}</Descriptions.Item>
            <Descriptions.Item label="Username">{selectedUser.username}</Descriptions.Item>
            <Descriptions.Item label="Phone">{selectedUser.phone}</Descriptions.Item>
            <Descriptions.Item label="KYC Status">
              <Tag color={selectedUser.kyc_status === 'approved' ? 'green' : 'orange'}>
                {selectedUser.kyc_status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Risk Score">
              <Progress percent={selectedUser.risk_score} size="small" />
            </Descriptions.Item>
            <Descriptions.Item label="Member Since">
              {moment(selectedUser.created_at).format('YYYY-MM-DD HH:mm')}
            </Descriptions.Item>
            <Descriptions.Item label="Last Login">
              {selectedUser.last_login ? moment(selectedUser.last_login).format('YYYY-MM-DD HH:mm') : 'Never'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </Layout>
  );
};

export default EnhancedAdminDashboard;