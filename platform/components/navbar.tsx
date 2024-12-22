'use client'

import React from 'react'
import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useConversations } from '@/context/ConversationsContext'
import { useRouter } from 'next/navigation'

const Navbar: React.FC = () => {
  const { conversations, loading, setSelectedConversation } = useConversations()
  const router = useRouter()

  const handleNewChat = (e: React.MouseEvent) => {
    e.preventDefault()
    setSelectedConversation(null)
    router.push('/')
  }

  return (
    <div className="w-64 bg-primary text-primary-foreground h-screen p-4 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Menu</h2>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-primary-foreground hover-light-primary"
          onClick={handleNewChat}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <ul className="flex-1 overflow-y-auto">
        {!loading && conversations.map((conv) => (
          <li key={conv.id} className="mb-2">
            <Link 
              href={`/conversations/${conv.id}`}
              className="block p-2 rounded hover-light-primary truncate"
            >
              {conv.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Navbar