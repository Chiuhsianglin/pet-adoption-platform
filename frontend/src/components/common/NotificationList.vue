<template>
  <v-snackbar
    v-for="notification in notificationStore.notifications"
    :key="notification.id"
    :model-value="true"
    :timeout="notification.timeout"
    :color="getColor(notification.type)"
    location="top right"
    @update:model-value="() => notificationStore.removeNotification(notification.id)"
  >
    <div class="d-flex align-center">
      <v-icon :icon="getIcon(notification.type)" class="mr-2" />
      <span>{{ notification.message }}</span>
    </div>
    
    <template v-slot:actions>
      <v-btn
        icon="mdi-close"
        variant="text"
        size="small"
        @click="notificationStore.removeNotification(notification.id)"
      />
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notification'
import type { Notification } from '@/stores/notification'

const notificationStore = useNotificationStore()

const getColor = (type: Notification['type']) => {
  const colors = {
    success: 'success',
    error: 'error',
    warning: 'warning',
    info: 'info',
  }
  return colors[type] || 'info'
}

const getIcon = (type: Notification['type']) => {
  const icons = {
    success: 'mdi-check-circle',
    error: 'mdi-alert-circle',
    warning: 'mdi-alert',
    info: 'mdi-information',
  }
  return icons[type] || 'mdi-information'
}
</script>
