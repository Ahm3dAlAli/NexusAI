'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ReactMarkdown from 'react-markdown'
import { AgentMessage, AgentMessageType } from '@/types/AgentMessage'
import { Copy } from "lucide-react"

const MarkdownLink = ({ href, children }: { href?: string, children: React.ReactNode }) => {
  return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
}

export default function Chat() {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [input, setInput] = useState('')
  const [aiTyping, setAiTyping] = useState(false)
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null)

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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '' || aiTyping) return

    const userMessage: AgentMessage = {
      type: AgentMessageType.system,
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
      case AgentMessageType.agent:
        return '🤖'
      case AgentMessageType.tool:
        return '⚙️'
      case AgentMessageType.system:
        return '👤'
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
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((m, index) => {
          // Skip final messages that follow a system->agent sequence
          if (
            m.type === AgentMessageType.final &&
            index >= 2 &&
            messages[index - 2].type === AgentMessageType.system &&
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
                  className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => copyToClipboard(m.content, index)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
                {copiedMessageIndex === index && (
                  <span className="absolute right-0 top-6 text-sm">Copied!</span>
                )}
                <div className="message-content">
                  <h2>Final Answer:</h2>
                  <ReactMarkdown components={{ a: MarkdownLink }}>{m.content}</ReactMarkdown>
                </div>
              </div>
            );
          }

          // Regular message rendering
          return (
            <div
              key={index}
              className={`p-4 ${
                m.type === AgentMessageType.system ? 'message-user' : 'message-ai'
              } max-w-[80%] flex`}
            >
              <span className="mr-2 text-xl mt-[6px]">{getEmoji(m.type)}</span>
              {m.type === AgentMessageType.tool ? (
                <div className="flex flex-col w-full">
                  {m.tool_name && (
                    <div className="font-bold mb-2 pb-2 border-b">{m.tool_name}</div>
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
            </div>
          );
        })}
        {aiTyping && (
          <div className="bg-gray-100 p-4 rounded-lg max-w-[80%] flex items-center">
            <div className="animate-pulse">💭 Working on it...</div>
          </div>
        )}
      </div>
      <div className="flex justify-center w-full">
        <form onSubmit={handleSubmit} className="flex space-x-2 mt-4 w-full max-w-[75%]">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="Type your message..."
            className="flex-1"
            disabled={aiTyping || !isConnected}
          />
          <Button type="submit" disabled={aiTyping || !isConnected}>Send</Button>
        </form>
      </div>
    </div>
  )
}