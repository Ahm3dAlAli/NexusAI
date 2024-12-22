import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { order, type, content, toolName } = await request.json()
    
    const message = await prisma.message.create({
      data: {
        conversationId: params.id,
        order,
        type,
        content,
        toolName,
      }
    })

    return NextResponse.json(message)
  } catch (error) {
    console.error('Error saving message:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}