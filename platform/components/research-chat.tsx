'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import { AgentMessage } from '@/types/AgentMessage'
import { MessageRequest } from '@/types/BackendModels'
import { AgentMessageType, ModelProviderType } from '@prisma/client'
import { Copy } from "lucide-react"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { MarkdownLink } from '@/components/ui/markdown-link'
import { publicConfig } from '@/config/environment'
import { saveResearchMessage, fetchMessages } from '@/lib/researches'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useMenu } from '@/context/MenuContext'
import { useNotification } from '@/context/NotificationContext'
import { createPapers } from '@/lib/papers'
import { Icons } from '@/components/ui/icons'
import { fetchUser } from '@/lib/user'
import { useSession } from 'next-auth/react'

interface ChatProps {
  researchId?: string
  initialMessage?: string
}

export default function ResearchChat({ researchId, initialMessage }: ChatProps) {
  const router = useRouter()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const user = useRef<any>(null)
  const initialMessageSent = useRef(false)
  const ws = useRef<WebSocket | null>(null)
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)
  const [messagesLoaded, setMessagesLoaded] = useState(false)
  const [aiTyping, setAiTyping] = useState(false)
  const [showThinking, setShowThinking] = useState(false)
  const { fetchPapers, setCurrentMenu } = useMenu()
  const { addNotification } = useNotification()
  const session = useSession()

  useEffect(() => {
    if (!researchId) return

    const fetchUserData = async () => {
      try {
        const userData = await fetchUser()
        user.current = userData
      } catch (error) {
        console.error('Error fetching user data:', error)
        router.push('/')
      }
    }

    fetchUserData()
  }, [researchId, router])

  useEffect(() => {
    if (!researchId) return

    console.log(`Loading messages for research: ${researchId}`)
    fetchMessages(researchId)
      .then((sortedMessages) => {
        if (!sortedMessages) {
          router.push('/')
          return
        }
        setMessages(sortedMessages)
        setMessagesLoaded(true)
      })
      .catch(error => {
        console.error('Error fetching sorted messages:', error)
        router.push('/')
      })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [researchId, router])

  useEffect(() => {
    if (messagesLoaded && !ws.current) {
      initializeWebSocket()
    }

    return () => {
      console.log('Cleaning up WebSocket connection.')
      ws.current?.close()
      ws.current = null
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messagesLoaded])

  const handleInitialMessage = (previousMessages: AgentMessage[]) => {
    const payload: MessageRequest = {
      history: previousMessages,
      query: initialMessage,
      custom_instructions: user.current?.customInstructions || undefined,
      model_provider: session?.data?.user?.sessionProviders?.find(p => p.modelProvider.selected)?.modelProvider.name || ModelProviderType.default,
      provider_details: session?.data?.user?.sessionProviders?.find(p => p.modelProvider.selected)?.details || null
    }

    if (initialMessage) {
      const message: AgentMessage = {
        order: 0,
        type: AgentMessageType.human,
        content: initialMessage,
      }

      setAiTyping(true)
      setShowThinking(true)
      setMessages(prev => [...prev, message])
      if (researchId) {
        saveResearchMessage(researchId, message)
      }

      ws.current?.send(JSON.stringify(payload))
    }
  }

  const initializeWebSocket = async () => {
    // Get WS token
    console.log('Getting jwt')
    const response = await fetch('/api/auth/jwt')
    if (!response.ok) {
      throw new Error('Failed to get jwt')
    }
    const { token } = await response.json()

    // Initialize WebSocket with token
    console.log('Initializing WebSocket')
    ws.current = new WebSocket(`${publicConfig.wsUrl}/ws?token=${token}`)

    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)

      const filteredMessages = messages.filter(m => m.type === AgentMessageType.human || m.type === AgentMessageType.final)
      console.log(`Sending ${filteredMessages.length} previous messages to ws server`)
      if (initialMessage && !initialMessageSent.current) {
        handleInitialMessage(filteredMessages)
        initialMessageSent.current = true
      } else if (messages.length > 0) {
        const payload: MessageRequest = { history: filteredMessages }
        ws.current?.send(JSON.stringify(payload))
      }
    }

    ws.current.onmessage = async (event) => {
      const message: AgentMessage = JSON.parse(event.data)
      console.log('Received message from ws server:', message)
      setMessages(prev => [...prev, message])
      setShowThinking(false)
      setTimeout(() => setShowThinking(true), 250)

      if (researchId) {
        await saveResearchMessage(researchId, message)
      }

      if (
        message.type === AgentMessageType.final ||
        message.type === AgentMessageType.error
      ) {
        setAiTyping(false)
        setShowThinking(false)
      }

      if (message.type === AgentMessageType.final && message.urls && message.urls.length > 0) {
        if (user.current?.collectPapers) {
          handlePapersCreation(message.urls)
        }
      }
    }

    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }
  }

  const handlePapersCreation = async (urls: string[]) => {
    let uniqueUrls = Array.from(new Set(urls));

    // Show a generic notification without mentioning a count
    addNotification('info', `Your research found new papers. They will be added to your collection.`);

    // Limit to maximum 10 papers without a warning notification
    if (uniqueUrls.length > 10) {
      uniqueUrls = uniqueUrls.slice(0, 10);
    }

    try {
      const successCount = await createPapersFromUrls(uniqueUrls);
      
      if (successCount === 0) {
        // If no paper is created, show an error notification
        addNotification('warning', 'No new papers were added to your collection.');
      } else {
        addNotification('success', `${successCount} new paper(s) added to your collection.`, {
          label: 'See',
          onClick: () => setCurrentMenu('papers')
        });
      }
    } catch (error) {
      console.error('Error creating papers:', error);
      addNotification('error', 'Failed to add papers to your collection.');
    }
  }

  const createPapersFromUrls = async (urls: string[]) => {
    console.log(`Creating papers from ${urls.length} urls`);

    const timeout = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Request timed out')), 600000) // 10 minutes
    );

    const successCount = await Promise.race([createPapers(urls), timeout]);

    console.log('Finished creating papers from urls');
    await fetchPapers();
    return successCount;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '' || aiTyping || !researchId) return

    setInput('')
    setAiTyping(true)
    setShowThinking(true)

    const userMessage: AgentMessage = {
      order: 0,
      type: AgentMessageType.human,
      content: input.trim(),
    }
    setMessages(prev => [...prev, userMessage])
    await saveResearchMessage(researchId, userMessage)
    const payload: MessageRequest = {
      query: input.trim(),
      custom_instructions: user.current?.customInstructions || undefined,
      model_provider: session?.data?.user?.sessionProviders?.find(p => p.modelProvider.selected)?.modelProvider.name || ModelProviderType.default,
      provider_details: session?.data?.user?.sessionProviders?.find(p => p.modelProvider.selected)?.details || null
    }
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
        <h1 className="text-4xl font-bold mb-2">📚 NexusAI 🤖</h1>
        <p className="text-xl text-muted-foreground">
          Research scientific literature in minutes, not hours
        </p>
      </motion.div>
      <div className="flex-1 overflow-y-auto space-y-4 px-4 no-scrollbar">
        {messages.map((m, index) => {
          if (
            m.type === AgentMessageType.final &&
            index >= 2 &&
            messages[index - 2].type === AgentMessageType.human &&
            messages[index - 1].type === AgentMessageType.agent
          ) {
            return null;
          }
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
                  <span className="absolute right-0 top-10 text-sm transform translate-x-1">
                    Copied!
                  </span>
                )}
                <div className="message-content">
                  <h2>✅ Task Completed</h2>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
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
                          remarkPlugins={[remarkGfm, remarkMath]}
                          rehypePlugins={[rehypeKatex]}
                          components={{ a: MarkdownLink }}
                        >
                          {m.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    <div className="message-content">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
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
        {aiTyping && showThinking && (
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
        <form onSubmit={handleSubmit} className="flex w-full max-w-[800px] space-x-2">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder={researchId ? "Type your message..." : "What do you want to research?"}
            className="flex-1"
            disabled={!isConnected}
          />
          <Button type="submit" disabled={aiTyping || !isConnected} size="icon">
            <Icons.arrowRight className="h-4 w-4" />
          </Button>
        </form>
      </motion.div>
    </div>
  )
} 