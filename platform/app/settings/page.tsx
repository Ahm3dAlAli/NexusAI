'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { updateUser, fetchUser } from '@/lib/user'
import useSWR from 'swr'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { ComboboxDemo } from '@/components/ui/combobox'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Icons } from '@/components/ui/icons'
import { ProviderForm } from '@/components/provider-form'
import { ModelProviderType } from '@prisma/client'
import { SessionModelProvider, ProviderDetails, deleteModelProvider, updateModelProvider, createModelProvider } from '@/lib/modelProviders'
import { providerEnumToName, providerNameToEnum } from '@/lib/utils'
import { useNotification } from '@/context/NotificationContext'

const fetcher = () => fetchUser()

interface ModelProviderInput {
  id?: string;
  name: ModelProviderType;
  details: ProviderDetails;
}

const SettingsPage: React.FC = () => {
  const { data: session, status, update: updateSession } = useSession()
  const router = useRouter()
  const { addNotification } = useNotification()

  const { data, mutate } = useSWR('/api/users/me', fetcher)

  const [username, setUsername] = useState('')
  const [isAccountEditing, setIsAccountEditing] = useState(false)
  const [instructions, setInstructions] = useState<string[]>([])
  const [newInstruction, setNewInstruction] = useState('')
  const [collectPapers, setCollectPapers] = useState<boolean | undefined>(undefined)
  const [isSaving, setIsSaving] = useState(false)

  // State for Model Providers
  const [sessionProviders, setSessionProviders] = useState<SessionModelProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string>('')
  const [showProviderDialog, setShowProviderDialog] = useState(false)
  const [pendingProvider, setPendingProvider] = useState<string>('')
  const [providerDetails, setProviderDetails] = useState<ProviderDetails>({})
  const [isProviderSaving, setIsProviderSaving] = useState(false)
  const [isProviderEditing, setIsProviderEditing] = useState(false)
  const [editingProviderId, setEditingProviderId] = useState<string | undefined>()

  // Instructions
  const [editingInstruction, setEditingInstruction] = useState<{index: number, text: string} | null>(null)

  // Providers
  const availableProviders = ['Azure OpenAI', 'OpenAI'].sort()
  const defaultProvider = useMemo(() => ({
    modelProvider: {
      id: 'default',
      name: 'default' as ModelProviderType,
      userId: session?.user?.id || '',
      secretName: '',
      selected: false
    },
    details: {}
  }), [session?.user?.id])

  const [openAccordionItem, setOpenAccordionItem] = useState<string | undefined>(undefined)

  // Add new state for delete loading
  const [deletingProviderId, setDeletingProviderId] = useState<string | null>(null)

  useEffect(() => {
    if (data) {
      setUsername(data.name || '')
      setInstructions(data.customInstructions || [])
      setCollectPapers(data.collectPapers ?? true)
    }

    // Update session providers whenever session changes
    if (session?.user?.sessionProviders) {
      const providers = [defaultProvider, ...session.user.sessionProviders]
      setSessionProviders(providers)
      
      // Find the selected provider from the session providers
      const selectedProv = session.user.sessionProviders.find(p => 
        p.modelProvider.selected
      )
      
      // Set selected provider name, defaulting to 'default' if none found
      setSelectedProvider(selectedProv ? selectedProv.modelProvider.name : 'default')
    } else {
      setSessionProviders([defaultProvider])
      setSelectedProvider('default')
    }
  }, [data, session, defaultProvider])

  useEffect(() => {
    if (status === "loading") return
    if (!session) router.push('/login')
  }, [session, status, router])

  if (status === "loading" || deletingProviderId || isProviderSaving) {
    return (
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    )
  }

  if (!session?.user) {
    return null
  }

  // Account
  const handleUsernameSave = async () => {
    if (username.trim() === '') {
      addNotification('error', 'Username cannot be empty.')
      return
    }

    setIsSaving(true)
    try {
      await updateUser({ name: username })
      setIsAccountEditing(false)
      mutate()
    } catch (err) {
      addNotification('error', (err as Error).message || 'Failed to update user.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCollectPapersToggle = async (value: boolean) => {
    setCollectPapers(value)
    try {
      await updateUser({ collectPapers: value })
      mutate()
    } catch (err) {
      addNotification('error', (err as Error).message || 'Failed to update collect papers settings.')
    }
  }

  // Instructions
  const handleAddInstruction = async () => {
    if (newInstruction.trim() === '') return
    try {
      const updatedInstructions = [...instructions, newInstruction.trim()]
      await updateUser({ customInstructions: updatedInstructions })
      setInstructions(updatedInstructions)
      setNewInstruction('')
      mutate()
    } catch (err) {
      addNotification('error', (err as Error).message || 'Failed to update custom instructions.')
    }
  }

  const handleEditInstruction = async () => {
    if (!editingInstruction || editingInstruction.text.trim() === '') return
    try {
      const updatedInstructions = [...instructions]
      updatedInstructions[editingInstruction.index] = editingInstruction.text.trim()
      await updateUser({ customInstructions: updatedInstructions })
      setInstructions(updatedInstructions)
      setEditingInstruction(null)
      mutate()
    } catch (err) {
      addNotification('error', (err as Error).message || 'Failed to update custom instruction.')
    }
  }

  const handleRemoveInstruction = async (index: number) => {
    try {
      const updatedInstructions = [...instructions]
      updatedInstructions.splice(index, 1)
      await updateUser({ customInstructions: updatedInstructions })
      setInstructions(updatedInstructions)
      mutate()
    } catch (err) {
      addNotification('error', (err as Error).message || 'Failed to update custom instructions.')
    }
  }

  // Providers
  const handleAddProvider = (providerDisplayName: string) => {
    const providerEnum = providerNameToEnum(providerDisplayName)
    if (!providerEnum) return
    
    setPendingProvider(providerEnum)
    setProviderDetails({})
    setIsProviderEditing(false)
    setShowProviderDialog(true)
  }

  const handleProviderSubmit = async (providerInput: ModelProviderInput) => {
    try {
      let provider;
      setShowProviderDialog(false);
      setIsProviderSaving(true)
      if (isProviderEditing && providerInput.id) {
        provider = await updateModelProvider(providerInput.id, providerInput.details);
      } else {
        provider = await createModelProvider(providerInput.name, providerInput.details);
      }

      // Update session with new provider
      const updatedProviders = sessionProviders.filter(p => 
        p.modelProvider.id !== provider.modelProvider.id && 
        p.modelProvider.name !== 'default'
      );
      
      const newProviders = [defaultProvider, ...updatedProviders, provider];
      setSessionProviders(newProviders);

      // Update the session
      await updateSession({
        sessionProviders: newProviders.filter(p => p.modelProvider.name !== 'default')
      });

      // Reset form state
      setProviderDetails({});
      setPendingProvider('');
      setIsProviderSaving(false)
      setIsProviderEditing(false);
      setEditingProviderId(undefined);
    } catch (error) {
      console.error('Error managing AI model provider:', error);
      addNotification('error', 'Failed to save AI model provider settings');
    }
  };

  const handleEditProvider = (provider: SessionModelProvider) => {
    setEditingProviderId(provider.modelProvider.id)
    setProviderDetails(provider.details)
    setPendingProvider(provider.modelProvider.name)
    setIsProviderEditing(true)
    setShowProviderDialog(true)
  }

  const handleRemoveProvider = async (provider: SessionModelProvider) => {
    // Ask for confirmation before deleting
    const isConfirmed = window.confirm(`Are you sure you want to remove ${providerEnumToName(provider.modelProvider.name)} from your AI model providers?`);
    if (!isConfirmed) return;

    // Set loading state immediately after confirmation
    setDeletingProviderId(provider.modelProvider.id)

    try {
      await deleteModelProvider(provider.modelProvider.id);

      // Update local state while preserving default provider
      const updatedProviders = [
        defaultProvider,
        ...sessionProviders.filter(p => 
          p.modelProvider.id !== provider.modelProvider.id && 
          p.modelProvider.name !== 'default'
        )
      ];
      setSessionProviders(updatedProviders);

      // If we're removing the selected provider, select the default
      if (selectedProvider === provider.modelProvider.name) {
        setSelectedProvider('default');
      }

      // Update session with new providers (excluding default)
      await updateSession({
        sessionProviders: updatedProviders.filter(p => p.modelProvider.name !== 'default')
      });
    } catch (error) {
      console.error('Error removing AI model provider:', error);
      addNotification('error', 'Failed to remove AI model provider');
    } finally {
      setDeletingProviderId(null)
    }
  };

  const handleSelectProvider = async (providerName: string) => {
    try {
      // Update the database through the user update endpoint
      await updateUser({ selectedProviderId: providerName === 'default' ? null : 
        sessionProviders.find(p => p.modelProvider.name === providerName)?.modelProvider.id
      });

      // Update local state
      setSelectedProvider(providerName);

      // Update session with the new selection
      await updateSession({
        sessionProviders: sessionProviders.filter(p => p.modelProvider.name !== 'default').map(p => ({
          ...p,
          modelProvider: {
            ...p.modelProvider,
            selected: p.modelProvider.name === providerName
          }
        }))
      });

    } catch (error) {
      console.error('Error selecting AI model provider:', error);
      addNotification('error', 'Failed to update selected AI model provider');
    }
  };

  // Clear error when dialog closes
  const handleDialogOpenChange = (open: boolean) => {
    if (!open) {
      // Only clear states when dialog is actually closing
      setShowProviderDialog(false)
      setEditingProviderId(undefined)
      setPendingProvider('')
      setProviderDetails({})
      setIsProviderEditing(false)
    }
  }

  return (
    <div className="container max-w-3xl mx-auto py-8 space-y-6 h-[calc(100vh-4rem)] overflow-y-auto no-scrollbar">
      {/* Account Card */}
      <Card>
        <CardHeader>
          <div className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl">Account</CardTitle>
            <div className="flex gap-2">
              {isAccountEditing && (
                <>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleUsernameSave}
                    title="Save"
                    className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                    disabled={isSaving}
                  >
                    <Icons.check className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setIsAccountEditing(false)
                      setUsername(data?.name || '')
                    }}
                    title="Dismiss"
                    className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                    disabled={isSaving}
                  >
                    <Icons.x className="h-4 w-4" />
                  </Button>
                </>
              )}
              {!isAccountEditing && session.user.password && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsAccountEditing(true)}
                  title="Edit"
                  className="h-8 w-8 hover:bg-primary hover:text-primary-foreground"
                >
                  <Icons.edit className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center">
              <span className="font-bold w-24">Username</span>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`flex-1 ${!isAccountEditing ? 'bg-transparent border-none shadow-none focus-visible:ring-0' : ''}`}
                readOnly={!isAccountEditing}
              />
            </div>
            <div className="flex items-center">
              <span className="font-bold w-24">Email</span>
              <Input
                value={session.user.email}
                className="flex-1 bg-transparent border-none shadow-none focus-visible:ring-0"
                readOnly
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Research Settings Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Research Settings</CardTitle>
          <div className="pt-4 border-t" />
        </CardHeader>
        <CardContent>
          <Accordion 
            type="single" 
            collapsible 
            value={openAccordionItem}
            onValueChange={setOpenAccordionItem}
          >
            {/* Collect Papers Accordion */}
            <AccordionItem value="collect-papers">
              <AccordionTrigger className="font-bold text-base hover:no-underline">
                <div className="flex-1 hover:underline">Collect papers</div>
                <div className="text-sm font-normal text-muted-foreground mr-2">
                  {collectPapers ? 'On' : 'Off'}
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="text-muted-foreground">
                  When enabled, relevant papers will be automatically saved to your collection. 
                  This allows you to build a personal library of relevant papers that you can access later.
                </p>
                <div className="mt-4 flex items-center">
                  <Switch
                    checked={collectPapers}
                    onCheckedChange={handleCollectPapersToggle}
                    aria-label="Toggle paper collection"
                  />
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Custom Instructions Accordion */}
            <AccordionItem value="custom-instructions">
              <AccordionTrigger className="font-bold text-base hover:no-underline">
                <div className="flex-1 hover:underline">Custom instructions</div>
                <div className="text-sm font-normal text-muted-foreground mr-2">
                  {instructions.length === 0 ? 'None' : `${instructions.length} added`}
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="font-medium text-muted-foreground mb-4">
                  These instructions will be used by NexusAI during research to better understand your preferences.
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
                    placeholder="What should the agent remember about you?"
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
                      {editingInstruction?.index === index ? (
                        <div className="flex-1 flex items-center gap-2">
                          <Input
                            value={editingInstruction.text}
                            onChange={(e) => setEditingInstruction({ 
                              index, 
                              text: e.target.value 
                            })}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                handleEditInstruction()
                              }
                            }}
                            className="flex-1"
                          />
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={handleEditInstruction}
                              title="Save"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            >
                              <Icons.check className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setEditingInstruction(null)}
                              title="Cancel"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            >
                              <Icons.x className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <span className="flex-1">{instruction}</span>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => setEditingInstruction({ index, text: instruction })}
                              title="Edit"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            >
                              <Icons.edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="icon"
                              onClick={() => handleRemoveInstruction(index)}
                              title="Remove"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            >
                              <Icons.trash className="h-4 w-4" />
                            </Button>
                          </div>
                        </>
                      )}
                    </Card>
                  ))}
                  {instructions.length === 0 && (
                    <p className="text-sm text-muted-foreground">No instructions added.</p>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Model Accordion */}
            <AccordionItem value="model">
              <AccordionTrigger className="font-bold text-base hover:no-underline">
                <div className="flex-1 hover:underline">AI model</div>
                <div className="text-sm font-normal text-muted-foreground mr-2">
                  {selectedProvider === 'default' ? 'Default' : providerEnumToName(selectedProvider as ModelProviderType)}
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="font-medium text-muted-foreground mb-4">
                  Select the AI model to use during research.
                </p>
                <div className="space-y-4">
                  {/* Add Provider */}
                  <ComboboxDemo 
                    onSelect={handleAddProvider} 
                    availableOptions={availableProviders.filter(p => 
                      !sessionProviders.some(mp => 
                        mp.modelProvider.name === providerNameToEnum(p)
                      )
                    )} 
                  />
                  
                  {/* List of Model Providers */}
                  {sessionProviders
                    .sort((a, b) => {
                      // Always keep default provider at the top
                      if (a.modelProvider.name === 'default') return -1;
                      if (b.modelProvider.name === 'default') return 1;
                      // Sort other providers alphabetically by their display names
                      return providerEnumToName(a.modelProvider.name).localeCompare(providerEnumToName(b.modelProvider.name));
                    })
                    .map((provider) => (
                      <Card key={provider.modelProvider.id} className="flex items-center justify-between p-4">
                        <div className="flex items-center">
                          <Checkbox
                            checked={selectedProvider === provider.modelProvider.name}
                            onCheckedChange={() => handleSelectProvider(provider.modelProvider.name)}
                            id={`provider-${provider.modelProvider.id}`}
                          />
                          <div className="flex items-center ml-3">
                            <label 
                              htmlFor={`provider-${provider.modelProvider.id}`}
                              className="font-medium cursor-pointer"
                            >
                              {provider.modelProvider.name === 'default' 
                                ? 'Default' 
                                : providerEnumToName(provider.modelProvider.name)}
                            </label>
                          </div>
                        </div>
                        {provider.modelProvider.name === 'default' ? (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            title="If no other AI model provider is selected, NexusAI will use its default configuration."
                          >
                            <Icons.info className="h-4 w-4 text-muted-foreground" />
                          </Button>
                        ) : (
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEditProvider(provider)}
                              title="Edit"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                              disabled={deletingProviderId === provider.modelProvider.id}
                            >
                              <Icons.edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRemoveProvider(provider)}
                              title="Remove"
                              className="h-8 w-8 hover:bg-transparent hover:text-foreground"
                            >
                              <Icons.trash className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                      </Card>
                    ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>

      {/* Provider Details Dialog */}
      <Dialog open={showProviderDialog} onOpenChange={handleDialogOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{providerEnumToName(pendingProvider as ModelProviderType)}</DialogTitle>
          </DialogHeader>
          
          <ProviderForm
            provider={{
              id: editingProviderId,
              name: pendingProvider as ModelProviderType,
              details: providerDetails
            }}
            onSubmit={handleProviderSubmit}
            onCancel={() => {
              setShowProviderDialog(false);
              setEditingProviderId(undefined);
            }}
            isEditing={isProviderEditing}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default SettingsPage 