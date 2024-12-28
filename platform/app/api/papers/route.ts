import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]/auth';

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

  const { title, authors, summary, url } = await req.json();

  if (!title || !authors || !summary || !url) {
    return NextResponse.json({ error: 'All fields are required' }, { status: 400 });
  }

  try {
    const paper = await prisma.paper.create({
      data: {
        title,
        authors,
        summary,
        url,
        userId: session.user.id,
      },
    });
    return NextResponse.json(paper, { status: 201 });
  } catch (error) {
    console.error('Error creating paper:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 