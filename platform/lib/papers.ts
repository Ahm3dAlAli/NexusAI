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

export async function createPaper(data: { title: string; authors: string; summary: string; url: string }): Promise<Paper> {
  const response = await fetch('/api/papers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create paper');
  }
  return response.json();
} 