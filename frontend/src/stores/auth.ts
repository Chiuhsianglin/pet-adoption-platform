import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData } from '@/types/auth'
import { authApi } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const isAdmin = computed(() => userRole.value === 'admin')
  const isShelter = computed(() => userRole.value === 'shelter')
  const isAdopter = computed(() => userRole.value === 'adopter')

  // Actions
  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(credentials)
      
      // Backend directly returns AuthResponse, not wrapped in success/data
      const authData = response.data
      
      // Handle tokens object
      if (authData.tokens && authData.user) {
        token.value = authData.tokens.access_token
        refreshToken.value = authData.tokens.refresh_token
        user.value = authData.user
        
        // Save to localStorage
        localStorage.setItem('auth_token', token.value)
        localStorage.setItem('refresh_token', refreshToken.value)
        localStorage.setItem('user', JSON.stringify(user.value))
        
        return true
      }
      
      error.value = 'Login failed: Invalid response format'
      return false
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Network error'
      console.error('Login error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authApi.register(data)
      console.log('📩 後端回傳資料:', response.data)
      
      // Backend directly returns AuthResponse, not wrapped in success/data
      const authData = response.data
      
      // Check if registration was successful
      if (authData.tokens && authData.user) {
        // Registration successful - DO NOT auto-login
        // User will be redirected to login page
        return true
      }
      
      error.value = 'Registration failed: Invalid response format'
      return false
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.response?.data?.message || 'Network error'
      console.error('Registration error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (err) {
      // Ignore logout errors
      console.error('Logout error:', err)
    } finally {
      // Clear state
      user.value = null
      token.value = null
      refreshToken.value = null
      
      // Clear localStorage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return
    
    loading.value = true
    try {
      const response = await authApi.getCurrentUser()
      
      console.log('🔍 API response from /auth/me:', response.data)
      
      // Backend returns UserResponse directly, not wrapped in success/data
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      
      console.log('🔍 User updated in store:', user.value)
    } catch (err) {
      console.error('Failed to fetch user:', err)
      // Token might be invalid, logout
      await logout()
    } finally {
      loading.value = false
    }
  }

  const updateToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
      
      // Fetch fresh user data
      fetchCurrentUser()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isShelter,
    isAdopter,
    
    // Actions
    login,
    register,
    logout,
    fetchCurrentUser,
    updateToken,
    initializeAuth,
  }
})
