'use client'

import { useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { SignupForm } from "@/components/signup-form"

export default function SignupPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return
    if (session) router.push('/')
  }, [session, status, router])

  if (status === "loading" || session) {
    return null
  }

  return <SignupForm />
}
