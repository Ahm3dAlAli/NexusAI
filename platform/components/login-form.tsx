'use client'

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Input, InputWrapper } from '@/components/ui/input'
import { Icons } from '@/components/ui/icons'
import Link from 'next/link'

export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError('Invalid credentials')
      }
    } catch {
      setError('An error occurred during sign in')
    } finally {
      setIsLoading(false)
    }
  }

  const handleMicrosoftLogin = () => {
    setIsLoading(true)
    signIn('azure-ad', { callbackUrl: '/' })
      .catch(() => {
        setError('An error occurred with Microsoft sign in')
      })
      .finally(() => {
        setIsLoading(false)
      })
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="mx-auto w-full max-w-md space-y-6 p-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Welcome back</h1>
          <p className="text-gray-500">Enter your credentials to sign in</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <InputWrapper>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
          </InputWrapper>
          
          <InputWrapper>
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
          </InputWrapper>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
            Sign In
          </Button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Or continue with
            </span>
          </div>
        </div>

        <Button
          variant="outline"
          type="button"
          className="w-full"
          onClick={handleMicrosoftLogin}
          disabled={isLoading}
        >
          <Icons.microsoft className="mr-2 h-4 w-4" />
          Microsoft
        </Button>

        <p className="text-center text-sm text-gray-500">
          Not registered yet?{' '}
          <Link href="/signup" className="text-blue-500 hover:text-blue-700">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}