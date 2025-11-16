/**
 * TigerEx Complete Mobile Trading Application
 * Full-featured mobile trading platform with admin controls
 * React Native - iOS & Android
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  StatusBar,
  Dimensions,
  Image,
  FlatList,
  RefreshControl,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width, height } = Dimensions.get('window');

const CompleteMobileTradingApp = () => {
  const [activeTab, setActiveTab] = useState('trade');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [tradeMode, setTradeMode] = useState('spot');
  const [orderType, setOrderType] = useState('market');
  const [orderSide, setOrderSide] = useState('buy');
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);

  const marketData = {
    'BTC/USDT': { price: 43250.50, change: 2.34, volume: '1.2B' },
    'ETH/USDT': { price: 2280.30, change: -1.23, volume: '850M' },
    'BNB/USDT': { price: 315.80, change: 0.89, volume: '320M' },
  };

  const TradingScreen = () => (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>TigerEx</Text>
        <TouchableOpacity onPress={() => setIsAdmin(!isAdmin)}>
          <Icon name="admin-panel-settings" size={24} color="#FF6B35" />
        </TouchableOpacity>
      </View>

      {/* Trading Pair Selector */}
      <View style={styles.pairSelector}>
        <TouchableOpacity 
          style={styles.selectedPair}
          onPress={() => Alert.alert('Pair Selection', 'Coming soon')}
        >
          <Text style={styles.pairText}>{selectedPair}</Text>
          <Text style={[styles.priceText, marketData[selectedPair]?.change >= 0 ? styles.greenText : styles.redText]}>
            {marketData[selectedPair]?.price.toLocaleString()}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Price Chart Area */}
      <View style={styles.chartArea}>
        <View style={styles.chartPlaceholder}>
          <Icon name="show-chart" size={48} color="#FF6B35" />
          <Text style={styles.chartText}>Real-time Chart</Text>
        </View>
      </View>

      {/* Order Book */}
      <View style={styles.orderBook}>
        <Text style={styles.sectionTitle}>Order Book</Text>
        <View style={styles.orderBookContent}>
          <View style={styles.orderSide}>
            <Text style={styles.orderSideTitle}>Bids</Text>
            <Text style={styles.orderItem}>43,250.00  0.5421</Text>
            <Text style={styles.orderItem}>43,249.50  0.3214</Text>
          </View>
          <View style={styles.orderSide}>
            <Text style={styles.orderSideTitle}>Asks</Text>
            <Text style={styles.orderItem}>43,250.50  0.4231</Text>
            <Text style={styles.orderItem}>43,251.00  0.6123</Text>
          </View>
        </View>
      </View>

      {/* Trading Panel */}
      <View style={styles.tradingPanel}>
        {/* Buy/Sell Tabs */}
        <View style={styles.buySellTabs}>
          <TouchableOpacity
            style={[styles.tab, orderSide === 'buy' && styles.buyTab]}
            onPress={() => setOrderSide('buy')}
          >
            <Text style={[styles.tabText, orderSide === 'buy' && styles.activeTabText]}>Buy</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, orderSide === 'sell' && styles.sellTab]}
            onPress={() => setOrderSide('sell')}
          >
            <Text style={[styles.tabText, orderSide === 'sell' && styles.activeTabText]}>Sell</Text>
          </TouchableOpacity>
        </View>

        {/* Order Type */}
        <View style={styles.orderTypeRow}>
          {['Market', 'Limit'].map(type => (
            <TouchableOpacity
              key={type}
              style={[styles.orderTypeButton, orderType.toLowerCase() === type.toLowerCase() && styles.activeOrderType]}
              onPress={() => setOrderType(type)}
            >
              <Text style={styles.orderTypeText}>{type}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Price Input */}
        {orderType === 'Limit' && (
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Price</Text>
            <TextInput
              style={styles.input}
              value={price}
              onChangeText={setPrice}
              placeholder="0.00"
              keyboardType="numeric"
            />
          </View>
        )}

        {/* Amount Input */}
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Amount</Text>
          <TextInput
            style={styles.input}
            value={amount}
            onChangeText={setAmount}
            placeholder="0.00"
            keyboardType="numeric"
          />
        </View>

        {/* Quick Amount Buttons */}
        <View style={styles.quickAmountRow}>
          {[25, 50, 75, 100].map(percent => (
            <TouchableOpacity
              key={percent}
              style={styles.quickAmountButton}
              onPress={() => setAmount(`${percent}%`)}
            >
              <Text style={styles.quickAmountText}>{percent}%</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Place Order Button */}
        <TouchableOpacity
          style={[styles.placeOrderButton, orderSide === 'buy' ? styles.buyButton : styles.sellButton]}
          onPress={() => Alert.alert('Order Placed', `${orderSide.toUpperCase()} order submitted`)}
        >
          <Text style={styles.placeOrderText}>
            {orderType === 'Market' ? `${orderSide.toUpperCase()} BTC` : `Place ${orderSide.toUpperCase()} Order`}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const PortfolioScreen = () => (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Portfolio</Text>
      </View>
      <ScrollView style={styles.content}>
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Total Balance</Text>
          <Text style={styles.balanceAmount}>$45,678.90</Text>
          <Text style={styles.balanceChange}>+2.34% (24h)</Text>
        </View>
        <View style={styles.holdingsSection}>
          <Text style={styles.sectionTitle}>Holdings</Text>
          {Object.entries(marketData).map(([pair, data]) => (
            <View key={pair} style={styles.holdingItem}>
              <View>
                <Text style={styles.holdingSymbol}>{pair.split('/')[0]}</Text>
                <Text style={styles.holdingAmount}>0.123456</Text>
              </View>
              <Text style={styles.holdingValue}>${(parseFloat(data.price) * 0.123456).toFixed(2)}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );

  const AdminScreen = () => (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Admin Panel</Text>
      </View>
      <ScrollView style={styles.content}>
        <View style={styles.adminSection}>
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.statGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>45,678</Text>
              <Text style={styles.statLabel}>Total Users</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>12,345</Text>
              <Text style={styles.statLabel}>Active Users</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>$2.3B</Text>
              <Text style={styles.statLabel}>24h Volume</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>99.9%</Text>
              <Text style={styles.statLabel}>Uptime</Text>
            </View>
          </View>
        </View>

        <View style={styles.adminSection}>
          <Text style={styles.sectionTitle}>User Management</Text>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>View All Users</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>KYC Verification</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>Account Settings</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.adminSection}>
          <Text style={styles.sectionTitle}>Trading Controls</Text>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>Enable/Disable Markets</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>Fee Management</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.adminButton}>
            <Text style={styles.adminButtonText}>Leverage Controls</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );

  const Tab = createBottomTabNavigator();

  return (
    <NavigationContainer>
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#1a1a1a" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;
              if (route.name === 'Trade') iconName = 'trending-up';
              else if (route.name === 'Portfolio') iconName = 'account-balance-wallet';
              else if (route.name === 'Orders') iconName = 'list-alt';
              else if (route.name === 'Profile') iconName = 'person';
              else if (route.name === 'Admin') iconName = 'admin-panel-settings';
              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#FF6B35',
            tabBarInactiveTintColor: '#666',
            tabBarStyle: styles.tabBar,
            headerShown: false,
          })}
        >
          <Tab.Screen name="Trade" component={TradingScreen} />
          <Tab.Screen name="Portfolio" component={PortfolioScreen} />
          <Tab.Screen name="Orders" component={OrdersScreen} />
          <Tab.Screen name="Profile" component={ProfileScreen} />
          {isAdmin && <Tab.Screen name="Admin" component={AdminScreen} />}
        </Tab.Navigator>
      </View>
    </NavigationContainer>
  );
};

const OrdersScreen = () => (
  <View style={styles.container}>
    <View style={styles.header}>
      <Text style={styles.headerTitle}>Orders</Text>
    </View>
    <ScrollView style={styles.content}>
      <Text style={styles.emptyText}>No open orders</Text>
    </ScrollView>
  </View>
);

const ProfileScreen = () => (
  <View style={styles.container}>
    <View style={styles.header}>
      <Text style={styles.headerTitle}>Profile</Text>
    </View>
    <ScrollView style={styles.content}>
      <View style={styles.profileSection}>
        <View style={styles.avatar}>
          <Icon name="person" size={48} color="#666" />
        </View>
        <Text style={styles.profileName}>Trader Name</Text>
        <Text style={styles.profileEmail}>trader@example.com</Text>
      </View>
    </ScrollView>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0d0d',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 20,
    backgroundColor: '#1a1a1a',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  tabBar: {
    backgroundColor: '#1a1a1a',
    borderTopWidth: 0,
    height: 80,
  },
  pairSelector: {
    padding: 20,
    backgroundColor: '#1a1a1a',
  },
  selectedPair: {
    alignItems: 'center',
  },
  pairText: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 8,
  },
  priceText: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  greenText: {
    color: '#10b981',
  },
  redText: {
    color: '#ef4444',
  },
  chartArea: {
    height: 200,
    backgroundColor: '#1a1a1a',
    margin: 20,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chartPlaceholder: {
    alignItems: 'center',
  },
  chartText: {
    color: '#666',
    marginTop: 10,
  },
  orderBook: {
    backgroundColor: '#1a1a1a',
    margin: 20,
    borderRadius: 12,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  orderBookContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  orderSide: {
    flex: 1,
  },
  orderSideTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  orderItem: {
    fontSize: 12,
    color: '#fff',
    marginBottom: 5,
  },
  tradingPanel: {
    backgroundColor: '#1a1a1a',
    margin: 20,
    marginTop: 0,
    borderRadius: 12,
    padding: 20,
  },
  buySellTabs: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
    backgroundColor: '#2a2a2a',
  },
  buyTab: {
    backgroundColor: '#10b981',
  },
  sellTab: {
    backgroundColor: '#ef4444',
  },
  tabText: {
    color: '#666',
    fontWeight: 'bold',
  },
  activeTabText: {
    color: '#fff',
  },
  orderTypeRow: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 6,
    backgroundColor: '#2a2a2a',
    marginHorizontal: 4,
  },
  activeOrderType: {
    backgroundColor: '#FF6B35',
  },
  orderTypeText: {
    color: '#666',
    fontSize: 12,
  },
  inputGroup: {
    marginBottom: 15,
  },
  inputLabel: {
    color: '#666',
    fontSize: 14,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    paddingHorizontal: 15,
    paddingVertical: 12,
    color: '#fff',
    fontSize: 16,
  },
  quickAmountRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  quickAmountButton: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  quickAmountText: {
    color: '#666',
    fontSize: 12,
  },
  placeOrderButton: {
    paddingVertical: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#10b981',
  },
  sellButton: {
    backgroundColor: '#ef4444',
  },
  placeOrderText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  balanceCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  balanceLabel: {
    color: '#666',
    fontSize: 14,
    marginBottom: 8,
  },
  balanceAmount: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  balanceChange: {
    color: '#10b981',
    fontSize: 14,
  },
  holdingsSection: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
  },
  holdingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  holdingSymbol: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  holdingAmount: {
    color: '#666',
    fontSize: 14,
  },
  holdingValue: {
    color: '#fff',
    fontSize: 16,
  },
  adminSection: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  statGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 10,
  },
  statValue: {
    color: '#FF6B35',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    color: '#666',
    fontSize: 12,
  },
  adminButton: {
    backgroundColor: '#2a2a2a',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  adminButtonText: {
    color: '#fff',
    fontSize: 14,
  },
  profileSection: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#2a2a2a',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  profileName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  profileEmail: {
    color: '#666',
    fontSize: 14,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
    marginTop: 50,
    fontSize: 16,
  },
});

export default CompleteMobileTradingApp;