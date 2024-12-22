import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma'
import { AgentMessageType } from '@prisma/client'

export async function GET() {
  const conversations = await prisma.conversation.findMany({
    orderBy: {
      updatedAt: 'desc',
    },
    include: {
      messages: true,
    },
  })

  return NextResponse.json(conversations, { status: 200 })
}

export async function POST(req: Request) {
  const { title, initialMessage } = await req.json()
  if (!title) {
    return NextResponse.json({ error: 'Title is required' }, { status: 400 })
  }
  
  const conversation = await prisma.conversation.create({
    data: {
      title,
      messages: {
        create: initialMessage ? {
          order: 0,
          type: AgentMessageType.human,
          content: initialMessage,
        } : undefined
      }
    },
    include: {
      messages: true,
    }
  })
  
  return NextResponse.json(conversation, { status: 201 })
}
