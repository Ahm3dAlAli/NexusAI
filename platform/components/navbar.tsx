'use client'

import React from 'react'
import Link from 'next/link'
import { Plus, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useConversations } from '@/context/ConversationsContext'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { signOut, useSession } from 'next-auth/react'

const Navbar: React.FC = () => {
  const { conversations, loading, setSelectedConversation } = useConversations()
  const router = useRouter()
  const { data: session } = useSession()

  const handleNewChat = (e: React.MouseEvent) => {
    e.preventDefault()
    setSelectedConversation(null)
    router.push('/')
  }

  const handleLogout = () => {
    signOut({ callbackUrl: '/login' })
  }

  if (!session) {
    return null
  }

  const user = session.user

  return (
    <motion.div 
      className="w-64 bg-primary text-primary-foreground h-screen p-4 flex flex-col no-scrollbar"
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ 
        duration: 0.3,
        ease: "easeOut"
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Menu</h2>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-primary-foreground hover-light-primary"
          onClick={handleNewChat}
          title="New conversation"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <ul className="flex-1 overflow-y-auto no-scrollbar">
        {!loading && conversations.map((conv) => (
          <motion.li
            key={conv.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ 
              duration: 0.3,
              delay: 0.2,
              ease: "easeOut"
            }}
            className="mb-2"
          >
            <Link 
              href={`/conversations/${conv.id}`}
              className="block p-2 rounded hover-light-primary truncate"
            >
              {conv.title}
            </Link>
          </motion.li>
        ))}
      </ul>

      <Card className="mt-auto bg-primary-foreground/10 border-primary-foreground/20">
        <CardContent className="p-4 flex items-center gap-3">
          <Avatar className="h-10 w-10 border-2 border-primary-foreground/20">
            <AvatarFallback className="bg-primary-foreground/10 text-primary-foreground">
              {user?.name?.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-primary-foreground">{user?.name}</p>
            <p className="text-xs text-primary-foreground/70 truncate">{user?.email}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-primary-foreground hover-light-primary"
            onClick={handleLogout}
            title="Logout"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default Navbar