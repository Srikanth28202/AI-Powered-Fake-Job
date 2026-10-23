// src/pages/AnalyticsPage.jsx
import React, { useState } from 'react'
import {
  BarChart3,
  TrendingUp,
  ShieldAlert,
  Cpu,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Globe,
  Filter,
} from 'lucide-react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import {
  MOCK_KPIS,
  MOCK_TREND_DATA,
  MOCK_INDUSTRY_DATA,
  MOCK_RED_FLAGS,
  MOCK_SEVERITY_DISTRIBUTION,
} from '../services/mockData'

function DarkTooltip({ active, payload, label }) {
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

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d')

  const confusionMatrix = {
    tp: 3290, // True Positive (Caught fake jobs)
    fp: 64,   // False Positive (Legit flagged as fake)
    fn: 120,  // False Negative (Missed fake jobs)
    tn: 11418 // True Negative (Correctly verified safe)
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full mb-2 border border-indigo-500/20">
            <Activity className="w-3.5 h-3.5" />
            <span>Fraud Intelligence & Classifier Telemetry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Threat Analytics & ML Performance
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Global attack vector telemetry, scam vector prevalence, and Scikit-learn model evaluation benchmarks.
          </p>
        </div>

        {/* Time Selector */}
        <div className="inline-flex rounded-xl bg-slate-900 p-1 border border-slate-800 self-start sm:self-auto">
          {[
            { id: '7d', label: '7 Days' },
            { id: '30d', label: '30 Days' },
            { id: '90d', label: 'Quarter' },
            { id: 'all', label: 'All Time' },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTimeRange(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                timeRange === t.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card hover>
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            Fraud Detection Rate
          </span>
          <div className="text-2xl font-extrabold text-rose-400 font-mono mt-1">
            {MOCK_KPIS.fraudPercentage}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            1 in 4.3 analyzed listings flagged as deceptive
          </p>
        </Card>

        <Card hover>
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            Highest Risk Sector
          </span>
          <div className="text-2xl font-extrabold text-amber-400 font-mono mt-1">
            Crypto (46.9%)
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Followed closely by Remote Data Entry (46.5%)
          </p>
        </Card>

        <Card hover>
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            Top Attack Vector
          </span>
          <div className="text-xl font-bold text-indigo-400 truncate mt-1">
            Free Webmail (54%)
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Public domains (@gmail, @proton) instead of enterprise DNS
          </p>
        </Card>

        <Card hover>
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            Model ROC-AUC
          </span>
          <div className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">
            0.984
          </div>
          <p className="text-xs text-slate-500 mt-2">
            TF-IDF + Logistic Regression ensemble
          </p>
        </Card>
      </div>

      {/* Attack Vectors Breakdown (Horizontal Bar) */}
      <Card
        title="Scam Vectors & Red Flag Taxonomy"
        subtitle="Distribution of identified fraudulent mechanics across 3,410 confirmed fake postings"
      >
        <div className="space-y-4 mt-2">
          {MOCK_RED_FLAGS.map((flag, idx) => (
            <div key={idx} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-medium">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${flag.severity === 'Critical' ? 'bg-rose-500' : 'bg-amber-500'}`} />
                  <span className="text-slate-200">{flag.flag}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{flag.count.toLocaleString()} cases</span>
                  <span className="font-mono font-bold text-indigo-400">{flag.percent}%</span>
                </div>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full ${
                    flag.severity === 'Critical'
                      ? 'bg-gradient-to-r from-rose-500 to-red-600'
                      : 'bg-gradient-to-r from-amber-500 to-indigo-500'
                  }`}
                  style={{ width: `${flag.percent}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Machine Learning Model Performance Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix */}
        <Card
          title="Classifier Confusion Matrix (Evaluation Set)"
          subtitle="True vs Predicted classification counts on n=14,892 test samples"
        >
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 text-center">
              <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block">
                True Positives (TP)
              </span>
              <div className="text-2xl font-extrabold text-white font-mono mt-1">
                {confusionMatrix.tp.toLocaleString()}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Scams successfully detected & neutralized
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider block">
                False Positives (FP)
              </span>
              <div className="text-2xl font-extrabold text-white font-mono mt-1">
                {confusionMatrix.fp.toLocaleString()}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Legitimate vacancies flagged as suspicious
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider block">
                False Negatives (FN)
              </span>
              <div className="text-2xl font-extrabold text-white font-mono mt-1">
                {confusionMatrix.fn.toLocaleString()}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Evasive scams missed by initial filter
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 text-center">
              <span className="text-[11px] font-semibold text-indigo-300 uppercase tracking-wider block">
                True Negatives (TN)
              </span>
              <div className="text-2xl font-extrabold text-white font-mono mt-1">
                {confusionMatrix.tn.toLocaleString()}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Authentic job postings correctly passed
              </p>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-slate-800 text-center font-mono text-xs">
            <div>
              <span className="text-slate-500 block text-[10px]">PRECISION</span>
              <span className="font-bold text-slate-200">{MOCK_KPIS.precisionScore}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">RECALL</span>
              <span className="font-bold text-slate-200">{MOCK_KPIS.recallScore}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">ACCURACY</span>
              <span className="font-bold text-emerald-400">{MOCK_KPIS.modelAccuracy}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">LATENCY</span>
              <span className="font-bold text-indigo-400">{MOCK_KPIS.avgInferenceTimeMs}ms</span>
            </div>
          </div>
        </Card>

        {/* Industry Risk Breakdown */}
        <Card
          title="Industry Threat Vulnerability"
          subtitle="Breakdown of analyzed jobs vs confirmed scam postings"
        >
          <div className="h-64 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MOCK_INDUSTRY_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="industry" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip content={<DarkTooltip />} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="total" name="Total Scanned" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fake" name="Fake Jobs" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Threat Bulletins */}
      <Card title="Active Threat Bulletins & Known Syndicates" subtitle="Recent intelligence advisories from the ML threat research team">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-2 text-rose-400 text-xs font-bold mb-1">
              <ShieldAlert className="w-4 h-4" />
              <span>Operation GhostCourier</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Reshipping fraud syndicate targeting remote workers with counterfeit USPS/FedEx shipping labels.
            </p>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">Identified: Oct 2026</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-bold mb-1">
              <AlertTriangle className="w-4 h-4" />
              <span>Fake Task Mule Wave</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Crypto commission scam impersonating Binance and Coinbase with Telegram interview pipelines.
            </p>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">Identified: Oct 2026</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold mb-1">
              <Cpu className="w-4 h-4" />
              <span>Disposable Domain Clones</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              128 lookalike domains impersonating Fortune 500 career subdomains automatically added to quarantine.
            </p>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">Active Defense Rule</span>
          </div>
        </div>
      </Card>
    </div>
  )
}
