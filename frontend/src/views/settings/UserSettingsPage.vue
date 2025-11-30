<template>
  <AppHeader />
  <v-container class="fill-height d-flex align-center justify-center">
    <v-card max-width="500" class="pa-6 text-center">
      <v-icon icon="mdi-cog" size="64" color="primary" class="mb-4" />
      <h2 class="text-h5 mb-4">設定頁面</h2>
      <p class="text-body-1 mb-4">
        個人資料設定已整合到個人檔案頁面
      </p>
      <v-btn 
        to="/profile" 
        color="primary" 
        size="large"
        prepend-icon="mdi-account"
      >
        前往個人檔案
      </v-btn>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()

// Auto-redirect to profile page after 2 seconds
onMounted(() => {
  setTimeout(() => {
    router.push('/profile')
  }, 2000)
})
</script>
