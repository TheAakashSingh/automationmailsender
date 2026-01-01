import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { isUnsubscribeReply } from '@/lib/email'

// This endpoint should be called when you receive email replies
// In production, you'd set up email forwarding or use a service like SendGrid Inbound Parse
// For now, this is a manual endpoint to process replies

export async function POST(request: Request) {
  try {
    const { from, to, subject, text } = await request.json()

    if (!from || !text) {
      return NextResponse.json(
        { error: 'from and text are required' },
        { status: 400 }
      )
    }

    // Find lead by email
    const lead = await prisma.lead.findFirst({
      where: { email: from.toLowerCase() },
    })

    if (!lead) {
      return NextResponse.json({ message: 'Lead not found' }, { status: 200 })
    }

    // Check if it's an unsubscribe request
    if (isUnsubscribeReply(text)) {
      // Mark as unsubscribed
      await prisma.lead.update({
        where: { id: lead.id },
        data: {
          status: 'unsubscribed',
        },
      })

      // Add to unsubscribe list
      await prisma.unsubscribe.upsert({
        where: { email: from.toLowerCase() },
        create: {
          email: from.toLowerCase(),
          reason: 'Reply with unsubscribe keyword',
          source: 'reply',
        },
        update: {},
      })

      return NextResponse.json({
        message: 'Lead unsubscribed',
        action: 'unsubscribed',
      })
    }

    // Mark as replied
    await prisma.lead.update({
      where: { id: lead.id },
      data: {
        status: 'replied',
        replyDetectedAt: new Date(),
      },
    })

    // Update campaign stats if lead is in a campaign
    const campaignLeads = await prisma.campaignLead.findMany({
      where: { leadId: lead.id },
      include: { campaign: true },
    })

    for (const campaignLead of campaignLeads) {
      if (campaignLead.campaign) {
        await prisma.campaign.update({
          where: { id: campaignLead.campaign.id },
          data: {
            totalReplies: { increment: 1 },
          },
        })
      }
    }

    // Update email log if exists
    const emailLog = await prisma.emailLog.findFirst({
      where: {
        leadId: lead.id,
        toEmail: from.toLowerCase(),
      },
      orderBy: { createdAt: 'desc' },
    })

    if (emailLog) {
      await prisma.emailLog.update({
        where: { id: emailLog.id },
        data: {
          replyDetected: true,
        },
      })
    }

    return NextResponse.json({
      message: 'Reply processed',
      action: 'replied',
    })
  } catch (error) {
    console.error('Error processing reply:', error)
    return NextResponse.json(
      { error: 'Failed to process reply' },
      { status: 500 }
    )
  }
}

