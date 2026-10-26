// src/store/authStore.js
// Zustand store for authentication state connected to FastAPI backend
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authAPI } from '../services/api'

const DEFAULT_STUDENT_USER = {
  id: 'usr-student-01',
  name: 'Srikanth',
  full_name: 'Srikanth',
  email: 'student@example.com',
  role: 'admin',
  title: 'Project Lead',
  is_active: true,
  scansUsed: 14,
  scansLimit: 100,
}

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: DEFAULT_STUDENT_USER,
      accessToken: 'demo-student-token-2026',
      isAuthenticated: true,
      isLoading: false,
      authError: null,


      login: async (email, password) => {
        set({ isLoading: true, authError: null })
        try {
          const res = await authAPI.login({ email, password })
          const { access_token, user } = res.data
          localStorage.setItem('access_token', access_token)
          set({
            user,
            accessToken: access_token,
            isAuthenticated: true,
            isLoading: false,
            authError: null,
          })
          return { success: true, user }
        } catch (error) {
          const msg =
            error.response?.data?.error?.message ||
            error.response?.data?.detail ||
            'Invalid email or password.'
          set({ isLoading: false, authError: msg })
          return { success: false, error: msg }
        }
      },

      register: async (userData) => {
        set({ isLoading: true, authError: null })
        try {
          const regRes = await authAPI.register({
            email: userData.email,
            password: userData.password,
            full_name: userData.full_name || userData.name,
          })

          // Automatically authenticate user after successful registration
          const loginRes = await authAPI.login({
            email: userData.email,
            password: userData.password,
          })

          const { access_token, user } = loginRes.data
          localStorage.setItem('access_token', access_token)
          set({
            user,
            accessToken: access_token,
            isAuthenticated: true,
            isLoading: false,
            authError: null,
          })
          return { success: true, user }
        } catch (error) {
          const msg =
            error.response?.data?.error?.message ||
            error.response?.data?.detail ||
            'Registration failed. Please check your credentials.'
          set({ isLoading: false, authError: msg })
          return { success: false, error: msg }
        }
      },

      logout: async () => {
        try {
          if (get().accessToken) {
            await authAPI.logout()
          }
        } catch (e) {
          // Ignore network errors on logout
        } finally {
          localStorage.removeItem('access_token')
          set({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            authError: null,
          })
        }
      },

      fetchCurrentUser: async () => {
        try {
          const res = await authAPI.getMe()
          if (res?.data) {
            set({ user: res.data, isAuthenticated: true })
            return res.data
          }
        } catch (error) {
          // Keep active default user state intact across all machines
        }
        return get().user
      },

      clearError: () => set({ authError: null }),

      updateProfile: (updatedData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updatedData } : null,
        }))
      },
    }),
    {
      name: 'fakejob-auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)

export default useAuthStore
