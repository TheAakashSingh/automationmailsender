import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function GET() {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const accounts = await prisma.sMTPAccount.findMany({
      orderBy: { createdAt: 'desc' },
      select: {
        id: true,
        name: true,
        host: true,
        port: true,
        secure: true,
        username: true,
        fromEmail: true,
        fromName: true,
        isActive: true,
        lastTestedAt: true,
        testStatus: true,
        createdAt: true,
      },
    })

    return NextResponse.json({ accounts })
  } catch (error) {
    console.error('Error fetching SMTP accounts:', error)
    return NextResponse.json(
      { error: 'Failed to fetch SMTP accounts' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const { name, host, port, secure, username, password, fromEmail, fromName } =
      await request.json()

    if (!name || !host || !port || !username || !password || !fromEmail) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    const account = await prisma.sMTPAccount.create({
      data: {
        name,
        host,
        port: parseInt(port.toString()),
        secure: secure !== false,
        username,
        password, // In production, encrypt this
        fromEmail,
        fromName: fromName || null,
        isActive: false, // Require testing before activation
      },
    })

    return NextResponse.json({ account: { ...account, password: undefined } })
  } catch (error) {
    console.error('Error creating SMTP account:', error)
    return NextResponse.json(
      { error: 'Failed to create SMTP account' },
      { status: 500 }
    )
  }
}

