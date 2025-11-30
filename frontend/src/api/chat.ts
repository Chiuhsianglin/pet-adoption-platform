/**
 * Chat System API Client
 * 聊天系統 API 客戶端 - 使用 V2 WebSocket
 */
import apiClient from './client'
export { chatWebSocket } from '@/services/chatWebSocket'
export type { WebSocketMessage, MessageListener } from '@/services/chatWebSocket'

// ===== Types =====
export enum MessageType {
  TEXT = 'text',
  IMAGE = 'image',
  FILE = 'file',
  PET_CARD = 'pet_card'
}

export interface PetCardData {
  pet_id: number
  pet_name: string
  pet_species?: string
  pet_breed?: string
  pet_age?: number  // 保留舊欄位以向後相容
  pet_age_years?: number
  pet_age_months?: number
  pet_photo_url?: string
}

export interface ChatMessage {
  id: number
  room_id: number
  sender_id: number
  sender_name?: string
  sender_email?: string
  message_type: MessageType
  content?: string
  file_url?: string
  file_name?: string
  file_size?: number
  is_read: boolean
  created_at: string
  pet_card_data?: PetCardData
}

export interface ChatRoom {
  id: number
  user_id: number
  user_name?: string
  user_email?: string
  shelter_id: number
  shelter_name?: string
  shelter_email?: string
  pet_id: number
  pet_name?: string
  pet_photo_url?: string
  pet?: {
    id: number
    name: string
    species: string
    breed?: string
    age_years?: number
    age_months?: number
    gender?: string
    size?: string
    color?: string
    description?: string
    status?: string
    photos?: Array<{
      id: number
      file_url?: string
      file_key?: string
      is_primary?: boolean
    }>
  }
  last_message_at?: string
  created_at: string
  updated_at: string
  unread_count: number
  last_message?: string
  last_message_type?: MessageType
}

export interface ChatRoomCreateRequest {
  pet_id: number
}

export interface ChatMessageCreateRequest {
  message_type: MessageType
  content?: string
  file_url?: string
  file_name?: string
  file_size?: number
}

export interface ChatMessagesResponse {
  items: ChatMessage[]
  total: number
}

export interface ChatRoomListResponse {
  total: number
  rooms: ChatRoom[]
}

export interface FileUploadResponse {
  file_url: string
  file_name: string
  file_size: number
  message_type: MessageType
}

// ===== REST API Functions =====

export async function createOrGetChatRoom(petId: number): Promise<ChatRoom> {
  const response = await apiClient.post('/chat/rooms', { pet_id: petId })
  return response.data
}

export async function getChatRooms(): Promise<ChatRoom[]> {
  const response = await apiClient.get<ChatRoomListResponse>('/chat/rooms')
  return response.data.rooms
}

export async function getChatMessages(
  roomId: number,
  skip: number = 0,
  limit: number = 50
): Promise<ChatMessagesResponse> {
  const response = await apiClient.get(`/chat/rooms/${roomId}/messages`, {
    params: { skip, limit }
  })
  return response.data
}

export async function sendMessage(
  roomId: number,
  data: ChatMessageCreateRequest
): Promise<ChatMessage> {
  // V2 API 使用不同端點處理不同類型
  if (data.message_type === MessageType.TEXT) {
    const response = await apiClient.post(`/chat/rooms/${roomId}/messages/text`, {
      content: data.content
    })
    return response.data
  } else if (data.message_type === MessageType.IMAGE) {
    const response = await apiClient.post(`/chat/rooms/${roomId}/messages/image`, {
      image_url: data.file_url
    })
    return response.data
  } else if (data.message_type === MessageType.FILE) {
    const response = await apiClient.post(`/chat/rooms/${roomId}/messages/file`, {
      file_url: data.file_url,
      file_name: data.file_name,
      file_size: data.file_size
    })
    return response.data
  } else {
    throw new Error(`Unsupported message type: ${data.message_type}`)
  }
}

export async function uploadChatFile(
  roomId: number,
  file: File
): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  // 不手動設置 Content-Type，讓 axios 自動處理
  const response = await apiClient.post(`/chat/rooms/${roomId}/upload`, formData)
  return response.data
}

export async function markMessagesAsRead(roomId: number): Promise<void> {
  await apiClient.put(`/chat/rooms/${roomId}/read`)
}

// ===== Utility Functions =====

export function formatMessageTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) {
    return '剛剛'
  } else if (diffMins < 60) {
    return `${diffMins} 分鐘前`
  } else if (diffHours < 24) {
    return `${diffHours} 小時前`
  } else if (diffDays < 7) {
    return `${diffDays} 天前`
  } else {
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${month}/${day} ${hours}:${minutes}`
  }
}
