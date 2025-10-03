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
}