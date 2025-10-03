'use client';

import { useEffect, useState } from 'react';
import HomeScreen from '@/components/mobile/HomeScreen';
import DashboardScreen from '@/components/desktop/DashboardScreen';

export default function HomePage() {
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
      {isMobile ? <HomeScreen /> : <DashboardScreen />}
    </div>
  );
}