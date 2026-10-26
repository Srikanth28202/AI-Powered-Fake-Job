// src/pages/AnalyseJobPage.jsx
import React, { useState } from 'react'
import {
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Zap,
  Download,
  Share2,
  CheckCircle2,
  HelpCircle,
  ExternalLink,
  Cpu,
  FileText,
  Building,
  Mail,
  DollarSign,
  MapPin,
  Briefcase,
  Layers,
  ArrowRight,
} from 'lucide-react'

import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { RiskBadge } from '../components/common/Badge'
import { RiskGauge } from '../components/common/RiskGauge'
import { useJobAnalysisStore } from '../store/jobAnalysisStore'
import { MOCK_JOB_PRESETS } from '../services/mockData'
import toast from 'react-hot-toast'

export default function AnalyseJobPage() {
  const {
    currentInput,
    setInputField,
    resetInput,
    loadPresetById,
    runAnalysis,
    isAnalyzing,
    analysisStep,
    scanProgress,
    activeResult,
    setActiveResult,
  } = useJobAnalysisStore()

  const [activeTab, setActiveTab] = useState('form') // 'form' or 'raw'
  const [rawText, setRawText] = useState('')
  const [presetFilter, setPresetFilter] = useState('all') // 'all', 'fake', 'real'

  const handlePresetClick = (presetId) => {
    loadPresetById(presetId)
    setActiveResult(null)
    toast.success('Loaded job preset. Click "Start AI Risk Scan" to inspect.')
  }

  const filteredPresets = MOCK_JOB_PRESETS.filter((preset) => {
    if (presetFilter === 'fake') return preset.id.startsWith('fake')
    if (presetFilter === 'real') return !preset.id.startsWith('fake')
    return true
  })

  const handleRawTextParse = () => {
    if (!rawText.trim()) {
      toast.error('Please paste job posting text first.')
      return
    }
    // Simple heuristic parser for raw text
    const lines = rawText.split('\n').map((l) => l.trim()).filter(Boolean)
    setInputField('title', lines[0] || 'Parsed Position')
    setInputField('company_name', lines[1] || 'Parsed Company')
    setInputField('description', rawText)
    setActiveTab('form')
    toast.success('Pasted text parsed into form fields.')
  }

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault()
    if (!currentInput.title && !currentInput.description) {
      toast.error('Please provide at least a Job Title or Description.')
      return
    }

    try {
      await runAnalysis()
      toast.success('AI Risk Evaluation completed!')
    } catch (err) {
      toast.error('Scan encountered an error.')
    }
  }

  const handleExportJson = () => {
    if (!activeResult) return
    const blob = new Blob([JSON.stringify(activeResult, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `RiskShield-Analysis-${activeResult.id}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Analysis report downloaded.')
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full mb-2 border border-indigo-500/20">
            <Cpu className="w-3.5 h-3.5" />
            <span>Dual-Engine: Scikit-learn + Domain Threat Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            AI Job Risk & Scam Screener
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Detect fraudulent vacancies, phishing schemes, and upfront check scams with calibrated ML confidence.
          </p>
        </div>

        {activeResult && (
          <Button
            variant="secondary"
            size="md"
            icon={RotateCcw}
            onClick={() => setActiveResult(null)}
          >
            New Job Scan
          </Button>
        )}
      </div>

      {/* Quick Demo Presets Bar with Dataset Ground-Truth Explanations */}
      <Card noPadding className="p-5 bg-slate-900/60 border-slate-800 shadow-xl space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              EMSCAD Benchmark Dataset Samples ({MOCK_JOB_PRESETS.length} postings):
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setPresetFilter('all')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                presetFilter === 'all'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All ({MOCK_JOB_PRESETS.length})
            </button>
            <button
              onClick={() => setPresetFilter('fake')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                presetFilter === 'fake'
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-rose-300'
              }`}
            >
              Fraudulent ({MOCK_JOB_PRESETS.filter((p) => p.id.startsWith('fake')).length})
            </button>
            <button
              onClick={() => setPresetFilter('real')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                presetFilter === 'real'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-emerald-300'
              }`}
            >
              Legitimate ({MOCK_JOB_PRESETS.filter((p) => !p.id.startsWith('fake')).length})
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 max-h-[460px] overflow-y-auto pr-1">
          {filteredPresets.map((preset) => {
            const isFake = preset.id.startsWith('fake')
            return (
              <button
                key={preset.id}
                onClick={() => handlePresetClick(preset.id)}
                className={`p-3 rounded-xl border text-left transition-all group flex flex-col justify-between ${
                  isFake
                    ? 'bg-rose-950/20 border-rose-500/30 hover:border-rose-500/60 hover:bg-rose-950/40'
                    : 'bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/60 hover:bg-emerald-950/40'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1.5">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                        isFake ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      {preset.verdict}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">EMSCAD</span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-white line-clamp-1">
                    {preset.title}
                  </div>
                  <div className="text-[11px] text-slate-400 mb-2">
                    {preset.company_name}
                  </div>
                  <p className="text-[10px] text-slate-400 line-clamp-3 bg-slate-950/60 p-2 rounded-lg border border-slate-800/80 leading-relaxed font-sans">
                    <strong className="text-slate-300">Why: </strong>
                    {preset.why_explanation}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                  <span className="text-indigo-400 group-hover:underline font-semibold flex items-center gap-1">
                    Load & Scan <ArrowRight className="w-3 h-3" />
                  </span>
                  <span className="text-slate-500">{preset.salary_range ? 'Salary Included' : ''}</span>
                </div>
              </button>
            )
          })}
        </div>
      </Card>


      {/* Scanning In-Progress Animation State */}
      {isAnalyzing && (
        <Card className="p-12 text-center bg-slate-900/90 border-indigo-500/40 shadow-2xl relative overflow-hidden">
          <div className="max-w-md mx-auto space-y-6">
            {/* Animated Pulsing Shield */}
            <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-indigo-500/20 animate-ping" />
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-xl shadow-indigo-500/30">
                <Sparkles className="w-10 h-10 text-white animate-spin" />
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold text-white">Inspecting Job Posting Telemetry</h3>
              <p className="text-sm text-indigo-300 font-mono mt-1 h-6 transition-all">
                {analysisStep}
              </p>
            </div>

            {/* Progress bar */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-slate-400 font-mono">
                <span>Model Pipeline Progress</span>
                <span>{scanProgress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${scanProgress}%` }}
                />
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Inspection Result Presentation */}
      {!isAnalyzing && activeResult && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Top Verdict Banner */}
          <div
            className={`p-6 rounded-3xl border flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-2xl ${
              activeResult.riskLevel === 'High Risk'
                ? 'bg-gradient-to-r from-rose-950/60 via-slate-900 to-slate-900 border-rose-500/40 shadow-rose-900/20'
                : activeResult.riskLevel === 'Suspicious'
                ? 'bg-gradient-to-r from-amber-950/60 via-slate-900 to-slate-900 border-amber-500/40 shadow-amber-900/20'
                : 'bg-gradient-to-r from-emerald-950/60 via-slate-900 to-slate-900 border-emerald-500/40 shadow-emerald-900/20'
            }`}
          >
            <div className="flex items-start gap-4">
              <div
                className={`p-3.5 rounded-2xl shrink-0 ${
                  activeResult.riskLevel === 'High Risk'
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : activeResult.riskLevel === 'Suspicious'
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}
              >
                {activeResult.riskLevel === 'High Risk' ? (
                  <ShieldAlert className="w-8 h-8" />
                ) : activeResult.riskLevel === 'Suspicious' ? (
                  <AlertTriangle className="w-8 h-8" />
                ) : (
                  <ShieldCheck className="w-8 h-8" />
                )}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <RiskBadge level={activeResult.riskLevel} size="md" />
                  <span className="text-xs font-mono text-slate-400">ID: {activeResult.id}</span>
                </div>
                <h2 className="text-2xl font-extrabold text-white tracking-tight">
                  {activeResult.riskLevel === 'High Risk'
                    ? 'HIGH RISK FRAUD DETECTED'
                    : activeResult.riskLevel === 'Suspicious'
                    ? 'SUSPICIOUS LISTING - CAUTION ADVISED'
                    : 'VERIFIED LEGITIMATE EMPLOYMENT VACANCY'}
                </h2>
                <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-xl">
                  {activeResult.title} at <strong className="text-white">{activeResult.company}</strong> ({activeResult.location})
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Button variant="secondary" size="sm" icon={Download} onClick={handleExportJson}>
                Export JSON
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={Share2}
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href)
                  toast.success('Inspection link copied to clipboard!')
                }}
              >
                Share
              </Button>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Risk Gauge & Model Metrics */}
            <div className="space-y-6">
              <Card title="Calibrated Risk Assessment" subtitle="Composite probability index">
                <RiskGauge score={activeResult.riskScore ?? activeResult.risk_score ?? 0} size={190} strokeWidth={15} />

                <div className="grid grid-cols-2 gap-2 mt-6 pt-4 border-t border-slate-800 text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-400 text-[10px] uppercase font-semibold">Fraud Probability</span>
                    <div className="text-base font-bold font-mono text-slate-200 mt-0.5">
                      {(((activeResult.ml_prediction?.fraud_probability ?? activeResult.fraudProbability) || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-400 text-[10px] uppercase font-semibold">Model Confidence</span>
                    <div className="text-base font-bold font-mono text-slate-200 mt-0.5">
                      {(((activeResult.ml_prediction?.confidence ?? activeResult.confidence) || 0.95) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-3 px-1">
                  <span>Engine: {activeResult.ml_prediction?.model_family || 'TF-IDF + Logistic Regression'}</span>
                  <span>Threshold: {activeResult.ml_prediction?.decision_threshold || 0.50}</span>
                </div>
              </Card>

              {/* Model Feature Attributions (Weights) */}
              <Card title="Model Feature Weights" subtitle="Top linguistic tokens influencing prediction">
                <div className="space-y-2 mt-1 max-h-60 overflow-y-auto pr-1">
                  {(activeResult.model_feature_attributions || activeResult.radarBreakdown || []).map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-950/70 border border-slate-800/60 text-xs">
                      <span className="font-mono text-slate-300 font-medium">{item.token || item.word || item.metric}</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        (item.weight ?? item.coefficient ?? 0) > 0 || item.impact?.includes('Fraud')
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}>
                        {item.impact || ((item.weight ?? item.coefficient ?? 0) > 0 ? 'Fraud Indication' : 'Safe')} ({(item.weight ?? item.score ?? 0).toFixed ? (item.weight ?? 0).toFixed(2) : item.score})
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Right Column: Identified Red Flags & Recommendations (2 cols) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Identified Red Flags */}
              <Card
                title={`Security Threat Indicators (${(activeResult.rule_based_warnings || activeResult.flags || []).length})`}
                subtitle="High-risk heuristic patterns and deceptive markers detected"
              >
                {(activeResult.rule_based_warnings || activeResult.flags || []).length === 0 ? (
                  <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-center">
                    <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                    <h4 className="text-base font-bold text-white">Clean Bill of Health</h4>
                    <p className="text-xs text-slate-300 max-w-md mx-auto mt-1">
                      No upfront fees, cryptocurrency mule routing, or encrypted chat application interviews were identified.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {(activeResult.rule_based_warnings || activeResult.flags || []).map((flag, idx) => (
                      <div
                        key={flag.id || idx}
                        className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700 transition-colors"
                      >
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <div className="flex items-center gap-2 font-semibold text-sm text-slate-100">
                            <AlertTriangle className={`w-4 h-4 shrink-0 ${
                              flag.severity === 'Critical' ? 'text-rose-400' : 'text-amber-400'
                            }`} />
                            <span>{flag.indicator || flag.title}</span>
                          </div>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 ${
                              flag.severity === 'Critical'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            }`}
                          >
                            {flag.severity}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed pl-6">
                          {flag.category ? `Category: ${flag.category}. ` : ''}
                          {flag.matched_text ? `Triggered by: "${flag.matched_text}"` : (flag.description || '')}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              {/* Actionable Candidate Safety Guidance */}
              <Card
                title="Recommended Candidate Actions"
                subtitle="Practical safety protocols when handling this vacancy"
              >
                <div className="space-y-2.5">
                  {(activeResult.verification_recommendations || activeResult.recommendations || []).map((rec, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800/60 text-xs text-slate-300 leading-relaxed">
                      <div className="w-5 h-5 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center shrink-0 font-mono text-[11px] font-bold mt-0.5">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        {rec.priority && (
                          <span className={`text-[10px] font-bold mr-2 uppercase ${rec.priority === 'CRITICAL' ? 'text-rose-400' : 'text-amber-400'}`}>
                            [{rec.priority}]
                          </span>
                        )}
                        <span>{rec.guidance || rec}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {activeResult.disclaimer && (
                  <p className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 italic">
                    Disclaimer: {activeResult.disclaimer}
                  </p>
                )}
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Input Form Screen */}
      {!isAnalyzing && !activeResult && (
        <Card title="Job Listing Parameters" subtitle="Fill in vacancy information to run automated risk detection">
          {/* Input mode tabs */}
          <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-4">
            <button
              onClick={() => setActiveTab('form')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'form'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Structured Fields
            </button>
            <button
              onClick={() => setActiveTab('raw')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'raw'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Paste Full Text
            </button>
          </div>

          {activeTab === 'raw' ? (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Paste Raw Job Posting Content
                </label>
                <textarea
                  rows={10}
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste the full job posting text including title, company name, contact info, salary, and requirements..."
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl p-4 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-sans leading-relaxed"
                />
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="secondary" size="md" onClick={() => setRawText('')}>
                  Clear
                </Button>
                <Button variant="primary" size="md" icon={Sparkles} onClick={handleRawTextParse}>
                  Parse into Structured Fields
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleAnalyze} className="space-y-6">
              {/* Row 1: Title, Company, Location */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" /> Job Title *
                  </label>
                  <input
                    type="text"
                    value={currentInput.title}
                    onChange={(e) => setInputField('title', e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-slate-400" /> Company Name *
                  </label>
                  <input
                    type="text"
                    value={currentInput.company_name}
                    onChange={(e) => setInputField('company_name', e.target.value)}
                    placeholder="e.g. Stripe, Acme Corp"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" /> Location / Remote
                  </label>
                  <input
                    type="text"
                    value={currentInput.location}
                    onChange={(e) => setInputField('location', e.target.value)}
                    placeholder="e.g. Remote (US) or New York, NY"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>
              </div>

              {/* Row 2: Salary, Contact Email, Department */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <DollarSign className="w-3.5 h-3.5 text-slate-400" /> Salary Range
                  </label>
                  <input
                    type="text"
                    value={currentInput.salary_range}
                    onChange={(e) => setInputField('salary_range', e.target.value)}
                    placeholder="e.g. $120,000 - $150,000 / yr"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" /> Recruiter Contact Email
                  </label>
                  <input
                    type="text"
                    value={currentInput.contact_email}
                    onChange={(e) => setInputField('contact_email', e.target.value)}
                    placeholder="e.g. recruiter@company.com or @gmail.com"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-slate-400" /> Industry / Category
                  </label>
                  <input
                    type="text"
                    value={currentInput.department}
                    onChange={(e) => setInputField('department', e.target.value)}
                    placeholder="e.g. Technology, Data Entry, Crypto"
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-3.5 py-2.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>
              </div>

              {/* Textareas */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-slate-400" /> Full Job Description *
                </label>
                <textarea
                  rows={4}
                  value={currentInput.description}
                  onChange={(e) => setInputField('description', e.target.value)}
                  placeholder="Paste the role overview, day-to-day duties, and responsibilities..."
                  className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl p-3.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all leading-relaxed"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Requirements & Qualifications
                  </label>
                  <textarea
                    rows={3}
                    value={currentInput.requirements}
                    onChange={(e) => setInputField('requirements', e.target.value)}
                    placeholder="Candidate qualifications, required tools, background..."
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl p-3.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all leading-relaxed"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Benefits & Hiring Process Notes
                  </label>
                  <textarea
                    rows={3}
                    value={currentInput.benefits}
                    onChange={(e) => setInputField('benefits', e.target.value)}
                    placeholder="Benefits, equipment checks, interview chat handles, etc..."
                    className="w-full bg-slate-950 text-sm text-slate-100 placeholder-slate-500 rounded-xl p-3.5 border border-slate-800 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all leading-relaxed"
                  />
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                <Button variant="ghost" size="md" icon={RotateCcw} onClick={resetInput}>
                  Reset Fields
                </Button>

                <Button variant="primary" size="lg" type="submit" icon={Sparkles} className="shadow-indigo-500/25">
                  Start AI Risk Scan
                </Button>
              </div>
            </form>
          )}
        </Card>
      )}
    </div>
  )
}
