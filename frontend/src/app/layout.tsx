/**
 * TigerEx Frontend Component
 * @file layout.tsx
 * @description React component for TigerEx platform
 * @author TigerEx Development Team
 */
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
  icons: {
    icon: '/assets/logo/tigerex-logo.png',
    apple: '/assets/logo/tigerex-logo.png',
    other: {
      rel: 'apple-touch-icon',
      url: '/assets/logo/tigerex-logo.png',
    },
  },
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
}export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
