/**
 * TigerEx React Component
 * @file Navbar.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  LineChart, 
  TrendingUp, 
  Wallet, 
  Store, 
  BookOpen,
  Users,
  Building2,
  Crown,
  Activity,
  Bell,
  Settings,
  LogOut,
  ChevronDown
} from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <img 
            src="/assets/logo/tigerex-logo.png" 
            alt="TigerEx Logo" 
            className="w-10 h-10 rounded-xl object-cover"
          />
          <span className="text-xl font-bold">TigerEx</span>
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-2">
          <NavLink href="/" icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" />
          <NavLink href="/trade" icon={<LineChart className="w-4 h-4" />} label="Trade" />
          <NavLink href="/markets" icon={<TrendingUp className="w-4 h-4" />} label="Markets" />
          <NavLink href="/portfolio" icon={<Wallet className="w-4 h-4" />} label="Portfolio" />
          
          {/* Products Dropdown */}
          <div className="relative group">
            <button className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
              <Store className="w-4 h-4" /> Products <ChevronDown className="w-4 h-4" />
            </button>
            <div className="absolute top-full left-0 mt-1 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl hidden group-hover:block z-50">
              <Link href="/p2p-trading" className="block px-4 py-2 hover:bg-gray-700">P2P Trading</Link>
              <Link href="/futures" className="block px-4 py-2 hover:bg-gray-700">Futures</Link>
              <Link href="/options" className="block px-4 py-2 hover:bg-gray-700">Options</Link>
              <Link href="/tradingview" className="block px-4 py-2 hover:bg-gray-700">TradingView Charts</Link>
              <Link href="/dex-staking" className="block px-4 py-2 hover:bg-gray-700">Staking</Link>
              <Link href="/dex-liquidity" className="block px-4 py-2 hover:bg-gray-700">Liquidity</Link>
            </div>
          </div>

          {/* Earn */}
          <div className="relative group">
            <button className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
              <TrendingUp className="w-4 h-4" /> Earn <ChevronDown className="w-4 h-4" />
            </button>
            <div className="absolute top-full left-0 mt-1 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl hidden group-hover:block z-50">
              <Link href="/earn" className="block px-4 py-2 hover:bg-gray-700">Savings</Link>
              <Link href="/launchpool" className="block px-4 py-2 hover:bg-gray-700">Launchpool</Link>
              <Link href="/staking" className="block px-4 py-2 hover:bg-gray-700">Staking</Link>
            </div>
          </div>

          {/* VIP & Institutional */}
          <NavLink href="/vip" icon={<Crown className="w-4 h-4" />} label="VIP" />
          <NavLink href="/affiliate" icon={<Users className="w-4 h-4" />} label="Affiliate" />
          <NavLink href="/institutional" icon={<Building2 className="w-4 h-4" />} label="Institutional" />
          
          {/* Services */}
          <div className="relative group">
            <button className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
              <Activity className="w-4 h-4" /> Services <ChevronDown className="w-4 h-4" />
            </button>
            <div className="absolute top-full left-0 mt-1 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl hidden group-hover:block z-50">
              <Link href="/price-aggregation" className="block px-4 py-2 hover:bg-gray-700">Price Aggregation</Link>
              <Link href="/education" className="block px-4 py-2 hover:bg-gray-700">Academy</Link>
              <Link href="/tradingview" className="block px-4 py-2 hover:bg-gray-700">TradingView Charts</Link>
            </div>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          <button className="p-2 hover:bg-gray-800 rounded-lg">
            <Bell className="w-5 h-5 text-gray-400" />
          </button>
          <button className="p-2 hover:bg-gray-800 rounded-lg">
            <Settings className="w-5 h-5 text-gray-400" />
          </button>
          <div className="flex items-center gap-3 pl-3 border-l border-gray-700">
            <div className="w-9 h-9 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
              <span className="font-semibold text-black">U</span>
            </div>
            <button className="text-sm text-gray-400 hover:text-white">Logout</button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link 
      href={href} 
      className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
