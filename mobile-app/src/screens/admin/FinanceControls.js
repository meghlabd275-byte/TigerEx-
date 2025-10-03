/**
 * TigerEx Mobile - Finance Controls Screen
 * Complete financial administration and monitoring
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function FinanceControls() {
  const [selectedTab, setSelectedTab] = useState('overview');

  const financialMetrics = {
    totalBalance: '$125,450,000',
    totalDeposits: '$89,230,000',
    totalWithdrawals: '$45,120,000',
    pendingWithdrawals: '$2,340,000',
    dailyVolume: '$12,500,000',
    fees24h: '$125,000',
  };

  const pendingWithdrawals = [
    {
      id: '1',
      user: 'john@example.com',
      amount: '$50,000',
      asset: 'USDT',
      status: 'pending',
      time: '2h ago',
    },
    {
      id: '2',
      user: 'jane@example.com',
      amount: '$25,000',
      asset: 'BTC',
      status: 'pending',
      time: '4h ago',
    },
    {
      id: '3',
      user: 'bob@example.com',
      amount: '$10,000',
      asset: 'ETH',
      status: 'reviewing',
      time: '6h ago',
    },
  ];

  const handleApproveWithdrawal = (withdrawal) => {
    Alert.alert(
      'Approve Withdrawal',
      `Approve ${withdrawal.amount} ${withdrawal.asset} for ${withdrawal.user}?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Approve',
          onPress: () => Alert.alert('Success', 'Withdrawal approved'),
        },
      ]
    );
  };

  const handleRejectWithdrawal = (withdrawal) => {
    Alert.alert(
      'Reject Withdrawal',
      `Reject ${withdrawal.amount} ${withdrawal.asset} for ${withdrawal.user}?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reject',
          style: 'destructive',
          onPress: () => Alert.alert('Success', 'Withdrawal rejected'),
        },
      ]
    );
  };

  const MetricCard = ({icon, label, value, change, color}) => (
    <View style={styles.metricCard}>
      <View style={[styles.metricIcon, {backgroundColor: color + '20'}]}>
        <Icon name={icon} size={28} color={color} />
      </View>
      <View style={styles.metricContent}>
        <Text style={styles.metricLabel}>{label}</Text>
        <Text style={styles.metricValue}>{value}</Text>
        {change && (
          <Text
            style={[
              styles.metricChange,
              {color: change.startsWith('+') ? '#4CAF50' : '#f44336'},
            ]}>
            {change}
          </Text>
        )}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Finance Controls</Text>
        <TouchableOpacity>
          <Icon name="download" size={24} color="#333" />
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        {[
          {key: 'overview', label: 'Overview'},
          {key: 'deposits', label: 'Deposits'},
          {key: 'withdrawals', label: 'Withdrawals'},
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[
              styles.tab,
              selectedTab === tab.key && styles.tabActive,
            ]}
            onPress={() => setSelectedTab(tab.key)}>
            <Text
              style={[
                styles.tabText,
                selectedTab === tab.key && styles.tabTextActive,
              ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView style={styles.content}>
        {/* Financial Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Financial Overview</Text>
          <MetricCard
            icon="wallet"
            label="Total Balance"
            value={financialMetrics.totalBalance}
            change="+5.2%"
            color="#4CAF50"
          />
          <MetricCard
            icon="arrow-down-bold"
            label="Total Deposits (24h)"
            value={financialMetrics.totalDeposits}
            change="+12.3%"
            color="#2196F3"
          />
          <MetricCard
            icon="arrow-up-bold"
            label="Total Withdrawals (24h)"
            value={financialMetrics.totalWithdrawals}
            change="+8.1%"
            color="#FF9800"
          />
          <MetricCard
            icon="clock-alert"
            label="Pending Withdrawals"
            value={financialMetrics.pendingWithdrawals}
            color="#f44336"
          />
          <MetricCard
            icon="chart-line"
            label="Daily Volume"
            value={financialMetrics.dailyVolume}
            change="+15.7%"
            color="#9C27B0"
          />
          <MetricCard
            icon="cash-multiple"
            label="Fees Collected (24h)"
            value={financialMetrics.fees24h}
            change="+10.5%"
            color="#00BCD4"
          />
        </View>

        {/* Pending Withdrawals */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Pending Withdrawals</Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{pendingWithdrawals.length}</Text>
            </View>
          </View>
          {pendingWithdrawals.map((withdrawal) => (
            <View key={withdrawal.id} style={styles.withdrawalCard}>
              <View style={styles.withdrawalHeader}>
                <View style={styles.withdrawalLeft}>
                  <Icon name="account-circle" size={40} color="#4CAF50" />
                  <View style={styles.withdrawalInfo}>
                    <Text style={styles.withdrawalUser}>{withdrawal.user}</Text>
                    <Text style={styles.withdrawalTime}>{withdrawal.time}</Text>
                  </View>
                </View>
                <View style={styles.withdrawalRight}>
                  <Text style={styles.withdrawalAmount}>{withdrawal.amount}</Text>
                  <Text style={styles.withdrawalAsset}>{withdrawal.asset}</Text>
                </View>
              </View>
              <View style={styles.withdrawalActions}>
                <TouchableOpacity
                  style={[styles.actionButton, styles.approveButton]}
                  onPress={() => handleApproveWithdrawal(withdrawal)}>
                  <Icon name="check" size={18} color="#fff" />
                  <Text style={styles.actionButtonText}>Approve</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.actionButton, styles.rejectButton]}
                  onPress={() => handleRejectWithdrawal(withdrawal)}>
                  <Icon name="close" size={18} color="#fff" />
                  <Text style={styles.actionButtonText}>Reject</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.actionButton, styles.viewButton]}
                  onPress={() => Alert.alert('Details', 'View withdrawal details')}>
                  <Icon name="eye" size={18} color="#2196F3" />
                  <Text style={[styles.actionButtonText, {color: '#2196F3'}]}>
                    View
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <TouchableOpacity style={styles.quickActionCard}>
            <View style={styles.quickActionLeft}>
              <Icon name="bank" size={24} color="#2196F3" />
              <View style={styles.quickActionText}>
                <Text style={styles.quickActionTitle}>Bank Accounts</Text>
                <Text style={styles.quickActionSubtitle}>
                  Manage bank connections
                </Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#ccc" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickActionCard}>
            <View style={styles.quickActionLeft}>
              <Icon name="cash-refund" size={24} color="#4CAF50" />
              <View style={styles.quickActionText}>
                <Text style={styles.quickActionTitle}>Refunds</Text>
                <Text style={styles.quickActionSubtitle}>Process refunds</Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#ccc" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickActionCard}>
            <View style={styles.quickActionLeft}>
              <Icon name="file-document" size={24} color="#FF9800" />
              <View style={styles.quickActionText}>
                <Text style={styles.quickActionTitle}>Financial Reports</Text>
                <Text style={styles.quickActionSubtitle}>
                  Generate and export reports
                </Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#ccc" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.quickActionCard}>
            <View style={styles.quickActionLeft}>
              <Icon name="shield-check" size={24} color="#9C27B0" />
              <View style={styles.quickActionText}>
                <Text style={styles.quickActionTitle}>AML Monitoring</Text>
                <Text style={styles.quickActionSubtitle}>
                  Anti-money laundering checks
                </Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#ccc" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
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
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    paddingHorizontal: 15,
    paddingTop: 10,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
  },
  tabTextActive: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    marginBottom: 15,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    paddingHorizontal: 15,
    marginBottom: 15,
    marginTop: 10,
  },
  badge: {
    backgroundColor: '#f44336',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginLeft: 10,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  metricCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  metricIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  metricContent: {
    flex: 1,
  },
  metricLabel: {
    fontSize: 13,
    color: '#666',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 3,
  },
  metricChange: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  withdrawalCard: {
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
  },
  withdrawalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  withdrawalLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  withdrawalInfo: {
    marginLeft: 12,
    flex: 1,
  },
  withdrawalUser: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 3,
  },
  withdrawalTime: {
    fontSize: 12,
    color: '#999',
  },
  withdrawalRight: {
    alignItems: 'flex-end',
  },
  withdrawalAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 3,
  },
  withdrawalAsset: {
    fontSize: 12,
    color: '#666',
  },
  withdrawalActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 8,
    gap: 5,
  },
  approveButton: {
    backgroundColor: '#4CAF50',
  },
  rejectButton: {
    backgroundColor: '#f44336',
  },
  viewButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  actionButtonText: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#fff',
  },
  quickActionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 15,
    marginHorizontal: 15,
    marginBottom: 10,
    borderRadius: 12,
  },
  quickActionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  quickActionText: {
    marginLeft: 15,
    flex: 1,
  },
  quickActionTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 3,
  },
  quickActionSubtitle: {
    fontSize: 12,
    color: '#666',
  },
});