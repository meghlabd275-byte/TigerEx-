'use client';

import { useEffect, useState } from 'react';
import SpotTradingScreen from '@/components/mobile/SpotTradingScreen';
import TradingScreen from '@/components/desktop/TradingScreen';

export default function TradePage() {
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
      {isMobile ? <SpotTradingScreen /> : <TradingScreen />}
    </div>
  );
}