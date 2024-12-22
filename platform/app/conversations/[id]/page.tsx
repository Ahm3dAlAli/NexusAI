'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Chat from '@/components/chat'
import { useConversations } from '@/context/ConversationsContext'

const ConversationPage = () => {
  const params = useParams()
  const id = params?.id as string
  const router = useRouter()
  const { setSelectedConversation, conversations } = useConversations()

  useEffect(() => {
    if (!id) {
      router.push('/')
      return
    }

    // Find and set the selected conversation based on the URL parameter
    const conversation = conversations.find(conv => conv.id === id)
    if (conversation) {
      setSelectedConversation(conversation)
    } else {
      // If conversation not found, redirect to home
      router.push('/')
    }
  }, [id, conversations, setSelectedConversation, router])

  if (!id) return null

  return (
    <Chat conversationId={id as string} />
  )
}

export default ConversationPage
