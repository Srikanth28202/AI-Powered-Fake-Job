// src/components/common/Skeleton.jsx
import React from 'react'

export function Skeleton({ className = '' }) {
  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-slate-800/80 via-slate-700/50 to-slate-800/80 rounded-lg ${className}`}
    />
  )
}

export function TableRowSkeleton({ cols = 5 }) {
  return (
    <tr className="border-b border-slate-800/60 animate-pulse">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="py-4 px-4">
          <div className="h-4 bg-slate-800 rounded w-full max-w-[120px]" />
        </td>
      ))}
    </tr>
  )
}
