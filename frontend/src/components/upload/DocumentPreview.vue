<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="800">
    <v-card v-if="document">
      <v-card-title class="d-flex align-center">
        <v-icon left>mdi-file-eye</v-icon>
        文件預覽
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="$emit('update:modelValue', false)"
        />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-0">
        <!-- Image Preview -->
        <div v-if="isImage(document.mime_type)" class="preview-container">
          <div v-if="!document.file_url" class="pa-8 text-center">
            <v-icon size="80" color="warning">mdi-alert</v-icon>
            <p class="text-h6 mt-4">無法載入圖片</p>
            <p class="text-body-2 text-grey">文件 URL 不存在</p>
          </div>
          <img
            v-else
            :src="document.file_url"
            :alt="document.original_filename"
            class="preview-image"
            @error="handleImageError"
          />
        </div>

        <!-- Non-image File Info -->
        <div v-else class="pa-8 text-center">
          <v-icon size="80" color="grey">
            {{ getDocumentIcon(document.mime_type) }}
          </v-icon>
          <p class="text-h6 mt-4">{{ document.original_filename }}</p>
          <p class="text-body-2 text-grey">
            此類型檔案不支援預覽，請下載後查看
          </p>
          <v-btn
            color="primary"
            class="mt-4"
            @click="downloadDoc"
          >
            <v-icon left>mdi-download</v-icon>
            下載檔案
          </v-btn>
        </div>
      </v-card-text>

      <v-divider />

      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="6">
            <p class="text-caption text-grey mb-1">文件類型</p>
            <p class="text-body-2">{{ DocumentTypeLabels[document.document_type] }}</p>
          </v-col>
          <v-col cols="12" md="6">
            <p class="text-caption text-grey mb-1">檔案大小</p>
            <p class="text-body-2">{{ formatFileSize(document.file_size) }}</p>
          </v-col>
          <v-col cols="12" md="6">
            <p class="text-caption text-grey mb-1">上傳時間</p>
            <p class="text-body-2">{{ formatDate(document.uploaded_at) }}</p>
          </v-col>
          <!--v-col cols="12" md="6">
            <p class="text-caption text-grey mb-1">審核狀態</p>
            <v-chip
              :color="DocumentStatusColors[document.status]"
              size="small"
              variant="flat"
            >
              {{ DocumentStatusLabels[document.status] }}
            </v-chip>
          </v-col-->
          <v-col v-if="document.description" cols="12">
            <p class="text-caption text-grey mb-1">說明</p>
            <p class="text-body-2">{{ document.description }}</p>
          </v-col>
          <v-col v-if="document.review_notes" cols="12">
            <p class="text-caption text-grey mb-1">審核意見</p>
            <v-alert type="info" variant="tonal" density="compact">
              {{ document.review_notes }}
            </v-alert>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          關閉
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="downloadDoc"
        >
          <v-icon left>mdi-download</v-icon>
          下載
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { downloadDocument } from '@/api/document'
import {
  formatFileSize,
  isImageFile,
  DocumentTypeLabels,
  DocumentStatusLabels,
  DocumentStatusColors,
  type DocumentResponse
} from '@/types/document'

interface Props {
  modelValue: boolean
  document: DocumentResponse | null
}

const props = defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function isImage(mimeType: string): boolean {
  return isImageFile(mimeType)
}

function getDocumentIcon(mimeType: string): string {
  if (mimeType === 'application/pdf') return 'mdi-file-pdf-box'
  if (mimeType.includes('word')) return 'mdi-file-word'
  if (mimeType === 'text/plain') return 'mdi-file-document'
  return 'mdi-file'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function downloadDoc() {
  if (!props.document) return
  try {
    await downloadDocument(props.document.id, props.document.original_filename)
  } catch (error) {
    console.error('Failed to download document:', error)
  }
}

function handleImageError(event: Event) {
  console.error('Failed to load image:', event)
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.preview-container {
  max-height: 600px;
  overflow: auto;
  background-color: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.preview-image {
  max-width: 100%;
  max-height: 580px;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
