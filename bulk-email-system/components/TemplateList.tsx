'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import TemplateForm from './TemplateForm'
import TemplateCard from './TemplateCard'

interface Template {
  id: string
  name: string
  subject: string
  body: string
  createdAt: Date
  updatedAt: Date
}

interface TemplateListProps {
  templates: Template[]
}

export default function TemplateList({ templates: initialTemplates }: TemplateListProps) {
  const router = useRouter()
  const [showForm, setShowForm] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null)
  const [templates, setTemplates] = useState(initialTemplates)

  const handleCreate = () => {
    setEditingTemplate(null)
    setShowForm(true)
  }

  const handleEdit = (template: Template) => {
    setEditingTemplate(template)
    setShowForm(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) {
      return
    }

    try {
      const response = await fetch(`/api/templates/${id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setTemplates(templates.filter((t) => t.id !== id))
        router.refresh()
      }
    } catch (error) {
      console.error('Error deleting template:', error)
      alert('Failed to delete template')
    }
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingTemplate(null)
    router.refresh()
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <TemplateCard
            key={template.id}
            template={template}
            onEdit={() => handleEdit(template)}
            onDelete={() => handleDelete(template.id)}
          />
        ))}
        
        {/* Create New Card */}
        <div
          onClick={handleCreate}
          className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
        >
          <div className="text-4xl mb-2">➕</div>
          <div className="text-lg font-medium text-gray-700 dark:text-gray-300">
            Create Template
          </div>
        </div>
      </div>

      {showForm && (
        <TemplateForm
          template={editingTemplate}
          onClose={handleFormClose}
          onSuccess={handleFormClose}
        />
      )}
    </>
  )
}

