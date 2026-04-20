/**
 * TigerEx Frontend Component
 * @file providers.tsx
 * @description React component for TigerEx platform
 * @author TigerEx Development Team
 */
"use client"

import { ReactNode } from "react"
import { SessionProvider } from "next-auth/react"

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return <SessionProvider>{children}</SessionProvider>
}