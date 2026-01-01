import { NextResponse } from 'next/server'
import { processJobQueue, scheduleFollowUps } from '@/lib/campaign'
import { prisma } from '@/lib/prisma'

// This endpoint should be called by a cron job or scheduled task
// For production, use a cron service or set up a worker process

export async function GET(request: Request) {
  // Simple auth check (use better auth in production)
  const authHeader = request.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
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

    return NextResponse.json({ success: true, message: 'Queue processed' })
  } catch (error) {
    console.error('Error processing queue:', error)
    return NextResponse.json(
      { error: 'Failed to process queue' },
      { status: 500 }
    )
  }
}

