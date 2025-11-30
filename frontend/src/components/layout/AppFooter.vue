<template>
  <v-footer app color="surface" class="text-center">
    <v-container>
      <v-row>
        <v-col cols="12" md="4" class="text-left">
          <h3 class="text-h6 mb-2">寵物領養平台</h3>
          <p class="text-body-2">
            為每一個毛孩找到溫暖的家
          </p>
        </v-col>
        
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-2">快速連結</h3>
          <v-list density="compact" class="bg-transparent">
            <v-list-item to="/pets" class="px-0">瀏覽寵物</v-list-item>
            <v-list-item to="/about" class="px-0">關於我們</v-list-item>
            <v-list-item to="/contact" class="px-0">聯絡我們</v-list-item>
          </v-list>
        </v-col>
        
        <v-col cols="12" md="4">
          <h3 class="text-h6 mb-2">聯絡資訊</h3>
          <v-list density="compact" class="bg-transparent">
            <v-list-item class="px-0">
              <v-icon icon="mdi-email" size="small" class="mr-2" />
              info@petadoption.com
            </v-list-item>
            <v-list-item class="px-0">
              <v-icon icon="mdi-phone" size="small" class="mr-2" />
              +886-2-1234-5678
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
      
      <v-divider class="my-4" />
      
      <v-row>
        <v-col cols="12">
          <p class="text-body-2">
            © {{ new Date().getFullYear() }} 寵物領養平台. All rights reserved.
          </p>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
// Footer component
</script>
