import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const body = await request.json()

    const updateData: any = {}
    if (body.name) updateData.name = body.name
    if (body.templateId) updateData.templateId = body.templateId
    if (body.dailyLimit) updateData.dailyLimit = parseInt(body.dailyLimit.toString())
    if (typeof body.followUpEnabled === 'boolean') updateData.followUpEnabled = body.followUpEnabled
    if (body.followUpDelayDays) updateData.followUpDelayDays = parseInt(body.followUpDelayDays.toString())
    if (body.followUpTemplateId !== undefined) updateData.followUpTemplateId = body.followUpTemplateId
    if (body.filters) updateData.filters = body.filters

    const campaign = await prisma.campaign.update({
      where: { id: params.id },
      data: updateData,
    })

    return NextResponse.json({ campaign })
  } catch (error) {
    console.error('Error updating campaign:', error)
    return NextResponse.json(
      { error: 'Failed to update campaign' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    await prisma.campaign.delete({
      where: { id: params.id },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error deleting campaign:', error)
    return NextResponse.json(
      { error: 'Failed to delete campaign' },
      { status: 500 }
    )
  }
}

