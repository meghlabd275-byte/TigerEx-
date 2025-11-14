/**
 * TigerEx Enhanced Mobile Application v11.0.0
 * Advanced trading mobile app with modern UX/UI and comprehensive features
 * Built with React Native for iOS and Android platforms
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Animated,
  Dimensions,
} from 'react-native';
import {
  NavigationContainer,
  useNavigation,
  useFocusEffect,
} from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

// Components
import TradingInterface from './components/TradingInterface';
import PortfolioDashboard from './components/PortfolioDashboard';
import MarketOverview from './components/MarketOverview';
import TradingBots from './components/TradingBots';
import ProfileSection from './components/ProfileSection';
import OrderBook from './components/OrderBook';
import PriceChart from './components/PriceChart';
import TradingHistory from './components/TradingHistory';
import NotificationsPanel from './components/NotificationsPanel';

// Services
import { apiService } from './services/apiService';
import { websocketService } from './services/websocketService';
import { biometricService } from './services/biometricService';
import { notificationService } from './services/notificationService';

// Utils
import { colors, typography, spacing } from './utils/theme';
import { formatPrice, formatPercentage } from './utils/formatters';
import { hapticFeedback } from './utils/haptics';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();
const { width, height } = Dimensions.get('window');

// Main Tab Navigator
const MainTabNavigator = () => {
  const navigation = useNavigation();
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  useEffect(() => {
    const unsubscribe = notificationService.onNotificationReceived((notification) => {
      setUnreadNotifications(prev => prev + 1);
      hapticFeedback.notification();
    });

    return unsubscribe;
  }, []);

  const getTabIcon = (focused, iconName, badge = 0) => {
    return (
      <View style={styles.tabIconContainer}>
        <Icon
          name={iconName}
          size={24}
          color={focused ? colors.primary : colors.grayMedium}
        />
        {badge > 0 && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{badge > 99 ? '99+' : badge}</Text>
          </View>
        )}
      </View>
    );
  };

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color }) => {
          let iconName;
          let badge = 0;

          switch (route.name) {
            case 'Trading':
              iconName = 'trending-up';
              break;
            case 'Portfolio':
              iconName = 'account-balance-wallet';
              break;
            case 'Markets':
              iconName = 'show-chart';
              break;
            case 'Bots':
              iconName = 'smart-toy';
              break;
            case 'Profile':
              iconName = 'person';
              badge = unreadNotifications;
              break;
          }

          return getTabIcon(focused, iconName, badge);
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.grayMedium,
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: true,
        tabBarLabelStyle: styles.tabLabel,
        headerShown: false,
      })}
    >
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Markets" component={MarketsScreen} />
      <Tab.Screen name="Bots" component={BotsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
};

// Trading Screen
const TradingScreen = () => {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [marketData, setMarketData] = useState({});
  const [orderBook, setOrderBook] = useState({ bids: [], asks: [] });
  const [refreshing, setRefreshing] = useState(false);
  const slideAnim = React.useRef(new Animated.Value(0)).current;

  useFocusEffect(
    useCallback(() => {
      loadMarketData();
      connectWebSocket();
      
      return () => {
        websocketService.disconnect();
      };
    }, [selectedPair])
  );

  const loadMarketData = async () => {
    try {
      const data = await apiService.getMarketData(selectedPair);
      setMarketData(data);
      
      const bookData = await apiService.getOrderBook(selectedPair);
      setOrderBook(bookData);
    } catch (error) {
      console.error('Error loading market data:', error);
    }
  };

  const connectWebSocket = () => {
    websocketService.subscribeToMarket(selectedPair, (data) => {
      setMarketData(prev => ({ ...prev, ...data }));
    });

    websocketService.subscribeToOrderBook(selectedPair, (data) => {
      setOrderBook(data);
    });
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadMarketData();
    setRefreshing(false);
  }, []);

  const onQuickTrade = (type) => {
    hapticFeedback.light();
    Animated.timing(slideAnim, {
      toValue: type === 'buy' ? 1 : -1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Price Display */}
        <View style={styles.headerSection}>
          <TouchableOpacity
            style={styles.pairSelector}
            onPress={() => {/* Navigate to pair selection */}}
          >
            <Text style={styles.pairText}>{selectedPair}</Text>
            <Icon name="keyboard-arrow-down" size={20} color={colors.white} />
          </TouchableOpacity>
          
          <View style={styles.priceDisplay}>
            <Text style={styles.currentPrice}>
              {formatPrice(marketData.price || 0)}
            </Text>
            <Text style={[
              styles.priceChange,
              marketData.change24h >= 0 ? styles.positive : styles.negative
            ]}>
              {marketData.change24h >= 0 ? '+' : ''}
              {formatPercentage(marketData.change24h || 0)}
            </Text>
          </View>
        </View>

        {/* Price Chart */}
        <Animated.View style={[styles.chartSection, { transform: [{ translateX: slideAnim }] }]}>
          <PriceChart pair={selectedPair} />
        </Animated.View>

        {/* Quick Trade Buttons */}
        <View style={styles.quickTradeSection}>
          <TouchableOpacity
            style={[styles.quickTradeButton, styles.buyButton]}
            onPress={() => onQuickTrade('buy')}
          >
            <Text style={styles.quickTradeText}>Buy</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.quickTradeButton, styles.sellButton]}
            onPress={() => onQuickTrade('sell')}
          >
            <Text style={styles.quickTradeText}>Sell</Text>
          </TouchableOpacity>
        </View>

        {/* Order Book */}
        <View style={styles.orderBookSection}>
          <Text style={styles.sectionTitle}>Order Book</Text>
          <OrderBook data={orderBook} />
        </View>

        {/* Trading Interface */}
        <View style={styles.tradingInterfaceSection}>
          <TradingInterface pair={selectedPair} />
        </View>
      </ScrollView>
    </View>
  );
};

// Portfolio Screen
const PortfolioScreen = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadPortfolio();
    }, [])
  );

  const loadPortfolio = async () => {
    try {
      const data = await apiService.getPortfolio();
      setPortfolio(data);
    } catch (error) {
      console.error('Error loading portfolio:', error);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            loadPortfolio().finally(() => setRefreshing(false));
          }} />
        }
      >
        <PortfolioDashboard portfolio={portfolio} />
        <TradingHistory />
      </ScrollView>
    </View>
  );
};

// Markets Screen
const MarketsScreen = () => {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <MarketOverview />
    </View>
  );
};

// Bots Screen
const BotsScreen = () => {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <TradingBots />
    </View>
  );
};

// Profile Screen
const ProfileScreen = () => {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <ProfileSection />
    </View>
  );
};

// Main App Component
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check for stored authentication
      const token = await apiService.getStoredToken();
      
      if (token) {
        // Validate token
        const isValid = await apiService.validateToken(token);
        setIsAuthenticated(isValid);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('App initialization error:', error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const onAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  const onLogout = () => {
    apiService.clearStoredToken();
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LinearGradient
          colors={colors.gradientBackground}
          style={styles.gradientContainer}
        />
        <Text style={styles.loadingText}>TigerEx</Text>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main">
            {() => <MainTabNavigator onLogout={onLogout} />}
          </Stack.Screen>
        ) : (
          <Stack.Screen name="Auth">
            {() => <AuthScreen onAuthSuccess={onAuthSuccess} />}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

// Auth Screen Component
const AuthScreen = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [biometricEnabled, setBiometricEnabled] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    const available = await biometricService.isAvailable();
    setBiometricEnabled(available);
  };

  const onBiometricAuth = async () => {
    try {
      const success = await biometricService.authenticate();
      if (success) {
        onAuthSuccess();
      }
    } catch (error) {
      console.error('Biometric authentication failed:', error);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={colors.gradientBackground}
        style={styles.gradientContainer}
      />
      
      <ScrollView style={styles.content}>
        <View style={styles.logoSection}>
          <Text style={styles.logoText}>TigerEx</Text>
          <Text style={styles.tagline}>Advanced Crypto Trading</Text>
        </View>

        {isLogin ? (
          <LoginForm onSuccess={onAuthSuccess} />
        ) : (
          <RegisterForm onSuccess={onAuthSuccess} />
        )}

        <TouchableOpacity
          style={styles.switchAuth}
          onPress={() => setIsLogin(!isLogin)}
        >
          <Text style={styles.switchAuthText}>
            {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
          </Text>
        </TouchableOpacity>

        {biometricEnabled && (
          <TouchableOpacity
            style={styles.biometricButton}
            onPress={onBiometricAuth}
          >
            <Icon name="fingerprint" size={30} color={colors.primary} />
            <Text style={styles.biometricText}>Login with Biometrics</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </View>
  );
};

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  gradientContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  content: {
    flex: 1,
    zIndex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.white,
    marginTop: 20,
  },
  tabBar: {
    backgroundColor: colors.surface,
    borderTopWidth: 0,
    elevation: 10,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tabLabel: {
    fontSize: 12,
    fontWeight: '600',
  },
  tabIconContainer: {
    position: 'relative',
  },
  badge: {
    position: 'absolute',
    right: -8,
    top: -4,
    backgroundColor: colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: {
    color: colors.white,
    fontSize: 10,
    fontWeight: 'bold',
  },
  headerSection: {
    padding: spacing.lg,
    paddingTop: spacing.xl,
  },
  pairSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  pairText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.white,
    marginRight: spacing.xs,
  },
  priceDisplay: {
    alignItems: 'flex-start',
  },
  currentPrice: {
    fontSize: 36,
    fontWeight: 'bold',
    color: colors.white,
  },
  priceChange: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: spacing.xs,
  },
  positive: {
    color: colors.success,
  },
  negative: {
    color: colors.error,
  },
  chartSection: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.lg,
  },
  quickTradeSection: {
    flexDirection: 'row',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  quickTradeButton: {
    flex: 1,
    paddingVertical: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: colors.success,
  },
  sellButton: {
    backgroundColor: colors.error,
  },
  quickTradeText: {
    color: colors.white,
    fontSize: 18,
    fontWeight: 'bold',
  },
  orderBookSection: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.lg,
  },
  tradingInterfaceSection: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.xl,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.white,
    marginBottom: spacing.md,
  },
  logoSection: {
    alignItems: 'center',
    marginTop: spacing.xxl,
    marginBottom: spacing.xxl,
  },
  logoText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  tagline: {
    fontSize: 16,
    color: colors.grayMedium,
  },
  switchAuth: {
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  switchAuthText: {
    color: colors.primary,
    fontSize: 14,
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.xl,
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 12,
    gap: spacing.md,
  },
  biometricText: {
    color: colors.primary,
    fontSize: 16,
    fontWeight: '600',
  },
});

export default App;