/**
 * TigerEx Market Maker Bot - Mobile Monitoring App
 * React Native application for real-time bot monitoring and control
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
  ActivityIndicator,
  Platform,
  Linking,
  Share,
} from 'react-native';
import {
  NavigationContainer,
  useNavigation,
  DrawerActions,
} from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import Icon from 'react-native-vector-icons/MaterialIcons';
import PushNotification from 'react-native-push-notification';
import WebSocket from 'react-native-websockets';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useSelector, useDispatch } from 'react-redux';
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

// Import Redux store and actions
import { store } from './src/redux/store';
import {
  setBots,
  updateBotStatus,
  setPerformanceData,
  setAlerts,
  setUserPermissions,
} from './src/redux/actions';

// Import services
import { ApiService } from './src/services/ApiService';
import { WebSocketService } from './src/services/WebSocketService';
import { NotificationService } from './src/services/NotificationService';
import { AuthService } from './src/services/AuthService';

// Import components
import { BotCard } from './src/components/BotCard';
import { PerformanceChart } from './src/components/PerformanceChart';
import { AlertItem } from './src/components/AlertItem';
import { PermissionToggle } from './src/components/PermissionToggle';
import { LoadingSpinner } from './src/components/LoadingSpinner';

// Import screens
import DashboardScreen from './src/screens/DashboardScreen';
import BotDetailScreen from './src/screens/BotDetailScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/LoginScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const { width, height } = Dimensions.get('window');
const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();
const Drawer = createDrawerNavigator();

// Main App Component
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const dispatch = useDispatch();
  
  // Services
  const apiService = useRef(new ApiService());
  const wsService = useRef(new WebSocketService());
  const notificationService = useRef(new NotificationService());
  const authService = useRef(new AuthService());

  // Initialize app
  useEffect(() => {
    initializeApp();
    
    // Configure push notifications
    PushNotification.configure({
      onNotification: handleNotification,
      requestPermissions: Platform.OS === 'ios',
      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },
    });

    return () => {
      cleanup();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // Check authentication
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        await authService.current.validateToken(token);
        setIsAuthenticated(true);
        await loadUserData();
      }

      // Initialize notifications
      await notificationService.current.initialize();
      
      // Initialize WebSocket connection
      if (isAuthenticated) {
        connectWebSocket();
      }

      setIsLoading(false);
    } catch (error) {
      console.error('App initialization error:', error);
      setIsLoading(false);
    }
  };

  const loadUserData = async () => {
    try {
      // Load user permissions
      const permissions = await apiService.current.getUserPermissions();
      dispatch(setUserPermissions(permissions));

      // Load initial bot data
      const bots = await apiService.current.getBots();
      dispatch(setBots(bots));

      // Load performance data
      const performanceData = await apiService.current.getPerformanceData();
      dispatch(setPerformanceData(performanceData));

      // Load alerts
      const alerts = await apiService.current.getAlerts();
      dispatch(setAlerts(alerts));
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const connectWebSocket = () => {
    wsService.current.connect({
      onOpen: () => {
        setConnectionStatus('connected');
        console.log('WebSocket connected');
      },
      onMessage: handleWebSocketMessage,
      onClose: () => {
        setConnectionStatus('disconnected');
        console.log('WebSocket disconnected');
        // Attempt reconnection
        setTimeout(connectWebSocket, 5000);
      },
      onError: (error) => {
        setConnectionStatus('error');
        console.error('WebSocket error:', error);
      },
    });
  };

  const handleWebSocketMessage = useCallback((message) => {
    try {
      const data = JSON.parse(message);
      
      switch (data.type) {
        case 'bot_status_update':
          dispatch(updateBotStatus(data.payload));
          break;
        case 'performance_update':
          dispatch(setPerformanceData(data.payload));
          break;
        case 'new_alert':
          dispatch(setAlerts([data.payload, ...useSelector(state => state.alerts)]));
          // Show push notification
          notificationService.current.showAlert(data.payload);
          break;
        case 'permission_update':
          dispatch(setUserPermissions(data.payload));
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, []);

  const handleNotification = useCallback((notification) => {
    if (notification.userInteraction) {
      // User tapped notification
      const { botId, type } = notification.data;
      
      if (type === 'bot_alert') {
        navigation.navigate('BotDetail', { botId });
      } else if (type === 'system_alert') {
        navigation.navigate('Dashboard');
      }
    }
  }, []);

  const cleanup = () => {
    wsService.current.disconnect();
    notificationService.current.cleanup();
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading TigerEx...</Text>
      </View>
    );
  }

  if (!isAuthenticated) {
    return (
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer>
      <Drawer.Navigator
        drawerContent={({ navigation }) => (
          <DrawerContent navigation={navigation} />
        )}
      >
        <Drawer.Screen name="Main" component={MainTabNavigator} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
};

// Main Tab Navigator
const MainTabNavigator = () => {
  const { alerts } = useSelector(state => state);
  const alertCount = alerts.filter(alert => !alert.acknowledged).length;

  return (
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
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Alerts':
              iconName = 'notifications';
              break;
            case 'Settings':
              iconName = 'settings';
              break;
            default:
              iconName = 'help';
          }

          return (
            <Icon
              name={iconName}
              size={size}
              color={color}
            />
          );
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#f8f9fa',
          borderTopWidth: 1,
          borderTopColor: '#e9ecef',
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
        }}
      />
      <Tab.Screen
        name="Bots"
        component={BotsTabScreen}
        options={{
          tabBarLabel: 'Bots',
          tabBarBadge: alertCount > 0 ? alertCount : undefined,
        }}
      />
      <Tab.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
        }}
      />
      <Tab.Screen
        name="Alerts"
        component={AlertsTabScreen}
        options={{
          tabBarLabel: 'Alerts',
          tabBarBadge: alertCount > 0 ? alertCount : undefined,
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
};

// Custom Drawer Content
const DrawerContent = ({ navigation }) => {
  const { user, permissions } = useSelector(state => state);
  const dispatch = useDispatch();

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
            await AsyncStorage.removeItem('auth_token');
            setIsAuthenticated(false);
          },
        },
      ]
    );
  };

  const menuItems = [
    {
      title: 'Dashboard',
      icon: 'dashboard',
      onPress: () => navigation.navigate('Main'),
    },
    {
      title: 'Profile',
      icon: 'person',
      onPress: () => navigation.navigate('Profile'),
    },
    {
      title: 'Portfolio',
      icon: 'account-balance-wallet',
      onPress: () => navigation.navigate('Portfolio'),
      disabled: !permissions.portfolio_access,
    },
    {
      title: 'Reports',
      icon: 'assessment',
      onPress: () => navigation.navigate('Reports'),
      disabled: !permissions.reports_access,
    },
    {
      title: 'API Keys',
      icon: 'vpn-key',
      onPress: () => navigation.navigate('APIKeys'),
      disabled: !permissions.api_management,
    },
    {
      title: 'Settings',
      icon: 'settings',
      onPress: () => navigation.navigate('Settings'),
    },
    {
      title: 'Help & Support',
      icon: 'help',
      onPress: () => Linking.openURL('https://support.tigerex.com'),
    },
    {
      title: 'Logout',
      icon: 'logout',
      onPress: handleLogout,
    },
  ];

  return (
    <View style={styles.drawerContainer}>
      <View style={styles.drawerHeader}>
        <View style={styles.profileContainer}>
          <Icon name="account-circle" size={60} color="#007AFF" />
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{user.name || 'User'}</Text>
            <Text style={styles.profileEmail}>{user.email || 'user@tigerex.com'}</Text>
            <View style={styles.permissionBadge}>
              <Text style={styles.permissionText}>
                {user.role || 'Trader'}
              </Text>
            </View>
          </View>
        </View>
      </View>

      <ScrollView style={styles.drawerMenu}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.menuItem,
              item.disabled && styles.menuItemDisabled,
            ]}
            onPress={item.onPress}
            disabled={item.disabled}
          >
            <Icon
              name={item.icon}
              size={24}
              color={item.disabled ? '#ccc' : '#333'}
              style={styles.menuIcon}
            />
            <Text
              style={[
                styles.menuText,
                item.disabled && styles.menuTextDisabled,
              ]}
            >
              {item.title}
            </Text>
            {item.disabled && (
              <Icon name="lock" size={16} color="#ccc" />
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>

      <View style={styles.drawerFooter}>
        <Text style={styles.versionText}>Version 2.0.0</Text>
        <Text style={styles.copyrightText}>© 2024 TigerEx</Text>
      </View>
    </View>
  );
};

// Bots Tab Screen
const BotsTabScreen = ({ navigation }) => {
  const { bots, isLoading } = useSelector(state => state);
  const [refreshing, setRefreshing] = useState(false);
  const dispatch = useDispatch();

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const updatedBots = await apiService.current.getBots();
      dispatch(setBots(updatedBots));
    } catch (error) {
      console.error('Error refreshing bots:', error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Market Maker Bots</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => navigation.navigate('CreateBot')}
        >
          <Icon name="add" size={24} color="white" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {isLoading ? (
          <LoadingSpinner />
        ) : bots.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="smart-toy" size={64} color="#ccc" />
            <Text style={styles.emptyStateText}>No bots configured</Text>
            <TouchableOpacity
              style={styles.createButton}
              onPress={() => navigation.navigate('CreateBot')}
            >
              <Text style={styles.createButtonText}>Create Your First Bot</Text>
            </TouchableOpacity>
          </View>
        ) : (
          bots.map((bot) => (
            <BotCard
              key={bot.id}
              bot={bot}
              onPress={() => navigation.navigate('BotDetail', { botId: bot.id })}
              onToggle={async (enabled) => {
                try {
                  await apiService.current.toggleBot(bot.id, enabled);
                  // Update local state
                } catch (error) {
                  Alert.alert('Error', 'Failed to toggle bot status');
                }
              }}
            />
          ))
        )}
      </ScrollView>
    </View>
  );
};

// Alerts Tab Screen
const AlertsTabScreen = ({ navigation }) => {
  const { alerts, isLoading } = useSelector(state => state);
  const dispatch = useDispatch();

  const acknowledgeAlert = async (alertId) => {
    try {
      await apiService.current.acknowledgeAlert(alertId);
      dispatch(setAlerts(alerts.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      )));
    } catch (error) {
      Alert.alert('Error', 'Failed to acknowledge alert');
    }
  };

  const clearAllAlerts = async () => {
    Alert.alert(
      'Clear All Alerts',
      'Are you sure you want to clear all alerts?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.current.clearAllAlerts();
              dispatch(setAlerts([]));
            } catch (error) {
              Alert.alert('Error', 'Failed to clear alerts');
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Alerts</Text>
        {alerts.length > 0 && (
          <TouchableOpacity style={styles.clearButton} onPress={clearAllAlerts}>
            <Text style={styles.clearButtonText}>Clear All</Text>
          </TouchableOpacity>
        )}
      </View>

      <ScrollView style={styles.content}>
        {isLoading ? (
          <LoadingSpinner />
        ) : alerts.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="notifications-none" size={64} color="#ccc" />
            <Text style={styles.emptyStateText}>No alerts</Text>
            <Text style={styles.emptyStateSubtext}>
              You'll see alerts here when your bots need attention
            </Text>
          </View>
        ) : (
          alerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
              onAcknowledge={() => acknowledgeAlert(alert.id)}
              onPress={() => {
                if (alert.botId) {
                  navigation.navigate('BotDetail', { botId: alert.botId });
                }
              }}
            />
          ))
        )}
      </ScrollView>
    </View>
  );
};

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  clearButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#dc3545',
    borderRadius: 4,
  },
  clearButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyStateText: {
    marginTop: 16,
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
  },
  emptyStateSubtext: {
    marginTop: 8,
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  createButton: {
    marginTop: 24,
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  createButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  drawerContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  drawerHeader: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  profileContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileInfo: {
    marginLeft: 16,
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  profileEmail: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  permissionBadge: {
    marginTop: 8,
    backgroundColor: '#007AFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  permissionText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  drawerMenu: {
    flex: 1,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  menuItemDisabled: {
    opacity: 0.5,
  },
  menuIcon: {
    marginRight: 16,
  },
  menuText: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  menuTextDisabled: {
    color: '#ccc',
  },
  drawerFooter: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    alignItems: 'center',
  },
  versionText: {
    fontSize: 12,
    color: '#666',
  },
  copyrightText: {
    fontSize: 10,
    color: '#999',
    marginTop: 4,
  },
});

export default App;