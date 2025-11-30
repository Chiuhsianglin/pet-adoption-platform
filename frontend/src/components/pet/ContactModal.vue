<template>
  <v-dialog v-model="dialog" max-width="600px" @click:outside="handleClose">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span class="text-h5 text-white">聯繫收容所</span>
        <v-btn icon="mdi-close" variant="text" @click="handleClose"></v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pt-6">
        <!-- Pet Info Summary -->
        <v-alert v-if="petName" type="info" variant="tonal" class="mb-4">
          <div class="d-flex align-center">
            <v-icon start>mdi-paw</v-icon>
            <span>關於 <strong>{{ petName }}</strong> 的諮詢</span>
          </div>
        </v-alert>

        <!-- Contact Form -->
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSubmit">
          <v-row>
            <!-- Name Field -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="formData.name"
                label="姓名 *"
                :rules="[rules.required, rules.minLength(2)]"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :disabled="loading"
              ></v-text-field>
            </v-col>

            <!-- Email Field -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="formData.email"
                label="電子郵件 *"
                :rules="[rules.required, rules.email]"
                prepend-inner-icon="mdi-email"
                type="email"
                variant="outlined"
                :disabled="loading"
              ></v-text-field>
            </v-col>

            <!-- Phone Field -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="formData.phone"
                label="聯絡電話 *"
                :rules="[rules.required, rules.phone]"
                prepend-inner-icon="mdi-phone"
                type="tel"
                variant="outlined"
                :disabled="loading"
              ></v-text-field>
            </v-col>

            <!-- Preferred Contact Method -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="formData.contactMethod"
                label="偏好聯繫方式 *"
                :items="contactMethods"
                :rules="[rules.required]"
                prepend-inner-icon="mdi-message"
                variant="outlined"
                :disabled="loading"
              ></v-select>
            </v-col>

            <!-- Inquiry Type -->
            <v-col cols="12">
              <v-select
                v-model="formData.inquiryType"
                label="諮詢類型 *"
                :items="inquiryTypes"
                :rules="[rules.required]"
                prepend-inner-icon="mdi-help-circle"
                variant="outlined"
                :disabled="loading"
              ></v-select>
            </v-col>

            <!-- Message Field -->
            <v-col cols="12">
              <v-textarea
                v-model="formData.message"
                label="訊息內容 *"
                :rules="[rules.required, rules.minLength(10)]"
                prepend-inner-icon="mdi-message-text"
                variant="outlined"
                rows="4"
                counter="500"
                maxlength="500"
                :disabled="loading"
                placeholder="請描述您的問題或需求..."
              ></v-textarea>
            </v-col>

            <!-- Preferred Visit Time (Optional) -->
            <v-col v-if="formData.inquiryType === '預約參觀'" cols="12" sm="6">
              <v-text-field
                v-model="formData.preferredDate"
                label="希望參觀日期"
                type="date"
                prepend-inner-icon="mdi-calendar"
                variant="outlined"
                :disabled="loading"
                :min="minDate"
              ></v-text-field>
            </v-col>

            <v-col v-if="formData.inquiryType === '預約參觀'" cols="12" sm="6">
              <v-select
                v-model="formData.preferredTime"
                label="希望參觀時段"
                :items="timeSlots"
                prepend-inner-icon="mdi-clock"
                variant="outlined"
                :disabled="loading"
              ></v-select>
            </v-col>

            <!-- Privacy Agreement -->
            <v-col cols="12">
              <v-checkbox
                v-model="formData.privacyAgreed"
                :rules="[rules.required]"
                :disabled="loading"
              >
                <template #label>
                  <div class="text-body-2">
                    我同意收容所使用我的個人資料以處理此諮詢 *
                  </div>
                </template>
              </v-checkbox>
            </v-col>
          </v-row>
        </v-form>

        <!-- Success Message -->
        <v-alert v-if="submitSuccess" type="success" variant="tonal" class="mt-4">
          <div class="d-flex align-center">
            <v-icon start>mdi-check-circle</v-icon>
            <div>
              <div class="font-weight-medium">訊息已成功送出！</div>
              <div class="text-body-2">收容所將在 1-2 個工作天內回覆您</div>
            </div>
          </div>
        </v-alert>

        <!-- Error Message -->
        <v-alert v-if="submitError" type="error" variant="tonal" class="mt-4" closable @click:close="submitError = null">
          <div class="d-flex align-center">
            <v-icon start>mdi-alert-circle</v-icon>
            <div>
              <div class="font-weight-medium">送出失敗</div>
              <div class="text-body-2">{{ submitError }}</div>
            </div>
          </div>
        </v-alert>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          @click="handleClose"
          :disabled="loading"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="handleSubmit"
          :loading="loading"
          :disabled="!formValid || submitSuccess"
        >
          <v-icon start>mdi-send</v-icon>
          送出諮詢
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/api/client'

interface ContactFormData {
  name: string
  email: string
  phone: string
  contactMethod: string
  inquiryType: string
  message: string
  preferredDate?: string
  preferredTime?: string
  privacyAgreed: boolean
}

interface Props {
  modelValue: boolean
  petId?: number
  petName?: string
  shelterId?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  petId: undefined,
  petName: undefined,
  shelterId: undefined
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submitted'): void
}>()

// Dialog state
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Form state
const formRef = ref<any>(null)
const formValid = ref(false)
const loading = ref(false)
const submitSuccess = ref(false)
const submitError = ref<string | null>(null)

// Form data
const formData = ref<ContactFormData>({
  name: '',
  email: '',
  phone: '',
  contactMethod: '電子郵件',
  inquiryType: '一般諮詢',
  message: '',
  preferredDate: undefined,
  preferredTime: undefined,
  privacyAgreed: false
})

// Contact methods
const contactMethods = [
  { title: '電子郵件', value: '電子郵件' },
  { title: '電話', value: '電話' },
  { title: 'LINE', value: 'LINE' },
  { title: '簡訊', value: '簡訊' }
]

// Inquiry types
const inquiryTypes = [
  { title: '一般諮詢', value: '一般諮詢' },
  { title: '領養相關', value: '領養相關' },
  { title: '預約參觀', value: '預約參觀' },
  { title: '寵物健康', value: '寵物健康' },
  { title: '領養流程', value: '領養流程' },
  { title: '費用相關', value: '費用相關' },
  { title: '其他問題', value: '其他問題' }
]

// Time slots for visit
const timeSlots = [
  { title: '上午 9:00 - 12:00', value: '上午 9:00 - 12:00' },
  { title: '下午 13:00 - 15:00', value: '下午 13:00 - 15:00' },
  { title: '下午 15:00 - 17:00', value: '下午 15:00 - 17:00' }
]

// Min date for visit (tomorrow)
const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

// Validation rules
const rules = {
  required: (v: any) => !!v || '此欄位為必填',
  minLength: (min: number) => (v: string) => 
    (v && v.length >= min) || `至少需要 ${min} 個字元`,
  email: (v: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return !v || pattern.test(v) || '請輸入有效的電子郵件'
  },
  phone: (v: string) => {
    const pattern = /^[0-9\s\-\+\(\)]{8,}$/
    return !v || pattern.test(v) || '請輸入有效的電話號碼'
  }
}

// Reset form when dialog opens/closes
watch(dialog, (newVal) => {
  if (!newVal) {
    submitSuccess.value = false
    submitError.value = null
  } else {
    // Pre-fill form from user profile if logged in
    loadUserInfo()
  }
})

// Load user info if authenticated
async function loadUserInfo() {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const response = await apiClient.get('/api/v2/auth/users/me')
    if (response.data.success && response.data.data) {
      const user = response.data.data
      formData.value.name = user.name || ''
      formData.value.email = user.email || ''
      formData.value.phone = user.phone || ''
    }
  } catch (error) {
    // User not logged in or error - use empty form
    console.log('User info not available, using empty form')
  }
}

// Handle form submission
async function handleSubmit() {
  if (!formValid.value) return

  // Validate form first
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  submitError.value = null

  try {
    // Prepare submission data
    const submissionData = {
      pet_id: props.petId,
      shelter_id: props.shelterId,
      name: formData.value.name,
      email: formData.value.email,
      phone: formData.value.phone,
      contact_method: formData.value.contactMethod,
      inquiry_type: formData.value.inquiryType,
      message: formData.value.message,
      preferred_date: formData.value.preferredDate,
      preferred_time: formData.value.preferredTime
    }

    // Submit to backend API
    // Note: This endpoint may need to be created in backend
    const response = await apiClient.post('/api/v2/inquiries', submissionData)

    if (response.data.success) {
      submitSuccess.value = true
      emit('submitted')
      
      // Auto close after 2 seconds
      setTimeout(() => {
        handleClose()
      }, 2000)
    } else {
      throw new Error(response.data.message || '送出失敗')
    }
  } catch (error: any) {
    console.error('Contact form submission error:', error)
    submitError.value = error.response?.data?.detail || error.message || '送出失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

// Handle dialog close
function handleClose() {
  if (!loading.value) {
    // Reset form
    formRef.value?.reset()
    formData.value = {
      name: '',
      email: '',
      phone: '',
      contactMethod: '電子郵件',
      inquiryType: '一般諮詢',
      message: '',
      preferredDate: undefined,
      preferredTime: undefined,
      privacyAgreed: false
    }
    submitSuccess.value = false
    submitError.value = null
    
    // Close dialog
    emit('update:modelValue', false)
  }
}
</script>

<style scoped>
.v-card-title {
  background-color: rgb(var(--v-theme-surface-variant));
}

.v-textarea :deep(textarea) {
  line-height: 1.6;
}

.v-alert {
  border-radius: 8px;
}

/* Smooth transitions */
.v-dialog {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Mobile responsive */
@media (max-width: 600px) {
  .v-card-title {
    font-size: 1.25rem !important;
  }
}
</style>
