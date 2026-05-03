/**
 * TigerEx React Component
 * @file BottomNavigation.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
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
  icon: React.ComponentType<{ size?: number | string; className?: string }>;
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
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
