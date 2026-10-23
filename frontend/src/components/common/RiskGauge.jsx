// src/components/common/RiskGauge.jsx
import React from 'react'
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react'

export function RiskGauge({ score = 0, size = 180, strokeWidth = 14, showIcon = true }) {
  const clamped = Math.min(Math.max(score, 0), 100)
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clamped / 100) * circumference

  let color = '#10b981' // emerald
  let glowColor = 'rgba(16, 185, 129, 0.3)'
  let label = 'Low Risk (Safe)'
  let Icon = ShieldCheck
  let textClass = 'text-emerald-400'

  if (clamped >= 70) {
    color = '#f43f5e' // rose
    glowColor = 'rgba(244, 63, 94, 0.4)'
    label = 'High Risk (Fraud)'
    Icon = ShieldAlert
    textClass = 'text-rose-400'
  } else if (clamped >= 35) {
    color = '#f59e0b' // amber
    glowColor = 'rgba(245, 158, 11, 0.35)'
    label = 'Suspicious Job'
    Icon = AlertTriangle
    textClass = 'text-amber-400'
  }

  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Glow backdrop */}
        <div
          className="absolute inset-0 rounded-full blur-xl transition-all duration-700 pointer-events-none"
          style={{ background: glowColor, opacity: 0.6 }}
        />

        <svg width={size} height={size} className="transform -rotate-90 relative z-10">
          {/* Background circle track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
          {showIcon && <Icon className={`w-6 h-6 mb-1 ${textClass}`} />}
          <div className="text-3xl font-extrabold tracking-tight text-white flex items-baseline">
            <span>{clamped}</span>
            <span className="text-sm font-semibold text-slate-400 ml-0.5">/100</span>
          </div>
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-400 mt-0.5">
            Risk Index
          </span>
        </div>
      </div>

      <div className="mt-3">
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${textClass} bg-slate-900 border border-slate-800`}>
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          {label}
        </span>
      </div>
    </div>
  )
}
