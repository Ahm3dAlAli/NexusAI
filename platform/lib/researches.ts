import { AgentMessage } from '@/types/AgentMessage'
import { AgentMessageType, Research, Message } from '@prisma/client'

export async function fetchResearches(): Promise<Research[]> {
  const response = await fetch('/api/researches')
  if (!response.ok) {
    throw new Error('Failed to fetch researches')
  }
  return response.json()
}

export async function fetchResearch(id: string): Promise<Research> {
  const response = await fetch(`/api/researches/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch research')
  }
  return response.json()
}

export async function createResearch({ 
  title,
}: { 
  title: string 
}): Promise<Research> {
  const response = await fetch('/api/researches', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
  if (!response.ok) {
    throw new Error('Failed to create research')
  }
  return response.json()
}

export async function fetchMessages(researchId: string): Promise<AgentMessage[]> {
  const response = await fetch(`/api/researches/${researchId}/messages`)
  if (!response.ok) {
    throw new Error('Failed to fetch messages')
  }
  const data = await response.json()
  return data.messages.map((msg: Message): AgentMessage => ({
    order: msg.order,
    type: msg.type as AgentMessageType,
    content: msg.content,
    tool_name: msg.toolName ?? undefined
  }))
}

export async function saveMessage(researchId: string, message: AgentMessage) {
  const response = await fetch(`/api/researches/${researchId}/messages`, {
    method: 'POST',
    body: JSON.stringify(message),
  })
  if (!response.ok) {
    throw new Error('Failed to save message')
  }
  return response.json()
}