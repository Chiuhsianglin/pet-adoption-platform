<template>
  <v-navigation-drawer
    v-model="uiStore.sidebarOpen"
    :temporary="uiStore.isMobile"
    app
  >
    <v-list density="compact" nav>
      <v-list-item
        v-if="!authStore.isAuthenticated"
        prepend-icon="mdi-home"
        title="首頁"
        to="/"
      />
      
      <v-list-item
        prepend-icon="mdi-paw"
        title="瀏覽寵物"
        to="/pets"
      />

      <template v-if="authStore.isAuthenticated">
        <v-divider class="my-2" />
        
        <v-list-item
          prepend-icon="mdi-account"
          title="個人檔案"
          to="/profile"
        />
        
        <!-- Shelter Options -->
        <template v-if="authStore.isShelter || authStore.isAdmin">
          <v-list-item
            prepend-icon="mdi-view-dashboard"
            title="寵物管理"
            to="/pets/manage"
          />
          <v-list-item
            prepend-icon="mdi-plus-circle"
            title="新增寵物"
            to="/pets/create"
          />
          <v-list-item
            prepend-icon="mdi-clipboard-check"
            title="申請審核"
            to="/adoptions/review"
          />
        </template>
        
        <!-- Adopter Options -->
        <template v-else>
          <v-list-item
            prepend-icon="mdi-heart"
            title="我的收藏"
            to="/favorites"
          />
          <v-list-item
            prepend-icon="mdi-file-document"
            title="我的申請"
            to="/applications"
          />
        </template>
      </template>

      <v-divider class="my-2" />
      
      <v-list-item
        prepend-icon="mdi-information"
        title="關於我們"
        to="/about"
      />
      
      <v-list-item
        prepend-icon="mdi-help-circle"
        title="幫助中心"
        to="/help"
      />
      
      <v-list-item
        prepend-icon="mdi-email"
        title="聯絡我們"
        to="/contact"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUIStore()
</script>
