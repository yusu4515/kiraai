export interface User {
  id: string
  email: string
  full_name: string | null
  role: 'user' | 'agent'
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
  role: 'user' | 'agent'
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
