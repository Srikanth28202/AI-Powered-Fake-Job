// src/pages/AnalysisHistoryPage.jsx
import React, { useState, useMemo, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  Sparkles,
  ArrowUpDown,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Calendar,
  Building,
  RotateCcw,
} from 'lucide-react'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { RiskBadge, StatusBadge } from '../components/common/Badge'
import { EmptyState } from '../components/common/EmptyState'
import { Modal } from '../components/common/Modal'
import { RiskGauge } from '../components/common/RiskGauge'
import { useJobAnalysisStore } from '../store/jobAnalysisStore'
import toast from 'react-hot-toast'

export default function AnalysisHistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { history, deleteFromHistory, clearAllHistory } = useJobAnalysisStore()

  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [riskFilter, setRiskFilter] = useState('ALL') // ALL, HIGH, SUSPICIOUS, SAFE
  const [sortBy, setSortBy] = useState('newest') // newest, highest_risk, lowest_risk
  const [selectedJob, setSelectedJob] = useState(null)

  // Sync search param from URL
  useEffect(() => {
    const q = searchParams.get('q')
    if (q) setSearchQuery(q)
  }, [searchParams])

  // Filter and sort items
  const filteredHistory = useMemo(() => {
    return history
      .filter((job) => {
        // Text search
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase()
          const matches =
            job.title?.toLowerCase().includes(q) ||
            job.company?.toLowerCase().includes(q) ||
            job.id?.toLowerCase().includes(q) ||
            job.location?.toLowerCase().includes(q) ||
            (job.keyFlags && job.keyFlags.some((f) => f.toLowerCase().includes(q)))
          if (!matches) return false
        }

        // Risk filter
        if (riskFilter === 'HIGH') {
          return job.riskScore >= 70 || (job.riskLevel || '').toLowerCase().includes('high')
        }
        if (riskFilter === 'SUSPICIOUS') {
          return (job.riskScore >= 35 && job.riskScore < 70) || (job.riskLevel || '').toLowerCase().includes('suspic')
        }
        if (riskFilter === 'SAFE') {
          return job.riskScore < 35 || (job.riskLevel || '').toLowerCase().includes('safe')
        }

        return true
      })
      .sort((a, b) => {
        if (sortBy === 'highest_risk') return b.riskScore - a.riskScore
        if (sortBy === 'lowest_risk') return a.riskScore - b.riskScore
        // default newest
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0)
      })
  }, [history, searchQuery, riskFilter, sortBy])

  const handleDelete = (id, e) => {
    e.stopPropagation()
    deleteFromHistory(id)
    toast.success(`Removed analysis ${id}`)
  }

  const handleExportCsv = () => {
    if (filteredHistory.length === 0) {
      toast.error('No records to export.')
      return
    }

    const headers = ['ID', 'Title', 'Company', 'Location', 'RiskScore', 'RiskLevel', 'Salary', 'Date']
    const rows = filteredHistory.map((j) => [
      j.id,
      `"${j.title?.replace(/"/g, '""') || ''}"`,
      `"${j.company?.replace(/"/g, '""') || ''}"`,
      `"${j.location?.replace(/"/g, '""') || ''}"`,
      j.riskScore,
      j.riskLevel,
      `"${j.salary || ''}"`,
      j.createdAt,
    ])

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `RiskShield-Scans-${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Exported CSV archive.')
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Analysis History & Threat Archive
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Search, filter, and audit all analyzed job postings ({history.length} records logged)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="secondary" size="md" icon={Download} onClick={handleExportCsv}>
            Export CSV
          </Button>
          <Link to="/analyse">
            <Button variant="primary" size="md" icon={Sparkles}>
              New Scan
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card noPadding className="p-4 bg-slate-900/60 border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by job title, company name, ID, or flag vector..."
              className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 transition-all"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800">
              {[
                { id: 'ALL', label: 'All' },
                { id: 'HIGH', label: 'High Risk' },
                { id: 'SUSPICIOUS', label: 'Suspicious' },
                { id: 'SAFE', label: 'Verified Safe' },
              ].map((pill) => (
                <button
                  key={pill.id}
                  onClick={() => setRiskFilter(pill.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    riskFilter === pill.id
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {pill.label}
                </button>
              ))}
            </div>

            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-950 text-xs text-slate-300 font-medium rounded-xl px-3 py-2 border border-slate-800 focus:outline-none focus:border-indigo-500"
            >
              <option value="newest">Sort: Newest First</option>
              <option value="highest_risk">Sort: Highest Risk First</option>
              <option value="lowest_risk">Sort: Lowest Risk First</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Table or Empty State */}
      {filteredHistory.length === 0 ? (
        <EmptyState
          title="No analyzed listings match your criteria"
          description="Try modifying your search term or filter parameters, or analyze a new job posting now."
          actionLabel="Reset Search & Filters"
          onAction={() => {
            setSearchQuery('')
            setRiskFilter('ALL')
            setSortBy('newest')
          }}
        />
      ) : (
        <Card noPadding className="overflow-hidden border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/70 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  <th className="py-3.5 px-6">ID & Job Title</th>
                  <th className="py-3.5 px-4">Company & Location</th>
                  <th className="py-3.5 px-4">Compensation</th>
                  <th className="py-3.5 px-4">Risk Level</th>
                  <th className="py-3.5 px-4">Risk Score</th>
                  <th className="py-3.5 px-4">Analyzed Date</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredHistory.map((job) => (
                  <tr
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
                  >
                    <td className="py-4 px-6">
                      <div className="font-semibold text-slate-100 max-w-xs truncate group-hover:text-indigo-300 transition-colors">
                        {job.title}
                      </div>
                      <span className="font-mono text-[10px] text-slate-500 mt-0.5 block">{job.id}</span>
                    </td>

                    <td className="py-4 px-4">
                      <div className="text-slate-200 font-medium">{job.company}</div>
                      <div className="text-xs text-slate-400">{job.location}</div>
                    </td>

                    <td className="py-4 px-4 text-xs font-mono text-slate-300 whitespace-nowrap">
                      {job.salary || 'Unspecified'}
                    </td>

                    <td className="py-4 px-4 whitespace-nowrap">
                      <RiskBadge level={job.riskLevel} />
                    </td>

                    <td className="py-4 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              job.riskScore >= 70 ? 'bg-rose-500' : job.riskScore >= 35 ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${job.riskScore}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold text-slate-200">{job.riskScore}%</span>
                      </div>
                    </td>

                    <td className="py-4 px-4 text-xs text-slate-400 whitespace-nowrap font-mono">
                      {job.createdAt ? new Date(job.createdAt).toLocaleDateString() : 'Recent'}
                    </td>

                    <td className="py-4 px-6 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={Eye}
                          onClick={() => setSelectedJob(job)}
                        >
                          View
                        </Button>
                        <button
                          onClick={(e) => handleDelete(job.id, e)}
                          title="Delete from archive"
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-4 bg-slate-950/60 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Showing {filteredHistory.length} of {history.length} records</span>
            {history.length > 0 && (
              <button
                onClick={() => {
                  if (confirm('Clear all local scan history?')) {
                    clearAllHistory()
                    toast.success('History cleared.')
                  }
                }}
                className="text-xs text-slate-500 hover:text-rose-400 transition-colors"
              >
                Clear All Archive
              </button>
            )}
          </div>
        </Card>
      )}

      {/* Detail Inspection Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
          title={`Archive Inspection: ${selectedJob.id}`}
        >
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
              <div>
                <h4 className="text-base font-bold text-slate-100">{selectedJob.title}</h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Company: <span className="text-indigo-400 font-semibold">{selectedJob.company}</span> • {selectedJob.location}
                </p>
                <p className="text-xs text-slate-500 font-mono mt-1">Salary: {selectedJob.salary}</p>
              </div>
              <div className="shrink-0">
                <RiskGauge score={selectedJob.riskScore} size={110} strokeWidth={8} showIcon={false} />
              </div>
            </div>

            <div>
              <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Flagged Signals & Indicators
              </h5>
              <div className="space-y-2">
                {selectedJob.keyFlags && selectedJob.keyFlags.length > 0 ? (
                  selectedJob.keyFlags.map((flag, idx) => (
                    <div key={idx} className="flex items-center gap-2.5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 font-medium">
                      <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                      <span>{flag}</span>
                    </div>
                  ))
                ) : (
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300">
                    No deceptive signatures detected. Verified authentic hiring profile.
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <Button variant="secondary" size="md" onClick={() => setSelectedJob(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
