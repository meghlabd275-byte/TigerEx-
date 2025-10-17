/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

/**
 * TigerEx Mobile App
 * Complete Crypto Exchange Platform
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Import auth screens
import LoginScreen from './src/screens/auth/LoginScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';

// Import user screens
import HomeScreen from './src/screens/user/HomeScreen';
import TradingScreen from './src/screens/user/TradingScreen';
import WalletScreen from './src/screens/user/WalletScreen';
import ProfileScreen from './src/screens/user/ProfileScreen';

// Import admin screens
import AdminDashboard from './src/screens/admin/AdminDashboard';
import UserManagement from './src/screens/admin/UserManagement';
import TradingControls from './src/screens/admin/TradingControls';
import FinanceControls from './src/screens/admin/FinanceControls';

// Import additional screens
import MarketsScreen from './src/screens/markets/MarketsScreen';
import SpotTradingScreen from './src/screens/trading/SpotTradingScreen';
import EarnScreen from './src/screens/earn/EarnScreen';
import P2PScreen from './src/screens/p2p/P2PScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// User Tab Navigator
function UserTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;
          if (route.name === 'Home') iconName = 'home';
          else if (route.name === 'Markets') iconName = 'chart-box';
          else if (route.name === 'Trading') iconName = 'chart-line';
          else if (route.name === 'Earn') iconName = 'trending-up';
          else if (route.name === 'P2P') iconName = 'account-group';
          else if (route.name === 'Wallet') iconName = 'wallet';
          else if (route.name === 'Profile') iconName = 'account';
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          paddingBottom: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 10,
        },
      })}>
      <Tab.Screen name="Home" component={HomeScreen} options={{headerShown: false}} />
      <Tab.Screen name="Markets" component={MarketsScreen} options={{headerShown: false}} />
      <Tab.Screen name="Trading" component={TradingScreen} options={{headerShown: false}} />
      <Tab.Screen name="Earn" component={EarnScreen} options={{headerShown: false}} />
      <Tab.Screen name="P2P" component={P2PScreen} options={{headerShown: false}} />
      <Tab.Screen name="Wallet" component={WalletScreen} options={{headerShown: false}} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{headerShown: false}} />
    </Tab.Navigator>
  );
}

// Admin Tab Navigator
function AdminTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;
          if (route.name === 'Dashboard') iconName = 'view-dashboard';
          else if (route.name === 'Users') iconName = 'account-group';
          else if (route.name === 'Trading') iconName = 'chart-box';
          else if (route.name === 'Finance') iconName = 'cash-multiple';
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#FF9800',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          paddingBottom: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
        },
      })}>
      <Tab.Screen name="Dashboard" component={AdminDashboard} options={{headerShown: false}} />
      <Tab.Screen name="Users" component={UserManagement} options={{headerShown: false}} />
      <Tab.Screen name="Trading" component={TradingControls} options={{headerShown: false}} />
      <Tab.Screen name="Finance" component={FinanceControls} options={{headerShown: false}} />
    </Tab.Navigator>
  );
}

// Main Stack Navigator
function MainStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="UserApp"
        component={UserTabs}
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="AdminApp"
        component={AdminTabs}
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="SpotTrading"
        component={SpotTradingScreen}
        options={{headerShown: false}}
      />
    </Stack.Navigator>
  );
}

// Main App
export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{headerShown: false}}
        />
        <Stack.Screen
          name="Register"
          component={RegisterScreen}
          options={{headerShown: false}}
        />
        <Stack.Screen
          name="Main"
          component={MainStack}
          options={{headerShown: false}}
        />
        <Stack.Screen
          name="UserApp"
          component={UserTabs}
          options={{headerShown: false}}
        />
        <Stack.Screen
          name="AdminApp"
          component={AdminTabs}
          options={{headerShown: false}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}