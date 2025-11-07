/**
 * Trading Admin Panel for Mobile
 * Complete admin controls for all trading types
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  Switch,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
} from 'react-native-chart-kit';
import { Card, Button, Chip, Divider } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useDispatch, useSelector } from 'react-redux';

const { width } = Dimensions.get('window');

interface TradingType {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'suspended';
  enabled: boolean;
  volume24h: number;
  orders24h: number;
  users: number;
  errors: number;
}

interface AdminAction {
  id: string;
  action: string;
  tradingType: string;
  reason: string;
  timestamp: string;
}

const TradingAdminPanel: React.FC = () => {
  const [tradingTypes, setTradingTypes] = useState<TradingType[]>([]);
  const [adminActions, setAdminActions] = useState<AdminAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedType, setSelectedType] = useState<TradingType | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [actionReason, setActionReason] = useState('');

  // Mock data
  useEffect(() => {
    const mockData: TradingType[] = [
      {
        id: 'spot',
        name: 'Spot Trading',
        status: 'active',
        enabled: true,
        volume24h: 1250000000,
        orders24h: 45000,
        users: 125000,
        errors: 12,
      },
      {
        id: 'future_perpetual',
        name: 'Future Perpetual',
        status: 'active',
        enabled: true,
        volume24h: 2500000000,
        orders24h: 67000,
        users: 45000,
        errors: 8,
      },
      {
        id: 'future_cross',
        name: 'Future Cross',
        status: 'paused',
        enabled: true,
        volume24h: 850000000,
        orders24h: 23000,
        users: 22000,
        errors: 5,
      },
      {
        id: 'margin',
        name: 'Margin Trading',
        status: 'active',
        enabled: true,
        volume24h: 420000000,
        orders24h: 15000,
        users: 18000,
        errors: 3,
      },
      {
        id: 'grid',
        name: 'Grid Trading',
        status: 'active',
        enabled: true,
        volume24h: 180000000,
        orders24h: 8500,
        users: 8500,
        errors: 2,
      },
      {
        id: 'copy',
        name: 'Copy Trading',
        status: 'active',
        enabled: true,
        volume24h: 95000000,
        orders24h: 4200,
        users: 12000,
        errors: 1,
      },
      {
        id: 'option',
        name: 'Option Trading',
        status: 'suspended',
        enabled: false,
        volume24h: 0,
        orders24h: 0,
        users: 0,
        errors: 0,
      },
    ];

    setTradingTypes(mockData);
  }, []);

  const handleTradingControl = async (
    tradingType: TradingType,
    action: 'pause' | 'resume' | 'suspend' | 'emergency_stop'
  ) => {
    if (!actionReason.trim()) {
      Alert.alert('Error', 'Please provide a reason for this action');
      return;
    }

    setIsLoading(true);
    try {
      // API call would go here
      setTradingTypes(prev =>
        prev.map(tt =>
          tt.id === tradingType.id
            ? { ...tt, status: action === 'resume' ? 'active' : action === 'pause' ? 'paused' : action }
            : tt
        )
      );

      // Add to action log
      const newAction: AdminAction = {
        id: Date.now().toString(),
        action,
        tradingType: tradingType.id,
        reason: actionReason,
        timestamp: new Date().toISOString(),
      };
      setAdminActions(prev => [newAction, ...prev.slice(0, 49)]);

      Alert.alert('Success', `${tradingType.name} ${action}d successfully`);
      setModalVisible(false);
      setActionReason('');
    } catch (error) {
      Alert.alert('Error', `Failed to ${action} ${tradingType.name}`);
    }
    setIsLoading(false);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    // Simulate data refresh
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#10b981';
      case 'paused': return '#f59e0b';
      case 'suspended': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return 'play-arrow';
      case 'paused': return 'pause';
      case 'suspended': return 'stop';
      default: return 'help';
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const renderTradingTypeCard = (type: TradingType) => (
    <Card key={type.id} style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.cardHeaderLeft}>
          <Text style={styles.cardTitle}>{type.name}</Text>
          <Chip
            style={[styles.statusChip, { backgroundColor: getStatusColor(type.status) }]}
            textStyle={styles.statusChipText}
          >
            {type.status.toUpperCase()}
          </Chip>
        </View>
        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => {
            setSelectedType(type);
            setModalVisible(true);
          }}
        >
          <Icon name="more-vert" size={24} color="#6b7280" />
        </TouchableOpacity>
      </View>

      <Divider style={styles.divider} />

      <View style={styles.metricsGrid}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Volume 24h</Text>
          <Text style={styles.metricValue}>${formatNumber(type.volume24h)}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Orders 24h</Text>
          <Text style={styles.metricValue}>{type.orders24h.toLocaleString()}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Users</Text>
          <Text style={styles.metricValue}>{formatNumber(type.users)}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Errors</Text>
          <Text style={[styles.metricValue, { color: type.errors > 5 ? '#ef4444' : '#10b981' }]}>
            {type.errors}
          </Text>
        </View>
      </View>

      <View style={styles.cardFooter}>
        <View style={styles.switchContainer}>
          <Text style={styles.switchLabel}>Enabled</Text>
          <Switch
            value={type.enabled}
            onValueChange={(value) => {
              setTradingTypes(prev =>
                prev.map(tt =>
                  tt.id === type.id ? { ...tt, enabled: value } : tt
                )
              );
            }}
          />
        </View>
        <View style={styles.statusIndicator}>
          <Icon
            name={getStatusIcon(type.status)}
            size={16}
            color={getStatusColor(type.status)}
          />
          <Text style={[styles.statusText, { color: getStatusColor(type.status) }]}>
            {type.status.replace('_', ' ')}
          </Text>
        </View>
      </View>
    </Card>
  );

  const renderOverviewStats = () => {
    const totalVolume = tradingTypes.reduce((sum, tt) => sum + tt.volume24h, 0);
    const totalOrders = tradingTypes.reduce((sum, tt) => sum + tt.orders24h, 0);
    const totalUsers = tradingTypes.reduce((sum, tt) => sum + tt.users, 0);
    const totalErrors = tradingTypes.reduce((sum, tt) => sum + tt.errors, 0);
    const activeTypes = tradingTypes.filter(tt => tt.status === 'active').length;

    return (
      <View style={styles.overviewContainer}>
        <Card style={styles.overviewCard}>
          <Text style={styles.overviewTitle}>System Overview</Text>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewItem}>
              <Icon name="trending-up" size={24} color="#3b82f6" />
              <Text style={styles.overviewValue}>${formatNumber(totalVolume)}</Text>
              <Text style={styles.overviewLabel}>Total Volume</Text>
            </View>
            <View style={styles.overviewItem}>
              <Icon name="shopping-cart" size={24} color="#10b981" />
              <Text style={styles.overviewValue}>{formatNumber(totalOrders)}</Text>
              <Text style={styles.overviewLabel}>Total Orders</Text>
            </View>
            <View style={styles.overviewItem}>
              <Icon name="people" size={24} color="#f59e0b" />
              <Text style={styles.overviewValue}>{formatNumber(totalUsers)}</Text>
              <Text style={styles.overviewLabel}>Total Users</Text>
            </View>
            <View style={styles.overviewItem}>
              <Icon name="check-circle" size={24} color="#8b5cf6" />
              <Text style={styles.overviewValue}>{activeTypes}/{tradingTypes.length}</Text>
              <Text style={styles.overviewLabel}>Active Types</Text>
            </View>
          </View>
        </Card>
      </View>
    );
  };

  const renderActionModal = () => (
    <Modal
      visible={modalVisible}
      transparent
      animationType="slide"
      onRequestClose={() => setModalVisible(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{selectedType?.name}</Text>
            <TouchableOpacity onPress={() => setModalVisible(false)}>
              <Icon name="close" size={24} color="#6b7280" />
            </TouchableOpacity>
          </View>

          <Text style={styles.modalSubtitle}>Admin Actions</Text>

          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Action Reason</Text>
            <TextInput
              style={styles.textInput}
              value={actionReason}
              onChangeText={setActionReason}
              placeholder="Enter reason for this action..."
              multiline
              numberOfLines={3}
            />
          </View>

          <View style={styles.actionButtons}>
            {selectedType?.status === 'active' ? (
              <Button
                mode="outlined"
                onPress={() => handleTradingControl(selectedType, 'pause')}
                disabled={isLoading}
                style={styles.actionButton}
              >
                {isLoading ? <ActivityIndicator size="small" /> : <Icon name="pause" size={18} color="#f59e0b" />}
                <Text style={styles.actionButtonText}>Pause Trading</Text>
              </Button>
            ) : (
              <Button
                mode="contained"
                onPress={() => handleTradingControl(selectedType, 'resume')}
                disabled={isLoading}
                style={styles.actionButton}
              >
                {isLoading ? <ActivityIndicator size="small" /> : <Icon name="play-arrow" size={18} color="white" />}
                <Text style={styles.actionButtonText}>Resume Trading</Text>
              </Button>
            )}

            <Button
              mode="contained-tonal"
              onPress={() => handleTradingControl(selectedType, 'suspend')}
              disabled={isLoading}
              style={[styles.actionButton, { backgroundColor: '#f59e0b' }]}
            >
              {isLoading ? <ActivityIndicator size="small" /> : <Icon name="block" size={18} color="white" />}
              <Text style={styles.actionButtonText}>Suspend</Text>
            </Button>

            <Button
              mode="contained"
              onPress={() => handleTradingControl(selectedType, 'emergency_stop')}
              disabled={isLoading}
              style={[styles.actionButton, { backgroundColor: '#ef4444' }]}
            >
              {isLoading ? <ActivityIndicator size="small" /> : <Icon name="dangerous" size={18} color="white" />}
              <Text style={styles.actionButtonText}>Emergency Stop</Text>
            </Button>
          </View>
        </View>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Trading Admin</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={onRefresh}>
          {refreshing ? (
            <ActivityIndicator size="small" color="#3b82f6" />
          ) : (
            <Icon name="refresh" size={24} color="#3b82f6" />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {renderOverviewStats()}

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Trading Types</Text>
          <Text style={styles.sectionSubtitle}>
            {tradingTypes.filter(tt => tt.status === 'active').length} of {tradingTypes.length} active
          </Text>
        </View>

        {tradingTypes.map(renderTradingTypeCard)}

        {adminActions.length > 0 && (
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Actions</Text>
          </View>
        )}

        {adminActions.slice(0, 5).map((action) => (
          <Card key={action.id} style={styles.actionCard}>
            <View style={styles.actionItem}>
              <View style={styles.actionItemLeft}>
                <Text style={styles.actionTitle}>{action.action.replace('_', ' ').toUpperCase()}</Text>
                <Text style={styles.actionSubtitle}>{action.tradingType}</Text>
                <Text style={styles.actionReason}>{action.reason}</Text>
              </View>
              <View style={styles.actionItemRight}>
                <Text style={styles.actionTime}>
                  {new Date(action.timestamp).toLocaleTimeString()}
                </Text>
                <Icon name="check-circle" size={16} color="#10b981" />
              </View>
            </View>
          </Card>
        ))}
      </ScrollView>

      {renderActionModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  refreshButton: {
    padding: 8,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  overviewContainer: {
    marginBottom: 24,
  },
  overviewCard: {
    padding: 16,
  },
  overviewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  overviewItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 16,
  },
  overviewValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 4,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  sectionHeader: {
    marginBottom: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  card: {
    marginBottom: 16,
    backgroundColor: 'white',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  cardHeaderLeft: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8,
  },
  statusChip: {
    alignSelf: 'flex-start',
  },
  statusChipText: {
    color: 'white',
    fontSize: 10,
  },
  menuButton: {
    padding: 4,
  },
  divider: {
    marginHorizontal: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  metricItem: {
    width: '50%',
    marginBottom: 12,
  },
  metricLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 2,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  switchLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginRight: 8,
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 12,
    marginLeft: 4,
  },
  actionCard: {
    marginBottom: 8,
    backgroundColor: 'white',
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 12,
  },
  actionItemLeft: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 2,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#3b82f6',
    marginBottom: 2,
  },
  actionReason: {
    fontSize: 12,
    color: '#6b7280',
  },
  actionItemRight: {
    alignItems: 'flex-end',
  },
  actionTime: {
    fontSize: 10,
    color: '#6b7280',
    marginBottom: 2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 12,
    padding: 20,
    width: width - 40,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  modalSubtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 20,
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: 'medium',
    color: '#374151',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    textAlignVertical: 'top',
  },
  actionButtons: {
    gap: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  actionButtonText: {
    color: 'white',
    fontWeight: 'medium',
    marginLeft: 8,
  },
});

export default TradingAdminPanel;