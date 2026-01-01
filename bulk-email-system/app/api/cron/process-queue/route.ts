import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { processJobQueue, scheduleFollowUps } from '@/lib/campaign'
import { prisma } from '@/lib/prisma'

// This endpoint can be called:
// 1. Manually from dashboard (requires session/auth)
// 2. Via external cron service (requires CRON_SECRET)

export async function GET(request: Request) {
  // Check for session (manual trigger from dashboard)
  const session = await getServerSession(authOptions)
  
  // Check for CRON_SECRET (external cron service)
  const authHeader = request.headers.get('authorization')
  const cronSecret = process.env.CRON_SECRET
  
  // Allow if: user is logged in (session) OR valid CRON_SECRET provided
  if (!session) {
    if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
  }

  try {
    // Process email queue
    await processJobQueue()

    // Schedule follow-ups for all running campaigns
    const runningCampaigns = await prisma.campaign.findMany({
      where: { status: 'running', followUpEnabled: true },
    })

    for (const campaign of runningCampaigns) {
      await scheduleFollowUps(campaign.id)
    }

    return NextResponse.json({ 
      success: true, 
      message: 'Queue processed successfully',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Error processing queue:', error)
    return NextResponse.json(
      { error: 'Failed to process queue', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}
