import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const campaign = await prisma.campaign.findUnique({
      where: { id: params.id },
    })

    if (!campaign) {
      return NextResponse.json({ error: 'Campaign not found' }, { status: 404 })
    }

    if (campaign.status !== 'running') {
      return NextResponse.json(
        { error: 'Campaign is not running' },
        { status: 400 }
      )
    }

    await prisma.campaign.update({
      where: { id: params.id },
      data: {
        status: 'paused',
        pausedAt: new Date(),
      },
    })

    return NextResponse.json({
      success: true,
      message: 'Campaign paused successfully',
    })
  } catch (error) {
    console.error('Error pausing campaign:', error)
    return NextResponse.json(
      { error: 'Failed to pause campaign' },
      { status: 500 }
    )
  }
}

