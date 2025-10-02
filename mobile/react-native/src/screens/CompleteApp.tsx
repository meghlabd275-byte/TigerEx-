import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Provider } from 'react-redux';
import { store } from '../store/store';
import { ThemeProvider } from '../theme/ThemeProvider';

// Import all screens
import SplashScreen from './auth/SplashScreen';
import LoginScreen from './auth/LoginScreen';
import RegisterScreen from './auth/RegisterScreen';
import KYCVerificationScreen from './auth/KYCVerificationScreen';
import BiometricSetupScreen from './auth/BiometricSetupScreen';

// Main app screens
import DashboardScreen from './main/DashboardScreen';
import SpotTradingScreen from './trading/SpotTradingScreen';
import FuturesTradingScreen from './trading/FuturesTradingScreen';
import OptionsTradingScreen from './trading/OptionsTradingScreen';
import TradingBotsScreen from './trading/TradingBotsScreen';
import CopyTradingScreen from './trading/CopyTradingScreen';

// Wallet screens
import WalletScreen from './wallet/WalletScreen';
import DepositScreen from './wallet/DepositScreen';
import WithdrawScreen from './wallet/WithdrawScreen';
import TransferScreen from './wallet/TransferScreen';
import TransactionHistoryScreen from './wallet/TransactionHistoryScreen';

// Earn screens
import EarnScreen from './earn/EarnScreen';
import StakingScreen from './earn/StakingScreen';
import SavingsScreen from './earn/SavingsScreen';
import YieldFarmingScreen from './earn/YieldFarmingScreen';
import DualInvestmentScreen from './earn/DualInvestmentScreen';

// NFT screens
import NFTMarketplaceScreen from './nft/NFTMarketplaceScreen';
import NFTCollectionScreen from './nft/NFTCollectionScreen';
import NFTDetailScreen from './nft/NFTDetailScreen';
import CreateNFTScreen from './nft/CreateNFTScreen';
import NFTAuctionScreen from './nft/NFTAuctionScreen';

// P2P screens
import P2PTradingScreen from './p2p/P2PTradingScreen';
import P2POrderScreen from './p2p/P2POrderScreen';
import P2PChatScreen from './p2p/P2PChatScreen';

// Card screens
import CryptoCardScreen from './cards/CryptoCardScreen';
import CardManagementScreen from './cards/CardManagementScreen';
import CardTransactionsScreen from './cards/CardTransactionsScreen';

// Settings screens
import SettingsScreen from './settings/SettingsScreen';
import SecuritySettingsScreen from './settings/SecuritySettingsScreen';
import NotificationSettingsScreen from './settings/NotificationSettingsScreen';
import APISettingsScreen from './settings/APISettingsScreen';

// Admin screens
import AdminDashboardScreen from './admin/AdminDashboardScreen';
import UserManagementScreen from './admin/UserManagementScreen';
import TradingManagementScreen from './admin/TradingManagementScreen';
import AssetManagementScreen from './admin/AssetManagementScreen';
import SystemMonitoringScreen from './admin/SystemMonitoringScreen';

const Stack = createNativeStackNavigator();

const CompleteApp = () => {
  return (
    <Provider store={store}>
      <ThemeProvider>
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName="Splash"
            screenOptions={{
              headerShown: false,
              animation: 'slide_from_right',
            }}
          >
            {/* Auth Stack */}
            <Stack.Screen name="Splash" component={SplashScreen} />
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
            <Stack.Screen name="KYCVerification" component={KYCVerificationScreen} />
            <Stack.Screen name="BiometricSetup" component={BiometricSetupScreen} />

            {/* Main App Stack */}
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="SpotTrading" component={SpotTradingScreen} />
            <Stack.Screen name="FuturesTrading" component={FuturesTradingScreen} />
            <Stack.Screen name="OptionsTrading" component={OptionsTradingScreen} />
            <Stack.Screen name="TradingBots" component={TradingBotsScreen} />
            <Stack.Screen name="CopyTrading" component={CopyTradingScreen} />

            {/* Wallet Stack */}
            <Stack.Screen name="Wallet" component={WalletScreen} />
            <Stack.Screen name="Deposit" component={DepositScreen} />
            <Stack.Screen name="Withdraw" component={WithdrawScreen} />
            <Stack.Screen name="Transfer" component={TransferScreen} />
            <Stack.Screen name="TransactionHistory" component={TransactionHistoryScreen} />

            {/* Earn Stack */}
            <Stack.Screen name="Earn" component={EarnScreen} />
            <Stack.Screen name="Staking" component={StakingScreen} />
            <Stack.Screen name="Savings" component={SavingsScreen} />
            <Stack.Screen name="YieldFarming" component={YieldFarmingScreen} />
            <Stack.Screen name="DualInvestment" component={DualInvestmentScreen} />

            {/* NFT Stack */}
            <Stack.Screen name="NFTMarketplace" component={NFTMarketplaceScreen} />
            <Stack.Screen name="NFTCollection" component={NFTCollectionScreen} />
            <Stack.Screen name="NFTDetail" component={NFTDetailScreen} />
            <Stack.Screen name="CreateNFT" component={CreateNFTScreen} />
            <Stack.Screen name="NFTAuction" component={NFTAuctionScreen} />

            {/* P2P Stack */}
            <Stack.Screen name="P2PTrading" component={P2PTradingScreen} />
            <Stack.Screen name="P2POrder" component={P2POrderScreen} />
            <Stack.Screen name="P2PChat" component={P2PChatScreen} />

            {/* Card Stack */}
            <Stack.Screen name="CryptoCard" component={CryptoCardScreen} />
            <Stack.Screen name="CardManagement" component={CardManagementScreen} />
            <Stack.Screen name="CardTransactions" component={CardTransactionsScreen} />

            {/* Settings Stack */}
            <Stack.Screen name="Settings" component={SettingsScreen} />
            <Stack.Screen name="SecuritySettings" component={SecuritySettingsScreen} />
            <Stack.Screen name="NotificationSettings" component={NotificationSettingsScreen} />
            <Stack.Screen name="APISettings" component={APISettingsScreen} />

            {/* Admin Stack */}
            <Stack.Screen name="AdminDashboard" component={AdminDashboardScreen} />
            <Stack.Screen name="UserManagement" component={UserManagementScreen} />
            <Stack.Screen name="TradingManagement" component={TradingManagementScreen} />
            <Stack.Screen name="AssetManagement" component={AssetManagementScreen} />
            <Stack.Screen name="SystemMonitoring" component={SystemMonitoringScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </ThemeProvider>
    </Provider>
  );
};

export default CompleteApp;