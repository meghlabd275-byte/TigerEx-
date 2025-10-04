import React, { useState, useEffect } from 'react';
import { ArrowLeft, User, Shield, Twitter, Settings, Copy, Eye, EyeOff, Crown, TrendingUp } from 'lucide-react';

interface AccountInfo {
  user_id: string;
  username: string;
  email: string;
  binance_id: string;
  account_type: string;
  verification_status: string;
  vip_level: number;
  vip_progress: number;
  trading_volume_30d: number;
  bnb_balance: number;
  twitter_connected: boolean;
  created_at: string;
}

const AccountInfoPage: React.FC = () => {
  const [accountInfo, setAccountInfo] = useState<AccountInfo>({
    user_id: '39333599',
    username: 'User-2ede9',
    email: 'shahrukhahamedsumon@gmail.com',
    binance_id: '39333599',
    account_type: 'Regular',
    verification_status: 'Verified',
    vip_level: 0,
    vip_progress: 15.5,
    trading_volume_30d: 1250.0,
    bnb_balance: 0.0,
    twitter_connected: false,
    created_at: '2024-01-15T10:30:00Z'
  });

  const [showEmail, setShowEmail] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCopyId = () => {
    navigator.clipboard.writeText(accountInfo.binance_id);
    // Show toast notification
  };

  const handleVIPUpgrade = () => {
    console.log('Navigate to VIP upgrade');
    // Handle VIP upgrade navigation
  };

  const handleVerificationClick = () => {
    console.log('Navigate to verification');
    // Handle verification navigation
  };

  const handleSecurityClick = () => {
    console.log('Navigate to security');
    // Handle security navigation
  };

  const handleTwitterConnect = () => {
    console.log('Connect Twitter');
    // Handle Twitter connection
  };

  const maskEmail = (email: string) => {
    if (showEmail) return email;
    const [username, domain] = email.split('@');
    const maskedUsername = username.substring(0, 3) + '*'.repeat(username.length - 3);
    return `${maskedUsername}@${domain}`;
  };

  const getVIPRequirement = () => {
    const nextLevel = accountInfo.vip_level + 1;
    const requirements = {
      1: { volume: 1000, bnb: 25 },
      2: { volume: 5000, bnb: 50 },
      3: { volume: 10000, bnb: 100 }
    };
    return requirements[nextLevel as keyof typeof requirements] || { volume: 0, bnb: 0 };
  };

  const vipRequirement = getVIPRequirement();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button className="p-2 mr-3">
                <ArrowLeft className="w-6 h-6" />
              </button>
              <h1 className="text-xl font-semibold">Account Info</h1>
            </div>
            <div className="flex items-center space-x-2">
              <span className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
                {accountInfo.account_type}
              </span>
              <button className="p-2">
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-md mx-auto">
        {/* Profile Section */}
        <div className="bg-white mt-4 px-4 py-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center relative">
              <User className="w-8 h-8 text-white" />
              <button className="absolute -bottom-1 -right-1 w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold">{accountInfo.username}</h2>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-sm text-gray-600">Binance ID (UID)</span>
                <span className="font-mono text-sm">{accountInfo.binance_id}</span>
                <button onClick={handleCopyId} className="p-1">
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-sm text-gray-600">Reg.Info</span>
                <span className="text-sm">{maskEmail(accountInfo.email)}</span>
                <button onClick={() => setShowEmail(!showEmail)} className="p-1">
                  {showEmail ? <EyeOff className="w-4 h-4 text-gray-400" /> : <Eye className="w-4 h-4 text-gray-400" />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* VIP Upgrade Section */}
        <div className="bg-white mt-4 mx-4 rounded-lg overflow-hidden">
          <div className="bg-gradient-to-r from-yellow-400 to-orange-400 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Crown className="w-6 h-6 text-white" />
                <div>
                  <h3 className="text-white font-semibold">Upgrade to VIP{accountInfo.vip_level + 1}</h3>
                  <p className="text-white text-sm opacity-90">Trade more to reach the next level</p>
                </div>
              </div>
              <button 
                onClick={handleVIPUpgrade}
                className="bg-white text-orange-500 px-4 py-2 rounded-lg font-medium text-sm hover:bg-gray-50 transition-colors"
              >
                Benefits
              </button>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-white text-xs mb-2">
                <span>Progress: {accountInfo.vip_progress}%</span>
                <span>VIP{accountInfo.vip_level + 1}</span>
              </div>
              <div className="w-full bg-white bg-opacity-30 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all duration-300"
                  style={{ width: `${accountInfo.vip_progress}%` }}
                ></div>
              </div>
            </div>

            {/* VIP Requirements */}
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-white text-xs opacity-75">30-Day Volume</div>
                <div className="text-white font-semibold">${accountInfo.trading_volume_30d.toLocaleString()}</div>
                <div className="text-white text-xs opacity-75">/ ${vipRequirement.volume.toLocaleString()}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="text-white text-xs opacity-75">BNB Balance</div>
                <div className="text-white font-semibold">{accountInfo.bnb_balance} BNB</div>
                <div className="text-white text-xs opacity-75">/ {vipRequirement.bnb} BNB</div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Options */}
        <div className="bg-white mt-4 px-4 py-4">
          <div className="space-y-1">
            <button
              onClick={handleVerificationClick}
              className="w-full flex items-center justify-between py-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <User className="w-5 h-5 text-gray-600" />
                <span className="font-medium">Verifications</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-green-600">{accountInfo.verification_status}</span>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>

            <button
              onClick={handleSecurityClick}
              className="w-full flex items-center justify-between py-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <Shield className="w-5 h-5 text-gray-600" />
                <span className="font-medium">Security</span>
              </div>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <button
              onClick={handleTwitterConnect}
              className="w-full flex items-center justify-between py-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <Twitter className="w-5 h-5 text-gray-600" />
                <span className="font-medium">Twitter</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {accountInfo.twitter_connected ? 'Connected' : 'Unlinked'}
                </span>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          </div>
        </div>
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

export default AccountInfoPage;