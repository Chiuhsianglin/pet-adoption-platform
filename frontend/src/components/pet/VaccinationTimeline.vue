<template>
  <v-card flat>
    <v-card-text>
      <!-- Timeline Header -->
      <div class="d-flex align-center mb-4">
        <v-icon color="primary" size="large" class="mr-2">mdi-needle</v-icon>
        <h3 class="text-h6">疫苗接種時間軸</h3>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <p class="text-body-2 text-grey mt-2">載入疫苗記錄中...</p>
      </div>

      <!-- Empty State -->
      <v-alert
        v-else-if="!loading && vaccinations.length === 0"
        type="info"
        variant="tonal"
        class="mb-0"
      >
        <template v-slot:prepend>
          <v-icon>mdi-information</v-icon>
        </template>
        <div>
          <div class="text-subtitle-1 mb-1">尚無疫苗接種記錄</div>
          <div class="text-body-2">目前沒有此寵物的疫苗接種記錄。請稍後再查看。</div>
        </div>
      </v-alert>

      <!-- Timeline Content -->
      <v-timeline
        v-else
        align="start"
        side="end"
        density="comfortable"
        truncate-line="both"
      >
        <v-timeline-item
          v-for="(vaccination, index) in sortedVaccinations"
          :key="index"
          :dot-color="getStatusColor(vaccination.status)"
          size="small"
        >
          <!-- Timeline Icon -->
          <template v-slot:icon>
            <v-icon :color="getStatusIconColor(vaccination.status)" size="small">
              {{ getStatusIcon(vaccination.status) }}
            </v-icon>
          </template>

          <!-- Timeline Content Card -->
          <v-card :color="getCardColor(vaccination.status)" variant="tonal">
            <v-card-text>
              <div class="d-flex justify-space-between align-start mb-2">
                <div>
                  <h4 class="text-subtitle-1 font-weight-bold">
                    {{ vaccination.vaccineName }}
                  </h4>
                  <p class="text-body-2 text-grey">
                    {{ vaccination.vaccineType }}
                  </p>
                </div>
                <v-chip
                  :color="getStatusColor(vaccination.status)"
                  size="small"
                  variant="flat"
                >
                  {{ getStatusText(vaccination.status) }}
                </v-chip>
              </div>

              <!-- Vaccination Date -->
              <div class="d-flex align-center mb-1">
                <v-icon size="small" class="mr-2">mdi-calendar</v-icon>
                <span class="text-body-2">
                  {{ formatDate(vaccination.date) }}
                  <span v-if="vaccination.status === 'scheduled'" class="text-grey">
                    (預定)
                  </span>
                </span>
              </div>

              <!-- Veterinarian -->
              <div v-if="vaccination.veterinarian" class="d-flex align-center mb-1">
                <v-icon size="small" class="mr-2">mdi-doctor</v-icon>
                <span class="text-body-2">{{ vaccination.veterinarian }}</span>
              </div>

              <!-- Clinic/Location -->
              <div v-if="vaccination.clinic" class="d-flex align-center mb-1">
                <v-icon size="small" class="mr-2">mdi-hospital-building</v-icon>
                <span class="text-body-2">{{ vaccination.clinic }}</span>
              </div>

              <!-- Batch Number -->
              <div v-if="vaccination.batchNumber" class="d-flex align-center mb-1">
                <v-icon size="small" class="mr-2">mdi-barcode</v-icon>
                <span class="text-body-2 text-grey">批號: {{ vaccination.batchNumber }}</span>
              </div>

              <!-- Notes -->
              <div v-if="vaccination.notes" class="mt-2">
                <v-divider class="my-2"></v-divider>
                <p class="text-body-2">
                  <v-icon size="small" class="mr-1">mdi-note-text</v-icon>
                  {{ vaccination.notes }}
                </p>
              </div>

              <!-- Next Due Date (for completed vaccinations) -->
              <div v-if="vaccination.nextDueDate && vaccination.status === 'completed'" class="mt-2">
                <v-divider class="my-2"></v-divider>
                <div class="d-flex align-center">
                  <v-icon size="small" color="warning" class="mr-2">mdi-bell-alert</v-icon>
                  <span class="text-body-2">
                    下次接種: {{ formatDate(vaccination.nextDueDate) }}
                    <span v-if="isOverdue(vaccination.nextDueDate)" class="text-error">
                      (已逾期)
                    </span>
                    <span v-else-if="isDueSoon(vaccination.nextDueDate)" class="text-warning">
                      (即將到期)
                    </span>
                  </span>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>

      <!-- Summary Section -->
      <v-card v-if="!loading && vaccinations.length > 0" variant="outlined" class="mt-4">
        <v-card-text>
          <div class="text-subtitle-2 font-weight-bold mb-2">疫苗接種摘要</div>
          <v-row dense>
            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-success">{{ completedCount }}</div>
                <div class="text-caption text-grey">已完成</div>
              </div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-primary">{{ scheduledCount }}</div>
                <div class="text-caption text-grey">已預約</div>
              </div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-warning">{{ overdueCount }}</div>
                <div class="text-caption text-grey">已逾期</div>
              </div>
            </v-col>
            <v-col cols="6" sm="3">
              <div class="text-center">
                <div class="text-h6 text-info">{{ totalCount }}</div>
                <div class="text-caption text-grey">總計</div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getVaccinations, type VaccinationResponse } from '@/api/vaccinations'

// Props
interface Props {
  petId: number
}

const props = defineProps<Props>()

// Types
interface Vaccination {
  vaccineName: string        // 疫苗名稱 (e.g., "狂犬病疫苗", "八合一疫苗")
  vaccineType: string        // 疫苗類型 (e.g., "核心疫苗", "非核心疫苗")
  date: string              // 接種日期 (ISO format)
  status: 'completed' | 'scheduled' | 'overdue' | 'cancelled'  // 狀態
  veterinarian?: string     // 獸醫師姓名
  clinic?: string           // 診所/醫院名稱
  batchNumber?: string      // 疫苗批號
  notes?: string            // 備註
  nextDueDate?: string      // 下次接種日期 (ISO format)
}

// State
const loading = ref(false)
const vaccinations = ref<Vaccination[]>([])

// Computed
const sortedVaccinations = computed(() => {
  return [...vaccinations.value].sort((a, b) => {
    // Sort by date descending (newest first)
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
})

const completedCount = computed(() => {
  return vaccinations.value.filter(v => v.status === 'completed').length
})

const scheduledCount = computed(() => {
  return vaccinations.value.filter(v => v.status === 'scheduled').length
})

const overdueCount = computed(() => {
  return vaccinations.value.filter(v => v.status === 'overdue').length
})

const totalCount = computed(() => {
  return vaccinations.value.length
})

// Methods
const loadVaccinations = async () => {
  loading.value = true
  try {
    const response = await getVaccinations(props.petId, 1, 50) // Get up to 50 vaccinations
    
    // Transform API response to component format
    vaccinations.value = response.data.items.map((item: VaccinationResponse) => ({
      vaccineName: item.vaccine_name,
      vaccineType: formatVaccineType(item.vaccine_type),
      date: item.administration_date || item.scheduled_date || '',
      status: item.status.toLowerCase() as Vaccination['status'],
      veterinarian: item.veterinarian_name || undefined,
      clinic: item.clinic_name || undefined,
      batchNumber: item.batch_number || undefined,
      notes: item.notes || undefined,
      nextDueDate: item.next_due_date || undefined
    }))
  } catch (error) {
    console.error('載入疫苗記錄失敗:', error)
    // TODO: Show error notification
  } finally {
    loading.value = false
  }
}

const formatVaccineType = (type: string): string => {
  switch (type.toLowerCase()) {
    case 'core':
      return '核心疫苗'
    case 'non_core':
      return '非核心疫苗'
    case 'optional':
      return '選擇性疫苗'
    default:
      return type
  }
}

const getStatusColor = (status: Vaccination['status']): string => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'scheduled':
      return 'primary'
    case 'overdue':
      return 'error'
    default:
      return 'grey'
  }
}

const getStatusIconColor = (_status: Vaccination['status']): string => {
  return 'white'
}

const getStatusIcon = (status: Vaccination['status']): string => {
  switch (status) {
    case 'completed':
      return 'mdi-check'
    case 'scheduled':
      return 'mdi-clock-outline'
    case 'overdue':
      return 'mdi-alert'
    default:
      return 'mdi-help'
  }
}

const getStatusText = (status: Vaccination['status']): string => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'scheduled':
      return '已預約'
    case 'overdue':
      return '已逾期'
    default:
      return '未知'
  }
}

const getCardColor = (status: Vaccination['status']): string => {
  switch (status) {
    case 'completed':
      return 'success-lighten-5'
    case 'scheduled':
      return 'primary-lighten-5'
    case 'overdue':
      return 'error-lighten-5'
    default:
      return 'grey-lighten-5'
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const isOverdue = (dateString: string): boolean => {
  const dueDate = new Date(dateString)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return dueDate < today
}

const isDueSoon = (dateString: string): boolean => {
  const dueDate = new Date(dateString)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diffDays = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  return diffDays > 0 && diffDays <= 30
}

// Lifecycle
onMounted(() => {
  loadVaccinations()
})
</script>

<style scoped>
/* Custom timeline styling */
:deep(.v-timeline-item__body) {
  padding-inline-start: 16px;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  :deep(.v-timeline) {
    padding-inline-start: 8px;
  }
}
</style>
