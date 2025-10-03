import React, { useState } from 'react';
import { useWallet } from '../contexts/WalletContext';
import ExchangeWalletTabs from '../components/layout/ExchangeWalletTabs';
import ExchangeModeToggle from '../components/layout/ExchangeModeToggle';
import MarketListings from '../components/exchange/MarketListings';
import WalletOverview from '../components/wallet/WalletOverview';
import WalletSetup from '../components/wallet/WalletSetup';
import DEXSwap from '../components/dex/DEXSwap';
import DEXWalletHome from '../components/dex/DEXWalletHome';
import Web3Onboarding from '../components/dex/Web3Onboarding';
import BottomNavigation from '../components/layout/BottomNavigation';

const HybridExchangePage: React.FC = () => {
  const { isConnected, exchangeMode } = useWallet();
  const [activeMainTab, setActiveMainTab] = useState<'exchange' | 'wallet'>('exchange');
  const [activeBottomTab, setActiveBottomTab] = useState('home');
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Handle tab changes
  const handleTabChange = (tab: 'exchange' | 'wallet') => {
    setActiveMainTab(tab);
    
    // If switching to wallet tab and no wallet connected, show onboarding
    if (tab === 'wallet' && !isConnected) {
      setShowOnboarding(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-16">
      {/* Top Navigation */}
      <ExchangeWalletTabs
        activeTab={activeMainTab}
        onTabChange={handleTabChange}
      />

      {/* Main Content */}
      <div className="max-w-screen-xl mx-auto">
        {activeMainTab === 'exchange' ? (
          <>
            {/* Exchange Mode Toggle */}
            <ExchangeModeToggle />
            
            {/* Show CEX or DEX based on mode */}
            {exchangeMode === 'cex' ? (
              <MarketListings />
            ) : (
              <DEXSwap />
            )}
          </>
        ) : (
          <>
            {/* Wallet Tab */}
            {!isConnected ? (
              showOnboarding ? (
                <Web3Onboarding />
              ) : (
                <WalletSetup />
              )
            ) : (
              <DEXWalletHome />
            )}
          </>
        )}
      </div>

      {/* Bottom Navigation */}
      <BottomNavigation
        activeTab={activeBottomTab}
        onTabChange={setActiveBottomTab}
      />
    </div>
  );
};

export default HybridExchangePage;