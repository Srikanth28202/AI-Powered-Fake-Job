// src/components/layout/Header.jsx
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Menu,
  Search,
  Bell,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  User,
  LogOut,
  ExternalLink,
} from 'lucide-react'
import useAuthStore from '../../store/authStore'
import { Button } from '../common/Button'

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/history?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  const notifications = [
    {
      id: 1,
      title: 'High Risk Campaign Detected',
      desc: 'Multiple fake Data Entry postings originating from apex-logistics-freecareers.com flagged.',
      time: '12m ago',
      icon: ShieldAlert,
      color: 'text-rose-400 bg-rose-500/10',
    },
    {
      id: 2,
      title: 'Model Retraining Checkpoint',
      desc: 'TF-IDF Classifier weights successfully re-evaluated with 97.4% test F1.',
      time: '2h ago',
      icon: CheckCircle2,
      color: 'text-emerald-400 bg-emerald-500/10',
    },
    {
      id: 3,
      title: 'Telegram Phishing Pattern Spike',
      desc: '34% increase in crypto wire forwarder postings across major boards.',
      time: '5h ago',
      icon: AlertTriangle,
      color: 'text-amber-400 bg-amber-500/10',
    },
  ]

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-4 sm:px-6 flex items-center justify-between">
      {/* Left: Mobile hamburger & Search bar */}
      <div className="flex items-center gap-3 flex-1 max-w-lg">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full hidden sm:block">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search analyzed jobs, companies, or keywords..."
            className="w-full bg-slate-900/90 text-sm text-slate-200 placeholder-slate-500 rounded-xl pl-10 pr-12 py-2 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono font-semibold text-slate-500 bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700">
            ↵
          </kbd>
        </form>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-3">
        {/* ML Status Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-300 font-medium">Model v1.4 Active</span>
        </div>

        {/* Quick Analyse Button */}
        <Link to="/analyse">
          <Button variant="primary" size="sm" icon={Sparkles}>
            <span className="hidden sm:inline">Analyse Job</span>
            <span className="sm:hidden">Scan</span>
          </Button>
        </Link>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications)
              setShowUserMenu(false)
            }}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 relative transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500 ring-2 ring-slate-950" />
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl z-50 p-4 animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-sm font-bold text-slate-100">Security & Risk Feed</span>
                <span className="text-[11px] font-medium text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full">
                  3 New
                </span>
              </div>

              <div className="divide-y divide-slate-800/60 my-2 max-h-72 overflow-y-auto">
                {notifications.map((n) => {
                  const Icon = n.icon
                  return (
                    <div key={n.id} className="py-2.5 flex items-start gap-3 hover:bg-slate-800/40 p-2 rounded-xl transition-colors">
                      <div className={`p-2 rounded-xl shrink-0 ${n.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="text-xs">
                        <div className="font-semibold text-slate-200">{n.title}</div>
                        <div className="text-slate-400 mt-0.5 leading-relaxed">{n.desc}</div>
                        <span className="text-[10px] text-slate-500 mt-1 block">{n.time}</span>
                      </div>
                    </div>
                  )
                })}
              </div>

              <Link
                to="/analytics"
                onClick={() => setShowNotifications(false)}
                className="block text-center text-xs font-semibold text-indigo-400 hover:text-indigo-300 pt-2 border-t border-slate-800"
              >
                View Full Threat Analytics →
              </Link>
            </div>
          )}
        </div>

        {/* User Avatar & Menu */}
        <div className="relative">
          <button
            onClick={() => {
              setShowUserMenu(!showUserMenu)
              setShowNotifications(false)
            }}
            className="flex items-center gap-2 p-1 rounded-xl hover:bg-slate-800/80 transition-colors"
          >
            <img
              src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'}
              alt={user?.name || 'User'}
              className="w-8 h-8 rounded-lg object-cover ring-1 ring-slate-700"
            />
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl z-50 p-2 animate-in fade-in zoom-in-95 duration-150">
              <div className="px-3 py-2 border-b border-slate-800 mb-1">
                <div className="text-xs font-semibold text-slate-100">{user?.name || 'Srikanth Rao'}</div>
                <div className="text-[11px] text-slate-400 truncate">{user?.email || 'srikanth@riskshield.ai'}</div>
              </div>

              <Link
                to="/profile"
                onClick={() => setShowUserMenu(false)}
                className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <User className="w-4 h-4 text-slate-400" />
                <span>Profile Settings</span>
              </Link>

              <Link
                to="/history"
                onClick={() => setShowUserMenu(false)}
                className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <ExternalLink className="w-4 h-4 text-slate-400" />
                <span>My Scans</span>
              </Link>

              <div className="border-t border-slate-800 my-1" />

              <button
                onClick={() => {
                  setShowUserMenu(false)
                  navigate('/')
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4 text-slate-400" />
                <span>Reset View</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
