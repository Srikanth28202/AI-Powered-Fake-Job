// src/pages/DashboardPage.jsx
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  FileSearch,
  ArrowUpRight,
  ChevronRight,
  Eye,
  CheckCircle,
  Clock,
  Layers,
  Cpu,
} from 'lucide-react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { RiskBadge, StatusBadge } from '../components/common/Badge'
import { Modal } from '../components/common/Modal'
import { RiskGauge } from '../components/common/RiskGauge'
import useAuthStore from '../store/authStore'
import { useJobAnalysisStore } from '../store/jobAnalysisStore'
import {
  MOCK_KPIS,
  MOCK_TREND_DATA,
  MOCK_INDUSTRY_DATA,
  MOCK_SEVERITY_DISTRIBUTION,
  MOCK_RED_FLAGS,
} from '../services/mockData'

// Custom sleek dark tooltip for Recharts
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-xl bg-slate-900/95 border border-slate-700/80 p-3 shadow-xl backdrop-blur-md text-xs">
        <p className="font-semibold text-slate-200 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center justify-between gap-4 py-0.5">
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              {entry.name}:
            </span>
            <span className="font-mono font-bold text-slate-100">{entry.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { history } = useJobAnalysisStore()
  const [selectedJob, setSelectedJob] = useState(null)

  const recentScans = history.slice(0, 6)

  return (
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900/80 border border-indigo-500/20 p-6 sm:p-8 overflow-hidden shadow-2xl">
        <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
              <Cpu className="w-3.5 h-3.5" />
              <span>AI Engine Active: Machine Learning NLP v1.4</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.name ? user.name.split(' ')[0] : 'Analyst'}!
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
              Real-time threat telemetry detected <span className="text-rose-400 font-semibold">18 new scam campaigns</span> today.
              Ensemble classifier is currently operating at <span className="text-emerald-400 font-semibold">{MOCK_KPIS.modelAccuracy} accuracy</span>.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <Link to="/analyse">
              <Button variant="primary" size="lg" icon={Sparkles} className="shadow-indigo-500/30">
                Analyse New Job
              </Button>
            </Link>
            <Link to="/analytics">
              <Button variant="secondary" size="lg" icon={TrendingUp}>
                Threat Intel
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Card 1: Total Scanned */}
        <Card hover className="relative overflow-hidden group">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Total Analyzed
            </span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 group-hover:scale-110 transition-transform">
              <FileSearch className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono tracking-tight">
            {MOCK_KPIS.totalScanned.toLocaleString()}
          </div>
          <div className="flex items-center gap-1.5 mt-3 text-xs text-emerald-400 font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+14.8% vs last month</span>
          </div>
        </Card>

        {/* Card 2: Fake Jobs Detected */}
        <Card hover className="relative overflow-hidden group">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Confirmed Fraudulent
            </span>
            <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 group-hover:scale-110 transition-transform">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono tracking-tight flex items-baseline gap-2">
            <span>{MOCK_KPIS.fakeDetected.toLocaleString()}</span>
            <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
              {MOCK_KPIS.fraudPercentage}
            </span>
          </div>
          <div className="flex items-center gap-1.5 mt-3 text-xs text-rose-400 font-medium">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>+8.2% new scam variants</span>
          </div>
        </Card>

        {/* Card 3: Suspicious Under Review */}
        <Card hover className="relative overflow-hidden group">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Suspicious / Review
            </span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 group-hover:scale-110 transition-transform">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono tracking-tight">
            {MOCK_KPIS.suspiciousCount.toLocaleString()}
          </div>
          <div className="flex items-center gap-1.5 mt-3 text-xs text-amber-400 font-medium">
            <Clock className="w-3.5 h-3.5" />
            <span>Requires manual verification</span>
          </div>
        </Card>

        {/* Card 4: Model Precision & Accuracy */}
        <Card hover className="relative overflow-hidden group">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Model Accuracy
            </span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono tracking-tight">
            {MOCK_KPIS.modelAccuracy}
          </div>
          <div className="flex items-center gap-1.5 mt-3 text-xs text-slate-400 font-mono">
            <span>Precision: {MOCK_KPIS.precisionScore}</span>
            <span>•</span>
            <span>Recall: {MOCK_KPIS.recallScore}</span>
          </div>
        </Card>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Monthly Detection Trend (2 cols) */}
        <Card
          className="lg:col-span-2"
          title="Fraud Detection Telemetry (6-Month Trend)"
          subtitle="Total job scans compared against confirmed fake job alerts"
        >
          <div className="h-72 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={MOCK_TREND_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorFake" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="totalScanned"
                  name="Total Scans"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorTotal)"
                />
                <Area
                  type="monotone"
                  dataKey="fakeDetected"
                  name="Fake Jobs Detected"
                  stroke="#f43f5e"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorFake)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Chart 2: Severity Distribution Pie (1 col) */}
        <Card
          title="Risk Level Ratio"
          subtitle="Classification split across all analyzed job listings"
        >
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={MOCK_SEVERITY_DISTRIBUTION}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {MOCK_SEVERITY_DISTRIBUTION.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="space-y-2 mt-2 pt-3 border-t border-slate-800">
            {MOCK_SEVERITY_DISTRIBUTION.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  {item.name}
                </span>
                <span className="font-mono font-bold text-slate-200">{item.value}%</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Secondary Section: Risk by Industry & Top Red Flags */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Industry Risk Breakdown */}
        <Card
          title="Risk Rate by Job Category (%)"
          subtitle="Percentage of analyzed jobs flagged as fraudulent by industry"
        >
          <div className="h-64 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_INDUSTRY_DATA} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" domain={[0, 60]} unit="%" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="industry" type="category" stroke="#94a3b8" fontSize={11} width={110} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="riskRate" name="Fraud Rate %" fill="#818cf8" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Top Detected Red Flag Vectors */}
        <Card
          title="Top Red Flag Signatures"
          subtitle="Most prevalent deceptive patterns identified by the NLP model"
          action={
            <Link to="/analytics" className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
              Deep Intel <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          }
        >
          <div className="space-y-3.5 mt-1">
            {MOCK_RED_FLAGS.slice(0, 4).map((flag, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                <div className="flex items-center justify-between text-xs font-semibold mb-1">
                  <span className="text-slate-200 truncate pr-2">{flag.flag}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] shrink-0 font-bold ${
                    flag.severity === 'Critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}>
                    {flag.severity}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Frequency: {flag.count.toLocaleString()} occurrences</span>
                  <span className="font-mono text-indigo-400 font-semibold">{flag.percent}% of fake jobs</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent Scans Table */}
      <Card
        title="Recent Analysis Activity"
        subtitle="Live feed of inspected job vacancies with calibrated risk index"
        action={
          <Link to="/history">
            <Button variant="outline" size="sm" icon={ChevronRight}>
              View All History ({history.length})
            </Button>
          </Link>
        }
        noPadding
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3.5 px-6">Job Title & Company</th>
                <th className="py-3.5 px-4">Location</th>
                <th className="py-3.5 px-4">Compensation</th>
                <th className="py-3.5 px-4">Risk Level</th>
                <th className="py-3.5 px-4">Risk Index</th>
                <th className="py-3.5 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recentScans.map((job) => (
                <tr key={job.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-4 px-6">
                    <div className="font-semibold text-slate-100 max-w-xs truncate">{job.title}</div>
                    <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                      <span className="text-indigo-400 font-medium">{job.company}</span>
                      <span>•</span>
                      <span className="font-mono text-[10px] text-slate-500">{job.id}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-xs text-slate-400 whitespace-nowrap">
                    {job.location}
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
                  <td className="py-4 px-6 text-right whitespace-nowrap">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={Eye}
                      onClick={() => setSelectedJob(job)}
                    >
                      Inspect
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Job Details Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
          title={`Job Threat Inspection: ${selectedJob.id}`}
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
                Identified Risk Vectors & Red Flags
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
              <Link to="/analyse">
                <Button variant="primary" size="md" icon={Sparkles}>
                  Scan Another Job
                </Button>
              </Link>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
