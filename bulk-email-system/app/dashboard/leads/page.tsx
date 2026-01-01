import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import LeadUpload from '@/components/LeadUpload'
import LeadsTable from '@/components/LeadsTable'

export default async function LeadsPage({
  searchParams,
}: {
  searchParams: { page?: string; status?: string; industry?: string }
}) {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  const page = parseInt(searchParams.page || '1')
  const status = searchParams.status
  const industry = searchParams.industry
  const itemsPerPage = 50

  const where: any = {}
  if (status) where.status = status
  if (industry) where.industry = industry

  const [leads, total] = await Promise.all([
    prisma.lead.findMany({
      where,
      skip: (page - 1) * itemsPerPage,
      take: itemsPerPage,
      orderBy: { createdAt: 'desc' },
    }),
    prisma.lead.count({ where }),
  ])

  const industries = await prisma.lead.findMany({
    select: { industry: true },
    distinct: ['industry'],
  })

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Leads
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage your lead database ({total.toLocaleString()} total)
          </p>
        </div>
        <LeadUpload />
      </div>

      <LeadsTable
        leads={leads}
        total={total}
        page={page}
        itemsPerPage={itemsPerPage}
        status={status}
        industry={industry}
        industries={industries.map((i) => i.industry).filter(Boolean) as string[]}
      />
    </div>
  )
}

