import React, { useState } from 'react';
import { useWallet } from '../contexts/WalletContext';
import ExchangeWalletTabs from '../components/layout/ExchangeWalletTabs';
import ExchangeModeToggle from '../components/layout/ExchangeModeToggle';
import MarketListings from '../components/exchange/MarketListings';
import WalletOverview from '../components/wallet/WalletOverview';
import WalletSetup from '../components/wallet/WalletSetup';
import DEXSwap from '../components/dex/DEXSwap';
import BottomNavigation from '../components/layout/BottomNavigation';

const HybridExchangePage: React.FC = () => {
  const { isConnected, exchangeMode } = useWallet();
  const [activeMainTab, setActiveMainTab] = useState<'exchange' | 'wallet'>('exchange');
  const [activeBottomTab, setActiveBottomTab] = useState('home');

  // Handle tab changes
  const handleTabChange = (tab: 'exchange' | 'wallet') => {
    setActiveMainTab(tab);
    
    // If switching to wallet tab and no wallet connected, show wallet setup
    if (tab === 'wallet' && !isConnected) {
      // Will be handled by the conditional rendering below
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
              <WalletSetup />
            ) : (
              <>
                <ExchangeModeToggle />
                <WalletOverview />
              </>
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