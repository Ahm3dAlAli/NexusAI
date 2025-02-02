import { NextResponse } from 'next/server';
import { getServerSession } from "next-auth/next";
import { authOptions } from '@/app/api/auth/[...nextauth]/auth';
import { prisma } from '@/lib/prisma';
import { storeSecret, deleteSecret, getSecret } from '@/lib/secrets';
import { ModelProviderType } from '@prisma/client';
import { v4 as uuidv4 } from 'uuid';

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const providers = await prisma.modelProvider.findMany({
      where: { userId: session.user.id },
      select: {
        id: true,
        name: true,
        userId: true,
        secretName: true,
      }
    });

    // Fetch all secrets in parallel and format as SessionModelProvider
    const providersWithDetails = await Promise.all(
      providers.map(async (modelProvider) => {
        const details = await getSecret(modelProvider.secretName);
        return { modelProvider, details };
      })
    );

    return NextResponse.json(providersWithDetails, { status: 200 });
  } catch (error) {
    console.error('Error fetching providers:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

export async function POST(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { name, details } = await req.json();

  if (!name) {
    return NextResponse.json({ error: 'Provider name is required' }, { status: 400 });
  }

  const secretName = `provider-${name}-${uuidv4()}`;
  const secretValue = JSON.stringify(details);

  try {
    await storeSecret(secretName, secretValue);

    const modelProvider = await prisma.modelProvider.create({
      data: {
        name: name as ModelProviderType,
        userId: session.user.id,
        secretName,
      },
      select: {
        id: true,
        name: true,
        userId: true,
        secretName: true,
      }
    });

    // Return in SessionModelProvider format
    return NextResponse.json({
      modelProvider,
      details
    }, { status: 201 });
  } catch (error) {
    console.error('Error adding provider:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { id, details } = await req.json();

  if (!id) {
    return NextResponse.json({ error: 'Provider ID is required' }, { status: 400 });
  }

  try {
    const provider = await prisma.modelProvider.findUnique({
      where: { id },
    });

    if (!provider || provider.userId !== session.user.id) {
      return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    // Generate new secret name with UUID
    const secretName = `provider-${provider.name}-${uuidv4()}`;
    const secretValue = JSON.stringify(details);

    // Store new secret first
    await storeSecret(secretName, secretValue);

    // Return in SessionModelProvider format
    return NextResponse.json({
      modelProvider: provider,
      details
    }, { status: 200 });
  } catch (error) {
    console.error('Error updating provider:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

export async function DELETE(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { id } = await req.json();

  if (!id) {
    return NextResponse.json({ error: 'Provider ID is required' }, { status: 400 });
  }

  try {
    const provider = await prisma.modelProvider.findUnique({
      where: { id },
    });

    if (!provider || provider.userId !== session.user.id) {
      return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    // Delete secret from Key Vault
    await deleteSecret(provider.secretName);

    // Remove provider from the database
    await prisma.modelProvider.delete({
      where: { id },
    });

    return NextResponse.json({ message: 'Provider deleted successfully' }, { status: 200 });
  } catch (error) {
    console.error('Error deleting provider:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}