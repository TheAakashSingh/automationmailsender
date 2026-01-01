'use client'

import { useState, useEffect } from 'react'

interface Campaign {
  id: string
  name: string
  templateId: string
  dailyLimit: number
  followUpEnabled: boolean
  followUpDelayDays: number
  followUpTemplateId: string | null
  filters: any
}

interface Template {
  id: string
  name: string
}

interface CampaignFormProps {
  campaign?: Campaign | null
  templates: Template[]
  industries: string[]
  countries: string[]
  onClose: () => void
  onSuccess: () => void
}

export default function CampaignForm({
  campaign,
  templates,
  industries,
  countries,
  onClose,
  onSuccess,
}: CampaignFormProps) {
  const [name, setName] = useState('')
  const [templateId, setTemplateId] = useState('')
  const [dailyLimit, setDailyLimit] = useState(50)
  const [followUpEnabled, setFollowUpEnabled] = useState(false)
  const [followUpDelayDays, setFollowUpDelayDays] = useState(5)
  const [followUpTemplateId, setFollowUpTemplateId] = useState('')
  
  // Filters
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([])
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const [selectedStatus, setSelectedStatus] = useState<string[]>(['pending'])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (campaign) {
      setName(campaign.name)
      setTemplateId(campaign.templateId)
      setDailyLimit(campaign.dailyLimit)
      setFollowUpEnabled(campaign.followUpEnabled)
      setFollowUpDelayDays(campaign.followUpDelayDays)
      setFollowUpTemplateId(campaign.followUpTemplateId || '')
      
      if (campaign.filters) {
        if (campaign.filters.industries) setSelectedIndustries(campaign.filters.industries)
        if (campaign.filters.countries) setSelectedCountries(campaign.filters.countries)
        if (campaign.filters.status) setSelectedStatus(campaign.filters.status)
      }
    }
  }, [campaign])

  const toggleIndustry = (industry: string) => {
    setSelectedIndustries((prev) =>
      prev.includes(industry)
        ? prev.filter((i) => i !== industry)
        : [...prev, industry]
    )
  }

  const toggleCountry = (country: string) => {
    setSelectedCountries((prev) =>
      prev.includes(country)
        ? prev.filter((c) => c !== country)
        : [...prev, country]
    )
  }

  const toggleStatus = (status: string) => {
    setSelectedStatus((prev) =>
      prev.includes(status)
        ? prev.filter((s) => s !== status)
        : [...prev, status]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!templateId) {
      setError('Please select a template')
      return
    }

    if (followUpEnabled && !followUpTemplateId) {
      setError('Please select a follow-up template')
      return
    }

    setLoading(true)

    try {
      const filters = {
        industries: selectedIndustries.length > 0 ? selectedIndustries : undefined,
        countries: selectedCountries.length > 0 ? selectedCountries : undefined,
        status: selectedStatus,
      }

      const url = campaign ? `/api/campaigns/${campaign.id}` : '/api/campaigns'
      const method = campaign ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          templateId,
          dailyLimit: parseInt(dailyLimit.toString()),
          followUpEnabled,
          followUpDelayDays: parseInt(followUpDelayDays.toString()),
          followUpTemplateId: followUpEnabled ? followUpTemplateId : null,
          filters,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save campaign')
      }

      onSuccess()
    } catch (err: any) {
      setError(err.message || 'Failed to save campaign')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {campaign ? 'Edit Campaign' : 'Create Campaign'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Campaign Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="e.g., Insurance Companies Q1 2024"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Template *
            </label>
            <select
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              required
              className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select a template</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Daily Sending Limit *
            </label>
            <input
              type="number"
              value={dailyLimit}
              onChange={(e) => setDailyLimit(parseInt(e.target.value))}
              required
              min={1}
              max={500}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Maximum emails to send per day (recommended: 50-100 for better deliverability)
            </p>
          </div>

          {/* Filters */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Lead Filters
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Industry (Leave empty for all)
                </label>
                <div className="flex flex-wrap gap-2">
                  {industries.map((industry) => (
                    <button
                      key={industry}
                      type="button"
                      onClick={() => toggleIndustry(industry)}
                      className={`px-3 py-1 text-sm rounded-md border ${
                        selectedIndustries.includes(industry)
                          ? 'bg-primary-100 text-primary-700 border-primary-300 dark:bg-primary-900 dark:text-primary-300 dark:border-primary-700'
                          : 'bg-white text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
                      }`}
                    >
                      {industry}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Country (Leave empty for all)
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {countries.map((country) => (
                    <button
                      key={country}
                      type="button"
                      onClick={() => toggleCountry(country)}
                      className={`px-3 py-1 text-sm rounded-md border ${
                        selectedCountries.includes(country)
                          ? 'bg-primary-100 text-primary-700 border-primary-300 dark:bg-primary-900 dark:text-primary-300 dark:border-primary-700'
                          : 'bg-white text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
                      }`}
                    >
                      {country}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <div className="flex flex-wrap gap-2">
                  {['pending', 'sent', 'replied', 'bounced'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => toggleStatus(status)}
                      className={`px-3 py-1 text-sm rounded-md border ${
                        selectedStatus.includes(status)
                          ? 'bg-primary-100 text-primary-700 border-primary-300 dark:bg-primary-900 dark:text-primary-300 dark:border-primary-700'
                          : 'bg-white text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
                      }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Follow-up Settings */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id="followUpEnabled"
                checked={followUpEnabled}
                onChange={(e) => setFollowUpEnabled(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="followUpEnabled" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Enable Follow-up Emails
              </label>
            </div>

            {followUpEnabled && (
              <div className="ml-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Follow-up Template *
                  </label>
                  <select
                    value={followUpTemplateId}
                    onChange={(e) => setFollowUpTemplateId(e.target.value)}
                    required={followUpEnabled}
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Select follow-up template</option>
                    {templates.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Follow-up Delay (Days) *
                  </label>
                  <input
                    type="number"
                    value={followUpDelayDays}
                    onChange={(e) => setFollowUpDelayDays(parseInt(e.target.value))}
                    required={followUpEnabled}
                    min={1}
                    max={30}
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Send follow-up email after this many days (if no reply)
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : campaign ? 'Update Campaign' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

