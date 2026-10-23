// src/components/common/Card.jsx
import React from 'react'

export function Card({
  children,
  className = '',
  title,
  subtitle,
  action,
  hover = false,
  glow = false,
  noPadding = false,
  ...props
}) {
  return (
    <div
      className={`rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl overflow-hidden ${
        hover ? 'transition-all duration-200 hover:border-slate-700 hover:bg-slate-900/80 hover:shadow-2xl hover:shadow-indigo-500/5' : ''
      } ${glow ? 'border-indigo-500/30 shadow-indigo-500/10' : ''} ${className}`}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between gap-4">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-100">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-6'}>{children}</div>
    </div>
  )
}
