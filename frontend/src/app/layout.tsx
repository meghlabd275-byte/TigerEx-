import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { WebSocketProvider } from '@/contexts/WebSocketContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TigerEx - Complete Cryptocurrency Exchange',
  description: 'Advanced cryptocurrency exchange with comprehensive trading features, multi-platform support, and enterprise-grade security',
  keywords: ['cryptocurrency', 'exchange', 'bitcoin', 'ethereum', 'trading', 'defi', 'nft'],
  authors: [{ name: 'TigerEx Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#000000',
  manifest: '/manifest.json',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <ThemeProvider>
            <AuthProvider>
              <WebSocketProvider>
                {children}
              </WebSocketProvider>
            </AuthProvider>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  )
}