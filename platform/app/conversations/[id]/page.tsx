'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Chat from '@/components/chat'
import { useConversations } from '@/context/ConversationsContext'

const ConversationPage = () => {
  const params = useParams()
  const id = params?.id as string
  const router = useRouter()
  const { setSelectedConversation, conversations, loading } = useConversations()

  useEffect(() => {
    if (!id) {
      router.push('/')
      return
    }

    // Only redirect if we're sure conversations have loaded and the ID wasn't found
    if (!loading && conversations.length > 0) {
      const conversation = conversations.find(conv => conv.id === id)
      if (conversation) {
        setSelectedConversation(conversation)
      } else {
        router.push('/')
      }
    }
  }, [id, conversations, setSelectedConversation, router, loading])

  if (!id || loading) return null

  return (
    <Chat conversationId={id} />
  )
}

export default ConversationPage
