<template>
  <v-card class="form-step">
    <v-card-title>個人資料</v-card-title>
    <v-card-text>
      <v-form ref="formRef" @submit.prevent>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.name"
              label="姓名 *"
              :rules="[rules.required, rules.minLength(2)]"
              :error-messages="errors?.name"
              @blur="validateField('name')"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.phone"
              label="電話 *"
              placeholder="0912345678"
              maxlength="10"
              :rules="[rules.required, rules.phone]"
              :error-messages="errors?.phone"
              @blur="validateField('phone')"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.email"
              label="Email *"
              type="email"
              :rules="[rules.required, rules.email]"
              :error-messages="errors?.email"
              @blur="validateField('email')"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.id_number"
              label="身份證字號"
              placeholder="A123456789"
              maxlength="10"
              :rules="[rules.required, rules.idNumber]"
              :error-messages="errors?.id_number"
              @blur="validateField('id_number')"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="formData.address"
              label="地址 *"
              :rules="[rules.required]"
              :error-messages="errors?.address"
              @blur="validateField('address')"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.occupation"
              label="職業 *"
              :rules="[rules.required]"
              :error-messages="errors?.occupation"
              @blur="validateField('occupation')"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="formData.monthly_income"
              label="月收入 (TWD) *"
              type="number"
              :rules="[rules.required, rules.minValue(0)]"
              :error-messages="errors?.monthly_income"
              @blur="validateField('monthly_income')"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { PersonalInfo } from '@/types/adoption'
import { useAuthStore } from '@/stores/auth'

interface Props {
  modelValue: PersonalInfo
  errors?: Partial<Record<keyof PersonalInfo, string>>
}

interface Emits {
  (e: 'update:modelValue', value: PersonalInfo): void
  (e: 'validate'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const authStore = useAuthStore()

const formRef = ref()
const formData = ref<PersonalInfo>({ ...props.modelValue })

// Auto-fill user data on mount
onMounted(() => {
  if (authStore.user) {
    // Only auto-fill if fields are empty
    if (!formData.value.name) {
      formData.value.name = authStore.user.name || ''
    }
    if (!formData.value.phone) {
      formData.value.phone = authStore.user.phone || ''
    }
    if (!formData.value.email) {
      formData.value.email = authStore.user.email || ''
    }
    if (!formData.value.address) {
      formData.value.address = authStore.user.address || ''
    }
  }
})

// Validation rules
const rules = {
  required: (v: any) => !!v || '此欄位為必填',
  minLength: (min: number) => (v: string) => 
    (v && v.length >= min) || `請輸入至少 ${min} 個字`,
  phone: (v: string) => 
    /^09\d{8}$/.test(v) || '請輸入電話號碼 (09開頭10碼',
  email: (v: string) => 
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '請輸入Email',
  idNumber: (v: string) => 
    /^[A-Z][12]\d{8}$/.test(v) || '請輸入身分證字號',
  minValue: (min: number) => (v: number) => 
    v >= min || `請輸入大於 ${min} 的數值`
}

// Watch for changes and emit
watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// Validate single field
const validateField = (_field: keyof PersonalInfo) => {
  emit('validate')
}

// Validate all fields
const validate = async () => {
  const { valid } = await formRef.value.validate()
  return valid
}

defineExpose({ validate })
</script>

<style scoped>
.form-step {
  margin-bottom: 1.5rem;
}
</style>
