import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import LogsTable from '@/components/LogsTable'

export default async function LogsPage({
  searchParams,
}: {
  searchParams: { page?: string; status?: string; campaign?: string }
}) {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  const page = parseInt(searchParams.page || '1')
  const status = searchParams.status
  const campaignId = searchParams.campaign
  const itemsPerPage = 50

  const where: any = {}
  if (status) where.status = status
  if (campaignId) where.campaignId = campaignId

  const [logs, total, campaigns] = await Promise.all([
    prisma.emailLog.findMany({
      where,
      skip: (page - 1) * itemsPerPage,
      take: itemsPerPage,
      orderBy: { createdAt: 'desc' },
      include: {
        lead: {
          select: {
            company: true,
            email: true,
          },
        },
      },
    }),
    prisma.emailLog.count({ where }),
    prisma.campaign.findMany({
      select: { id: true, name: true },
    }),
  ])

  // Enrich logs with campaign names
  const logsWithCampaigns = await Promise.all(
    logs.map(async (log) => {
      let campaignName = null
      if (log.campaignId) {
        const campaign = await prisma.campaign.findUnique({
          where: { id: log.campaignId },
          select: { name: true },
        })
        campaignName = campaign?.name || null
      }
      return { ...log, campaignName }
    })
  )

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Email Logs
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            View all email sending activity ({total.toLocaleString()} total)
          </p>
        </div>
      </div>

      <LogsTable
        logs={logsWithCampaigns}
        total={total}
        page={page}
        itemsPerPage={itemsPerPage}
        status={status}
        campaignId={campaignId}
        campaigns={campaigns}
      />
    </div>
  )
}

