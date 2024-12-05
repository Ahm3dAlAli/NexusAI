'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ReactMarkdown from 'react-markdown'
import { AgentMessage, AgentMessageType } from '@/types/AgentMessage'
import { Copy } from "lucide-react"
import {
  Card,
  CardContent,
} from "@/components/ui/card"

const MarkdownLink = ({
  href,
  children,
  ...props
}: React.AnchorHTMLAttributes<HTMLAnchorElement>) => {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
      {children}
    </a>
  )
}

export default function Chat() {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [input, setInput] = useState('')
  const [aiTyping, setAiTyping] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    ws.current = new WebSocket('ws://localhost:8000/ws')

    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
    }

    ws.current.onmessage = (event) => {
      const message: AgentMessage = JSON.parse(event.data)
      setMessages(prev => [...prev, message])

      if (message.type === AgentMessageType.final) {
        setAiTyping(false)
      }
    }

    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }

    return () => {
      ws.current?.close()
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, aiTyping])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '' || aiTyping) return

    const userMessage: AgentMessage = {
      type: AgentMessageType.human,
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setAiTyping(true)

    // Send message to WebSocket
    ws.current?.send(JSON.stringify({ query: input.trim() }))
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
    <div className="flex flex-col h-screen max-w-5xl mx-auto p-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">🤖 NexusAI 📚</h1>
        <p className="text-xl text-muted-foreground">Your assistant to research scientific literature in minutes instead of hours</p>
      </div>
      <div className="flex-1 overflow-y-auto space-y-4">
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
              <div key={index} className="final-message group relative">
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
                  <h2>Task Completed:</h2>
                  <ReactMarkdown components={{ a: MarkdownLink }}>{m.content}</ReactMarkdown>
                </div>
              </div>
            );
          }

          return (
            <Card
              key={index}
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
                      <ReactMarkdown components={{ a: MarkdownLink }}>{m.content}</ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <div className="message-content">
                    <ReactMarkdown components={{ a: MarkdownLink }}>{m.content}</ReactMarkdown>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
        {aiTyping && (
          <Card className="mb-4 mr-auto max-w-[80%]">
            <CardContent className="flex items-center p-4">
              <div>💭 Thinking...</div>
            </CardContent>
          </Card>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex justify-center w-full">
        <form onSubmit={handleSubmit} className="flex space-x-2 mt-4 w-full max-w-[75%]">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="What do you want to research?"
            className="flex-1"
            disabled={!isConnected}
          />
          <Button type="submit" disabled={aiTyping || !isConnected}>Send</Button>
        </form>
      </div>
    </div>
  )
}