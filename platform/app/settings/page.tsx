'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Icons } from '@/components/ui/icons'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { X, Pencil, Check } from 'lucide-react'
import { updateUser, fetchUser } from '@/lib/user'
import useSWR from 'swr'

const fetcher = () => fetchUser()

const SettingsPage: React.FC = () => {
  const { data: session } = useSession()
  const router = useRouter()

  const { data, mutate } = useSWR('/api/users/me', fetcher)

  const [username, setUsername] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [instructions, setInstructions] = useState<string[]>([])
  const [newInstruction, setNewInstruction] = useState('')
  const [collectPapers, setCollectPapers] = useState<boolean | undefined>(undefined)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (data) {
      setUsername(data.name || '')
      setInstructions(data.customInstructions || [])
      setCollectPapers(data.collectPapers ?? true)
    }
  }, [data])

  if (!session?.user) {
    router.push('/login')
    return null
  }

  const handleUsernameSave = async () => {
    if (username.trim() === '') {
      setErrorMsg('Username cannot be empty.')
      return
    }

    setIsSaving(true)
    try {
      await updateUser({ name: username })
      setIsEditing(false)
      setErrorMsg(null)
      mutate()
    } catch (err) {
      setErrorMsg((err as Error).message || 'Failed to update user.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCollectPapersToggle = async (value: boolean) => {
    setCollectPapers(value)
    try {
      await updateUser({ collectPapers: value })
      setErrorMsg(null)
      mutate()
    } catch (err) {
      setErrorMsg((err as Error).message || 'Failed to update collect papers settings.')
    }
  }

  const handleAddInstruction = async () => {
    if (newInstruction.trim() === '') return
    try {
      const updatedInstructions = [...instructions, newInstruction.trim()]
      await updateUser({ customInstructions: updatedInstructions })
      setInstructions(updatedInstructions)
      setNewInstruction('')
      setErrorMsg(null)
      mutate() // Refresh data
    } catch (err) {
      setErrorMsg((err as Error).message || 'Failed to update custom instructions.')
    }
  }

  const handleRemoveInstruction = async (index: number) => {
    try {
      const updatedInstructions = [...instructions]
      updatedInstructions.splice(index, 1)
      await updateUser({ customInstructions: updatedInstructions })
      setInstructions(updatedInstructions)
      setErrorMsg(null)
      mutate()
    } catch (err) {
      setErrorMsg((err as Error).message || 'Failed to update custom instructions.')
    }
  }

  return (
    <div className="container max-w-3xl mx-auto py-8 space-y-6 h-[calc(100vh-4rem)] overflow-y-auto no-scrollbar">
      <Card>
        <CardHeader>
          <div className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl">Account</CardTitle>
            <div className="flex gap-2">
              {isEditing && (
                <>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleUsernameSave}
                    title="Save"
                    className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                    disabled={isSaving}
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setIsEditing(false)
                      setUsername(data?.name || '')
                      setErrorMsg(null)
                    }}
                    title="Dismiss"
                    className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                    disabled={isSaving}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </>
              )}
              {!isEditing && session.user.password && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsEditing(true)}
                  title="Edit"
                  className="h-8 w-8 hover:bg-primary hover:text-primary-foreground"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {errorMsg && (
              <div className="text-red-500 text-sm">{errorMsg}</div>
            )}
            <div className="flex items-center">
              <span className="font-medium w-24">Username</span>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`flex-1 ${!isEditing ? 'bg-transparent border-none shadow-none focus-visible:ring-0' : ''}`}
                readOnly={!isEditing}
              />
            </div>
            <div className="flex items-center">
              <span className="font-medium w-24">Email</span>
              <Input
                value={session.user.email}
                className="flex-1 bg-transparent border-none shadow-none focus-visible:ring-0"
                readOnly
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl">Papers Collection</CardTitle>
            {collectPapers !== undefined && (
              <Switch
                checked={collectPapers}
                onCheckedChange={handleCollectPapersToggle}
                aria-label="Toggle paper collection"
              />
            )}
          </div>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            When enabled, papers referenced during your research will be automatically saved to your collection. 
            This allows you to build a personal library of relevant papers and access them later.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Custom Instructions</CardTitle>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <p className="font-medium text-muted-foreground mb-4">
            These instructions will be used by the agent during research to better understand your preferences and requirements.
          </p>
          <div className="flex items-center gap-2 mb-4">
            <Input
              value={newInstruction}
              onChange={(e) => setNewInstruction(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleAddInstruction()
                }
              }}
              placeholder="What should the agent remember during its research?"
              className="flex-1"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleAddInstruction}
              title="Add instruction"
              className="h-8 w-8 hover:bg-primary hover:text-primary-foreground"
            >
              <Icons.plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-2">
            {instructions.map((instruction, index) => (
              <Card key={index} className="flex justify-between items-center p-4">
                <span>{instruction}</span>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => handleRemoveInstruction(index)}
                  title="Remove"
                  className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </Button>
              </Card>
            ))}
            {instructions.length === 0 && (
              <p className="text-sm text-muted-foreground">No instructions added.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SettingsPage
