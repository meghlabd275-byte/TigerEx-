import React, { useState } from 'react';
import ExchangeWalletTabs from '../components/layout/ExchangeWalletTabs';
import MarketListings from '../components/exchange/MarketListings';
import WalletOverview from '../components/wallet/WalletOverview';
import BottomNavigation from '../components/layout/BottomNavigation';

const HybridExchangePage: React.FC = () => {
  const [activeMainTab, setActiveMainTab] = useState<'exchange' | 'wallet'>('exchange');
  const [activeBottomTab, setActiveBottomTab] = useState('home');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-16">
      {/* Top Navigation */}
      <ExchangeWalletTabs
        activeTab={activeMainTab}
        onTabChange={setActiveMainTab}
      />

      {/* Main Content */}
      <div className="max-w-screen-xl mx-auto">
        {activeMainTab === 'exchange' ? (
          <MarketListings />
        ) : (
          <WalletOverview />
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