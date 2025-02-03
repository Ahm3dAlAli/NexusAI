'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input, InputWrapper } from '@/components/ui/input'
import { Icons } from '@/components/ui/icons'
import { DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { ModelProviderType } from '@prisma/client'
import { providerEnumToName } from '@/lib/utils'

// Define the types
interface ProviderDetails {
  key?: string
  endpoint?: string
}

interface ModelProviderInput {
  id?: string
  name: ModelProviderType
  details: ProviderDetails
}

interface ProviderFormProps {
  provider: ModelProviderInput
  onSubmit: (provider: ModelProviderInput) => void
  onCancel: () => void
  isEditing?: boolean
}

export function ProviderForm({
  provider,
  onSubmit,
  onCancel,
}: ProviderFormProps) {
  const [error, setError] = useState<string | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [providerDetails, setProviderDetails] = useState<ModelProviderInput>({
    id: provider.id,
    name: provider.name,
    details: provider.details || {}
  })

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    // Validation
    if (providerDetails.name === ModelProviderType.openai) {
      if (!providerDetails.details.key?.trim()) {
        setError('API Key is required')
        return
      }
    }

    if (providerDetails.name === ModelProviderType.azureopenai) {
      if (!providerDetails.details.key?.trim()) {
        setError('API Key is required')
        return
      }
      if (!providerDetails.details.endpoint?.trim()) {
        setError('API Endpoint is required')
        return
      }

      // Validate endpoint URL format
      try {
        new URL(providerDetails.details.endpoint)
      } catch {
        setError('Invalid API Endpoint URL format')
        return
      }
    }

    setError(null)
    setIsLoading(true)
    
    try {
      onSubmit(providerDetails)
    } catch (err) {
      setError((err as Error).message || 'Failed to save AI model provider details.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = (e: React.MouseEvent) => {
    e.preventDefault() // Prevent form submission
    onCancel()
  }

  const updateProviderDetails = (updates: Partial<typeof providerDetails.details>) => {
    setProviderDetails(prev => ({
      ...prev,
      details: { ...prev.details, ...updates }
    }))
    setError(null)
  }

  const LabelWithInfo = ({ htmlFor, label, info }: { htmlFor: string, label: string, info: string }) => (
    <div className="flex justify-between items-center">
      <Label htmlFor={htmlFor} className="font-bold">{label}</Label>
      <span
        className="ml-2 cursor-pointer flex-shrink-0"
        title={info}
      >
        <Icons.info className="h-4 w-4 text-muted-foreground" />
      </span>
    </div>
  )

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm text-muted-foreground mb-8">
        Provide the following parameters to integrate {providerEnumToName(provider.name)} with NexusAI.
      </p>

      {error && (
        <div className="text-sm font-medium text-destructive">
          {error}
        </div>
      )}

      {provider.name === ModelProviderType.openai && (
        <div className="space-y-2">
          <LabelWithInfo
            htmlFor="openai-api-key"
            label="API Key"
            info="The API key can be generated from the dashboard of your OpenAI account. For more information, visit https://platform.openai.com/docs/quickstart."
          />
          <InputWrapper>
            <div className="flex">
              <Input
                id="openai-api-key"
                type={showApiKey ? "text" : "password"}
                value={providerDetails.details.key || ''}
                onChange={(e) => updateProviderDetails({ key: e.target.value })}
                placeholder="Enter your API key"
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => setShowApiKey(!showApiKey)}
                className="ml-2"
                aria-label={showApiKey ? "Hide API Key" : "Show API Key"}
              >
                {showApiKey ? <Icons.eyeOff className="h-4 w-4" /> : <Icons.eye className="h-4 w-4" />}
              </Button>
            </div>
          </InputWrapper>
        </div>
      )}

      {provider.name === ModelProviderType.azureopenai && (
        <>
          <div className="space-y-2">
            <LabelWithInfo
              htmlFor="azure-endpoint"
              label="Target URI"
              info="The target URI can be found in the details page of your deployment in Azure AI Foundry. For more information, visit https://azure.microsoft.com/en-us/products/ai-foundry."
            />
            <InputWrapper>
              <Input
                id="azure-endpoint"
                value={providerDetails.details.endpoint || ''}
                onChange={(e) => updateProviderDetails({ endpoint: e.target.value })}
                placeholder="https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
                disabled={isLoading}
                className="flex-1"
              />
            </InputWrapper>
          </div>

          <div className="space-y-2">
            <LabelWithInfo
              htmlFor="azure-api-key"
              label="API Key"
              info="The API key can be found in the details page of your deployment in Azure AI Foundry. For more information, visit https://azure.microsoft.com/en-us/products/ai-foundry."
            />
            <InputWrapper>
              <div className="flex">
                <Input
                  id="azure-api-key"
                  type={showApiKey ? "text" : "password"}
                  value={providerDetails.details.key || ''}
                  onChange={(e) => updateProviderDetails({ key: e.target.value })}
                  placeholder="Enter your API key"
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="ml-2"
                  aria-label={showApiKey ? "Hide API Key" : "Show API Key"}
                >
                  {showApiKey ? <Icons.eyeOff className="h-4 w-4" /> : <Icons.eye className="h-4 w-4" />}
                </Button>
              </div>
            </InputWrapper>
          </div>
        </>
      )}

      <DialogFooter>
        <Button variant="outline" onClick={handleCancel} type="button">
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading && <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />}
          Save
        </Button>
      </DialogFooter>
    </form>
  )
} 