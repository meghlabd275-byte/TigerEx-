'use client';

import React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { 
  Home, 
  TrendingUp, 
  ArrowLeftRight, 
  FileText, 
  Wallet 
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  path: string;
}

const navItems: NavItem[] = [
  {
    id: 'home',
    label: 'Home',
    icon: Home,
    path: '/',
  },
  {
    id: 'markets',
    label: 'Markets',
    icon: TrendingUp,
    path: '/markets',
  },
  {
    id: 'trade',
    label: 'Trade',
    icon: ArrowLeftRight,
    path: '/trade',
  },
  {
    id: 'futures',
    label: 'Futures',
    icon: FileText,
    path: '/futures',
  },
  {
    id: 'assets',
    label: 'Assets',
    icon: Wallet,
    path: '/assets',
  },
];

export default function BottomNavigation() {
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 md:hidden">
      <div className="flex items-center justify-around py-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          
          return (
            <button
              key={item.id}
              onClick={() => handleNavigation(item.path)}
              className={`mobile-tab ${isActive ? 'mobile-tab-active' : ''}`}
            >
              <Icon 
                size={20} 
                className={isActive ? 'text-primary' : 'text-gray-500'} 
              />
              <span 
                className={`text-xs ${
                  isActive ? 'text-primary font-medium' : 'text-gray-500'
                }`}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}