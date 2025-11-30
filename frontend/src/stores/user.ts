import { defineStore } from 'pinia'
import { useAuthStore } from './auth'
import { computed } from 'vue'

/**
 * User store - provides a simple interface to access current user info
 * This is a wrapper around the auth store for convenience
 */
export const useUserStore = defineStore('user', () => {
  const authStore = useAuthStore()
  
  const currentUser = computed(() => authStore.user)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const userRole = computed(() => authStore.userRole)
  
  return {
    currentUser,
    isAuthenticated,
    userRole
  }
})
