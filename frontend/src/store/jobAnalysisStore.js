// src/store/jobAnalysisStore.js
// Store for job analysis, history management, and backend inference integration
import { create } from 'zustand'
import { jobsAPI } from '../services/api'
import { MOCK_JOB_PRESETS } from '../services/mockData'

const initialForm = {
  title: '',
  company_name: '',
  location: '',
  salary_range: '',
  contact_email: '',
  company_url: '',
  description: '',
  company_profile: '',
  required_experience: '',
  required_education: '',
  industry: '',
  has_company_logo: false,
  has_questions: false,
  telecommuting: false,
}

export const useJobAnalysisStore = create((set, get) => ({
  history: [],
  historyTotal: 0,
  historyPage: 1,
  historyTotalPages: 1,
  isLoadingHistory: false,

  currentInput: initialForm,
  activeResult: null,
  isAnalyzing: false,
  analysisStep: '',
  scanProgress: 0,
  analysisError: null,

  setInputField: (field, value) => {
    set((state) => ({
      currentInput: { ...state.currentInput, [field]: value },
    }))
  },

  setEntireInput: (newInput) => {
    set({ currentInput: { ...initialForm, ...newInput } })
  },

  resetInput: () => {
    set({ currentInput: initialForm, activeResult: null, analysisError: null })
  },

  loadPresetById: (presetId) => {
    const preset = MOCK_JOB_PRESETS.find((p) => p.id === presetId)
    if (preset) {
      const { id, ...formData } = preset
      set({ currentInput: { ...initialForm, ...formData }, analysisError: null })
    }
  },

  fetchHistory: async (page = 1, pageSize = 20) => {
    set({ isLoadingHistory: true })
    try {
      const res = await jobsAPI.getHistory({ page, page_size: pageSize })
      const data = res.data
      set({
        history: data.items || [],
        historyTotal: data.total || 0,
        historyPage: data.page || 1,
        historyTotalPages: data.total_pages || 1,
        isLoadingHistory: false,
      })
      return data
    } catch (error) {
      set({ isLoadingHistory: false })
      return null
    }
  },

  fetchAnalysisById: async (analysisId) => {
    try {
      const res = await jobsAPI.getAnalysisById(analysisId)
      set({ activeResult: res.data })
      return res.data
    } catch (error) {
      return null
    }
  },

  runAnalysis: async (jobData) => {
    const inputToAnalyze = jobData || get().currentInput
    set({
      isAnalyzing: true,
      analysisError: null,
      scanProgress: 15,
      analysisStep: 'Tokenizing job posting and running TF-IDF vectorization...',
    })

    try {
      // Step progression animation
      setTimeout(() => {
        if (get().isAnalyzing) set({ scanProgress: 45, analysisStep: 'Computing calibrated fraud probability & model weights...' })
      }, 300)

      setTimeout(() => {
        if (get().isAnalyzing) set({ scanProgress: 75, analysisStep: 'Evaluating security heuristic rules & scam indicators...' })
      }, 600)

      const payload = {
        title: inputToAnalyze.title,
        description: inputToAnalyze.description,
        company_name: inputToAnalyze.company_name || null,
        company_profile: inputToAnalyze.company_profile || null,
        company_url: inputToAnalyze.company_url || null,
        contact_email: inputToAnalyze.contact_email || null,
        location: inputToAnalyze.location || null,
        salary_range: inputToAnalyze.salary_range || null,
        employment_type: inputToAnalyze.employment_type || null,
        required_experience: inputToAnalyze.required_experience || null,
        required_education: inputToAnalyze.required_education || null,
        industry: inputToAnalyze.industry || null,
        has_company_logo: Boolean(inputToAnalyze.has_company_logo),
        has_questions: Boolean(inputToAnalyze.has_questions),
        telecommuting: Boolean(inputToAnalyze.telecommuting),
      }

      const response = await jobsAPI.analyzeJob(payload)
      const result = response.data

      set({
        isAnalyzing: false,
        scanProgress: 100,
        analysisStep: 'Analysis Complete',
        activeResult: result,
        analysisError: null,
      })

      // Refresh history silently
      get().fetchHistory(1)

      return result
    } catch (error) {
      const errorMsg =
        error.response?.data?.error?.message ||
        error.response?.data?.detail?.[0]?.msg ||
        error.message ||
        'Failed to complete job risk analysis.'
      set({
        isAnalyzing: false,
        scanProgress: 0,
        analysisStep: '',
        analysisError: errorMsg,
      })
      throw new Error(errorMsg)
    }
  },

  setActiveResult: (result) => {
    set({ activeResult: result })
  },
}))
