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

'use client';

import React, { useState } from 'react';
import DesktopTradingDashboard from '../../components/desktop/DesktopTradingDashboard';
import CopyTradingInterface from '../../components/desktop/CopyTradingInterface';
import OptionsTrading from '../../components/desktop/OptionsTrading';
import GridTrading from '../../components/desktop/GridTrading';
import BotTrading from '../../components/desktop/BotTrading';

export default function DesktopPage() {
  const [currentView, setCurrentView] = useState('trading');

  const handleNavigation = (section: string) => {
    setCurrentView(section);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'trading':
      case 'dashboard':
        return <DesktopTradingDashboard onNavigate={handleNavigation} />;
      case 'copy-trading':
        return <CopyTradingInterface />;
      case 'options':
        return <OptionsTrading />;
      case 'grid':
        return <GridTrading />;
      case 'bot':
        return <BotTrading />;
      default:
        return <DesktopTradingDashboard onNavigate={handleNavigation} />;
    }
  };

  return (
    <div className="desktop-trading">
      {renderCurrentView()}
    </div>
  );
}