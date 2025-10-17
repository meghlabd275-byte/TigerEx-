/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import React from 'react';
import { Home, TrendingUp, Repeat, Search, User } from 'lucide-react';
import { useRouter } from 'next/router';

const BottomNavigation: React.FC = () => {
  const router = useRouter();
  const currentPath = router.pathname;

  const navItems = [
    { icon: Home, label: 'Home', path: '/', key: 'home' },
    { icon: TrendingUp, label: 'Markets', path: '/markets', key: 'markets' },
    { icon: Repeat, label: 'Trade', path: '/trade', key: 'trade' },
    { icon: Search, label: 'Discover', path: '/discover', key: 'discover' },
    { icon: User, label: 'Assets', path: '/assets', key: 'assets' }
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(path);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-1 z-50">
      <div className="flex justify-around items-center">
        {navItems.map(({ icon: Icon, label, path, key }) => (
          <button
            key={key}
            onClick={() => router.push(path)}
            className={`flex flex-col items-center py-2 px-3 rounded-lg transition-colors ${
              isActive(path)
                ? 'text-yellow-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Icon className="w-5 h-5 mb-1" />
            <span className="text-xs font-medium">{label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default BottomNavigation;