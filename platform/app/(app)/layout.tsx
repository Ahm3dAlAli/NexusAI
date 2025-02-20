'use client'

import { ReactNode } from 'react'

interface AppLayoutProps {
  children: ReactNode
}

const AppLayout = ({ children }: AppLayoutProps) => {
  return (
    <>
      {children}
    </>
  )
}

export default AppLayout