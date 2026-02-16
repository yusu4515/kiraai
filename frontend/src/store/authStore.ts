import { create } from 'zustand'
import type { User } from '../types/auth'
import { authService } from '../services/auth'

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  isAuthenticated: boolean

  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string, role: 'user' | 'agent') => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: authService.isAuthenticated(),

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      await authService.login({ email, password })
      const user = await authService.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      })
      throw err
    }
  },

  register: async (email: string, password: string, fullName: string, role: 'user' | 'agent') => {
    set({ isLoading: true, error: null })
    try {
      await authService.register({ email, password, full_name: fullName || undefined, role })
      // Auto-login after registration
      await authService.login({ email, password })
      const user = await authService.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      })
      throw err
    }
  },

  logout: () => {
    authService.logout()
    set({ user: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    if (!authService.isAuthenticated()) return
    set({ isLoading: true })
    try {
      const user = await authService.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      authService.logout()
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
