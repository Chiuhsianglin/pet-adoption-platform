<template>
  <v-container fluid class="batch-edit-page">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">
          <v-icon class="mr-2">mdi-pencil-box-multiple</v-icon>
          批次編輯寵物資訊
        </h1>
      </v-col>
    </v-row>

    <!-- Step 1: Select Pets -->
    <v-row v-if="step === 1">
      <v-col cols="12">
        <v-card>
          <v-card-title>步驟 1: 選擇要編輯的寵物</v-card-title>
          
          <v-card-text>
            <!-- Filters -->
            <v-row class="mb-4">
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.status"
                  :items="statusOptions"
                  label="狀態"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.species"
                  :items="speciesOptions"
                  label="物種"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.search"
                  label="搜尋"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-btn
                  color="primary"
                  block
                  @click="loadPets"
                  :loading="loading"
                >
                  搜尋
                </v-btn>
              </v-col>
            </v-row>

            <!-- Pet Selection Table -->
            <v-data-table
              v-model="selectedPets"
              :headers="petHeaders"
              :items="pets"
              :loading="loading"
              item-value="id"
              show-select
              class="elevation-1"
            >
              <template #item.name="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="40" class="mr-2">
                    <v-img
                      v-if="item.primary_photo_url"
                      :src="item.primary_photo_url"
                    />
                    <v-icon v-else>mdi-paw</v-icon>
                  </v-avatar>
                  {{ item.name }}
                </div>
              </template>

              <template #item.species="{ item }">
                {{ getSpeciesLabel(item.species) }}
              </template>

              <template #item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small">
                  {{ getStatusLabel(item.status) }}
                </v-chip>
              </template>

              <template #item.age_months="{ item }">
                {{ item.age_months ? `${item.age_months} 個月` : '-' }}
              </template>
            </v-data-table>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :disabled="selectedPets.length === 0"
              @click="step = 2"
            >
              下一步 (已選擇 {{ selectedPets.length }} 隻)
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Step 2: Edit Fields -->
    <v-row v-if="step === 2">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            步驟 2: 選擇要編輯的欄位
            <v-chip class="ml-2" color="primary">
              已選擇 {{ selectedPets.length }} 隻寵物
            </v-chip>
          </v-card-title>

          <v-card-text>
            <v-alert type="info" variant="tonal" class="mb-4">
              只有勾選的欄位會被更新，未勾選的欄位保持原值
            </v-alert>

            <!-- Editable Fields -->
            <v-row>
              <!-- Status -->
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editFields.status.enabled"
                  label="狀態"
                  hide-details
                />
                <v-select
                  v-if="editFields.status.enabled"
                  v-model="editFields.status.value"
                  :items="statusOptions"
                  label="新狀態"
                  class="mt-2"
                />
              </v-col>

              <!-- Location -->
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editFields.location.enabled"
                  label="所在地點"
                  hide-details
                />
                <v-text-field
                  v-if="editFields.location.enabled"
                  v-model="editFields.location.value"
                  label="新地點"
                  class="mt-2"
                />
              </v-col>

              <!-- Vaccination Status -->
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editFields.vaccination_status.enabled"
                  label="疫苗接種狀態"
                  hide-details
                />
                <v-switch
                  v-if="editFields.vaccination_status.enabled"
                  v-model="editFields.vaccination_status.value"
                  label="已接種疫苗"
                  color="primary"
                  class="mt-2"
                />
              </v-col>

              <!-- Sterilized -->
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editFields.sterilized.enabled"
                  label="結紮狀態"
                  hide-details
                />
                <v-switch
                  v-if="editFields.sterilized.enabled"
                  v-model="editFields.sterilized.value"
                  label="已結紮"
                  color="primary"
                  class="mt-2"
                />
              </v-col>

              <!-- Health Status -->
              <v-col cols="12">
                <v-checkbox
                  v-model="editFields.health_status.enabled"
                  label="健康狀況"
                  hide-details
                />
                <v-textarea
                  v-if="editFields.health_status.enabled"
                  v-model="editFields.health_status.value"
                  label="健康狀況描述"
                  rows="3"
                  class="mt-2"
                />
              </v-col>

              <!-- Reason -->
              <v-col cols="12">
                <v-textarea
                  v-model="updateReason"
                  label="變更原因（必填）"
                  rows="2"
                  :rules="[v => !!v || '請填寫變更原因']"
                  required
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-btn @click="step = 1">上一步</v-btn>
            <v-spacer />
            <v-btn
              color="primary"
              :disabled="!hasEnabledFields || !updateReason"
              @click="step = 3"
            >
              預覽變更
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Step 3: Confirm and Execute -->
    <v-row v-if="step === 3">
      <v-col cols="12">
        <v-card>
          <v-card-title>步驟 3: 確認變更</v-card-title>

          <v-card-text>
            <!-- Summary -->
            <v-alert type="warning" variant="tonal" class="mb-4">
              <strong>即將更新 {{ selectedPets.length }} 隻寵物的以下欄位：</strong>
            </v-alert>

            <v-list>
              <v-list-item
                v-for="field in enabledFieldsSummary"
                :key="field.name"
              >
                <v-list-item-title>{{ field.label }}</v-list-item-title>
                <v-list-item-subtitle>{{ field.value }}</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-2" />

              <v-list-item>
                <v-list-item-title>變更原因</v-list-item-title>
                <v-list-item-subtitle>{{ updateReason }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <!-- Selected Pets -->
            <v-expansion-panels class="mt-4">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  查看將被更新的寵物清單 ({{ selectedPets.length }})
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-chip
                    v-for="pet in selectedPetObjects"
                    :key="pet.id"
                    class="ma-1"
                  >
                    {{ pet.name }}
                  </v-chip>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Progress -->
            <v-progress-linear
              v-if="updating"
              :model-value="updateProgress"
              color="primary"
              height="25"
              class="mt-4"
            >
              <template #default="{ value }">
                <strong>{{ Math.ceil(value) }}%</strong>
              </template>
            </v-progress-linear>

            <!-- Results -->
            <v-alert
              v-if="updateResult"
              :type="updateResult.failed === 0 ? 'success' : 'warning'"
              variant="tonal"
              class="mt-4"
            >
              <div class="text-h6 mb-2">更新完成</div>
              <div>成功: {{ updateResult.successful }} 隻</div>
              <div>失敗: {{ updateResult.failed }} 隻</div>

              <!-- Failed Items -->
              <v-expansion-panels v-if="updateResult.failed > 0" class="mt-2">
                <v-expansion-panel>
                  <v-expansion-panel-title>查看失敗項目</v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-list dense>
                      <v-list-item
                        v-for="result in updateResult.results.filter((r: any) => !r.success)"
                        :key="result.pet_id"
                      >
                        <v-list-item-title>
                          寵物 ID: {{ result.pet_id }}
                        </v-list-item-title>
                        <v-list-item-subtitle class="text-error">
                          {{ result.error }}
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-alert>
          </v-card-text>

          <v-card-actions>
            <v-btn @click="step = 2" :disabled="updating">上一步</v-btn>
            <v-spacer />
            <v-btn
              v-if="!updateResult"
              color="primary"
              :loading="updating"
              @click="executeBatchUpdate"
            >
              確認執行
            </v-btn>
            <v-btn
              v-else
              color="primary"
              @click="resetForm"
            >
              完成
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import apiClient from '@/services/api'

interface Pet {
  id: number
  name: string
  species: string
  breed: string | null
  age_months: number | null
  status: string
  location: string | null
  primary_photo_url: string | null
}

interface EditField {
  enabled: boolean
  value: any
}

// State
const step = ref(1)
const loading = ref(false)
const updating = ref(false)
const updateProgress = ref(0)
const updateResult = ref<any>(null)

const pets = ref<Pet[]>([])
const selectedPets = ref<number[]>([])
const updateReason = ref('')

const filters = ref({
  status: null,
  species: null,
  search: ''
})

const editFields = ref<Record<string, EditField>>({
  status: { enabled: false, value: null },
  location: { enabled: false, value: '' },
  vaccination_status: { enabled: false, value: false },
  sterilized: { enabled: false, value: false },
  adoption_fee: { enabled: false, value: 0 },
  health_status: { enabled: false, value: '' }
})

// Options
const statusOptions = [
  { title: '草稿', value: 'draft' },
  { title: '待審核', value: 'pending_review' },
  { title: '可領養', value: 'available' },
  { title: '已預約', value: 'reserved' },
  { title: '已領養', value: 'adopted' },
  { title: '暫不開放', value: 'unavailable' }
]

const speciesOptions = [
  { title: '狗', value: 'dog' },
  { title: '貓', value: 'cat' },
  { title: '兔子', value: 'rabbit' },
  { title: '其他', value: 'other' }
]

const petHeaders = [
  { title: '名稱', key: 'name', sortable: true },
  { title: '物種', key: 'species', sortable: true },
  { title: '品種', key: 'breed', sortable: false },
  { title: '年齡', key: 'age_months', sortable: true },
  { title: '狀態', key: 'status', sortable: true },
  { title: '地點', key: 'location', sortable: false }
]

// Computed
const hasEnabledFields = computed(() => {
  return Object.values(editFields.value).some(field => field.enabled)
})

const enabledFieldsSummary = computed(() => {
  const summary: Array<{ name: string; label: string; value: string }> = []

  Object.entries(editFields.value).forEach(([key, field]) => {
    if (field.enabled) {
      let label = key
      let value = String(field.value)

      // Format labels
      const labels: Record<string, string> = {
        status: '狀態',
        location: '所在地點',
        vaccination_status: '疫苗接種',
        sterilized: '結紮狀態',
        adoption_fee: '領養費用',
        health_status: '健康狀況'
      }

      label = labels[key] || key

      // Format values
      if (key === 'status') {
        const option = statusOptions.find(opt => opt.value === field.value)
        value = option ? option.title : field.value
      } else if (key === 'vaccination_status' || key === 'sterilized') {
        value = field.value ? '是' : '否'
      } else if (key === 'adoption_fee') {
        value = `NT$ ${field.value}`
      }

      summary.push({ name: key, label, value })
    }
  })

  return summary
})

const selectedPetObjects = computed(() => {
  return pets.value.filter(pet => selectedPets.value.includes(pet.id))
})

// Methods
const loadPets = async () => {
  loading.value = true

  try {
    const params = new URLSearchParams()
    if (filters.value.status) params.append('status', filters.value.status)
    if (filters.value.species) params.append('species', filters.value.species)
    if (filters.value.search) params.append('search', filters.value.search)

    const response = await apiClient.get('/pets', { params })
    pets.value = response.data.pets || []
    
  } catch (error) {
    console.error('Failed to load pets:', error)
  } finally {
    loading.value = false
  }
}

const executeBatchUpdate = async () => {
  updating.value = true
  updateProgress.value = 0

  try {
    // Build update object
    const updates: Record<string, any> = {}
    Object.entries(editFields.value).forEach(([key, field]) => {
      if (field.enabled) {
        updates[key] = field.value
      }
    })

    // Call batch update API
    const response = await apiClient.put('/pets/batch/update', {
      pet_ids: selectedPets.value,
      updates,
      reason: updateReason.value
    })

    updateResult.value = response.data

    // Simulate progress
    const interval = setInterval(() => {
      updateProgress.value += 10
      if (updateProgress.value >= 100) {
        clearInterval(interval)
      }
    }, 100)
    
  } catch (error: any) {
    console.error('Batch update failed:', error)
    alert(error.response?.data?.detail || '批次更新失敗')
  } finally {
    updating.value = false
    updateProgress.value = 100
  }
}

const resetForm = () => {
  step.value = 1
  selectedPets.value = []
  updateReason.value = ''
  updateResult.value = null
  
  Object.keys(editFields.value).forEach(key => {
    editFields.value[key].enabled = false
  })
}

// Helper functions
const getSpeciesLabel = (species: string) => {
  const option = speciesOptions.find(opt => opt.value === species)
  return option ? option.title : species
}

const getStatusLabel = (status: string) => {
  const option = statusOptions.find(opt => opt.value === status)
  return option ? option.title : status
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'grey',
    pending_review: 'orange',
    available: 'green',
    reserved: 'blue',
    adopted: 'purple',
    unavailable: 'red'
  }
  return colors[status] || 'grey'
}

// Load pets on mount
loadPets()
</script>

<style scoped lang="scss">
.batch-edit-page {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
