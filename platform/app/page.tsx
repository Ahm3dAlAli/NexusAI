'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Chat from '@/components/chat'
import { useConversations } from '@/context/ConversationsContext'

const Home: React.FC = () => {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initialMessage, setInitialMessage] = useState<string | null>(null)
  const { createConversation, selectedConversation } = useConversations()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '') return
    setLoading(true)
    try {
      const conversation = await createConversation({ 
        title: input.trim(),
        initialMessage: input.trim()
      })
      if (conversation) {
        setInitialMessage(input.trim())
        setInput('')
      }
    } catch (error) {
      console.error('Failed to create conversation:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {!selectedConversation ? (
        <div className="flex flex-col h-screen max-w-5xl mx-auto items-center justify-center">
          <h1 className="text-4xl font-bold mb-2">🤖 NexusAI 📚</h1>
          <p className="text-xl text-muted-foreground mb-4">Your assistant to research scientific literature in minutes instead of hours</p>
          <div className="flex justify-center w-full">
            <form onSubmit={handleSubmit} className="flex space-x-2 w-full max-w-[75%]">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="What do you want to research?"
                className="flex-1"
                disabled={loading}
              />
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Send'}
              </Button>
            </form>
          </div>
        </div>
      ) : (
        <Chat
          conversationId={selectedConversation.id}
          initialMessage={initialMessage || undefined}
        />
      )}
    </>
  )
}

export default Home