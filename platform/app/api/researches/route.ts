import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma'
import { getServerSession } from "next-auth"
import { authOptions } from '../auth/[...nextauth]/auth'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session || !session.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const researches = await prisma.research.findMany({
    where: { userId: session.user.id },
    orderBy: {
      updatedAt: 'desc',
    },
    include: {
      messages: true,
    },
  })

  return NextResponse.json(researches, { status: 200 })
}

export async function POST(req: Request) {
  const session = await getServerSession(authOptions)
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { title } = await req.json()
  if (!title) {
    return NextResponse.json({ error: 'Title is required' }, { status: 400 })
  }
  
  const research = await prisma.research.create({
    data: {
      title,
      userId: session.user.id,
    },
    include: {
      messages: true,
    }
  })

  return NextResponse.json(research, { status: 201 })
}