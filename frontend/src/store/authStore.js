// src/store/authStore.js
// Zustand store for authentication state with mock user session
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { MOCK_USER } from '../services/mockData'

const useAuthStore = create(
  persist(
    (set) => ({
      user: MOCK_USER,
      accessToken: 'demo_jwt_access_token_token_9921820',
      isAuthenticated: true,

      login: (email, password) => {
        const loggedUser = {
          ...MOCK_USER,
          email: email || MOCK_USER.email,
        }
        set({ user: loggedUser, accessToken: 'demo_jwt_token_active', isAuthenticated: true })
        return true
      },

      register: (userData) => {
        const newUser = {
          ...MOCK_USER,
          name: userData.name || 'New Member',
          email: userData.email,
          role: userData.role || 'Talent Researcher',
        }
        set({ user: newUser, accessToken: 'demo_jwt_token_registered', isAuthenticated: true })
        return true
      },

      logout: () => {
        set({ user: null, accessToken: null, isAuthenticated: false })
      },

      updateProfile: (updatedData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updatedData } : null,
        }))
      },

      regenerateApiKey: () => {
        set((state) => {
          if (!state.user) return state
          const newKey = 'fjd_live_key_' + Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
          return {
            user: { ...state.user, apiKey: newKey, apiKeyCreated: new Date().toISOString().split('T')[0] },
          }
        })
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
