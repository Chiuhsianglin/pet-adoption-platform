<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="modelValue" class="dialog-overlay" @click="handleOverlayClick">
        <div class="dialog-container" @click.stop>
          <div class="dialog-header">
            <div class="dialog-icon" :class="iconClass">
              <i :class="iconName"></i>
            </div>
            <h3 class="dialog-title">{{ title }}</h3>
          </div>

          <div class="dialog-body">
            <p class="dialog-message">{{ message }}</p>
          </div>

          <div class="dialog-footer">
            <button
              @click="handleCancel"
              class="btn btn-cancel"
              :disabled="loading"
            >
              {{ cancelText }}
            </button>
            <button
              @click="handleConfirm"
              class="btn btn-confirm"
              :class="confirmButtonClass"
              :disabled="loading"
            >
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? loadingText : confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  loadingText?: string
  loading?: boolean
  type?: 'warning' | 'danger' | 'info' | 'success'
  closeOnOverlay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '確認操作',
  message: '您確定要執行此操作嗎？',
  confirmText: '確定',
  cancelText: '取消',
  loadingText: '處理中...',
  loading: false,
  type: 'warning',
  closeOnOverlay: true
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
  cancel: []
}>()

const iconName = computed(() => {
  const icons = {
    warning: 'mdi mdi-alert-circle-outline',
    danger: 'mdi mdi-alert-octagon-outline',
    info: 'mdi mdi-information-outline',
    success: 'mdi mdi-check-circle-outline'
  }
  return icons[props.type]
})

const iconClass = computed(() => `icon-${props.type}`)

const confirmButtonClass = computed(() => {
  const classes = {
    warning: 'btn-warning',
    danger: 'btn-danger',
    info: 'btn-info',
    success: 'btn-success'
  }
  return classes[props.type]
})

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('update:modelValue', false)
    emit('cancel')
  }
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay && !props.loading) {
    handleCancel()
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.dialog-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 450px;
  width: 100%;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  padding: 2rem 2rem 1rem;
  text-align: center;
}

.dialog-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.icon-warning {
  background: #fff3cd;
  color: #ff9800;
}

.icon-danger {
  background: #ffe0e0;
  color: #e91e63;
}

.icon-info {
  background: #e3f2fd;
  color: #2196f3;
}

.icon-success {
  background: #e8f5e9;
  color: #4caf50;
}

.dialog-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.dialog-body {
  padding: 0 2rem 1.5rem;
  text-align: center;
}

.dialog-message {
  font-size: 1rem;
  color: #5a6c7d;
  line-height: 1.6;
  margin: 0;
}

.dialog-footer {
  padding: 1.5rem 2rem;
  background: #f8f9fa;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: #e0e0e0;
  color: #5a6c7d;
}

.btn-cancel:hover:not(:disabled) {
  background: #d0d0d0;
}

.btn-confirm {
  color: white;
}

.btn-warning {
  background: #ff9800;
}

.btn-warning:hover:not(:disabled) {
  background: #f57c00;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.btn-danger {
  background: #e91e63;
}

.btn-danger:hover:not(:disabled) {
  background: #c2185b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}

.btn-info {
  background: #2196f3;
}

.btn-info:hover:not(:disabled) {
  background: #1976d2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.btn-success {
  background: #4caf50;
}

.btn-success:hover:not(:disabled) {
  background: #388e3c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-active .dialog-container {
  animation: slideUp 0.3s ease-out;
}

.dialog-leave-active .dialog-container {
  animation: slideDown 0.3s ease-in;
}

@keyframes slideDown {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(20px);
  }
}

/* Responsive */
@media (max-width: 576px) {
  .dialog-container {
    max-width: 100%;
    margin: 1rem;
  }

  .dialog-header {
    padding: 1.5rem 1.5rem 1rem;
  }

  .dialog-body {
    padding: 0 1.5rem 1rem;
  }

  .dialog-footer {
    padding: 1rem 1.5rem;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}
</style>
