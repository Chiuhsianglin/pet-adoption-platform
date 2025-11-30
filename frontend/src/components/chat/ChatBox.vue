<template>
  <v-card>
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon icon="mdi-chat" class="mr-2" />
        {{ roomName }}
      </div>
      <v-chip v-if="unreadCount > 0" color="primary" size="small">
        {{ unreadCount }} 則未讀
      </v-chip>
    </v-card-title>

    <v-divider />

    <!-- 訊息列表 -->
    <v-card-text
      ref="messagesContainer"
      class="messages-container"
      style="height: 400px; overflow-y: auto"
    >
      <div v-if="loading" class="text-center py-4">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="messages.length === 0" class="text-center text-grey py-8">
        尚無訊息,開始聊天吧!
      </div>

      <div v-else>
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item mb-3"
          :class="{ 'own-message': message.sender_id === currentUserId }"
        >
          <div class="message-bubble">
            <div class="message-header">
              <span class="font-weight-bold text-caption">
                {{ message.sender_name }}
              </span>
              <span class="text-caption text-grey ml-2">
                {{ formatMessageTime(message.created_at) }}
              </span>
            </div>
            <div class="message-content">
              {{ message.content }}
            </div>
          </div>
        </div>
      </div>
    </v-card-text>

    <v-divider />

    <!-- 輸入區域 -->
    <v-card-actions class="pa-4">
      <v-textarea
        v-model="messageInput"
        label="輸入訊息..."
        rows="2"
        variant="outlined"
        density="compact"
        hide-details
        :disabled="sending"
        @keydown.enter.exact.prevent="handleSend"
      />
      <v-btn
        icon="mdi-send"
        color="primary"
        class="ml-2"
        :loading="sending"
        :disabled="!messageInput.trim()"
        @click="handleSend"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  getMessages,
  sendMessage,
  formatMessageTime,
  type Message
} from '@/api/chat'

const props = defineProps<{
  roomId: number
  roomName: string
}>()

const emit = defineEmits<{
  (e: 'unread-count', count: number): void
}>()

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id || 0)

// State
const messages = ref<Message[]>([])
const messageInput = ref('')
const loading = ref(false)
const sending = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const pollingInterval = ref<number | null>(null)

const unreadCount = computed(() => {
  return messages.value.filter(
    (m) => !m.is_read && m.sender_id !== currentUserId.value
  ).length
})

// Methods
async function loadMessages() {
  if (!props.roomId) return

  loading.value = true
  try {
    messages.value = await getMessages(props.roomId, 50)
    await nextTick()
    scrollToBottom()
  } catch (error: any) {
    console.error('載入訊息失敗:', error)
  } finally {
    loading.value = false
  }
}

async function handleSend() {
  if (!messageInput.value.trim() || sending.value) return

  const content = messageInput.value.trim()
  messageInput.value = ''
  sending.value = true

  try {
    const newMessage = await sendMessage(props.roomId, {
      content,
      type: 'TEXT'
    })

    messages.value.push(newMessage)
    await nextTick()
    scrollToBottom()
  } catch (error: any) {
    console.error('發送訊息失敗:', error)
    alert('發送訊息失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    sending.value = false
  }
}

async function pollNewMessages() {
  if (loading.value || sending.value) return

  try {
    const latestMessages = await getMessages(props.roomId, 50)

    // 檢查是否有新訊息
    if (latestMessages.length > messages.value.length) {
      const wasAtBottom = isScrollAtBottom()
      messages.value = latestMessages

      if (wasAtBottom) {
        await nextTick()
        scrollToBottom()
      }
    }
  } catch (error: any) {
    console.error('輪詢訊息失敗:', error)
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function isScrollAtBottom(): boolean {
  if (!messagesContainer.value) return false

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  return scrollHeight - scrollTop - clientHeight < 100
}

function startPolling() {
  // 每 3 秒輪詢一次新訊息
  pollingInterval.value = window.setInterval(() => {
    pollNewMessages()
  }, 3000)
}

function stopPolling() {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// Lifecycle
onMounted(() => {
  loadMessages()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// Watch room changes
watch(() => props.roomId, () => {
  loadMessages()
})

// Watch unread count and emit changes
watch(unreadCount, (newCount) => {
  emit('unread-count', newCount)
}, { immediate: true })
</script>

<style scoped>
.messages-container {
  background-color: #f5f5f5;
}

.message-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-item.own-message {
  align-items: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 12px;
  background-color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-item.own-message .message-bubble {
  background-color: #1976d2;
  color: white;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.message-item.own-message .message-header {
  color: rgba(255, 255, 255, 0.9);
}

.message-content {
  word-wrap: break-word;
  white-space: pre-wrap;
}
</style>
