import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { getActiveSMTPAccount } from '@/lib/email'

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    // Check if SMTP account is configured
    try {
      await getActiveSMTPAccount()
    } catch (error) {
      return NextResponse.json(
        { error: 'No active SMTP account found. Please configure SMTP first.' },
        { status: 400 }
      )
    }

    const campaign = await prisma.campaign.findUnique({
      where: { id: params.id },
      include: {
        campaignLeads: {
          where: { status: 'pending' },
        },
      },
    })

    if (!campaign) {
      return NextResponse.json({ error: 'Campaign not found' }, { status: 404 })
    }

    if (campaign.status === 'running') {
      return NextResponse.json({ error: 'Campaign is already running' }, { status: 400 })
    }

    // Update campaign status
    await prisma.campaign.update({
      where: { id: params.id },
      data: {
        status: 'running',
        startedAt: new Date(),
        pausedAt: null,
      },
    })

    return NextResponse.json({
      success: true,
      message: 'Campaign started successfully',
      pendingLeads: campaign.campaignLeads.length,
    })
  } catch (error: any) {
    console.error('Error starting campaign:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to start campaign' },
      { status: 500 }
    )
  }
}

