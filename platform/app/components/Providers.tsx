'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { MenuProvider } from '@/context/MenuContext'
import { NotificationProvider } from '@/context/NotificationContext'
import Notifications from '@/components/ui/notifications'

interface ProvidersProps {
  children: ReactNode
}

const Providers = ({ children }: ProvidersProps) => {
  return (
    <SessionProvider>
      <MenuProvider>
        <NotificationProvider>
          {children}
          <Notifications />
        </NotificationProvider>
      </MenuProvider>
    </SessionProvider>
  )
}

export default Providers
