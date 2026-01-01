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

    // Build update data
    const updateData: any = {}
    if (body.name) updateData.name = body.name
    if (body.host) updateData.host = body.host
    if (body.port) updateData.port = parseInt(body.port.toString())
    if (typeof body.secure === 'boolean') updateData.secure = body.secure
    if (body.username) updateData.username = body.username
    if (body.password) updateData.password = body.password
    if (body.fromEmail) updateData.fromEmail = body.fromEmail
    if (body.fromName !== undefined) updateData.fromName = body.fromName || null
    if (typeof body.isActive === 'boolean') updateData.isActive = body.isActive

    const account = await prisma.sMTPAccount.update({
      where: { id: params.id },
      data: updateData,
    })

    return NextResponse.json({ account: { ...account, password: undefined } })
  } catch (error) {
    console.error('Error updating SMTP account:', error)
    return NextResponse.json(
      { error: 'Failed to update SMTP account' },
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
    await prisma.sMTPAccount.delete({
      where: { id: params.id },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error deleting SMTP account:', error)
    return NextResponse.json(
      { error: 'Failed to delete SMTP account' },
      { status: 500 }
    )
  }
}

