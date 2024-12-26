'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { AgentMessage } from '@/types/AgentMessage'
import { MessageType, MessageRequest } from '@/types/MessageRequest'
import { AgentMessageType } from '@prisma/client'
import { Copy } from "lucide-react"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { MarkdownLink } from '@/components/ui/markdown-link'
import { config } from '@/config/environment'
import { saveMessage, fetchMessages } from '@/lib/conversations'
import { motion } from 'framer-motion'

interface ChatProps {
  conversationId?: string
  initialMessage?: string
}

export default function Chat({ conversationId, initialMessage }: ChatProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [input, setInput] = useState('')
  const [aiTyping, setAiTyping] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)
  const [initialMessageSent, setInitialMessageSent] = useState(false)

  useEffect(() => {
    if (conversationId) {
      fetchMessages(conversationId)
        .then((sortedMessages) => {
          // Display all messages
          setMessages(sortedMessages)

          // Only use user and final messages for websocket communication
          const filteredMessages = sortedMessages.filter((msg: AgentMessage) => 
            msg.type === AgentMessageType.human || msg.type === AgentMessageType.final
          )
          initializeWebSocket(filteredMessages)
        })
        .catch(error => {
          console.error('Error fetching sorted messages:', error)
        })
    } else {
      initializeWebSocket([])
    }

    return () => {
      ws.current?.close()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId])

  const initializeWebSocket = (previousMessages: AgentMessage[]) => {
    ws.current = new WebSocket(config.wsUrl)

    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      if (conversationId && previousMessages.length > 0) {
        // Send initial message with history
        const payload: MessageRequest = { type: MessageType.init, messages: previousMessages }
        ws.current?.send(JSON.stringify(payload))
      } else if (initialMessage && !initialMessageSent) {
        // Send the initial message if it's a new conversation
        const payload: MessageRequest = { type: MessageType.query, query: initialMessage }
        ws.current?.send(JSON.stringify(payload))
        setInitialMessageSent(true)
        setAiTyping(true)
      }
    }

    ws.current.onmessage = async (event) => {
      if (!conversationId) return
      const message: AgentMessage = JSON.parse(event.data)
      setMessages(prev => [...prev, message])
      await saveMessage(conversationId, message)

      if (
        message.type === AgentMessageType.final ||
        message.type === AgentMessageType.error
      ) {
        setAiTyping(false)
      }
    }

    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '' || aiTyping || !conversationId) return

    setInput('')
    setAiTyping(true)
    const userMessage: AgentMessage = {
      order: messages.length,
      type: AgentMessageType.human,
      content: input.trim(),
    }
    setMessages(prev => [...prev, userMessage])
    await saveMessage(conversationId, userMessage)
    const payload: MessageRequest = { type: MessageType.query, query: input.trim() }
    ws.current?.send(JSON.stringify(payload))
  }

  const getEmoji = (type: AgentMessageType) => {
    switch(type) {
      case AgentMessageType.system:
        return '⚙️'
      case AgentMessageType.human:
        return '👤'
      case AgentMessageType.agent:
        return '🤖'
      case AgentMessageType.tool:
        return '📚'
      case AgentMessageType.error:
        return '❌'
      default:
        return ''
    }
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedMessageIndex(index)
      setTimeout(() => setCopiedMessageIndex(null), 1000) // Hide after 1 second
    })
  }

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto no-scrollbar">
      <motion.div 
        className="text-center mb-4 pt-4 max-w-[800px] mx-auto px-4"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ 
          duration: 0.3,
          ease: "easeOut"
        }}
      >
        <h1 className="text-4xl font-bold mb-2">🤖 NexusAI 📚</h1>
        <p className="text-xl text-muted-foreground">
          Research scientific literature in minutes, not hours
        </p>
      </motion.div>
      <div className="flex-1 overflow-y-auto space-y-4 px-4 no-scrollbar">
        {messages.map((m, index) => {
          // Skip final messages that follow a system->agent sequence
          if (
            m.type === AgentMessageType.final &&
            index >= 2 &&
            messages[index - 2].type === AgentMessageType.human &&
            messages[index - 1].type === AgentMessageType.agent
          ) {
            return null;
          }

          // Render final messages outside of the message box
          if (m.type === AgentMessageType.final) {
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.3,
                  delay: 0.1,
                  ease: "easeOut"
                }}
                className="final-message group relative"
              >
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="absolute right-0 top-0 transition-opacity"
                  onClick={() => copyToClipboard(m.content, index)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
                {copiedMessageIndex === index && (
                  <span className="absolute right-0 top-6 text-sm">Copied!</span>
                )}
                <div className="message-content">
                  <h2>✅ Task Completed</h2>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{ a: MarkdownLink }}
                  >
                    {m.content}
                  </ReactMarkdown>
                </div>
              </motion.div>
            );
          }

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ 
                duration: 0.3,
                delay: 0.1,
                ease: "easeOut"
              }}
            >
              <Card
                className={`mb-4 ${
                  m.type === AgentMessageType.human 
                    ? 'ml-auto bg-primary text-primary-foreground' 
                    : 'mr-auto'
                } max-w-[80%]`}
              >
                <CardContent className="flex p-3">
                  <span className="mr-2 text-2xl mt-[6px]">{getEmoji(m.type)}</span>
                  {m.type === AgentMessageType.tool ? (
                    <div className="flex flex-col w-full">
                      {m.tool_name && (
                        <div className="font-bold mt-2 mb-2 pb-2 border-b">{m.tool_name}</div>
                      )}
                      <div className="message-content">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{ a: MarkdownLink }}
                        >
                          {m.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    <div className="message-content">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{ a: MarkdownLink }}
                      >
                        {m.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
        {aiTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ 
              duration: 0.3,
              delay: 0.1,
              ease: "easeOut"
            }}
          >
            <Card className="mb-4 mr-auto max-w-[80%]">
              <CardContent className="flex items-center p-4">
                <div>
                  💭 <span className="animated-thinking"></span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
      <motion.div 
        className="flex justify-center w-full p-4 bg-background sticky bottom-0"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ 
          duration: 0.3,
          ease: "easeOut"
        }}
      >
        <form onSubmit={handleSubmit} className="flex w-full max-w-[800px] mx-auto space-x-2">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder={conversationId ? "Type your message..." : "What do you want to research?"}
            className="flex-1"
            disabled={!isConnected}
          />
          <Button type="submit" disabled={aiTyping || !isConnected}>
            Send
          </Button>
        </form>
      </motion.div>
    </div>
  )
} 