'use client'

import React, { useEffect } from 'react'
import { LogOut, Search, FileText, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useMenu } from '@/context/MenuContext'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { signOut, useSession } from 'next-auth/react'
import { MenuHeader } from '@/components/ui/menu-header'

const Navbar: React.FC = () => {
  const { 
    setSelectedResearch, 
    selectedResearch, 
    loadingResearches,
    currentMenu,
    setCurrentMenu
  } = useMenu()
  const router = useRouter()
  const { data: session } = useSession()

  useEffect(() => {
    if (selectedResearch) {
      setCurrentMenu('researches')
    }
  }, [selectedResearch, setCurrentMenu])

  if (!session?.user) return null
  const user = session.user

  const handleNewChat = (e: React.MouseEvent) => {
    e.preventDefault()
    setSelectedResearch(null)
    router.push('/')
  }

  const handleSettingsClick = () => {
    router.push('/settings')
  }

  const renderMainMenu = () => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="flex-1"
    >
      <MenuHeader onNewChat={handleNewChat} title="Home" />
      <div>
        <Button
          variant="ghost"
          className="w-full justify-start text-lg py-4"
          onClick={() => setCurrentMenu('researches')}
        >
          <Search className="mr-3 h-5 w-5" />
          Researches
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start text-lg py-4"
          onClick={() => setCurrentMenu('papers')}
        >
          <FileText className="mr-3 h-5 w-5" />
          Papers
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start text-lg py-4"
          onClick={handleSettingsClick}
        >
          <Settings className="mr-3 h-5 w-5" />
          Settings
        </Button>
      </div>
    </motion.div>
  )

  const renderResearchesMenu = () => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="flex-1"
    >
      <MenuHeader 
        showBackButton 
        onBack={() => setCurrentMenu('main')}
        onNewChat={handleNewChat}
        title="Researches"
        type="researches"
      />
      {loadingResearches && (
        <div className="flex items-center justify-center p-4">
          <p className="text-primary-foreground/70">Loading researches...</p>
        </div>
      )}
    </motion.div>
  )

  const renderPapersMenu = () => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="flex-1"
    >
      <MenuHeader 
        showBackButton 
        onBack={() => setCurrentMenu('main')}
        onNewChat={handleNewChat}
        title="Papers"
        type="papers"
      />
    </motion.div>
  )

  return (
    <div className="w-80 bg-primary text-primary-foreground h-screen p-4 flex flex-col">
      <div className="flex-1 overflow-y-auto no-scrollbar">
        <AnimatePresence mode="wait">
          {currentMenu === 'main' && renderMainMenu()}
          {currentMenu === 'researches' && renderResearchesMenu()}
          {currentMenu === 'papers' && renderPapersMenu()}
        </AnimatePresence>
      </div>

      <Card className="mt-4 bg-primary-foreground/10 border-primary-foreground/20">
        <CardContent className="p-4 flex items-center gap-3">
          <Avatar className="h-10 w-10 border-2 border-primary-foreground/20">
            <AvatarFallback className="bg-primary-foreground/10 text-primary-foreground">
              {user.name?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-primary-foreground">{user.name}</p>
            <p className="text-xs text-primary-foreground/70 truncate">{user.email}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-primary-foreground hover-light-primary"
            onClick={() => signOut({ callbackUrl: '/login' })}
            title="Logout"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default Navbar