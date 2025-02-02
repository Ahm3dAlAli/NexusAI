import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]/auth';
import { publicConfig } from '@/config/environment'
import { PapersRequest, PaperOutput } from '@/types/BackendModels';
import { generateWebSocketToken } from '@/lib/jwt'

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const papers = await prisma.paper.findMany({
    where: { userId: session.user.id },
    orderBy: { updatedAt: 'desc' },
  });

  return NextResponse.json(papers, { status: 200 });
}

export async function POST(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { urls } = await req.json();

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json({ error: 'URLs array is required' }, { status: 400 });
  }

  if (urls.length > 8) {
    return NextResponse.json({ error: 'Maximum 8 papers can be processed at once' }, { status: 400 });
  }

  try {
    // Filter for unique URLs first
    const uniqueUrls = Array.from(new Set(urls));
    
    // Find any existing papers with the same URLs for this user
    const existingPapers = await prisma.paper.findMany({
      where: {
        userId: session.user.id,
        url: { in: uniqueUrls },
      }
    });
    
    // Filter out URLs that already exist
    const existingUrls = existingPapers.map(paper => paper.url);
    const newUrls = uniqueUrls.filter(url => !existingUrls.includes(url));

    // Only create papers for new URLs
    const token = generateWebSocketToken({ userId: session.user.id, email: session.user.email })
    const payload = { urls: newUrls } satisfies PapersRequest;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 300 seconds

    const response = await fetch(
      `${publicConfig.apiUrl}/papers?token=${token}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Response error:', errorText);
      throw new Error(errorText);
    }

    const papers: PaperOutput[] = await response.json();
    const newPaperPromises = papers.map(paper => 
      prisma.paper.create({
        data: {
          ...paper,
          userId: session.user.id,
        }
      })
    );
    const newPapers = await Promise.all(newPaperPromises);

    // Check if all paper downloads failed
    if (newPapers.length === 0 && newUrls.length > 0) {
      throw new Error('Failed to download papers');
    }

    return NextResponse.json(
      {
        newPapersCount: newPapers.length,
        failedPapersCount: newUrls.length - newPapers.length
      }, 
      { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json({ error: 'Request timeout' }, { status: 504 });
    }
    console.error('Error creating papers:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 