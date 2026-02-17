import api from './api'

export interface Job {
  id: string
  source: string
  external_id?: string
  title: string
  company_name?: string
  location?: string
  salary_min?: number
  salary_max?: number
  description?: string
  requirements?: string
  job_type?: string
  url?: string
  posted_at?: string
}

export interface JobSearchRequest {
  keyword: string
  location?: string
  salary_min?: number
  job_type?: string
  page?: number
  per_page?: number
}

export interface JobSearchResponse {
  jobs: Job[]
  total: number
  page: number
  per_page: number
}

export interface ApplicationData {
  id: string
  user_id: string
  job_id?: string
  status: string
  applied_at?: string
  notes?: string
  document_ids?: string[]
  cover_message?: string
  created_at: string
  updated_at: string
}

export const jobsService = {
  search: async (params: JobSearchRequest): Promise<JobSearchResponse> => {
    const { data } = await api.post('/jobs/search', params)
    return data
  },

  get: async (jobId: string): Promise<Job> => {
    const { data } = await api.get(`/jobs/${jobId}`)
    return data
  },

  seed: async (): Promise<{ count: number }> => {
    const { data } = await api.post('/jobs/seed')
    return data
  },
}

export const applicationsService = {
  list: async (): Promise<ApplicationData[]> => {
    const { data } = await api.get('/applications')
    return data
  },

  create: async (jobId: string, status = 'interested'): Promise<ApplicationData> => {
    const { data } = await api.post('/applications', { job_id: jobId, status })
    return data
  },

  update: async (id: string, updates: { status?: string; notes?: string }): Promise<ApplicationData> => {
    const { data } = await api.put(`/applications/${id}`, updates)
    return data
  },

  apply: async (id: string, documentIds: string[], coverMessage?: string): Promise<ApplicationData> => {
    const { data } = await api.post(`/applications/${id}/apply`, {
      document_ids: documentIds,
      cover_message: coverMessage,
    })
    return data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/applications/${id}`)
  },
}
