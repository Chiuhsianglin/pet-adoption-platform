/**
 * User Settings API Client
 * MVP implementation for profile management and preferences
 */
import apiClient from './client'

// Types
export interface UserProfile {
  id: number
  email: string
  name: string 
  phone?: string
  address_line1?: string
  role: string
  is_active: boolean
  is_verified: boolean
}

export interface UserProfileUpdate {
  name?: string
  phone?: string
  bio?: string
  address_line1?: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

export interface NotificationPreferences {
  email_notifications: boolean
  application_updates: boolean
  chat_messages: boolean
  system_announcements: boolean
}

// API Functions

/**
 * Get current user's profile
 */
export async function getCurrentUserProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/users/me/profile')
  return response.data
}

/**
 * Update current user's profile
 */
export async function updateUserProfile(
  data: UserProfileUpdate
): Promise<UserProfile> {
  const response = await apiClient.put<UserProfile>('/users/me/profile', data)
  return response.data
}

/**
 * Upload user avatar
 */
export async function uploadUserAvatar(file: File): Promise<UserProfile> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UserProfile>(
    '/users/me/avatar',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  )
  return response.data
}

/**
 * Change user password
 */
export async function changePassword(
  data: PasswordChangeRequest
): Promise<{ message: string }> {
  const response = await apiClient.put<{ message: string }>(
    '/users/me/password',
    data
  )
  return response.data
}

/**
 * Get notification preferences
 */
export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const response = await apiClient.get<NotificationPreferences>(
    '/users/me/notification-preferences'
  )
  return response.data
}

/**
 * Update notification preferences
 */
export async function updateNotificationPreferences(
  preferences: NotificationPreferences
): Promise<NotificationPreferences> {
  const response = await apiClient.put<NotificationPreferences>(
    '/users/me/notification-preferences',
    preferences
  )
  return response.data
}
