import React, { useState, useEffect } from 'react';
import { Search, Grid, List, Settings, User, Bell, HelpCircle, Gift, TrendingUp, DollarSign, Info, Users, MoreHorizontal } from 'lucide-react';

interface Service {
  id: string;
  name: string;
  icon: string;
  category: string;
  description: string;
  status: 'active' | 'inactive';
}

const ServicesPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Common Function');
  const [searchQuery, setSearchQuery] = useState('');
  const [services, setServices] = useState<Service[]>([]);
  const [userProfile, setUserProfile] = useState({
    id: '39333599',
    username: 'User-2ede9',
    status: 'Regular',
    verified: true
  });

  // Service categories matching the screenshots
  const categories = [
    'Common Function',
    'Gift & Campaign', 
    'Trade',
    'Earn',
    'Finance',
    'Information',
    'Help & Support',
    'Others'
  ];

  // Services data matching the screenshots
  const servicesData: Record<string, Service[]> = {
    'Common Function': [
      { id: 'transfer', name: 'Transfer', icon: '💸', category: 'Common Function', description: 'Transfer cryptocurrencies', status: 'active' },
      { id: 'binance-wallet', name: 'Binance Wallet', icon: '💼', category: 'Common Function', description: 'Wallet management', status: 'active' },
      { id: 'buy-crypto', name: 'Buy crypto', icon: '🛒', category: 'Common Function', description: 'Purchase cryptocurrencies', status: 'active' },
      { id: 'disable-account', name: 'Disable Account', icon: '👤', category: 'Common Function', description: 'Account management', status: 'active' },
      { id: 'account-statement', name: 'Account Statement', icon: '📄', category: 'Common Function', description: 'View account history', status: 'active' },
      { id: 'demo-trading', name: 'Demo Trading', icon: '🎮', category: 'Common Function', description: 'Practice trading', status: 'active' },
      { id: 'launchpool', name: 'Launchpool', icon: '🚀', category: 'Common Function', description: 'Token launches', status: 'active' },
      { id: 'recurring-buy', name: 'Recurring Buy', icon: '🔄', category: 'Common Function', description: 'Automated purchases', status: 'active' },
      { id: 'deposit-fiat', name: 'Deposit Fiat', icon: '📥', category: 'Common Function', description: 'Deposit fiat currency', status: 'active' },
      { id: 'deposit', name: 'Deposit', icon: '⬇️', category: 'Common Function', description: 'Deposit crypto', status: 'active' },
      { id: 'referral', name: 'Referral', icon: '👥', category: 'Common Function', description: 'Referral program', status: 'active' },
      { id: 'pay', name: 'Pay', icon: '💳', category: 'Common Function', description: 'Payment services', status: 'active' },
      { id: 'orders', name: 'Orders', icon: '📋', category: 'Common Function', description: 'Order management', status: 'active' },
      { id: 'sell-to-fiat', name: 'Sell to Fiat', icon: '💰', category: 'Common Function', description: 'Convert to fiat', status: 'active' },
      { id: 'withdraw-fiat', name: 'Withdraw Fiat', icon: '🏦', category: 'Common Function', description: 'Withdraw fiat', status: 'active' },
      { id: 'security', name: 'Security', icon: '🔒', category: 'Common Function', description: 'Security settings', status: 'active' }
    ],
    'Gift & Campaign': [
      { id: 'word-of-day', name: 'Word of the Day', icon: '📝', category: 'Gift & Campaign', description: 'Daily word challenge', status: 'active' },
      { id: 'new-listing-promos', name: 'New Listing Promos', icon: '🎯', category: 'Gift & Campaign', description: 'New token promotions', status: 'active' },
      { id: 'spot-colosseum', name: 'Spot Colosseum', icon: '🏛️', category: 'Gift & Campaign', description: 'Trading competition', status: 'active' },
      { id: 'button-game', name: 'Button Game', icon: '🎮', category: 'Gift & Campaign', description: 'Interactive game', status: 'active' },
      { id: 'carnival-quest', name: 'Carnival Quest', icon: '🎪', category: 'Gift & Campaign', description: 'Quest challenges', status: 'active' },
      { id: 'refer-win-bnb', name: 'Refer & Win BNB', icon: '🏆', category: 'Gift & Campaign', description: 'BNB referral rewards', status: 'active' },
      { id: 'bnb-ath', name: 'BNB ATH', icon: '📈', category: 'Gift & Campaign', description: 'BNB all-time high', status: 'active' },
      { id: 'monthly-challenge', name: 'Monthly Challenge', icon: '📅', category: 'Gift & Campaign', description: 'Monthly competitions', status: 'active' },
      { id: 'rewards-hub', name: 'Rewards Hub', icon: '🎁', category: 'Gift & Campaign', description: 'Centralized rewards', status: 'active' },
      { id: 'futures-masters', name: 'Futures Masters', icon: '⚡', category: 'Gift & Campaign', description: 'Futures competition', status: 'active' },
      { id: 'my-gifts', name: 'My Gifts', icon: '🎀', category: 'Gift & Campaign', description: 'Personal gifts', status: 'active' },
      { id: 'learn-earn', name: 'Learn & Earn', icon: '🎓', category: 'Gift & Campaign', description: 'Educational rewards', status: 'active' },
      { id: 'red-packet', name: 'Red Packet', icon: '🧧', category: 'Gift & Campaign', description: 'Digital red packets', status: 'active' },
      { id: 'alpha-events', name: 'Alpha Events', icon: '🌟', category: 'Gift & Campaign', description: 'Alpha trading events', status: 'active' }
    ],
    'Trade': [
      { id: 'convert', name: 'Convert', icon: '🔄', category: 'Trade', description: 'Currency conversion', status: 'active' },
      { id: 'spot', name: 'Spot', icon: '📊', category: 'Trade', description: 'Spot trading', status: 'active' },
      { id: 'alpha', name: 'Alpha', icon: '⭐', category: 'Trade', description: 'Alpha trading', status: 'active' },
      { id: 'margin', name: 'Margin', icon: '📈', category: 'Trade', description: 'Margin trading', status: 'active' },
      { id: 'futures', name: 'Futures', icon: '📋', category: 'Trade', description: 'Futures trading', status: 'active' },
      { id: 'copy-trading', name: 'Copy Trading', icon: '👥', category: 'Trade', description: 'Copy other traders', status: 'active' },
      { id: 'otc', name: 'OTC', icon: '🤝', category: 'Trade', description: 'Over-the-counter', status: 'active' },
      { id: 'p2p', name: 'P2P', icon: '👤', category: 'Trade', description: 'Peer-to-peer trading', status: 'active' },
      { id: 'trading-bots', name: 'Trading Bots', icon: '🤖', category: 'Trade', description: 'Automated trading', status: 'active' },
      { id: 'convert-recurring', name: 'Convert Recurring', icon: '🔄', category: 'Trade', description: 'Recurring conversions', status: 'active' },
      { id: 'index-linked', name: 'Index-Linked', icon: '📊', category: 'Trade', description: 'Index-linked products', status: 'active' },
      { id: 'options', name: 'Options', icon: '📋', category: 'Trade', description: 'Options trading', status: 'active' }
    ],
    'Earn': [
      { id: 'earn', name: 'Earn', icon: '💰', category: 'Earn', description: 'Earning opportunities', status: 'active' },
      { id: 'sol-staking', name: 'SOL Staking', icon: '🌟', category: 'Earn', description: 'Solana staking', status: 'active' },
      { id: 'smart-arbitrage', name: 'Smart Arbitrage', icon: '🎯', category: 'Earn', description: 'Automated arbitrage', status: 'active' },
      { id: 'yield-arena', name: 'Yield Arena', icon: '🏟️', category: 'Earn', description: 'Yield competitions', status: 'active' },
      { id: 'super-mine', name: 'Super Mine', icon: '⛏️', category: 'Earn', description: 'Mining rewards', status: 'active' },
      { id: 'discount-buy', name: 'Discount Buy', icon: '💸', category: 'Earn', description: 'Discounted purchases', status: 'active' },
      { id: 'rwusd', name: 'RWUSD', icon: '💵', category: 'Earn', description: 'RWUSD stablecoin', status: 'active' },
      { id: 'bfusd', name: 'BFUSD', icon: '💴', category: 'Earn', description: 'BFUSD stablecoin', status: 'active' },
      { id: 'onchain-yields', name: 'On-chain Yields', icon: '🔗', category: 'Earn', description: 'On-chain earning', status: 'active' },
      { id: 'soft-staking', name: 'Soft Staking', icon: '📊', category: 'Earn', description: 'Flexible staking', status: 'active' },
      { id: 'simple-earn', name: 'Simple Earn', icon: '💰', category: 'Earn', description: 'Simple earning', status: 'active' },
      { id: 'pool', name: 'Pool', icon: '🏊', category: 'Earn', description: 'Liquidity pools', status: 'active' },
      { id: 'eth-staking', name: 'ETH Staking', icon: '💎', category: 'Earn', description: 'Ethereum staking', status: 'active' },
      { id: 'dual-investment', name: 'Dual Investment', icon: '♾️', category: 'Earn', description: 'Dual investment products', status: 'active' }
    ],
    'Finance': [
      { id: 'loans', name: 'Loans', icon: '🏦', category: 'Finance', description: 'Crypto loans', status: 'active' },
      { id: 'sharia-earn', name: 'Sharia Earn', icon: '🌙', category: 'Finance', description: 'Sharia-compliant earning', status: 'active' },
      { id: 'vip-loan', name: 'VIP Loan', icon: '👑', category: 'Finance', description: 'VIP lending services', status: 'active' },
      { id: 'fixed-rate-loans', name: 'Fixed Rate Loans', icon: '🔒', category: 'Finance', description: 'Fixed-rate lending', status: 'active' },
      { id: 'binance-wealth', name: 'Binance Wealth', icon: '💎', category: 'Finance', description: 'Wealth management', status: 'active' }
    ],
    'Information': [
      { id: 'chat', name: 'Chat', icon: '💬', category: 'Information', description: 'Chat system', status: 'active' },
      { id: 'square', name: 'Square', icon: '⬜', category: 'Information', description: 'Social platform', status: 'active' },
      { id: 'binance-academy', name: 'Binance Academy', icon: '🎓', category: 'Information', description: 'Educational content', status: 'active' },
      { id: 'live', name: 'Live', icon: '📺', category: 'Information', description: 'Live streaming', status: 'active' },
      { id: 'research', name: 'Research', icon: '🔬', category: 'Information', description: 'Market research', status: 'active' },
      { id: 'futures-chatroom', name: 'Futures Chatroom', icon: '💬', category: 'Information', description: 'Futures discussions', status: 'active' },
      { id: 'deposit-withdrawal-status', name: 'Deposit & Withdrawal Status', icon: '📊', category: 'Information', description: 'Transaction status', status: 'active' },
      { id: 'proof-of-reserves', name: 'Proof of Reserves', icon: '🔍', category: 'Information', description: 'Reserve verification', status: 'active' }
    ],
    'Help & Support': [
      { id: 'action-required', name: 'Action Required', icon: '⚠️', category: 'Help & Support', description: 'Required actions', status: 'active' },
      { id: 'binance-verify', name: 'Binance Verify', icon: '✅', category: 'Help & Support', description: 'Identity verification', status: 'active' },
      { id: 'support', name: 'Support', icon: '📞', category: 'Help & Support', description: 'Customer support', status: 'active' },
      { id: 'customer-service', name: 'Customer Service', icon: '🎧', category: 'Help & Support', description: 'Customer service', status: 'active' },
      { id: 'self-service', name: 'Self Service', icon: '🛠️', category: 'Help & Support', description: 'Self-service portal', status: 'active' }
    ],
    'Others': [
      { id: 'third-party-account', name: 'Third-party Account', icon: '🔗', category: 'Others', description: 'External accounts', status: 'active' },
      { id: 'affiliate', name: 'Affiliate', icon: '🤝', category: 'Others', description: 'Affiliate program', status: 'active' },
      { id: 'megadrop', name: 'Megadrop', icon: '🎯', category: 'Others', description: 'Megadrop events', status: 'active' },
      { id: 'token-unlock', name: 'Token Unlock', icon: '🔓', category: 'Others', description: 'Token unlocking', status: 'active' },
      { id: 'gift-card', name: 'Gift Card', icon: '🎁', category: 'Others', description: 'Digital gift cards', status: 'active' },
      { id: 'trading-insight', name: 'Trading Insight', icon: '📈', category: 'Others', description: 'Trading analytics', status: 'active' },
      { id: 'api-management', name: 'API Management', icon: '⚙️', category: 'Others', description: 'API management', status: 'active' },
      { id: 'fan-token', name: 'Fan Token', icon: '⚽', category: 'Others', description: 'Fan tokens', status: 'active' },
      { id: 'binance-nft', name: 'Binance NFT', icon: '🖼️', category: 'Others', description: 'NFT marketplace', status: 'active' },
      { id: 'marketplace', name: 'Marketplace', icon: '🏪', category: 'Others', description: 'Digital marketplace', status: 'active' },
      { id: 'babt', name: 'BABT', icon: '🎖️', category: 'Others', description: 'BABT tokens', status: 'active' },
      { id: 'send-cash', name: 'Send Cash', icon: '💸', category: 'Others', description: 'Cash transfer', status: 'active' },
      { id: 'charity', name: 'Charity', icon: '❤️', category: 'Others', description: 'Charitable donations', status: 'active' }
    ]
  };

  // Shortcut services
  const shortcuts = [
    { id: 'loans', name: 'Loans', icon: '🏦' },
    { id: 'rewards-hub', name: 'Rewards Hub', icon: '🎁' },
    { id: 'referral', name: 'Referral', icon: '👥' },
    { id: 'gift-card', name: 'Gift Card', icon: '🎁' },
    { id: 'red-packet', name: 'Red Packet', icon: '🧧' },
    { id: 'futures', name: 'Futures', icon: '📋' },
    { id: 'spot', name: 'Spot', icon: '📊' },
    { id: 'edit', name: 'Edit', icon: '✏️' }
  ];

  // Recommended services
  const recommended = [
    { id: 'new-listing-promos', name: 'New Listing Promos', icon: '🎯' },
    { id: 'simple-earn', name: 'Simple Earn', icon: '💰' },
    { id: 'referral', name: 'Referral', icon: '👥' },
    { id: 'alpha-events', name: 'Alpha Events', icon: '🌟' },
    { id: 'p2p', name: 'P2P', icon: '👤' },
    { id: 'square', name: 'Square', icon: '⬜' }
  ];

  useEffect(() => {
    // Initialize services
    const allServices = Object.values(servicesData).flat();
    setServices(allServices);
  }, []);

  const filteredServices = servicesData[activeTab]?.filter(service =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleServiceClick = (service: Service) => {
    console.log(`Clicked on ${service.name}`);
    // Handle service navigation
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <button className="p-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold">Services</h1>
            <div className="flex items-center space-x-2">
              <button className="p-2">
                <Bell className="w-5 h-5" />
              </button>
              <button className="p-2">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* User Profile Section */}
      <div className="bg-white border-b">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-sm text-gray-500">ID: {userProfile.id}</div>
                <div className="font-semibold">{userProfile.username}</div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{userProfile.status}</span>
                  {userProfile.verified && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Verified</span>
                  )}
                </div>
              </div>
            </div>
            <button className="p-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white border-b">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search more services"
              className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Shortcuts Section */}
      <div className="bg-white border-b">
        <div className="max-w-md mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">Shortcut</h2>
            <button className="text-gray-400">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-600">Add to Homepage</span>
            <div className="w-12 h-6 bg-gray-200 rounded-full relative">
              <div className="w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5 shadow"></div>
            </div>
          </div>
          <div className="grid grid-cols-6 gap-4">
            {shortcuts.map((service) => (
              <button
                key={service.id}
                onClick={() => handleServiceClick(service as Service)}
                className="flex flex-col items-center space-y-1"
              >
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-lg">
                  {service.icon}
                </div>
              </button>
            ))}
            <button className="flex flex-col items-center space-y-1">
              <div className="w-10 h-10 bg-yellow-400 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Recommend Section */}
      <div className="bg-white border-b">
        <div className="max-w-md mx-auto px-4 py-4">
          <h2 className="font-semibold mb-3">Recommend</h2>
          <div className="grid grid-cols-4 gap-4">
            {recommended.map((service) => (
              <button
                key={service.id}
                onClick={() => handleServiceClick(service as Service)}
                className="flex flex-col items-center space-y-2"
              >
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-lg">
                  {service.icon}
                </div>
                <span className="text-xs text-center">{service.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-md mx-auto">
          <div className="flex overflow-x-auto scrollbar-hide">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setActiveTab(category)}
                className={`flex-shrink-0 px-4 py-3 text-sm font-medium border-b-2 ${
                  activeTab === category
                    ? 'text-yellow-600 border-yellow-600'
                    : 'text-gray-500 border-transparent hover:text-gray-700'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="max-w-md mx-auto px-4 py-6">
        <h2 className="font-semibold mb-4">{activeTab}</h2>
        <div className="grid grid-cols-4 gap-4">
          {filteredServices.map((service) => (
            <button
              key={service.id}
              onClick={() => handleServiceClick(service)}
              className="flex flex-col items-center space-y-2 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-lg">
                {service.icon}
              </div>
              <span className="text-xs text-center leading-tight">{service.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* More Services Button */}
      <div className="max-w-md mx-auto px-4 pb-6">
        <button className="w-full py-3 bg-gray-100 rounded-lg text-gray-600 font-medium">
          More Services
        </button>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t">
        <div className="max-w-md mx-auto px-4 py-2">
          <div className="flex justify-around">
            <button className="p-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button className="p-3">
              <div className="w-6 h-6 bg-gray-300 rounded-full"></div>
            </button>
            <button className="p-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServicesPage;