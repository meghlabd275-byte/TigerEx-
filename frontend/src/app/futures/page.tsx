/**
 * TigerEx Frontend Component
 * @file page.tsx
 * @description React component for TigerEx exchange
 * @author TigerEx Development Team
 */

'use client';

import { useEffect, useState } from 'react';
import FuturesTradingScreen from '@/components/mobile/FuturesTradingScreen';
import TradingScreen from '@/components/desktop/TradingScreen';

export default function FuturesPage() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkDevice = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  return (
    <div className="min-h-screen">
      {isMobile ? <FuturesTradingScreen /> : <TradingScreen />}
    </div>
  );
}// TigerEx Wallet API
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
