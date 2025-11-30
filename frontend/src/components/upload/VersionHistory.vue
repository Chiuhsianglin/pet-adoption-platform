<template>
  <v-dialog v-model="dialog" max-width="800" scrollable>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon left color="primary">mdi-history</v-icon>
        版本歷史
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" @click="dialog = false" />
      </v-card-title>

      <v-divider />

      <!-- Loading State -->
      <v-card-text v-if="loading" class="text-center py-8">
        <v-progress-circular indeterminate color="primary" size="48" />
        <p class="text-grey mt-4">載入版本歷史中...</p>
      </v-card-text>

      <!-- Version List -->
      <v-card-text v-else-if="versions.length > 0" class="pa-0">
        <v-list lines="three">
          <template v-for="(version, index) in versions" :key="version.id">
          <v-list-item
            :class="{ 'bg-primary-lighten-5': version.is_current_version }"
          >
            <template #prepend>
              <v-avatar :color="version.is_current_version ? 'primary' : 'grey-lighten-2'">
                <v-icon :color="version.is_current_version ? 'white' : 'grey'">
                  {{ version.is_current_version ? 'mdi-check-circle' : 'mdi-file-document-outline' }}
                </v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="d-flex align-center">
              版本 {{ version.version }}
              <v-chip
                v-if="version.is_current_version"
                color="primary"
                size="x-small"
                variant="flat"
                class="ml-2"
              >
                當前版本
              </v-chip>
              <v-chip
                v-else
                color="grey"
                size="x-small"
                variant="outlined"
                class="ml-2"
              >
                歷史版本
              </v-chip>
            </v-list-item-title>

            <v-list-item-subtitle>
              <div class="mt-1">
                <v-icon size="small">mdi-file</v-icon>
                {{ version.original_filename }}
                <v-chip size="x-small" variant="text" class="ml-2">
                  {{ formatFileSize(version.file_size) }}
                </v-chip>
              </div>
              <div class="mt-1">
                <v-icon size="small">mdi-clock-outline</v-icon>
                {{ formatDateTime(version.uploaded_at) }}
              </div>
              <div v-if="version.description" class="mt-1 text-caption">
                <v-icon size="small">mdi-note-text</v-icon>
                {{ version.description }}
              </div>
            </v-list-item-subtitle>

            <template #append>
              <div class="d-flex flex-column ga-2">
                <!-- Download Button -->
                <v-btn
                  icon="mdi-download"
                  variant="text"
                  size="small"
                  color="primary"
                  @click="downloadVersion(version)"
                  title="下載此版本"
                />

                <!-- Preview Button (if image) -->
                <v-btn
                  v-if="isImageFile(version.mime_type)"
                  icon="mdi-eye"
                  variant="text"
                  size="small"
                  color="primary"
                  @click="previewVersion(version)"
                  title="預覽此版本"
                />

                <!-- Revert Button (if not current) -->
                <v-btn
                  v-if="!version.is_current_version"
                  icon="mdi-restore"
                  variant="text"
                  size="small"
                  color="warning"
                  @click="confirmRevert(version)"
                  :disabled="reverting"
                  title="恢復此版本"
                />

                <!-- Compare Button (if not first) -->
                <v-btn
                  v-if="index < versions.length - 1"
                  icon="mdi-compare"
                  variant="text"
                  size="small"
                  color="info"
                  @click="compareVersions(version, versions[index + 1])"
                  title="與前一版本比較"
                />
              </div>
            </template>
          </v-list-item>
          
          <v-divider v-if="index < versions.length - 1" />
          </template>
        </v-list>
      </v-card-text>

      <!-- Empty State -->
      <v-card-text v-else class="text-center py-8">
        <v-icon size="64" color="grey-lighten-2">mdi-history</v-icon>
        <p class="text-grey mt-4">沒有版本歷史記錄</p>
      </v-card-text>

      <!-- Error State -->
      <v-card-text v-if="error">
        <v-alert type="error" variant="tonal">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">關閉</v-btn>
      </v-card-actions>
    </v-card>

    <!-- Revert Confirmation Dialog -->
    <v-dialog v-model="revertDialog" max-width="500">
      <v-card>
        <v-card-title class="text-warning">
          <v-icon left>mdi-alert</v-icon>
          確認恢復版本
        </v-card-title>

        <v-card-text>
          <p class="mb-4">
            您確定要恢復到 <strong>版本 {{ revertTarget?.version }}</strong> 嗎？
          </p>
          <p class="text-caption text-grey">
            這將會創建一個新版本，內容與所選版本相同。當前版本將被保留在歷史記錄中。
          </p>

          <v-alert type="info" variant="tonal" class="mt-4">
            <div>
              <strong>版本 {{ revertTarget?.version }} 資訊：</strong>
              <ul class="mt-2">
                <li>檔案名稱：{{ revertTarget?.original_filename }}</li>
                <li>檔案大小：{{ formatFileSize(revertTarget?.file_size || 0) }}</li>
                <li>上傳時間：{{ formatDateTime(revertTarget?.uploaded_at) }}</li>
              </ul>
            </div>
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="revertDialog = false" :disabled="reverting">
            取消
          </v-btn>
          <v-btn
            color="warning"
            variant="elevated"
            @click="revertToVersion"
            :loading="reverting"
          >
            確認恢復
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Version Comparison Dialog -->
    <v-dialog v-model="compareDialog" max-width="900">
      <v-card>
        <v-card-title>
          <v-icon left>mdi-compare</v-icon>
          版本比較
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-row>
            <!-- Version 1 -->
            <v-col cols="6">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1 bg-primary-lighten-5">
                  版本 {{ compareVersion1?.version }}
                  <v-chip
                    v-if="compareVersion1?.is_current_version"
                    color="primary"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    當前
                  </v-chip>
                </v-card-title>
                <v-card-text>
                  <div class="version-info">
                    <p><strong>檔案名稱：</strong>{{ compareVersion1?.original_filename }}</p>
                    <p><strong>檔案大小：</strong>{{ formatFileSize(compareVersion1?.file_size || 0) }}</p>
                    <p><strong>上傳時間：</strong>{{ formatDateTime(compareVersion1?.uploaded_at) }}</p>
                    <p><strong>MIME 類型：</strong>{{ compareVersion1?.mime_type }}</p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Version 2 -->
            <v-col cols="6">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1 bg-grey-lighten-4">
                  版本 {{ compareVersion2?.version }}
                </v-card-title>
                <v-card-text>
                  <div class="version-info">
                    <p><strong>檔案名稱：</strong>{{ compareVersion2?.original_filename }}</p>
                    <p><strong>檔案大小：</strong>{{ formatFileSize(compareVersion2?.file_size || 0) }}</p>
                    <p><strong>上傳時間：</strong>{{ formatDateTime(compareVersion2?.uploaded_at) }}</p>
                    <p><strong>MIME 類型：</strong>{{ compareVersion2?.mime_type }}</p>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Differences -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="text-subtitle-1">
              <v-icon left>mdi-delta</v-icon>
              差異分析
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item v-if="sizeDifference !== 0">
                  <v-list-item-title>
                    檔案大小變化：
                    <v-chip
                      :color="sizeDifference > 0 ? 'success' : 'error'"
                      size="small"
                      variant="flat"
                      class="ml-2"
                    >
                      {{ sizeDifference > 0 ? '+' : '' }}{{ formatFileSize(Math.abs(sizeDifference)) }}
                    </v-chip>
                  </v-list-item-title>
                </v-list-item>
                <v-list-item v-if="compareVersion1?.original_filename !== compareVersion2?.original_filename">
                  <v-list-item-title>
                    檔案名稱已變更
                  </v-list-item-title>
                </v-list-item>
                <v-list-item v-if="timeDifference">
                  <v-list-item-title>
                    時間間隔：{{ timeDifference }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="compareDialog = false">關閉</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getDocumentVersions, downloadDocument } from '@/api/document'
import type { DocumentResponse } from '@/types/document'
import { formatFileSize } from '@/types/document'

interface Props {
  documentId: number | null
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'version-reverted': []
}>()

// State
const versions = ref<DocumentResponse[]>([])
const loading = ref(false)
const error = ref('')
const reverting = ref(false)
const revertDialog = ref(false)
const revertTarget = ref<DocumentResponse | null>(null)
const compareDialog = ref(false)
const compareVersion1 = ref<DocumentResponse | null>(null)
const compareVersion2 = ref<DocumentResponse | null>(null)

// Computed
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const sizeDifference = computed(() => {
  if (!compareVersion1.value || !compareVersion2.value) return 0
  return compareVersion1.value.file_size - compareVersion2.value.file_size
})

const timeDifference = computed(() => {
  if (!compareVersion1.value || !compareVersion2.value) return ''
  const diff = new Date(compareVersion1.value.uploaded_at).getTime() - 
                new Date(compareVersion2.value.uploaded_at).getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days} 天`
  if (hours > 0) return `${hours} 小時`
  return `${Math.floor(diff / (1000 * 60))} 分鐘`
})

// Methods
const loadVersions = async () => {
  if (!props.documentId) return
  
  loading.value = true
  error.value = ''
  
  try {
    versions.value = await getDocumentVersions(props.documentId)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '載入版本歷史失敗'
    console.error('Failed to load versions:', err)
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateString: string | undefined) => {
  if (!dateString) return ''
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

const downloadVersion = async (version: DocumentResponse) => {
  try {
    await downloadDocument(version.id)
  } catch (err) {
    console.error('Failed to download version:', err)
  }
}

const previewVersion = (version: DocumentResponse) => {
  // Open preview in new window
  if (version.preview_url) {
    window.open(version.preview_url, '_blank')
  }
}

const confirmRevert = (version: DocumentResponse) => {
  revertTarget.value = version
  revertDialog.value = true
}

const revertToVersion = async () => {
  if (!revertTarget.value) return
  
  reverting.value = true
  
  try {
    // TODO: Implement revert API call
    // await revertDocumentVersion(revertTarget.value.id)
    
    // For now, just show success message
    alert('版本恢復功能開發中')
    
    revertDialog.value = false
    emit('version-reverted')
    await loadVersions()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '恢復版本失敗'
    console.error('Failed to revert version:', err)
  } finally {
    reverting.value = false
  }
}

const compareVersions = (version1: DocumentResponse, version2: DocumentResponse) => {
  compareVersion1.value = version1
  compareVersion2.value = version2
  compareDialog.value = true
}

// Watch for dialog open
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.documentId) {
    loadVersions()
  }
})

// Load on mount if dialog is already open
watch(() => props.documentId, (newVal) => {
  if (newVal && props.modelValue) {
    loadVersions()
  }
}, { immediate: true })
</script>

<style scoped>
.version-info p {
  margin-bottom: 8px;
  font-size: 0.875rem;
}

.version-info p:last-child {
  margin-bottom: 0;
}
</style>
