import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import SMTPList from '@/components/SMTPList'

export default async function SMTPPage() {
  const session = await getServerSession(authOptions)

  if (!session) {
    redirect('/login')
  }

  const accounts = await prisma.sMTPAccount.findMany({
    orderBy: { createdAt: 'desc' },
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          SMTP Accounts
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your SMTP server configurations for sending emails
        </p>
      </div>

      <SMTPList accounts={accounts} />
    </div>
  )
}

