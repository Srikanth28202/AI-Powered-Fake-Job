// src/components/layout/ProtectedRoute.jsx
import React, { useEffect, useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import useAuthStore from '../../store/authStore'
import { Shield } from 'lucide-react'

export default function ProtectedRoute() {
  const { isAuthenticated, accessToken, fetchCurrentUser } = useAuthStore()
  const [checking, setChecking] = useState(true)
  const location = useLocation()

  useEffect(() => {
    const verifySession = async () => {
      if (accessToken) {
        await fetchCurrentUser()
      }
      setChecking(false)
    }
    verifySession()
  }, [accessToken, fetchCurrentUser])

  if (checking) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center animate-pulse">
            <Shield className="w-6 h-6 text-indigo-400" />
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400 font-mono">
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            Verifying secure session...
          </div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated && !accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
