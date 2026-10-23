// src/store/jobAnalysisStore.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { MOCK_HISTORICAL_JOBS, MOCK_JOB_PRESETS, analyzeJobMock } from '../services/mockData'

const initialForm = {
  title: '',
  company_name: '',
  location: '',
  department: '',
  salary_range: '',
  contact_email: '',
  company_url: '',
  description: '',
  requirements: '',
  benefits: '',
}

export const useJobAnalysisStore = create(
  persist(
    (set, get) => ({
      history: MOCK_HISTORICAL_JOBS,
      currentInput: initialForm,
      activeResult: null,
      isAnalyzing: false,
      analysisStep: '',
      scanProgress: 0,

      setInputField: (field, value) => {
        set((state) => ({
          currentInput: { ...state.currentInput, [field]: value },
        }))
      },

      setEntireInput: (newInput) => {
        set({ currentInput: { ...initialForm, ...newInput } })
      },

      resetInput: () => {
        set({ currentInput: initialForm })
      },

      loadPresetById: (presetId) => {
        const preset = MOCK_JOB_PRESETS.find((p) => p.id === presetId)
        if (preset) {
          const { id, ...formData } = preset
          set({ currentInput: formData })
        }
      },

      runAnalysis: async (jobData) => {
        const inputToAnalyze = jobData || get().currentInput
        set({ isAnalyzing: true, scanProgress: 10, analysisStep: 'Normalizing text & tokenizing job tokens...' })

        await new Promise((r) => setTimeout(r, 400))
        set({ scanProgress: 35, analysisStep: 'Cross-referencing enterprise DNS & WHOIS records...' })

        await new Promise((r) => setTimeout(r, 450))
        set({ scanProgress: 60, analysisStep: 'Benchmarking compensation disparity against BLS database...' })

        await new Promise((r) => setTimeout(r, 500))
        set({ scanProgress: 85, analysisStep: 'Extracting deception vectors & linguistic scam markers...' })

        await new Promise((r) => setTimeout(r, 400))
        set({ scanProgress: 100, analysisStep: 'Generating calibrated ensemble risk evaluation...' })

        const result = analyzeJobMock(inputToAnalyze)

        await new Promise((r) => setTimeout(r, 250))
        set((state) => {
          // Put new result at top of history
          const historyEntry = {
            id: result.id,
            title: result.title,
            company: result.company,
            location: result.location,
            riskLevel: result.riskLevel,
            riskScore: result.riskScore,
            fraudProbability: result.fraudProbability,
            createdAt: result.createdAt,
            category: result.category,
            keyFlags: result.flags.map((f) => f.title),
            salary: result.salary,
            status: result.status,
            fullResult: result,
          }

          return {
            isAnalyzing: false,
            scanProgress: 0,
            analysisStep: '',
            activeResult: result,
            history: [historyEntry, ...state.history],
          }
        })

        return result
      },

      deleteFromHistory: (jobId) => {
        set((state) => ({
          history: state.history.filter((item) => item.id !== jobId),
          activeResult: state.activeResult?.id === jobId ? null : state.activeResult,
        }))
      },

      clearAllHistory: () => {
        set({ history: [] })
      },

      setActiveResult: (result) => {
        set({ activeResult: result })
      },
    }),
    {
      name: 'fakejob-analysis-store',
      partialize: (state) => ({
        history: state.history,
      }),
    },
  ),
)
