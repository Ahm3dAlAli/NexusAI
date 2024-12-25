'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { fetchConversations, createConversation as apiCreateConversation } from '@/lib/conversations'
import { useSession } from 'next-auth/react'

interface CreateConversationParams {
  title: string
  initialMessage: string
}

interface Conversation {
  id: string
  title: string
  updatedAt: Date
}

interface ConversationsContextType {
  conversations: Conversation[]
  loading: boolean
  createConversation: (params: CreateConversationParams) => Promise<Conversation | null>
  selectedConversation: Conversation | null
  setSelectedConversation: (conv: Conversation | null) => void
}

const ConversationsContext = createContext<ConversationsContextType | undefined>(undefined)

export const useConversations = () => {
  const context = useContext(ConversationsContext)
  if (!context) {
    throw new Error('useConversations must be used within a ConversationsProvider')
  }
  return context
}

export const ConversationsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const { data: session } = useSession()

  const loadConversations = async () => {
    if (!session) return
    setLoading(true)
    try {
      const convs = await fetchConversations()
      setConversations(convs)
    } catch (error) {
      console.error('Error fetching conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const createConversation = async ({ title, initialMessage }: CreateConversationParams): Promise<Conversation | null> => {
    if (!session) return null
    try {
      const newConv = await apiCreateConversation({ title, initialMessage })
      setConversations((prev) => [newConv, ...prev])
      setSelectedConversation(newConv)
      return newConv
    } catch (error) {
      console.error('Error creating conversation:', error)
      return null
    }
  }

  useEffect(() => {
    loadConversations()
  }, [session])

  return (
    <ConversationsContext.Provider value={{ 
        conversations, 
        loading, 
        createConversation, 
        selectedConversation, 
        setSelectedConversation 
      }}>
      {children}
    </ConversationsContext.Provider>
  )
}