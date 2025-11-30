export interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'shelter' | 'adopter'
  phone?: string
  address?: string
  is_active: boolean
  is_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface LoginCredentials {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterData {
  email: string
  name: string
  password: string
  role: 'shelter' | 'adopter'
  phone?: string
}

export interface TokenData {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenData
  message: string
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  loading: boolean
  error: string | null
}
