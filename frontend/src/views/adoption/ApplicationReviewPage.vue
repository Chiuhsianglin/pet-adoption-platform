<template>
  <v-app>
    <AppHeader />
    <v-main>
      <v-container class="py-8">
        <h1 class="text-h4 mb-6">領養申請審核</h1>

        <!-- Filters -->
        <v-card class="mb-6">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-select
                  v-model="statusFilter"
                  label="申請狀態"
                  :items="statusOptions"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="loadApplications"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchQuery"
                  label="搜尋申請人或寵物名稱"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="debouncedSearch"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Applications List -->
        <v-row>
          <v-col
            v-for="application in applications"
            :key="application.id"
            cols="12"
          >
            <v-card>
              <v-card-text>
                <v-row>
                  <!-- Pet Info (30%) -->
                  <v-col cols="12" md="4">
                    <div class="d-flex align-center">
                      <v-avatar size="80" rounded class="mr-4">
                        <v-img
                          v-if="application.pet?.photos?.[0]"
                          :src="application.pet.photos[0].file_url || application.pet.photos[0].url"
                          cover
                        />
                        <v-icon v-else size="40">mdi-paw</v-icon>
                      </v-avatar>
                      <div>
                        <h3 class="text-h6">{{ application.pet?.name || '未知寵物' }}</h3>
                        <p class="text-body-2 text-grey">
                          {{ getSpeciesText(application.pet?.species) }} · {{ application.pet?.breed }}
                        </p>
                        <v-chip size="small" :color="getStatusColor(application.status)" class="mt-1">
                          {{ getStatusText(application.status) }}
                        </v-chip>
                      </div>
                    </div>
                  </v-col>

                  <!-- Applicant Info (30%) -->
                  <v-col cols="12" md="4">
                    <div>
                      <div class="text-subtitle-2 text-grey mb-1">
                        申請編號：#{{ application.id }}
                      </div>
                      <div class="mb-1">
                        <v-icon size="small" class="mr-1">mdi-account</v-icon>
                        {{ application.user?.name || '未知用戶' }}
                      </div>
                      <div class="mb-1">
                        <v-icon size="small" class="mr-1">mdi-email</v-icon>
                        {{ application.user?.email }}
                      </div>
                      <div v-if="application.user?.phone" class="mb-1">
                        <v-icon size="small" class="mr-1">mdi-phone</v-icon>
                        {{ application.user.phone }}
                      </div>
                      <div class="text-caption text-grey mt-2">
                        申請日期：{{ formatDate(application.created_at) }}
                      </div>
                    </div>
                  </v-col>

                  <!-- Actions (40%) -->
                  <v-col cols="12" md="4" class="d-flex align-center justify-end">
                    <div class="d-flex flex-column ga-2" style="width: 100%;">
                      <v-btn
                        color="primary"
                        variant="outlined"
                        block
                        :to="`/adoptions/applications/${application.id}`"
                      >
                        <v-icon start>mdi-eye</v-icon>
                        查看詳情與審核
                      </v-btn>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Empty State -->
        <v-card v-if="!loading && applications.length === 0" class="text-center py-12">
          <v-icon icon="mdi-inbox" size="64" color="grey" />
          <div class="text-h6 mt-4 text-grey">目前沒有申請</div>
        </v-card>

        <!-- Loading -->
        <v-progress-linear v-if="loading" indeterminate color="primary" class="mt-4" />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()

interface Application {
  id: number
  pet_id: number
  user_id: number
  status: string
  reason?: string
  living_situation?: string
  pet_experience?: string
  created_at: string
  home_visit_date?: string
  home_visit_notes?: string
  home_visit_document?: string
  final_decision_notes?: string
  pet?: any
  user?: any
  documents?: any[]
}

const applications = ref<Application[]>([])
const loading = ref(false)
const statusFilter = ref<string | null>(null)
const searchQuery = ref('')

const statusOptions = [
  { title: '全部', value: null },
  { title: '已提交', value: 'submitted' },
  { title: '文件審核中', value: 'document_review' },
  { title: '家訪已安排', value: 'home_visit_scheduled' },
  { title: '家訪已完成', value: 'home_visit_completed' },
  { title: '評估中', value: 'under_evaluation' },
  { title: '已通過', value: 'approved' },
  { title: '已拒絕', value: 'rejected' },
]

const loadApplications = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const response = await api.get('/adoptions/shelter/applications', { params })
    applications.value = response.data
  } catch (error: any) {
    console.error('Failed to load applications:', error)
    notificationStore.error('載入申請失敗')
  } finally {
    loading.value = false
  }
}

let searchTimeout: NodeJS.Timeout | null = null
const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadApplications()
  }, 500)
}

const getSpeciesText = (species: string) => {
  const speciesMap: Record<string, string> = {
    'dog': '狗',
    'cat': '貓',
    'bird': '鳥',
    'rabbit': '兔子',
    'hamster': '倉鼠',
    'other': '其他'
  }
  return speciesMap[species] || species
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'submitted':
    case 'document_review':
      return 'orange'
    case 'home_visit_scheduled':
      return 'blue'
    case 'home_visit_completed':
    case 'under_evaluation':
      return 'purple'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'error'
    default:
      return 'grey'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'submitted':
      return '已提交'
    case 'document_review':
      return '文件審核中'
    case 'home_visit_scheduled':
      return '家訪已安排'
    case 'home_visit_completed':
      return '家訪已完成'
    case 'under_evaluation':
      return '評估中'
    case 'approved':
      return '已通過'
    case 'rejected':
      return '已拒絕'
    default:
      return status
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

onMounted(() => {
  loadApplications()
})
</script>
