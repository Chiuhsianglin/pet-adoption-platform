<template>
  <v-card class="document-request-panel">
    <v-card-title class="d-flex align-center justify-space-between">
      <span>
        <v-icon class="mr-2">mdi-file-document-multiple</v-icon>
        補件請求
      </span>
      <v-btn
        v-if="canCreateRequest"
        color="primary"
        size="small"
        prepend-icon="mdi-plus"
        @click="openCreateDialog"
      >
        新增補件請求
      </v-btn>
    </v-card-title>

    <v-card-text>
      <!-- 補件請求列表 -->
      <v-list v-if="requests.length > 0">
        <v-list-item
          v-for="request in requests"
          :key="request.id"
          class="mb-2"
        >
          <template v-slot:prepend>
            <v-avatar :color="getStatusColor(request.status)">
              <v-icon color="white">mdi-file-document</v-icon>
            </v-avatar>
          </template>

          <v-list-item-title>
            {{ request.requested_documents.join('、') }}
            <v-chip
              :color="getStatusColor(request.status)"
              size="small"
              class="ml-2"
            >
              {{ getStatusDisplayName(request.status) }}
            </v-chip>
          </v-list-item-title>

          <v-list-item-subtitle class="mt-1">
            {{ request.request_reason }}
          </v-list-item-subtitle>

          <v-list-item-subtitle v-if="request.due_date" class="mt-1">
            <v-icon size="small">mdi-calendar-clock</v-icon>
            截止日期: {{ formatDate(request.due_date) }}
          </v-list-item-subtitle>

          <v-list-item-subtitle class="mt-1 text-caption">
            請求時間: {{ formatDateTime(request.created_at) }}
          </v-list-item-subtitle>

          <v-divider class="mt-2" />
        </v-list-item>
      </v-list>

      <v-alert v-else type="info" variant="tonal">
        目前沒有補件請求
      </v-alert>
    </v-card-text>

    <!-- 創建補件請求對話框 -->
    <v-dialog v-model="createDialogOpen" max-width="600">
      <v-card>
        <v-card-title>新增補件請求</v-card-title>
        <v-card-text>
          <v-form ref="formRef" v-model="formValid">
            <!-- 文件類型選擇 -->
            <v-combobox
              v-model="newRequest.requested_documents"
              :items="COMMON_DOCUMENT_TYPES"
              label="請求的文件類型"
              multiple
              chips
              closable-chips
              hint="可以選擇或輸入自訂文件類型"
              :rules="[v => (v && v.length > 0) || '請至少選擇一個文件類型']"
            />

            <!-- 請求原因 -->
            <v-textarea
              v-model="newRequest.request_reason"
              label="請求原因"
              rows="3"
              :rules="[v => !!v || '請輸入請求原因']"
              class="mt-4"
            />

            <!-- 截止日期 -->
            <v-text-field
              v-model="newRequest.due_date"
              label="截止日期（選填）"
              type="date"
              hint="設定補件截止日期"
              class="mt-4"
            />
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn @click="createDialogOpen = false">取消</v-btn>
          <v-btn
            color="primary"
            :loading="submitting"
            :disabled="!formValid"
            @click="submitRequest"
          >
            送出請求
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  getDocumentRequests,
  createDocumentRequest,
  getStatusDisplayName,
  getStatusColor,
  COMMON_DOCUMENT_TYPES,
  type DocumentRequest,
  type DocumentRequestCreate
} from '@/api/documentRequests'

// ===== Props =====
const props = defineProps<{
  applicationId: number
}>()

// ===== Emits =====
const emit = defineEmits<{
  requestCreated: []
}>()

// ===== State =====
const authStore = useAuthStore()
const requests = ref<DocumentRequest[]>([])
const createDialogOpen = ref(false)
const formRef = ref()
const formValid = ref(false)
const submitting = ref(false)

const newRequest = ref<DocumentRequestCreate>({
  requested_documents: [],
  request_reason: '',
  due_date: undefined
})

// ===== Computed =====
const canCreateRequest = computed(() => {
  return authStore.userRole === 'shelter' || authStore.userRole === 'admin'
})

// ===== Methods =====
async function loadRequests() {
  try {
    const response = await getDocumentRequests(props.applicationId)
    requests.value = response.requests
  } catch (error) {
    console.error('Failed to load document requests:', error)
  }
}

function openCreateDialog() {
  newRequest.value = {
    requested_documents: [],
    request_reason: '',
    due_date: undefined
  }
  createDialogOpen.value = true
}

async function submitRequest() {
  if (!formValid.value) return

  submitting.value = true
  try {
    await createDocumentRequest(props.applicationId, newRequest.value)
    createDialogOpen.value = false
    await loadRequests()
    emit('requestCreated')
  } catch (error) {
    console.error('Failed to create document request:', error)
    alert('創建補件請求失敗')
  } finally {
    submitting.value = false
  }
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('zh-TW')
}

function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-TW')
}

// ===== Lifecycle =====
onMounted(() => {
  loadRequests()
})
</script>

<style scoped>
.document-request-panel {
  height: 100%;
}
</style>
