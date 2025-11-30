<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" class="text-center">
        <v-icon icon="mdi-alert-circle-outline" size="120" color="error" class="mb-4" />
        <h1 class="text-h2 mb-4">404</h1>
        <h2 class="text-h4 mb-6">頁面不存在</h2>
        <p class="text-h6 text-medium-emphasis mb-8">
          抱歉，您訪問的頁面不存在或已被移除
        </p>
        <v-btn to="/" color="primary" size="large">
          返回首頁
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
// 404 Not Found Page
</script>
