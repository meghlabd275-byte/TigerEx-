/**
 * TigerEx Mobile App
 * Complete Crypto Exchange Platform
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Import screens
import LoginScreen from './src/screens/auth/LoginScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';
import HomeScreen from './src/screens/user/HomeScreen';
import TradingScreen from './src/screens/user/TradingScreen';
import WalletScreen from './src/screens/user/WalletScreen';
import ProfileScreen from './src/screens/user/ProfileScreen';
import AdminDashboard from './src/screens/admin/AdminDashboard';
import UserManagement from './src/screens/admin/UserManagement';
import TradingControls from './src/screens/admin/TradingControls';
import FinanceControls from './src/screens/admin/FinanceControls';

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
          else if (route.name === 'Trading') iconName = 'chart-line';
          else if (route.name === 'Wallet') iconName = 'wallet';
          else if (route.name === 'Profile') iconName = 'account';
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: 'gray',
      })}>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Wallet" component={WalletScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
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
      })}>
      <Tab.Screen name="Dashboard" component={AdminDashboard} />
      <Tab.Screen name="Users" component={UserManagement} />
      <Tab.Screen name="Trading" component={TradingControls} />
      <Tab.Screen name="Finance" component={FinanceControls} />
    </Tab.Navigator>
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