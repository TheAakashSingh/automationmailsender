'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import SMTPForm from './SMTPForm'

interface SMTPAccount {
  id: string
  name: string
  host: string
  port: number
  secure: boolean
  username: string
  fromEmail: string
  fromName: string | null
  isActive: boolean
  lastTestedAt: Date | null
  testStatus: string | null
  createdAt: Date
}

interface SMTPListProps {
  accounts: SMTPAccount[]
}

export default function SMTPList({ accounts: initialAccounts }: SMTPListProps) {
  const router = useRouter()
  const [showForm, setShowForm] = useState(false)
  const [editingAccount, setEditingAccount] = useState<SMTPAccount | null>(null)
  const [accounts, setAccounts] = useState(initialAccounts)
  const [testing, setTesting] = useState<string | null>(null)

  const handleCreate = () => {
    setEditingAccount(null)
    setShowForm(true)
  }

  const handleEdit = (account: SMTPAccount) => {
    setEditingAccount(account)
    setShowForm(true)
  }

  const handleTest = async (id: string) => {
    setTesting(id)
    try {
      const response = await fetch(`/api/smtp/${id}/test`, {
        method: 'POST',
      })

      const data = await response.json()

      if (response.ok) {
        alert('SMTP test successful!')
        router.refresh()
      } else {
        alert(`SMTP test failed: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      alert('Failed to test SMTP connection')
    } finally {
      setTesting(null)
    }
  }

  const handleToggleActive = async (id: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/smtp/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isActive: !currentStatus }),
      })

      if (response.ok) {
        router.refresh()
      }
    } catch (error) {
      alert('Failed to update SMTP account')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this SMTP account?')) {
      return
    }

    try {
      const response = await fetch(`/api/smtp/${id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setAccounts(accounts.filter((a) => a.id !== id))
        router.refresh()
      }
    } catch (error) {
      alert('Failed to delete SMTP account')
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingAccount(null)
    router.refresh()
  }

  return (
    <>
      <div className="mb-6">
        <button
          onClick={handleCreate}
          className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md"
        >
          + Add SMTP Account
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {accounts.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              No SMTP accounts configured
            </p>
            <button
              onClick={handleCreate}
              className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md"
            >
              Add Your First SMTP Account
            </button>
          </div>
        ) : (
          accounts.map((account) => (
            <div
              key={account.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {account.name}
                    </h3>
                    {account.isActive && (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        Active
                      </span>
                    )}
                    {account.testStatus === 'success' && (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        Tested ✓
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {account.host}:{account.port} ({account.secure ? 'TLS/SSL' : 'None'})
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTest(account.id)}
                    disabled={testing === account.id}
                    className="px-3 py-1 text-sm font-medium text-primary-600 hover:text-primary-700 border border-primary-600 rounded disabled:opacity-50"
                  >
                    {testing === account.id ? 'Testing...' : 'Test'}
                  </button>
                  <button
                    onClick={() => handleEdit(account)}
                    className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleToggleActive(account.id, account.isActive)}
                    className={`px-3 py-1 text-sm font-medium rounded ${
                      account.isActive
                        ? 'text-yellow-700 hover:text-yellow-800 border border-yellow-600'
                        : 'text-green-700 hover:text-green-800 border border-green-600'
                    }`}
                  >
                    {account.isActive ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(account.id)}
                    className="px-3 py-1 text-sm font-medium text-red-600 hover:text-red-700 border border-red-600 rounded"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">From Email:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{account.fromEmail}</span>
                </div>
                {account.fromName && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">From Name:</span>
                    <span className="ml-2 text-gray-900 dark:text-white">{account.fromName}</span>
                  </div>
                )}
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Username:</span>
                  <span className="ml-2 text-gray-900 dark:text-white">{account.username}</span>
                </div>
                {account.lastTestedAt && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Last Tested:</span>
                    <span className="ml-2 text-gray-900 dark:text-white">
                      {new Date(account.lastTestedAt).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {showForm && (
        <SMTPForm
          account={editingAccount}
          onClose={handleFormClose}
          onSuccess={handleFormClose}
        />
      )}
    </>
  )
}

