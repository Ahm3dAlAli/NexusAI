import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { getServerSession } from "next-auth"
import { authOptions } from '@/app/api/auth/[...nextauth]/auth'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const research = await prisma.research.findUnique({
      where: { id: params.id },
    })

    if (!research) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }

    if (research.userId !== session.user.id) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    }

    const messages = await prisma.message.findMany({
      where: { researchId: params.id },
      orderBy: [
        { createdAt: 'asc' },
        { order: 'asc' },
      ],
    })

    return NextResponse.json({ messages }, { status: 200 })
  } catch (error) {
    console.error('Error fetching messages:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const research = await prisma.research.findUnique({
      where: { id: params.id },
    })

    if (!research) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }

    if (research.userId !== session.user.id) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    }

    const { order, type, content, toolName } = await request.json()
    
    const message = await prisma.message.create({
      data: {
        researchId: params.id,
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