import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  timeout?: number
}

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<Notification[]>([])

  // Actions
  const addNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36)
    const newNotification: Notification = {
      ...notification,
      id,
      timeout: notification.timeout || 5000,
    }

    notifications.value.push(newNotification)

    // Auto remove after timeout
    if (newNotification.timeout) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.timeout)
    }

    return id
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message: string, timeout?: number) => {
    return addNotification({ type: 'success', message, timeout })
  }

  const error = (message: string, timeout?: number) => {
    return addNotification({ type: 'error', message, timeout })
  }

  const warning = (message: string, timeout?: number) => {
    return addNotification({ type: 'warning', message, timeout })
  }

  const info = (message: string, timeout?: number) => {
    return addNotification({ type: 'info', message, timeout })
  }

  return {
    // State
    notifications,

    // Actions
    addNotification,
    removeNotification,
    clearAll,

    // Convenience methods
    success,
    error,
    warning,
    info,
  }
})
