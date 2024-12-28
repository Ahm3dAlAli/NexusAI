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
      include: {
        messages: {
          orderBy: [
            { createdAt: 'asc' },
            { order: 'asc' },
          ],
        },
      },
    })

    if (!research) {
      return NextResponse.json(null, { status: 404 })
    }

    if (research.userId !== session.user.id) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    }

    return NextResponse.json(research)
  } catch (error) {
    console.error('Error fetching research:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}