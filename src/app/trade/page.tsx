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

import { Suspense } from 'react';
import { TradingInterface } from '@/components/trading/TradingInterface';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function TradePage() {
  return (
    <div className="min-h-screen bg-gray-900">
      <Suspense fallback={<LoadingSpinner />}>
        <TradingInterface />
      </Suspense>
    </div>
  );
}
