'use client'

interface Template {
  id: string
  name: string
  subject: string
  body: string
  createdAt: Date
  updatedAt: Date
}

interface TemplateCardProps {
  template: Template
  onEdit: () => void
  onDelete: () => void
}

export default function TemplateCard({ template, onEdit, onDelete }: TemplateCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {template.name}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={onEdit}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Edit
          </button>
          <button
            onClick={onDelete}
            className="text-red-600 hover:text-red-700 text-sm font-medium"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="mb-3">
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
          Subject:
        </div>
        <div className="text-sm text-gray-900 dark:text-white font-medium">
          {template.subject}
        </div>
      </div>

      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
          Preview:
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
          {template.body.substring(0, 150)}...
        </div>
      </div>

      <div className="text-xs text-gray-500 dark:text-gray-400">
        Updated: {new Date(template.updatedAt).toLocaleDateString()}
      </div>
    </div>
  )
}

