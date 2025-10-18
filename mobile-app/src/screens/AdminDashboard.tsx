import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl,
  Modal,
  TextInput,
  Switch,
  ActivityIndicator,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Types
interface TradingContract {
  contract_id: string;
  exchange: string;
  trading_type: string;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  status: 'pending' | 'active' | 'paused' | 'suspended' | 'delisted';
  leverage_available: number[];
  min_order_size: number;
  max_order_size: number;
  maker_fee: number;
  taker_fee: number;
  created_at: string;
  created_by: string;
}

interface User {
  user_id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'super_admin' | 'admin' | 'moderator' | 'trader' | 'viewer' | 'suspended';
  status: 'active' | 'suspended' | 'banned' | 'pending_verification';
  kyc_status: string;
  kyc_level: number;
  trading_enabled: boolean;
  withdrawal_enabled: boolean;
  deposit_enabled: boolean;
  created_at: string;
  last_login: string;
  permissions: string[];
}

interface SystemStats {
  users: {
    total: number;
    active: number;
    suspended: number;
  };
  contracts: {
    total: number;
    active: number;
    paused: number;
  };
  audit: {
    total_logs: number;
    recent_actions_24h: number;
  };
}

// API Service
class MobileAdminAPIService {
  private baseURL = 'http://localhost:8005'; // Configure for your environment
  private token = ''; // Get from secure storage

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Contract Management
  async createContract(data: any) {
    return this.request('/api/admin/contracts/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async launchContract(contractId: string) {
    return this.request(`/api/admin/contracts/${contractId}/launch`, {
      method: 'POST',
    });
  }

  async pauseContract(contractId: string, reason: string) {
    return this.request(`/api/admin/contracts/${contractId}/pause`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async resumeContract(contractId: string) {
    return this.request(`/api/admin/contracts/${contractId}/resume`, {
      method: 'POST',
    });
  }

  async deleteContract(contractId: string, reason: string) {
    return this.request(`/api/admin/contracts/${contractId}`, {
      method: 'DELETE',
      body: JSON.stringify({ reason }),
    });
  }

  async getContracts(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/contracts?${params}`);
  }

  // User Management
  async createUser(data: any) {
    return this.request('/api/admin/users/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUsers(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/users?${params}`);
  }

  async suspendUser(userId: string, reason: string) {
    return this.request(`/api/admin/users/${userId}/suspend`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async activateUser(userId: string) {
    return this.request(`/api/admin/users/${userId}/activate`, {
      method: 'POST',
    });
  }

  // Emergency Controls
  async emergencyHaltTrading(reason: string) {
    return this.request('/api/admin/emergency/halt-trading', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async emergencyResumeTrading() {
    return this.request('/api/admin/emergency/resume-trading', {
      method: 'POST',
    });
  }

  // Analytics
  async getSystemStats() {
    return this.request('/api/admin/statistics');
  }

  async getAuditLogs(filters: any = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/admin/audit-logs?${params}`);
  }
}

const apiService = new MobileAdminAPIService();

// Main Admin Dashboard Component
export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [contracts, setContracts] = useState<TradingContract[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [createContractModal, setCreateContractModal] = useState(false);
  const [createUserModal, setCreateUserModal] = useState(false);
  const [emergencyModal, setEmergencyModal] = useState(false);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadSystemStats(),
        loadContracts(),
        loadUsers(),
      ]);
      setError(null);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadSystemStats = async () => {
    try {
      const stats = await apiService.getSystemStats();
      setSystemStats(stats);
    } catch (err) {
      console.error('Failed to load system statistics');
    }
  };

  const loadContracts = async () => {
    try {
      const response = await apiService.getContracts();
      setContracts(response.contracts);
    } catch (err) {
      console.error('Failed to load contracts');
    }
  };

  const loadUsers = async () => {
    try {
      const response = await apiService.getUsers();
      setUsers(response.users);
    } catch (err) {
      console.error('Failed to load users');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInitialData();
    setRefreshing(false);
  };

  // Contract Actions
  const handleContractAction = async (action: string, contractId: string, data?: any) => {
    try {
      switch (action) {
        case 'launch':
          await apiService.launchContract(contractId);
          Alert.alert('Success', 'Contract launched successfully');
          break;
        case 'pause':
          await apiService.pauseContract(contractId, data?.reason || 'Admin pause');
          Alert.alert('Success', 'Contract paused successfully');
          break;
        case 'resume':
          await apiService.resumeContract(contractId);
          Alert.alert('Success', 'Contract resumed successfully');
          break;
        case 'delete':
          Alert.alert(
            'Confirm Delete',
            'Are you sure you want to delete this contract?',
            [
              { text: 'Cancel', style: 'cancel' },
              {
                text: 'Delete',
                style: 'destructive',
                onPress: async () => {
                  await apiService.deleteContract(contractId, data?.reason || 'Admin deletion');
                  Alert.alert('Success', 'Contract deleted successfully');
                  await loadContracts();
                },
              },
            ]
          );
          return;
      }
      await loadContracts();
    } catch (err) {
      Alert.alert('Error', `Failed to ${action} contract`);
    }
  };

  // User Actions
  const handleUserAction = async (action: string, userId: string, data?: any) => {
    try {
      switch (action) {
        case 'suspend':
          await apiService.suspendUser(userId, data?.reason || 'Admin suspension');
          Alert.alert('Success', 'User suspended successfully');
          break;
        case 'activate':
          await apiService.activateUser(userId);
          Alert.alert('Success', 'User activated successfully');
          break;
      }
      await loadUsers();
    } catch (err) {
      Alert.alert('Error', `Failed to ${action} user`);
    }
  };

  // Emergency Actions
  const handleEmergencyAction = async (action: string, reason?: string) => {
    try {
      if (action === 'halt') {
        await apiService.emergencyHaltTrading(reason!);
        Alert.alert('Emergency', 'Trading halted system-wide');
      } else if (action === 'resume') {
        await apiService.emergencyResumeTrading();
        Alert.alert('Success', 'Trading resumed');
      }
      await loadSystemStats();
    } catch (err) {
      Alert.alert('Error', `Failed to ${action} trading`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10B981';
      case 'pending':
        return '#F59E0B';
      case 'paused':
        return '#F97316';
      case 'suspended':
      case 'delisted':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab systemStats={systemStats} />;
      case 'contracts':
        return (
          <ContractsTab
            contracts={contracts}
            onAction={handleContractAction}
            onCreatePress={() => setCreateContractModal(true)}
          />
        );
      case 'users':
        return (
          <UsersTab
            users={users}
            onAction={handleUserAction}
            onCreatePress={() => setCreateUserModal(true)}
          />
        );
      case 'emergency':
        return (
          <EmergencyTab
            onEmergencyPress={() => setEmergencyModal(true)}
            onResumePress={() => handleEmergencyAction('resume')}
          />
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading Admin Dashboard...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>TigerEx Admin</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={onRefresh}>
          <Icon name="refresh" size={24} color="#3B82F6" />
        </TouchableOpacity>
      </View>

      {/* Error Alert */}
      {error && (
        <View style={styles.errorContainer}>
          <Icon name="error" size={20} color="#EF4444" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {[
            { key: 'overview', label: 'Overview', icon: 'dashboard' },
            { key: 'contracts', label: 'Contracts', icon: 'assignment' },
            { key: 'users', label: 'Users', icon: 'people' },
            { key: 'emergency', label: 'Emergency', icon: 'warning' },
          ].map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[
                styles.tab,
                activeTab === tab.key && styles.activeTab,
              ]}
              onPress={() => setActiveTab(tab.key)}
            >
              <Icon
                name={tab.icon}
                size={20}
                color={activeTab === tab.key ? '#3B82F6' : '#6B7280'}
              />
              <Text
                style={[
                  styles.tabText,
                  activeTab === tab.key && styles.activeTabText,
                ]}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {renderTabContent()}
      </ScrollView>

      {/* Modals */}
      <CreateContractModal
        visible={createContractModal}
        onClose={() => setCreateContractModal(false)}
        onSuccess={() => {
          setCreateContractModal(false);
          loadContracts();
        }}
      />

      <CreateUserModal
        visible={createUserModal}
        onClose={() => setCreateUserModal(false)}
        onSuccess={() => {
          setCreateUserModal(false);
          loadUsers();
        }}
      />

      <EmergencyModal
        visible={emergencyModal}
        onClose={() => setEmergencyModal(false)}
        onConfirm={(reason) => {
          setEmergencyModal(false);
          handleEmergencyAction('halt', reason);
        }}
      />
    </SafeAreaView>
  );
};

// Overview Tab Component
const OverviewTab: React.FC<{ systemStats: SystemStats | null }> = ({ systemStats }) => {
  if (!systemStats) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="small" color="#3B82F6" />
      </View>
    );
  }

  return (
    <View style={styles.overviewContainer}>
      {/* Stats Cards */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Icon name="people" size={32} color="#3B82F6" />
          <Text style={styles.statNumber}>{systemStats.users.total}</Text>
          <Text style={styles.statLabel}>Total Users</Text>
          <Text style={styles.statSubtext}>
            {systemStats.users.active} active, {systemStats.users.suspended} suspended
          </Text>
        </View>

        <View style={styles.statCard}>
          <Icon name="assignment" size={32} color="#10B981" />
          <Text style={styles.statNumber}>{systemStats.contracts.total}</Text>
          <Text style={styles.statLabel}>Contracts</Text>
          <Text style={styles.statSubtext}>
            {systemStats.contracts.active} active, {systemStats.contracts.paused} paused
          </Text>
        </View>

        <View style={styles.statCard}>
          <Icon name="security" size={32} color="#F59E0B" />
          <Text style={styles.statNumber}>{systemStats.audit.total_logs}</Text>
          <Text style={styles.statLabel}>Audit Logs</Text>
          <Text style={styles.statSubtext}>
            {systemStats.audit.recent_actions_24h} in 24h
          </Text>
        </View>

        <View style={styles.statCard}>
          <Icon name="check-circle" size={32} color="#10B981" />
          <Text style={styles.statNumber}>100%</Text>
          <Text style={styles.statLabel}>System Health</Text>
          <Text style={styles.statSubtext}>All systems operational</Text>
        </View>
      </View>

      {/* System Status */}
      <View style={styles.systemStatus}>
        <Text style={styles.sectionTitle}>System Status</Text>
        {[
          { name: 'Database', status: 'Connected', color: '#10B981' },
          { name: 'Redis Cache', status: 'Connected', color: '#10B981' },
          { name: 'API Gateway', status: 'Healthy', color: '#10B981' },
          { name: 'Trading Engine', status: 'Running', color: '#10B981' },
        ].map((service, index) => (
          <View key={index} style={styles.serviceItem}>
            <Text style={styles.serviceName}>{service.name}</Text>
            <View style={[styles.statusBadge, { backgroundColor: service.color }]}>
              <Text style={styles.statusText}>{service.status}</Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  );
};

// Contracts Tab Component
const ContractsTab: React.FC<{
  contracts: TradingContract[];
  onAction: (action: string, contractId: string, data?: any) => void;
  onCreatePress: () => void;
}> = ({ contracts, onAction, onCreatePress }) => {
  return (
    <View style={styles.tabContent}>
      {/* Header */}
      <View style={styles.tabHeader}>
        <Text style={styles.sectionTitle}>Trading Contracts</Text>
        <TouchableOpacity style={styles.addButton} onPress={onCreatePress}>
          <Icon name="add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* Contracts List */}
      {contracts.map((contract) => (
        <View key={contract.contract_id} style={styles.contractCard}>
          <View style={styles.contractHeader}>
            <Text style={styles.contractSymbol}>{contract.symbol}</Text>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(contract.status) },
              ]}
            >
              <Text style={styles.statusText}>{contract.status.toUpperCase()}</Text>
            </View>
          </View>

          <View style={styles.contractDetails}>
            <Text style={styles.contractDetail}>
              Exchange: {contract.exchange.toUpperCase()}
            </Text>
            <Text style={styles.contractDetail}>
              Type: {contract.trading_type.replace('_', ' ').toUpperCase()}
            </Text>
            <Text style={styles.contractDetail}>
              Fees: {contract.maker_fee}% / {contract.taker_fee}%
            </Text>
          </View>

          <View style={styles.contractActions}>
            {contract.status === 'pending' && (
              <TouchableOpacity
                style={[styles.actionButton, styles.launchButton]}
                onPress={() => onAction('launch', contract.contract_id)}
              >
                <Icon name="play-arrow" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Launch</Text>
              </TouchableOpacity>
            )}

            {contract.status === 'active' && (
              <TouchableOpacity
                style={[styles.actionButton, styles.pauseButton]}
                onPress={() => onAction('pause', contract.contract_id)}
              >
                <Icon name="pause" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Pause</Text>
              </TouchableOpacity>
            )}

            {contract.status === 'paused' && (
              <TouchableOpacity
                style={[styles.actionButton, styles.resumeButton]}
                onPress={() => onAction('resume', contract.contract_id)}
              >
                <Icon name="play-arrow" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Resume</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={[styles.actionButton, styles.deleteButton]}
              onPress={() => onAction('delete', contract.contract_id)}
            >
              <Icon name="delete" size={16} color="#FFFFFF" />
              <Text style={styles.actionButtonText}>Delete</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </View>
  );
};

// Users Tab Component
const UsersTab: React.FC<{
  users: User[];
  onAction: (action: string, userId: string, data?: any) => void;
  onCreatePress: () => void;
}> = ({ users, onAction, onCreatePress }) => {
  return (
    <View style={styles.tabContent}>
      {/* Header */}
      <View style={styles.tabHeader}>
        <Text style={styles.sectionTitle}>User Management</Text>
        <TouchableOpacity style={styles.addButton} onPress={onCreatePress}>
          <Icon name="person-add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* Users List */}
      {users.map((user) => (
        <View key={user.user_id} style={styles.userCard}>
          <View style={styles.userHeader}>
            <View>
              <Text style={styles.username}>{user.username}</Text>
              <Text style={styles.userEmail}>{user.email}</Text>
            </View>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(user.status) },
              ]}
            >
              <Text style={styles.statusText}>{user.status.toUpperCase()}</Text>
            </View>
          </View>

          <View style={styles.userDetails}>
            <Text style={styles.userDetail}>
              Role: {user.role.replace('_', ' ').toUpperCase()}
            </Text>
            <Text style={styles.userDetail}>KYC Level: {user.kyc_level}</Text>
            <View style={styles.userSwitches}>
              <View style={styles.switchItem}>
                <Text style={styles.switchLabel}>Trading</Text>
                <Switch
                  value={user.trading_enabled}
                  onValueChange={(value) =>
                    onAction('update', user.user_id, { trading_enabled: value })
                  }
                />
              </View>
            </View>
          </View>

          <View style={styles.userActions}>
            {user.status === 'active' && (
              <TouchableOpacity
                style={[styles.actionButton, styles.suspendButton]}
                onPress={() => onAction('suspend', user.user_id)}
              >
                <Icon name="block" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Suspend</Text>
              </TouchableOpacity>
            )}

            {user.status === 'suspended' && (
              <TouchableOpacity
                style={[styles.actionButton, styles.activateButton]}
                onPress={() => onAction('activate', user.user_id)}
              >
                <Icon name="check-circle" size={16} color="#FFFFFF" />
                <Text style={styles.actionButtonText}>Activate</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      ))}
    </View>
  );
};

// Emergency Tab Component
const EmergencyTab: React.FC<{
  onEmergencyPress: () => void;
  onResumePress: () => void;
}> = ({ onEmergencyPress, onResumePress }) => {
  return (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>Emergency Controls</Text>
      
      <View style={styles.emergencyContainer}>
        <View style={styles.emergencyCard}>
          <Icon name="warning" size={48} color="#EF4444" />
          <Text style={styles.emergencyTitle}>Emergency Trading Halt</Text>
          <Text style={styles.emergencyDescription}>
            Immediately halt all trading activities system-wide. Use only in emergency situations.
          </Text>
          <TouchableOpacity
            style={styles.emergencyButton}
            onPress={onEmergencyPress}
          >
            <Icon name="stop" size={20} color="#FFFFFF" />
            <Text style={styles.emergencyButtonText}>HALT ALL TRADING</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.emergencyCard}>
          <Icon name="play-arrow" size={48} color="#10B981" />
          <Text style={styles.emergencyTitle}>Resume Trading</Text>
          <Text style={styles.emergencyDescription}>
            Resume normal trading operations for all active users.
          </Text>
          <TouchableOpacity
            style={styles.resumeButton}
            onPress={onResumePress}
          >
            <Icon name="play-arrow" size={20} color="#FFFFFF" />
            <Text style={styles.emergencyButtonText}>RESUME TRADING</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

// Modal Components
const CreateContractModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ visible, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    exchange: '',
    trading_type: '',
    symbol: '',
    base_asset: '',
    quote_asset: '',
    maker_fee: '0.001',
    taker_fee: '0.001',
  });

  const handleSubmit = async () => {
    try {
      await apiService.createContract({
        ...formData,
        maker_fee: parseFloat(formData.maker_fee),
        taker_fee: parseFloat(formData.taker_fee),
      });
      Alert.alert('Success', 'Contract created successfully');
      onSuccess();
    } catch (err) {
      Alert.alert('Error', 'Failed to create contract');
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Create Contract</Text>
          <TouchableOpacity onPress={onClose}>
            <Icon name="close" size={24} color="#6B7280" />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Exchange</Text>
            <Picker
              selectedValue={formData.exchange}
              onValueChange={(value) => setFormData({ ...formData, exchange: value })}
              style={styles.picker}
            >
              <Picker.Item label="Select Exchange" value="" />
              <Picker.Item label="Binance" value="binance" />
              <Picker.Item label="KuCoin" value="kucoin" />
              <Picker.Item label="Bybit" value="bybit" />
              <Picker.Item label="OKX" value="okx" />
              <Picker.Item label="MEXC" value="mexc" />
              <Picker.Item label="Bitget" value="bitget" />
              <Picker.Item label="Bitfinex" value="bitfinex" />
            </Picker>
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Trading Type</Text>
            <Picker
              selectedValue={formData.trading_type}
              onValueChange={(value) => setFormData({ ...formData, trading_type: value })}
              style={styles.picker}
            >
              <Picker.Item label="Select Type" value="" />
              <Picker.Item label="Spot" value="spot" />
              <Picker.Item label="Futures Perpetual" value="futures_perpetual" />
              <Picker.Item label="Futures Cross" value="futures_cross" />
              <Picker.Item label="Margin" value="margin" />
              <Picker.Item label="Options" value="options" />
              <Picker.Item label="Derivatives" value="derivatives" />
              <Picker.Item label="Copy Trading" value="copy_trading" />
              <Picker.Item label="ETF" value="etf" />
            </Picker>
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Symbol</Text>
            <TextInput
              style={styles.textInput}
              value={formData.symbol}
              onChangeText={(text) => setFormData({ ...formData, symbol: text })}
              placeholder="BTC/USDT"
            />
          </View>

          <View style={styles.formRow}>
            <View style={styles.formGroupHalf}>
              <Text style={styles.formLabel}>Base Asset</Text>
              <TextInput
                style={styles.textInput}
                value={formData.base_asset}
                onChangeText={(text) => setFormData({ ...formData, base_asset: text })}
                placeholder="BTC"
              />
            </View>

            <View style={styles.formGroupHalf}>
              <Text style={styles.formLabel}>Quote Asset</Text>
              <TextInput
                style={styles.textInput}
                value={formData.quote_asset}
                onChangeText={(text) => setFormData({ ...formData, quote_asset: text })}
                placeholder="USDT"
              />
            </View>
          </View>

          <View style={styles.formRow}>
            <View style={styles.formGroupHalf}>
              <Text style={styles.formLabel}>Maker Fee (%)</Text>
              <TextInput
                style={styles.textInput}
                value={formData.maker_fee}
                onChangeText={(text) => setFormData({ ...formData, maker_fee: text })}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.formGroupHalf}>
              <Text style={styles.formLabel}>Taker Fee (%)</Text>
              <TextInput
                style={styles.textInput}
                value={formData.taker_fee}
                onChangeText={(text) => setFormData({ ...formData, taker_fee: text })}
                keyboardType="numeric"
              />
            </View>
          </View>

          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
            <Text style={styles.submitButtonText}>Create Contract</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const CreateUserModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ visible, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    role: 'trader',
  });

  const handleSubmit = async () => {
    try {
      await apiService.createUser(formData);
      Alert.alert('Success', 'User created successfully');
      onSuccess();
    } catch (err) {
      Alert.alert('Error', 'Failed to create user');
    }
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Create User</Text>
          <TouchableOpacity onPress={onClose}>
            <Icon name="close" size={24} color="#6B7280" />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Email</Text>
            <TextInput
              style={styles.textInput}
              value={formData.email}
              onChangeText={(text) => setFormData({ ...formData, email: text })}
              placeholder="user@example.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Username</Text>
            <TextInput
              style={styles.textInput}
              value={formData.username}
              onChangeText={(text) => setFormData({ ...formData, username: text })}
              placeholder="username"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Password</Text>
            <TextInput
              style={styles.textInput}
              value={formData.password}
              onChangeText={(text) => setFormData({ ...formData, password: text })}
              placeholder="Password"
              secureTextEntry
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Full Name</Text>
            <TextInput
              style={styles.textInput}
              value={formData.full_name}
              onChangeText={(text) => setFormData({ ...formData, full_name: text })}
              placeholder="Full Name"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.formLabel}>Role</Text>
            <Picker
              selectedValue={formData.role}
              onValueChange={(value) => setFormData({ ...formData, role: value })}
              style={styles.picker}
            >
              <Picker.Item label="Trader" value="trader" />
              <Picker.Item label="Moderator" value="moderator" />
              <Picker.Item label="Admin" value="admin" />
              <Picker.Item label="Viewer" value="viewer" />
            </Picker>
          </View>

          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
            <Text style={styles.submitButtonText}>Create User</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const EmergencyModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => void;
}> = ({ visible, onClose, onConfirm }) => {
  const [reason, setReason] = useState('');

  const handleConfirm = () => {
    if (reason.trim()) {
      onConfirm(reason);
      setReason('');
    } else {
      Alert.alert('Error', 'Please provide a reason for the emergency halt');
    }
  };

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.emergencyModalOverlay}>
        <View style={styles.emergencyModalContainer}>
          <View style={styles.emergencyModalHeader}>
            <Icon name="warning" size={32} color="#EF4444" />
            <Text style={styles.emergencyModalTitle}>Emergency Halt</Text>
          </View>

          <Text style={styles.emergencyModalText}>
            This will immediately halt all trading activities system-wide. Please provide a reason:
          </Text>

          <TextInput
            style={styles.emergencyTextInput}
            value={reason}
            onChangeText={setReason}
            placeholder="Enter reason for emergency halt"
            multiline
          />

          <View style={styles.emergencyModalActions}>
            <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.confirmButton} onPress={handleConfirm}>
              <Text style={styles.confirmButtonText}>CONFIRM HALT</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

// Helper function
const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return '#10B981';
    case 'pending':
      return '#F59E0B';
    case 'paused':
      return '#F97316';
    case 'suspended':
    case 'delisted':
      return '#EF4444';
    default:
      return '#6B7280';
  }
};

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  refreshButton: {
    padding: 8,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginTop: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  errorText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#DC2626',
    flex: 1,
  },
  tabContainer: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 4,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#3B82F6',
  },
  tabText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#6B7280',
  },
  activeTabText: {
    color: '#3B82F6',
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  overviewContainer: {
    padding: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    marginRight: '2%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  statSubtext: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 4,
  },
  systemStatus: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  serviceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  serviceName: {
    fontSize: 14,
    color: '#374151',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  tabContent: {
    padding: 16,
  },
  tabHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  addButton: {
    backgroundColor: '#3B82F6',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  contractCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  contractHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  contractSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  contractDetails: {
    marginBottom: 12,
  },
  contractDetail: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  contractActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    flex: 1,
    justifyContent: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  launchButton: {
    backgroundColor: '#10B981',
  },
  pauseButton: {
    backgroundColor: '#F97316',
  },
  resumeButton: {
    backgroundColor: '#10B981',
  },
  deleteButton: {
    backgroundColor: '#EF4444',
  },
  userCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  userHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  username: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  userDetails: {
    marginBottom: 12,
  },
  userDetail: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  userSwitches: {
    marginTop: 8,
  },
  switchItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  switchLabel: {
    fontSize: 14,
    color: '#374151',
  },
  userActions: {
    flexDirection: 'row',
    gap: 8,
  },
  suspendButton: {
    backgroundColor: '#EF4444',
  },
  activateButton: {
    backgroundColor: '#10B981',
  },
  emergencyContainer: {
    gap: 16,
  },
  emergencyCard: {
    backgroundColor: '#FFFFFF',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  emergencyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 16,
    marginBottom: 8,
  },
  emergencyDescription: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  emergencyButton: {
    backgroundColor: '#EF4444',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  resumeButton: {
    backgroundColor: '#10B981',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emergencyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  formGroup: {
    marginBottom: 16,
  },
  formRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  formGroupHalf: {
    flex: 1,
  },
  formLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: '#111827',
  },
  picker: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
  },
  submitButton: {
    backgroundColor: '#3B82F6',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 24,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  emergencyModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  emergencyModalContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: '100%',
    maxWidth: 400,
  },
  emergencyModalHeader: {
    alignItems: 'center',
    marginBottom: 16,
  },
  emergencyModalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#EF4444',
    marginTop: 8,
  },
  emergencyModalText: {
    fontSize: 16,
    color: '#374151',
    textAlign: 'center',
    marginBottom: 16,
  },
  emergencyTextInput: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: '#111827',
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: 24,
  },
  emergencyModalActions: {
    flexDirection: 'row',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButton: {
    flex: 1,
    backgroundColor: '#EF4444',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default AdminDashboard;