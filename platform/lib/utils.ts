import { ModelProviderType } from "@prisma/client"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string): string {
  const d = new Date(date)
  const now = new Date()
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  
  const isToday = d.toDateString() === now.toDateString()
  const isYesterday = d.toDateString() === yesterday.toDateString()
  
  if (isToday) return 'Today'
  if (isYesterday) return 'Yesterday'
  
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function providerEnumToName(provider: ModelProviderType): string {
  if (provider === ModelProviderType.openai) {
    return 'OpenAI'
  }
  if (provider === ModelProviderType.azureOpenai) {
    return 'Azure OpenAI'
  }
  return provider
}

export function providerNameToEnum(provider: string): ModelProviderType {
  if (provider === 'OpenAI') {
    return ModelProviderType.openai
  }
  return ModelProviderType.azureOpenai
}