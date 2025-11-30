<template>
  <v-card class="form-step">
    <v-card-title>養寵經驗與意願</v-card-title>
    <v-card-text>
      <v-form ref="formRef">
        <v-row>
          <v-col cols="12">
            <v-textarea
              v-model="formData.previous_experience"
              label="過往養寵經驗 *"
              rows="4"
              :rules="[rules.required, rules.minLength(1)]"
              hint="請詳細描述您過往的養寵經驗 (不能空白)"
              persistent-hint
            ></v-textarea>
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="formData.pet_knowledge"
              label="對此寵物的了解 *"
              rows="4"
              :rules="[rules.required, rules.minLength(1)]"
              hint="請說明您對這隻寵物品種或特性的了解 (不能空白)"
              persistent-hint
            ></v-textarea>
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="formData.care_schedule"
              label="照護計劃與時間安排 *"
              rows="4"
              :rules="[rules.required, rules.minLength(1)]"
              hint="請說明您的日常照護計劃 (不能空白)"
              persistent-hint
            ></v-textarea>
          </v-col>

          <v-col cols="12" md="8">
            <v-text-field
              v-model="formData.veterinarian_info"
              label="獸醫診所資訊 *"
              :rules="[rules.required, rules.minLength(1)]"
              hint="請提供您計劃就診的獸醫診所名稱、地址或電話"
              persistent-hint
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="4">
            <v-text-field
              v-model.number="formData.emergency_fund"
              label="緊急醫療費用準備 (TWD) *"
              type="number"
              :rules="[rules.required, rules.minValue(0)]"
              hint="建議至少準備 20,000 元"
              persistent-hint
            ></v-text-field>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { PetExperience } from '@/types/adoption'

interface Props {
  modelValue: PetExperience
}

interface Emits {
  (e: 'update:modelValue', value: PetExperience): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()
const formData = ref<PetExperience>({ ...props.modelValue })

const rules = {
  required: (v: any) => !!v || '此欄位為必填',
  minLength: (min: number) => (v: string) => 
    (v && v.length >= min) || `至少需要 ${min} 個字元`,
  minValue: (min: number) => (v: number) => 
    v >= min || `數值不能小於 ${min}`
}

watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

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
