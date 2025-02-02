export interface User {
  id: string
  name: string | null
  email: string
  collectPapers: boolean
  customInstructions: string[]
  password: string | null
  modelProviders: {
    id: string;
    name: string;
    selected: boolean;
  }[]
}

export interface UpdateUserPayload {
  name?: string
  collectPapers?: boolean
  customInstructions?: string[]
  selectedProviderId?: string | null
}

export async function fetchUser(): Promise<User> {
  const response = await fetch('/api/users/me', {
    method: 'GET'
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user data')
  }

  return response.json()
}

export async function updateUser(payload: UpdateUserPayload): Promise<User> {
  const response = await fetch('/api/users/me', {
    method: 'PUT',
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error('Failed to update user')
  }

  return response.json()
}
