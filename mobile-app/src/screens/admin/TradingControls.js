/**
 * TigerEx Mobile - Trading Controls Screen
 * Complete trading administration and monitoring
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function TradingControls() {
  const [tradingEnabled, setTradingEnabled] = useState(true);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [circuitBreaker, setCircuitBreaker] = useState(false);

  const tradingPairs = [
    {id: '1', pair: 'BTC/USDT', status: 'active', volume: '$125M', orders: 5432},
    {id: '2', pair: 'ETH/USDT', status: 'active', volume: '$89M', orders: 3421},
    {id: '3', pair: 'BNB/USDT', status: 'paused', volume: '$45M', orders: 1234},
  ];

  const handleToggleTrading = (value) => {
    Alert.alert(
      value ? 'Enable Trading' : 'Disable Trading',
      `Are you sure you want to ${value ? 'enable' : 'disable'} all trading?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Confirm',
          onPress: () => {
            setTradingEnabled(value);
            Alert.alert('Success', `Trading ${value ? 'enabled' : 'disabled'}`);
          },
        },
      ]
    );
  };

  const handleMaintenanceMode = (value) => {
    Alert.alert(
      value ? 'Enable Maintenance' : 'Disable Maintenance',
      value
        ? 'This will pause all trading activities'
        : 'This will resume all trading activities',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Confirm',
          onPress: () => {
            setMaintenanceMode(value);
            Alert.alert('Success', `Maintenance mode ${value ? 'enabled' : 'disabled'}`);
          },
        },
      ]
    );
  };

  const ControlCard = ({icon, title, description, value, onValueChange, color}) => (
    <View style={styles.controlCard}>
      <View style={styles.controlLeft}>
        <View style={[styles.controlIcon, {backgroundColor: color + '20'}]}>
          <Icon name={icon} size={28} color={color} />
        </View>
        <View style={styles.controlText}>
          <Text style={styles.controlTitle}>{title}</Text>
          <Text style={styles.controlDescription}>{description}</Text>
        </View>
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{false: '#ccc', true: color}}
      />
    </View>
  );

  const StatCard = ({icon, label, value, color}) => (
    <View style={styles.statCard}>
      <Icon name={icon} size={32} color={color} />
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Trading Controls</Text>
        <TouchableOpacity>
          <Icon name="refresh" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* System Controls */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Controls</Text>
        <ControlCard
          icon="chart-line"
          title="Global Trading"
          description="Enable/disable all trading activities"
          value={tradingEnabled}
          onValueChange={handleToggleTrading}
          color="#4CAF50"
        />
        <ControlCard
          icon="wrench"
          title="Maintenance Mode"
          description="Pause all trading for maintenance"
          value={maintenanceMode}
          onValueChange={handleMaintenanceMode}
          color="#FF9800"
        />
        <ControlCard
          icon="alert-octagon"
          title="Circuit Breaker"
          description="Emergency stop for extreme volatility"
          value={circuitBreaker}
          onValueChange={setCircuitBreaker}
          color="#f44336"
        />
      </View>

      {/* Trading Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Trading Statistics</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <StatCard
            icon="chart-box"
            label="Active Pairs"
            value="156"
            color="#2196F3"
          />
          <StatCard
            icon="clipboard-list"
            label="Total Orders"
            value="12,345"
            color="#4CAF50"
          />
          <StatCard
            icon="cash-multiple"
            label="24h Volume"
            value="$2.5B"
            color="#FF9800"
          />
          <StatCard
            icon="account-group"
            label="Active Traders"
            value="45,231"
            color="#9C27B0"
          />
        </ScrollView>
      </View>

      {/* Trading Pairs Management */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Trading Pairs</Text>
          <TouchableOpacity>
            <Icon name="plus-circle" size={24} color="#4CAF50" />
          </TouchableOpacity>
        </View>
        {tradingPairs.map((pair) => (
          <View key={pair.id} style={styles.pairCard}>
            <View style={styles.pairLeft}>
              <Text style={styles.pairName}>{pair.pair}</Text>
              <View style={styles.pairStats}>
                <View style={styles.pairStat}>
                  <Icon name="chart-line" size={14} color="#666" />
                  <Text style={styles.pairStatText}>{pair.volume}</Text>
                </View>
                <View style={styles.pairStat}>
                  <Icon name="clipboard-list" size={14} color="#666" />
                  <Text style={styles.pairStatText}>{pair.orders} orders</Text>
                </View>
              </View>
            </View>
            <View style={styles.pairRight}>
              <View
                style={[
                  styles.pairStatus,
                  pair.status === 'active'
                    ? styles.statusActive
                    : styles.statusPaused,
                ]}>
                <Text
                  style={[
                    styles.pairStatusText,
                    pair.status === 'active'
                      ? styles.statusActiveText
                      : styles.statusPausedText,
                  ]}>
                  {pair.status}
                </Text>
              </View>
              <TouchableOpacity
                onPress={() =>
                  Alert.alert('Pair Actions', `Manage ${pair.pair}`)
                }>
                <Icon name="dots-vertical" size={24} color="#666" />
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </View>

      {/* Order Management */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Order Management</Text>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="clipboard-list" size={24} color="#2196F3" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Active Orders</Text>
              <Text style={styles.actionSubtitle}>View and manage all orders</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="cancel" size={24} color="#f44336" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Cancel Orders</Text>
              <Text style={styles.actionSubtitle}>Bulk cancel operations</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="history" size={24} color="#FF9800" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Order History</Text>
              <Text style={styles.actionSubtitle}>View completed orders</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
      </View>

      {/* Risk Management */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Risk Management</Text>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="shield-alert" size={24} color="#f44336" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Position Limits</Text>
              <Text style={styles.actionSubtitle}>Configure max positions</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="alert-circle" size={24} color="#FF9800" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Price Alerts</Text>
              <Text style={styles.actionSubtitle}>Manage price thresholds</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard}>
          <View style={styles.actionLeft}>
            <Icon name="chart-bell-curve" size={24} color="#9C27B0" />
            <View style={styles.actionText}>
              <Text style={styles.actionTitle}>Volatility Monitor</Text>
              <Text style={styles.actionSubtitle}>Track market volatility</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#ccc" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    paddingHorizontal: 15,
    marginBottom: 15,
    marginTop: 10,
  },
  controlCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
  },
  controlLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  controlIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  controlText: {
    flex: 1,
  },
  controlTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  controlDescription: {
    fontSize: 12,
    color: '#666',
  },
  statCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginLeft: 15,
    alignItems: 'center',
    minWidth: 120,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  pairCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
  },
  pairLeft: {
    flex: 1,
  },
  pairName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  pairStats: {
    flexDirection: 'row',
    gap: 15,
  },
  pairStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  pairStatText: {
    fontSize: 12,
    color: '#666',
  },
  pairRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  pairStatus: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusActive: {
    backgroundColor: '#e8f5e9',
  },
  statusPaused: {
    backgroundColor: '#fff3e0',
  },
  pairStatusText: {
    fontSize: 11,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  statusActiveText: {
    color: '#4CAF50',
  },
  statusPausedText: {
    color: '#FF9800',
  },
  actionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
  },
  actionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  actionText: {
    marginLeft: 15,
    flex: 1,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 3,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#666',
  },
});