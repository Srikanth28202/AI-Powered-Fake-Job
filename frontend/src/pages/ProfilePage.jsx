// src/pages/ProfilePage.jsx
import React, { useState } from 'react'
import {
  User,
  Mail,
  Building,
  Key,
  Copy,
  RotateCw,
  Shield,
  Zap,
  Bell,
  Check,
  Save,
  Lock,
} from 'lucide-react'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import useAuthStore from '../store/authStore'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, updateProfile, regenerateApiKey } = useAuthStore()

  const [formData, setFormData] = useState({
    name: user?.name || 'Srikanth Rao',
    email: user?.email || 'srikanth@riskshield.ai',
    organization: user?.organization || 'Apex Cyber Intelligence',
    role: user?.role || 'Senior Cyber Risk Analyst',
    emailAlerts: user?.preferences?.emailAlerts ?? true,
    weeklyReport: user?.preferences?.weeklyReport ?? true,
    strictDomainCheck: user?.preferences?.strictDomainCheck ?? true,
  })

  const [copiedKey, setCopiedKey] = useState(false)

  const handleCopyKey = () => {
    if (!user?.apiKey) return
    navigator.clipboard.writeText(user.apiKey)
    setCopiedKey(true)
    toast.success('API Key copied to clipboard!')
    setTimeout(() => setCopiedKey(false), 2000)
  }

  const handleRegenerateKey = () => {
    if (confirm('Regenerating your API key will immediately invalidate your existing key. Continue?')) {
      regenerateApiKey()
      toast.success('Generated fresh API token!')
    }
  }

  const handleSaveProfile = (e) => {
    e.preventDefault()
    updateProfile({
      name: formData.name,
      email: formData.email,
      organization: formData.organization,
      role: formData.role,
      preferences: {
        emailAlerts: formData.emailAlerts,
        weeklyReport: formData.weeklyReport,
        strictDomainCheck: formData.strictDomainCheck,
      },
    })
    toast.success('Profile settings saved successfully!')
  }

  const scansPercentage = user ? Math.round((user.scansUsed / user.scansLimit) * 100) : 50

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Analyst Profile & Security Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage your credentials, organization parameters, API access keys, and threat alert preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Profile Card & Plan Overview */}
        <div className="space-y-6">
          <Card className="text-center relative overflow-hidden">
            <div className="relative w-24 h-24 mx-auto mb-4">
              <img
                src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80'}
                alt={user?.name || 'Avatar'}
                className="w-24 h-24 rounded-2xl object-cover ring-2 ring-indigo-500/50 shadow-xl"
              />
              <span className="absolute bottom-0 right-0 w-5 h-5 rounded-full bg-emerald-500 ring-4 ring-slate-900 flex items-center justify-center">
                <Check className="w-3 h-3 text-white" />
              </span>
            </div>

            <h3 className="text-lg font-bold text-white">{user?.name}</h3>
            <p className="text-xs text-indigo-400 font-medium">{user?.role}</p>
            <p className="text-xs text-slate-400 mt-1">{user?.organization}</p>

            <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>Account Status:</span>
              <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Verified Active
              </span>
            </div>
          </Card>

          {/* Quota & Plan Card */}
          <Card title="Subscription & Scan Quota" subtitle="Monthly rate limits & usage tracking">
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium">Plan Level</span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {user?.plan || 'Enterprise Pro ML'}
                </span>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Monthly Scans</span>
                  <span className="font-mono font-bold text-slate-200">
                    {user?.scansUsed} / {user?.scansLimit}
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${scansPercentage}%` }}
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Resets in 9 days on the 1st of next month.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Profile Form & API Keys (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Form */}
          <Card title="Personal & Organization Details" subtitle="Update your display identity and enterprise affiliation">
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full bg-slate-950 text-sm text-slate-100 rounded-xl pl-10 pr-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Work Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full bg-slate-950 text-sm text-slate-100 rounded-xl pl-10 pr-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 transition-all"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Organization / Company
                  </label>
                  <div className="relative">
                    <Building className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={formData.organization}
                      onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                      className="w-full bg-slate-950 text-sm text-slate-100 rounded-xl pl-10 pr-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Role Title
                  </label>
                  <input
                    type="text"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full bg-slate-950 text-sm text-slate-100 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 transition-all"
                  />
                </div>
              </div>

              {/* Notification Toggles */}
              <div className="pt-4 border-t border-slate-800 space-y-3">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Threat Notification Preferences
                </h4>

                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <div>
                    <div className="text-xs font-semibold text-slate-200">Email Alerts on High-Risk Detections</div>
                    <div className="text-[11px] text-slate-400">Immediate dispatch when a critical fraud score is registered</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={formData.emailAlerts}
                    onChange={(e) => setFormData({ ...formData, emailAlerts: e.target.checked })}
                    className="rounded border-slate-700 bg-slate-900 text-indigo-500 focus:ring-indigo-500"
                  />
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <div>
                    <div className="text-xs font-semibold text-slate-200">Weekly Threat Intelligence Digest</div>
                    <div className="text-[11px] text-slate-400">Summarized PDF report of detected syndicate campaigns</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={formData.weeklyReport}
                    onChange={(e) => setFormData({ ...formData, weeklyReport: e.target.checked })}
                    className="rounded border-slate-700 bg-slate-900 text-indigo-500 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-3">
                <Button type="submit" variant="primary" size="md" icon={Save}>
                  Save Settings
                </Button>
              </div>
            </form>
          </Card>

          {/* API Keys Management */}
          <Card
            title="REST API & Automated Ingestion Key"
            subtitle="Authenticate background job feeds or candidate pipeline integrations"
          >
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Production Secret API Key
                </label>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-slate-950 font-mono text-xs text-indigo-300 px-3.5 py-2.5 rounded-xl border border-slate-800 truncate select-all">
                    {user?.apiKey || 'fjd_live_key_9a7b63c2e41108a994ef03d7b8821e90'}
                  </div>
                  <Button
                    variant="secondary"
                    size="md"
                    icon={copiedKey ? Check : Copy}
                    onClick={handleCopyKey}
                  >
                    {copiedKey ? 'Copied' : 'Copy'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="md"
                    icon={RotateCw}
                    onClick={handleRegenerateKey}
                    title="Roll key"
                  >
                    Roll
                  </Button>
                </div>
                <p className="text-[11px] text-slate-500 mt-1.5">
                  Created on {user?.apiKeyCreated || '2026-08-14'}. Never share your API secret in client-side code.
                </p>
              </div>

              {/* Code snippet example */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300">
                <div className="text-[10px] text-slate-500 uppercase font-semibold mb-1">CURL Quickstart</div>
                <div className="overflow-x-auto text-indigo-300 whitespace-pre">
                  curl -X POST https://api.riskshield.ai/v1/jobs/analyze \<br />
                  &nbsp;&nbsp;-H "Authorization: Bearer {user?.apiKey?.slice(0, 14)}..." \<br />
                  &nbsp;&nbsp;-d '&#123;"title": "Remote Data Entry", "description": "..."&#125;'
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
