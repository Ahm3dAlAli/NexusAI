import { sign } from 'jsonwebtoken'

interface UserTokenPayload {
  userId: string
  email: string
}

export function generateWebSocketToken(user: UserTokenPayload): string {
  return sign(
    { 
      userId: user.userId,
      email: user.email
    },
    process.env.NEXTAUTH_SECRET!,
    { expiresIn: '5m' }
  )
}
