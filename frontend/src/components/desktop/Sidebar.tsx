'use client';

import React, { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { 
  Home, 
  Wallet, 
  FileText, 
  Gift, 
  Users, 
  User, 
  Users2, 
  Settings,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  path?: string;
  children?: SidebarItem[];
  expandable?: boolean;
}

const sidebarItems: SidebarItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    path: '/dashboard',
  },
  {
    id: 'assets',
    label: 'Assets',
    icon: Wallet,
    expandable: true,
    children: [
      { id: 'overview', label: 'Overview', icon: Home, path: '/assets/overview' },
      { id: 'spot', label: 'Spot', icon: Wallet, path: '/assets/spot' },
      { id: 'margin', label: 'Margin', icon: FileText, path: '/assets/margin' },
      { id: 'third-party', label: 'Third-Party Wallet', icon: Wallet, path: '/assets/third-party' },
    ],
  },
  {
    id: 'orders',
    label: 'Orders',
    icon: FileText,
    expandable: true,
    children: [
      { id: 'open-orders', label: 'Open Orders', icon: FileText, path: '/orders/open' },
      { id: 'order-history', label: 'Order History', icon: FileText, path: '/orders/history' },
      { id: 'trade-history', label: 'Trade History', icon: FileText, path: '/orders/trades' },
    ],
  },
  {
    id: 'rewards-hub',
    label: 'Rewards Hub',
    icon: Gift,
    path: '/rewards',
  },
  {
    id: 'referral',
    label: 'Referral',
    icon: Users,
    path: '/referral',
  },
  {
    id: 'account',
    label: 'Account',
    icon: User,
    expandable: true,
    children: [
      { id: 'profile', label: 'Profile', icon: User, path: '/account/profile' },
      { id: 'security', label: 'Security', icon: Settings, path: '/account/security' },
      { id: 'verification', label: 'Verification', icon: FileText, path: '/account/verification' },
      { id: 'payment', label: 'Payment Methods', icon: Wallet, path: '/account/payment' },
    ],
  },
  {
    id: 'sub-accounts',
    label: 'Sub Accounts',
    icon: Users2,
    path: '/sub-accounts',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/settings',
  },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>(['assets']);

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  const isActive = (item: SidebarItem): boolean => {
    if (item.path) {
      return pathname === item.path;
    }
    if (item.children) {
      return item.children.some(child => pathname === child.path);
    }
    return false;
  };

  const renderSidebarItem = (item: SidebarItem, level: number = 0) => {
    const Icon = item.icon;
    const active = isActive(item);
    const expanded = expandedItems.includes(item.id);

    return (
      <div key={item.id}>
        <button
          onClick={() => {
            if (item.expandable) {
              toggleExpanded(item.id);
            } else if (item.path) {
              handleNavigation(item.path);
            }
          }}
          className={`sidebar-item w-full ${active ? 'sidebar-item-active' : ''}`}
          style={{ paddingLeft: `${16 + level * 16}px` }}
        >
          <Icon size={16} />
          <span className="flex-1 text-left">{item.label}</span>
          {item.expandable && (
            expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
          )}
        </button>
        
        {item.children && expanded && (
          <div className="ml-4">
            {item.children.map(child => renderSidebarItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="hidden lg:flex flex-col w-60 bg-bg-secondary border-r border-border-primary h-screen">
      {/* Logo */}
      <div className="p-4 border-b border-border-primary">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-black font-bold text-sm">T</span>
          </div>
          <span className="text-primary font-bold text-xl">TigerEx</span>
        </div>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto py-4 px-2">
        <nav className="space-y-1">
          {sidebarItems.map(item => renderSidebarItem(item))}
        </nav>
      </div>

      {/* User Profile */}
      <div className="p-4 border-t border-border-primary">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <span className="text-black font-bold">U</span>
          </div>
          <div className="flex-1">
            <div className="text-sm font-medium text-text-primary">User-0f8ed</div>
            <div className="text-xs text-text-secondary">Regular User</div>
          </div>
          <Settings size={16} className="text-text-secondary cursor-pointer hover:text-text-primary" />
        </div>
      </div>
    </div>
  );
}