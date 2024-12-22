'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input, InputWrapper } from '@/components/ui/input'
import Chat from '@/components/chat'
import { useConversations } from '@/context/ConversationsContext'
import { motion } from 'framer-motion'

const Home: React.FC = () => {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initialMessage, setInitialMessage] = useState<string | null>(null)
  const { createConversation, selectedConversation } = useConversations()
  const [, setWindowHeight] = useState(0)

  useEffect(() => {
    setWindowHeight(window.innerHeight)
  }, [])

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
        <div className="flex flex-col h-screen max-w-5xl mx-auto items-center justify-center no-scrollbar overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.4,
              delay: 0.2,
              ease: "easeOut"
            }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold mb-2">
              🤖 NexusAI 📚
            </h1>
            <p className="text-xl text-muted-foreground mb-4">
              Research scientific literature in minutes, not hours
            </p>
          </motion.div>
          <motion.div 
            className="flex justify-center w-full"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.4,
              delay: 0.2,
              ease: "easeOut"
            }}
          >
            <form onSubmit={handleSubmit} className="flex w-full max-w-[800px] space-x-2">
              <InputWrapper>
                <Input
                  value={input}
                  onChange={handleInputChange}
                  placeholder="What do you want to research?"
                  disabled={loading}
                />
              </InputWrapper>
              <Button type="submit" disabled={loading}>
                Send
              </Button>
            </form>
          </motion.div>
        </div>
      ) : (
        <div className="h-screen no-scrollbar overflow-y-auto">
          <Chat
            conversationId={selectedConversation.id}
            initialMessage={initialMessage || undefined}
          />
        </div>
      )}
    </>
  )
}

export default Home