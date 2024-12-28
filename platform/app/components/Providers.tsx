'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { MenuProvider } from '@/context/MenuContext'

interface ProvidersProps {
  children: ReactNode
}

const Providers = ({ children }: ProvidersProps) => {
  return (
    <SessionProvider>
      <MenuProvider>
        {children}
      </MenuProvider>
    </SessionProvider>
  )
}

export default Providers
