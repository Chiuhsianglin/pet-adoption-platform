<template>
  <AppHeader />
  <v-container fluid style="padding-top: 70px;">
    <v-row>
      <v-col cols="12">
        <!-- Page Header -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-btn icon @click="goBack" class="mr-2">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div class="flex-grow-1">
              <h2 class="text-h5">申請狀態追蹤</h2>
              <div class="text-caption text-grey">申請編號: #{{ applicationId }}</div>
            </div>
            <v-chip
              color="success"
              size="large"
            >
              <v-icon start>mdi-check-circle</v-icon>
              已提交
            </v-chip>
          </v-card-title>
        </v-card>

        <!-- Current Status Summary -->
        <v-card class="mb-4">
          <v-card-title>申請摘要</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <div class="text-caption text-grey mb-1">當前狀態</div>
                <div class="text-h6">{{ getStatusText(application?.status) }}</div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="text-caption text-grey mb-1">提交時間</div>
                <div class="text-h6">{{ application?.submitted_at ? formatDateTime(application.submitted_at) : '-' }}</div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="text-caption text-grey mb-1">預計完成</div>
                <div class="text-h6">7-14 工作天</div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="text-caption text-grey mb-1">聯繫方式</div>
                <div class="text-h6">電子郵件</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Main Content: Tabs for Timeline, Comments, and Chat -->
        <v-card>
          <v-card-title>申請詳情</v-card-title>
          <v-card-text>
            <v-alert type="info" variant="tonal" :icon="false" color="success">
              <div class="text-subtitle-2 mb-2">
                <v-icon class="mr-1">mdi-check-circle</v-icon>
                申請已成功提交
              </div>
              <p class="text-body-2 mb-2">
                感謝您的申請！我們已收到您的領養申請及相關文件。
              </p>
              <p class="text-body-2 mb-0">
                我們的團隊將盡快審核您的申請，並透過電子郵件或電話與您聯繫。
              </p>
            </v-alert>

            <!-- Document Status -->
            <v-card variant="outlined" class="mt-4">
              <v-card-title class="text-subtitle-1">
                <v-icon class="mr-2" color="success">mdi-file-check</v-icon>
                已提交文件
              </v-card-title>
              <v-card-text>
                <p class="text-body-2 text-grey">
                  您的申請文件已成功上傳。如需查看或修改文件，請返回文件上傳頁面。
                </p>
                <v-btn
                  color="primary"
                  variant="outlined"
                  class="mt-2"
                  :to="`/applications/${applicationId}/documents`"
                  prepend-icon="mdi-file-document-multiple"
                >
                  查看已上傳文件
                </v-btn>
              </v-card-text>
            </v-card>

            <!-- Next Steps -->
            <v-card variant="outlined" class="mt-4" v-if="application">
              <v-card-title class="text-subtitle-1">
                <v-icon class="mr-2" color="info">mdi-lightbulb-on</v-icon>
                接下來的步驟
              </v-card-title>
              <v-card-text>
                <v-timeline side="end" density="compact">
                  <v-timeline-item :dot-color="getStepColor(application.status, 1)" size="small">
                    <div class="text-body-2">
                      <strong>1. 文件審核</strong>
                      <div class="text-caption text-grey">{{ getStepDescription(1) }}</div>
                    </div>
                  </v-timeline-item>
                  <v-timeline-item :dot-color="getStepColor(application.status, 2)" size="small">
                    <div class="text-body-2">
                      <strong>2. 家訪安排</strong>
                      <div class="text-caption text-grey">{{ getStepDescription(2) }}</div>
                    </div>
                  </v-timeline-item>
                  <v-timeline-item :dot-color="getStepColor(application.status, 3)" size="small">
                    <div class="text-body-2">
                      <strong>3. 家訪完成</strong>
                      <div class="text-caption text-grey">{{ getStepDescription(3) }}</div>
                    </div>
                  </v-timeline-item>
                  <v-timeline-item :dot-color="getStepColor(application.status, 4)" size="small">
                    <div class="text-body-2">
                      <strong>4. 最終決定</strong>
                      <div class="text-caption text-grey">{{ getStepDescription(4) }}</div>
                    </div>
                  </v-timeline-item>
                </v-timeline>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const applicationId = computed(() => Number(route.params.applicationId))
const application = ref<any>(null)
const loading = ref(false)

onMounted(async () => {
  await loadApplicationStatus()
})

async function loadApplicationStatus() {
  loading.value = true
  try {
    const response = await api.get(`/adoptions/applications/${applicationId.value}`)
    application.value = response.data
  } catch (error) {
    console.error('Failed to load application status:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/applications')
}

function getStepColor(status: string, step: number): string {
  const statusStepMap: Record<string, number> = {
    draft: 0,
    pending: 0,
    submitted: 1,
    document_review: 1,
    home_visit_scheduled: 2,
    home_visit_completed: 3,
    under_evaluation: 3,
    approved: 4,
    rejected: 4,
    completed: 4,
    withdrawn: 0
  }

  const currentStep = statusStepMap[status] || 0

  if (step < currentStep) {
    return 'success'
  } else if (step === currentStep) {
    if (step === 4 && (status === 'approved' || status === 'rejected')) {
      return 'success'
    }
    return 'primary'
  } else {
    return 'grey'
  }
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    pending: '待提交',
    submitted: '已提交',
    document_review: '文件審核中',
    home_visit_scheduled: '已安排家訪',
    home_visit_completed: '家訪已完成',
    under_evaluation: '評估中',
    approved: '已通過',
    rejected: '未通過',
    completed: '已完成',
    withdrawn: '已撤回'
  }
  return statusMap[status] || '審核中'
}

function getStepDescription(step: number): string {
  if (!application.value) return ''
  
  const status = application.value.status
  const currentStep = getStepColor(status, step)
  
  if (currentStep === 'success') {
    if (step === 4) {
      if (status === 'approved') return '✓ 申請通過'
      if (status === 'rejected') return '✗ 申請拒絕'
    }
    return '✓ 已完成'
  } else if (currentStep === 'primary') {
    const descriptions: Record<number, string> = {
      1: '正在審核您提交的文件',
      2: application.value.home_visit_date 
        ? `家訪日期：${formatDateTime(application.value.home_visit_date)}`
        : '等待安排家訪日期',
      3: '家訪已完成，評估中',
      4: '即將通知您最終決定'
    }
    return descriptions[step] || '進行中'
  } else {
    const descriptions: Record<number, string> = {
      1: '我們將審核您提交的文件',
      2: '安排工作人員進行家訪',
      3: '完成家訪後進行評估',
      4: '通知您最終的領養決定'
    }
    return descriptions[step] || '等待中'
  }
}

const formatDateTime = (dateString: string) => {
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
</script>

<style scoped>
/* Add any custom styles here */
</style>
