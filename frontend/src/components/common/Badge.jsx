// src/components/common/Badge.jsx
import React from 'react'

export function RiskBadge({ level, size = 'md' }) {
  const norm = (level || '').toLowerCase()

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5',
  }[size] || 'text-xs px-2.5 py-1'

  if (norm.includes('high') || norm.includes('fraud') || norm.includes('fake') || norm.includes('block')) {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20 ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
        High Risk / Fraud
      </span>
    )
  }

  if (norm.includes('suspic') || norm.includes('warn') || norm.includes('medium') || norm.includes('review')) {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
        Suspicious
      </span>
    )
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${sizeClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
      Verified Safe
    </span>
  )
}

export function StatusBadge({ status }) {
  const norm = (status || '').toLowerCase()

  if (norm.includes('block') || norm.includes('flag')) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-950 text-rose-300 border border-rose-800/60">
        Blocked
      </span>
    )
  }

  if (norm.includes('review')) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-950 text-amber-300 border border-amber-800/60">
        Under Review
      </span>
    )
  }

  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950 text-emerald-300 border border-emerald-800/60">
      Verified
    </span>
  )
}
