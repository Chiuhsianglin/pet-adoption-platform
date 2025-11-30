<template>
  <v-app>
    <app-header />
    <v-main>
      <div class="home-page">
        <!-- Hero Section -->
        <v-card class="hero-section mb-8" elevation="0">
        <v-img
          src="https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=1920&h=600&fit=crop"
          cover
          height="400"
          gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
        >
          <v-container class="fill-height">
            <v-row align="center" justify="center">
              <v-col cols="12" class="text-center text-white">
                <h1 class="text-h2 font-weight-bold mb-4">
                  為每個毛孩找到溫暖的家
                </h1>
                <p class="text-h5 mb-6">
                  我們致力於幫助流浪動物找到愛他們的家庭
                </p>
                <v-btn
                  to="/pets"
                  size="x-large"
                  color="primary"
                  class="mr-4"
                >
                  開始尋找
                </v-btn>
                <v-btn
                  to="/auth/register"
                  size="x-large"
                  variant="outlined"
                  color="white"
                >
                  加入我們
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-img>
      </v-card>

      <!-- Features Section -->
      <v-container>
        <v-row>
          <v-col cols="12" class="text-center mb-8">
            <h2 class="text-h3 font-weight-bold mb-4">為什麼選擇我們？</h2>
            <p class="text-h6 text-medium-emphasis">
              我們提供最安全、最透明的寵物領養服務
            </p>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="4">
            <v-card class="text-center pa-6" elevation="2">
              <v-icon icon="mdi-shield-check" size="64" color="primary" class="mb-4" />
              <h3 class="text-h5 mb-2">安全可靠</h3>
              <p class="text-body-1">
                所有寵物都已健康檢查，領養流程透明公開
              </p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="text-center pa-6" elevation="2">
              <v-icon icon="mdi-heart-multiple" size="64" color="secondary" class="mb-4" />
              <h3 class="text-h5 mb-2">專業服務</h3>
              <p class="text-body-1">
                提供專業的領養諮詢和後續追蹤服務
              </p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="text-center pa-6" elevation="2">
              <v-icon icon="mdi-account-group" size="64" color="accent" class="mb-4" />
              <h3 class="text-h5 mb-2">社群支持</h3>
              <p class="text-body-1">
                加入我們的社群，與其他寵物主人交流經驗
              </p>
            </v-card>
          </v-col>
        </v-row>

        <!-- Call to Action -->
        <v-row class="mt-12">
          <v-col cols="12" class="text-center">
            <v-card color="primary" dark class="pa-8">
              <h2 class="text-h4 mb-4">準備好領養一隻寵物了嗎？</h2>
              <p class="text-h6 mb-6">
                現在就開始瀏覽我們的寵物資料庫，找到您的完美夥伴！
              </p>
              <v-btn
                to="/pets"
                size="x-large"
                color="white"
                variant="elevated"
              >
                瀏覽寵物
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.hero-section {
  border-radius: 0;
}
</style>
