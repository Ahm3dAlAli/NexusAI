import { NextResponse } from 'next/server'
import { getServerSession } from "next-auth"
import { authOptions } from '../[...nextauth]/auth'
import { generateWebSocketToken } from '@/lib/jwt'


export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session || !session.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const token = generateWebSocketToken({
    userId: session.user.id,
    email: session.user.email
  })

  return NextResponse.json({ token })
}
