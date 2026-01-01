import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function GET(request: Request) {
  const session = await getServerSession(authOptions)

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(request.url)
  const type = searchParams.get('type') || 'sent' // sent | replied | bounced

  try {
    let leads
    let filename

    switch (type) {
      case 'sent':
        leads = await prisma.lead.findMany({
          where: { status: 'sent' },
          orderBy: { emailSentAt: 'desc' },
        })
        filename = 'sent_leads.csv'
        break
      case 'replied':
        leads = await prisma.lead.findMany({
          where: { status: 'replied' },
          orderBy: { replyDetectedAt: 'desc' },
        })
        filename = 'replied_leads.csv'
        break
      case 'bounced':
        leads = await prisma.lead.findMany({
          where: { status: 'bounced' },
          orderBy: { updatedAt: 'desc' },
        })
        filename = 'bounced_leads.csv'
        break
      default:
        return NextResponse.json({ error: 'Invalid export type' }, { status: 400 })
    }

    // Convert to CSV
    const headers = ['Company', 'Email', 'Phone', 'Website', 'City', 'Country', 'Industry', 'Status', 'Email Sent At']
    const rows = leads.map((lead) => [
      lead.company,
      lead.email,
      lead.phone || '',
      lead.website || '',
      lead.city || '',
      lead.country || '',
      lead.industry || '',
      lead.status,
      lead.emailSentAt ? new Date(lead.emailSentAt).toISOString() : '',
    ])

    const csv = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')),
    ].join('\n')

    return new NextResponse(csv, {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    })
  } catch (error) {
    console.error('Error exporting leads:', error)
    return NextResponse.json(
      { error: 'Failed to export leads' },
      { status: 500 }
    )
  }
}

