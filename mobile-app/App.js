/**
 * TigerEx Market Maker Bot Mobile App - Complete Version
 * Advanced monitoring and control application with all features
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
  StatusBar,
  Platform,
  Animated,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import PushNotification from 'react-native-push-notification';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useSelector, useDispatch } from 'react-redux';
import { Chart, LineChart } from 'react-native-chart-kit';

// Import components
import Dashboard from './src/components/Dashboard';
import BotManagement from './src/components/BotManagement';
import Portfolio from './src/components/Portfolio';
import Analytics from './src/components/Analytics';
import Settings from './src/components/Settings';
import LoginScreen from './src/components/LoginScreen';
import BotDetail from './src/components/BotDetail';
import TradingView from './src/components/TradingView';
import Notifications from './src/components/Notifications';
import DeFiDashboard from './src/components/DeFiDashboard';
import NFTMarketplace from './src/components/NFTMarketplace';
import OptionsTrading from './src/components/OptionsTrading';
import ComplianceCenter from './src/components/ComplianceCenter';

// Import services
import ApiService from './src/services/ApiService';
import NotificationService from './src/services/NotificationService';
import WebSocketService from './src/services/WebSocketService';
import BiometricService from './src/services/BiometricService';
import LocationService from './src/services/LocationService';

// Import store
import { store } from './src/store';
import { setBots, updateBotStatus, addNotification } from './src/store/actions';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();
const { width, height } = Dimensions.get('window');

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [securityLevel, setSecurityLevel] = useState('standard');
  const dispatch = useDispatch();
  const fadeAnim = new Animated.Value(0);

  // Initialize services
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Animate logo
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 2000,
        useNativeDriver: true,
      }).start();

      // Check biometric availability
      const biometricAvailable = await BiometricService.isAvailable();
      setBiometricEnabled(biometricAvailable);

      // Check authentication
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        ApiService.setAuthToken(token);
        
        // Check security level
        const userSecurityLevel = await AsyncStorage.getItem('security_level');
        setSecurityLevel(userSecurityLevel || 'standard');
        
        // Biometric authentication for high security
        if (userSecurityLevel === 'high' && biometricAvailable) {
          const authenticated = await BiometricService.authenticate();
          if (authenticated) {
            setIsAuthenticated(true);
          }
        } else {
          setIsAuthenticated(true);
        }
      }

      // Initialize push notifications
      initializePushNotifications();

      // Initialize WebSocket connection
      WebSocketService.initialize();

      // Initialize location services for compliance
      await LocationService.initialize();

      // Load initial data
      if (token) {
        await loadInitialData();
      }

      setLoading(false);
    } catch (error) {
      console.error('Error initializing app:', error);
      setLoading(false);
    }
  };

  const initializePushNotifications = () => {
    PushNotification.configure({
      onNotification: function (notification) {
        console.log('Notification:', notification);
        
        if (notification.userInteraction) {
          handleNotificationPress(notification);
        } else {
          // Handle background notification
          NotificationService.handleBackgroundNotification(notification);
        }
      },
      requestPermissions: Platform.OS === 'ios',
    });

    // Create notification channels (Android)
    if (Platform.OS === 'android') {
      const channels = [
        {
          channelId: 'bot-alerts',
          channelName: 'Bot Alerts',
          channelDescription: 'Critical alerts for market maker bot activities',
          playSound: true,
          soundName: 'default',
          importance: 5,
          vibrate: true,
        },
        {
          channelId: 'portfolio-updates',
          channelName: 'Portfolio Updates',
          channelDescription: 'Portfolio performance updates',
          playSound: false,
          importance: 3,
          vibrate: false,
        },
        {
          channelId: 'compliance-alerts',
          channelName: 'Compliance Alerts',
          channelDescription: 'Regulatory compliance notifications',
          playSound: true,
          soundName: 'alert',
          importance: 4,
          vibrate: true,
        },
        {
          channelId: 'defi-opportunities',
          channelName: 'DeFi Opportunities',
          channelDescription: 'New DeFi yield opportunities',
          playSound: false,
          importance: 2,
          vibrate: false,
        },
        {
          channelId: 'nft-alerts',
          channelName: 'NFT Alerts',
          channelDescription: 'NFT marketplace opportunities',
          playSound: false,
          importance: 2,
          vibrate: false,
        },
      ];

      channels.forEach(channel => {
        PushNotification.createChannel(channel, (created) => 
          console.log(`Channel ${channel.channelId} created:`, created)
        );
      });
    }
  };

  const loadInitialData = async () => {
    try {
      // Load bots data
      const bots = await ApiService.getBots();
      dispatch(setBots(bots));

      // Load portfolio data including DeFi positions
      const portfolio = await ApiService.getPortfolio();
      
      // Load NFT portfolio
      const nftPortfolio = await ApiService.getNFTPortfolio();
      
      // Load options positions
      const optionsPositions = await ApiService.getOptionsPositions();
      
      // Load compliance status
      const complianceStatus = await ApiService.getComplianceStatus();
      
      // Load notifications
      const notifications = await ApiService.getNotifications();
      notifications.forEach(notification => {
        dispatch(addNotification(notification));
      });
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const handleNotificationPress = (notification) => {
    // Navigate to relevant screen based on notification type
    switch (notification.data?.type) {
      case 'bot_alert':
        // Navigate to bot detail
        break;
      case 'portfolio_update':
        // Navigate to portfolio
        break;
      case 'compliance_alert':
        // Navigate to compliance center
        break;
      case 'defi_opportunity':
        // Navigate to DeFi dashboard
        break;
      case 'nft_alert':
        // Navigate to NFT marketplace
        break;
      case 'options_alert':
        // Navigate to options trading
        break;
      default:
        // Navigate to dashboard
        break;
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await loadInitialData();
      await WebSocketService.refreshData();
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
    setRefreshing(false);
  }, []);

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.multiRemove(['auth_token', 'security_level']);
            ApiService.clearAuthToken();
            WebSocketService.disconnect();
            LocationService.stopTracking();
            setIsAuthenticated(false);
          },
        },
      ]
    );
  };

  const handleSecurityUpgrade = async () => {
    Alert.alert(
      'Security Upgrade',
      'Enable biometric authentication for enhanced security?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Enable',
          onPress: async () => {
            if (biometricEnabled) {
              const authenticated = await BiometricService.authenticate();
              if (authenticated) {
                await AsyncStorage.setItem('security_level', 'high');
                setSecurityLevel('high');
                Alert.alert('Success', 'Biometric authentication enabled');
              }
            } else {
              Alert.alert('Error', 'Biometric authentication not available on this device');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return <LoadingScreen fadeAnim={fadeAnim} />;
  }

  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  const MainTabs = () => (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Bots':
              iconName = 'smart-toy';
              break;
            case 'DeFi':
              iconName = 'currency-bitcoin';
              break;
            case 'NFT':
              iconName = 'collections';
              break;
            case 'Options':
              iconName = 'show-chart';
              break;
            case 'Portfolio':
              iconName = 'account-balance-wallet';
              break;
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Compliance':
              iconName = 'security';
              break;
            case 'Settings':
              iconName = 'settings';
              break;
            default:
              iconName = 'help';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#0066cc',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: [
          styles.tabBar,
          { height: Platform.OS === 'ios' ? 90 : 70 }
        ],
        headerStyle: styles.header,
        headerTintColor: '#fff',
        headerTitleStyle: styles.headerTitle,
        tabBarLabelStyle: styles.tabBarLabel,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={Dashboard}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen 
        name="Bots" 
        component={BotManagement}
        options={{ title: 'Market Makers' }}
      />
      <Tab.Screen 
        name="DeFi" 
        component={DeFiDashboard}
        options={{ title: 'DeFi' }}
      />
      <Tab.Screen 
        name="NFT" 
        component={NFTMarketplace}
        options={{ title: 'NFTs' }}
      />
      <Tab.Screen 
        name="Options" 
        component={OptionsTrading}
        options={{ title: 'Options' }}
      />
      <Tab.Screen 
        name="Portfolio" 
        component={Portfolio}
        options={{ title: 'Portfolio' }}
      />
      <Tab.Screen 
        name="Analytics" 
        component={Analytics}
        options={{ title: 'Analytics' }}
      />
      <Tab.Screen 
        name="Compliance" 
        component={ComplianceCenter}
        options={{ title: 'Compliance' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={Settings}
        options={{ 
          title: 'Settings',
          headerRight: () => (
            <View style={styles.headerButtons}>
              <TouchableOpacity onPress={handleSecurityUpgrade} style={styles.headerButton}>
                <Icon name="enhanced-security" size={24} color="#fff" />
              </TouchableOpacity>
              <TouchableOpacity onPress={handleLogout} style={styles.headerButton}>
                <Icon name="logout" size={24} color="#fff" />
              </TouchableOpacity>
            </View>
          ),
        }}
      />
    </Tab.Navigator>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0066cc" />
      <NavigationContainer>
        <Stack.Navigator>
          <Stack.Screen 
            name="Main" 
            component={MainTabs}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="BotDetail" 
            component={BotDetail}
            options={({ route }) => ({ title: route.params.botName })}
          />
          <Stack.Screen 
            name="TradingView" 
            component={TradingView}
            options={({ route }) => ({ title: route.params.symbol })}
          />
          <Stack.Screen 
            name="Notifications" 
            component={Notifications}
            options={{ title: 'Notifications' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaView>
  );
};

const LoadingScreen = ({ fadeAnim }) => (
  <View style={styles.loadingContainer}>
    <Animated.View style={[styles.logoContainer, { opacity: fadeAnim }]}>
      <Icon name="smart-toy" size={80} color="#fff" />
      <Text style={styles.loadingText}>TigerEx</Text>
      <Text style={styles.loadingSubtext}>Market Maker Bot</Text>
      <Text style={styles.loadingVersion}>Enterprise Edition</Text>
    </Animated.View>
    <View style={styles.loadingFeatures}>
      <View style={styles.featureItem}>
        <Icon name="check-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>Advanced AI Trading</Text>
      </View>
      <View style={styles.featureItem}>
        <Icon name="check-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>DeFi Integration</Text>
      </View>
      <View style={styles.featureItem}>
        <Icon name="check-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>NFT Marketplace</Text>
      </View>
      <View style={styles.featureItem}>
        <Icon name="check-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>Options Trading</Text>
      </View>
      <View style={styles.featureItem}>
        <Icon name="check-circle" size={16} color="#4CAF50" />
        <Text style={styles.featureText}>Compliance Tools</Text>
      </View>
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0066cc',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 50,
  },
  loadingText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 20,
  },
  loadingSubtext: {
    fontSize: 16,
    color: '#fff',
    marginTop: 5,
    opacity: 0.8,
  },
  loadingVersion: {
    fontSize: 12,
    color: '#fff',
    marginTop: 5,
    opacity: 0.6,
  },
  loadingFeatures: {
    paddingHorizontal: 40,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 5,
  },
  featureText: {
    color: '#fff',
    marginLeft: 10,
    fontSize: 14,
  },
  tabBar: {
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingBottom: Platform.OS === 'ios' ? 20 : 10,
  },
  tabBarLabel: {
    fontSize: 10,
  },
  header: {
    backgroundColor: '#0066cc',
    elevation: 0,
    shadowOpacity: 0,
  },
  headerTitle: {
    fontWeight: 'bold',
  },
  headerButtons: {
    flexDirection: 'row',
  },
  headerButton: {
    marginRight: 15,
  },
});

export default App;