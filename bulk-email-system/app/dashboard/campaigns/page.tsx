import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import CampaignList from '@/components/CampaignList'

export default async function CampaignsPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  const [campaigns, templates] = await Promise.all([
    prisma.campaign.findMany({
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
    }),
    prisma.emailTemplate.findMany({
      select: { id: true, name: true },
    }),
  ])

  const industries = await prisma.lead.findMany({
    select: { industry: true },
    distinct: ['industry'],
  })

  const countries = await prisma.lead.findMany({
    select: { country: true },
    distinct: ['country'],
  })

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Campaigns
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Create and manage your email campaigns
          </p>
        </div>
      </div>

      <CampaignList
        campaigns={campaigns}
        templates={templates}
        industries={industries.map((i) => i.industry).filter(Boolean) as string[]}
        countries={countries.map((c) => c.country).filter(Boolean) as string[]}
      />
    </div>
  )
}

