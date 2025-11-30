<template>
  <AppHeader />
  <v-container class="py-8" style="margin-top: 50px;">
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-text class="text-center">
            <v-avatar size="120" color="primary">
              <v-icon icon="mdi-account" size="80" />
            </v-avatar>
            <h2 class="text-h5 mt-4">{{ user?.name }}</h2>
            <p class="text-body-2 text-grey">{{ user?.email }}</p>
            <v-chip :color="getRoleColor(user?.role)" class="mt-2">
              {{ getRoleText(user?.role) }}
            </v-chip>
          </v-card-text>

            <v-divider />

            <v-list>
              <v-list-item
                v-for="item in menuItems"
                :key="item.title"
                :active="activeTab === item.value"
                @click="activeTab = item.value"
              >
                <template #prepend>
                  <v-icon :icon="item.icon" />
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>

        <v-col cols="12" md="8">
          <!-- Profile Tab -->
          <v-card v-if="activeTab === 'profile'">
            <v-card-text>
              <v-form>
                <v-text-field
                  v-model="profileForm.username"
                  label="姓名"
                  variant="outlined"
                  class="mb-2"
                />
                <v-text-field
                  v-model="profileForm.email"
                  label="電子信箱"
                  variant="outlined"
                  readonly
                  class="mb-2"
                />
                <v-text-field
                  v-model="profileForm.phone"
                  label="電話"
                  variant="outlined"
                  class="mb-2"
                  maxlength="10"
                />
                <v-text-field
                  v-model="profileForm.address"
                  label="地址"
                  variant="outlined"
                  class="mb-2"
                />
                <v-btn 
                  color="primary" 
                  @click="updateProfile"
                  :loading="updating"
                  :disabled="updating"
                >
                  更新資訊
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Password Tab -->
          <v-card v-if="activeTab === 'password'">
            <v-card-title>變更密碼</v-card-title>
            <v-card-text>
              <v-form>
                <v-text-field
                  v-model="passwordForm.currentPassword"
                  label="目前密碼"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  :append-inner-icon="showCurrentPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append-inner="showCurrentPassword = !showCurrentPassword"
                  variant="outlined"
                  class="mb-4"
                />
                <v-text-field
                  v-model="passwordForm.newPassword"
                  label="新密碼"
                  :type="showNewPassword ? 'text' : 'password'"
                  :append-inner-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append-inner="showNewPassword = !showNewPassword"
                  variant="outlined"
                  class="mb-2"
                />

                <!-- Password rules -->
                <div class="mb-3 password-rules">
                  <div class="text-subtitle-2 mb-1">密碼規則（必須全部符合才能變更）</div>
                  <v-list dense>
                    <v-list-item>
                      <template #prepend>
                        <v-icon :color="hasMixedCase ? 'success' : 'grey'">mdi-check-circle</v-icon>
                      </template>
                      <v-list-item-title>含有大小寫英文字母</v-list-item-title>
                    </v-list-item>

                    <v-list-item>
                      <template #prepend>
                        <v-icon :color="hasNumber ? 'success' : 'grey'">mdi-check-circle</v-icon>
                      </template>
                      <v-list-item-title>含有數字</v-list-item-title>
                    </v-list-item>

                    <v-list-item>
                      <template #prepend>
                        <v-icon :color="hasSpecial ? 'success' : 'grey'">mdi-check-circle</v-icon>
                      </template>
                      <v-list-item-title>含有特殊符號（例如 # ? ! 等）</v-list-item-title>
                    </v-list-item>

                    <v-list-item>
                      <template #prepend>
                        <v-icon :color="hasMinLength ? 'success' : 'grey'">mdi-check-circle</v-icon>
                      </template>
                      <v-list-item-title>至少八碼</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </div>

                <v-text-field
                  v-model="passwordForm.confirmPassword"
                  label="確認新密碼"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append-inner="showConfirmPassword = !showConfirmPassword"
                  variant="outlined"
                  class="mb-4"
                />
                <v-btn 
                  color="primary" 
                  @click="changePassword"
                  :disabled="!isPasswordValid || !passwordForm.currentPassword || !passwordForm.confirmPassword || passwordForm.newPassword !== passwordForm.confirmPassword"
                >
                  變更密碼
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Profile Update Success Dialog -->
    <v-dialog v-model="profileSuccessDialog" max-width="500">
      <v-card>
        <v-card-text class="text-center py-4">
          <v-icon 
            icon="mdi-check-circle" 
            color="success" 
            size="80"
            class="mb-4"
          />
          <div class="text-h5 mb-3">個人資訊更新成功</div>
          <div class="text-body-1 text-medium-emphasis mb-4">
            您的個人資訊已成功更新
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="success"
            variant="elevated"
            size="large"
            @click="profileSuccessDialog = false"
          >
            <v-icon icon="mdi-check" start />
            確定
          </v-btn>
          <v-spacer />
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Password Change Success Dialog -->
    <v-dialog v-model="passwordSuccessDialog" max-width="500">
      <v-card>
        <v-card-text class="text-center py-4">
          <v-icon 
            icon="mdi-shield-check" 
            color="success" 
            size="80"
            class="mb-4"
          />
          <div class="text-h5 mb-3">密碼變更成功</div>
          <div class="text-body-1 text-medium-emphasis mb-4">
            您的密碼已成功變更，請妥善保管新密碼
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="success"
            variant="elevated"
            size="large"
            @click="passwordSuccessDialog = false"
          >
            <v-icon icon="mdi-check" start />
            我知道了
          </v-btn>
          <v-spacer />
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import AppHeader from '@/components/layout/AppHeader.vue'
import api from '@/services/api'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const activeTab = ref('profile')
const user = computed(() => authStore.user)
const updating = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const profileSuccessDialog = ref(false)
const passwordSuccessDialog = ref(false)

const profileForm = ref({
  username: '',
  email: '',
  phone: '',
  address: '',
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const menuItems = [
  { title: '個人資訊', value: 'profile', icon: 'mdi-account' },
  { title: '變更密碼', value: 'password', icon: 'mdi-lock' },
]

// Password validation computed properties
const hasMixedCase = computed(() => /[a-z]/.test(passwordForm.value.newPassword) && /[A-Z]/.test(passwordForm.value.newPassword))
const hasNumber = computed(() => /\d/.test(passwordForm.value.newPassword))
const hasSpecial = computed(() => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?#?]/.test(passwordForm.value.newPassword))
const hasMinLength = computed(() => passwordForm.value.newPassword.length >= 8)

// Check if password meets all four requirements
const isPasswordValid = computed(() => 
  hasMixedCase.value && hasNumber.value && hasSpecial.value && hasMinLength.value
)

const getRoleColor = (role?: string) => {
  switch (role) {
    case 'admin':
      return 'error'
    case 'shelter':
      return 'primary'
    case 'adopter':
      return 'success'
    default:
      return 'grey'
  }
}

const getRoleText = (role?: string) => {
  switch (role) {
    case 'admin':
      return '管理員'
    case 'shelter':
      return '收容所'
    case 'adopter':
      return '領養者'
    default:
      return '未知'
  }
}

const loadProfile = () => {
  if (user.value) {
    console.log('📝 Loading profile, user data:', user.value)
    console.log('📝 user.phone:', user.value.phone)
    console.log('📝 user.address:', user.value.address)
    profileForm.value.username = user.value.name
    profileForm.value.email = user.value.email
    profileForm.value.phone = user.value.phone || ''
    profileForm.value.address = user.value.address || ''
    console.log('📝 Profile form loaded:', profileForm.value)
  }
}

const updateProfile = async () => {
  if (updating.value) return
  
  updating.value = true
  try {
    const response = await api.put('/auth/me', {
      name: profileForm.value.username,
      phone: profileForm.value.phone,
      address: profileForm.value.address
    })
    
    // Update user in store with response data
    if (response.data) {
      authStore.user = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    }
    
    profileSuccessDialog.value = true
    notificationStore.success('個人資訊已更新')
  } catch (error: any) {
    console.error('Failed to update profile:', error)
    notificationStore.error(error.response?.data?.detail || '更新失敗，請稍後再試')
  } finally {
    updating.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    notificationStore.error('新密碼與確認密碼不一致')
    return
  }

  if (!isPasswordValid.value) {
    notificationStore.error('新密碼不符合規則要求')
    return
  }

  try {
    await api.post('/auth/change-password', {
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })

    passwordSuccessDialog.value = true
    notificationStore.success('密碼已變更')
    
    // Clear form
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    }
  } catch (error: any) {
    console.error('Failed to change password:', error)
    const errorMsg = error.response?.data?.detail || '密碼變更失敗，請稍後再試'
    notificationStore.error(errorMsg)
  }
}

onMounted(async () => {
  // 立即使用現有的用戶資料載入表單
  loadProfile()
  
  // 背景更新用戶資料（不阻塞 UI）
  authStore.fetchCurrentUser()
})

// Watch for user changes and reload profile
watch(user, () => {
  loadProfile()
})
</script>
