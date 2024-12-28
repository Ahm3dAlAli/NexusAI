import { NextResponse } from 'next/server'
import { getServerSession } from "next-auth"
import { authOptions } from '../auth/[...nextauth]/auth'
import { sign } from 'jsonwebtoken'

const WS_TOKEN_SECRET = process.env.NEXTAUTH_SECRET

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session || !session.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Create a short-lived token (5 minutes)
  const token = sign(
    { 
      userId: session.user.id,
      email: session.user.email 
    },
    WS_TOKEN_SECRET!,
    { expiresIn: '5m' }
  )

  return NextResponse.json({ token })
}
