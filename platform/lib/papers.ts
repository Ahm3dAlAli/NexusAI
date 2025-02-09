import { Paper } from '@prisma/client';

export async function fetchPapers(): Promise<Paper[]> {
  const response = await fetch('/api/papers');
  if (!response.ok) {
    throw new Error('Failed to fetch papers');
  }
  return response.json();
}

export async function fetchPaper(id: string): Promise<Paper> {
  const response = await fetch(`/api/papers/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch paper');
  }
  return response.json();
}

export async function createPapers(urls: string[]): Promise<{ newPapersCount: number, expectedPapersCount: number }> {
  const response = await fetch('/api/papers', {
    method: 'POST',
    body: JSON.stringify({ urls })
  });
  
  if (!response.ok) {
    throw new Error('Failed to create papers');
  }
  
  return response.json();
} 