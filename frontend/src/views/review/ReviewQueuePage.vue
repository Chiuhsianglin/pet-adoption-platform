<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 mb-2">申請審核佇列</h1>
            <p class="text-body-2 text-grey">管理和審核領養申請</p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            @click="refreshData"
            :loading="loading"
          >
            重新整理
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards - Loading Skeleton -->
    <v-row v-if="!dashboard && loading" class="mb-4">
      <v-col v-for="i in 4" :key="i" cols="12" sm="6" md="3">
        <v-card>
          <v-card-text>
            <v-skeleton-loader type="heading" />
            <v-skeleton-loader type="text" width="80" class="mt-2" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row v-if="dashboard" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card color="warning" variant="tonal">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h4 font-weight-bold">{{ dashboard.statistics.pending_count }}</div>
                <div class="text-body-2">待審核</div>
              </div>
              <v-icon size="48" color="warning">mdi-clock-alert</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="success" variant="tonal">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h4 font-weight-bold">{{ dashboard.statistics.today_completed }}</div>
                <div class="text-body-2">今日完成</div>
              </div>
              <v-icon size="48" color="success">mdi-check-circle</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="info" variant="tonal">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h4 font-weight-bold">{{ dashboard.statistics.week_completed }}</div>
                <div class="text-body-2">本週完成</div>
              </div>
              <v-icon size="48" color="info">mdi-calendar-week</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" variant="tonal">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h4 font-weight-bold">{{ dashboard.statistics.approval_rate.toFixed(0) }}%</div>
                <div class="text-body-2">批准率</div>
              </div>
              <v-icon size="48" color="primary">mdi-chart-line</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Average Processing Time -->
    <v-row v-if="dashboard" class="mb-4">
      <v-col cols="12">
        <v-alert color="info" variant="tonal" density="compact">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-clock-outline</v-icon>
            <span>平均處理時間: <strong>{{ formatDuration(dashboard.statistics.avg_processing_time_minutes) }}</strong></span>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Filter and Search -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-select
          v-model="statusFilter"
          :items="statusFilterOptions"
          label="狀態篩選"
          variant="outlined"
          density="compact"
          hide-details
          @update:model-value="loadQueue"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="priorityFilter"
          :items="priorityFilterOptions"
          label="優先級篩選"
          variant="outlined"
          density="compact"
          hide-details
          @update:model-value="applyFilters"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="perPage"
          :items="[10, 20, 50, 100]"
          label="每頁顯示"
          variant="outlined"
          density="compact"
          hide-details
          @update:model-value="loadQueue"
        />
      </v-col>
    </v-row>

    <!-- Queue Table -->
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>審核佇列</span>
        <v-chip v-if="queueData" size="small">
          共 {{ queueData.total }} 筆申請
        </v-chip>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="filteredItems"
          :loading="loading"
          :items-per-page="perPage"
          hide-default-footer
          class="elevation-0"
        >
          <!-- Priority -->
          <template #item.priority="{ item }">
            <v-chip
              :color="getPriorityColor(item.priority)"
              size="small"
              variant="flat"
            >
              <v-icon start size="small">{{ getPriorityIcon(item.priority) }}</v-icon>
              {{ getPriorityText(item.priority) }}
            </v-chip>
          </template>

          <!-- Applicant -->
          <template #item.applicant_name="{ item }">
            <div>
              <div class="font-weight-bold">{{ item.applicant_name }}</div>
              <div class="text-caption text-grey">ID: {{ item.applicant_id }}</div>
            </div>
          </template>

          <!-- Pet -->
          <template #item.pet_name="{ item }">
            <div>
              <div class="font-weight-bold">{{ item.pet_name }}</div>
              <div class="text-caption text-grey">ID: {{ item.pet_id }}</div>
            </div>
          </template>

          <!-- Status -->
          <template #item.status="{ item }">
            <v-chip size="small" :color="getStatusColor(item.status)">
              {{ getStatusDisplayName(item.status) }}
            </v-chip>
          </template>

          <!-- Days Since Submitted -->
          <template #item.days_since_submitted="{ item }">
            <div class="text-center">
              <div class="font-weight-bold">{{ item.days_since_submitted }}</div>
              <div class="text-caption text-grey">天</div>
            </div>
          </template>

          <!-- Documents -->
          <template #item.documents_complete="{ item }">
            <v-chip
              :color="item.documents_complete ? 'success' : 'warning'"
              size="small"
              variant="tonal"
            >
              <v-icon start size="small">
                {{ item.documents_complete ? 'mdi-check-circle' : 'mdi-alert-circle' }}
              </v-icon>
              {{ item.total_documents }}/3
            </v-chip>
          </template>

          <!-- Latest Comment -->
          <template #item.latest_comment="{ item }">
            <div v-if="item.latest_comment" class="text-caption" style="max-width: 200px">
              {{ item.latest_comment }}
            </div>
            <span v-else class="text-grey">無</span>
          </template>

          <!-- Actions -->
          <template #item.actions="{ item }">
            <v-btn
              color="primary"
              size="small"
              variant="tonal"
              @click="openReviewModal(item)"
            >
              <v-icon start>mdi-pencil</v-icon>
              審核
            </v-btn>
          </template>

          <!-- Loading state -->
          <template #loading>
            <v-skeleton-loader type="table-row@5" />
          </template>

          <!-- No data -->
          <template #no-data>
            <v-alert type="info" variant="tonal">
              目前沒有待審核的申請
            </v-alert>
          </template>
        </v-data-table>

        <!-- Pagination -->
        <div v-if="queueData && queueData.total_pages > 1" class="mt-4">
          <v-pagination
            v-model="currentPage"
            :length="queueData.total_pages"
            :total-visible="7"
            @update:model-value="loadQueue"
          />
        </div>
      </v-card-text>
    </v-card>

    <!-- Review Modal -->
    <ReviewModal
      v-model="reviewModalOpen"
      :application="selectedApplication"
      @decision-submitted="handleDecisionSubmitted"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  getReviewDashboard, 
  getReviewQueue,
  getPriorityColor,
  getPriorityIcon,
  formatDuration,
  type ReviewDashboardResponse,
  type ReviewQueueResponse,
  type ApplicationQueueItem
} from '@/api/review'
import { getStatusDisplayName, getStatusColor } from '@/api/application-status'
import ReviewModal from '@/components/review/ReviewModal.vue'

// ==================== Data ====================

const dashboard = ref<ReviewDashboardResponse | null>(null)
const queueData = ref<ReviewQueueResponse | null>(null)
const loading = ref(true) // Start with loading true for initial skeleton
const error = ref<string | null>(null)

const statusFilter = ref('all')
const priorityFilter = ref('all')
const currentPage = ref(1)
const perPage = ref(20)

const reviewModalOpen = ref(false)
const selectedApplication = ref<ApplicationQueueItem | null>(null)

const statusFilterOptions = [
  { title: '全部', value: 'all' },
  { title: '已提交', value: 'submitted' },
  { title: '文件審核中', value: 'document_review' },
  { title: '審核中', value: 'under_review' },
]

const priorityFilterOptions = [
  { title: '全部優先級', value: 'all' },
  { title: '低', value: 'low' },
  { title: '中', value: 'medium' },
  { title: '高', value: 'high' },
  { title: '緊急', value: 'urgent' },
]

const headers = [
  { title: '優先級', key: 'priority', sortable: true },
  { title: '申請人', key: 'applicant_name', sortable: true },
  { title: '寵物', key: 'pet_name', sortable: true },
  { title: '狀態', key: 'status', sortable: true },
  { title: '提交天數', key: 'days_since_submitted', sortable: true, align: 'center' as const },
  { title: '文件狀態', key: 'documents_complete', sortable: false },
  { title: '最新評論', key: 'latest_comment', sortable: false },
  { title: '操作', key: 'actions', sortable: false, align: 'center' as const },
]

// ==================== Computed ====================

const filteredItems = computed(() => {
  if (!queueData.value) return []
  
  let items = queueData.value.items
  
  // Filter by priority
  if (priorityFilter.value !== 'all') {
    items = items.filter(item => item.priority === priorityFilter.value)
  }
  
  return items
})

// ==================== Methods ====================

const loadDashboard = async () => {
  try {
    dashboard.value = await getReviewDashboard()
  } catch (err: any) {
    console.error('Failed to load dashboard:', err)
    error.value = err.response?.data?.message || '加載儀表板失敗'
  }
}

const loadQueue = async () => {
  loading.value = true
  error.value = null
  
  try {
    queueData.value = await getReviewQueue(
      statusFilter.value,
      currentPage.value,
      perPage.value
    )
  } catch (err: any) {
    console.error('Failed to load queue:', err)
    error.value = err.response?.data?.message || '加載審核佇列失敗'
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Parallel loading for faster performance
    await Promise.all([loadDashboard(), loadQueue()])
  } catch (err: any) {
    console.error('Failed to refresh data:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  // Filters are applied via computed property
  // No need to reload from server
}

const openReviewModal = (application: ApplicationQueueItem) => {
  selectedApplication.value = application
  reviewModalOpen.value = true
}

const handleDecisionSubmitted = () => {
  reviewModalOpen.value = false
  selectedApplication.value = null
  refreshData()
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

// ==================== Lifecycle ====================

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.v-data-table {
  font-size: 0.875rem;
}
</style>
