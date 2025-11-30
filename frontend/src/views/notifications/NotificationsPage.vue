<template>
  <AppHeader/>
  <v-container style="margin-top: 70px;">
    <v-row>
      <v-col cols="12">
        <!-- Header -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
                <v-col cols="auto" class="d-flex align-start pt-2">
                  <v-btn icon="mdi-arrow-left" variant="text" @click="$router.back()" />
              </v-col>
              <v-icon class="mr-2">mdi-bell</v-icon>
              <span>通知中心</span>
              <v-chip
                v-if="unreadCount > 0"
                color="error"
                size="small"
                class="ml-2"
              >
                {{ unreadCount }} 未讀
              </v-chip>
            </div>
            <div>
              <v-btn
                v-if="unreadCount > 0"
                variant="text"
                prepend-icon="mdi-check-all"
                @click="handleMarkAllAsRead"
              >
                全部已讀
              </v-btn>
            </div>
          </v-card-title>
        </v-card>

        <!-- Filters -->
        <v-card class="mb-4">
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6">
                <v-btn-toggle
                  v-model="filterMode"
                  color="primary"
                  variant="outlined"
                  divided
                  mandatory
                >
                  <v-btn value="all">全部</v-btn>
                  <v-btn value="unread">未讀</v-btn>
                </v-btn-toggle>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Notifications List -->
        <v-card>
          <v-list v-if="notifications.length > 0">
            <template
              v-for="(notification, index) in notifications"
              :key="notification.id"
            >
              <v-list-item
                :class="{ 'bg-blue-lighten-5': !notification.is_read }"
                @click="handleNotificationClick(notification)"
              >
                <template v-slot:prepend>
                  <v-avatar color="primary">
                    <v-icon>mdi-bell</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-wrap font-weight-medium">
                  {{ notification.title }}
                  <v-chip
                    v-if="!notification.is_read"
                    color="error"
                    size="x-small"
                    class="ml-2"
                  >
                    新
                  </v-chip>
                </v-list-item-title>

                <v-list-item-subtitle class="text-wrap mt-1">
                  {{ notification.message }}
                </v-list-item-subtitle>

                <v-list-item-subtitle class="mt-2">
                  <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                  {{ formatNotificationTime(notification.created_at) }}
                </v-list-item-subtitle>

                <!-- 查看按鈕 - 根據通知類型顯示不同文字 -->
                <div v-if="notification.link" class="mt-2">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    size="small"
                    @click.stop="goToPost(notification.link)"
                  >
                    <v-icon start>mdi-open-in-new</v-icon>
                    {{ getLinkButtonText(notification.notification_type, notification.link) }}
                  </v-btn>
                </div>

                <template v-slot:append>
                  <v-menu>
                    <template v-slot:activator="{ props }">
                      <v-btn
                        icon="mdi-dots-vertical"
                        size="small"
                        variant="text"
                        v-bind="props"
                      />
                    </template>
                    <v-list>
                      <v-list-item
                        v-if="!notification.is_read"
                        @click="handleMarkAsRead(notification.id)"
                      >
                        <v-list-item-title>
                          <v-icon class="mr-2">mdi-check</v-icon>
                          標記為已讀
                        </v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="handleDelete(notification.id)">
                        <v-list-item-title class="text-error">
                          <v-icon class="mr-2">mdi-delete</v-icon>
                          刪除
                        </v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
              <v-divider v-if="index < notifications.length - 1" />
            </template>
          </v-list>

          <!-- Empty State -->
          <v-card-text v-else class="text-center py-12">
            <v-icon size="64" color="grey-lighten-2" class="mb-4">
              mdi-bell-off-outline
            </v-icon>
            <div class="text-h6 text-grey">暫無通知</div>
          </v-card-text>

          <!-- Load More -->
          <v-card-actions v-if="hasMore && notifications.length > 0">
            <v-spacer />
            <v-btn
              variant="text"
              color="primary"
              :loading="loading"
              @click="loadMore"
            >
              載入更多
            </v-btn>
            <v-spacer />
          </v-card-actions>
        </v-card>

        <!-- Loading State -->
        <v-card v-if="loading && notifications.length === 0">
          <v-card-text class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
            <div class="mt-4">載入中...</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getUserNotifications,
  markNotificationAsRead,
  markAllAsRead,
  deleteNotification,
  formatNotificationTime,
  type Notification
} from '@/api/notifications'
import AppHeader from '@/components/layout/AppHeader.vue'
import { notificationEvents } from '@/utils/notificationEvents'

const router = useRouter()

// State
const notifications = ref<Notification[]>([])
const total = ref(0)
const unreadCount = ref(0)
const loading = ref(false)
const filterMode = ref<'all' | 'unread'>('all')
const page = ref(0)
const pageSize = 20

const hasMore = computed(() => notifications.value.length < total.value)

// Methods
async function loadNotifications(reset: boolean = false) {
  if (reset) {
    page.value = 0
    notifications.value = []
  }

  loading.value = true
  try {
    const response = await getUserNotifications(
      page.value * pageSize,
      pageSize,
      filterMode.value === 'unread'
    )

    if (reset) {
      notifications.value = response.notifications
    } else {
      notifications.value.push(...response.notifications)
    }

    total.value = response.total
    unreadCount.value = response.unread_count
  } catch (error) {
    console.error('載入通知失敗:', error)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  page.value++
  await loadNotifications()
}

async function handleNotificationClick(notification: Notification) {
  // 標記為已讀
  if (!notification.is_read) {
    await handleMarkAsRead(notification.id)
  }

  // 導航到相關頁面
  if (notification.link) {
    router.push(notification.link)
  }
}

async function handleMarkAsRead(notificationId: number) {
  try {
    await markNotificationAsRead(notificationId)
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    // 通知其他組件更新
    notificationEvents.emit()
  } catch (error) {
    console.error('標記已讀失敗:', error)
  }
}

async function handleMarkAllAsRead() {
  loading.value = true
  try {
    await markAllAsRead()
    notifications.value.forEach(n => (n.is_read = true))
    unreadCount.value = 0
    // 通知其他組件更新
    notificationEvents.emit()
  } catch (error) {
    console.error('標記全部已讀失敗:', error)
  } finally {
    loading.value = false
  }
}

function getLinkButtonText(notificationType: string | null | undefined, link?: string | null): string {
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

function goToPost(link: string) {
  router.push(link)
}

async function handleDelete(notificationId: number) {
  try {
    await deleteNotification(notificationId)
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      const wasUnread = !notifications.value[index].is_read
      notifications.value.splice(index, 1)
      total.value--
      if (wasUnread) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
    // 通知其他組件更新
    notificationEvents.emit()
  } catch (error) {
    console.error('刪除通知失敗:', error)
  }
}

// Watchers
watch(filterMode, () => {
  loadNotifications(true)
})

// Lifecycle
onMounted(() => {
  loadNotifications(true)
})
</script>

<style scoped>
.text-wrap {
  white-space: normal;
  word-break: break-word;
}
</style>
