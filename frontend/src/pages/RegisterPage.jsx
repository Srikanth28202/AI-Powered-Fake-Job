// src/pages/RegisterPage.jsx
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ShieldCheck, Mail, Lock, User, Briefcase, ArrowRight, Check } from 'lucide-react'
import useAuthStore from '../store/authStore'
import { Button } from '../components/common/Button'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'Cyber Risk Analyst',
    password: '',
    agree: true,
  })
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuthStore()
  const navigate = useNavigate()

  const calculateStrength = (pwd) => {
    if (!pwd) return 0
    let score = 0
    if (pwd.length >= 8) score += 25
    if (/[A-Z]/.test(pwd)) score += 25
    if (/[0-9]/.test(pwd)) score += 25
    if (/[^A-Za-z0-9]/.test(pwd)) score += 25
    return score
  }

  const pwdStrength = calculateStrength(formData.password)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name || !formData.email || !formData.password) {
      toast.error('Please fill in all required fields.')
      return
    }

    if (!formData.agree) {
      toast.error('Please accept the Terms of Service to proceed.')
      return
    }

    setIsLoading(true)
    await new Promise((r) => setTimeout(r, 600))
    register(formData)
    setIsLoading(false)
    toast.success('Account created successfully! Welcome to RiskShield AI.')
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background glow orbs */}
      <div className="absolute top-1/4 -right-20 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -left-20 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10 my-8">
        {/* Brand header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 shadow-xl shadow-indigo-500/25 mb-4 border border-indigo-400/30">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Create Your Account
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Access enterprise AI fake job detection and analytics
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-800 p-6 sm:p-8 shadow-2xl shadow-black/60">
          <form onSubmit={handleSubmit} className="space-y-4">
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
                  placeholder="Srikanth Rao"
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  required
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
                  placeholder="analyst@domain.com"
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Primary Role
              </label>
              <div className="relative">
                <Briefcase className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full bg-slate-950 text-sm text-slate-100 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                >
                  <option value="Cyber Risk Analyst">Cyber Risk Analyst</option>
                  <option value="Talent Acquisition / Recruiter">Talent Acquisition / Recruiter</option>
                  <option value="Candidate & Job Seeker">Candidate & Job Seeker</option>
                  <option value="Threat Intelligence Researcher">Threat Intelligence Researcher</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Create a strong password"
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  required
                />
              </div>

              {/* Password strength bar */}
              {formData.password && (
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Password Strength</span>
                    <span className="font-medium text-slate-300">
                      {pwdStrength <= 25 ? 'Weak' : pwdStrength <= 75 ? 'Good' : 'Strong'}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        pwdStrength <= 25 ? 'bg-rose-500' : pwdStrength <= 75 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${pwdStrength}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="agree"
                checked={formData.agree}
                onChange={(e) => setFormData({ ...formData, agree: e.target.checked })}
                className="rounded border-slate-700 bg-slate-950 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-slate-950"
              />
              <label htmlFor="agree" className="text-xs text-slate-400">
                I accept the{' '}
                <a href="#terms" onClick={(e) => e.preventDefault()} className="text-indigo-400 hover:underline">
                  Security Terms of Service
                </a>{' '}
                and Privacy Notice.
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-3"
              isLoading={isLoading}
              icon={ArrowRight}
            >
              Complete Registration
            </Button>
          </form>
        </div>

        {/* Footer link */}
        <div className="text-center mt-6 text-sm text-slate-400">
          Already registered?{' '}
          <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300">
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  )
}
