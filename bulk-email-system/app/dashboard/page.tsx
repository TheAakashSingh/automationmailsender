import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import DashboardStats from '@/components/DashboardStats'
import RecentActivity from '@/components/RecentActivity'

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    redirect('/login')
  }

  // Fetch stats
  const [
    totalLeads,
    emailsSentToday,
    emailsPending,
    campaignsRunning,
    totalReplies,
    totalBounces,
    totalUnsubscribed,
  ] = await Promise.all([
    prisma.lead.count(),
    prisma.emailLog.count({
      where: {
        status: 'sent',
        createdAt: {
          gte: new Date(new Date().setHours(0, 0, 0, 0)),
        },
      },
    }),
    prisma.jobQueue.count({
      where: { status: 'pending' },
    }),
    prisma.campaign.count({
      where: { status: 'running' },
    }),
    prisma.lead.count({
      where: { status: 'replied' },
    }),
    prisma.lead.count({
      where: { status: 'bounced' },
    }),
    prisma.unsubscribe.count(),
  ])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Overview of your email automation system
        </p>
      </div>

      <DashboardStats
        totalLeads={totalLeads}
        emailsSentToday={emailsSentToday}
        emailsPending={emailsPending}
        campaignsRunning={campaignsRunning}
        totalReplies={totalReplies}
        totalBounces={totalBounces}
        totalUnsubscribed={totalUnsubscribed}
      />

      <div className="mt-8">
        <RecentActivity />
      </div>
    </div>
  )
}

