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
    const campaigns = await prisma.campaign.findMany({
      include: {
        template: {
          select: {
            name: true,
          },
        },
        _count: {
          select: {
            campaignLeads: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    })

    return NextResponse.json({ campaigns })
  } catch (error) {
    console.error('Error fetching campaigns:', error)
    return NextResponse.json(
      { error: 'Failed to fetch campaigns' },
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
    const {
      name,
      templateId,
      dailyLimit,
      followUpEnabled,
      followUpDelayDays,
      followUpTemplateId,
      filters,
    } = await request.json()

    if (!name || !templateId) {
      return NextResponse.json(
        { error: 'Name and template are required' },
        { status: 400 }
      )
    }

    // Build where clause for lead filtering
    const where: any = {}
    if (filters?.status && filters.status.length > 0) {
      where.status = { in: filters.status }
    }
    if (filters?.industries && filters.industries.length > 0) {
      where.industry = { in: filters.industries }
    }
    if (filters?.countries && filters.countries.length > 0) {
      where.country = { in: filters.countries }
    }

    // Find matching leads
    const matchingLeads = await prisma.lead.findMany({
      where,
      select: { id: true },
    })

    if (matchingLeads.length === 0) {
      return NextResponse.json(
        { error: 'No leads match the selected filters' },
        { status: 400 }
      )
    }

    // Create campaign
    const campaign = await prisma.campaign.create({
      data: {
        name,
        templateId,
        dailyLimit: parseInt(dailyLimit.toString()) || 50,
        followUpEnabled: followUpEnabled === true,
        followUpDelayDays: followUpDelayDays ? parseInt(followUpDelayDays.toString()) : 5,
        followUpTemplateId: followUpEnabled && followUpTemplateId ? followUpTemplateId : null,
        filters: filters || {},
        status: 'draft',
      },
    })

    // Create campaign leads
    await prisma.campaignLead.createMany({
      data: matchingLeads.map((lead) => ({
        campaignId: campaign.id,
        leadId: lead.id,
        status: 'pending',
      })),
    })

    // Create jobs for all leads
    await prisma.jobQueue.createMany({
      data: matchingLeads.map((lead) => ({
        campaignId: campaign.id,
        leadId: lead.id,
        type: 'send',
        status: 'pending',
        scheduledAt: new Date(),
      })),
    })

    return NextResponse.json({
      campaign,
      leadsAdded: matchingLeads.length,
    })
  } catch (error: any) {
    console.error('Error creating campaign:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to create campaign' },
      { status: 500 }
    )
  }
}

