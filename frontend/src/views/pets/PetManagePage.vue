<template>
  <v-app>
    <AppHeader />
    <v-main>
      <v-container class="py-8">
        <v-row>
          <v-col cols="12">
            <div class="d-flex align-center mb-6">
          <h1 class="text-h4">寵物管理</h1>
          <v-spacer />
          <v-btn
            color="primary"
            variant="elevated"
            size="large"
            to="/pets/create"
          >
            <v-icon icon="mdi-plus" start />
            發布新寵物
          </v-btn>
        </div>

        <!-- Filters -->
        <v-card class="mb-6">
          <v-card-text>
            <v-row>
              <!-- Search -->
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchQuery"
                  label="搜尋寵物名稱"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="debouncedSearch"
                />
              </v-col>

              <!-- Status Filter -->
              <v-col cols="12" md="4">
                <v-select
                  v-model="statusFilter"
                  label="狀態"
                  :items="statusOptions"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="handleFilterChange"
                />
              </v-col>

              <!-- Species Filter -->
              <v-col cols="12" md="4">
                <v-select
                  v-model="speciesFilter"
                  label="種類"
                  :items="speciesOptions"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="handleFilterChange"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Pet List -->
        <v-card>
          <v-data-table
            :headers="headers"
            :items="pets"
            :loading="loading"
            :items-per-page="itemsPerPage"
            :items-length="totalItems"
            loading-text="載入中..."
            @update:options="onOptionsUpdate"
          >
            <!-- Photo Column -->
            <template #item.photo="{ item }">
              <v-avatar size="100" rounded class="my-2">
                <v-img
                  v-if="(getPhotoUrl(item))"
                  :src="getPhotoUrl(item)"
                  cover
                  lazy-src="/placeholder-pet.png"
                  @error="() => handleImageError(item)"
                >
                  <template v-slot:placeholder>
                    <v-skeleton-loader type="image" />
                  </template>
                </v-img>
                <v-icon v-else icon="mdi-image-off" />
              </v-avatar>
            </template>

            <!-- Name Column -->
            <template #item.name="{ item }">
              <div class="font-weight-bold">{{ item.name }}</div>
              <div class="text-caption text-grey">{{ getSpeciesLabel(item.species) }}</div>
            </template>

            <!-- Breed Column -->
            <template #item.breed="{ item }">
              {{ item.breed || '-' }}
            </template>

            <!-- Birth Date Column -->
            <template #item.birth_date="{ item }">
              <div v-if="item.age_years && item.age_months">
                <div class="text-body-2">{{ item.age_years }}年{{ item.age_months }}月</div>
                <div class="text-caption text-grey">({{ calculateAge(item.age_years, item.age_months) }})</div>
              </div>
              <span v-else>-</span>
            </template>

            <!-- Status Column -->
            <template #item.status="{ item }">
              <PetStatusBadge :status="item.status" size="small" />
            </template>

            <!-- Created At Column -->
            <template #item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>

            <!-- Updated At Column -->
            <template #item.updated_at="{ item }">
              {{ formatDate(item.updated_at) }}
            </template>

            <!-- Actions Column -->
            <template #item.actions="{ item }">
              <div class="d-flex gap-2">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="handleViewDetails(item.id)"
                />
                <v-menu>
                  <template #activator="{ props }">
                    <v-btn v-bind="props" icon size="small" variant="text">
                      <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="goToEdit(item.id, 1)">
                      <v-list-item-title>編輯資訊</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="goToEdit(item.id, 2)">
                      <v-list-item-title>編輯照片</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="openStatusDialog(item)">
                      <v-list-item-title>編輯狀態</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
                <v-btn
                  v-if="canSubmitForReview(item)"
                  icon="mdi-send"
                  size="small"
                  variant="text"
                  color="primary"
                  @click="confirmSubmitReview(item)"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  color="error"
                  @click="confirmDelete(item)"
                />
              </div>
            </template>

            <!-- Loading slot -->
            <template #loading>
              <v-skeleton-loader
                v-for="i in 5"
                :key="i"
                type="table-row"
              />
            </template>

            <!-- No data slot -->
            <template #no-data>
              <div class="text-center py-8">
                <v-icon icon="mdi-inbox" size="64" color="grey" />
                <div class="text-h6 mt-4 text-grey">尚無寵物資料</div>
                <v-btn
                  color="primary"
                  variant="elevated"
                  class="mt-4"
                  to="/pets/create"
                >
                  <v-icon icon="mdi-plus" start />
                  發布第一隻寵物
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5">
          確認刪除
        </v-card-title>
        <v-card-text>
          確定要刪除「{{ selectedPet?.name }}」嗎？此操作無法復原。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            :loading="deleting"
            @click="deletePet"
          >
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Submit Review Confirmation Dialog -->
    <v-dialog v-model="submitDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5">
          提交審核
        </v-card-title>
        <v-card-text>
          確定要提交「{{ selectedPet?.name }}」審核嗎？
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="submitDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="submitting"
            @click="submitReview"
          >
            提交
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Status Edit Dialog -->
    <v-dialog v-model="statusDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5">
          編輯狀態
        </v-card-title>
        <v-card-text>
          <div class="mb-4">
            <strong>寵物名稱：</strong>{{ selectedPet?.name }}
          </div>
          <div class="mb-2">
            <strong>目前狀態：</strong>
            <PetStatusBadge v-if="selectedPet" :status="selectedPet.status" size="small" class="ml-2" />
          </div>
          <v-select
            v-model="newStatus"
            label="選擇新狀態"
            :items="allStatusOptions"
            variant="outlined"
            density="comfortable"
            class="mt-4"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="statusDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="updatingStatus"
            :disabled="!newStatus || newStatus === selectedPet?.status"
            @click="updateStatus"
          >
            更新狀態
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Pet Detail Dialog -->
    <v-dialog
      v-model="petDetailDialog"
      max-width="90vw"
      scrollable
    >
      <v-card style="height: 85vh;">
        <v-toolbar color="primary" dark dense>
          <v-btn icon="mdi-arrow-left" @click="closePetDialog" />
          <v-toolbar-title>寵物詳情</v-toolbar-title>
          <v-spacer />
          <v-btn icon="mdi-close" @click="closePetDialog" />
        </v-toolbar>
        <v-card-text class="pa-0" style="height: calc(85vh - 48px); overflow-y: auto;">
          <PetDetailContent 
            v-if="selectedPetId" 
            :pet-id="selectedPetId" 
            :in-dialog="true"
            @close="closePetDialog"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import PetStatusBadge from '@/components/pet/PetStatusBadge.vue'
import PetDetailContent from '@/components/pet/PetDetailContent.vue'
import { calculateAge } from '@/utils/ageCalculator'
import { petService } from '@/services/pet'
import { useNotificationStore } from '@/stores/notification'
import { PetStatus, PetSpecies, type Pet } from '@/types/pet'
import { useRouter } from 'vue-router'

const router = useRouter()

const notificationStore = useNotificationStore()

const petDetailDialog = ref(false)
const selectedPetId = ref<number | null>(null)

const handleViewDetails = (petId: number) => {
  selectedPetId.value = petId
  petDetailDialog.value = true
}

const closePetDialog = () => {
  petDetailDialog.value = false
  selectedPetId.value = null
}

const openInNewTab = () => {
  if (selectedPetId.value) {
    window.open(`/pets/${selectedPetId.value}`, '_blank')
  }
}

// Helper: get best photo URL for preview (falls back to several fields)
const getPhotoUrl = (item: any) => {
  if (!item) return null
  
  // First try: primary_photo_url (direct field from backend)
  if (item.primary_photo_url) {
    return item.primary_photo_url
  }
  
  // Second try: photos array
  if (item.photos && item.photos.length > 0) {
    const photo = item.photos[0]
    return photo?.file_url || photo?.url || photo?.preview || null
  }
  
  // Fallback: return null to show placeholder icon
  return null
}

// Navigate to edit page with optional step: 1=info,2=photos,3=status
const goToEdit = (petId: number, step: number) => {
  const s = Math.min(Math.max(Number(step) || 1, 1), 3)
  router.push({ path: `/pets/${petId}/edit`, query: { step: String(s) } })
}

// Handle image load error (e.g., 403 from expired presigned URL)
const handleImageError = async (item: Pet) => {
  if (!item?.id || !item.photos || item.photos.length === 0) return
  
  try {
    console.log(`🔄 Refreshing photo URLs for pet ${item.id}`)
    const refreshedPhotos = await petService.refreshPhotoUrls(item.id)
    
    // Update the pet's photos with new URLs
    const petIndex = pets.value.findIndex(p => p.id === item.id)
    if (petIndex !== -1 && refreshedPhotos.length > 0) {
      pets.value[petIndex].photos = refreshedPhotos
      console.log(`✅ Photo URLs refreshed for pet ${item.id}`)
    }
  } catch (error) {
    console.error(`❌ Failed to refresh photo URLs for pet ${item.id}:`, error)
  }
}

// Data
const pets = ref<Pet[]>([])
const loading = ref(true) // Start with loading true for skeleton
const searchQuery = ref('')
const statusFilter = ref<PetStatus | null>(null)
const speciesFilter = ref<PetSpecies | null>(null)

// Pagination
const page = ref(1)
const itemsPerPage = ref(10)
const totalItems = ref(0)

// Dialogs
const deleteDialog = ref(false)
const submitDialog = ref(false)
const statusDialog = ref(false)
const selectedPet = ref<Pet | null>(null)
const deleting = ref(false)
const submitting = ref(false)
const updatingStatus = ref(false)
const newStatus = ref<PetStatus | null>(null)

// Table headers
const headers = [
  { title: '照片', key: 'photo', sortable: false },
  { title: '名稱', key: 'name', sortable: true },
  { title: '品種', key: 'breed', sortable: false },
  { title: '出生年月', key: 'birth_date', sortable: false },
  { title: '狀態', key: 'status', sortable: true },
  { title: '建立時間', key: 'created_at', sortable: true },
  { title: '更新時間', key: 'updated_at', sortable: true },
  { title: '操作', key: 'actions', sortable: false },
]

// Filter options
const statusOptions = [
  { title: '全部', value: null },
 // { title: '草稿', value: PetStatus.DRAFT },
  //{ title: '審核中', value: PetStatus.PENDING_REVIEW },
  { title: '可領養', value: PetStatus.AVAILABLE },
  //{ title: '申請中', value: PetStatus.PENDING },
  { title: '已領養', value: PetStatus.ADOPTED },
  //{ title: '已拒絕', value: PetStatus.REJECTED },
  { title: '暫停', value: PetStatus.UNAVAILABLE },
]

// All status options for status dialog (without "全部")
const allStatusOptions = [
  { title: '草稿', value: PetStatus.DRAFT },
  //{ title: '審核中', value: PetStatus.PENDING_REVIEW },
  { title: '可領養', value: PetStatus.AVAILABLE },
  //{ title: '申請中', value: PetStatus.PENDING },
  { title: '已領養', value: PetStatus.ADOPTED },
  { title: '暫停', value: PetStatus.UNAVAILABLE },
]

const speciesOptions = [
  { title: '全部', value: null },
  { title: '狗', value: PetSpecies.DOG },
  { title: '貓', value: PetSpecies.CAT },
  //{ title: '兔子', value: PetSpecies.RABBIT },
  //{ title: '鳥類', value: PetSpecies.BIRD },
  //{ title: '其他', value: PetSpecies.OTHER },
]

const loadPets = async () => {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      limit: itemsPerPage.value,
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (speciesFilter.value) {
      params.species = speciesFilter.value
    }

    console.log('📡 Calling getMyPets with params:', params)
    const response = await petService.getMyPets(params)
    console.log('📥 getMyPets response:', response)
    
    pets.value = response.pets || []
    totalItems.value = response.pagination?.total || 0
    
    console.log('✅ Loaded pets:', pets.value.length, 'Total:', totalItems.value)
    // Debug: Check first pet's photo data
    if (pets.value.length > 0) {
      console.log('🖼️ First pet photo data:', {
        id: pets.value[0].id,
        name: pets.value[0].name,
        primary_photo_url: pets.value[0].primary_photo_url,
        photos: pets.value[0].photos
      })
    }
  } catch (error: any) {
    console.error('❌ Failed to load pets:', error)
    console.error('❌ Error response:', error.response?.data)
    notificationStore.error('載入失敗')
  } finally {
    loading.value = false
  }
}

// Debounced search
let searchTimeout: NodeJS.Timeout | null = null
const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    page.value = 1 // Reset to first page on search
    loadPets()
  }, 300) // Reduced from 500ms to 300ms for faster response
}

const handleFilterChange = () => {
  page.value = 1 // Reset to first page when filter changes
  loadPets()
}

const onOptionsUpdate = (options: any) => {
  console.log('📊 Table options updated:', options)
  // v-data-table uses 1-based page indexing
  page.value = options.page || 1
  itemsPerPage.value = options.itemsPerPage || 10
  loadPets()
}

const canSubmitForReview = (pet: Pet) => {
  return pet.status === PetStatus.DRAFT || pet.status === PetStatus.REJECTED
}

const confirmDelete = (pet: Pet) => {
  selectedPet.value = pet
  deleteDialog.value = true
}

const deletePet = async () => {
  if (!selectedPet.value) return

  deleting.value = true
  try {
    await petService.deletePet(selectedPet.value.id)
    notificationStore.success('刪除成功')
    deleteDialog.value = false
    await loadPets()
  } catch (error) {
    console.error('Failed to delete pet:', error)
    notificationStore.error('刪除失敗')
  } finally {
    deleting.value = false
  }
}

const confirmSubmitReview = (pet: Pet) => {
  selectedPet.value = pet
  submitDialog.value = true
}

const submitReview = async () => {
  if (!selectedPet.value) return

  submitting.value = true
  try {
    await petService.submitForReview(selectedPet.value.id)
    notificationStore.success('已提交審核')
    submitDialog.value = false
    await loadPets()
  } catch (error) {
    console.error('Failed to submit for review:', error)
    notificationStore.error('提交失敗')
  } finally {
    submitting.value = false
  }
}

const openStatusDialog = (pet: Pet) => {
  selectedPet.value = pet
  newStatus.value = pet.status
  statusDialog.value = true
}

const updateStatus = async () => {
  if (!selectedPet.value || !newStatus.value) return

  updatingStatus.value = true
  try {
    await petService.updateStatus(selectedPet.value.id, { status: newStatus.value })
    notificationStore.success('狀態更新成功')
    statusDialog.value = false
    await loadPets()
  } catch (error) {
    console.error('Failed to update status:', error)
    notificationStore.error('狀態更新失敗')
  } finally {
    updatingStatus.value = false
  }
}

const getSpeciesLabel = (species: PetSpecies) => {
  const labels = {
    [PetSpecies.DOG]: '狗',
    [PetSpecies.CAT]: '貓',
    [PetSpecies.RABBIT]: '兔子',
    [PetSpecies.BIRD]: '鳥類',
    [PetSpecies.OTHER]: '其他',
  }
  return labels[species]
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const datePart = date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
  const timePart = date.toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false, // 使用 24 小時制
  })
  return `${datePart} ${timePart}`
}


onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>
