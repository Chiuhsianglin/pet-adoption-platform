<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="8" rounded="lg">
          <v-card-title class="text-h5 text-center pa-6 bg-primary">
            <v-icon icon="mdi-account-plus" size="32" class="mr-2" />
            註冊新帳號
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="formRef" v-model="valid" @submit.prevent="handleRegister">
              <v-text-field
                v-model="formData.name"
                label="姓名"
                prepend-inner-icon="mdi-account"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-2"
              />

              <v-text-field
                v-model="formData.email"
                label="電子郵件"
                prepend-inner-icon="mdi-email"
                type="email"
                :rules="[rules.required, rules.email]"
                variant="outlined"
                class="mb-2"
              />

              <v-text-field
                v-model="formData.password"
                label="密碼"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-2"
              />

              <!-- Password rule hints (informational only, not enforced) -->
              <div class="mb-3 password-rules">
                <div class="text-subtitle-2 mb-1">密碼規則（必須全部符合才能註冊）</div>
                <v-list dense>
                  <v-list-item>
                    <v-list-item-icon>
                      <v-icon :color="hasMixedCase ? 'success' : 'grey'">mdi-check-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>含有大小寫英文字母</v-list-item-content>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-icon>
                      <v-icon :color="hasNumber ? 'success' : 'grey'">mdi-check-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>含有數字</v-list-item-content>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-icon>
                      <v-icon :color="hasSpecial ? 'success' : 'grey'">mdi-check-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>含有特殊符號（例如 # ? ! 等）</v-list-item-content>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-icon>
                      <v-icon :color="hasMinLength ? 'success' : 'grey'">mdi-check-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>至少八碼</v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>

              <v-text-field
                v-model="formData.confirmPassword"
                label="確認密碼"
                prepend-inner-icon="mdi-lock-check"
                :type="showPassword ? 'text' : 'password'"
                :rules="[rules.required, rules.passwordMatch]"
                variant="outlined"
                class="mb-2"
              />

              <v-select
                v-model="formData.role"
                label="身份"
                prepend-inner-icon="mdi-account-badge"
                :items="roleOptions"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-4"
              />

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!valid || !isPasswordValid"
              >
                註冊
              </v-btn>
            </v-form>
          </v-card-text>

          <v-divider />

          <!-- Duplicate email modal -->
          <v-dialog v-model="showDuplicateModal" max-width="350">
            <v-card>
              <v-card-title class="text-h6">此帳號已被註冊</v-card-title>
              <v-card-text>請選擇要繼續的動作：</v-card-text>
              <v-card-actions class="pa-4 justify-center d-flex gap-10">
                <v-btn variant="tonal" color="grey" class="me-6" @click="onChooseRegisterNew">註冊新帳號</v-btn>
                <v-btn color="primary" @click="onChooseGoLogin">前往登入頁</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

          <v-card-actions class="pa-4">
            <v-spacer />
            <span class="text-body-2">已有帳號？</span>
            <v-btn
              variant="text"
              color="primary"
              :to="{ name: 'Login' }"
            >
              立即登入
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const formRef = ref()
const valid = ref(false)
const loading = ref(false)
const showPassword = ref(false)

const formData = ref<{
  name: string
  email: string
  password: string
  confirmPassword: string
  role: 'adopter' | 'shelter'
}>({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'adopter',
})

const roleOptions = [
  { title: '領養者', value: 'adopter' },
  { title: '收容所', value: 'shelter' },
]

const rules = {
  required: (v: string) => !!v || '此欄位為必填',
  email: (v: string) => /.+@.+\..+/.test(v) || '電子郵件格式不正確',
  // Note: We removed enforced complexity rules; confirmPassword still checked
  passwordMatch: (v: string) => v === formData.value.password || '密碼不一致',
}

// UI state for duplicate-email modal
const showDuplicateModal = ref(false)

// Password hint checks (informational only)
const hasMixedCase = computed(() => /[a-z]/.test(formData.value.password) && /[A-Z]/.test(formData.value.password))
const hasNumber = computed(() => /\d/.test(formData.value.password))
const hasSpecial = computed(() => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?#?]/.test(formData.value.password))
const hasMinLength = computed(() => formData.value.password.length >= 8)

// Check if password meets all four requirements
const isPasswordValid = computed(() => 
  hasMixedCase.value && hasNumber.value && hasSpecial.value && hasMinLength.value
)

const onChooseRegisterNew = () => {
  // Close modal and clear email so user can register a different account
  showDuplicateModal.value = false
  formData.value.email = ''
}

const onChooseGoLogin = () => {
  // Navigate to login page
  showDuplicateModal.value = false
  router.push({ name: 'Login' })
}

const handleRegister = async () => {
  
  if (!valid.value) return

  loading.value = true
  try {
    const success = await authStore.register({
      name: formData.value.name,
      email: formData.value.email,
      password: formData.value.password,
      role: formData.value.role,
    })

    if (success) {
      // 清空表單
      formData.value = {
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'adopter',
      }
      // 跳轉到登入頁面，帶上註冊成功的訊息
      router.push({ 
        name: 'Login',
        query: { registered: 'true' }
      })
    } else {
      // If backend says email already registered, show modal with options
      const errMsg = (authStore.error || '').toString()
      if (/already registered|已被註冊|Email already registered/i.test(errMsg)) {
        showDuplicateModal.value = true
      } else {
        notificationStore.error(authStore.error || '註冊失敗，請稍後再試')
      }
    }
  } catch (error: any) {
    notificationStore.error(error.message || '註冊失敗，請稍後再試')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffffff 0%, #eebfbf 100%);
}
</style>
