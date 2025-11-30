<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon left>mdi-file-multiple</v-icon>
      已上傳文件
      <v-spacer />
      <v-chip
        :color="completionColor"
        variant="flat"
        size="small"
      >
        完成度：{{ documentList?.completion_percentage || 0 }}%
      </v-chip>
    </v-card-title>

    <v-divider />

    <!-- Loading State -->
    <v-card-text v-if="loading">
      <v-progress-linear indeterminate color="primary" />
      <p class="text-center text-grey mt-4">載入中...</p>
    </v-card-text>

    <!-- Empty State -->
    <v-card-text v-else-if="!documentList || documentList.documents.length === 0">
      <v-alert type="info" variant="tonal">
        <div class="d-flex align-center">
          <div>
            <p class="mb-2">尚未上傳任何文件</p>
            <p class="text-caption mb-0">
              必要文件：{{ requiredDocumentsText }}
            </p>
          </div>
        </div>
      </v-alert>
    </v-card-text>

    <!-- Document List -->
    <v-card-text v-else>
      <!-- Missing Documents Alert -->
      <v-alert
        v-if="documentList.missing_documents.length > 0"
        type="warning"
        variant="tonal"
        class="mb-4"
      >
        缺少必要文件：{{ documentList.missing_documents.map(d => DocumentTypeLabels[d as DocumentType]).join('、') }}
      </v-alert>

      <!-- Documents Grid -->
      <v-list>
        <v-list-item
          v-for="doc in documentList.documents"
          :key="doc.id"
          class="document-item mb-2"
        >
          <template #prepend>
            <v-avatar :color="getStatusColor(doc.status)" variant="tonal">
              <v-icon :color="getStatusColor(doc.status)">
                {{ getDocumentIcon(doc.mime_type) }}
              </v-icon>
            </v-avatar>
          </template>

          <v-list-item-title>
            <span class="font-weight-medium">{{ DocumentTypeLabels[doc.document_type] }}</span>
            <!--v-chip
              :color="getStatusColor(doc.status)"
              size="x-small"
              variant="flat"
              class="ml-2"
            >
              {{ DocumentStatusLabels[doc.status] }}
            </v-chip-->
          </v-list-item-title>

          <v-list-item-subtitle>
            {{ doc.original_filename }} · {{ formatFileSize(doc.file_size) }}
            <br />
            <span class="text-caption">
              上傳於 {{ formatDate(doc.uploaded_at) }}
              <span v-if="doc.version > 1"> · 版本 {{ doc.version }}</span>
            </span>
          </v-list-item-subtitle>

          <template #append>
            <div class="d-flex gap-1">
              <!-- Preview Button (Images Only) -->
              <v-btn
                v-if="isImage(doc.mime_type)"
                icon="mdi-eye"
                size="small"
                variant="text"
                @click="previewDocument(doc)"
                :title="'預覽'"
              />

              <!-- Download Button 
              <v-btn
                icon="mdi-download"
                size="small"
                variant="text"
                @click="downloadDoc(doc)"
                :title="'下載'"
              />-->

              <!-- Version History Button 
              <v-btn
                icon="mdi-history"
                size="small"
                variant="text"
                color="info"
                @click="showVersionHistory(doc)"
                :title="'版本歷史'"
              />-->

              <!-- Replace Button 
              <v-btn
                v-if="canReplace(doc)"
                icon="mdi-file-replace"
                size="small"
                variant="text"
                color="primary"
                @click="replaceDocument(doc)"
                :title="'替換'"
              />-->

              <!-- Delete Button -->
              <v-btn
                v-if="canDelete(doc)"
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="confirmDelete(doc)"
                :title="'刪除'"
                :loading="deletingId === doc.id"
              />
            </div>
          </template>

          <!-- Review Notes -->
          <v-expand-transition>
            <div v-if="doc.review_notes" class="mt-2 pa-3 bg-grey-lighten-4 rounded">
              <p class="text-caption font-weight-medium mb-1">審核意見：</p>
              <p class="text-body-2 mb-0">{{ doc.review_notes }}</p>
            </div>
          </v-expand-transition>
        </v-list-item>
      </v-list>

      <!-- Total Size -->
      <v-divider class="my-4" />
      <div class="text-caption text-grey text-right">
        總檔案大小：{{ formatFileSize(documentList.total_size) }}
      </div>
    </v-card-text>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>確認刪除</v-card-title>
        <v-card-text>
          確定要刪除文件「{{ documentToDelete?.original_filename }}」嗎？此操作無法復原。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">取消</v-btn>
          <v-btn color="error" @click="handleDelete" :loading="deletingId !== null">
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Preview Dialog -->
    <DocumentPreview
      v-model="previewDialog"
      :document="documentToPreview"
    />

    <!-- Version History Dialog -->
    <VersionHistory
      v-model="versionHistoryDialog"
      :document-id="versionHistoryDocId"
      @version-reverted="handleVersionReverted"
    />
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDocumentList, deleteDocument, downloadDocument } from '@/api/document'
import {
  formatFileSize,
  isImageFile,
  DocumentType,
  DocumentTypeLabels,
  DocumentStatus,
  DocumentStatusLabels,
  DocumentStatusColors,
  REQUIRED_DOCUMENT_TYPES,
  type DocumentResponse,
  type DocumentListResponse
} from '@/types/document'
import DocumentPreview from './DocumentPreview.vue'
import VersionHistory from './VersionHistory.vue'

interface Props {
  applicationId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'document-deleted': []
  'replace-document': [doc: DocumentResponse]
}>()

const loading = ref(false)
const documentList = ref<DocumentListResponse | null>(null)
const deleteDialog = ref(false)
const previewDialog = ref(false)
const versionHistoryDialog = ref(false)
const documentToDelete = ref<DocumentResponse | null>(null)
const documentToPreview = ref<DocumentResponse | null>(null)
const versionHistoryDocId = ref<number | null>(null)
const deletingId = ref<number | null>(null)

const completionColor = computed(() => {
  const percentage = documentList.value?.completion_percentage || 0
  if (percentage === 100) return 'success'
  if (percentage >= 60) return 'warning'
  return 'error'
})

const requiredDocumentsText = computed(() => {
  return REQUIRED_DOCUMENT_TYPES.map(type => DocumentTypeLabels[type]).join('、')
})

onMounted(() => {
  loadDocuments()
})

async function loadDocuments() {
  loading.value = true
  try {
    documentList.value = await getDocumentList(props.applicationId)
  } catch (error) {
    console.error('Failed to load documents:', error)
  } finally {
    loading.value = false
  }
}

function getDocumentIcon(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'mdi-file-image'
  if (mimeType === 'application/pdf') return 'mdi-file-pdf-box'
  if (mimeType.includes('word')) return 'mdi-file-word'
  if (mimeType === 'text/plain') return 'mdi-file-document'
  return 'mdi-file'
}

function getStatusColor(status: DocumentStatus): string {
  return DocumentStatusColors[status]
}

function isImage(mimeType: string): boolean {
  return isImageFile(mimeType)
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

function canDelete(doc: DocumentResponse): boolean {
  // 允許刪除任何文件（已取消審核流程）
  return true
}

function canReplace(doc: DocumentResponse): boolean {
  // 允許替換任何文件（已取消審核流程）
  return true
}

function previewDocument(doc: DocumentResponse) {
  documentToPreview.value = doc
  previewDialog.value = true
}

async function downloadDoc(doc: DocumentResponse) {
  try {
    await downloadDocument(doc.id, doc.original_filename)
  } catch (error) {
    console.error('Failed to download document:', error)
  }
}

function showVersionHistory(doc: DocumentResponse) {
  versionHistoryDocId.value = doc.id
  versionHistoryDialog.value = true
}

function handleVersionReverted() {
  versionHistoryDialog.value = false
  loadDocuments()
}

function replaceDocument(doc: DocumentResponse) {
  emit('replace-document', doc)
}

function confirmDelete(doc: DocumentResponse) {
  documentToDelete.value = doc
  deleteDialog.value = true
}

async function handleDelete() {
  if (!documentToDelete.value) return

  deletingId.value = documentToDelete.value.id
  try {
    await deleteDocument(props.applicationId, documentToDelete.value.id)
    deleteDialog.value = false
    documentToDelete.value = null
    await loadDocuments()
    emit('document-deleted')
  } catch (error) {
    console.error('Failed to delete document:', error)
  } finally {
    deletingId.value = null
  }
}

// Expose reload method for parent component
defineExpose({
  loadDocuments
})
</script>

<style scoped>
.document-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.document-item:hover {
  border-color: #1976d2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
