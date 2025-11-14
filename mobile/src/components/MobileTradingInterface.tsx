import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  SafeAreaView,
  StatusBar,
  Alert,
  Modal,
  FlatList,
  RefreshControl,
  Dimensions,
  Image,
} from 'react-native';
import {
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  CandlestickChart,
} from 'react-native-chart-kit';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  Ionicons,
  MaterialIcons,
  FontAwesome5,
  MaterialCommunityIcons,
  FontAwesome,
  AntDesign,
  Entypo,
  Feather,
} from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

interface TradingPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  favorite: boolean;
  sparkline: number[];
}

interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  type: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'OCO';
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: 'NEW' | 'FILLED' | 'CANCELED';
  createdAt: string;
}

interface Balance {
  asset: string;
  available: number;
  locked: number;
  total: number;
  usdValue: number;
  change24h: number;
}

interface Position {
  symbol: string;
  side: 'LONG' | 'SHORT';
  size: number;
  entryPrice: number;
  markPrice: number;
  unrealizedPnl: number;
  leverage: number;
  liquidationPrice: number;
}

const MobileTradingInterface: React.FC = () => {
  const [selectedPair, setSelectedPair] = useState<string>('BTCUSDT');
  const [tradingPairs, setTradingPairs] = useState<TradingPair[]>([]);
  const [balances, setBalances] = useState<Balance[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [chartType, setChartType] = useState<'line' | 'candlestick' | 'area'>('candlestick');
  const [timeframe, setTimeframe] = useState('1h');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'STOP_LOSS'>('LIMIT');
  const [orderSide, setOrderSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderQuantity, setOrderQuantity] = useState<string>('');
  const [orderPrice, setOrderPrice] = useState<string>('');
  const [stopPrice, setStopPrice] = useState<string>('');
  const [leverage, setLeverage] = useState<number>(1);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showOrderConfirm, setShowOrderConfirm] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadTradingData();
    loadUserData();
  }, []);

  const loadTradingData = async () => {
    const mockPairs: TradingPair[] = [
      {
        symbol: 'BTCUSDT',
        baseAsset: 'BTC',
        quoteAsset: 'USDT',
        price: 43250.50,
        change24h: 2.34,
        volume24h: 1250000000,
        high24h: 44500.00,
        low24h: 42100.00,
        favorite: true,
        sparkline: [42000, 42500, 43000, 43250, 43100, 43300, 43250],
      },
      {
        symbol: 'ETHUSDT',
        baseAsset: 'ETH',
        quoteAsset: 'USDT',
        price: 2280.75,
        change24h: -1.23,
        volume24h: 850000000,
        high24h: 2350.00,
        low24h: 2250.00,
        favorite: true,
        sparkline: [2300, 2285, 2270, 2280, 2290, 2285, 2280],
      },
      {
        symbol: 'BNBUSDT',
        baseAsset: 'BNB',
        quoteAsset: 'USDT',
        price: 315.60,
        change24h: 0.87,
        volume24h: 420000000,
        high24h: 320.00,
        low24h: 310.50,
        favorite: false,
        sparkline: [310, 312, 315, 314, 316, 315, 315],
      },
    ];

    const mockBalances: Balance[] = [
      { asset: 'BTC', available: 0.125, locked: 0.0, total: 0.125, usdValue: 5406.31, change24h: 2.34 },
      { asset: 'ETH', available: 2.5, locked: 0.5, total: 3.0, usdValue: 6842.25, change24h: -1.23 },
      { asset: 'USDT', available: 10000, locked: 2500, total: 12500, usdValue: 12500, change24h: 0 },
    ];

    const mockOrders: Order[] = [
      {
        id: '1',
        symbol: 'BTCUSDT',
        side: 'BUY',
        type: 'LIMIT',
        quantity: 0.01,
        price: 42000,
        status: 'NEW',
        createdAt: new Date().toISOString(),
      },
    ];

    const mockPositions: Position[] = [
      {
        symbol: 'BTCUSDT',
        side: 'LONG',
        size: 0.05,
        entryPrice: 41000,
        markPrice: 43250,
        unrealizedPnl: 112.50,
        leverage: 3,
        liquidationPrice: 38500,
      },
    ];

    setTradingPairs(mockPairs);
    setBalances(mockBalances);
    setOrders(mockOrders);
    setPositions(mockPositions);
  };

  const loadUserData = async () => {
    try {
      const darkMode = await AsyncStorage.getItem('darkMode');
      setIsDarkMode(darkMode === 'true');
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const handlePlaceOrder = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    Alert.alert(
      'Order Placed',
      `${orderSide} ${orderQuantity} ${selectedPair} order has been placed successfully.`,
      [{ text: 'OK', onPress: () => setShowOrderConfirm(false) }]
    );

    setOrderQuantity('');
    setOrderPrice('');
    setStopPrice('');
  };

  const selectedPairData = useMemo(() => {
    return tradingPairs.find(pair => pair.symbol === selectedPair);
  }, [tradingPairs, selectedPair]);

  const chartData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
    datasets: [
      {
        data: selectedPairData?.sparkline || [42500, 42800, 43200, 43000, 43500, 43300, 43250],
        color: (opacity = 1) => `rgba(52, 211, 153, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  return (
    <SafeAreaView style={[styles.container, isDarkMode && styles.containerDark]}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#000' : '#fff'}
      />

      {/* Header */}
      <LinearGradient
        colors={isDarkMode ? ['#1a1a1a', '#2a2a2a'] : ['#fff', '#f9fafb']}
        style={styles.header}
      >
        <View style={styles.headerTop}>
          <Text style={[styles.headerTitle, isDarkMode && styles.textLight]}>
            TigerEx Trading
          </Text>
        </View>

        {/* Current Pair Info */}
        {selectedPairData && (
          <View style={styles.currentPairInfo}>
            <View style={styles.pairDetails}>
              <Text style={[styles.currentSymbol, isDarkMode && styles.textLight]}>
                {selectedPairData.symbol}
              </Text>
              <Text style={[styles.currentPrice, isDarkMode && styles.textLight]}>
                ${selectedPairData.price.toFixed(2)}
              </Text>
              <Text style={[
                styles.currentChange,
                selectedPairData.change24h >= 0 ? styles.positiveChange : styles.negativeChange
              ]}>
                {selectedPairData.change24h >= 0 ? '+' : ''}{selectedPairData.change24h.toFixed(2)}%
              </Text>
            </View>
          </View>
        )}
      </LinearGradient>

      {/* Main Content */}
      <ScrollView style={styles.content}>
        {/* Trading Form */}
        <View style={[styles.tradingForm, isDarkMode && styles.tradingFormDark]}>
          <Text style={[styles.sectionTitle, isDarkMode && styles.textLight]}>
            Place Order
          </Text>

          {/* Order Form */}
          <View style={styles.inputContainer}>
            <TextInput
              style={[styles.input, isDarkMode && styles.inputDark]}
              placeholder="Quantity"
              placeholderTextColor={isDarkMode ? '#666' : '#999'}
              value={orderQuantity}
              onChangeText={setOrderQuantity}
              keyboardType="numeric"
            />

            <TouchableOpacity
              style={[
                styles.placeOrderButton,
                orderSide === 'BUY' ? styles.buyOrderButton : styles.sellOrderButton,
              ]}
              onPress={() => setShowOrderConfirm(true)}
            >
              <Text style={styles.placeOrderButtonText}>
                {orderSide === 'BUY' ? 'Buy' : 'Sell'} {selectedPairData?.baseAsset}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  containerDark: {
    backgroundColor: '#000',
  },
  header: {
    paddingTop: 10,
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  textLight: {
    color: '#fff',
  },
  textSecondary: {
    color: '#666',
  },
  currentPairInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  pairDetails: {
    flexDirection: 'column',
  },
  currentSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  currentPrice: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  positiveChange: {
    color: '#10B981',
  },
  negativeChange: {
    color: '#EF4444',
  },
  currentChange: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 2,
  },
  content: {
    flex: 1,
  },
  tradingForm: {
    backgroundColor: '#fff',
    margin: 16,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tradingFormDark: {
    backgroundColor: '#1a1a1a',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  inputContainer: {
    gap: 12,
  },
  input: {
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  inputDark: {
    color: '#fff',
    borderColor: '#333',
    backgroundColor: '#1a1a1a',
  },
  placeOrderButton: {
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  buyOrderButton: {
    backgroundColor: '#10B981',
  },
  sellOrderButton: {
    backgroundColor: '#EF4444',
  },
  placeOrderButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default MobileTradingInterface;