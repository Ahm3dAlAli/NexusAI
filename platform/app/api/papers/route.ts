import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]/auth';
import { config } from '@/config/environment'
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

  try {
    // Find any existing papers with the same URLs for this user
    const existingPapers = await prisma.paper.findMany({
      where: {
        userId: session.user.id,
        url: { in: urls },
      },
    });
    // Filter out URLs that already exist and duplicates
    const existingUrls = existingPapers.map(paper => paper.url);
    const newUrls = Array.from(new Set(urls)).filter(url => !existingUrls.includes(url));

    // Only create papers for new URLs
    const token = generateWebSocketToken({ userId: session.user.id, email: session.user.email })
    const payload = { urls: newUrls } satisfies PapersRequest;
    
    const response = await fetch(
      `${config.apiUrl}/papers?token=${token}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }
    );

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
    const createdPapers = await Promise.all(newPaperPromises);

    return NextResponse.json(createdPapers, { status: 201 });
  } catch (error) {
    console.error('Error creating papers:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 