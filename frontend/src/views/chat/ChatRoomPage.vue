<template>
  <v-app>
    <v-container fluid class="chat-room-page pa-0">
      <v-row no-gutters class="chat-layout">
        <!-- 左側：聊天列表 -->
        <v-col cols="12" md="4" lg="3" class="chat-list-sidebar">
          <v-card flat tile height="100vh" class="d-flex flex-column">
            <!-- 聊天列表 Header -->
            <v-card-title class="chat-list-header bg-primary text-white d-flex align-center" >
                <v-btn icon size="small" @click="$router.push('/chat')" class="me-4 mr-2 bg-primary text-white">
                  <v-icon>mdi-arrow-left</v-icon>
                </v-btn>
              聊天列表
            </v-card-title>

            <v-divider />

            <!-- 聊天室列表 -->
            <v-card-text class="pa-0 flex-grow-1 overflow-y-auto">
              <!-- Loading Skeleton -->
              <v-list v-if="loadingRooms" lines="two">
                <v-list-item v-for="i in 4" :key="`skeleton-${i}`">
                  <template v-slot:prepend>
                    <v-skeleton-loader type="avatar" />
                  </template>
                  <v-list-item-title>
                    <v-skeleton-loader type="text" width="70%" />
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <v-skeleton-loader type="text" width="90%" />
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>

              <v-list v-if="!loadingRooms && chatRooms.length > 0" lines="two">
                <v-list-item
                  v-for="room in chatRooms"
                  :key="room.id"
                  :active="room.id === roomId"
                  @click="switchRoom(room.id)"
                  class="chat-list-item"
                >
                  <template v-slot:prepend>
                    <v-avatar size="48" color="grey-lighten-2">
                      <v-img
                        v-if="room.pet_photo_url"
                        :src="room.pet_photo_url"
                        :lazy-src="room.pet_photo_url"
                        cover
                      >
                        <template v-slot:placeholder>
                          <v-skeleton-loader type="avatar" />
                        </template>
                      </v-img>
                      <v-icon v-else size="24">mdi-paw</v-icon>
                    </v-avatar>
                  </template>

                  <v-list-item-title class="font-weight-medium">
                    {{ getChatRoomTitle(room) }}
                  </v-list-item-title>

                  <v-list-item-subtitle class="text-truncate">
                    <!-- 只在非當前聊天室時顯示最後訊息 -->
                    <template v-if="room.id !== roomId">
                      {{ room.last_message || '尚無訊息' }}
                    </template>
                    <template v-else>
                      <span class="text-grey-lighten-1"></span>
                    </template>
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <!-- 只在非當前聊天室時顯示未讀數量 -->
                    <v-badge
                      v-if="room.id !== roomId && room.unread_count > 0"
                      :content="room.unread_count"
                      color="error"
                    />
                  </template>
                </v-list-item>
              </v-list>

              <!-- 空狀態 -->
              <div v-if="!loadingRooms && chatRooms.length === 0" class="text-center pa-8">
                <v-icon size="64" color="grey-lighten-1">mdi-message-outline</v-icon>
                <div class="text-body-2 text-grey mt-2">尚無聊天記錄</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- 右側：聊天內容 -->
        <v-col cols="12" md="8" lg="9" class="chat-content-area">
          <v-card flat tile height="100vh" class="d-flex flex-column">
            <!-- Header -->
            <v-card-title class="chat-content-header d-flex align-center justify-space-between">

              <v-btn icon size="small" @click="$router.push('/chat')" class="mr-2 d-md-none">
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>

              <span>{{ roomTitle }}</span>

              <!-- WebSocket 連接狀態 -->
              <!--v-chip
                :color="chatWebSocket.connected.value ? 'success' : 'error'"
                size="small"
                variant="flat"
              >
                <v-icon start size="small">
                  {{ chatWebSocket.connected.value ? 'mdi-wifi' : 'mdi-wifi-off' }}
                </v-icon>
              </v-chip-->
              
              <v-btn icon size="small" @click="handleClose">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>

            <v-divider />

            <!-- 訊息列表容器 -->
            <div
              ref="messageContainer"
              class="message-container flex-grow-1"
              @scroll="handleScroll"
            >
        <!-- 載入更多按鈕 -->
        <div v-if="hasMore && !loadingMore" class="text-center py-2">
          <v-btn
            size="small"
            variant="text"
            @click="loadMoreMessages"
          >
            載入更多訊息
          </v-btn>
        </div>

        <v-progress-circular
          v-if="loadingMore"
          indeterminate
          size="24"
          class="mx-auto d-block my-2"
        />

        <!-- 寵物卡片（最上方） -->
        <v-card
          v-if="petCardData"
          class="pet-card ma-4"
          elevation="2"
        >
          <v-card-text class="d-flex align-center">
            <v-avatar size="80" class="mr-4">
              <v-img
                v-if="petPhotoUrl"
                :src="petPhotoUrl"
                :lazy-src="petPhotoUrl"
                cover
              >
                <template v-slot:placeholder>
                  <v-skeleton-loader type="avatar" />
                </template>
              </v-img>
              <v-icon v-else size="48">mdi-paw</v-icon>
            </v-avatar>

            <div class="flex-grow-1">
              <div class="text-h6">{{ petCardData.pet_name }}</div>
              <div class="text-body-2 text-grey">
                <v-icon size="small" class="mr-1">mdi-paw</v-icon>
                {{ petCardData.pet_species || '未知' }}
                {{ petCardData.pet_breed ? ` · ${petCardData.pet_breed}` : '' }}
              </div>
              <div v-if="formatPetAge(petCardData)" class="text-body-2 text-grey">
                <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
                {{ formatPetAge(petCardData) }}
              </div>
            </div>

            <v-btn
              icon="mdi-open-in-new"
              size="small"
              variant="text"
              @click="goToPetDetail"
            />
          </v-card-text>
        </v-card>

        <!-- 訊息列表 -->
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'message-item',
            message.sender_id === currentUserId ? 'message-sent' : 'message-received'
          ]"
        >
          <!-- 寵物卡片訊息 -->
          <div v-if="message.message_type === 'pet_card'" class="message-bubble pet-card-message">
            <v-icon class="mr-2">mdi-card-account-details</v-icon>
            {{ message.content }}
          </div>

          <!-- 圖片訊息 -->
          <div v-else-if="message.message_type === 'image'" class="message-bubble image-message">
            <v-img
              :src="getFullImageUrl(message.file_url)"
              max-width="300"
              min-height="100"
              aspect-ratio="1"
              cover
              @click="openImagePreview(getFullImageUrl(message.file_url))"
              @error="handleImageError"
              class="rounded cursor-pointer"
            >
              <template v-slot:placeholder>
                <v-row
                  class="fill-height ma-0"
                  align="center"
                  justify="center"
                >
                  <v-progress-circular
                    indeterminate
                    color="grey-lighten-5"
                  />
                </v-row>
              </template>
              <template v-slot:error>
                <v-row
                  class="fill-height ma-0"
                  align="center"
                  justify="center"
                >
                  <div class="text-center">
                    <v-icon size="48" color="error">mdi-image-broken</v-icon>
                    <div class="text-caption mt-2">圖片載入失敗</div>
                  </div>
                </v-row>
              </template>
            </v-img>
            <div class="text-caption mt-1">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>
          </div>

          <!-- 檔案訊息 -->
          <div v-else-if="message.message_type === 'file'" class="message-bubble file-message">
            <v-icon class="mr-2">mdi-file</v-icon>
            <div class="flex-grow-1">
              <div class="text-subtitle-2">{{ message.file_name }}</div>
              <div class="text-caption text-grey">
                {{ formatFileSize(message.file_size) }}
              </div>
            </div>
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="downloadFile(getFullImageUrl(message.file_url), message.file_name!)"
            />
          </div>

          <!-- 文字訊息 -->
          <div v-else class="message-bubble text-message">
            {{ message.content }}
          </div>

          <!-- 時間戳記 -->
          <div class="message-time">
            {{ formatMessageTime(message.created_at) }}
          </div>
        </div>

        <!-- 捲動到底部按鈕 -->
        <v-fab
          v-if="showScrollToBottom"
          icon="mdi-chevron-down"
          size="small"
          color="primary"
          location="bottom end"
          class="scroll-to-bottom-btn"
          @click="scrollToBottom"
        />
      </div>

      <!-- 輸入區域 -->
      <div class="input-container">
        <input
          ref="fileInput"
          type="file"
          accept="image/*,.pdf,.doc,.docx,.txt"
          style="display: none"
          @change="handleFileSelected"
        />

        <v-btn
          icon="mdi-paperclip"
          variant="text"
          @click="($refs.fileInput as HTMLInputElement).click()"
        />

        <v-textarea
          v-model="messageInput"
          placeholder="輸入訊息..."
          rows="1"
          auto-grow
          max-rows="4"
          variant="outlined"
          density="compact"
          hide-details
          class="flex-grow-1 mx-2"
          @keydown.enter.exact.prevent="sendTextMessage"
        />

        <v-btn
          icon="mdi-send"
          color="primary"
          :disabled="!messageInput.trim() && !uploadingFile"
          :loading="sending"
          @click="sendTextMessage"
        />
      </div>

      <!-- 檔案上傳進度 -->
      <v-dialog v-model="uploadingFile" persistent max-width="300">
        <v-card>
          <v-card-text class="text-center py-6">
            <v-progress-circular
              indeterminate
              color="primary"
              size="48"
            />
            <div class="mt-4">上傳檔案中...</div>
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- 圖片預覽 -->
      <v-dialog v-model="imagePreview" max-width="800">
        <v-card>
          <v-img :src="previewImageUrl" />
          <v-card-actions>
            <v-spacer />
            <v-btn @click="imagePreview = false">關閉</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Error -->
      <v-snackbar v-model="showError" color="error" timeout="3000">
        {{ errorMessage }}
      </v-snackbar>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  getChatMessages,
  getChatRooms,
  sendMessage,
  uploadChatFile,
  markMessagesAsRead,
  chatWebSocket,
  type ChatMessage,
  type ChatRoom,
  type WebSocketMessage,
  type PetCardData,
  MessageType as MessageTypeEnum
} from '@/api/chat'
import apiClient from '@/api/client'
import { formatAge, calculateAge } from '@/utils/ageCalculator'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const roomId = ref<number>(parseInt(route.params.id as string))
const messages = ref<ChatMessage[]>([])
const chatRooms = ref<ChatRoom[]>([])
const messageInput = ref('')
const loading = ref(true)
const loadingRooms = ref(true)
const sending = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const limit = 50
const showScrollToBottom = ref(false)
const messageContainer = ref<HTMLElement | null>(null)
const uploadingFile = ref(false)
const imagePreview = ref(false)
const previewImageUrl = ref('')
const showError = ref(false)
const errorMessage = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// 寵物卡片資料（從第一則 pet_card 訊息提取）
const petCardData = ref<PetCardData | null>(null)

// 寵物照片完整 URL（後端已返回完整 URL）
const petPhotoUrl = computed(() => petCardData.value?.pet_photo_url || null)

/**
 * 取得完整的圖片 URL（後端已返回完整 URL）
 */
function getFullImageUrl(url: string | undefined): string {
  console.log('🖼️ Image URL:', url)
  return url || ''
}

/**
 * 處理圖片載入錯誤
 */
function handleImageError(event: unknown) {
  console.error('❌ Image load error:', event)
}

/**
 * 載入聊天室列表
 */
async function loadChatRooms() {
  try {
    const rooms = await getChatRooms()
    chatRooms.value = rooms
  } catch (err) {
    console.error('❌ Failed to load chat rooms:', err)
  } finally {
    loadingRooms.value = false
  }
}

/**
 * 切換聊天室
 */
function switchRoom(newRoomId: number) {
  router.push(`/chat/${newRoomId}`)
}

/**
 * 獲取聊天室標題
 */
function getChatRoomTitle(room: ChatRoom): string {
  const currentUser = authStore.user
  if (!currentUser) return room.pet_name || '聊天室'
  
  const isShelter = currentUser.id === room.shelter_id
  
  if (isShelter) {
    // Shelter 看到：用戶名稱 + 寵物名稱
    return `${room.user_name || '用戶'} - ${room.pet_name || '寵物'}`
  } else {
    // 使用者看到：寵物名稱
    return room.pet_name || '寵物'
  }
}

// 當前用戶 ID
const currentUserId = computed(() => authStore.user?.id)

// 聊天室標題（根據當前聊天室動態生成）
const roomTitle = computed(() => {
  const currentRoom = chatRooms.value.find(r => r.id === roomId.value)
  if (currentRoom) {
    return getChatRoomTitle(currentRoom)
  }
  return (route.query.title as string) || '聊天室'
})

// 預填文字（首次進入時）
const prefillText = computed(() => route.query.prefill as string)

// Methods

/**
 * 載入訊息歷史
 */
async function loadMessages(append: boolean = false) {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    // 重置寵物卡片，避免顯示舊資料
    petCardData.value = null
  }

  try {
    const response = await getChatMessages(roomId.value, skip.value, limit)
    
    // 反轉訊息順序（最舊的在上）
    const newMessages = response.items.reverse()
    
    if (append) {
      // 追加到開頭
      messages.value = [...newMessages, ...messages.value]
    } else {
      messages.value = newMessages
      
      // 從聊天室資料中提取寵物資訊（而不是從訊息）
      console.log('🔍 Looking for room in chatRooms:', roomId.value)
      console.log('📋 Available chatRooms:', chatRooms.value.map(r => ({ id: r.id, pet_name: r.pet_name, has_pet: !!r.pet })))
      
      const currentRoom = chatRooms.value.find(r => r.id === roomId.value)
      console.log('📦 Current room found:', currentRoom)
      
      if (currentRoom?.pet) {
        console.log('🐕 Pet data found:', currentRoom.pet)
        // 從 chatRoom.pet 轉換為 PetCardData 格式
        const pet = currentRoom.pet as any
        petCardData.value = {
          pet_id: pet.id,
          pet_name: pet.name,
          pet_species: pet.species,
          pet_breed: pet.breed,
          pet_age_years: pet.age_years,
          pet_age_months: pet.age_months,
          pet_photo_url: pet.photos?.[0]?.file_url || null
        }
        console.log('✅ Pet card data set:', petCardData.value)
      } else {
        console.log('❌ No pet data found in room')
        // 如果聊天室列表中沒有當前房間，嘗試單獨獲取
        if (!currentRoom) {
          console.log('⚠️ Room not in list, fetching room details...')
          try {
            const roomData = await apiClient.get(`/chat/rooms/${roomId.value}`)
            console.log('📦 Fetched room data:', roomData.data)
            if (roomData.data?.pet) {
              const pet = roomData.data.pet as any
              petCardData.value = {
                pet_id: pet.id,
                pet_name: pet.name,
                pet_species: pet.species,
                pet_breed: pet.breed,
                pet_age_years: pet.age_years,
                pet_age_months: pet.age_months,
                pet_photo_url: pet.photos?.[0]?.file_url || null
              }
              console.log('✅ Pet card data set from fetched room:', petCardData.value)
            }
          } catch (err) {
            console.error('❌ Failed to fetch room details:', err)
          }
        }
      }
      
      // 滾動到底部
      await nextTick()
      scrollToBottom(false)
    }
    
    // 判斷是否還有更多訊息
    hasMore.value = response.items.length === limit
    
    // 標記訊息為已讀（只在初次載入時，即 append=false）
    if (!append && response.items.length > 0) {
      try {
        await markMessagesAsRead(roomId.value)
        console.log('✅ Marked messages as read in room', roomId.value)
      } catch (err) {
        console.error('❌ Failed to mark messages as read:', err)
        // 不影響主流程，靜默失敗
      }
    }
    
  } catch (err: any) {
    console.error('❌ Failed to load messages:', err)
    showErrorMessage('載入訊息失敗')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

/**
 * 載入更多訊息
 */
async function loadMoreMessages() {
  if (!hasMore.value || loadingMore.value) return
  
  skip.value += limit
  await loadMessages(true)
}

/**
 * 發送文字訊息
 */
async function sendTextMessage() {
  const content = messageInput.value.trim()
  if (!content || sending.value) return

  sending.value = true

  try {
    const newMessage = await sendMessage(roomId.value, {
      content,
      message_type: MessageTypeEnum.TEXT
    })

    // 添加到訊息列表
    messages.value.push(newMessage)
    messageInput.value = ''

    // 滾動到底部
    await nextTick()
    scrollToBottom()

  } catch (err: any) {
    console.error('❌ Failed to send message:', err)
    showErrorMessage('發送訊息失敗')
  } finally {
    sending.value = false
  }
}

/**
 * 處理檔案選擇
 */
async function handleFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const files = input.files
  
  if (!files || files.length === 0) return

  const file = files[0]
  uploadingFile.value = true

  try {
    // 上傳檔案到 S3
    const uploadResult = await uploadChatFile(roomId.value, file)

    // 發送檔案訊息
    const newMessage = await sendMessage(roomId.value, {
      message_type: uploadResult.message_type,
      file_url: uploadResult.file_url,
      file_name: uploadResult.file_name,
      file_size: uploadResult.file_size
    })

    // 添加到訊息列表
    messages.value.push(newMessage)

    // 滾動到底部
    await nextTick()
    scrollToBottom()

  } catch (err: any) {
    console.error('❌ Failed to upload file:', err)
    showErrorMessage(err.response?.data?.detail || '檔案上傳失敗')
  } finally {
    uploadingFile.value = false
    // 重置檔案輸入
    const input = fileInput.value as HTMLInputElement
    if (input) input.value = ''
  }
}

/**
 * 滾動到底部
 */
function scrollToBottom(smooth: boolean = true) {
  if (!messageContainer.value) return

  messageContainer.value.scrollTo({
    top: messageContainer.value.scrollHeight,
    behavior: smooth ? 'smooth' : 'auto'
  })

  showScrollToBottom.value = false
}

/**
 * 處理滾動事件
 */
function handleScroll() {
  if (!messageContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messageContainer.value
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight

  // 顯示/隱藏「滾動到底部」按鈕
  showScrollToBottom.value = distanceFromBottom > 200
}

/**
 * 格式化訊息時間（轉換為台灣時區 UTC+8）
 */
function formatMessageTime(timestamp: string): string {
  // 解析 UTC 時間並轉換為台灣時區
  const utcDate = new Date(timestamp)
  
  // 使用 toLocaleString 轉換為台灣時區
  const options: Intl.DateTimeFormatOptions = {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }
  
  const formatter = new Intl.DateTimeFormat('zh-TW', options)
  const parts = formatter.formatToParts(utcDate)
  
  const year = parts.find(p => p.type === 'year')?.value
  const month = parts.find(p => p.type === 'month')?.value
  const day = parts.find(p => p.type === 'day')?.value
  const hour = parseInt(parts.find(p => p.type === 'hour')?.value || '0')
  const minute = parts.find(p => p.type === 'minute')?.value
  
  const period = hour >= 12 ? '下午' : '上午'
  const displayHour = String(hour % 12 || 12).padStart(2, '0')
  
  return `${year}-${month}-${day} ${period}${displayHour}:${minute}`
}

/**
 * 格式化檔案大小
 */
function formatFileSize(bytes?: number): string {
  if (!bytes) return '未知大小'

  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/**
 * 開啟圖片預覽
 */
function openImagePreview(url: string) {
  previewImageUrl.value = url
  imagePreview.value = true
}

/**
 * 下載檔案
 */
function downloadFile(url: string, filename: string) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 格式化寵物年齡（從卡片的出生年月即時計算）
 */
function formatPetAge(pet: PetCardData): string {
  // pet_age_years 和 pet_age_months 實際上儲存的是出生年月
  // 但舊資料可能儲存的是年齡快照，所以需要判斷
  
  const years = pet.pet_age_years ?? 0
  const months = pet.pet_age_months ?? 0
  
  // 判斷：如果 years > 1900，說明是出生年份，需要計算年齡
  if (years > 1900) {
    return calculateAge(years, months)
  } else {
    // 否則是舊的年齡快照，直接顯示
    return formatAge(years, months)
  }
}

/**
 * 前往寵物詳情頁
 */
function goToPetDetail() {
  if (petCardData.value) {
    router.push(`/pets/${petCardData.value.pet_id}`)
  }
}

/**
 * 處理關閉按鈕
 */
function handleClose() {
  const currentUser = authStore.user
  if (currentUser?.role === 'shelter') {
    // Shelter 回到寵物管理頁面
    router.push('/pets/manage')
  } else {
    // 申請者回到瀏覽寵物頁面
    router.push('/pets')
  }
}

/**
 * 顯示錯誤訊息
 */
function showErrorMessage(message: string) {
  errorMessage.value = message
  showError.value = true
}

/**
 * 處理 WebSocket 訊息
 */
function handleWebSocketMessage(data: WebSocketMessage) {
  console.log('📨 Received WebSocket message:', data)
  
  if (data.type === 'new_message' && data.room_id === roomId.value && data.message) {
    const message = data.message as ChatMessage
    // 檢查是否已存在（避免重複）
    const exists = messages.value.some(m => m.id === message.id)
    if (!exists) {
      console.log('✅ Adding new message to list:', message)
      messages.value.push(message)
      
      // 滾動到底部
      nextTick(() => {
        if (!showScrollToBottom.value) {
          scrollToBottom()
        }
      })
      
      // 標記為已讀
      if (message.sender_id !== currentUserId.value) {
        markMessagesAsRead(roomId.value)
      }
    }
  }
}

// Lifecycle
onMounted(async () => {
  // 先載入聊天室列表（確保有寵物資料）
  await loadChatRooms()
  
  // 再載入訊息
  await loadMessages()

  // 連接 WebSocket
  try {
    await chatWebSocket.connect()
    
    // 訂閱當前聊天室
    chatWebSocket.subscribeRoom(roomId.value)
    
    // 註冊 WebSocket 訊息處理器
    chatWebSocket.addListener(handleWebSocketMessage)
    
    console.log('✅ WebSocket connected and subscribed to room', roomId.value)
  } catch (error) {
    console.error('❌ Failed to connect WebSocket:', error)
  }

  // 預填文字（首次進入時）
  if (prefillText.value) {
    messageInput.value = prefillText.value
  }
})

onUnmounted(() => {
  // 移除訊息處理器
  chatWebSocket.removeListener(handleWebSocketMessage)
  
  // 取消訂閱聊天室
  chatWebSocket.unsubscribeRoom(roomId.value)
})

// 監聽 route 變化，切換聊天室時重新載入
watch(() => route.params.id, async (newId) => {
  if (newId) {
    // 取消訂閱舊聊天室
    chatWebSocket.unsubscribeRoom(roomId.value)
    
    // 更新 roomId
    roomId.value = parseInt(newId as string)
    
    // 重置狀態
    skip.value = 0
    hasMore.value = true
    messages.value = []
    petCardData.value = null  // 重置寵物卡片資料
    
    // 載入新聊天室訊息
    await loadMessages()
    
    // 訂閱新聊天室
    chatWebSocket.subscribeRoom(roomId.value)
  }
})
</script>

<style scoped>
.chat-room-page {
  height: 100vh;
  overflow: hidden;
}

.chat-layout {
  height: 100vh;
}

/* 左側聊天列表 */
.chat-list-sidebar {
  border-right: 1px solid #e0e0e0;
  background-color: white;
}

.chat-list-header {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 5;
}

.chat-list-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-list-item:hover {
  background-color: #f5f5f5;
}

/* 右側聊天內容 */
.chat-content-area {
  background-color: #e5ddd5;
}

.chat-content-header {
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 5;
}

.message-container {
  overflow-y: auto;
  padding: 16px;
  position: relative;
  background-color: #e5ddd5;
}

.pet-card {
  margin-bottom: 16px;
}

.message-item {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
}

.message-sent {
  align-items: flex-end;
}

.message-received {
  align-items: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-sent .message-bubble {
  background-color: #dcf8c6;
}

.message-received .message-bubble {
  background-color: white;
}

.text-message {
  white-space: pre-wrap;
}

.pet-card-message {
  background-color: #fff3cd !important;
  border: 1px solid #ffc107;
}

.image-message {
  padding: 4px;
  background-color: transparent !important;
}

.file-message {
  display: flex;
  align-items: center;
  min-width: 250px;
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.input-container {
  background-color: white;
  padding: 12px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  border-top: 1px solid #e0e0e0;
}

.scroll-to-bottom-btn {
  position: absolute !important;
  bottom: 80px;
  right: 16px;
}

.cursor-pointer {
  cursor: pointer;
}
</style>
