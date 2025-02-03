import { ModelProviderType } from "@prisma/client";

export interface ProviderDetails {
    key?: string;
    endpoint?: string;
  }
  
export interface SessionModelProvider {
    modelProvider: {
        id: string;
        name: ModelProviderType | 'default';
        userId: string;
        secretName: string;
        selected: boolean;
    };
    details: ProviderDetails;
  }
  

export async function getModelProviders(): Promise<SessionModelProvider[]> {
    const response = await fetch(`/api/providers`);
  
    if (!response.ok) {
      throw new Error('Failed to fetch model providers');
    }
  
    const data = await response.json();
    return data;
  }
  
  export async function createModelProvider(providerName: ModelProviderType, details: ProviderDetails): Promise<SessionModelProvider> {
    const response = await fetch(`/api/providers`, {
      method: 'POST',
      body: JSON.stringify({ name: providerName, details }),
    });
  
    if (!response.ok) {
      throw new Error('Failed to create model provider');
    }
  
    return response.json();
  }
  
  export async function updateModelProvider(providerId: string, details: ProviderDetails): Promise<SessionModelProvider> {
    const response = await fetch(`/api/providers`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: providerId,
        details,
      }),
    });
  
    if (!response.ok) {
      throw new Error('Failed to update model provider');
    }
  
    return response.json();
  }
  
  export async function deleteModelProvider(providerId: string): Promise<void> {
    const response = await fetch(`/api/providers`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: providerId,
      }),
    });
  
    if (!response.ok) {
      throw new Error('Failed to delete model provider');
    }
  }
  