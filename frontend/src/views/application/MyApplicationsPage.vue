<template>
  <AppHeader />
  <v-container style="padding-top: 80px;">
    <v-row>
      <v-col cols="12">
        <!-- Page Header -->
        <div class="mb-6">
            <h1 class="text-h4 mb-1 d-flex align-center" style="font-weight: 600">
                <v-icon class="mr-1" color="black">mdi-history</v-icon>
                我的領養申請
            </h1>
          <p class="text-body-2 text-grey">
            <span> &nbsp&nbsp&nbsp&nbsp  </span>  查看您提交的所有領養申請及其狀態
          </p>
        </div>

        <!-- Loading State -->
        <div v-if="loading">
          <v-card v-for="i in 3" :key="`skeleton-${i}`" class="mb-4">
            <v-card-title>
              <v-skeleton-loader type="heading" width="40%" />
              <v-skeleton-loader type="text" width="30%" class="mt-2" />
            </v-card-title>
            <v-divider />
            <v-card-text>
              <v-row>
                <v-col cols="12" md="7">
                  <v-skeleton-loader type="text" width="30%" class="mb-3" />
                  <v-row>
                    <v-col cols="12" sm="5">
                      <v-skeleton-loader type="image" aspect-ratio="1" />
                    </v-col>
                    <v-col cols="12" sm="7">
                      <v-skeleton-loader type="list-item-two-line" />
                      <v-skeleton-loader type="list-item-two-line" />
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="12" md="5">
                  <v-skeleton-loader type="text" width="30%" class="mb-3" />
                  <v-skeleton-loader type="list-item" />
                  <v-skeleton-loader type="list-item" />
                  <v-skeleton-loader type="list-item" />
                  <v-skeleton-loader type="list-item" />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </div>

        <!-- Error State -->
        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 mb-1">載入失敗</div>
              <div>{{ error }}</div>
            </div>
            <v-btn
              color="error"
              variant="elevated"
              @click="loadApplications"
            >
              重試
            </v-btn>
          </div>
        </v-alert>

        <!-- Empty State -->
        <v-card v-else-if="applications.length === 0">
          <v-card-text class="text-center py-12">
            <v-icon size="80" color="grey-lighten-1">mdi-clipboard-text-outline</v-icon>
            <h3 class="text-h6 mt-4 mb-2">尚無申請記錄</h3>
            <p class="text-body-2 text-grey mb-4">
              您還沒有提交任何領養申請
            </p>
            <v-btn
              color="primary"
              to="/pets"
              prepend-icon="mdi-paw"
            >
              瀏覽可領養寵物
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Applications List -->
        <div v-else>
          <v-card
            v-for="application in applications"
            :key="application.id"
            class="mb-4"
          >
            <v-card-title class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-h6">申請編號 #{{ application.id }}</div>
                <div class="text-caption text-grey">
                  提交時間：{{ formatDateTime(application.created_at) }}
                </div>
              </div>
            </v-card-title>

            <v-divider />

            <v-card-text class="pa-0">
              <v-row no-gutters>
                <!-- 左半邊：寵物資訊 -->
                <v-col cols="12" md="7" class="pa-4 border-e">
                  <div class="text-subtitle-2 mb-3 d-flex align-center">
                    <v-icon class="mr-2" color="primary">mdi-paw</v-icon>
                    寵物資訊
                  </div>
                  
                  <v-row align="center">
                    <v-col cols="12" sm="5">
                      <v-img
                        v-if="application.pet?.photos && application.pet.photos.length > 0"
                        :src="application.pet.photos[0].file_url"
                        :lazy-src="application.pet.photos[0].file_url"
                        :alt="application.pet.name"
                        aspect-ratio="1"
                        cover
                        class="rounded"
                      >
                        <template #placeholder>
                          <v-skeleton-loader type="image" />
                        </template>
                      </v-img>
                      <div v-else class="d-flex align-center justify-center bg-grey-lighten-3 rounded" style="aspect-ratio: 1">
                        <v-icon size="48" color="grey">mdi-image-off</v-icon>
                      </div>
                    </v-col>
                    
                    <v-col cols="12" sm="7">
                      <v-row dense>
                        <v-col cols="6">
                        <div class="text-caption text-grey">寵物名稱</div>
                        <div class="text-h6">{{ application.pet?.name || '載入中...' }}</div>
                        </v-col>
                        <v-col cols="6">
                        <div class="text-caption text-grey">品種</div>
                        <div class="text-body-2">{{ application.pet?.breed || '-' }}</div>
                        </v-col>
                      </v-row>                      
                      <v-row dense>
                        <v-col cols="6">
                          <div class="text-caption text-grey">年齡</div>
                          <div class="text-body-2">{{ getPetAge(application.pet) }}</div>
                        </v-col>
                        <v-col cols="6">
                          <div class="text-caption text-grey">性別</div>
                          <div class="text-body-2">{{ getPetGender(application.pet?.gender) }}</div>
                        </v-col>
                      </v-row>
                    </v-col>
                  </v-row>
                </v-col>

                <!-- 右半邊：接下來的步驟 或 上傳文件提示 -->
                <v-col cols="12" md="5" class="pa-4">
                  <!-- 如果還沒有上傳文件，顯示上傳提示 -->
                  <div v-if="!application.documents || application.documents.length === 0">
                    <v-alert
                      type="warning"
                      variant="tonal"
                      class="mb-4"
                    >
                      <div class="text-body-2 mb-2">
                        您尚未上傳所需的申請文件
                      </div>
                      <div class="text-caption">
                        請上傳身分證明、收入證明等必要文件以完成申請流程
                      </div>
                    </v-alert>
                    
                    <v-btn
                      color="primary"
                      size="large"
                      block
                      prepend-icon="mdi-file-upload"
                      :to="`/applications/${application.id}/documents`"
                    >
                      上傳文件
                    </v-btn>
                  </div>
                  
                  <!-- 如果已上傳文件，顯示接下來的步驟 -->
                  <div v-else>
                    <div class="text-subtitle-2 mb-3 d-flex align-center">
                      <v-icon class="mr-2" color="black">mdi-timeline-check</v-icon>
                      審核進度
                    </div>
                    
                    <!-- 家訪日期提示 
                    <v-alert
                      v-if="application.home_visit_date && application.status === 'home_visit_scheduled'"
                      type="info"
                      variant="tonal"
                      class="mb-3"
                      density="compact"
                    >
                      <div class="text-caption">
                        <strong>家訪已安排</strong><br>
                        日期：{{ formatDateTime(application.home_visit_date) }}
                      </div>
                    </v-alert>-->

                    <!-- 最終決定備註 -->
                    <v-alert
                      v-if="application.final_decision_notes"
                      :type="application.status === 'approved' ? 'success' : 'error'"
                      variant="tonal"
                      class="mb-3"
                      density="compact"
                    >
                      <div class="text-caption">
                        <strong>{{ application.status === 'approved' ? '通過備註' : '拒絕原因' }}</strong><br>
                        {{ application.final_decision_notes }}
                      </div>
                    </v-alert>
                    
                    <v-timeline side="end" density="compact" align="start">
                      <v-timeline-item 
                        :dot-color="getStepColor(application.status, 1)" 
                        size="small"
                      >
                        <div class="text-body-2">
                          <strong>1. 文件審核</strong>
                          <div class="text-caption text-grey">
                            {{ getStepDescription(application, 1) }}
                          </div>
                        </div>
                      </v-timeline-item>
                      <v-timeline-item 
                        :dot-color="getStepColor(application.status, 2)" 
                        size="small"
                      >
                        <div class="text-body-2">
                          <strong>2. 家訪安排</strong>
                          <div class="text-caption text-grey">
                            {{ getStepDescription(application, 2) }}
                          </div>
                        </div>
                      </v-timeline-item>
                      <v-timeline-item 
                        :dot-color="getStepColor(application.status, 3)" 
                        size="small"
                      >
                        <div class="text-body-2">
                          <strong>3. 家訪完成</strong>
                          <div class="text-caption text-grey">
                            {{ getStepDescription(application, 3) }}
                          </div>
                        </div>
                      </v-timeline-item>
                      <v-timeline-item 
                        :dot-color="getStepColor(application.status, 4)" 
                        size="small"
                      >
                        <div class="text-body-2">
                          <strong>4. 最終決定</strong>
                          <div class="text-caption text-grey">
                            {{ getStepDescription(application, 4) }}
                          </div>
                        </div>
                      </v-timeline-item>
                    </v-timeline>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>

            <v-divider />

            <v-card-actions v-if="application.documents && application.documents.length > 0">
              <v-spacer />
              <v-btn
                variant="text"
                :to="`/applications/${application.id}/documents`"
                prepend-icon="mdi-file-document"
              >
                編輯文件
              </v-btn>
              <v-btn
                color="primary"
                variant="text"
                :to="`/applications/${application.id}/status`"
                prepend-icon="mdi-information"
              >
                查看詳情
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>

        <!-- Error State -->
        <v-alert
          v-if="error"
          type="error"
          class="mt-4"
          closable
          @click:close="error = null"
        >
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import AppHeader from '@/components/layout/AppHeader.vue'

interface PetPhoto {
  id: number
  file_url: string
  is_primary: boolean
}

interface Pet {
  id: number
  name: string
  breed: string
  species: string
  age_years: number
  age_months: number
  gender: string
  photos?: PetPhoto[]
}

interface Document {
  id: number
  document_type: string
  file_url: string
  uploaded_at: string
}

interface Application {
  id: number
  application_id: string
  pet_id: number
  applicant_id: number
  status: string
  personal_info: {
    name: string
    phone: string
    email: string
    address: string
  }
  pet?: Pet
  documents?: Document[]
  review_notes?: string
  home_visit_date?: string
  home_visit_notes?: string
  home_visit_document?: string
  final_decision_notes?: string
  created_at: string
  updated_at: string
}

const applications = ref<Application[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(() => {
  loadApplications()
})

async function loadApplications() {
  loading.value = true
  error.value = null

  try {
    const response = await api.get('/adoptions/applications', {
      timeout: 30000 // 30 seconds timeout
    })
    const apps = response.data.applications || []
    
    console.log('📋 Applications loaded with pets and documents:', apps)
    
    // Backend now returns all data (pet + documents) in one request
    applications.value = apps
    
  } catch (err: any) {
    console.error('Failed to load applications:', err)
    console.error('Error response:', err.response)
    console.error('Error message:', err.message)
    console.error('Error config:', err.config)
    
    // 提供更友善的錯誤訊息
    if (err.message === 'Network Error') {
      error.value = '無法連接到後端服務，請確認後端服務是否正在運行'
    } else {
      error.value = err.response?.data?.detail || err.message || '載入申請列表失敗'
    }
  } finally {
    loading.value = false
  }
}

function getPetAge(pet?: Pet): string {
  if (!pet || !pet.age_years || !pet.age_months) return '未知'
  
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1
  
  let ageYears = currentYear - pet.age_years
  let ageMonths = currentMonth - pet.age_months
  
  if (ageMonths < 0) {
    ageYears -= 1
    ageMonths += 12
  }
  
  if (ageYears === 0) return `${ageMonths} 個月`
  if (ageMonths === 0) return `${ageYears} 歲`
  return `${ageYears} 歲 ${ageMonths} 個月`
}

function getPetGender(gender?: string): string {
  const genderMap: Record<string, string> = {
    male: '男生',
    female: '女生',
    unknown: '未知'
  }
  return gender ? (genderMap[gender] || gender) : '-'
}

function getStepColor(status: string, step: number): string {
  // 定義狀態對應的步驟進度
  const statusStepMap: Record<string, number> = {
    draft: 0,                      // 草稿：未開始
    pending: 0,                    // 待處理：未開始
    submitted: 1,                  // 已提交：文件審核中
    document_review: 1,            // 文件審核中
    home_visit_scheduled: 2,       // 家訪已安排
    home_visit_completed: 3,       // 家訪已完成
    under_evaluation: 3,           // 評估中
    approved: 4,                   // 已通過：所有步驟完成
    rejected: 4,                   // 已拒絕：步驟 4 完成但顯示拒絕
    completed: 4,                  // 已完成：所有步驟完成
    withdrawn: 0                   // 已撤回：顯示為未完成
  }

  const currentStep = statusStepMap[status] || 0

  if (step < currentStep) {
    return 'success'  // 已完成的步驟
  } else if (step === currentStep) {
    // 步驟 4 且狀態是 approved 或 rejected 時，顯示為已完成
    if (step === 4 && (status === 'approved' || status === 'rejected')) {
      return 'success'
    }
    return 'primary'     // 進行中的步驟
  } else {
    return 'grey'     // 未開始的步驟
  }
}

function getStepDescription(application: Application, step: number): string {
  const status = application.status
  const currentStep = getStepColor(status, step)
  
  // Debug log for step 2
  if (step === 2) {
    console.log('🔍 Step 2 Debug:', {
      applicationId: application.id,
      status: application.status,
      home_visit_date: application.home_visit_date,
      currentStep: currentStep
    })
  }
  
  if (currentStep === 'success') {
    // 步驟 4 特殊處理：顯示通過或拒絕
    if (step === 4) {
      if (status === 'approved') {
        return '✓ 申請通過'
      } else if (status === 'rejected') {
        return '✗ 申請拒絕'
      }
    }
    return '✓ 已完成'
  } else if (currentStep === 'primary') {
    const descriptions: Record<number, string> = {
      1: '正在審核您提交的文件',
      2: application.home_visit_date 
        ? `家訪日期：${formatDateTime(application.home_visit_date)}`
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

function formatDateTime(dateString: string): string {
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
/* Add any component-specific styles here */
</style>
