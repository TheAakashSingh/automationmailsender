import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { createTransporter } from '@/lib/email'

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const account = await prisma.sMTPAccount.findUnique({
      where: { id: params.id },
    })

    if (!account) {
      return NextResponse.json({ error: 'SMTP account not found' }, { status: 404 })
    }

    // Create transporter and test
    const transporter = await createTransporter({
      host: account.host,
      port: account.port,
      secure: account.secure,
      auth: {
        user: account.username,
        password: account.password,
      },
      fromEmail: account.fromEmail,
      fromName: account.fromName || undefined,
    })

    // Send test email to the from email address
    await transporter.verify()

    // Update test status
    await prisma.sMTPAccount.update({
      where: { id: params.id },
      data: {
        lastTestedAt: new Date(),
        testStatus: 'success',
      },
    })

    return NextResponse.json({ success: true, message: 'SMTP connection successful' })
  } catch (error: any) {
    console.error('SMTP test failed:', error)

    // Update test status
    await prisma.sMTPAccount.update({
      where: { id: params.id },
      data: {
        lastTestedAt: new Date(),
        testStatus: 'failed',
      },
    })

    return NextResponse.json(
      { error: error.message || 'SMTP connection failed' },
      { status: 400 }
    )
  }
}

