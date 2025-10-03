import type { Metadata } from 'next';
import './globals.css';
import MainLayout from '@/components/layout/MainLayout';

export const metadata: Metadata = {
  title: 'TigerEx - Hybrid Cryptocurrency Exchange',
  description: 'Advanced hybrid crypto exchange platform combining CEX and DEX functionality',
  keywords: ['cryptocurrency', 'exchange', 'trading', 'blockchain', 'defi', 'cex', 'dex'],
  authors: [{ name: 'TigerEx Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#F0B90B',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    title: 'TigerEx - Hybrid Cryptocurrency Exchange',
    description: 'Advanced hybrid crypto exchange platform combining CEX and DEX functionality',
    url: 'https://tigerex.com',
    siteName: 'TigerEx',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'TigerEx Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TigerEx - Hybrid Cryptocurrency Exchange',
    description: 'Advanced hybrid crypto exchange platform combining CEX and DEX functionality',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <MainLayout>
          {children}
        </MainLayout>
      </body>
    </html>
  );
}