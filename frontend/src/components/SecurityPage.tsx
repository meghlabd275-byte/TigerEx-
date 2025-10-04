import React, { useState, useEffect } from 'react';
import { ArrowLeft, Shield, Smartphone, Mail, Lock, Key, AlertTriangle, CheckCircle, Settings } from 'lucide-react';

interface SecuritySettings {
  passkeys_enabled: boolean;
  authenticator_enabled: boolean;
  email_2fa_enabled: boolean;
  password_enabled: boolean;
  emergency_contact?: string;
  anti_phishing_code?: string;
  auto_lock_enabled: boolean;
  auto_lock_duration: number;
}

const SecurityPage: React.FC = () => {
  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    passkeys_enabled: true,
    authenticator_enabled: true,
    email_2fa_enabled: true,
    password_enabled: false,
    auto_lock_enabled: false,
    auto_lock_duration: 30
  });

  const [loading, setLoading] = useState(false);

  const securityOptions = [
    {
      id: 'passkeys',
      name: 'Passkeys (Biometrics)',
      description: 'Use biometric authentication',
      icon: <Key className="w-6 h-6" />,
      enabled: securitySettings.passkeys_enabled,
      recommended: true
    },
    {
      id: 'authenticator',
      name: 'Authenticator App',
      description: 'Use authenticator app for 2FA',
      icon: <Shield className="w-6 h-6" />,
      enabled: securitySettings.authenticator_enabled,
      recommended: false
    },
    {
      id: 'email',
      name: 'Email',
      description: 'Email verification for security',
      icon: <Mail className="w-6 h-6" />,
      enabled: securitySettings.email_2fa_enabled,
      recommended: false
    },
    {
      id: 'password',
      name: 'Password',
      description: 'Password-based authentication',
      icon: <Lock className="w-6 h-6" />,
      enabled: securitySettings.password_enabled,
      recommended: false
    }
  ];

  const additionalSecurityOptions = [
    {
      id: 'emergency_contact',
      name: 'Emergency Contact',
      description: 'Set emergency contact for account recovery',
      icon: <AlertTriangle className="w-5 h-5" />
    },
    {
      id: 'anti_phishing',
      name: 'Anti-Phishing Code',
      description: 'Protect against phishing attacks',
      icon: <Shield className="w-5 h-5" />
    },
    {
      id: 'account_activities',
      name: 'Account Activities',
      description: 'View recent account activities',
      icon: <Settings className="w-5 h-5" />
    },
    {
      id: 'auto_lock',
      name: 'Auto-Lock',
      description: 'Automatically lock account after inactivity',
      icon: <Lock className="w-5 h-5" />,
      status: securitySettings.auto_lock_enabled ? 'Enabled' : 'Never'
    },
    {
      id: 'app_authorization',
      name: 'App Authorization',
      description: 'Manage authorized applications',
      icon: <Smartphone className="w-5 h-5" />
    },
    {
      id: 'account_connections',
      name: 'Account Connections',
      description: 'Manage connected accounts',
      icon: <Settings className="w-5 h-5" />
    },
    {
      id: '2fa_strategy',
      name: '2FA Verification Strategy',
      description: 'Configure 2FA verification methods',
      icon: <Shield className="w-5 h-5" />
    },
    {
      id: 'devices',
      name: 'Devices',
      description: 'Manage trusted devices',
      icon: <Smartphone className="w-5 h-5" />
    },
    {
      id: 'manage_account',
      name: 'Manage Account',
      description: 'Account management settings',
      icon: <Settings className="w-5 h-5" />
    }
  ];

  const handleToggle2FA = async (optionId: string) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSecuritySettings(prev => ({
        ...prev,
        [`${optionId}_enabled`]: !prev[`${optionId}_enabled` as keyof SecuritySettings]
      }));
    } catch (error) {
      console.error('Error toggling 2FA:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSecurityOptionClick = (optionId: string) => {
    console.log(`Clicked on ${optionId}`);
    // Handle navigation to specific security settings
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center">
            <button className="p-2 mr-3">
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1 className="text-xl font-semibold">Security</h1>
          </div>
        </div>
      </header>

      <div className="max-w-md mx-auto">
        {/* Two-Factor Authentication Section */}
        <div className="bg-white mt-4 px-4 py-6">
          <h2 className="text-lg font-semibold mb-2">Two-Factor Authentication (2FA)</h2>
          <p className="text-gray-600 text-sm mb-6">
            To protect your account, it is recommended to enable at least two forms of 2FA.
          </p>

          <div className="space-y-4">
            {securityOptions.map((option) => (
              <div key={option.id} className="flex items-center justify-between py-3">
                <div className="flex items-center space-x-3">
                  <div className="text-gray-600">
                    {option.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{option.name}</span>
                      {option.recommended && (
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                          Recommended
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center">
                  {option.enabled && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Security Options */}
        <div className="bg-white mt-4 px-4 py-4">
          <div className="space-y-1">
            {additionalSecurityOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSecurityOptionClick(option.id)}
                className="w-full flex items-center justify-between py-3 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-gray-600">
                    {option.icon}
                  </div>
                  <span className="font-medium text-left">{option.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  {option.status && (
                    <span className="text-sm text-gray-500">{option.status}</span>
                  )}
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            ))}
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

export default SecurityPage;