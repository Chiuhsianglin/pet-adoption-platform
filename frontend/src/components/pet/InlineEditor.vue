<template>
  <div class="inline-editor">
    <!-- Display Mode -->
    <div v-if="!isEditing" class="display-mode" @click="startEdit">
      <span class="value" :class="{ empty: isEmpty }">
        {{ displayValue }}
      </span>
      <v-icon v-if="canEdit" size="small" class="edit-icon">mdi-pencil</v-icon>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Text Input -->
      <v-text-field
        v-if="fieldType === 'text'"
        v-model="editValue"
        :label="label"
        :rules="rules"
        density="compact"
        hide-details="auto"
        @keyup.enter="saveEdit"
        @keyup.esc="cancelEdit"
        autofocus
      />

      <!-- Textarea -->
      <v-textarea
        v-else-if="fieldType === 'textarea'"
        v-model="editValue"
        :label="label"
        :rules="rules"
        rows="3"
        density="compact"
        hide-details="auto"
        @keyup.esc="cancelEdit"
        autofocus
      />

      <!-- Number Input -->
      <v-text-field
        v-else-if="fieldType === 'number'"
        v-model.number="editValue"
        :label="label"
        :rules="rules"
        type="number"
        density="compact"
        hide-details="auto"
        @keyup.enter="saveEdit"
        @keyup.esc="cancelEdit"
        autofocus
      />

      <!-- Select -->
      <v-select
        v-else-if="fieldType === 'select'"
        v-model="editValue"
        :items="options"
        :label="label"
        :rules="rules"
        density="compact"
        hide-details="auto"
        @update:model-value="autoSave && saveEdit()"
        autofocus
      />

      <!-- Boolean Switch -->
      <v-switch
        v-else-if="fieldType === 'boolean'"
        v-model="editValue"
        :label="label"
        color="primary"
        density="compact"
        hide-details
        @update:model-value="autoSave && saveEdit()"
      />

      <!-- Action Buttons -->
      <div v-if="!autoSave" class="action-buttons">
        <v-btn
          size="small"
          variant="text"
          color="success"
          icon="mdi-check"
          :loading="saving"
          @click="saveEdit"
        />
        <v-btn
          size="small"
          variant="text"
          color="error"
          icon="mdi-close"
          @click="cancelEdit"
        />
      </div>
    </div>

    <!-- Error Message -->
    <v-alert
      v-if="errorMessage"
      type="error"
      density="compact"
      closable
      @click:close="errorMessage = ''"
      class="mt-2"
    >
      {{ errorMessage }}
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import apiClient from '@/services/api'

interface Props {
  petId: number
  fieldName: string
  fieldValue: any
  fieldType?: 'text' | 'textarea' | 'number' | 'select' | 'boolean'
  label?: string
  options?: Array<{ title: string; value: any }>
  canEdit?: boolean
  autoSave?: boolean
  rules?: Array<(v: any) => boolean | string>
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  fieldType: 'text',
  label: '',
  canEdit: true,
  autoSave: false,
  rules: () => [],
  emptyText: '未設定'
})

const emit = defineEmits<{
  (e: 'updated', value: any): void
  (e: 'error', error: string): void
}>()

const isEditing = ref(false)
const editValue = ref<any>(props.fieldValue)
const saving = ref(false)
const errorMessage = ref('')

// Computed
const isEmpty = computed(() => {
  return props.fieldValue === null || 
         props.fieldValue === undefined || 
         props.fieldValue === ''
})

const displayValue = computed(() => {
  if (isEmpty.value) return props.emptyText

  if (props.fieldType === 'boolean') {
    return props.fieldValue ? '是' : '否'
  }

  if (props.fieldType === 'select' && props.options) {
    const option = props.options.find(opt => opt.value === props.fieldValue)
    return option ? option.title : props.fieldValue
  }

  return props.fieldValue
})

// Watch for external value changes
watch(() => props.fieldValue, (newValue) => {
  if (!isEditing.value) {
    editValue.value = newValue
  }
})

// Methods
const startEdit = () => {
  if (!props.canEdit) return
  
  editValue.value = props.fieldValue
  isEditing.value = true
  errorMessage.value = ''
}

const cancelEdit = () => {
  editValue.value = props.fieldValue
  isEditing.value = false
  errorMessage.value = ''
}

const saveEdit = async () => {
  // Validate
  if (props.rules.length > 0) {
    for (const rule of props.rules) {
      const result = rule(editValue.value)
      if (result !== true) {
        errorMessage.value = typeof result === 'string' ? result : '驗證失敗'
        return
      }
    }
  }

  // No change
  if (editValue.value === props.fieldValue) {
    isEditing.value = false
    return
  }

  saving.value = true
  errorMessage.value = ''

  try {
    // Call API to update single field
    await apiClient.put(
      `/pets/${props.petId}/field/${props.fieldName}`,
      {
        value: editValue.value,
        reason: `更新 ${props.label || props.fieldName}`
      }
    )

    // Success
    isEditing.value = false
    emit('updated', editValue.value)
    
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '更新失敗'
    emit('error', errorMessage.value)
  } finally {
    saving.value = false
  }
}

// Expose methods
defineExpose({
  startEdit,
  cancelEdit,
  saveEdit
})
</script>

<style scoped lang="scss">
.inline-editor {
  .display-mode {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba(0, 0, 0, 0.04);

      .edit-icon {
        opacity: 1;
      }
    }

    .value {
      flex: 1;
      
      &.empty {
        color: rgba(0, 0, 0, 0.38);
        font-style: italic;
      }
    }

    .edit-icon {
      opacity: 0;
      transition: opacity 0.2s;
      color: rgba(0, 0, 0, 0.54);
    }
  }

  .edit-mode {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .action-buttons {
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }
  }
}
</style>
