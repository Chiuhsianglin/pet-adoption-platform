<template>
  <v-form ref="formRef" v-model="valid" @submit.prevent>
    <v-container>
      <v-row>
        <!-- Health Status -->
        <v-col cols="12">
          <v-textarea
            v-model="healthStatus"
            label="健康狀況"
            variant="outlined"
            rows="3"
            hint="描述寵物目前的健康狀態"
          />
        </v-col>

        <!-- Vaccination Status -->
        <v-col cols="12" md="6">
          <v-select
            v-model="vaccinationStatus"
            label="疫苗注射狀態"
            :items="[
              { title: '尚未完成', value: false },
              { title: '已完成', value: true }
            ]"
            variant="outlined"
            placeholder="請選擇"
            clearable
          />
        </v-col>

        <!-- Sterilized -->
        <v-col cols="12" md="6">
          <v-select
            v-model="sterilized"
            label="絕育手術狀態"
            :items="[
              { title: '尚未完成', value: false },
              { title: '已完成', value: true }
            ]"
            variant="outlined"
            placeholder="請選擇"
            clearable
          />
        </v-col>

        <!-- Special Needs -->
        <v-col cols="12">
          <v-textarea
            v-model="specialNeeds"
            label="特殊需求"
            variant="outlined"
            rows="3"
            hint="特殊照顧需求、疾病史、過敏等"
          />
        </v-col>

        <!-- Additional Health Information -->
        <v-col cols="12">
          <v-alert type="info" variant="tonal" class="mb-4">
            <strong>健康資訊提示：</strong>
            <ul class="mt-2">
              <li>請詳細描述寵物的健康狀態，包括任何慢性疾病</li>
              <li>列出已完成的疫苗種類和時間</li>
              <li>說明是否有特殊的飲食需求或限制</li>
              <li>如有定期服用的藥物，請註明藥名和用途</li>
            </ul>
          </v-alert>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PetCreate } from '@/types/pet'

interface Props {
  modelValue: Partial<PetCreate>
}

interface Emits {
  (e: 'update:modelValue', value: Partial<PetCreate>): void
  (e: 'valid', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()
const valid = ref(true) // Health form doesn't have required fields

// Use computed for two-way binding without watch conflicts
const healthStatus = computed({
  get: () => props.modelValue.health_status || '',
  set: (value) => emit('update:modelValue', { ...props.modelValue, health_status: value })
})

const vaccinationStatus = computed({
  get: () => props.modelValue.vaccination_status ?? undefined,
  set: (value) => emit('update:modelValue', { ...props.modelValue, vaccination_status: value })
})

const sterilized = computed({
  get: () => props.modelValue.sterilized ?? undefined,
  set: (value) => emit('update:modelValue', { ...props.modelValue, sterilized: value })
})

const specialNeeds = computed({
  get: () => props.modelValue.special_needs || '',
  set: (value) => emit('update:modelValue', { ...props.modelValue, special_needs: value })
})

// Watch valid state
import { watch } from 'vue'
watch(valid, (newValue) => {
  emit('valid', newValue)
})

// Expose validate method
defineExpose({
  validate: async () => {
    // Health form is always valid as it has no required fields
    return true
  },
})
</script>

<style scoped>
ul {
  padding-left: 20px;
}

li {
  margin: 4px 0;
}
</style>
