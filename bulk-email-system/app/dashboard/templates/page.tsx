import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import TemplateList from '@/components/TemplateList'

export default async function TemplatesPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  const templates = await prisma.emailTemplate.findMany({
    orderBy: { createdAt: 'desc' },
  })

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Email Templates
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Create and manage email templates for your campaigns
          </p>
        </div>
        <TemplateList templates={templates} />
      </div>
    </div>
  )
}

