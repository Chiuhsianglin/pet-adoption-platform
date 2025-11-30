<template>
  <AppHeader />
  <v-container fluid class="chat-list-page pa-0" style="margin-top: 70px;">
    <!-- Header -->
    <v-card class="chat-header" elevation="2">
      <v-card-title class="d-flex align-center pa-3">
        <!-- 返回按鈕 -->
        <v-btn icon size="small" @click="$router.push('/pets')" class="mr-2">
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
        <span>&nbsp;聊天列表</span>
        
        <v-spacer />
        
        <!-- WebSocket 連接狀態 
        <v-chip
          :color="wsConnected ? 'success' : 'error'"
          size="small"
          variant="flat"
        >
        </v-chip>-->
      </v-card-title>
    </v-card>

    <!-- Loading Skeleton -->
    <v-list v-if="loading" lines="three">
      <v-list-item v-for="i in 5" :key="`skeleton-${i}`">
        <template v-slot:prepend>
          <v-skeleton-loader type="avatar" />
        </template>
        <v-list-item-title>
          <v-skeleton-loader type="text" width="60%" />
        </v-list-item-title>
        <v-list-item-subtitle>
          <v-skeleton-loader type="text" width="80%" />
        </v-list-item-subtitle>
        <template v-slot:append>
          <v-skeleton-loader type="chip" width="60px" />
        </template>
      </v-list-item>
    </v-list>

    <!-- 聊天室列表 -->
        <v-list v-if="!loading && rooms.length > 0" lines="three">
        <v-list-item
          v-for="room in rooms"
          :key="room.id"
          @click="openChatRoom(room.id)"
          class="chat-room-item"
        >
          <template v-slot:prepend>
            <!-- 寵物/用戶頭像 -->
            <v-avatar size="56" color="grey-lighten-2">
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
              <v-icon v-else size="32">mdi-paw</v-icon>
            </v-avatar>
          </template>

          <v-list-item-title class="font-weight-medium">
            {{ getRoomTitle(room) }}
          </v-list-item-title>

          <v-list-item-subtitle>
            <div class="d-flex align-center">
              <!-- 最後訊息類型圖示 -->
              <v-icon
                v-if="room.last_message_type"
                size="small"
                class="mr-1"
              >
                {{ getMessageTypeIcon(room.last_message_type) }}
              </v-icon>
              
              <!-- 最後訊息內容 -->
              <span class="text-truncate">
                {{ getLastMessagePreview(room) }}
              </span>
            </div>
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex flex-column align-end">
              <!-- 時間 -->
              <span class="text-body-2 text-grey">
                {{ formatTime(room.last_message_at) }}
              </span>
              
              <!-- 未讀數量 -->
              <v-badge
                v-if="room.unread_count > 0"
                :content="room.unread_count"
                color="error"
                inline
                class="mt-1"
              />
            </div>
          </template>
        </v-list-item>

        <v-divider />
      </v-list>

      <!-- 空狀態 -->
      <v-container v-if="!loading && rooms.length === 0" class="text-center py-16">
        <v-icon size="80" color="grey-lighten-1">mdi-message-outline</v-icon>
        <div class="text-h6 text-grey mt-4">尚無聊天記錄</div>
        <div class="text-body-2 text-grey mt-2">
          瀏覽寵物並點擊「詢問機構」開始對話
        </div>
        <v-btn
          color="primary"
          class="mt-4"
          @click="$router.push('/pets')"
        >
          <v-icon start>mdi-paw</v-icon>
          瀏覽寵物
        </v-btn>
      </v-container>

      <!-- Error -->
      <v-alert
        v-if="error"
        type="error"
        class="ma-4"
        closable
        @click:close="error = null"
      >
        {{ error }}
      </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  getChatRooms,
  type ChatRoom
} from '@/api/chat'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const rooms = ref<ChatRoom[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// 當前用戶
const currentUser = computed(() => authStore.user)

// Methods
async function loadChatRooms() {
  loading.value = true
  error.value = null

  try {
    const response = await getChatRooms()
    rooms.value = response
    console.log('✅ Loaded chat rooms:', response)
    console.log('✅ Rooms count:', rooms.value?.length || 0)
    console.log('✅ Rooms data:', rooms.value)
  } catch (err: any) {
    console.error('❌ Failed to load chat rooms:', err)
    console.error('❌ Error details:', err.response?.data)
    error.value = '載入聊天室列表失敗'
  } finally {
    loading.value = false
  }
}

/**
 * 獲取聊天室標題
 * - 使用者：寵物名稱
 * - Shelter：用戶名稱 + 寵物名稱
 */
function getRoomTitle(room: ChatRoom): string {
  if (!currentUser.value) return ''

  const isShelter = currentUser.value.id === room.shelter_id

  if (isShelter) {
    // Shelter 看到：用戶名稱 + 寵物名稱
    return `${room.user_name || '用戶'} - ${room.pet_name || '寵物'}`
  } else {
    // 使用者看到：寵物名稱
    return room.pet_name || '寵物'
  }
}

/**
 * 獲取訊息類型圖示
 */
function getMessageTypeIcon(type: string): string {
  switch (type) {
    case 'image':
      return 'mdi-image'
    case 'file':
      return 'mdi-file'
    case 'pet_card':
      return 'mdi-card-account-details'
    default:
      return 'mdi-message-text'
  }
}

/**
 * 獲取最後訊息預覽
 */
function getLastMessagePreview(room: ChatRoom): string {
  if (!room.last_message) {
    return '尚無訊息'
  }

  if (room.last_message_type === 'image') {
    return '[圖片]'
  }

  if (room.last_message_type === 'file') {
    return '[檔案]'
  }

  if (room.last_message_type === 'pet_card') {
    return '[寵物資訊]'
  }

  return room.last_message
}

/**
 * 格式化時間 (YYYY-MM-DD HH:mm)
 */
function formatTime(timestamp?: string): string {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}`
}

/**
 * 開啟聊天室
 */
function openChatRoom(roomId: number) {
  router.push(`/chat/${roomId}`)
}

// Lifecycle
onMounted(() => {
  console.log('📱 ChatListPage mounted')
  console.log('👤 Current user:', authStore.user)
  console.log('🔑 Token:', authStore.token ? 'exists' : 'missing')
  
  // 載入聊天室
  loadChatRooms()

  // V2 使用 REST API 輪詢，不需要 WebSocket
  // TODO: 可以添加定期輪詢更新聊天室列表
})
</script>

<style scoped>
.chat-list-page {
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f5f5f5;
}

.chat-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: white;
}

.chat-room-item {
  background-color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-room-item:hover {
  background-color: #f5f5f5;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}
</style>
