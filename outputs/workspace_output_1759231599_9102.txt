import { Suspense } from 'react';
import { Header } from '@/components/layout/Header';
import BinanceStyleLanding from '@/components/BinanceStyleLanding';
import { Footer } from '@/components/layout/Footer';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function HomePage() {
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
