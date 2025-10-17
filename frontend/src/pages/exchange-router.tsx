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
import { useWallet } from '../contexts/WalletContext';
import WalletSetup from '../components/wallet/WalletSetup';
import HybridExchangePage from './hybrid-exchange';
import DEXSwap from '../components/dex/DEXSwap';

const ExchangeRouter: React.FC = () => {
  const { wallet, isConnected, exchangeMode } = useWallet();

  // If no wallet is connected, show wallet setup
  if (!isConnected) {
    return <WalletSetup />;
  }

  // If wallet is connected and mode is DEX, show DEX interface
  if (exchangeMode === 'dex') {
    return <DEXSwap />;
  }

  // Default to CEX (Centralized Exchange)
  return <HybridExchangePage />;
};

export default ExchangeRouter;