<template>
  <div class="file-upload">
    <!-- 拖拽上傳區域 -->
    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging, 'drop-zone--disabled': disabled }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @click="!disabled && selectFiles()"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        style="display: none"
        @change="handleFileSelect"
      />

      <v-icon size="64" color="primary" class="mb-4">
        mdi-cloud-upload-outline
      </v-icon>

      <div class="drop-zone__text">
        <p class="text-h6 mb-2">
          {{ isDragging ? '放開以上傳檔案' : '拖拽檔案至此處' }}
        </p>
        <p class="text-body-2 text-medium-emphasis">
          或點擊選擇檔案
        </p>
        <p class="text-caption text-medium-emphasis mt-2">
          {{ acceptText }}
        </p>
        <p class="text-caption text-medium-emphasis">
          最大檔案大小: {{ maxSizeText }}
        </p>
      </div>
    </div>

    <!-- 檔案預覽列表 -->
    <v-list v-if="uploadingFiles.length > 0" class="mt-4">
      <v-list-item
        v-for="item in uploadingFiles"
        :key="item.id"
        class="file-preview-item"
      >
        <!-- 預覽圖片 -->
        <template v-slot:prepend>
          <v-avatar
            size="56"
            rounded="lg"
            :image="item.preview"
            class="file-preview-item__avatar"
          >
            <v-icon v-if="!item.preview">mdi-file</v-icon>
          </v-avatar>
        </template>

        <!-- 檔案資訊 -->
        <v-list-item-title>
          {{ item.file.name }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ formatFileSize(item.file.size) }}
        </v-list-item-subtitle>

        <!-- 上傳進度 -->
        <template v-slot:append>
          <div class="file-preview-item__status">
            <!-- 上傳中 -->
            <v-progress-circular
              v-if="item.status === 'uploading' || item.status === 'processing'"
              :model-value="item.progress"
              :size="40"
              :width="4"
              color="primary"
            >
              {{ item.progress }}%
            </v-progress-circular>

            <!-- 成功 -->
            <v-icon v-else-if="item.status === 'success'" color="success" size="40">
              mdi-check-circle
            </v-icon>

            <!-- 錯誤 -->
            <v-tooltip v-else-if="item.status === 'error'" location="top">
              <template v-slot:activator="{ props }">
                <v-icon v-bind="props" color="error" size="40">
                  mdi-alert-circle
                </v-icon>
              </template>
              {{ item.error }}
            </v-tooltip>

            <!-- 待上傳 -->
            <v-icon v-else color="grey" size="40">
              mdi-clock-outline
            </v-icon>

            <!-- 移除按鈕 -->
            <v-btn
              v-if="item.status !== 'uploading' && item.status !== 'processing'"
              icon
              size="small"
              variant="text"
              @click="removeFile(item.id)"
              class="ml-2"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </template>
      </v-list-item>
    </v-list>

    <!-- 上傳按鈕 -->
    <div v-if="showUploadButton && uploadingFiles.length > 0" class="mt-4">
      <v-btn
        color="primary"
        :disabled="isUploading || !hasFilesToUpload"
        :loading="isUploading"
        @click="uploadFiles"
        block
      >
        <v-icon start>mdi-upload</v-icon>
        上傳 {{ pendingFiles.length }} 個檔案
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { fileService } from '@/services/file'
import type { FileCategory, UploadProgress } from '@/types/file'

interface Props {
  accept?: string
  multiple?: boolean
  maxSize?: number // bytes
  maxFiles?: number
  category: FileCategory
  relatedId?: number
  isPublic?: boolean
  disabled?: boolean
  autoUpload?: boolean
  showUploadButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accept: 'image/jpeg,image/png,image/gif,image/webp',
  multiple: true,
  maxSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 10,
  isPublic: false,
  disabled: false,
  autoUpload: true,
  showUploadButton: false,
})

interface Emits {
  (e: 'upload-success', files: any[]): void
  (e: 'upload-error', error: string): void
  (e: 'files-selected', files: File[]): void
}

const emit = defineEmits<Emits>()

// Refs
const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)
const uploadingFiles = ref<UploadProgress[]>([])
const isUploading = ref(false)

// Computed
const acceptText = computed(() => {
  const types = props.accept.split(',').map(t => t.trim())
  if (types.some(t => t.startsWith('image/'))) {
    return '支援 JPG, PNG, GIF, WebP 圖片格式'
  }
  return '支援的檔案類型: ' + types.join(', ')
})

const maxSizeText = computed(() => {
  return fileService.formatFileSize(props.maxSize)
})

const pendingFiles = computed(() => {
  return uploadingFiles.value.filter(f => f.status === 'pending')
})

const hasFilesToUpload = computed(() => {
  return pendingFiles.value.length > 0
})

// Methods
const selectFiles = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    processFiles(Array.from(target.files))
    target.value = '' // 清空 input，允許重複選擇相同檔案
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (props.disabled) return

  const files = Array.from(event.dataTransfer?.files || [])
  processFiles(files)
}

const processFiles = (files: File[]) => {
  // 檢查檔案數量限制
  const totalFiles = uploadingFiles.value.length + files.length
  if (totalFiles > props.maxFiles) {
    emit('upload-error', `最多只能上傳 ${props.maxFiles} 個檔案`)
    return
  }

  // 驗證並添加檔案
  const allowedTypes = props.accept.split(',').map(t => t.trim())
  const validFiles: File[] = []

  for (const file of files) {
    // 驗證檔案類型
    if (!fileService.validateFileType(file, allowedTypes)) {
      emit('upload-error', `檔案 ${file.name} 格式不支援`)
      continue
    }

    // 驗證檔案大小
    if (!fileService.validateFileSize(file, props.maxSize)) {
      emit('upload-error', `檔案 ${file.name} 超過大小限制 (${maxSizeText.value})`)
      continue
    }

    validFiles.push(file)
  }

  // 創建上傳項目
  validFiles.forEach(file => {
    const id = `${Date.now()}-${Math.random()}`
    const uploadItem: UploadProgress = {
      id,
      file,
      progress: 0,
      status: 'pending',
    }

    // 生成預覽圖
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        uploadItem.preview = e.target?.result as string
      }
      reader.readAsDataURL(file)
    }

    uploadingFiles.value.push(uploadItem)
  })

  emit('files-selected', validFiles)

  // 自動上傳
  if (props.autoUpload && validFiles.length > 0) {
    uploadFiles()
  }
}

const removeFile = (id: string) => {
  const index = uploadingFiles.value.findIndex(f => f.id === id)
  if (index !== -1) {
    uploadingFiles.value.splice(index, 1)
  }
}

const uploadFiles = async () => {
  if (isUploading.value || pendingFiles.value.length === 0) return

  isUploading.value = true

  try {
    // 標記為上傳中
    pendingFiles.value.forEach(item => {
      item.status = 'uploading'
      item.progress = 0
    })

    // 上傳檔案
    const filesToUpload = pendingFiles.value.map(item => item.file)
    const result = await fileService.upload({
      files: filesToUpload,
      category: props.category,
      related_id: props.relatedId,
      is_public: props.isPublic,
      onProgress: (progress) => {
        // 更新所有上傳中檔案的進度
        uploadingFiles.value.forEach(item => {
          if (item.status === 'uploading') {
            item.progress = progress
            if (progress === 100) {
              item.status = 'processing'
            }
          }
        })
      },
    })

    // 更新上傳結果
    result.files.forEach((fileMetadata, index) => {
      const uploadItem = pendingFiles.value[index]
      if (uploadItem) {
        uploadItem.status = 'success'
        uploadItem.progress = 100
        uploadItem.result = fileMetadata
      }
    })

    emit('upload-success', result.files)
  } catch (error: any) {
    // 標記為錯誤
    pendingFiles.value.forEach(item => {
      item.status = 'error'
      item.error = error.response?.data?.detail || error.message || '上傳失敗'
    })

    emit('upload-error', error.response?.data?.detail || '上傳失敗')
  } finally {
    isUploading.value = false
  }
}

const clearSuccessful = () => {
  uploadingFiles.value = uploadingFiles.value.filter(f => f.status !== 'success')
}

const clearAll = () => {
  uploadingFiles.value = []
}

const formatFileSize = fileService.formatFileSize

// Expose methods
defineExpose({
  uploadFiles,
  clearSuccessful,
  clearAll,
})
</script>

<style scoped lang="scss">
.file-upload {
  width: 100%;
}

.drop-zone {
  border: 2px dashed rgb(var(--v-theme-primary));
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: rgb(var(--v-theme-surface));

  &:hover:not(.drop-zone--disabled) {
    background-color: rgba(var(--v-theme-primary), 0.05);
    border-color: rgb(var(--v-theme-primary));
  }

  &--active {
    background-color: rgba(var(--v-theme-primary), 0.1);
    border-color: rgb(var(--v-theme-primary));
    transform: scale(1.02);
  }

  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &__text {
    color: rgb(var(--v-theme-on-surface));
  }
}

.file-preview-item {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  margin-bottom: 8px;

  &__avatar {
    border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  }

  &__status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
