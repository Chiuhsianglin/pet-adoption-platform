<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">

        <v-card elevation="8" class="pa-4">
          <v-card-title class="text-h4 text-center mb-2 font-weight-bold d-flex align-center justify-center">
            <v-icon icon="mdi-paw" size="median" color="primary" class="mr-2" />
            登入
          </v-card-title>

          <v-card-text>
            <v-alert
              v-if="registrationSuccess"
              variant="tonal"
              color="success"
              class="mb-4"
              density="compact"
            >
              註冊成功 請登入
            </v-alert>

            <v-alert
              v-if="loginError"
              variant="tonal"
              color="error"
              class="mb-4"
              density="compact"
            >
              {{ loginError }}
            </v-alert>

            <v-form ref="formRef" @submit.prevent="handleLogin">
              <v-text-field
                v-model="credentials.email"
                label="電子郵件"
                type="email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                :rules="[rules.required]"
                class="mb-2"
              />

              <v-text-field
                v-model="credentials.password"
                label="密碼"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                :rules="[rules.required]"
                class="mb-2"
              />

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="authStore.loading"
                class="mb-4 "
              >
                登入
              </v-btn>

              <div class="text-center d-flex justify-center align-center mt-2">
                <v-btn
                  to="/"
                  variant="text"
                  size="small"
                  color="primary"
                >
                <v-icon start>mdi-arrow-left</v-icon>
                  返回首頁
                </v-btn>
                <!--
                <v-btn
                  to="/auth/forgot-password"
                  variant="text"
                  size="small"
                  class="ml-2"
                >
                  忘記密碼？
                </v-btn>-->
              </div>

            </v-form>
          </v-card-text>

          <v-divider class="my-4" />

          <v-card-actions class="justify-center">
            <span class="text-body-2">還沒有帳號？</span>
            <v-btn to="/auth/register" variant="text" color="primary">
              立即註冊
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import type { LoginCredentials } from '@/types/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const credentials = ref<LoginCredentials>({
  email: '',
  password: '',
  remember_me: false,
})

const showPassword = ref(false)
const loginError = ref<string | null>(null)
const registrationSuccess = ref(false)

const formRef = ref()

// 檢查是否從註冊頁面跳轉過來
onMounted(() => {
  if (route.query.registered === 'true') {
    registrationSuccess.value = true
    // 3 秒後自動隱藏成功訊息
  }
})

const rules = {
  required: (value: string) => !!value || '此欄位為必填',
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || '請輸入有效的電子郵件地址'
  },
}

const handleLogin = async () => {
  // Validate form
  loginError.value = null
  const { valid } = await formRef.value.validate()

  if (!valid) {
    return
  }

  const success = await authStore.login(credentials.value)
  if (success) {
    notificationStore.success('登入成功！')

    // Redirect based on user role
    const redirect = router.currentRoute.value.query.redirect as string
    if (redirect) {
      router.push(redirect)
    } else if (authStore.userRole === 'admin') {
      // Admin users go to community
      router.push('/community')
    } else if (authStore.isShelter) {
      // Shelter users go to pet management
      router.push('/pets/manage')
    } else {
      // Adopters go to pet browsing
      router.push('/pets')
    }
  } else {
    // Show inline red alert for invalid credentials
    loginError.value = '帳號或密碼輸入錯誤'
    // also fallback to notification for other contexts
    notificationStore.error(authStore.error || '登入失敗')
  }
}
</script>
<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffffff 0%, #eebfbf 100%);
}
</style>