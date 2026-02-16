import api from './api'

export interface AgentProfile {
  id: string
  user_id: string
  company_name: string
  plan: string
  description?: string
  logo_url?: string
  website_url?: string
  is_approved: boolean
  created_at: string
  updated_at: string
}

export interface AgentDashboard {
  profile: AgentProfile
  stats: {
    page_views: number
    profile_views: number
    inquiries: number
    plan: string
  }
}

export const agentService = {
  getDashboard: async (): Promise<AgentDashboard> => {
    const { data } = await api.get('/api/agent/dashboard')
    return data
  },

  getProfile: async (): Promise<AgentProfile> => {
    const { data } = await api.get('/api/agent/profile')
    return data
  },

  updateProfile: async (updates: {
    company_name?: string
    description?: string
    logo_url?: string
    website_url?: string
  }): Promise<AgentProfile> => {
    const { data } = await api.put('/api/agent/profile', updates)
    return data
  },
}
