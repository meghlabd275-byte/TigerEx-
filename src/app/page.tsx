'use client';

import { Suspense, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import BinanceStyleLanding from '@/components/BinanceStyleLanding';
import { Footer } from '@/components/layout/Footer';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is on mobile device
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isSmallScreen = window.innerWidth <= 768;
    
    if (isMobile || isSmallScreen) {
      router.push('/mobile');
    } else {
      // Check if user wants to go directly to trading interface
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('trade') === 'true') {
        router.push('/desktop');
      }
    }
  }, [router]);

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Suspense fallback={<LoadingSpinner />}>
          <BinanceStyleLanding />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
