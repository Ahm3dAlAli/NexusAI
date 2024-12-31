'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Icons } from '@/components/ui/icons'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { X, Pencil, Check } from 'lucide-react'

const SettingsPage: React.FC = () => {
  const { data: session } = useSession()
  const router = useRouter()

  const [username, setUsername] = useState(session?.user?.name || '')
  const [isEditing, setIsEditing] = useState(false)
  const [instructions, setInstructions] = useState<string[]>([])
  const [newInstruction, setNewInstruction] = useState('')
  const [collectPapers, setCollectPapers] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  if (!session?.user) {
    router.push('/login')
    return null
  }

  const handleUsernameSave = async () => {
    if (username.trim() === '') {
      setError('Username cannot be empty.')
      return
    }

    setIsSaving(true)
    try {
      // Assuming that password is null if user logged in via Microsoft
      const canEdit = session.user.password !== null
      if (!canEdit) {
        setError('Cannot change username for Microsoft accounts.')
        setUsername(session.user.name || '')
        setIsEditing(false)
        return
      }

      setError(null)
      // Add your save logic here if needed
      await new Promise(resolve => setTimeout(resolve, 500))  // Simulate API call if needed
      setIsEditing(false)
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddInstruction = () => {
    if (newInstruction.trim() === '') return
    setInstructions([...instructions, newInstruction.trim()])
    setNewInstruction('')
  }

  const handleRemoveInstruction = (index: number) => {
    const updated = [...instructions]
    updated.splice(index, 1)
    setInstructions(updated)
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
                      setUsername(session.user.name || '')
                      setError(null)
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
            {error && (
              <div className="text-red-500 text-sm">{error}</div>
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

      <Card className={!collectPapers ? "opacity-45" : ""}>
        <CardHeader>
          <div className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl">Papers Collection</CardTitle>
            <Switch
              checked={collectPapers}
              onCheckedChange={setCollectPapers}
              aria-label="Toggle paper collection"
            />
          </div>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <p className="font-medium text-muted-foreground">
            When enabled, new papers found during research will be automatically added to your collection.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default SettingsPage
