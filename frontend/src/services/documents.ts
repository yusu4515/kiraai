import api from './api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface DocumentResponse {
  id: string
  document_type: string
  title: string | null
  content_html: string | null
  generated_at: string
}

export const documentsService = {
  async generate(documentType: 'resume' | 'career_sheet'): Promise<DocumentResponse> {
    const response = await api.post<DocumentResponse>('/documents/generate', {
      document_type: documentType,
    })
    return response.data
  },

  async list(): Promise<DocumentResponse[]> {
    const response = await api.get<DocumentResponse[]>('/documents')
    return response.data
  },

  async get(documentId: string): Promise<DocumentResponse> {
    const response = await api.get<DocumentResponse>(`/documents/${documentId}`)
    return response.data
  },

  getPdfUrl(documentId: string): string {
    const token = localStorage.getItem('access_token')
    return `${API_BASE_URL}/api/documents/${documentId}/pdf?token=${token}`
  },

  async downloadPdf(documentId: string, filename: string): Promise<void> {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/pdf`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'document.pdf'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
  },

  async downloadDocx(documentId: string, filename: string): Promise<void> {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/docx`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'document.docx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    a.remove()
  },
}
