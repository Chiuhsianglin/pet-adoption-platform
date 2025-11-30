<template>
  <v-card class="application-timeline">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>申請進度時間軸</span>
      <v-btn icon size="small" @click="refreshTimeline">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <!-- Progress Bar -->
      <div class="mb-6">
        <div class="d-flex justify-space-between mb-2">
          <span class="text-subtitle-2">整體進度</span>
          <span class="text-subtitle-2 font-weight-bold">{{ timelineData?.progress_percentage || 0 }}%</span>
        </div>
        <v-progress-linear
          :model-value="timelineData?.progress_percentage || 0"
          :color="getProgressColor(timelineData?.progress_percentage || 0)"
          height="12"
          rounded
        />
        <div class="d-flex justify-space-between mt-1 text-caption text-grey">
          <span>已完成里程碑: {{ timelineData?.milestones_completed || 0 }}/{{ timelineData?.milestones_total || 7 }}</span>
          <span v-if="timelineData?.total_duration_days">總時長: {{ timelineData.total_duration_days }} 天</span>
        </div>
      </div>

      <!-- Current Status Card -->
      <v-alert
        v-if="timelineData?.current_status"
        :color="getStatusColor(timelineData.current_status)"
        variant="tonal"
        density="compact"
        class="mb-4"
      >
        <div class="d-flex align-center">
          <v-icon :icon="getStatusIcon(timelineData.current_status)" class="mr-2" />
          <span class="font-weight-bold">當前狀態: {{ getStatusDisplayName(timelineData.current_status) }}</span>
        </div>
      </v-alert>

      <!-- Timeline Events -->
      <v-timeline side="end" align="start" density="compact">
        <v-timeline-item
          v-for="event in timelineData?.events"
          :key="event.id"
          :dot-color="event.is_milestone ? 'primary' : 'grey-lighten-1'"
          :size="event.is_milestone ? 'default' : 'small'"
        >
          <template #icon v-if="event.is_milestone">
            <v-icon color="white">mdi-flag-checkered</v-icon>
          </template>

          <v-card>
            <v-card-title class="text-subtitle-1 py-2">
              <div class="d-flex justify-space-between align-center">
                <span>{{ getStatusDisplayName(event.status) }}</span>
                <v-chip
                  v-if="event.is_milestone"
                  size="x-small"
                  color="primary"
                  variant="flat"
                >
                  里程碑
                </v-chip>
              </div>
            </v-card-title>
            <v-card-text class="pb-2">
              <div class="text-caption text-grey mb-2">
                {{ formatDateTime(event.created_at) }}
                <span v-if="event.changed_by"> · 由 {{ event.changed_by }}</span>
              </div>
              
              <div v-if="event.previous_status" class="mb-2">
                <v-icon size="small" class="mr-1">mdi-arrow-right</v-icon>
                <span class="text-caption">
                  從 <strong>{{ getStatusDisplayName(event.previous_status) }}</strong>
                  變更為 <strong>{{ getStatusDisplayName(event.status) }}</strong>
                </span>
              </div>

              <div v-if="event.change_reason" class="text-body-2 mb-2">
                <v-icon size="small" class="mr-1">mdi-text</v-icon>
                {{ event.change_reason }}
              </div>

              <div v-if="event.estimated_completion" class="text-caption text-grey">
                <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                預計完成: {{ formatDateTime(event.estimated_completion) }}
              </div>

              <div v-if="event.notes" class="text-caption mt-2 pa-2 bg-grey-lighten-4 rounded">
                {{ event.notes }}
              </div>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>

      <!-- Next Steps Card -->
      <v-card v-if="nextSteps.length > 0" variant="outlined" color="info" class="mt-4">
        <v-card-title class="text-subtitle-1 py-2">
          <v-icon class="mr-2">mdi-lightbulb-on</v-icon>
          下一步行動
        </v-card-title>
        <v-card-text>
          <v-list density="compact" class="py-0">
            <v-list-item v-for="(step, index) in nextSteps" :key="index">
              <template #prepend>
                <v-icon size="small" color="info">mdi-chevron-right</v-icon>
              </template>
              <v-list-item-title class="text-body-2">{{ step }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>

      <!-- Required Actions Card -->
      <v-card v-if="requiredActions.length > 0" variant="outlined" color="warning" class="mt-4">
        <v-card-title class="text-subtitle-1 py-2">
          <v-icon class="mr-2">mdi-alert</v-icon>
          需要處理的事項
        </v-card-title>
        <v-card-text>
          <v-list density="compact" class="py-0">
            <v-list-item v-for="(action, index) in requiredActions" :key="index">
              <template #prepend>
                <v-icon size="small" color="warning">mdi-checkbox-marked-circle-outline</v-icon>
              </template>
              <v-list-item-title class="text-body-2">{{ action }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>

      <!-- Loading State -->
      <v-skeleton-loader v-if="loading" type="article, list-item@3" />

      <!-- Error State -->
      <v-alert v-if="error" type="error" class="mt-4">
        {{ error }}
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getApplicationTimeline, getStatusDisplayName, getStatusColor, getStatusIcon, type TimelineResponse } from '@/api/application-status'

const props = defineProps<{
  applicationId: number
  autoRefresh?: boolean
  refreshInterval?: number
}>()

const timelineData = ref<TimelineResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
let refreshTimer: number | null = null

const nextSteps = computed(() => {
  // Extract next steps from the timeline data or latest event
  // This would be populated by the backend TimelineService.get_next_steps()
  // For now, return empty array - will be populated when backend returns this data
  return []
})

const requiredActions = computed(() => {
  // Extract required actions from the timeline data
  // This would be populated by the backend TimelineService.get_required_actions()
  return []
})

const fetchTimeline = async () => {
  loading.value = true
  error.value = null
  
  try {
    timelineData.value = await getApplicationTimeline(props.applicationId)
  } catch (err: any) {
    error.value = err.response?.data?.message || '加載時間軸失敗'
    console.error('Failed to fetch timeline:', err)
  } finally {
    loading.value = false
  }
}

const refreshTimeline = () => {
  fetchTimeline()
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

const getProgressColor = (progress: number) => {
  if (progress >= 80) return 'success'
  if (progress >= 50) return 'info'
  if (progress >= 20) return 'warning'
  return 'grey'
}

onMounted(() => {
  fetchTimeline()
  
  if (props.autoRefresh && props.refreshInterval) {
    refreshTimer = window.setInterval(() => {
      fetchTimeline()
    }, props.refreshInterval)
  }
})

// Cleanup
const cleanup = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
}

// Note: In Vue 3 Composition API, onBeforeUnmount should be used
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(cleanup)
</script>

<style scoped>
.application-timeline {
  max-height: 80vh;
  overflow-y: auto;
}
</style>
