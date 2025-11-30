<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="1400"
    scrollable
    persistent
  >
    <v-card v-if="application">
      <!-- Header -->
      <v-card-title class="d-flex align-center justify-space-between bg-primary">
        <div>
          <h3 class="text-h5">審核申請 #{{ application.application_id }}</h3>
          <div class="text-body-2 mt-1">
            {{ application.applicant_name }} 申請領養 {{ application.pet_name }}
          </div>
        </div>
        <v-btn
          icon
          variant="text"
          @click="closeModal"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-row no-gutters>
          <!-- Left Column: Application Details -->
          <v-col cols="12" lg="8" class="pa-4" style="max-height: 80vh; overflow-y: auto;">
            <!-- Application Info -->
            <v-card variant="outlined" class="mb-4">
              <v-card-title class="text-subtitle-1 bg-grey-lighten-4">
                <v-icon class="mr-2">mdi-information</v-icon>
                申請資訊
              </v-card-title>
              <v-card-text>
                <v-row dense>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">申請ID</div>
                    <div class="font-weight-bold">#{{ application.application_id }}</div>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">狀態</div>
                    <v-chip size="small" :color="getStatusColor(application.status)">
                      {{ getStatusDisplayName(application.status) }}
                    </v-chip>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">提交時間</div>
                    <div>{{ formatDate(application.submitted_at) }}</div>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">等待天數</div>
                    <div class="font-weight-bold text-warning">{{ application.days_since_submitted }} 天</div>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">優先級</div>
                    <v-chip size="small" :color="getPriorityColor(application.priority)">
                      {{ getPriorityText(application.priority) }}
                    </v-chip>
                  </v-col>
                  <v-col cols="6" sm="3">
                    <div class="text-caption text-grey">文件狀態</div>
                    <v-chip 
                      size="small" 
                      :color="application.documents_complete ? 'success' : 'warning'"
                    >
                      {{ application.total_documents }}/3
                    </v-chip>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>

            <!-- Timeline -->
            <div class="mb-4">
              <ApplicationTimeline :application-id="application.application_id" />
            </div>

            <!-- Comments -->
            <div class="mb-4">
              <ReviewComments 
                :application-id="application.application_id"
                :can-resolve="true"
                :show-internal="true"
              />
            </div>

            <!-- Document Requests (Story 3.5) -->
            <div class="mb-4">
              <DocumentRequestPanel 
                :application-id="application.id"
                @request-created="handleRequestCreated"
              />
            </div>

            <!-- Decision History -->
            <v-card variant="outlined" class="mb-4">
              <v-card-title class="text-subtitle-1 bg-grey-lighten-4">
                <v-icon class="mr-2">mdi-history</v-icon>
                審核決策歷史
              </v-card-title>
              <v-card-text>
                <v-timeline v-if="decisionHistory.length > 0" density="compact" side="end">
                  <v-timeline-item
                    v-for="decision in decisionHistory"
                    :key="decision.id"
                    :dot-color="getDecisionColor(decision.decision)"
                    size="small"
                  >
                    <v-card variant="outlined">
                      <v-card-text class="py-2">
                        <div class="d-flex align-center justify-space-between mb-2">
                          <v-chip 
                            size="small" 
                            :color="getDecisionColor(decision.decision)"
                          >
                            {{ getDecisionDisplayName(decision.decision) }}
                          </v-chip>
                          <span class="text-caption text-grey">
                            {{ formatDateTime(decision.created_at) }}
                          </span>
                        </div>
                        
                        <div v-if="decision.decision_reason" class="text-body-2 mb-1">
                          <strong>原因:</strong> {{ decision.decision_reason }}
                        </div>
                        
                        <div v-if="decision.recommendations" class="text-body-2 mb-1">
                          <strong>建議:</strong> {{ decision.recommendations }}
                        </div>
                        
                        <div v-if="decision.overall_score !== null" class="text-body-2 mb-1">
                          <strong>評分:</strong> {{ decision.overall_score }}/100
                        </div>
                        
                        <div class="d-flex align-center text-caption text-grey mt-2">
                          <v-icon size="small" class="mr-1">mdi-account</v-icon>
                          {{ decision.reviewer_name || '審核員' }}
                          <span v-if="decision.time_spent_minutes" class="ml-3">
                            <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                            {{ formatDuration(decision.time_spent_minutes) }}
                          </span>
                          <v-chip v-if="decision.is_final" size="x-small" color="primary" class="ml-2">
                            最終決策
                          </v-chip>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-timeline-item>
                </v-timeline>
                
                <v-alert v-else type="info" variant="tonal" density="compact">
                  尚無審核決策記錄
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Right Column: Decision Form -->
          <v-col 
            cols="12" 
            lg="4" 
            class="pa-4 bg-grey-lighten-5" 
            style="max-height: 80vh; overflow-y: auto;"
          >
            <h3 class="text-h6 mb-4">
              <v-icon class="mr-2">mdi-gavel</v-icon>
              提交審核決策
            </h3>

            <v-form ref="decisionForm" v-model="formValid">
              <!-- Decision Type -->
              <v-select
                v-model="newDecision.decision"
                :items="decisionOptions"
                label="決策結果 *"
                variant="outlined"
                :rules="[v => !!v || '請選擇決策結果']"
                class="mb-3"
              />

              <!-- Overall Score -->
              <div class="mb-4">
                <label class="text-body-2 mb-2 d-block">綜合評分 (0-100)</label>
                <v-slider
                  v-model="newDecision.overall_score"
                  :min="0"
                  :max="100"
                  :step="1"
                  thumb-label="always"
                  color="primary"
                  class="mb-2"
                />
                <div class="text-caption text-grey">
                  當前分數: {{ newDecision.overall_score }}/100
                </div>
              </div>

              <!-- Decision Reason -->
              <v-textarea
                v-model="newDecision.decision_reason"
                label="決策原因 *"
                variant="outlined"
                rows="4"
                :rules="[v => !!v || '請填寫決策原因']"
                placeholder="請詳細說明做出此決策的原因..."
                class="mb-3"
              />

              <!-- Recommendations -->
              <v-textarea
                v-model="newDecision.recommendations"
                label="建議事項"
                variant="outlined"
                rows="3"
                placeholder="給申請人或團隊的建議..."
                class="mb-3"
              />

              <!-- Conditions (for approved) -->
              <div v-if="newDecision.decision === 'approved'" class="mb-4">
                <label class="text-body-2 mb-2 d-block">批准附加條件</label>
                <v-combobox
                  v-model="newDecision.conditions"
                  chips
                  multiple
                  variant="outlined"
                  placeholder="輸入條件後按 Enter"
                  hint="例如: 需要家訪、需要補充文件等"
                  persistent-hint
                >
                  <template #chip="{ item, props }">
                    <v-chip v-bind="props" closable>
                      {{ item.title }}
                    </v-chip>
                  </template>
                </v-combobox>
              </div>

              <!-- Is Final Decision -->
              <v-switch
                v-model="newDecision.is_final"
                label="這是最終決策"
                color="primary"
                hint="最終決策將自動更新申請狀態"
                persistent-hint
                class="mb-4"
              />

              <!-- Action Buttons -->
              <v-divider class="my-4" />

              <div class="d-flex flex-column gap-2">
                <v-btn
                  color="primary"
                  size="large"
                  block
                  :loading="submitting"
                  :disabled="!formValid"
                  @click="submitDecision"
                >
                  <v-icon start>mdi-check</v-icon>
                  提交決策
                </v-btn>

                <v-btn
                  variant="outlined"
                  size="large"
                  block
                  @click="resetForm"
                >
                  <v-icon start>mdi-refresh</v-icon>
                  重置表單
                </v-btn>

                <v-btn
                  variant="text"
                  size="large"
                  block
                  @click="closeModal"
                >
                  取消
                </v-btn>
              </div>
            </v-form>

            <!-- Help Card -->
            <v-card variant="outlined" color="info" class="mt-4">
              <v-card-text class="text-caption">
                <div class="font-weight-bold mb-2">
                  <v-icon size="small" class="mr-1">mdi-help-circle</v-icon>
                  決策指引
                </div>
                <ul class="ml-4">
                  <li><strong>批准:</strong> 申請人符合所有條件</li>
                  <li><strong>拒絕:</strong> 申請人不符合要求</li>
                  <li><strong>需補充資料:</strong> 需要更多資訊</li>
                  <li><strong>待定:</strong> 暫時無法決定</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { 
  submitReviewDecision,
  getReviewDecisionHistory,
  getPriorityColor,
  getDecisionDisplayName,
  getDecisionColor,
  formatDuration,
  type ApplicationQueueItem,
  type ReviewDecisionCreate,
  type ReviewDecision
} from '@/api/review'
import { getStatusDisplayName, getStatusColor } from '@/api/application-status'
import ApplicationTimeline from '@/components/status/ApplicationTimeline.vue'
import ReviewComments from '@/components/status/ReviewComments.vue'
import DocumentRequestPanel from '@/components/review/DocumentRequestPanel.vue'

// ==================== Props & Emits ====================

const props = defineProps<{
  modelValue: boolean
  application: ApplicationQueueItem | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'decision-submitted': []
}>()

// ==================== Data ====================

const formValid = ref(false)
const submitting = ref(false)
const decisionHistory = ref<ReviewDecision[]>([])
const reviewStartTime = ref<Date | null>(null)

const newDecision = ref<ReviewDecisionCreate>({
  decision: 'pending',
  decision_reason: '',
  recommendations: '',
  overall_score: 70,
  conditions: [],
  is_final: false,
})

const decisionOptions = [
  { title: '批准', value: 'approved' },
  { title: '拒絕', value: 'rejected' },
  { title: '需補充資料', value: 'needs_info' },
  { title: '待定', value: 'pending' },
]

// ==================== Methods ====================

const loadDecisionHistory = async () => {
  if (!props.application) return
  
  try {
    decisionHistory.value = await getReviewDecisionHistory(props.application.application_id)
  } catch (err: any) {
    console.error('Failed to load decision history:', err)
  }
}

const submitDecision = async () => {
  if (!props.application || !formValid.value) return
  
  submitting.value = true
  
  try {
    await submitReviewDecision(
      props.application.application_id,
      newDecision.value,
      reviewStartTime.value || undefined
    )
    
    emit('decision-submitted')
    resetForm()
  } catch (err: any) {
    console.error('Failed to submit decision:', err)
    alert(err.response?.data?.message || '提交決策失敗')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  newDecision.value = {
    decision: 'pending',
    decision_reason: '',
    recommendations: '',
    overall_score: 70,
    conditions: [],
    is_final: false,
  }
}

const closeModal = () => {
  emit('update:modelValue', false)
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getPriorityText = (priority: string): string => {
  const texts: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '緊急',
  }
  return texts[priority] || priority
}

const handleRequestCreated = () => {
  // 當創建補件請求時，可以做一些處理（例如刷新資料）
  console.log('Document request created')
}

// ==================== Watchers ====================

watch(() => props.modelValue, (newVal) => {
  if (newVal && props.application) {
    reviewStartTime.value = new Date()
    loadDecisionHistory()
  } else {
    reviewStartTime.value = null
  }
})
</script>

<style scoped>
.bg-primary {
  background-color: rgb(var(--v-theme-primary)) !important;
  color: white !important;
}

.bg-grey-lighten-4 {
  background-color: rgb(var(--v-theme-grey-lighten-4)) !important;
}

.bg-grey-lighten-5 {
  background-color: rgb(var(--v-theme-grey-lighten-5)) !important;
}
</style>
