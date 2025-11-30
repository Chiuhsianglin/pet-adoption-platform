<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon left>mdi-file-check</v-icon>
      文件審核狀態
    </v-card-title>

    <v-divider />

    <v-card-text>
      <!-- Overall Progress -->
      <div class="mb-6">
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-subtitle-2">整體進度</span>
          <v-chip
            :color="overallStatusColor"
            size="small"
            variant="flat"
          >
            {{ overallStatusText }}
          </v-chip>
        </div>

        <v-progress-linear
          :model-value="overallProgress"
          :color="overallStatusColor"
          height="8"
          rounded
        />

        <div class="d-flex justify-space-between mt-2 text-caption text-grey">
          <span>已審核：{{ approvedCount }} / {{ totalCount }}</span>
          <span>{{ overallProgress.toFixed(0) }}%</span>
        </div>
      </div>

      <!-- Documents Status List -->
      <v-expansion-panels v-if="documents.length > 0" variant="accordion">
        <v-expansion-panel
          v-for="doc in documents"
          :key="doc.id"
          :value="doc.id"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center" style="width: 100%">
              <!-- Status Icon -->
              <v-icon
                :color="getStatusColor(doc.status)"
                size="small"
                class="mr-3"
              >
                {{ getStatusIcon(doc.status) }}
              </v-icon>

              <!-- Document Info -->
              <div class="flex-grow-1">
                <div class="font-weight-medium">
                  {{ DocumentTypeLabels[doc.document_type as DocumentType] }}
                </div>
                <div class="text-caption text-grey">
                  {{ doc.original_filename }}
                </div>
              </div>

              <!-- Status Chip -->
              <v-chip
                :color="getStatusColor(doc.status)"
                size="small"
                variant="flat"
              >
                {{ DocumentStatusLabels[doc.status as DocumentStatus] }}
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-card variant="outlined" class="mt-2">
              <v-card-text>
                <!-- Document Details -->
                <v-list density="compact">
                  <v-list-item>
                    <template #prepend>
                      <v-icon size="small">mdi-file</v-icon>
                    </template>
                    <v-list-item-title>檔案名稱</v-list-item-title>
                    <v-list-item-subtitle>{{ doc.original_filename }}</v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item>
                    <template #prepend>
                      <v-icon size="small">mdi-file-chart</v-icon>
                    </template>
                    <v-list-item-title>檔案大小</v-list-item-title>
                    <v-list-item-subtitle>{{ formatFileSize(doc.file_size) }}</v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item>
                    <template #prepend>
                      <v-icon size="small">mdi-upload</v-icon>
                    </template>
                    <v-list-item-title>上傳時間</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(doc.uploaded_at) }}</v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item v-if="doc.reviewed_at">
                    <template #prepend>
                      <v-icon size="small">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>審核時間</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(doc.reviewed_at) }}</v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item>
                    <template #prepend>
                      <v-icon size="small">mdi-shield-check</v-icon>
                    </template>
                    <v-list-item-title>安全掃描</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="doc.is_safe ? 'success' : 'error'"
                        size="x-small"
                        variant="flat"
                      >
                        {{ doc.is_safe ? '安全' : '有風險' }}
                      </v-chip>
                      <span class="ml-2 text-caption">
                        {{ doc.security_scan_status }}
                      </span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>

                <!-- Review Notes -->
                <v-alert
                  v-if="doc.review_notes"
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="mt-4"
                >
                  <div class="d-flex align-center">
                    <v-icon left size="small">mdi-note-text</v-icon>
                    <strong>審核意見：</strong>
                  </div>
                  <p class="mt-2 mb-0">{{ doc.review_notes }}</p>
                </v-alert>

                <!-- Status Timeline -->
                <v-timeline
                  v-if="doc.status !== 'pending'"
                  density="compact"
                  class="mt-4"
                  side="end"
                >
                  <v-timeline-item
                    dot-color="success"
                    size="small"
                  >
                    <template #icon>
                      <v-icon size="x-small">mdi-upload</v-icon>
                    </template>
                    <div>
                      <div class="font-weight-medium">文件已上傳</div>
                      <div class="text-caption text-grey">
                        {{ formatDateTime(doc.uploaded_at) }}
                      </div>
                    </div>
                  </v-timeline-item>

                  <v-timeline-item
                    v-if="doc.status === 'reviewing' || doc.status === 'approved' || doc.status === 'rejected'"
                    :dot-color="doc.status === 'reviewing' ? 'primary' : doc.status === 'approved' ? 'success' : 'error'"
                    size="small"
                  >
                    <template #icon>
                      <v-icon size="x-small">
                        {{ doc.status === 'reviewing' ? 'mdi-magnify' : doc.status === 'approved' ? 'mdi-check' : 'mdi-close' }}
                      </v-icon>
                    </template>
                    <div>
                      <div class="font-weight-medium">
                        {{ doc.status === 'reviewing' ? '審核中' : doc.status === 'approved' ? '審核通過' : '審核未通過' }}
                      </div>
                      <div v-if="doc.reviewed_at" class="text-caption text-grey">
                        {{ formatDateTime(doc.reviewed_at) }}
                      </div>
                    </div>
                  </v-timeline-item>

                  <v-timeline-item
                    v-if="doc.status === 'resubmission_required'"
                    dot-color="warning"
                    size="small"
                  >
                    <template #icon>
                      <v-icon size="x-small">mdi-refresh</v-icon>
                    </template>
                    <div>
                      <div class="font-weight-medium">需要重新提交</div>
                      <div v-if="doc.reviewed_at" class="text-caption text-grey">
                        {{ formatDateTime(doc.reviewed_at) }}
                      </div>
                    </div>
                  </v-timeline-item>
                </v-timeline>

                <!-- Actions -->
                <div class="d-flex ga-2 mt-4">
                  <v-btn
                    v-if="isImageFile(doc.mime_type)"
                    variant="tonal"
                    color="primary"
                    size="small"
                    prepend-icon="mdi-eye"
                    @click="$emit('preview', doc)"
                  >
                    預覽
                  </v-btn>

                  <v-btn
                    variant="tonal"
                    color="primary"
                    size="small"
                    prepend-icon="mdi-download"
                    @click="$emit('download', doc)"
                  >
                    下載
                  </v-btn>

                  <v-btn
                    v-if="canResubmit(doc.status)"
                    variant="tonal"
                    color="warning"
                    size="small"
                    prepend-icon="mdi-upload"
                    @click="$emit('resubmit', doc)"
                  >
                    重新上傳
                  </v-btn>

                  <v-btn
                    variant="tonal"
                    color="info"
                    size="small"
                    prepend-icon="mdi-history"
                    @click="$emit('show-versions', doc)"
                  >
                    版本歷史
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Empty State -->
      <v-alert v-else type="info" variant="tonal">
        <div class="d-flex align-center">
          <v-icon left>mdi-information</v-icon>
          <span>尚未上傳任何文件</span>
        </div>
      </v-alert>

      <!-- Summary Statistics -->
      <v-card v-if="documents.length > 0" variant="outlined" class="mt-6">
        <v-card-text>
          <div class="text-subtitle-2 mb-4">審核統計</div>
          
          <v-row>
            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-primary">{{ totalCount }}</div>
                <div class="text-caption text-grey">總文件數</div>
              </div>
            </v-col>

            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-success">{{ approvedCount }}</div>
                <div class="text-caption text-grey">已通過</div>
              </div>
            </v-col>

            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-warning">{{ pendingCount }}</div>
                <div class="text-caption text-grey">待審核</div>
              </div>
            </v-col>

            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-error">{{ rejectedCount }}</div>
                <div class="text-caption text-grey">未通過</div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Help Text -->
      <v-alert type="info" variant="tonal" density="compact" class="mt-4">
        <v-icon left size="small">mdi-lightbulb</v-icon>
        <strong>審核流程說明：</strong>
        <ul class="mt-2 ml-4">
          <li>文件上傳後會自動進行安全掃描</li>
          <li>通過安全掃描後進入人工審核階段</li>
          <li>審核通過的文件才能用於申請流程</li>
          <li>如需重新提交，請先刪除原文件後重新上傳</li>
        </ul>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DocumentResponse, DocumentStatus, DocumentType } from '@/types/document'
import { 
  DocumentStatusLabels, 
  DocumentTypeLabels, 
  DocumentStatusColors,
  formatFileSize 
} from '@/types/document'

interface Props {
  documents: DocumentResponse[]
}

const props = defineProps<Props>()

defineEmits<{
  'preview': [doc: DocumentResponse]
  'download': [doc: DocumentResponse]
  'resubmit': [doc: DocumentResponse]
  'show-versions': [doc: DocumentResponse]
}>()

// Computed
const totalCount = computed(() => props.documents.length)

const approvedCount = computed(() => 
  props.documents.filter(d => d.status === 'approved').length
)

const pendingCount = computed(() => 
  props.documents.filter(d => d.status === 'pending' || d.status === 'reviewing').length
)

const rejectedCount = computed(() => 
  props.documents.filter(d => d.status === 'rejected' || d.status === 'resubmission_required').length
)

const overallProgress = computed(() => {
  if (totalCount.value === 0) return 0
  return (approvedCount.value / totalCount.value) * 100
})

const overallStatusText = computed(() => {
  if (approvedCount.value === totalCount.value) return '全部通過'
  if (rejectedCount.value > 0) return '部分未通過'
  if (pendingCount.value > 0) return '審核中'
  return '待審核'
})

const overallStatusColor = computed(() => {
  if (approvedCount.value === totalCount.value) return 'success'
  if (rejectedCount.value > 0) return 'error'
  if (pendingCount.value > 0) return 'primary'
  return 'warning'
})

// Methods
const getStatusColor = (status: string) => {
  return DocumentStatusColors[status as DocumentStatus] || 'grey'
}

const getStatusIcon = (status: string) => {
  const icons: Record<string, string> = {
    pending: 'mdi-clock-outline',
    reviewing: 'mdi-magnify',
    approved: 'mdi-check-circle',
    rejected: 'mdi-close-circle',
    resubmission_required: 'mdi-refresh'
  }
  return icons[status] || 'mdi-file-document'
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isImageFile = (mimeType: string) => {
  return mimeType.startsWith('image/')
}

const canResubmit = (status: string) => {
  return status === 'rejected' || status === 'resubmission_required'
}
</script>

<style scoped>
.v-expansion-panel-title {
  padding: 16px !important;
}

.v-timeline {
  padding-left: 0;
}
</style>
