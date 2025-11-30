/**
 * Notifications API Client (MVP version)
 */
import apiClient from './client'

// Types
export interface Notification {
  id: number
  user_id: number
  title: string
  message: string
  is_read: boolean
  notification_type?: string | null
  link?: string | null
  created_at: string
}

export interface NotificationListResponse {
  total: number
  unread_count: number
  notifications: Notification[]
}

export interface MarkReadRequest {
  notification_ids: number[]
}

// API Functions
export async function getUserNotifications(
  skip: number = 0,
  limit: number = 20,
  unreadOnly: boolean = false
): Promise<NotificationListResponse> {
  const response = await apiClient.get('/notifications/', {
    params: { skip, limit, unread_only: unreadOnly }
  })
  return response.data
}

export async function getUnreadCount(): Promise<{ unread_count: number }> {
  const response = await apiClient.get('/notifications/unread-count')
  return response.data
}

export async function markNotificationAsRead(
  notificationId: number
): Promise<void> {
  await apiClient.put(`/notifications/${notificationId}/read`)
}

export async function markNotificationsAsRead(
  notificationIds: number[]
): Promise<void> {
  await apiClient.post('/notifications/mark-read', {
    notification_ids: notificationIds
  })
}

export async function markAllAsRead(): Promise<void> {
  await apiClient.post('/notifications/mark-all-read')
}

export async function deleteNotification(
  notificationId: number
): Promise<void> {
  await apiClient.delete(`/notifications/${notificationId}`)
}

// Utility Functions
export function getNotificationIcon(type: string): string {
  const icons: Record<string, string> = {
    APPLICATION_STATUS: 'mdi-file-document',
    MESSAGE: 'mdi-message',
    SYSTEM: 'mdi-information',
    REMINDER: 'mdi-bell',
    REVIEW_STATUS: 'mdi-check-circle'
  }
  return icons[type] || 'mdi-bell'
}

export function getNotificationColor(type: string): string {
  const colors: Record<string, string> = {
    APPLICATION_STATUS: 'primary',
    MESSAGE: 'success',
    SYSTEM: 'info',
    REMINDER: 'warning',
    REVIEW_STATUS: 'success'
  }
  return colors[type] || 'grey'
}

export function formatNotificationTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '剛剛'
  if (diffMins < 60) return `${diffMins}分鐘前`
  if (diffHours < 24) return `${diffHours}小時前`
  if (diffDays < 7) return `${diffDays}天前`

  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
