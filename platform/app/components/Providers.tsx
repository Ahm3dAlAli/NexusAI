'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { ConversationsProvider } from '@/context/ConversationsContext'

interface ProvidersProps {
  children: ReactNode
}

const Providers = ({ children }: ProvidersProps) => {
  return (
    <SessionProvider>
      <ConversationsProvider>
        {children}
      </ConversationsProvider>
    </SessionProvider>
  )
}

export default Providers
