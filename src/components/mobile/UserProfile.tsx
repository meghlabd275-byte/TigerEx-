import React from 'react';
import { 
  ChevronRight, 
  Mail, 
  Lock, 
  Shield, 
  Activity, 
  Smartphone, 
  Users, 
  AlertTriangle,
  Settings,
  UserCheck,
  Share2,
  Eye,
  Trash2
} from 'lucide-react';

interface UserProfileProps {
  user: {
    id: string;
    username: string;
    email: string;
    isVerified: boolean;
    avatar?: string;
  };
  onNavigate: (section: string) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onNavigate }) => {
  const profileStats = {
    trades: 2,
    completionRate: '100.00%',
    avgReleaseTime: '7.22 m',
    avgPayTime: '5.15 m'
  };

  const menuSections = [
    {
      title: 'Account Security',
      items: [
        { icon: Mail, label: 'Email', value: user.email, action: 'email-settings' },
        { icon: Lock, label: 'Password', action: 'password-settings' },
        { icon: Shield, label: 'Emergency Contact', action: 'emergency-contact' },
        { icon: AlertTriangle, label: 'Anti-Phishing Code', action: 'anti-phishing' },
        { icon: Activity, label: 'Account Activities', action: 'account-activities' },
        { icon: Lock, label: 'Auto-Lock', value: 'Never', action: 'auto-lock' },
        { icon: Smartphone, label: 'App Authorization', action: 'app-authorization' },
        { icon: Users, label: 'Account Connections', action: 'account-connections' },
        { icon: Shield, label: '2FA Verification Strategy', action: '2fa-settings' },
        { icon: Settings, label: 'Devices', action: 'device-management' },
        { icon: UserCheck, label: 'Manage Account', action: 'manage-account' }
      ]
    },
    {
      title: 'Trading & Activity',
      items: [
        { icon: Activity, label: 'Received Feedback', value: '35', action: 'feedback' },
        { icon: Settings, label: 'Payment Method(s)', value: '11', action: 'payment-methods' },
        { icon: Shield, label: 'Restrictions Removal Center', action: 'restrictions' },
        { icon: Users, label: 'Follows', action: 'follows' },
        { icon: Trash2, label: 'Blocked Users', action: 'blocked-users' },
        { icon: Share2, label: 'Ad Sharing Code', action: 'sharing-code' },
        { icon: Eye, label: 'Recently Viewed', action: 'recently-viewed' }
      ]
    }
  ];

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Profile Header */}
      <div className="bg-white p-6">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center">
            <span className="text-white text-xl font-bold">
              {user.username.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-gray-900">{user.username}</h2>
              <button className="p-1">
                <Share2 className="w-4 h-4 text-gray-400" />
              </button>
            </div>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                Regular
              </span>
              {user.isVerified && (
                <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                  Verified
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{profileStats.trades}</div>
            <div className="text-sm text-gray-500">30d Trades</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{profileStats.completionRate}</div>
            <div className="text-sm text-gray-500">30d Completion Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{profileStats.avgReleaseTime}</div>
            <div className="text-sm text-gray-500">Avg. Release Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{profileStats.avgPayTime}</div>
            <div className="text-sm text-gray-500">Avg. Pay Time</div>
          </div>
        </div>

        <button 
          onClick={() => onNavigate('more-stats')}
          className="w-full mt-4 text-center text-blue-600 text-sm font-medium"
        >
          More →
        </button>
      </div>

      {/* Menu Sections */}
      <div className="mt-4 space-y-4">
        {menuSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="bg-white">
            <div className="px-4 py-3 border-b border-gray-100">
              <h3 className="font-medium text-gray-900">{section.title}</h3>
            </div>
            <div className="divide-y divide-gray-100">
              {section.items.map((item, itemIndex) => (
                <button
                  key={itemIndex}
                  onClick={() => onNavigate(item.action)}
                  className="w-full px-4 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <item.icon className="w-5 h-5 text-gray-600" />
                    <span className="text-gray-900">{item.label}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {item.value && (
                      <span className="text-sm text-gray-500">{item.value}</span>
                    )}
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* User ID */}
      <div className="bg-white mt-4 p-4">
        <div className="text-sm text-gray-500">
          ID: {user.id}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;