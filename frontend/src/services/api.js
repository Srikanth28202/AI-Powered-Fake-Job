// src/services/api.js
// Centralized Axios instance with environment base URL, token interceptors, and typed endpoints

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20000,
})

// ── Request Interceptor: Attach JWT Bearer Token ──────────────
api.interceptors.request.use(
  (config) => {
    // Check localStorage direct token or Zustand storage
    let token = localStorage.getItem('access_token')
    if (!token) {
      try {
        const storedAuth = localStorage.getItem('fakejob-auth-storage')
        if (storedAuth) {
          const parsed = JSON.parse(storedAuth)
          token = parsed?.state?.accessToken
        }
      } catch (e) {
        // Fallback silently
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response Interceptor: Format errors and handle 401 ───────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // For student demo, never force page redirects on 401
    return Promise.reject(error)
  },
)


// ── Typed API Endpoints ───────────────────────────────────────

export const authAPI = {
  register: (payload) => api.post('/auth/register', payload),
  login: (payload) => api.post('/auth/login', payload),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
}

export const jobsAPI = {
  analyzeJob: (payload) => api.post('/jobs/analyze', payload),
  getHistory: (params) => api.get('/jobs/history', { params }),
  getAnalysisById: (id) => api.get(`/jobs/${id}`),
}

export const analyticsAPI = {
  getOverview: (params) => api.get('/analytics/overview', { params }),
  getAdminOverview: (params) => api.get('/analytics/admin/overview', { params }),
}

export const adminAPI = {
  getUsers: (params) => api.get('/admin/users', { params }),
  updateUser: (userId, payload) => api.patch(`/admin/users/${userId}`, payload),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  deleteJobAnalysis: (analysisId) => api.delete(`/admin/jobs/${analysisId}`),
  getSuspiciousJobs: (params) => api.get('/admin/suspicious-jobs', { params }),
  getAuditLogs: (params) => api.get('/admin/audit-logs', { params }),
}

export const healthAPI = {
  checkHealth: () => api.get('/health'),
  checkDbHealth: () => api.get('/health/db'),
  checkFullHealth: () => api.get('/health/full'),
}

export default api

