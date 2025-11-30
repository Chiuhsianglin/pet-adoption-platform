<template>
  <v-app>
    <app-header />
    <app-sidebar v-if="!uiStore.isMobile || uiStore.sidebarOpen" />
    
    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
    
    <app-footer />
    <notification-list />
  </v-app>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import NotificationList from '@/components/common/NotificationList.vue'

const uiStore = useUIStore()
</script>
