'use client'

interface StatsProps {
  totalLeads: number
  emailsSentToday: number
  emailsPending: number
  campaignsRunning: number
  totalReplies: number
  totalBounces: number
  totalUnsubscribed: number
}

export default function DashboardStats({
  totalLeads,
  emailsSentToday,
  emailsPending,
  campaignsRunning,
  totalReplies,
  totalBounces,
  totalUnsubscribed,
}: StatsProps) {
  const stats = [
    {
      name: 'Total Leads',
      value: totalLeads.toLocaleString(),
      icon: '👥',
      color: 'bg-blue-500',
    },
    {
      name: 'Emails Sent Today',
      value: emailsSentToday.toLocaleString(),
      icon: '📧',
      color: 'bg-green-500',
    },
    {
      name: 'Pending Emails',
      value: emailsPending.toLocaleString(),
      icon: '⏳',
      color: 'bg-yellow-500',
    },
    {
      name: 'Running Campaigns',
      value: campaignsRunning.toLocaleString(),
      icon: '🚀',
      color: 'bg-purple-500',
    },
    {
      name: 'Replies',
      value: totalReplies.toLocaleString(),
      icon: '💬',
      color: 'bg-indigo-500',
    },
    {
      name: 'Bounces',
      value: totalBounces.toLocaleString(),
      icon: '⚠️',
      color: 'bg-red-500',
    },
    {
      name: 'Unsubscribed',
      value: totalUnsubscribed.toLocaleString(),
      icon: '🚫',
      color: 'bg-gray-500',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <div
          key={stat.name}
          className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center">
            <div className={`${stat.color} p-3 rounded-lg text-2xl`}>
              {stat.icon}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {stat.name}
              </p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stat.value}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

