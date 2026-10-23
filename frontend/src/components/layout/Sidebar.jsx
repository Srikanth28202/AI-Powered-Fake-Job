// src/components/layout/Sidebar.jsx
import React from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import {
  ShieldCheck,
  LayoutDashboard,
  SearchCheck,
  History,
  BarChart3,
  User,
  LogOut,
  Zap,
  Sparkles,
  X,
  Cpu,
  UserCog,
} from 'lucide-react'
import useAuthStore from '../../store/authStore'
import { MOCK_KPIS } from '../../services/mockData'

const navigationItems = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Analyse Job', to: '/analyse', icon: SearchCheck, badge: 'AI Scan' },
  { label: 'Analysis History', to: '/history', icon: History },
  { label: 'Risk Analytics', to: '/analytics', icon: BarChart3 },
]





export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const scansPercentage = user ? Math.round((user.scansUsed / user.scansLimit) * 100) : 50

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-950/95 border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo and Brand */}
        <div className="h-16 px-5 border-b border-slate-800/80 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-slate-100 tracking-tight text-base flex items-center gap-1.5">
                RiskShield <span className="text-xs px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-400 font-mono">AI</span>
              </span>
              <p className="text-[10px] text-slate-400 font-medium">Job Threat Intelligence</p>
            </div>
          </Link>

          {/* Mobile close button */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
            Platform Menu
          </div>

          {navigationItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600/20 to-purple-600/10 text-white border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 transition-colors group-hover:text-indigo-400" />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            )
          })}



          {/* AI Engine Status Card */}
          <div className="pt-6 px-1">
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 relative overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  <span>ML Engine v1.4</span>
                </div>
                <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Online
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mb-2">
                Ensemble NLP: Scikit-learn + TF-IDF with 97.4% test accuracy.
              </p>
              <div className="flex items-center justify-between text-[10px] text-slate-400 border-t border-slate-800/80 pt-2 font-mono">
                <span>Lat: {MOCK_KPIS.avgInferenceTimeMs}ms</span>
                <span>F1: 96.5%</span>
              </div>
            </div>
          </div>

          {/* Quota Usage Bar */}
          <div className="px-1 pt-2">
            <div className="p-3 rounded-xl bg-gradient-to-br from-slate-900/90 to-indigo-950/20 border border-slate-800/80">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-slate-300 font-medium flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-amber-400" /> Monthly Scans
                </span>
                <span className="text-slate-400 font-mono text-[11px]">
                  {user?.scansUsed || 74} / {user?.scansLimit || 150}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${scansPercentage}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-400 mt-1.5">
                {scansPercentage}% quota utilized this cycle.
              </p>
            </div>
          </div>
        </div>

        {/* System Version Badge */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950">
          <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
            <span className="font-medium text-slate-300">Status</span>
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Operational
            </span>
          </div>
        </div>
      </aside>
    </>
  )
}


