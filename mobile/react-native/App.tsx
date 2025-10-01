import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { ThemeProvider, useAppTheme } from './src/contexts/ThemeContext';
import { WebSocketProvider } from './src/contexts/WebSocketContext';

// Import screens
import LoginScreen from './src/screens/auth/LoginScreen';
import RegisterScreen from './src/screens/auth/RegisterScreen';
import ForgotPasswordScreen from './src/screens/auth/ForgotPasswordScreen';
import BiometricAuthScreen from './src/screens/auth/BiometricAuthScreen';

// User screens
import HomeScreen from './src/screens/user/HomeScreen';
import MarketsScreen from './src/screens/user/MarketsScreen';
import TradingScreen from './src/screens/user/TradingScreen';
import WalletScreen from './src/screens/user/WalletScreen';
import ProfileScreen from './src/screens/user/ProfileScreen';

// Trading screens
import SpotTradingScreen from './src/screens/trading/SpotTradingScreen';
import FuturesTradingScreen from './src/screens/trading/FuturesTradingScreen';
import MarginTradingScreen from './src/screens/trading/MarginTradingScreen';
import CopyTradingScreen from './src/screens/trading/CopyTradingScreen';
import GridTradingScreen from './src/screens/trading/GridTradingScreen';

// Admin screens
import AdminDashboardScreen from './src/screens/admin/AdminDashboardScreen';
import UserManagementScreen from './src/screens/admin/UserManagementScreen';
import TradingManagementScreen from './src/screens/admin/TradingManagementScreen';
import FinancialManagementScreen from './src/screens/admin/FinancialManagementScreen';
import SystemSettingsScreen from './src/screens/admin/SystemSettingsScreen';

// Feature screens
import StakingScreen from './src/screens/features/StakingScreen';
import NFTScreen from './src/screens/features/NFTScreen';
import DeFiScreen from './src/screens/features/DeFiScreen';
import AutoInvestScreen from './src/screens/features/AutoInvestScreen';
import CryptoCardScreen from './src/screens/features/CryptoCardScreen';

// Settings screens
import SettingsScreen from './src/screens/settings/SettingsScreen';
import SecuritySettingsScreen from './src/screens/settings/SecuritySettingsScreen';
import NotificationSettingsScreen from './src/screens/settings/NotificationSettingsScreen';
import KYCSettingsScreen from './src/screens/settings/KYCSettingsScreen';

// Components
import BottomTabBar from './src/components/BottomTabBar';
import LoadingSpinner from './src/components/LoadingSpinner';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// User Tab Navigator
const UserTabNavigator = () => {
  return (
    <Tab.Navigator
      tabBar={(props) => <BottomTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Markets" component={MarketsScreen} />
      <Tab.Screen name="Trading" component={TradingScreen} />
      <Tab.Screen name="Wallet" component={WalletScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
};

// Admin Tab Navigator
const AdminTabNavigator = () => {
  return (
    <Tab.Navigator
      tabBar={(props) => <BottomTabBar {...props} isAdmin={true} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen name="Dashboard" component={AdminDashboardScreen} />
      <Tab.Screen name="Users" component={UserManagementScreen} />
      <Tab.Screen name="Trading" component={TradingManagementScreen} />
      <Tab.Screen name="Finance" component={FinancialManagementScreen} />
      <Tab.Screen name="Settings" component={SystemSettingsScreen} />
    </Tab.Navigator>
  );
};

// Main App Navigator
const AppNavigator = () => {
  const { user, isLoading } = useAuth();
  const { theme } = useAppTheme();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: theme.colors.background },
      }}
    >
      {!user ? (
        // Auth Stack
        <>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          <Stack.Screen name="BiometricAuth" component={BiometricAuthScreen} />
        </>
      ) : user.role === 'admin' ? (
        // Admin Stack
        <>
          <Stack.Screen name="AdminTabs" component={AdminTabNavigator} />
          <Stack.Screen name="UserManagement" component={UserManagementScreen} />
          <Stack.Screen name="TradingManagement" component={TradingManagementScreen} />
          <Stack.Screen name="FinancialManagement" component={FinancialManagementScreen} />
          <Stack.Screen name="SystemSettings" component={SystemSettingsScreen} />
        </>
      ) : (
        // User Stack
        <>
          <Stack.Screen name="UserTabs" component={UserTabNavigator} />
          <Stack.Screen name="SpotTrading" component={SpotTradingScreen} />
          <Stack.Screen name="FuturesTrading" component={FuturesTradingScreen} />
          <Stack.Screen name="MarginTrading" component={MarginTradingScreen} />
          <Stack.Screen name="CopyTrading" component={CopyTradingScreen} />
          <Stack.Screen name="GridTrading" component={GridTradingScreen} />
          <Stack.Screen name="Staking" component={StakingScreen} />
          <Stack.Screen name="NFT" component={NFTScreen} />
          <Stack.Screen name="DeFi" component={DeFiScreen} />
          <Stack.Screen name="AutoInvest" component={AutoInvestScreen} />
          <Stack.Screen name="CryptoCard" component={CryptoCardScreen} />
          <Stack.Screen name="Settings" component={SettingsScreen} />
          <Stack.Screen name="SecuritySettings" component={SecuritySettingsScreen} />
          <Stack.Screen name="NotificationSettings" component={NotificationSettingsScreen} />
          <Stack.Screen name="KYCSettings" component={KYCSettingsScreen} />
        </>
      )}
    </Stack.Navigator>
  );
};

// Main App Component
const App: React.FC = () => {
  const theme = {
    ...DefaultTheme,
    colors: {
      ...DefaultTheme.colors,
      primary: '#1976d2',
      secondary: '#dc004e',
    },
  };

  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <PaperProvider theme={theme}>
              <NavigationContainer>
                <AppNavigator />
              </NavigationContainer>
              <StatusBar style="auto" />
            </PaperProvider>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
};

export default App;