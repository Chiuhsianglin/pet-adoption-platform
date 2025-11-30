<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn
          :to="`/applications/${applicationId}`"
          variant="text"
          prepend-icon="mdi-arrow-left"
          class="mb-4"
        >
          返回申請詳情
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" />
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- Main Content -->
    <template v-else-if="confirmationData">
      <v-row>
        <v-col cols="12" md="8">
          <!-- Confirmation Info Card -->
          <v-card class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon icon="mdi-check-circle" class="mr-2" />
              確認資訊
            </v-card-title>
            <v-card-text>
              <v-chip
                :color="getConfirmationStatusColor(confirmationData.confirmation.status)"
                class="mb-4"
              >
                {{ getConfirmationStatusDisplayName(confirmationData.confirmation.status) }}
              </v-chip>

              <v-list>
                <v-list-item v-if="confirmationData.confirmation.approval_notes">
                  <v-list-item-title>核准備註</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ confirmationData.confirmation.approval_notes }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="confirmationData.confirmation.conditions">
                  <v-list-item-title>核准條件</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ confirmationData.confirmation.conditions }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="confirmationData.confirmation.approved_at">
                  <v-list-item-title>核准時間</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatDateTime(confirmationData.confirmation.approved_at) }}
                  </v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="confirmationData.confirmation.completed_at">
                  <v-list-item-title>完成時間</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatDateTime(confirmationData.confirmation.completed_at) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>

              <!-- Approval Section (Shelter/Admin only) -->
              <template v-if="canApprove">
                <v-divider class="my-4" />
                <v-form @submit.prevent="handleApprove">
                  <v-textarea
                    v-model="approvalNotes"
                    label="核准備註 *"
                    rows="3"
                    :rules="[v => !!v || '請輸入核准備註']"
                    required
                  />
                  <v-textarea
                    v-model="approvalConditions"
                    label="核准條件 (選填)"
                    rows="2"
                    hint="例如：需在交接前完成居家環境檢查"
                  />
                  <v-btn
                    type="submit"
                    color="success"
                    :loading="approving"
                    class="mt-2"
                  >
                    核准確認
                  </v-btn>
                </v-form>
              </template>
            </v-card-text>
          </v-card>

          <!-- Handover Schedule Card -->
          <v-card v-if="confirmationData.handover || canScheduleHandover">
            <v-card-title class="d-flex align-center">
              <v-icon icon="mdi-calendar-clock" class="mr-2" />
              交接安排
            </v-card-title>
            <v-card-text>
              <!-- Existing Handover -->
              <template v-if="confirmationData.handover">
                <v-chip
                  :color="getHandoverStatusColor(confirmationData.handover.status)"
                  class="mb-4"
                >
                  {{ getHandoverStatusDisplayName(confirmationData.handover.status) }}
                </v-chip>

                <v-list>
                  <v-list-item>
                    <v-list-item-title>交接日期</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ formatDate(confirmationData.handover.handover_date) }}
                      <template v-if="confirmationData.handover.handover_time">
                        {{ confirmationData.handover.handover_time }}
                      </template>
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-title>地點</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ confirmationData.handover.location }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item v-if="confirmationData.handover.contact_person">
                    <v-list-item-title>聯絡人</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ confirmationData.handover.contact_person }}
                      <template v-if="confirmationData.handover.contact_phone">
                        - {{ confirmationData.handover.contact_phone }}
                      </template>
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item v-if="confirmationData.handover.items_checklist">
                    <v-list-item-title>交接項目</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ confirmationData.handover.items_checklist }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item v-if="confirmationData.handover.special_instructions">
                    <v-list-item-title>特別說明</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ confirmationData.handover.special_instructions }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>

                <!-- Update Handover (Shelter/Admin only) -->
                <template v-if="canUpdateHandover">
                  <v-divider class="my-4" />
                  <v-btn
                    v-if="!showUpdateForm"
                    @click="showUpdateForm = true"
                    color="primary"
                    variant="outlined"
                  >
                    更新交接資訊
                  </v-btn>
                  <v-form v-else @submit.prevent="handleUpdateHandover">
                    <v-select
                      v-model="updateHandoverData.status"
                      :items="handoverStatusOptions"
                      label="交接狀態"
                      item-title="label"
                      item-value="value"
                    />
                    <v-textarea
                      v-if="updateHandoverData.status === 'completed'"
                      v-model="updateHandoverData.completed_notes"
                      label="完成備註"
                      rows="2"
                    />
                    <div class="d-flex gap-2">
                      <v-btn type="submit" color="primary" :loading="updating">
                        確認更新
                      </v-btn>
                      <v-btn @click="showUpdateForm = false" variant="outlined">
                        取消
                      </v-btn>
                    </div>
                  </v-form>
                </template>
              </template>

              <!-- Create Handover Form (Shelter/Admin only) -->
              <template v-else-if="canScheduleHandover">
                <v-form @submit.prevent="handleCreateHandover">
                  <v-text-field
                    v-model="handoverData.handover_date"
                    label="交接日期 *"
                    type="date"
                    :rules="[v => !!v || '請選擇交接日期']"
                    required
                  />
                  <v-text-field
                    v-model="handoverData.handover_time"
                    label="交接時間"
                    type="time"
                  />
                  <v-text-field
                    v-model="handoverData.location"
                    label="交接地點 *"
                    :rules="[v => !!v || '請輸入交接地點']"
                    required
                  />
                  <v-text-field
                    v-model="handoverData.contact_person"
                    label="聯絡人"
                  />
                  <v-text-field
                    v-model="handoverData.contact_phone"
                    label="聯絡電話"
                  />
                  <v-combobox
                    v-model="handoverData.items_checklist"
                    :items="COMMON_HANDOVER_ITEMS"
                    label="交接項目"
                    multiple
                    chips
                    hint="可從列表選擇或自行輸入"
                    persistent-hint
                  />
                  <v-textarea
                    v-model="handoverData.special_instructions"
                    label="特別說明"
                    rows="2"
                  />
                  <v-btn
                    type="submit"
                    color="primary"
                    :loading="scheduling"
                    class="mt-2"
                  >
                    安排交接
                  </v-btn>
                </v-form>
              </template>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Actions Sidebar -->
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>操作</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-if="canComplete"
                  @click="handleComplete"
                  :disabled="completing"
                >
                  <template #prepend>
                    <v-icon icon="mdi-check-all" />
                  </template>
                  <v-list-item-title>完成確認流程</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Status Timeline -->
          <v-card class="mt-4">
            <v-card-title>流程狀態</v-card-title>
            <v-card-text>
              <v-timeline density="compact" side="end">
                <v-timeline-item
                  dot-color="success"
                  size="small"
                >
                  <template #opposite>
                    <div class="text-caption">
                      {{ formatDateTime(confirmationData.confirmation.created_at) }}
                    </div>
                  </template>
                  <div>
                    <div class="font-weight-bold">確認創建</div>
                  </div>
                </v-timeline-item>

                <v-timeline-item
                  v-if="confirmationData.confirmation.approved_at"
                  dot-color="success"
                  size="small"
                >
                  <template #opposite>
                    <div class="text-caption">
                      {{ formatDateTime(confirmationData.confirmation.approved_at) }}
                    </div>
                  </template>
                  <div>
                    <div class="font-weight-bold">確認核准</div>
                  </div>
                </v-timeline-item>

                <v-timeline-item
                  v-if="confirmationData.handover"
                  dot-color="primary"
                  size="small"
                >
                  <template #opposite>
                    <div class="text-caption">
                      {{ formatDateTime(confirmationData.handover.created_at) }}
                    </div>
                  </template>
                  <div>
                    <div class="font-weight-bold">交接安排</div>
                  </div>
                </v-timeline-item>

                <v-timeline-item
                  v-if="confirmationData.confirmation.completed_at"
                  dot-color="info"
                  size="small"
                >
                  <template #opposite>
                    <div class="text-caption">
                      {{ formatDateTime(confirmationData.confirmation.completed_at) }}
                    </div>
                  </template>
                  <div>
                    <div class="font-weight-bold">流程完成</div>
                  </div>
                </v-timeline-item>
              </v-timeline>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  getConfirmation,
  approveConfirmation,
  createHandover,
  updateHandover,
  completeConfirmation,
  getConfirmationStatusDisplayName,
  getConfirmationStatusColor,
  getHandoverStatusDisplayName,
  getHandoverStatusColor,
  COMMON_HANDOVER_ITEMS,
  type ConfirmationWithHandover,
  type CreateHandoverRequest,
  type UpdateHandoverRequest
} from '@/api/confirmations'

const route = useRoute()
const authStore = useAuthStore()

const applicationId = computed(() => Number(route.params.id))

// State
const loading = ref(false)
const error = ref<string | null>(null)
const confirmationData = ref<ConfirmationWithHandover | null>(null)

// Approval form
const approving = ref(false)
const approvalNotes = ref('')
const approvalConditions = ref('')

// Handover form
const scheduling = ref(false)
const handoverData = ref<CreateHandoverRequest>({
  handover_date: '',
  location: '',
  items_checklist: ''
})

// Update handover
const updating = ref(false)
const showUpdateForm = ref(false)
const updateHandoverData = ref<UpdateHandoverRequest>({
  status: 'scheduled'
})

const completing = ref(false)

// Computed
const canApprove = computed(() => {
  if (!authStore.user) return false
  if (!confirmationData.value) return false
  const isAuthorized = ['shelter', 'admin'].includes(authStore.user.role)
  const isPending = confirmationData.value.confirmation.status === 'pending'
  return isAuthorized && isPending
})

const canScheduleHandover = computed(() => {
  if (!authStore.user) return false
  if (!confirmationData.value) return false
  const isAuthorized = ['shelter', 'admin'].includes(authStore.user.role)
  const isApproved = confirmationData.value.confirmation.status === 'approved'
  const noHandover = !confirmationData.value.handover
  return isAuthorized && isApproved && noHandover
})

const canUpdateHandover = computed(() => {
  if (!authStore.user) return false
  if (!confirmationData.value?.handover) return false
  const isAuthorized = ['shelter', 'admin'].includes(authStore.user.role)
  const notCancelled = confirmationData.value.handover.status !== 'cancelled'
  return isAuthorized && notCancelled
})

const canComplete = computed(() => {
  if (!authStore.user) return false
  if (!confirmationData.value) return false
  const isAuthorized = ['shelter', 'admin'].includes(authStore.user.role)
  const isApproved = confirmationData.value.confirmation.status === 'approved'
  const notCompleted = confirmationData.value.confirmation.status !== 'completed'
  return isAuthorized && isApproved && notCompleted
})

const handoverStatusOptions = [
  { label: '已安排', value: 'scheduled' },
  { label: '進行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

// Methods
async function loadConfirmation() {
  loading.value = true
  error.value = null
  
  try {
    confirmationData.value = await getConfirmation(applicationId.value)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '載入確認資訊失敗'
  } finally {
    loading.value = false
  }
}

async function handleApprove() {
  if (!confirmationData.value) return
  
  approving.value = true
  
  try {
    await approveConfirmation(confirmationData.value.confirmation.id, {
      approval_notes: approvalNotes.value,
      conditions: approvalConditions.value || undefined
    })
    
    await loadConfirmation()
    approvalNotes.value = ''
    approvalConditions.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.detail || '核准失敗'
  } finally {
    approving.value = false
  }
}

async function handleCreateHandover() {
  if (!confirmationData.value) return
  
  scheduling.value = true
  
  try {
    // Convert items_checklist array to string
    const items = Array.isArray(handoverData.value.items_checklist)
      ? handoverData.value.items_checklist.join('\n')
      : handoverData.value.items_checklist
    
    await createHandover(confirmationData.value.confirmation.id, {
      ...handoverData.value,
      items_checklist: items
    })
    
    await loadConfirmation()
    
    // Reset form
    handoverData.value = {
      handover_date: '',
      location: '',
      items_checklist: ''
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '安排交接失敗'
  } finally {
    scheduling.value = false
  }
}

async function handleUpdateHandover() {
  if (!confirmationData.value?.handover) return
  
  updating.value = true
  
  try {
    await updateHandover(confirmationData.value.handover.id, updateHandoverData.value)
    await loadConfirmation()
    showUpdateForm.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '更新交接資訊失敗'
  } finally {
    updating.value = false
  }
}

async function handleComplete() {
  if (!confirmationData.value) return
  if (!confirm('確定要完成確認流程嗎？')) return
  
  completing.value = true
  
  try {
    await completeConfirmation(confirmationData.value.confirmation.id)
    await loadConfirmation()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '完成確認失敗'
  } finally {
    completing.value = false
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-TW')
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-TW')
}

onMounted(() => {
  loadConfirmation()
})
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>
