'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { ResearchesProvider } from '@/context/ResearchesContext'

interface ProvidersProps {
  children: ReactNode
}

const Providers = ({ children }: ProvidersProps) => {
  return (
    <SessionProvider>
      <ResearchesProvider>
        {children}
      </ResearchesProvider>
    </SessionProvider>
  )
}

export default Providers
