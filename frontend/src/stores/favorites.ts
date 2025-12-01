import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

export const useFavoritesStore = defineStore('favorites', () => {
  // State: store full favorite objects when available
  // Each item shape expected: { id?, pet_id: number, user_id?: number, created_at?: string, ... }
  const favorites = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetched = ref<number | null>(null)
  const CACHE_DURATION = 5 * 60 * 1000 // 5分鐘快取

  // Getters
  const favoriteCount = computed(() => favorites.value.length)

  const authStore = useAuthStore()

  // 根據用戶 ID 生成 localStorage key
  const getStorageKey = () => {
    const userId = authStore.user?.id
    return userId ? `pet_favorites_${userId}` : 'pet_favorites_guest'
  }

  // Check if a pet is favorited; optional userId to ensure ownership
  const isFavorite = (petId: number, userId?: number) => {
    if (!favorites.value || favorites.value.length === 0) return false

    // If stored as simple number array, handle that
    if (typeof favorites.value[0] === 'number') {
      return favorites.value.includes(petId)
    }

    // Otherwise items are objects
    return favorites.value.some((f: any) => {
      if (!f) return false
      const matchesPet = f.pet_id === petId || f.petId === petId || f.id === petId
      if (!matchesPet) return false
      if (userId !== undefined && f.user_id !== undefined) {
        return f.user_id === userId
      }
      // If no userId provided, consider it a match on pet only
      return matchesPet
    })
  }

  const isFavoriteForCurrentUser = (petId: number) => {
    const userId = authStore.user?.id
    if (!userId) return false
    return isFavorite(petId, userId)
  }

  // Actions
  const loadFavorites = async (forceRefresh = false) => {
    const currentUserId = authStore.user?.id
    
    // 如果未登入，清空收藏並返回
    if (!currentUserId) {
      favorites.value = []
      return
    }
    
    // 檢查快取是否有效
    const now = Date.now()
    if (!forceRefresh && lastFetched.value && (now - lastFetched.value) < CACHE_DURATION) {
      console.log('✅ Using cached favorites data')
      return
    }

    // Try to load from localStorage first (使用用戶專屬的 key)
    const storageKey = getStorageKey()
    const stored = localStorage.getItem(storageKey)
    if (stored && !forceRefresh) {
      try {
        const parsed = JSON.parse(stored)
        // normalize: if array of numbers -> convert to objects with pet_id
        if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'number') {
          favorites.value = parsed.map((p: number) => ({ pet_id: p, user_id: currentUserId }))
        } else {
          favorites.value = parsed
        }
      } catch (e) {
        console.error('Failed to parse stored favorites:', e)
      }
    }

    // Then fetch from API
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/pets/favorites')

      // Support different response shapes
      if (response.data && Array.isArray(response.data)) {
        // API returned array directly
        favorites.value = response.data
      } else if (response.data && response.data.data && Array.isArray(response.data.data.items)) {
        favorites.value = response.data.data.items
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        favorites.value = response.data.data
      } else if (response.data && response.data.items && Array.isArray(response.data.items)) {
        favorites.value = response.data.items
      } else {
        // Fallback: keep existing local data
      }

      // Sync to localStorage and update last fetched time (使用用戶專屬的 key)
      localStorage.setItem(storageKey, JSON.stringify(favorites.value))
      lastFetched.value = Date.now()
    } catch (err: any) {
      // If not authenticated, just use localStorage
      if (err.response?.status !== 401) {
        error.value = err.response?.data?.detail || 'Failed to load favorites'
      }
    } finally {
      loading.value = false
    }
  }

  const addFavorite = async (petId: number) => {
    // If already favorited by current user, return
    const userId = authStore.user?.id
    if (userId && isFavorite(petId, userId)) {
      console.log('Pet already favorited, skipping')
      return
    }

    // Optimistic update: push a lightweight object
    const optimistic = { pet_id: petId, user_id: userId }
    favorites.value.push(optimistic)
    const storageKey = getStorageKey()
    localStorage.setItem(storageKey, JSON.stringify(favorites.value))
    console.log('✅ Optimistic update: added to favorites', petId)

    try {
      const resp = await api.post(`/pets/${petId}/favorite`)
      console.log('✅ Server response:', resp.data)
      // If API returns the created favorite object, replace optimistic entry
      if (resp.data) {
        // find and replace the optimistic by pet_id & maybe user_id
        const idx = favorites.value.findIndex((f: any) => f.pet_id === petId && (!f.id || f.id === resp.data.id || !resp.data.id))
        if (idx !== -1) favorites.value.splice(idx, 1, resp.data)
        localStorage.setItem(storageKey, JSON.stringify(favorites.value))
      }
      // 清除快取，強制下次重新載入
      lastFetched.value = null
    } catch (err: any) {
      console.error('❌ Failed to add favorite:', err.response?.data || err.message)
      // Rollback on error
      favorites.value = favorites.value.filter((f: any) => f.pet_id !== petId || (userId && f.user_id !== userId))
      localStorage.setItem(storageKey, JSON.stringify(favorites.value))

      if (err.response?.status !== 401) {
        error.value = err.response?.data?.detail || 'Failed to add favorite'
        throw err
      }
    }
  }

  const removeFavorite = async (petId: number) => {
    const userId = authStore.user?.id
    // If not favorited by current user, nothing to do
    if (userId && !isFavorite(petId, userId)) {
      console.log('Pet not favorited, skipping removal')
      return
    }

    // Optimistic update
    const previousFavorites = [...favorites.value]
    favorites.value = favorites.value.filter((f: any) => !(f.pet_id === petId && (!userId || f.user_id === userId)))
    const storageKey = getStorageKey()
    localStorage.setItem(storageKey, JSON.stringify(favorites.value))
    console.log('✅ Optimistic update: removed from favorites', petId)

    try {
      await api.delete(`/pets/${petId}/favorite`)
      console.log('✅ Server confirmed removal')
      // 清除快取，強制下次重新載入
      lastFetched.value = null
    } catch (err: any) {
      console.error('❌ Failed to remove favorite:', err.response?.data || err.message)
      // Rollback on error
      favorites.value = previousFavorites
      localStorage.setItem(storageKey, JSON.stringify(favorites.value))

      if (err.response?.status !== 401) {
        error.value = err.response?.data?.detail || 'Failed to remove favorite'
        throw err
      }
    }
  }

  const clearFavorites = () => {
    favorites.value = []
    // 清除所有可能的 localStorage keys
    const storageKey = getStorageKey()
    localStorage.removeItem(storageKey)
    localStorage.removeItem('pet_favorites') // 清除舊的通用 key
    lastFetched.value = null
  }

  return {
    // State
    favorites,
    loading,
    error,

    // Getters
    favoriteCount,
    isFavorite,
    isFavoriteForCurrentUser,

    // Actions
    loadFavorites,
    addFavorite,
    removeFavorite,
    clearFavorites
  }
})
