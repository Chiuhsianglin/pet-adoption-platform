<template>
  <v-card class="document-uploader" :class="{ 'drag-over': isDragOver }">
    <v-card-text>
      <div
        class="drop-zone"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @click="triggerFileInput"
      >
        <v-icon size="64" color="primary" class="mb-4">mdi-cloud-upload</v-icon>
        <h3 class="text-h6 mb-2">拖曳檔案至此或點擊選擇</h3>
        <p class="text-body-2 text-grey">
          支援格式：PDF, JPG, PNG, DOC, DOCX, TXT
        </p>
        <p class="text-caption text-grey">
          檔案大小上限：10MB
        </p>
      </div>

      <input
        ref="fileInput"
        type="file"
        multiple
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.txt"
        style="display: none"
        @change="handleFileSelect"
      />

      <!-- File Selection -->
      <v-row v-if="selectedFiles.length > 0" class="mt-4">
        <v-col cols="12">
          <h4 class="text-subtitle-1 mb-2">已選擇的檔案</h4>
          <v-list>
            <v-list-item
              v-for="(fileInfo, index) in selectedFiles"
              :key="index"
              class="file-item"
            >
              <template #prepend>
                <v-icon :color="getFileIconColor(fileInfo)">
                  {{ getFileIcon(fileInfo.file) }}
                </v-icon>
              </template>

              <v-list-item-title>{{ fileInfo.file.name }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatFileSize(fileInfo.file.size) }}
                <span v-if="fileInfo.error" class="text-red ml-2">
                  ● {{ fileInfo.error }}
                </span>
                <span v-else-if="fileInfo.warning" class="text-orange ml-2">
                  ⚠ {{ fileInfo.warning }}
                </span>
              </v-list-item-subtitle>

              <template #append>
                <div class="d-flex align-center">
                  <!-- Document Type Selection -->
                  <v-select
                    v-model="fileInfo.documentType"
                    :items="documentTypeOptions"
                    item-title="label"
                    item-value="value"
                    label="文件類型"
                    density="compact"
                    style="min-width: 180px"
                    class="mr-2"
                    :error="!fileInfo.documentType"
                  />

                  <!-- Progress -->
                  <div v-if="fileInfo.uploading" class="upload-progress mr-2">
                    <v-progress-circular
                      :model-value="fileInfo.progress"
                      size="24"
                      width="3"
                      color="primary"
                    />
                    <span class="text-caption ml-2">{{ fileInfo.progress }}%</span>
                  </div>

                  <!-- Status Icons -->
                  <v-icon v-if="fileInfo.uploaded" color="success" class="mr-2">
                    mdi-check-circle
                  </v-icon>
                  <v-icon v-if="fileInfo.error" color="error" class="mr-2">
                    mdi-alert-circle
                  </v-icon>

                  <!-- Remove Button -->
                  <v-btn
                    icon="mdi-close"
                    size="small"
                    variant="text"
                    @click="removeFile(index)"
                    :disabled="fileInfo.uploading"
                  />
                </div>
              </template>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>

      <!-- Upload Actions -->
      <v-row v-if="selectedFiles.length > 0" class="mt-2">
        <v-col cols="12" class="d-flex justify-end gap-2">
          <v-btn
            color="grey"
            variant="outlined"
            @click="clearAll"
            :disabled="isUploading"
          >
            清除全部
          </v-btn>
          <v-btn
            color="primary"
            @click="uploadAll"
            :disabled="!canUpload"
            :loading="isUploading"
          >
            <v-icon left>mdi-upload</v-icon>
            上傳 ({{ validFileCount }}/{{ selectedFiles.length }})
          </v-btn>
        </v-col>
      </v-row>

      <!-- Upload Summary -->
      <v-alert
        v-if="uploadSummary"
        :type="uploadSummary.type"
        class="mt-4"
        closable
        @click:close="uploadSummary = null"
      >
        {{ uploadSummary.message }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { uploadDocument } from '@/api/document'
import {
  validateFileType,
  validateFileSize,
  formatFileSize,
  DocumentType,
  DocumentTypeLabels,
  type DocumentResponse
} from '@/types/document'

interface FileUploadInfo {
  file: File
  documentType: DocumentType | null
  error: string | null
  warning: string | null
  uploading: boolean
  uploaded: boolean
  progress: number
  response?: DocumentResponse
}

interface Props {
  applicationId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'upload-success': [document: DocumentResponse]
  'upload-complete': [results: { success: number; failed: number }]
}>()

const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)
const selectedFiles = ref<FileUploadInfo[]>([])
const uploadSummary = ref<{ type: 'success' | 'error' | 'warning'; message: string } | null>(null)

const documentTypeOptions = computed(() => {
  return Object.entries(DocumentTypeLabels).map(([value, label]) => ({
    value,
    label
  }))
})

const validFileCount = computed(() => {
  return selectedFiles.value.filter(f => !f.error && f.documentType).length
})

const canUpload = computed(() => {
  return validFileCount.value > 0 && !isUploading.value
})

const isUploading = computed(() => {
  return selectedFiles.value.some(f => f.uploading)
})

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
  // Reset input
  target.value = ''
}

function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

function addFiles(files: File[]) {
  const newFiles = files.map(file => {
    const sizeValidation = validateFileSize(file)
    const typeValidation = validateFileType(file)
    
    let error = null
    let warning = null
    
    if (!sizeValidation.valid) {
      error = sizeValidation.error!
    } else if (!typeValidation.valid) {
      error = typeValidation.error!
    }

    return {
      file,
      documentType: null,
      error,
      warning,
      uploading: false,
      uploaded: false,
      progress: 0
    } as FileUploadInfo
  })

  selectedFiles.value.push(...newFiles)
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

function clearAll() {
  selectedFiles.value = []
  uploadSummary.value = null
}

function getFileIcon(file: File): string {
  if (file.type.startsWith('image/')) return 'mdi-file-image'
  if (file.type === 'application/pdf') return 'mdi-file-pdf-box'
  if (file.type.includes('word')) return 'mdi-file-word'
  if (file.type === 'text/plain') return 'mdi-file-document'
  return 'mdi-file'
}

function getFileIconColor(fileInfo: FileUploadInfo): string {
  if (fileInfo.error) return 'error'
  if (fileInfo.uploaded) return 'success'
  if (fileInfo.uploading) return 'primary'
  return 'grey'
}

async function uploadAll() {
  const filesToUpload = selectedFiles.value.filter(f => !f.error && f.documentType && !f.uploaded)
  
  if (filesToUpload.length === 0) {
    uploadSummary.value = {
      type: 'warning',
      message: '請為所有檔案選擇文件類型'
    }
    return
  }

  let successCount = 0
  let failedCount = 0

  for (const fileInfo of filesToUpload) {
    try {
      fileInfo.uploading = true
      fileInfo.error = null

      const response = await uploadDocument(
        props.applicationId,
        fileInfo.file,
        fileInfo.documentType!,
        undefined,
        (progress) => {
          fileInfo.progress = progress
        }
      )

      fileInfo.uploaded = true
      fileInfo.response = response
      successCount++
      emit('upload-success', response)
    } catch (error: any) {
      fileInfo.error = error.response?.data?.detail || '上傳失敗'
      failedCount++
    } finally {
      fileInfo.uploading = false
    }
  }

  // Show summary
  if (failedCount === 0) {
    uploadSummary.value = {
      type: 'success',
      message: `成功上傳 ${successCount} 個檔案`
    }
    // Clear uploaded files after a delay
    setTimeout(() => {
      selectedFiles.value = selectedFiles.value.filter(f => !f.uploaded)
    }, 2000)
  } else {
    uploadSummary.value = {
      type: 'error',
      message: `上傳完成：${successCount} 個成功，${failedCount} 個失敗`
    }
  }

  emit('upload-complete', { success: successCount, failed: failedCount })
}
</script>

<style scoped>
.document-uploader {
  border: 2px dashed #ccc;
  transition: all 0.3s ease;
}

.document-uploader.drag-over {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.05);
}

.drop-zone {
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.drop-zone:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.file-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 8px;
}

.upload-progress {
  display: flex;
  align-items: center;
  min-width: 80px;
}
</style>
