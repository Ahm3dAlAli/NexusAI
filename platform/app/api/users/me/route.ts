import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { getServerSession } from "next-auth"
import { authOptions } from '../../auth/[...nextauth]/auth'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const user = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: {
        id: true,
        name: true,
        email: true,
        password: true,
        collectPapers: true,
        customInstructions: true,
        modelProviders: {
          select: {
            id: true,
            name: true,
            selected: true,
          }
        },
      },
    })

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    return NextResponse.json(user)
  } catch (error) {
    console.error('Error fetching user:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function PUT(req: Request) {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const updates = await req.json()
    const allowedUpdates = ['name', 'collectPapers', 'customInstructions']
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([key]) => allowedUpdates.includes(key))
    )

    // Handle provider selection update if present
    if ('selectedProviderId' in updates) {
      // First, unselect all providers
      await prisma.modelProvider.updateMany({
        where: { userId: session.user.id },
        data: { selected: false },
      })

      // Then select the specified provider if not default
      if (updates.selectedProviderId && updates.selectedProviderId !== 'default') {
        await prisma.modelProvider.update({
          where: { 
            id: updates.selectedProviderId,
            userId: session.user.id,
          },
          data: { selected: true },
        })
      }
    }

    const user = await prisma.user.update({
      where: { id: session.user.id },
      data: filteredUpdates,
      select: {
        id: true,
        name: true,
        email: true,
        password: true,
        collectPapers: true,
        customInstructions: true,
        modelProviders: {
          select: {
            id: true,
            name: true,
            selected: true,
          }
        },
      },
    })

    return NextResponse.json(user)
  } catch (error) {
    console.error('Error updating user:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
} 