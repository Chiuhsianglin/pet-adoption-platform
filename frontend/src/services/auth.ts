import api from './api'
import type { LoginCredentials, RegisterData, User, AuthResponse, TokenData } from '@/types/auth'

export const authApi = {
  // Login - Backend returns AuthResponse directly
  async login(credentials: LoginCredentials) {
    return api.post<AuthResponse>('/auth/login', credentials)
  },

  // Register - Backend returns AuthResponse directly
  async register(data: RegisterData) {
    return api.post<AuthResponse>('/auth/register', data)
  },

  // Logout
  async logout() {
    return api.post<{ success: boolean }>('/auth/logout')
  },

  // Get current user
  async getCurrentUser() {
    return api.get<User>('/auth/me')
  },

  // Refresh token
  async refreshToken(refreshToken: string) {
    return api.post<{
      success: boolean
      data: TokenData
    }>('/auth/refresh', { refresh_token: refreshToken })
  },

  // Change password
  async changePassword(data: { old_password: string; new_password: string }) {
    return api.post<{ success: boolean }>('/auth/change-password', data)
  },

  // Request password reset
  async requestPasswordReset(email: string) {
    return api.post<{ success: boolean }>('/auth/forgot-password', { email })
  },

  // Reset password
  async resetPassword(data: { token: string; new_password: string }) {
    return api.post<{ success: boolean }>('/auth/reset-password', data)
  },

  // Verify email
  async verifyEmail(token: string) {
    return api.post<{ success: boolean }>('/auth/verify-email', { token })
  },

  // Resend verification email
  async resendVerificationEmail() {
    return api.post<{ success: boolean }>('/auth/resend-verification')
  },
}
