// src/pages/AdminDashboardPage.jsx
// Enterprise Administrator Console: User Management, Suspicious Job Monitoring, Audit Logs, and Global Platform Analytics

import React, { useState, useEffect } from 'react'
import {
  Users,
  AlertTriangle,
  FileText,
  Shield,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Trash2,
  Edit,
  ArrowUpDown,
  RefreshCw,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Calendar,
  Lock,
  UserCheck,
  Building,
  MapPin,
  Flame,
} from 'lucide-react'
import { adminAPI, analyticsAPI } from '../services/api'
import useAuthStore from '../store/authStore'
import toast from 'react-hot-toast'

export default function AdminDashboardPage() {
  const { user: currentUser } = useAuthStore()
  const [activeTab, setActiveTab] = useState('users') // 'users' | 'suspicious' | 'audit' | 'analytics'

  // Users state
  const [users, setUsers] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [userSearch, setUserSearch] = useState('')
  const [userRoleFilter, setUserRoleFilter] = useState('')
  const [userPage, setUserPage] = useState(1)
  const [userTotalPages, setUserTotalPages] = useState(1)
  const [userTotal, setUserTotal] = useState(0)

  // Suspicious jobs state
  const [suspiciousJobs, setSuspiciousJobs] = useState([])
  const [suspiciousLoading, setSuspiciousLoading] = useState(false)
  const [suspiciousPage, setSuspiciousPage] = useState(1)
  const [suspiciousTotalPages, setSuspiciousTotalPages] = useState(1)
  const [suspiciousTotal, setSuspiciousTotal] = useState(0)

  // Audit logs state
  const [auditLogs, setAuditLogs] = useState([])
  const [auditLoading, setAuditLoading] = useState(false)
  const [auditPage, setAuditPage] = useState(1)
  const [auditTotalPages, setAuditTotalPages] = useState(1)
  const [auditTotal, setAuditTotal] = useState(0)

  // Global Analytics State
  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)

  // Destructive Confirmation Modal
  const [confirmModal, setConfirmModal] = useState({
    isOpen: false,
    type: null, // 'delete_user' | 'delete_job' | 'toggle_user'
    targetId: null,
    targetName: '',
    data: null,
  })

  // Role Edit Modal
  const [editUserModal, setEditUserModal] = useState({
    isOpen: false,
    user: null,
    role: 'user',
    isActive: true,
  })

  // Load Users
  const fetchUsers = async () => {
    setUsersLoading(true)
    try {
      const res = await adminAPI.getUsers({
        search: userSearch || undefined,
        role: userRoleFilter || undefined,
        page: userPage,
        page_size: 10,
      })
      setUsers(res.data.items || [])
      setUserTotal(res.data.total || 0)
      setUserTotalPages(res.data.total_pages || 1)
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to load users list')
    } finally {
      setUsersLoading(false)
    }
  }

  // Load Suspicious Jobs
  const fetchSuspiciousJobs = async () => {
    setSuspiciousLoading(true)
    try {
      const res = await adminAPI.getSuspiciousJobs({
        page: suspiciousPage,
        page_size: 10,
      })
      setSuspiciousJobs(res.data.items || [])
      setSuspiciousTotal(res.data.total || 0)
      setSuspiciousTotalPages(res.data.total_pages || 1)
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to fetch suspicious jobs')
    } finally {
      setSuspiciousLoading(false)
    }
  }

  // Load Audit Logs
  const fetchAuditLogs = async () => {
    setAuditLoading(true)
    try {
      const res = await adminAPI.getAuditLogs({
        page: auditPage,
        page_size: 15,
      })
      setAuditLogs(res.data.items || [])
      setAuditTotal(res.data.total || 0)
      setAuditTotalPages(res.data.total_pages || 1)
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to fetch audit log trail')
    } finally {
      setAuditLoading(false)
    }
  }

  // Load Global Analytics
  const fetchAnalytics = async () => {
    setAnalyticsLoading(true)
    try {
      const res = await analyticsAPI.getAdminOverview()
      setAnalytics(res.data)
    } catch (err) {
      toast.error('Failed to fetch platform global analytics')
    } finally {
      setAnalyticsLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'users') fetchUsers()
    if (activeTab === 'suspicious') fetchSuspiciousJobs()
    if (activeTab === 'audit') fetchAuditLogs()
    if (activeTab === 'analytics') fetchAnalytics()
  }, [activeTab, userPage, suspiciousPage, auditPage, userRoleFilter])

  // Trigger search on enter
  const handleUserSearchSubmit = (e) => {
    e.preventDefault()
    setUserPage(1)
    fetchUsers()
  }

  // Execute Destructive Action
  const handleExecuteConfirmedAction = async () => {
    if (!confirmModal.targetId) return
    const { type, targetId, data } = confirmModal
    try {
      if (type === 'delete_user') {
        await adminAPI.deleteUser(targetId)
        toast.success('User account purged successfully')
        fetchUsers()
      } else if (type === 'delete_job') {
        await adminAPI.deleteJobAnalysis(targetId)
        toast.success('Job analysis purged from database')
        fetchSuspiciousJobs()
      } else if (type === 'toggle_user') {
        await adminAPI.updateUser(targetId, { is_active: data.newStatus })
        toast.success(`User ${data.newStatus ? 'activated' : 'deactivated'} successfully`)
        fetchUsers()
      }
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Administrative action failed')
    } finally {
      setConfirmModal({ isOpen: false, type: null, targetId: null, targetName: '', data: null })
    }
  }

  // Update Role or Status via Edit Modal
  const handleSaveUserUpdate = async () => {
    if (!editUserModal.user) return
    try {
      await adminAPI.updateUser(editUserModal.user.id, {
        role: editUserModal.role,
        is_active: editUserModal.isActive,
      })
      toast.success(`Permissions updated for ${editUserModal.user.email}`)
      setEditUserModal({ isOpen: false, user: null, role: 'user', isActive: true })
      fetchUsers()
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to update user account')
    }
  }

  // Helper Badge Color
  const getRiskBadge = (level) => {
    if (level === 'High Risk' || level === 'Suspicious') {
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    }
    return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-indigo-950/40 border border-slate-800 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">Security Command Center</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 font-mono">
                RBAC Level 3: Admin
              </span>
            </div>
            <p className="text-sm text-slate-400">
              Backend-enforced administrator controls, user lifecycle management, and threat audit trail.
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            if (activeTab === 'users') fetchUsers()
            if (activeTab === 'suspicious') fetchSuspiciousJobs()
            if (activeTab === 'audit') fetchAuditLogs()
            if (activeTab === 'analytics') fetchAnalytics()
          }}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold transition-all self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh View
        </button>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 p-1.5 rounded-xl bg-slate-900/80 border border-slate-800 overflow-x-auto">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
            activeTab === 'users'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Users className="w-4 h-4" /> User Management
          {userTotal > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[11px] bg-indigo-950 text-indigo-200">
              {userTotal}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('suspicious')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
            activeTab === 'suspicious'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <ShieldAlert className="w-4 h-4" /> Suspicious Job Queue
          {suspiciousTotal > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[11px] bg-rose-500/20 text-rose-300 border border-rose-500/30">
              {suspiciousTotal}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
            activeTab === 'audit'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <FileText className="w-4 h-4" /> Immutable Audit Logs
        </button>

        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
            activeTab === 'analytics'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Building className="w-4 h-4" /> Platform Aggregates
        </button>
      </div>

      {/* ────────────────── TAB 1: USERS MANAGEMENT ────────────────── */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col md:flex-row gap-3 items-center justify-between">
            <form onSubmit={handleUserSearchSubmit} className="relative w-full md:w-80">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search user name or email..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </form>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs text-slate-400 font-medium">Role:</span>
              </div>
              <select
                value={userRoleFilter}
                onChange={(e) => {
                  setUserRoleFilter(e.target.value)
                  setUserPage(1)
                }}
                className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Roles</option>
                <option value="user">User</option>
                <option value="analyst">Security Analyst</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
          </div>

          {/* Users Table */}
          <div className="rounded-xl bg-slate-900/40 border border-slate-800/80 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    <th className="py-3 px-4">User Details</th>
                    <th className="py-3 px-4">Role</th>
                    <th className="py-3 px-4">Account Status</th>
                    <th className="py-3 px-4">Registered Date</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {usersLoading ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-500">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-400" />
                        Loading user accounts...
                      </td>
                    </tr>
                  ) : users.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-500">
                        No user accounts found matching query.
                      </td>
                    </tr>
                  ) : (
                    users.map((u) => {
                      const isSelf = u.id === currentUser?.id
                      return (
                        <tr key={u.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-semibold text-slate-200 flex items-center gap-2">
                              {u.full_name || 'No Name'}
                              {isSelf && (
                                <span className="px-1.5 py-0.2 rounded text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                  You
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-slate-400 font-mono">{u.email}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-md text-xs font-semibold capitalize ${
                                u.role === 'admin'
                                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                                  : u.role === 'analyst'
                                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                  : 'bg-slate-800 text-slate-300'
                              }`}
                            >
                              {u.role}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${
                                u.is_active
                                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                              }`}
                            >
                              <span
                                className={`w-1.5 h-1.5 rounded-full ${
                                  u.is_active ? 'bg-emerald-400' : 'bg-rose-400'
                                }`}
                              />
                              {u.is_active ? 'Active' : 'Disabled'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-xs text-slate-400 font-mono">
                            {new Date(u.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              {/* Edit permissions */}
                              <button
                                onClick={() =>
                                  setEditUserModal({
                                    isOpen: true,
                                    user: u,
                                    role: u.role,
                                    isActive: u.is_active,
                                  })
                                }
                                title="Edit Role & Permissions"
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                              >
                                <Edit className="w-3.5 h-3.5" />
                              </button>

                              {/* Toggle active status */}
                              {!isSelf && (
                                <button
                                  onClick={() =>
                                    setConfirmModal({
                                      isOpen: true,
                                      type: 'toggle_user',
                                      targetId: u.id,
                                      targetName: u.email,
                                      data: { newStatus: !u.is_active },
                                    })
                                  }
                                  title={u.is_active ? 'Deactivate User' : 'Activate User'}
                                  className={`p-1.5 rounded-lg transition-colors ${
                                    u.is_active
                                      ? 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-400'
                                      : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400'
                                  }`}
                                >
                                  {u.is_active ? (
                                    <XCircle className="w-3.5 h-3.5" />
                                  ) : (
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                  )}
                                </button>
                              )}

                              {/* Purge user */}
                              {!isSelf && (
                                <button
                                  onClick={() =>
                                    setConfirmModal({
                                      isOpen: true,
                                      type: 'delete_user',
                                      targetId: u.id,
                                      targetName: u.email,
                                    })
                                  }
                                  title="Permanently Purge Account"
                                  className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
              <span>
                Showing page {userPage} of {userTotalPages} ({userTotal} total users)
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={userPage <= 1}
                  onClick={() => setUserPage((p) => Math.max(1, p - 1))}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={userPage >= userTotalPages}
                  onClick={() => setUserPage((p) => p + 1)}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────── TAB 2: SUSPICIOUS JOBS MONITORING ────────────────── */}
      {activeTab === 'suspicious' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <span>Flagged High-Risk & Suspicious Job Postings across all users</span>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Total Flagged: {suspiciousTotal}
            </span>
          </div>

          <div className="rounded-xl bg-slate-900/40 border border-slate-800/80 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    <th className="py-3 px-4">Job Title & Company</th>
                    <th className="py-3 px-4">Risk Level</th>
                    <th className="py-3 px-4">Risk Score</th>
                    <th className="py-3 px-4">Warnings Flagged</th>
                    <th className="py-3 px-4">Submission Date</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {suspiciousLoading ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-500">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-rose-400" />
                        Scanning threat feed...
                      </td>
                    </tr>
                  ) : suspiciousJobs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-12 text-center text-slate-500">
                        No suspicious jobs currently detected.
                      </td>
                    </tr>
                  ) : (
                    suspiciousJobs.map((job) => (
                      <tr key={job.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4">
                          <div className="font-semibold text-slate-200">{job.title}</div>
                          <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                            <span>{job.company_name || 'Anonymous Employer'}</span>
                            {job.location && (
                              <span className="flex items-center gap-1 text-[11px] text-slate-500">
                                <MapPin className="w-3 h-3" /> {job.location}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded-md text-xs font-semibold border ${getRiskBadge(
                              job.risk_level
                            )}`}
                          >
                            {job.risk_level}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-rose-500 h-1.5 rounded-full"
                                style={{ width: `${job.risk_score}%` }}
                              />
                            </div>
                            <span className="font-mono text-xs font-bold text-rose-400">
                              {job.risk_score}/100
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-xs font-mono text-amber-400">
                          {job.warning_count} Rule Trigger{job.warning_count === 1 ? '' : 's'}
                        </td>
                        <td className="py-3 px-4 text-xs text-slate-400 font-mono">
                          {new Date(job.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() =>
                                setConfirmModal({
                                  isOpen: true,
                                  type: 'delete_job',
                                  targetId: job.id,
                                  targetName: job.title,
                                })
                              }
                              title="Purge Analysis"
                              className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
              <span>
                Showing page {suspiciousPage} of {suspiciousTotalPages} ({suspiciousTotal} flagged posts)
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={suspiciousPage <= 1}
                  onClick={() => setSuspiciousPage((p) => Math.max(1, p - 1))}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={suspiciousPage >= suspiciousTotalPages}
                  onClick={() => setSuspiciousPage((p) => p + 1)}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────── TAB 3: IMMUTABLE AUDIT LOGS ────────────────── */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Lock className="w-4 h-4 text-purple-400" />
              <span>Immutable security audit events: administrative mutations and user interventions</span>
            </div>
            <span className="text-xs text-slate-400 font-mono">Total Recorded Events: {auditTotal}</span>
          </div>

          <div className="rounded-xl bg-slate-900/40 border border-slate-800/80 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    <th className="py-3 px-4">Event Type</th>
                    <th className="py-3 px-4">Actor</th>
                    <th className="py-3 px-4">Target Entity</th>
                    <th className="py-3 px-4">Audit Metadata Diffs</th>
                    <th className="py-3 px-4 text-right">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {auditLoading ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-500">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-400" />
                        Querying audit trail...
                      </td>
                    </tr>
                  ) : auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-500">
                        No audit events recorded yet.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-800/30 transition-colors font-mono text-xs">
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold">
                            {log.action}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-300">{log.actor_email}</td>
                        <td className="py-3 px-4 text-slate-400">
                          {log.target_type}: {log.target_id.slice(-8)}
                        </td>
                        <td className="py-3 px-4 text-slate-300">
                          <pre className="text-[11px] bg-slate-950 p-1.5 rounded border border-slate-800 max-w-xs overflow-x-auto font-mono">
                            {JSON.stringify(log.details, null, 2)}
                          </pre>
                        </td>
                        <td className="py-3 px-4 text-right text-slate-400">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
              <span>
                Showing page {auditPage} of {auditTotalPages} ({auditTotal} audit events)
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={auditPage <= 1}
                  onClick={() => setAuditPage((p) => Math.max(1, p - 1))}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={auditPage >= auditTotalPages}
                  onClick={() => setAuditPage((p) => p + 1)}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 text-slate-200 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────── TAB 4: PLATFORM AGGREGATES ────────────────── */}
      {activeTab === 'analytics' && (
        <div className="space-y-4">
          {analyticsLoading ? (
            <div className="py-16 text-center text-slate-500">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-indigo-400" />
              Loading real-time platform aggregates...
            </div>
          ) : analytics ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-semibold">Total Platform Jobs</div>
                <div className="text-3xl font-extrabold text-white mt-1">
                  {analytics.total_jobs_analyzed}
                </div>
                <div className="text-xs text-indigo-400 mt-2 font-mono">Global dataset</div>
              </div>
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-semibold">Suspicious Posts</div>
                <div className="text-3xl font-extrabold text-rose-400 mt-1">
                  {analytics.suspicious_jobs_count}
                </div>
                <div className="text-xs text-slate-400 mt-2 font-mono">
                  {analytics.suspicious_percentage}% Threat Ratio
                </div>
              </div>
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-semibold">Avg Risk Score</div>
                <div className="text-3xl font-extrabold text-amber-400 mt-1">
                  {analytics.average_risk_score}/100
                </div>
                <div className="text-xs text-slate-400 mt-2 font-mono">Across all analyses</div>
              </div>
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 uppercase font-semibold">Registered Users</div>
                <div className="text-3xl font-extrabold text-purple-400 mt-1">{userTotal}</div>
                <div className="text-xs text-purple-400 mt-2 font-mono">Enterprise accounts</div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
              No analytics data returned.
            </div>
          )}
        </div>
      )}

      {/* ────────────────── CONFIRMATION MODAL (DESTRUCTIVE ACTIONS) ────────────────── */}
      {confirmModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center border border-rose-500/30">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Confirm Destructive Action</h3>
                <p className="text-xs text-slate-400">This operation cannot be reversed.</p>
              </div>
            </div>

            <p className="text-sm text-slate-300">
              Are you sure you want to proceed with{' '}
              <strong className="text-white">
                {confirmModal.type === 'delete_user'
                  ? `purging user "${confirmModal.targetName}" and all linked job records`
                  : confirmModal.type === 'delete_job'
                  ? `purging job analysis "${confirmModal.targetName}"`
                  : `changing status for "${confirmModal.targetName}"`}
              </strong>
              ?
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() =>
                  setConfirmModal({
                    isOpen: false,
                    type: null,
                    targetId: null,
                    targetName: '',
                    data: null,
                  })
                }
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteConfirmedAction}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-600/30 transition-all"
              >
                Yes, Execute Action
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────── EDIT USER PERMISSIONS MODAL ────────────────── */}
      {editUserModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
                <Edit className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Modify User Permissions</h3>
                <p className="text-xs text-slate-400 font-mono">{editUserModal.user?.email}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Assigned RBAC Role
                </label>
                <select
                  value={editUserModal.role}
                  onChange={(e) =>
                    setEditUserModal((prev) => ({ ...prev, role: e.target.value }))
                  }
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="user">Standard User</option>
                  <option value="analyst">Security Analyst</option>
                  <option value="admin">Platform Administrator</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Account Active Status
                </label>
                <select
                  value={editUserModal.isActive ? 'active' : 'disabled'}
                  onChange={(e) =>
                    setEditUserModal((prev) => ({
                      ...prev,
                      isActive: e.target.value === 'active',
                    }))
                  }
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="active">Active (Access Allowed)</option>
                  <option value="disabled">Disabled (Access Blocked)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() =>
                  setEditUserModal({ isOpen: false, user: null, role: 'user', isActive: true })
                }
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveUserUpdate}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
