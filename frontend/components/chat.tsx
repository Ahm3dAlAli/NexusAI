'use client'

import { useState } from 'react'
import { useChat } from 'ai/react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function Chat() {
  const [aiTyping, setAiTyping] = useState(false)
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    onFinish: () => setAiTyping(false),
  })

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    setAiTyping(true)
    handleSubmit(e)
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map(m => (
          <div
            key={m.id}
            className={`p-4 rounded-lg ${
              m.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
            } max-w-[80%]`}
          >
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" />
              }}
            >
              {m.content}
            </ReactMarkdown>
          </div>
        ))}
        {aiTyping && (
          <div className="bg-gray-100 p-4 rounded-lg max-w-[80%]">
            <div className="animate-pulse">Typing...</div>
          </div>
        )}
      </div>
      <form onSubmit={onSubmit} className="flex space-x-2 mt-4">
        <Input
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="flex-1"
        />
        <Button type="submit">Send</Button>
      </form>
    </div>
  )
}

