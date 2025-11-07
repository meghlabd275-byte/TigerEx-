/**
 * TigerEx Enhanced Mobile Application
 * Complete cryptocurrency exchange mobile app with full admin controls
 */

import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Alert,
  Modal,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Image,
  Share,
  Linking
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { BlurView } from 'expo-blur';

const { width, height } = Dimensions.get('window');

const EnhancedMobileApp = () => {
  const [user, setUser] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [selectedCrypto, setSelectedCrypto] = useState(null);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [priceData, setPriceData] = useState([]);
  const [portfolioData, setPortfolioData] = useState([]);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [marketData, setMarketData] = useState([]);
  const [orders, setOrders] = useState([]);
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [tradeType, setTradeType] = useState('buy');
  const [tradeAmount, setTradeAmount] = useState('');
  const [tradePrice, setTradePrice] = useState('');

  useEffect(() => {
    checkLoginStatus();
    loadMarketData();
    loadPortfolioData();
  }, []);

  const checkLoginStatus = async () => {
    try {
      const userData = await AsyncStorage.getItem('user');
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsLoggedIn(true);
        if (parsedUser.is_admin || parsedUser.is_superadmin) {
          setShowAdminPanel(true);
        }
      }
    } catch (error) {
      console.error('Error checking login status:', error);
    }
  };

  const loadMarketData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      const mockMarketData = [
        { id: '1', symbol: 'BTC/USDT', price: 43567.89, change: 2.34, volume: 1234567890 },
        { id: '2', symbol: 'ETH/USDT', price: 2234.56, change: -1.23, volume: 987654321 },
        { id: '3', symbol: 'BNB/USDT', price: 312.45, change: 0.87, volume: 456789012 },
        { id: '4', symbol: 'SOL/USDT', price: 98.76, change: 5.43, volume: 234567890 },
        { id: '5', symbol: 'ADA/USDT', price: 0.543, change: -2.15, volume: 123456789 },
      ];
      setMarketData(mockMarketData);
      
      // Generate price chart data
      const chartData = Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        price: 43000 + Math.random() * 1000,
        volume: Math.random() * 1000000
      }));
      setPriceData(chartData);
    } catch (error) {
      Alert.alert('Error', 'Failed to load market data');
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolioData = async () => {
    try {
      // Simulate API call
      const mockPortfolio = [
        { id: '1', symbol: 'BTC', balance: 0.5, value: 21783.95, change: 2.34 },
        { id: '2', symbol: 'ETH', balance: 2.5, value: 5586.40, change: -1.23 },
        { id: '3', symbol: 'USDT', balance: 1000, value: 1000, change: 0 },
      ];
      setPortfolioData(mockPortfolio);
      
      const mockTransactions = [
        { id: '1', type: 'buy', symbol: 'BTC/USDT', amount: 0.1, price: 43567.89, time: '2025-01-07 14:30', status: 'completed' },
        { id: '2', type: 'sell', symbol: 'ETH/USDT', amount: 0.5, price: 2234.56, time: '2025-01-07 13:15', status: 'completed' },
        { id: '3', type: 'buy', symbol: 'BNB/USDT', amount: 2, price: 312.45, time: '2025-01-07 12:00', status: 'pending' },
      ];
      setRecentTransactions(mockTransactions);
    } catch (error) {
      console.error('Error loading portfolio data:', error);
    }
  };

  const handleLogin = async (email, password) => {
    setLoading(true);
    try {
      // Simulate API call
      const mockUser = {
        id: 1,
        email: email,
        username: 'trader',
        full_name: 'John Trader',
        is_admin: true,
        is_superadmin: false,
        kyc_status: 'approved',
        balance: 50000
      };
      
      await AsyncStorage.setItem('user', JSON.stringify(mockUser));
      setUser(mockUser);
      setIsLoggedIn(true);
      if (mockUser.is_admin || mockUser.is_superadmin) {
        setShowAdminPanel(true);
      }
      
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      Alert.alert('Error', 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = async () => {
    if (!tradeAmount || !selectedCrypto) {
      Alert.alert('Error', 'Please enter amount and select cryptocurrency');
      return;
    }
    
    setLoading(true);
    try {
      // Simulate API call
      const newOrder = {
        id: Date.now().toString(),
        type: tradeType,
        symbol: selectedCrypto.symbol,
        amount: parseFloat(tradeAmount),
        price: parseFloat(tradePrice) || selectedCrypto.price,
        time: new Date().toLocaleString(),
        status: 'pending'
      };
      
      setOrders([newOrder, ...orders]);
      setShowTradeModal(false);
      setTradeAmount('');
      setTradePrice('');
      
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      Alert.alert('Success', `${tradeType === 'buy' ? 'Buy' : 'Sell'} order placed successfully`);
    } catch (error) {
      Alert.alert('Error', 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadMarketData();
    await loadPortfolioData();
    setRefreshing(false);
  };

  const renderLoginScreen = () => (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#4A90E2', '#357ABD']} style={styles.gradient}>
        <View style={styles.loginContainer}>
          <Image source={require('./assets/logo.png')} style={styles.logo} />
          <Text style={styles.title}>TigerEx</Text>
          <Text style={styles.subtitle}>Professional Cryptocurrency Exchange</Text>
          
          <View style={styles.formContainer}>
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor="#999"
              autoCapitalize="none"
              keyboardType="email-address"
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor="#999"
              secureTextEntry
            />
            
            <TouchableOpacity
              style={styles.loginButton}
              onPress={() => handleLogin('admin@tigerex.com', 'password')}
            >
              <Text style={styles.loginButtonText}>Sign In</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.forgotPassword}>
              <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
            </TouchableOpacity>
          </View>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );

  const renderMainApp = () => (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.welcomeText}>Welcome back,</Text>
          <Text style={styles.userName}>{user?.full_name}</Text>
        </View>
        <View style={styles.headerButtons}>
          <TouchableOpacity style={styles.headerButton} onPress={() => Share.share({
            message: 'Check out TigerEx - Professional Cryptocurrency Exchange',
            url: 'https://tigerex.com'
          })}>
            <Text style={styles.headerButtonText}>Share</Text>
          </TouchableOpacity>
          {(user?.is_admin || user?.is_superadmin) && (
            <TouchableOpacity 
              style={[styles.headerButton, styles.adminButton]} 
              onPress={() => setActiveTab('admin')}
            >
              <Text style={styles.headerButtonText}>Admin</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {activeTab === 'portfolio' && renderPortfolio()}
      {activeTab === 'markets' && renderMarkets()}
      {activeTab === 'trade' && renderTrade()}
      {activeTab === 'orders' && renderOrders()}
      {activeTab === 'admin' && renderAdminPanel()}

      <View style={styles.bottomNav}>
        {['portfolio', 'markets', 'trade', 'orders', 'admin'].filter(tab => 
          tab !== 'admin' || showAdminPanel
        ).map(tab => (
          <TouchableOpacity
            key={tab}
            style={[styles.navItem, activeTab === tab && styles.navItemActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.navText, activeTab === tab && styles.navTextActive]}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );

  const renderPortfolio = () => (
    <ScrollView
      style={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.portfolioHeader}>
        <Text style={styles.portfolioTitle}>Total Balance</Text>
        <Text style={styles.portfolioValue}>${(portfolioData.reduce((sum, item) => sum + item.value, 0)).toLocaleString()}</Text>
        <Text style={styles.portfolioChange}>+5.67% (24h)</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Assets</Text>
        {portfolioData.map(asset => (
          <TouchableOpacity
            key={asset.id}
            style={styles.assetItem}
            onPress={() => setSelectedCrypto(asset)}
          >
            <View style={styles.assetInfo}>
              <Text style={styles.assetSymbol}>{asset.symbol}</Text>
              <Text style={styles.assetBalance}>{asset.balance}</Text>
            </View>
            <View style={styles.assetValue}>
              <Text style={styles.assetPrice}>${asset.value.toLocaleString()}</Text>
              <Text style={[styles.assetChange, asset.change >= 0 ? styles.positive : styles.negative]}>
                {asset.change >= 0 ? '+' : ''}{asset.change}%
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Transactions</Text>
        {recentTransactions.map(transaction => (
          <View key={transaction.id} style={styles.transactionItem}>
            <View style={styles.transactionInfo}>
              <Text style={styles.transactionType}>{transaction.type.toUpperCase()}</Text>
              <Text style={styles.transactionSymbol}>{transaction.symbol}</Text>
              <Text style={styles.transactionTime}>{transaction.time}</Text>
            </View>
            <View style={styles.transactionAmount}>
              <Text style={styles.transactionValue}>{transaction.amount}</Text>
              <View style={[
                styles.statusBadge, 
                transaction.status === 'completed' ? styles.statusCompleted : styles.statusPending
              ]}>
                <Text style={styles.statusText}>{transaction.status}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>

      <View style={styles.chartSection}>
        <Text style={styles.sectionTitle}>Portfolio Performance</Text>
        <View style={styles.chartContainer}>
          <LineChart
            width={width - 40}
            height={200}
            data={priceData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="#4A90E2" strokeWidth={2} />
          </LineChart>
        </View>
      </View>
    </ScrollView>
  );

  const renderMarkets = () => (
    <ScrollView
      style={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.searchSection}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search markets..."
          placeholderTextColor="#999"
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Top Markets</Text>
        {marketData.map(market => (
          <TouchableOpacity
            key={market.id}
            style={styles.marketItem}
            onPress={() => {
              setSelectedCrypto(market);
              setActiveTab('trade');
            }}
          >
            <View style={styles.marketInfo}>
              <Text style={styles.marketSymbol}>{market.symbol}</Text>
              <Text style={styles.marketVolume}>Vol: ${(market.volume / 1000000).toFixed(2)}M</Text>
            </View>
            <View style={styles.marketPrice}>
              <Text style={styles.price}>${market.price.toLocaleString()}</Text>
              <Text style={[styles.change, market.change >= 0 ? styles.positive : styles.negative]}>
                {market.change >= 0 ? '+' : ''}{market.change}%
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Market Overview</Text>
        <View style={styles.chartContainer}>
          <BarChart
            width={width - 40}
            height={200}
            data={marketData.slice(0, 5)}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="change" fill="#4A90E2" />
          </BarChart>
        </View>
      </View>
    </ScrollView>
  );

  const renderTrade = () => (
    <View style={styles.content}>
      {selectedCrypto ? (
        <View style={styles.tradeContainer}>
          <View style={styles.selectedCrypto}>
            <Text style={styles.selectedSymbol}>{selectedCrypto.symbol}</Text>
            <Text style={styles.selectedPrice}>${selectedCrypto.price.toLocaleString()}</Text>
            <Text style={[styles.selectedChange, selectedCrypto.change >= 0 ? styles.positive : styles.negative]}>
              {selectedCrypto.change >= 0 ? '+' : ''}{selectedCrypto.change}%
            </Text>
          </View>

          <View style={styles.tradeTypeSelector}>
            <TouchableOpacity
              style={[styles.tradeTypeButton, tradeType === 'buy' && styles.tradeTypeButtonActive]}
              onPress={() => setTradeType('buy')}
            >
              <Text style={[styles.tradeTypeText, tradeType === 'buy' && styles.tradeTypeTextActive]}>
                Buy
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tradeTypeButton, tradeType === 'sell' && styles.tradeTypeButtonActive]}
              onPress={() => setTradeType('sell')}
            >
              <Text style={[styles.tradeTypeText, tradeType === 'sell' && styles.tradeTypeTextActive]}>
                Sell
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.tradeForm}>
            <Text style={styles.inputLabel}>Amount (USDT)</Text>
            <TextInput
              style={styles.tradeInput}
              placeholder="0.00"
              value={tradeAmount}
              onChangeText={setTradeAmount}
              keyboardType="numeric"
            />
            
            <Text style={styles.inputLabel}>Price (USDT)</Text>
            <TextInput
              style={styles.tradeInput}
              placeholder={selectedCrypto.price.toString()}
              value={tradePrice}
              onChangeText={setTradePrice}
              keyboardType="numeric"
            />

            <TouchableOpacity
              style={[styles.tradeButton, tradeType === 'buy' ? styles.buyButton : styles.sellButton]}
              onPress={handleTrade}
            >
              <Text style={styles.tradeButtonText}>
                {tradeType === 'buy' ? 'Buy' : 'Sell'} {selectedCrypto.symbol}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.noSelection}>
          <Text style={styles.noSelectionText}>Select a cryptocurrency from markets to start trading</Text>
          <TouchableOpacity
            style={styles.goToMarketsButton}
            onPress={() => setActiveTab('markets')}
          >
            <Text style={styles.goToMarketsText}>Go to Markets</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  const renderOrders = () => (
    <ScrollView style={styles.content}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Orders</Text>
        {orders.length > 0 ? (
          orders.map(order => (
            <View key={order.id} style={styles.orderItem}>
              <View style={styles.orderInfo}>
                <Text style={styles.orderType}>{order.type.toUpperCase()}</Text>
                <Text style={styles.orderSymbol}>{order.symbol}</Text>
                <Text style={styles.orderAmount}>{order.amount}</Text>
                <Text style={styles.orderPrice}>${order.price}</Text>
              </View>
              <View style={styles.orderStatus}>
                <View style={[
                  styles.statusBadge,
                  order.status === 'completed' ? styles.statusCompleted : styles.statusPending
                ]}>
                  <Text style={styles.statusText}>{order.status}</Text>
                </View>
                <Text style={styles.orderTime}>{order.time}</Text>
              </View>
            </View>
          ))
        ) : (
          <Text style={styles.noOrdersText}>No orders yet</Text>
        )}
      </View>
    </ScrollView>
  );

  const renderAdminPanel = () => (
    <ScrollView style={styles.content}>
      <View style={styles.adminHeader}>
        <Text style={styles.adminTitle}>Admin Panel</Text>
        <Text style={styles.adminSubtitle}>System Management</Text>
      </View>

      <View style={styles.adminStats}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>15,420</Text>
          <Text style={styles.statLabel}>Total Users</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>2,100</Text>
          <Text style={styles.statLabel}>Orders Today</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>$45.6M</Text>
          <Text style={styles.statLabel}>Volume Today</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity style={styles.adminAction}>
          <Text style={styles.adminActionText}>User Management</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.adminAction}>
          <Text style={styles.adminActionText}>Trading Operations</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.adminAction}>
          <Text style={styles.adminActionText}>Security Monitoring</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.adminAction}>
          <Text style={styles.adminActionText}>System Configuration</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Health</Text>
        <View style={styles.healthItem}>
          <Text style={styles.healthLabel}>Database</Text>
          <Text style={[styles.healthStatus, styles.healthy]}>Healthy</Text>
        </View>
        <View style={styles.healthItem}>
          <Text style={styles.healthLabel}>Trading Engine</Text>
          <Text style={[styles.healthStatus, styles.healthy]}>Healthy</Text>
        </View>
        <View style={styles.healthItem}>
          <Text style={styles.healthLabel}>API Gateway</Text>
          <Text style={[styles.healthStatus, styles.healthy]}>Healthy</Text>
        </View>
      </View>
    </ScrollView>
  );

  if (!isLoggedIn) {
    return renderLoginScreen();
  }

  return renderMainApp();
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  gradient: {
    flex: 1,
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
    marginBottom: 40,
  },
  formContainer: {
    width: '100%',
    maxWidth: 300,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  loginButton: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginBottom: 15,
  },
  loginButtonText: {
    color: '#4A90E2',
    fontSize: 16,
    fontWeight: 'bold',
  },
  forgotPassword: {
    alignItems: 'center',
  },
  forgotPasswordText: {
    color: '#fff',
    fontSize: 14,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  welcomeText: {
    fontSize: 14,
    color: '#666',
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  headerButtons: {
    flexDirection: 'row',
  },
  headerButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginLeft: 10,
  },
  adminButton: {
    backgroundColor: '#ff6b6b',
  },
  headerButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  navItem: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
  },
  navItemActive: {
    borderTopWidth: 2,
    borderTopColor: '#4A90E2',
  },
  navText: {
    fontSize: 12,
    color: '#666',
  },
  navTextActive: {
    color: '#4A90E2',
    fontWeight: 'bold',
  },
  portfolioHeader: {
    backgroundColor: '#4A90E2',
    padding: 30,
    alignItems: 'center',
  },
  portfolioTitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
  },
  portfolioValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginVertical: 8,
  },
  portfolioChange: {
    fontSize: 16,
    color: '#4ade80',
  },
  section: {
    backgroundColor: '#fff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  assetItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  assetInfo: {
    flex: 1,
  },
  assetSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  assetBalance: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  assetValue: {
    alignItems: 'flex-end',
  },
  assetPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  assetChange: {
    fontSize: 14,
    marginTop: 2,
  },
  positive: {
    color: '#10b981',
  },
  negative: {
    color: '#ef4444',
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  transactionInfo: {
    flex: 1,
  },
  transactionType: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  transactionSymbol: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  transactionTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  transactionAmount: {
    alignItems: 'flex-end',
  },
  transactionValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 4,
  },
  statusCompleted: {
    backgroundColor: '#10b981',
  },
  statusPending: {
    backgroundColor: '#f59e0b',
  },
  statusText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: 'bold',
  },
  chartSection: {
    backgroundColor: '#fff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  chartContainer: {
    alignItems: 'center',
  },
  searchSection: {
    backgroundColor: '#fff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  searchInput: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  marketItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  marketInfo: {
    flex: 1,
  },
  marketSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  marketVolume: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  marketPrice: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  change: {
    fontSize: 14,
    marginTop: 2,
  },
  tradeContainer: {
    padding: 20,
  },
  selectedCrypto: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  selectedSymbol: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  selectedPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
    marginVertical: 8,
  },
  selectedChange: {
    fontSize: 16,
  },
  tradeTypeSelector: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 8,
    marginBottom: 20,
  },
  tradeTypeButton: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    borderRadius: 8,
  },
  tradeTypeButtonActive: {
    backgroundColor: '#4A90E2',
  },
  tradeTypeText: {
    fontSize: 16,
    color: '#666',
    fontWeight: 'bold',
  },
  tradeTypeTextActive: {
    color: '#fff',
  },
  tradeForm: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 8,
  },
  inputLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  tradeInput: {
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    marginBottom: 20,
  },
  tradeButton: {
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
  tradeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  noSelection: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  noSelectionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  goToMarketsButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
  },
  goToMarketsText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  orderInfo: {
    flex: 1,
  },
  orderType: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  orderSymbol: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  orderAmount: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  orderPrice: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  orderStatus: {
    alignItems: 'flex-end',
  },
  orderTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  noOrdersText: {
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
  },
  adminHeader: {
    backgroundColor: '#ff6b6b',
    padding: 30,
    alignItems: 'center',
  },
  adminTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  adminSubtitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.8,
    marginTop: 8,
  },
  adminStats: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
  },
  statCard: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#f0f0f0',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  adminAction: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  adminActionText: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
  },
  healthItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  healthLabel: {
    fontSize: 16,
    color: '#333',
  },
  healthStatus: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  healthy: {
    color: '#10b981',
  },
});

export default EnhancedMobileApp;