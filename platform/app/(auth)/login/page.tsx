'use client'

import { useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { LoginForm } from "@/components/login-form"

export default function LoginPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return
    if (session) router.push('/')
  }, [session, status, router])

  if (status === "loading" || session) {
    return null
  }

  return <LoginForm />
}
