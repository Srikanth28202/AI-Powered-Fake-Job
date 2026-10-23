// src/components/common/EmptyState.jsx
import React from 'react'
import { FolderSearch } from 'lucide-react'
import { Button } from './Button'

export function EmptyState({
  icon: Icon = FolderSearch,
  title = 'No records found',
  description = 'Try adjusting your search filters or scan a new job posting to populate this list.',
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-12 rounded-2xl border border-dashed border-slate-800/80 bg-slate-900/30 backdrop-blur ${className}`}>
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4 shadow-lg shadow-indigo-500/10">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-semibold text-slate-100 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-md mb-6">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" size="md" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
