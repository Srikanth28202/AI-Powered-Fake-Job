// src/pages/LoginPage.jsx
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck, Mail, Lock, ArrowRight, Shield, Zap, Sparkles } from 'lucide-react'
import useAuthStore from '../store/authStore'
import { Button } from '../components/common/Button'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please enter both email and password.')
      return
    }

    setIsLoading(true)
    await new Promise((r) => setTimeout(r, 600))
    login(email, password)
    setIsLoading(false)
    toast.success('Welcome back, analyst!')
    navigate('/dashboard')
  }

  const handleQuickDemo = (demoEmail) => {
    setEmail(demoEmail)
    setPassword('demoSecurePass2026!')
    login(demoEmail, 'demoSecurePass2026!')
    toast.success(`Logged in as ${demoEmail.split('@')[0]}`)
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background glow orbs */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />

      {/* Auth Card Container */}
      <div className="w-full max-w-md relative z-10">
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 shadow-xl shadow-indigo-500/25 mb-4 border border-indigo-400/30">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Sign In to RiskShield
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            AI-Powered Fake Job Detection & Risk Intelligence
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 shadow-2xl shadow-black/60">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@enterprise.com"
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Password
                </label>
                <a href="#forgot" onClick={(e) => { e.preventDefault(); toast.info('Demo password reset triggered.'); }} className="text-xs text-indigo-400 hover:text-indigo-300">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-2"
              isLoading={isLoading}
              icon={ArrowRight}
            >
              Sign In to Platform
            </Button>
          </form>

          {/* Quick Demo Fill Buttons */}
          <div className="mt-6 pt-5 border-t border-slate-800/80">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" /> One-Click Demo Access
              </span>
              <span className="text-[10px] text-slate-500 font-mono">No pwd needed</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemo('srikanth@riskshield.ai')}
                className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-indigo-500/50 text-left transition-all group"
              >
                <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                  Security Analyst
                </div>
                <div className="text-[10px] text-slate-500">srikanth@riskshield.ai</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickDemo('talent.recruiter@verifirm.org')}
                className="p-2.5 rounded-xl bg-slate-950 hover:bg-slate-800/80 border border-slate-800 hover:border-purple-500/50 text-left transition-all group"
              >
                <div className="text-xs font-semibold text-slate-200 group-hover:text-purple-300">
                  Talent Recruiter
                </div>
                <div className="text-[10px] text-slate-500">talent.recruiter@verifirm.org</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer link */}
        <div className="text-center mt-6 text-sm text-slate-400">
          Don't have an enterprise account?{' '}
          <Link to="/register" className="font-semibold text-indigo-400 hover:text-indigo-300">
            Register now
          </Link>
        </div>

        {/* Security badge */}
        <div className="flex items-center justify-center gap-2 text-center mt-8 text-xs text-slate-600">
          <Shield className="w-3.5 h-3.5 text-emerald-500/80" />
          <span>256-bit TLS Encrypted Session • ISO-27001 Compliant</span>
        </div>
      </div>
    </div>
  )
}
