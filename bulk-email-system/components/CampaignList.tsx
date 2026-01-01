'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import CampaignForm from './CampaignForm'

interface Campaign {
  id: string
  name: string
  status: string
  dailyLimit: number
  totalSent: number
  totalReplies: number
  totalBounces: number
  createdAt: Date
  startedAt: Date | null
  template: {
    name: string
  }
  _count: {
    campaignLeads: number
  }
}

interface Template {
  id: string
  name: string
}

interface CampaignListProps {
  campaigns: Campaign[]
  templates: Template[]
  industries: string[]
  countries: string[]
}

export default function CampaignList({
  campaigns: initialCampaigns,
  templates,
  industries,
  countries,
}: CampaignListProps) {
  const router = useRouter()
  const [showForm, setShowForm] = useState(false)
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null)
  const [campaigns, setCampaigns] = useState(initialCampaigns)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const handleCreate = () => {
    setEditingCampaign(null)
    setShowForm(true)
  }

  const handleStart = async (id: string) => {
    setActionLoading(id)
    try {
      const response = await fetch(`/api/campaigns/${id}/start`, {
        method: 'POST',
      })

      if (response.ok) {
        router.refresh()
      } else {
        const data = await response.json()
        alert(data.error || 'Failed to start campaign')
      }
    } catch (error) {
      alert('Failed to start campaign')
    } finally {
      setActionLoading(null)
    }
  }

  const handlePause = async (id: string) => {
    setActionLoading(id)
    try {
      const response = await fetch(`/api/campaigns/${id}/pause`, {
        method: 'POST',
      })

      if (response.ok) {
        router.refresh()
      } else {
        const data = await response.json()
        alert(data.error || 'Failed to pause campaign')
      }
    } catch (error) {
      alert('Failed to pause campaign')
    } finally {
      setActionLoading(null)
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingCampaign(null)
    router.refresh()
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    running: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    paused: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    stopped: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  }

  return (
    <>
      <div className="mb-6">
        <button
          onClick={handleCreate}
          className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md"
        >
          + Create Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {campaigns.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              No campaigns created yet
            </p>
            <button
              onClick={handleCreate}
              className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md"
            >
              Create Your First Campaign
            </button>
          </div>
        ) : (
          campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {campaign.name}
                    </h3>
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        statusColors[campaign.status] || statusColors.draft
                      }`}
                    >
                      {campaign.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Template: {campaign.template.name}
                  </p>
                </div>
                <div className="flex gap-2">
                  {campaign.status === 'draft' && (
                    <button
                      onClick={() => handleStart(campaign.id)}
                      disabled={actionLoading === campaign.id}
                      className="px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                    >
                      {actionLoading === campaign.id ? 'Starting...' : 'Start'}
                    </button>
                  )}
                  {campaign.status === 'running' && (
                    <button
                      onClick={() => handlePause(campaign.id)}
                      disabled={actionLoading === campaign.id}
                      className="px-3 py-1 text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 rounded disabled:opacity-50"
                    >
                      {actionLoading === campaign.id ? 'Pausing...' : 'Pause'}
                    </button>
                  )}
                  {campaign.status === 'paused' && (
                    <button
                      onClick={() => handleStart(campaign.id)}
                      disabled={actionLoading === campaign.id}
                      className="px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                    >
                      {actionLoading === campaign.id ? 'Resuming...' : 'Resume'}
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Leads</div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {campaign._count.campaignLeads}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Sent</div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {campaign.totalSent}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Replies</div>
                  <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {campaign.totalReplies}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Daily Limit</div>
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {campaign.dailyLimit}
                  </div>
                </div>
              </div>

              {campaign.startedAt && (
                <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                  Started: {new Date(campaign.startedAt).toLocaleString()}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {showForm && (
        <CampaignForm
          campaign={editingCampaign}
          templates={templates}
          industries={industries}
          countries={countries}
          onClose={handleFormClose}
          onSuccess={handleFormClose}
        />
      )}
    </>
  )
}

