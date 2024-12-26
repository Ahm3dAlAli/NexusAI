'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Chat from '@/components/chat'
import { useConversations } from '@/context/ConversationsContext'
import { useSession } from 'next-auth/react'

const ConversationPage = () => {
  const params = useParams()
  const id = params?.id as string
  const router = useRouter()
  const { setSelectedConversation, conversations, loading } = useConversations()
  const { status } = useSession()

  useEffect(() => {
    if (status === "loading") return
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
  }, [id, conversations, setSelectedConversation, router, loading, status])

  if (status === "loading" || !id || loading) return null

  return (
    <Chat conversationId={id} />
  )
}

export default ConversationPage
