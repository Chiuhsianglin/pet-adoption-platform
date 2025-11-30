<template>
  <v-app-bar app color="primary" dark elevation="2">
    <v-app-bar-nav-icon
      v-if="uiStore.isMobile"
      @click="uiStore.toggleSidebar"
    />

    <v-toolbar-title class="d-flex align-center">
      <router-link :to="authStore.isAuthenticated ? '/pets' : '/'" class="text-decoration-none text-white">
        <v-icon icon="mdi-paw" size="large" class="mr-2" />
        <span class="font-weight-bold">寵物領養平台</span>
      </router-link>
    </v-toolbar-title>

    <!-- Navigation Menu (Desktop) - Centered -->
    <div v-if="!uiStore.isMobile && authStore.isAuthenticated" class="d-flex justify-center" style="position: absolute; left: 50%; transform: translateX(-50%);">
      <!-- Shelter Navigation -->
      <template v-if="authStore.isShelter">
        <v-btn to="/pets/manage" variant="text" class="mx-2 text-white">寵物管理</v-btn>
        <v-btn to="/adoptions/review" variant="text" class="mx-2 text-white">申請審核</v-btn>
        <v-btn to="/community" variant="text" class="mx-2 text-white">社群</v-btn>
      </template>
      <!-- Adopter Navigation -->
      <template v-else>
        <v-btn to="/pets" variant="text" class="mx-2 text-white">瀏覽寵物</v-btn>
        <v-btn to="/favorites" variant="text" class="mx-2 text-white">我的收藏</v-btn>
        <v-btn to="/applications" variant="text" class="mx-2 text-white">我的申請</v-btn>
        <v-btn to="/community" variant="text" class="mx-2 text-white">社群</v-btn>
      </template>
    </div>

    <v-spacer />

    <!-- User Menu -->
    <template v-if="authStore.isAuthenticated">
      <!-- Chat Icon -->
      <v-btn
        icon
        to="/chat"
        class="mr-2"
      >
        <v-badge
          v-if="unreadCount > 0"
          :content="unreadCount"
          color="error"
        >
          <v-icon>mdi-message-text</v-icon>
        </v-badge>
        <v-icon v-else>mdi-message-text-outline</v-icon>
      </v-btn>

      <!-- Notification Bell -->
      <NotificationBell class="mr-2" />

      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar size="36">
              <v-icon>mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
                          <v-list-item-title>
                <v-icon icon="mdi-account-circle" size="small" class="mr-2" />
              {{ authStore.user?.name || authStore.user?.email }}
              </v-list-item-title>
            <v-list-item-subtitle>
              {{ authStore.user?.email }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item to="/profile" prepend-icon="mdi-account">
            個人檔案
          </v-list-item>
          <v-divider />
          <v-list-item @click="showLogoutDialog = true" prepend-icon="mdi-logout">
            登出
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <!-- Login/Register Buttons -->
    <template v-else>
      <v-btn to="/auth/login" variant="text">登入</v-btn>
      <v-btn to="/auth/register" variant="outlined">註冊</v-btn>
    </template>
  </v-app-bar>

  <!-- Logout Confirmation Dialog -->
  <v-dialog v-model="showLogoutDialog" max-width="400">
    <v-card>
      <v-card-title class="text-h6 bg-primary text-white">
        <v-icon icon="mdi-logout" class="mr-2" />
        確認登出
      </v-card-title>
      <v-card-text class="pt-4">
        <p>您確定要登出嗎？</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="showLogoutDialog = false">
          取消
        </v-btn>
        <v-btn color="primary" variant="flat" @click="confirmLogout">
          確認登出
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import NotificationBell from '@/components/notifications/NotificationBell.vue'
import { getChatRooms } from '@/api/chat'

const authStore = useAuthStore()
const uiStore = useUIStore()
const notificationStore = useNotificationStore()
const router = useRouter()

// 未讀訊息數量
const unreadCount = ref(0)
let refreshInterval: number | null = null

// 登出確認對話框
const showLogoutDialog = ref(false)

/**
 * 載入未讀訊息數量
 */
async function loadUnreadCount() {
  if (!authStore.isAuthenticated) return
  
  try {
    const rooms = await getChatRooms()
    unreadCount.value = rooms.reduce((sum: number, room) => sum + room.unread_count, 0)
  } catch (err) {
    console.error('❌ Failed to load unread count:', err)
  }
}

/**
 * 確認登出
 */
const confirmLogout = async () => {
  showLogoutDialog.value = false
  await authStore.logout()
  notificationStore.success('已成功登出')
  router.push('/')
}

// 生命週期
onMounted(() => {
  if (authStore.isAuthenticated) {
    loadUnreadCount()
    // 每30秒更新一次未讀數量
    refreshInterval = window.setInterval(loadUnreadCount, 30000)
  }
})

onUnmounted(() => {
  if (refreshInterval !== null) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.v-toolbar-title a {
  display: flex;
  align-items: center;
}
</style>
