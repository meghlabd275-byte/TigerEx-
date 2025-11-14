import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  FlatList,
  Dimensions,
  RefreshControl,
  Animated,
  PanGestureHandler,
  State,
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
  ResponsiveContainer,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  BarChart3,
  Settings,
  Bell,
  Search,
  Star,
  Eye,
  EyeOff,
  Plus,
  Minus,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  Zap,
  Shield,
  Wallet,
  History,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Home,
  PieChart as PieChartIcon,
  FileText,
  User,
  LogOut,
  Filter,
  Download,
  Upload,
  RefreshCw,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Lock,
  Unlock,
  Code,
  Layers,
  Grid,
  List,
  Save,
  Copy,
  ExternalLink,
  Calendar,
  Target,
  Award,
  Gift,
  Trophy,
  Flame,
  Bolt,
  Cpu,
  Database,
  Server,
  Globe,
  Wifi,
  WifiOff,
  HardDrive,
  Cpu as CpuIcon,
} from 'lucide-react-native';

const { width, height } = Dimensions.get('window');

interface TradingPair {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  isFavorite: boolean;
}

interface OrderBookEntry {
  price: number;
  amount: number;
  total: number;
}

interface Trade {
  time: string;
  price: number;
  amount: number;
  type: 'buy' | 'sell';
}

interface Position {
  id: string;
  symbol: string;
  type: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  leverage: number;
  margin: number;
}

const EnhancedTradingScreen: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState('trade');
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [orderType, setOrderType] = useState('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [amount, setAmount] = useState('');
  const [price, setPrice] = useState('');
  const [leverage, setLeverage] = useState('1');
  const [showOrders, setShowOrders] = useState(false);
  const [showPositions, setShowPositions] = useState(false);
  const [showChart, setShowChart] = useState(true);
  const [timeframe, setTimeframe] = useState('1h');
  const [chartType, setChartType] = useState('candlestick');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFavorites, setShowFavorites] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Animation values
  const slideAnim = useState(new Animated.Value(width))[0];
  const fadeAnim = useState(new Animated.Value(0))[0];

  const tradingPairs: TradingPair[] = [
    { symbol: 'BTC/USDT', name: 'Bitcoin', price: 67850.25, change24h: 2.5, volume24h: 1250000000, high24h: 68900, low24h: 66500, isFavorite: true },
    { symbol: 'ETH/USDT', name: 'Ethereum', price: 3542.18, change24h: -1.2, volume24h: 850000000, high24h: 3650, low24h: 3480, isFavorite: true },
    { symbol: 'SOL/USDT', name: 'Solana', price: 145.67, change24h: 3.2, volume24h: 450000000, high24h: 152, low24h: 140, isFavorite: false },
    { symbol: 'BNB/USDT', name: 'Binance Coin', price: 612.45, change24h: 0.8, volume24h: 320000000, high24h: 625, low24h: 605, isFavorite: false },
    { symbol: 'ADA/USDT', name: 'Cardano', price: 0.385, change24h: -0.5, volume24h: 180000000, high24h: 0.395, low24h: 0.380, isFavorite: false },
  ];

  const orderBookBuy: OrderBookEntry[] = [
    { price: 67845.50, amount: 0.1254, total: 8508.92 },
    { price: 67844.75, amount: 0.0892, total: 6050.15 },
    { price: 67843.25, amount: 0.1567, total: 10633.48 },
    { price: 67842.00, amount: 0.2341, total: 15875.60 },
    { price: 67840.50, amount: 0.0987, total: 6698.54 },
  ];

  const orderBookSell: OrderBookEntry[] = [
    { price: 67846.25, amount: 0.1342, total: 9103.68 },
    { price: 67847.50, amount: 0.0765, total: 5189.75 },
    { price: 67848.75, amount: 0.1983, total: 13452.18 },
    { price: 67850.00, amount: 0.1456, total: 9874.80 },
    { price: 67851.25, amount: 0.0891, total: 6042.46 },
  ];

  const recentTrades: Trade[] = [
    { time: '10:30:45', price: 67845.50, amount: 0.1254, type: 'buy' },
    { time: '10:30:42', price: 67846.25, amount: 0.1342, type: 'sell' },
    { time: '10:30:38', price: 67844.75, amount: 0.0892, type: 'buy' },
    { time: '10:30:35', price: 67847.50, amount: 0.0765, type: 'sell' },
    { time: '10:30:32', price: 67843.25, amount: 0.1567, type: 'buy' },
  ];

  const positions: Position[] = [
    {
      id: '1',
      symbol: 'BTC/USDT',
      type: 'long',
      size: 0.5,
      entryPrice: 67000,
      currentPrice: 67850.25,
      pnl: 425.13,
      pnlPercent: 1.27,
      leverage: 10,
      margin: 3350.00
    },
    {
      id: '2',
      symbol: 'ETH/USDT',
      type: 'short',
      size: 5.0,
      entryPrice: 3600,
      currentPrice: 3542.18,
      pnl: 289.10,
      pnlPercent: 1.61,
      leverage: 5,
      margin: 3600.00
    },
  ];

  const chartData = [
    { time: '09:00', price: 67200, volume: 150000 },
    { time: '10:00', price: 67500, volume: 180000 },
    { time: '11:00', price: 67800, volume: 220000 },
    { time: '12:00', price: 67650, volume: 190000 },
    { time: '13:00', price: 67850, volume: 250000 },
    { time: '14:00', price: 67950, volume: 210000 },
    { time: '15:00', price: 67850, volume: 230000 },
  ];

  const filteredPairs = useMemo(() => {
    return tradingPairs.filter(pair =>
      pair.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pair.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  const currentPair = tradingPairs.find(pair => pair.symbol === selectedPair);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  }, []);

  const toggleSidebar = () => {
    if (sidebarOpen) {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: width,
          duration: 300,
          useNativeDriver: false,
        }),
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: false,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: false,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: false,
        }),
      ]).start();
    }
    setSidebarOpen(!sidebarOpen);
  };

  const renderHeader = () => (
    <View style={styles.header}>
      <TouchableOpacity onPress={toggleSidebar} style={styles.menuButton}>
        <Menu size={24} color="#fff" />
      </TouchableOpacity>
      
      <View style={styles.headerCenter}>
        <TouchableOpacity style={styles.pairSelector}>
          <Text style={styles.selectedPair}>{selectedPair}</Text>
          <ChevronDown size={16} color="#fff" />
        </TouchableOpacity>
        {currentPair && (
          <View style={styles.priceInfo}>
            <Text style={styles.currentPrice}>
              ${currentPair.price.toLocaleString()}
            </Text>
            <View style={[
              styles.changeBadge,
              { backgroundColor: currentPair.change24h >= 0 ? '#10b981' : '#ef4444' }
            ]}>
              {currentPair.change24h >= 0 ? (
                <TrendingUp size={12} color="#fff" />
              ) : (
                <TrendingDown size={12} color="#fff" />
              )}
              <Text style={styles.changeText}>
                {Math.abs(currentPair.change24h)}%
              </Text>
            </View>
          </View>
        )}
      </View>
      
      <View style={styles.headerRight}>
        <TouchableOpacity style={styles.iconButton}>
          <Search size={20} color="#fff" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.iconButton}>
          <Bell size={20} color="#fff" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.iconButton}>
          <Settings size={20} color="#fff" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderChart = () => (
    <View style={styles.chartContainer}>
      <View style={styles.chartHeader}>
        <View style={styles.timeframes}>
          {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
            <TouchableOpacity
              key={tf}
              style={[
                styles.timeframeButton,
                timeframe === tf && styles.activeTimeframe
              ]}
              onPress={() => setTimeframe(tf)}
            >
              <Text style={[
                styles.timeframeText,
                timeframe === tf && styles.activeTimeframeText
              ]}>
                {tf}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        
        <View style={styles.chartTypes}>
          <TouchableOpacity style={styles.chartTypeButton}>
            <BarChart3 size={16} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.chartTypeButton}>
            <Activity size={16} color="#9ca3af" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.chartTypeButton}>
            <LineChart size={16} color="#3b82f6" />
          </TouchableOpacity>
        </View>
      </View>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <ResponsiveContainer width={width * 1.2} height={200}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: 'none',
                borderRadius: 8,
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ScrollView>
      
      <View style={styles.chartStats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>24h High</Text>
          <Text style={styles.statValue}>
            ${currentPair?.high24h.toLocaleString()}
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>24h Low</Text>
          <Text style={styles.statValue}>
            ${currentPair?.low24h.toLocaleString()}
          </Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>24h Volume</Text>
          <Text style={styles.statValue}>
            ${(currentPair?.volume24h / 1000000000).toFixed(2)}B
          </Text>
        </View>
      </View>
    </View>
  );

  const renderOrderForm = () => (
    <View style={styles.orderForm}>
      <View style={styles.orderTypeSelector}>
        <TouchableOpacity
          style={[
            styles.orderTypeButton,
            orderSide === 'buy' && styles.buyButton
          ]}
          onPress={() => setOrderSide('buy')}
        >
          <Text style={[
            styles.orderTypeText,
            orderSide === 'buy' && styles.buyButtonText
          ]}>
            Buy
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.orderTypeButton,
            orderSide === 'sell' && styles.sellButton
          ]}
          onPress={() => setOrderSide('sell')}
        >
          <Text style={[
            styles.orderTypeText,
            orderSide === 'sell' && styles.sellButtonText
          ]}>
            Sell
          </Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.formSection}>
        <Text style={styles.formLabel}>Order Type</Text>
        <View style={styles.orderTypeOptions}>
          {['market', 'limit'].map(type => (
            <TouchableOpacity
              key={type}
              style={[
                styles.orderTypeOption,
                orderType === type && styles.selectedOrderType
              ]}
              onPress={() => setOrderType(type)}
            >
              <Text style={[
                styles.orderTypeOptionText,
                orderType === type && styles.selectedOrderTypeText
              ]}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      {orderType === 'limit' && (
        <View style={styles.formSection}>
          <Text style={styles.formLabel}>Price</Text>
          <TextInput
            style={styles.textInput}
            value={price}
            onChangeText={setPrice}
            placeholder="Enter price"
            placeholderTextColor="#6b7280"
            keyboardType="decimal-pad"
          />
        </View>
      )}
      
      <View style={styles.formSection}>
        <Text style={styles.formLabel}>Amount</Text>
        <TextInput
          style={styles.textInput}
          value={amount}
          onChangeText={setAmount}
          placeholder="Enter amount"
          placeholderTextColor="#6b7280"
          keyboardType="decimal-pad"
        />
      </View>
      
      <View style={styles.formSection}>
        <Text style={styles.formLabel}>Leverage</Text>
        <View style={styles.leverageOptions}>
          {[1, 2, 5, 10, 20, 50, 100].map(lev => (
            <TouchableOpacity
              key={lev}
              style={[
                styles.leverageOption,
                leverage === lev.toString() && styles.selectedLeverage
              ]}
              onPress={() => setLeverage(lev.toString())}
            >
              <Text style={[
                styles.leverageOptionText,
                leverage === lev.toString() && styles.selectedLeverageText
              ]}>
                {lev}x
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      
      <View style={styles.orderSummary}>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Total</Text>
          <Text style={styles.summaryValue}>
            ${amount && price ? (parseFloat(amount) * parseFloat(price)).toFixed(2) : '0.00'}
          </Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Est. Fee</Text>
          <Text style={styles.summaryValue}>
            ${amount && price ? (parseFloat(amount) * parseFloat(price) * 0.001).toFixed(2) : '0.00'}
          </Text>
        </View>
      </View>
      
      <TouchableOpacity
        style={[
          styles.submitButton,
          orderSide === 'buy' ? styles.buySubmitButton : styles.sellSubmitButton
        ]}
        onPress={() => Alert.alert('Order Placed', 'Your order has been placed successfully!')}
      >
        <Text style={[
          styles.submitButtonText,
          orderSide === 'buy' ? styles.buySubmitButtonText : styles.sellSubmitButtonText
        ]}>
          {orderSide === 'buy' ? 'Buy' : 'Sell'} {selectedPair}
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderOrderBook = () => (
    <View style={styles.orderBook}>
      <View style={styles.orderBookHeader}>
        <Text style={styles.orderBookTitle}>Order Book</Text>
        <TouchableOpacity style={styles.orderBookToggle}>
          <Text style={styles.orderBookToggleText}>Depth</Text>
        </TouchableOpacity>
      </View>
      
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.orderBookSection}>
          <Text style={styles.orderBookSectionTitle}>Sells</Text>
          {orderBookSell.map((order, index) => (
            <View key={index} style={styles.orderBookRow}>
              <Text style={[styles.orderBookPrice, { color: '#ef4444' }]}>
                ${order.price.toFixed(2)}
              </Text>
              <Text style={styles.orderBookAmount}>
                {order.amount.toFixed(4)}
              </Text>
              <Text style={styles.orderBookTotal}>
                ${order.total.toFixed(2)}
              </Text>
            </View>
          ))}
        </View>
        
        <View style={styles.spreadRow}>
          <Text style={styles.spreadText}>
            Spread: ${(orderBookSell[0].price - orderBookBuy[0].price).toFixed(2)}
          </Text>
        </View>
        
        <View style={styles.orderBookSection}>
          <Text style={styles.orderBookSectionTitle}>Buys</Text>
          {orderBookBuy.map((order, index) => (
            <View key={index} style={styles.orderBookRow}>
              <Text style={[styles.orderBookPrice, { color: '#10b981' }]}>
                ${order.price.toFixed(2)}
              </Text>
              <Text style={styles.orderBookAmount}>
                {order.amount.toFixed(4)}
              </Text>
              <Text style={styles.orderBookTotal}>
                ${order.total.toFixed(2)}
              </Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );

  const renderRecentTrades = () => (
    <View style={styles.recentTrades}>
      <View style={styles.recentTradesHeader}>
        <Text style={styles.recentTradesTitle}>Recent Trades</Text>
        <TouchableOpacity style={styles.recentTradesToggle}>
          <Text style={styles.recentTradesToggleText}>All</Text>
        </TouchableOpacity>
      </View>
      
      <ScrollView showsVerticalScrollIndicator={false}>
        {recentTrades.map((trade, index) => (
          <View key={index} style={styles.tradeRow}>
            <Text style={styles.tradeTime}>{trade.time}</Text>
            <Text style={[
              styles.tradePrice,
              { color: trade.type === 'buy' ? '#10b981' : '#ef4444' }
            ]}>
              ${trade.price.toFixed(2)}
            </Text>
            <Text style={styles.tradeAmount}>
              {trade.amount.toFixed(4)}
            </Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );

  const renderPositions = () => (
    <View style={styles.positions}>
      <Text style={styles.positionsTitle}>Open Positions</Text>
      {positions.map(position => (
        <View key={position.id} style={styles.positionCard}>
          <View style={styles.positionHeader}>
            <Text style={styles.positionSymbol}>{position.symbol}</Text>
            <Text style={[
              styles.positionType,
              { color: position.type === 'long' ? '#10b981' : '#ef4444' }
            ]}>
              {position.type.toUpperCase()}
            </Text>
          </View>
          
          <View style={styles.positionDetails}>
            <View style={styles.positionDetail}>
              <Text style={styles.positionLabel}>Size</Text>
              <Text style={styles.positionValue}>{position.size}</Text>
            </View>
            <View style={styles.positionDetail}>
              <Text style={styles.positionLabel}>Entry</Text>
              <Text style={styles.positionValue}>
                ${position.entryPrice.toLocaleString()}
              </Text>
            </View>
            <View style={styles.positionDetail}>
              <Text style={styles.positionLabel}>Mark</Text>
              <Text style={styles.positionValue}>
                ${position.currentPrice.toLocaleString()}
              </Text>
            </View>
            <View style={styles.positionDetail}>
              <Text style={styles.positionLabel}>PNL</Text>
              <Text style={[
                styles.positionValue,
                { color: position.pnl >= 0 ? '#10b981' : '#ef4444' }
              ]}>
                ${position.pnl >= 0 ? '+' : ''}{position.pnl.toFixed(2)}
              </Text>
            </View>
          </View>
          
          <View style={styles.positionActions}>
            <TouchableOpacity style={styles.positionAction}>
              <Text style={styles.positionActionText}>Close</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.positionAction}>
              <Text style={styles.positionActionText}>Modify</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </View>
  );

  const renderSidebar = () => (
    <Modal
      transparent={true}
      visible={sidebarOpen}
      animationType="none"
      onRequestClose={toggleSidebar}
    >
      <Animated.View
        style={[
          styles.sidebarOverlay,
          { opacity: fadeAnim }
        ]}
      >
        <TouchableOpacity
          style={styles.sidebarOverlayTouchable}
          onPress={toggleSidebar}
        />
        <Animated.View
          style={[
            styles.sidebar,
            { transform: [{ translateX: slideAnim }] }
          ]}
        >
          <View style={styles.sidebarHeader}>
            <Text style={styles.sidebarTitle}>Trading Menu</Text>
            <TouchableOpacity onPress={toggleSidebar}>
              <X size={24} color="#fff" />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.sidebarContent}>
            <TouchableOpacity style={styles.sidebarItem}>
              <Home size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Home</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <TrendingUp size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Markets</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <Wallet size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Wallet</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <History size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Orders</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <BarChart3 size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Positions</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <Star size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Favorites</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <Settings size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Settings</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <User size={20} color="#9ca3af" />
              <Text style={styles.sidebarItemText}>Profile</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.sidebarItem}>
              <LogOut size={20} color="#ef4444" />
              <Text style={[styles.sidebarItemText, { color: '#ef4444' }]}>
                Logout
              </Text>
            </TouchableOpacity>
          </ScrollView>
        </Animated.View>
      </Animated.View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {renderHeader()}
      
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {renderChart()}
        
        <View style={styles.mainContent}>
          <View style={styles.leftColumn}>
            {renderOrderForm()}
          </View>
          
          <View style={styles.rightColumn}>
            {showChart && renderOrderBook()}
            {!showChart && renderRecentTrades()}
            
            <View style={styles.tabToggle}>
              <TouchableOpacity
                style={[
                  styles.tabButton,
                  showChart && styles.activeTab
                ]}
                onPress={() => setShowChart(true)}
              >
                <Text style={[
                  styles.tabButtonText,
                  showChart && styles.activeTabButtonText
                ]}>
                  Order Book
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.tabButton,
                  !showChart && styles.activeTab
                ]}
                onPress={() => setShowChart(false)}
              >
                <Text style={[
                  styles.tabButtonText,
                  !showChart && styles.activeTabButtonText
                ]}>
                  Recent Trades
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
        
        {positions.length > 0 && renderPositions()}
      </ScrollView>
      
      {renderSidebar()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#1f2937',
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  menuButton: {
    padding: 8,
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  pairSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#374151',
    borderRadius: 8,
  },
  selectedPair: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 4,
  },
  priceInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  currentPrice: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginRight: 8,
  },
  changeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  changeText: {
    color: '#fff',
    fontSize: 12,
    marginLeft: 2,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconButton: {
    padding: 8,
    marginLeft: 8,
  },
  content: {
    flex: 1,
  },
  chartContainer: {
    backgroundColor: '#1f2937',
    margin: 16,
    borderRadius: 12,
    padding: 16,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  timeframes: {
    flexDirection: 'row',
  },
  timeframeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    backgroundColor: '#374151',
    borderRadius: 6,
  },
  activeTimeframe: {
    backgroundColor: '#3b82f6',
  },
  timeframeText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  activeTimeframeText: {
    color: '#fff',
  },
  chartTypes: {
    flexDirection: 'row',
  },
  chartTypeButton: {
    padding: 8,
    marginLeft: 8,
    backgroundColor: '#374151',
    borderRadius: 6,
  },
  chartStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#374151',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    color: '#9ca3af',
    fontSize: 12,
  },
  statValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 4,
  },
  mainContent: {
    flexDirection: 'row',
    paddingHorizontal: 16,
  },
  leftColumn: {
    flex: 1,
    marginRight: 8,
  },
  rightColumn: {
    flex: 1,
    marginLeft: 8,
  },
  orderForm: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
  },
  orderTypeSelector: {
    flexDirection: 'row',
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 4,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#10b981',
  },
  sellButton: {
    backgroundColor: '#ef4444',
  },
  orderTypeText: {
    color: '#9ca3af',
    fontSize: 14,
    fontWeight: '600',
  },
  buyButtonText: {
    color: '#fff',
  },
  sellButtonText: {
    color: '#fff',
  },
  formSection: {
    marginTop: 16,
  },
  formLabel: {
    color: '#9ca3af',
    fontSize: 14,
    marginBottom: 8,
  },
  orderTypeOptions: {
    flexDirection: 'row',
  },
  orderTypeOption: {
    flex: 1,
    paddingVertical: 8,
    backgroundColor: '#374151',
    borderRadius: 6,
    alignItems: 'center',
    marginRight: 8,
  },
  selectedOrderType: {
    backgroundColor: '#3b82f6',
  },
  orderTypeOptionText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  selectedOrderTypeText: {
    color: '#fff',
  },
  textInput: {
    backgroundColor: '#374151',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: '#fff',
    fontSize: 14,
  },
  leverageOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  leverageOption: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#374151',
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  selectedLeverage: {
    backgroundColor: '#3b82f6',
  },
  leverageOptionText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  selectedLeverageText: {
    color: '#fff',
  },
  orderSummary: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#374151',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    color: '#9ca3af',
    fontSize: 12,
  },
  summaryValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  submitButton: {
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  buySubmitButton: {
    backgroundColor: '#10b981',
  },
  sellSubmitButton: {
    backgroundColor: '#ef4444',
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  buySubmitButtonText: {
    color: '#fff',
  },
  sellSubmitButtonText: {
    color: '#fff',
  },
  orderBook: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  orderBookHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  orderBookTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  orderBookToggle: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    backgroundColor: '#374151',
    borderRadius: 6,
  },
  orderBookToggleText: {
    color: '#9ca3af',
    fontSize: 12,
  },
  orderBookSection: {
    marginBottom: 16,
  },
  orderBookSectionTitle: {
    color: '#9ca3af',
    fontSize: 12,
    marginBottom: 8,
  },
  orderBookRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  orderBookPrice: {
    fontSize: 12,
    fontWeight: '500',
    flex: 1,
  },
  orderBookAmount: {
    color: '#9ca3af',
    fontSize: 12,
    flex: 1,
    textAlign: 'center',
  },
  orderBookTotal: {
    color: '#9ca3af',
    fontSize: 12,
    flex: 1,
    textAlign: 'right',
  },
  spreadRow: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#374151',
    alignItems: 'center',
  },
  spreadText: {
    color: '#9ca3af',
    fontSize: 12,
  },
  recentTrades: {
    backgroundColor: '#1f2937',
    borderRadius: 12,
    padding: 16,
  },
  recentTradesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  recentTradesTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  recentTradesToggle: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    backgroundColor: '#374151',
    borderRadius: 6,
  },
  recentTradesToggleText: {
    color: '#9ca3af',
    fontSize: 12,
  },
  tradeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  tradeTime: {
    color: '#9ca3af',
    fontSize: 12,
    flex: 1,
  },
  tradePrice: {
    fontSize: 12,
    fontWeight: '500',
    flex: 1,
    textAlign: 'center',
  },
  tradeAmount: {
    color: '#9ca3af',
    fontSize: 12,
    flex: 1,
    textAlign: 'right',
  },
  positions: {
    backgroundColor: '#1f2937',
    margin: 16,
    borderRadius: 12,
    padding: 16,
  },
  positionsTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  positionCard: {
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  positionSymbol: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  positionType: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  positionDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  positionDetail: {
    alignItems: 'center',
  },
  positionLabel: {
    color: '#9ca3af',
    fontSize: 10,
  },
  positionValue: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 2,
  },
  positionActions: {
    flexDirection: 'row',
  },
  positionAction: {
    flex: 1,
    paddingVertical: 6,
    backgroundColor: '#1f2937',
    borderRadius: 6,
    alignItems: 'center',
    marginRight: 8,
  },
  positionActionText: {
    color: '#9ca3af',
    fontSize: 12,
  },
  tabToggle: {
    flexDirection: 'row',
    backgroundColor: '#374151',
    borderRadius: 8,
    padding: 4,
    marginTop: 8,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  activeTab: {
    backgroundColor: '#3b82f6',
  },
  tabButtonText: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '500',
  },
  activeTabButtonText: {
    color: '#fff',
  },
  sidebarOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  sidebarOverlayTouchable: {
    flex: 1,
  },
  sidebar: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    width: width * 0.75,
    backgroundColor: '#1f2937',
  },
  sidebarHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  sidebarTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  sidebarContent: {
    flex: 1,
    paddingHorizontal: 16,
  },
  sidebarItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
  },
  sidebarItemText: {
    color: '#9ca3af',
    fontSize: 16,
    marginLeft: 16,
  },
});

export default EnhancedTradingScreen;