// src/pages/NotFoundPage.jsx
import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldAlert, ArrowLeft } from 'lucide-react'
import { Button } from '../components/common/Button'

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6 text-center px-4 bg-slate-950 text-slate-100 relative overflow-hidden">
      <div className="absolute top-1/3 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-2 shadow-xl shadow-indigo-500/10">
        <ShieldAlert className="w-8 h-8" />
      </div>

      <div className="space-y-2">
        <span className="font-mono text-xs font-bold text-indigo-400 uppercase tracking-widest">
          Error 404 • Resource Not Located
        </span>
        <h1 className="text-4xl sm:text-5xl font-black text-white tracking-tight">
          Endpoint Not Found
        </h1>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          The requested threat intelligence report or dashboard view does not exist or has been archived.
        </p>
      </div>

      <Link to="/dashboard">
        <Button variant="primary" size="lg" icon={ArrowLeft} className="mt-2">
          Return to Dashboard
        </Button>
      </Link>
    </div>
  )
}
