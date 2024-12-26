import { AgentMessage } from '@/types/AgentMessage'
import { AgentMessageType, Conversation, Message } from '@prisma/client'

export async function fetchConversations(): Promise<Conversation[]> {
  const response = await fetch('/api/conversations')
  if (!response.ok) {
    throw new Error('Failed to fetch conversations')
  }
  return response.json()
}

export async function fetchConversation(id: string): Promise<Conversation> {
  const response = await fetch(`/api/conversations/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch conversation')
  }
  return response.json()
}

export async function createConversation({ 
  title,
  initialMessage
}: { 
  title: string 
  initialMessage: string
}): Promise<Conversation> {
  const response = await fetch('/api/conversations', {
    method: 'POST',
    body: JSON.stringify({ title, initialMessage }),
  })
  if (!response.ok) {
    throw new Error('Failed to create conversation')
  }
  return response.json()
}

export async function fetchMessages(conversationId: string): Promise<AgentMessage[]> {
  const response = await fetch(`/api/conversations/${conversationId}/messages`)
  if (!response.ok) {
    throw new Error('Failed to fetch messages')
  }
  const data = await response.json()
  return data.messages.map((msg: Message) => ({
    ...msg,
    type: msg.type as AgentMessageType,
  }))
}

export async function saveMessage(conversationId: string, message: AgentMessage) {
  const response = await fetch(`/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify(message),
  })
  if (!response.ok) {
    throw new Error('Failed to save message')
  }
  return response.json()
}