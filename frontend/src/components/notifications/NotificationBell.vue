<template>
  <v-menu offset-y :close-on-content-click="false" max-width="600" @update:model-value="handleMenuToggle">
    <template v-slot:activator="{ props }">
      <v-btn icon v-bind="props" :loading="loading">
        <v-badge
          :content="unreadCount"
          :model-value="unreadCount > 0"
          color="error"
          overlap
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>
    </template>

    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>通知</span>
        <v-btn
          v-if="unreadCount > 0"
          size="small"
          variant="text"
          @click="handleMarkAllAsRead"
        >
          全部已讀
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-list
        v-if="notifications.length > 0"
        max-height="500"
        class="overflow-y-auto"
      >
        <v-list-item
          v-for="notification in notifications"
          :key="notification.id"
          :class="{ 'bg-blue-lighten-5': !notification.is_read }"
        >
          <template v-slot:prepend>
            <v-avatar color="primary">
              <v-icon>mdi-bell</v-icon>
            </v-avatar>
          </template>

          <v-list-item-title class="text-wrap">
            {{ notification.title }}
          </v-list-item-title>

          <v-list-item-subtitle class="text-wrap mt-1">
            {{ notification.message }}
          </v-list-item-subtitle>

          <v-list-item-subtitle v-if="notification.link" class="mt-2">
            <v-btn
              size="small"
              color="primary"
              variant="tonal"
              prepend-icon="mdi-open-in-new"
              @click="handleNotificationClick(notification)"
            >
              {{ getLinkButtonText(notification.notification_type, notification.link) }}
            </v-btn>
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex flex-column align-end">
              <span class="text-caption text-grey">
                {{ formatNotificationTime(notification.created_at) }}
              </span>
              <v-btn
                icon="mdi-delete"
                size="x-small"
                variant="text"
                @click.stop="handleDelete(notification.id)"
              />
            </div>
          </template>
        </v-list-item>
      </v-list>

      <v-card-text v-else class="text-center text-grey">
        <v-icon size="48" class="mb-2">mdi-bell-off</v-icon>
        <div>暫無通知</div>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" color="primary" @click="navigateToNotifications">
          查看全部
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getUserNotifications,
  markNotificationAsRead,
  markAllAsRead,
  deleteNotification,
  formatNotificationTime,
  type Notification
} from '@/api/notifications'
import { notificationEvents } from '@/utils/notificationEvents'

const router = useRouter()

// State
const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const loading = ref(false)
const pollingInterval = ref<number | null>(null)

// Methods
async function loadNotifications() {
  try {
    const response = await getUserNotifications(0, 5) // 只顯示最新 5 條
    notifications.value = response.notifications
    unreadCount.value = response.unread_count
  } catch (error) {
    console.error('加載通知失敗:', error)
  }
}

function getLinkButtonText(notificationType: string | undefined | null, link?: string): string {
  if (notificationType === 'application_status' && link) {
    // 如果是查看申請頁面（shelter 收到申請通知）
    if (link.includes('/adoptions/applications/')) {
      return '查看申請'
    }
    // 如果是上傳文件頁面（申請者收到補件通知）
    if (link.includes('/documents')) {
      return '上傳文件'
    }
  }
  
  switch (notificationType) {
    case 'application_status':
      return '查看詳情'
    case 'post_like':
    case 'post_comment':
      return '查看貼文'
    case 'review_status':
      return '查看寵物'
    default:
      return '查看詳情'
  }
}

async function handleNotificationClick(notification: Notification) {
  // 標記為已讀
  if (!notification.is_read) {
    try {
      await markNotificationAsRead(notification.id)
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('標記已讀失敗:', error)
    }
  }

  // 導航到相關頁面
  if (notification.link) {
    router.push(notification.link)
  }
}

async function handleMenuToggle(isOpen: boolean) {
  // 當菜單打開時，立即顯示已載入的通知，並在背景標記為已讀
  if (isOpen && unreadCount.value > 0) {
    // 立即更新 UI（樂觀更新）
    const hadUnread = unreadCount.value > 0
    notifications.value.forEach(n => (n.is_read = true))
    unreadCount.value = 0
    
    // 在背景發送 API 請求
    if (hadUnread) {
      markAllAsRead().catch(error => {
        console.error('標記全部已讀失敗:', error)
      })
    }
  }
}

async function handleMarkAllAsRead() {
  loading.value = true
  try {
    await markAllAsRead()
    notifications.value.forEach(n => (n.is_read = true))
    unreadCount.value = 0
  } catch (error) {
    console.error('標記全部已讀失敗:', error)
  } finally {
    loading.value = false
  }
}

async function handleDelete(notificationId: number) {
  try {
    await deleteNotification(notificationId)
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      const wasUnread = !notifications.value[index].is_read
      notifications.value.splice(index, 1)
      if (wasUnread) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
  } catch (error) {
    console.error('刪除通知失敗:', error)
  }
}

function navigateToNotifications() {
  router.push('/notifications')
}

function startPolling() {
  // 每 15 秒更新一次通知列表（包含未讀計數）
  pollingInterval.value = window.setInterval(() => {
    loadNotifications()
  }, 15000)
}

function stopPolling() {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// Lifecycle
onMounted(() => {
  loadNotifications()
  startPolling()
  // 監聽通知更新事件
  notificationEvents.on(loadNotifications)
})

onUnmounted(() => {
  stopPolling()
  notificationEvents.off(loadNotifications)
})
</script>

<style scoped>
.text-wrap {
  white-space: normal;
  word-break: break-word;
}

.overflow-y-auto {
  overflow-y: auto;
}
</style>
