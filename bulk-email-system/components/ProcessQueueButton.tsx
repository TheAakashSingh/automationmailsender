'use client'

import { useState } from 'react'

export default function ProcessQueueButton() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleProcessQueue = async () => {
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await fetch('/api/cron/process-queue', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_CRON_SECRET || 'manual-trigger'}`,
        },
      })

      const data = await response.json()

      if (response.ok) {
        setMessage(data.message || 'Queue processed successfully!')
        // Refresh page after 2 seconds to update stats
        setTimeout(() => {
          window.location.reload()
        }, 2000)
      } else {
        setError(data.error || 'Failed to process queue')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process queue')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Email Queue Processing
      </h3>
      
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Click the button below to process pending emails in the queue. This will send emails one by one with proper delays.
      </p>

      <button
        onClick={handleProcessQueue}
        disabled={loading}
        className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <span className="animate-spin">⏳</span>
            Processing Queue...
          </>
        ) : (
          <>
            <span>📧</span>
            Process Email Queue Now
          </>
        )}
      </button>

      {message && (
        <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 px-4 py-3 rounded">
          {message}
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        💡 Tip: Process the queue regularly (every 1-2 minutes) for best results. You can also set up an external cron service if needed.
      </p>
    </div>
  )
}

