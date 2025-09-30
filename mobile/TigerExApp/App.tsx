import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { Provider as ReduxProvider } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { store } from './src/store';
import { theme } from './src/theme';

// Screens
import LoginScreen from './src/screens/Auth/LoginScreen';
import RegisterScreen from './src/screens/Auth/RegisterScreen';
import HomeScreen from './src/screens/Home/HomeScreen';
import MarketsScreen from './src/screens/Markets/MarketsScreen';
import TradeScreen from './src/screens/Trade/TradeScreen';
import PortfolioScreen from './src/screens/Portfolio/PortfolioScreen';
import WalletScreen from './src/screens/Wallet/WalletScreen';
import ProfileScreen from './src/screens/Profile/ProfileScreen';
import P2PScreen from './src/screens/P2P/P2PScreen';
import CopyTradingScreen from './src/screens/CopyTrading/CopyTradingScreen';
import EarnScreen from './src/screens/Earn/EarnScreen';
import TradingBotsScreen from './src/screens/TradingBots/TradingBotsScreen';
import LaunchpadScreen from './src/screens/Launchpad/LaunchpadScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Markets') {
            iconName = focused ? 'chart-line' : 'chart-line';
          } else if (route.name === 'Trade') {
            iconName = focused ? 'swap-horizontal' : 'swap-horizontal';
          } else if (route.name === 'Portfolio') {
            iconName = focused ? 'wallet' : 'wallet-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'account' : 'account-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Markets" component={MarketsScreen} />
      <Tab.Screen name="Trade" component={TradeScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

function AppNavigator() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Auth" component={AuthStack} />
      ) : (
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen name="Wallet" component={WalletScreen} />
          <Stack.Screen name="P2P" component={P2PScreen} />
          <Stack.Screen name="CopyTrading" component={CopyTradingScreen} />
          <Stack.Screen name="Earn" component={EarnScreen} />
          <Stack.Screen name="TradingBots" component={TradingBotsScreen} />
          <Stack.Screen name="Launchpad" component={LaunchpadScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <ReduxProvider store={store}>
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <AppNavigator />
        </NavigationContainer>
      </PaperProvider>
    </ReduxProvider>
  );
}