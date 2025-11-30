import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // State
  const loading = ref(false)
  const sidebarOpen = ref(true)
  const theme = ref<'light' | 'dark'>('light')
  const isMobile = ref(false)

  // Actions
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const closeSidebar = () => {
    sidebarOpen.value = false
  }

  const openSidebar = () => {
    sidebarOpen.value = true
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
  }

  const setMobile = (value: boolean) => {
    isMobile.value = value
    if (value) {
      sidebarOpen.value = false
    }
  }

  const initializeUI = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'light' || savedTheme === 'dark') {
      theme.value = savedTheme
    }

    // Check if mobile
    const checkMobile = () => {
      setMobile(window.innerWidth < 960)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
  }

  return {
    // State
    loading,
    sidebarOpen,
    theme,
    isMobile,

    // Actions
    setLoading,
    toggleSidebar,
    closeSidebar,
    openSidebar,
    toggleTheme,
    setTheme,
    setMobile,
    initializeUI,
  }
})
