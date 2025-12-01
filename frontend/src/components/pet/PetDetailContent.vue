<template>
  <v-container v-if="!loading && pet" fluid class="pet-detail-content">
    <!-- Main Content -->
    <v-row>
      <!-- Left Column - Photos -->
      <v-col cols="12" md="6">
        <v-card>
          <div class="photo-carousel-container">
            <v-img
              :src="primaryPhoto"
              :alt="pet.name"
              height="500"
              cover
              class="pet-main-photo"
              eager
            >
              <template v-slot:placeholder>
                <v-row
                  class="fill-height ma-0"
                  align="center"
                  justify="center"
                >
                  <v-progress-circular
                    indeterminate
                    color="grey-lighten-5"
                  ></v-progress-circular>
                </v-row>
              </template>
            </v-img>

            <!-- Navigation Arrows (only show if more than 1 photo) -->
            <div v-if="pet.photos && pet.photos.length > 1" class="photo-navigation">
              <v-btn
                icon
                size="large"
                variant="elevated"
                color="white"
                class="nav-arrow nav-arrow-left"
                @click="previousPhoto"
                :disabled="selectedPhotoIndex === 0"
              >
                <v-icon size="large">mdi-chevron-left</v-icon>
              </v-btn>
              
              <v-btn
                icon
                size="large"
                variant="elevated"
                color="white"
                class="nav-arrow nav-arrow-right"
                @click="nextPhoto"
                :disabled="selectedPhotoIndex === pet.photos.length - 1"
              >
                <v-icon size="large">mdi-chevron-right</v-icon>
              </v-btn>

              <!-- Photo Counter -->
              <div class="photo-counter">
                {{ selectedPhotoIndex + 1 }} / {{ pet.photos.length }}
              </div>
            </div>
          </div>

          <!-- Photo Gallery Thumbnails -->
          <v-card-text v-if="pet.photos && pet.photos.length > 1" class="pa-2">
            <v-row dense>
              <v-col
                v-for="(photo, index) in pet.photos"
                :key="photo.id"
                cols="3"
              >
                <v-img
                  :src="photo.file_url"
                  :alt="`${pet.name} photo ${index + 1}`"
                  height="100"
                  cover
                  class="cursor-pointer thumbnail"
                  :class="{ 'thumbnail-active': selectedPhotoIndex === index }"
                  @click="selectedPhotoIndex = index"
                  lazy-src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23f0f0f0' width='100' height='100'/%3E%3C/svg%3E"
                ></v-img>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column - Details -->
      <v-col cols="12" md="6">
        <!-- Basic Info Card -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center justify-space-between">
            <div>
              <h1 class="text-h3">{{ pet.name }}</h1>
              <v-chip
                :color="getStatusColor(pet.status)"
                size="small"
                class="mt-2"
              >
                {{ getStatusText(pet.status) }}
              </v-chip>
            </div>
            <div class="d-flex gap-2">
              <v-btn
                :icon="isFavorite ? 'mdi-heart' : 'mdi-heart-outline'"
                variant="text"
                :color="isFavorite ? 'red' : 'grey'"
                @click="toggleFavorite"
              ></v-btn>
              <!--
              <v-btn
                icon="mdi-message-text"
                variant="text"
                color="primary"
                @click="contactShelter"
              >
                <v-icon>mdi-message-text</v-icon>
                <v-tooltip activator="parent" location="bottom">
                  聯繫機構
                </v-tooltip>
              </v-btn>
              <v-btn
                icon="mdi-share-variant"
                variant="text"
                @click="sharePet"
              ></v-btn>-->
            </div>
          </v-card-title>

          <v-card-text>
            <!-- Quick Stats -->
            <v-row dense class="mb-4">
              <v-col cols="6" sm="3">
                <div class="text-caption text-grey">品種</div>
                <div class="text-body-1 font-weight-bold">{{ pet.breed || '混種' }}</div>
              </v-col>
              <v-col cols="6" sm="3">
                <div class="text-caption text-grey">年齡</div>
                <div class="text-body-1 font-weight-bold">{{ calculateAge(pet.age_years, pet.age_months) }}</div>
              </v-col>
              <v-col cols="6" sm="3">
                <div class="text-caption text-grey">性別</div>
                <div class="text-body-1 font-weight-bold">{{ getGenderText(pet.gender) }}</div>
              </v-col>
              <v-col cols="6" sm="3">
                <div class="text-caption text-grey">體型</div>
                <div class="text-body-1 font-weight-bold">{{ getSizeText(pet.size) }}</div>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <!-- Description -->
            <div class="mb-4">
              <h3 class="text-h6 mb-2 d-flex align-center" style="font-weight: bold;">
                <v-icon icon="mdi-paw" class="me-2"/>
                關於 {{ pet.name }}
              </h3>
              <p class="text-body-1">{{ pet.description }}</p>
              <p class="text-body-1">{{ pet.behavioral_info }}</p>
            </div>
            <v-divider class="my-4"></v-divider>

            <!-- Characteristics -->
            <div class="mb-4">
              <h3 class="text-h6 mb-2 d-flex align-center" style="font-weight: bold;">
                <v-icon icon="mdi-creation" class="me-2" />
                性格特徵
              </h3>
              <v-chip-group>
                <v-chip
                  v-if="pet.energy_level"
                  color="blue"
                  variant="flat"
                >
                  {{ getEnergyText(pet.energy_level) }}
                </v-chip>
                <v-chip
                  v-if="pet.good_with_kids"
                  color="green"
                  variant="flat"
                >
                  適合有小孩的家庭
                </v-chip>
                <v-chip
                  v-if="pet.good_with_pets"
                  color="orange"
                  variant="flat"
                >
                  可與其他寵物相處
                </v-chip>
                <v-chip
                  v-if="pet.house_trained"
                  color="purple"
                  variant="flat"
                >
                  已訓練
                </v-chip>
              </v-chip-group>
            </div>
            <v-divider class="my-4"></v-divider>

            <!-- Health Info -->
            <div class="mb-4">
              <h3 class="text-h6 mb-2 d-flex align-center" style="font-weight: bold;">
                <v-icon icon="mdi-medical-bag" class="me-2" />
                健康資訊
              </h3>
              <v-list density="compact">
                <v-list-item prepend-icon="mdi-needle">
                  <v-list-item-title>
                    {{ pet.spayed_neutered ? '已結紮' : '未結紮' }}
                  </v-list-item-title>
                </v-list-item>
                <v-list-item prepend-icon="mdi-shield-check">
                  <v-list-item-title>疫苗接種完整</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>

            <!-- Action Buttons -->
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-btn
                  block
                  color="secondary"
                  variant="outlined"
                  size="large"
                  @click="contactShelter"
                  
                >
                  <v-icon start>mdi-message-text</v-icon>
                  詢問機構
                </v-btn>
              </v-col>
              <v-col v-if="pet?.status === 'available'" cols="12" sm="6">
                <v-btn
                  block
                  color="primary"
                  size="large"
                  prepend-icon="mdi-hand-heart"
                  @click="startAdoption"
                >
                  我想領養
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Additional Details -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-tabs
            v-model="activeTab"
            bg-color="primary"
          >
            <v-tab value="details">詳細資訊</v-tab>
            <v-tab value="health">健康記錄</v-tab>
            <v-tab value="shelter">機構資訊</v-tab>
          </v-tabs>

          <v-card-text>
            <v-window v-model="activeTab">
              <!-- Details Tab -->
              <v-window-item value="details">
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon>mdi-palette</v-icon>
                    </template>
                    <v-list-item-title>顏色</v-list-item-title>
                    <v-list-item-subtitle>{{ pet.color || '未指定' }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon>mdi-flash</v-icon>
                    </template>
                    <v-list-item-title>活力等級</v-list-item-title>
                    <v-list-item-subtitle>{{ getEnergyText(pet.energy_level) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon>mdi-calendar</v-icon>
                    </template>
                    <v-list-item-title>發布日期</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(pet.created_at) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-window-item>

              <!-- Health Tab -->
              <v-window-item value="health">
                <!-- Basic Health Info -->
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="success">mdi-check-circle</v-icon>
                    </template>
                    <v-list-item-title>結紮狀態</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ pet.spayed_neutered ? '已完成結紮手術' : '尚未結紮' }}
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon :color="pet.vaccination_status ? 'success' : 'warning'">
                        mdi-needle
                      </v-icon>
                    </template>
                    <v-list-item-title>疫苗接種狀態</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ pet.vaccination_status ? '疫苗接種紀錄完整' : '疫苗接種未完成' }}
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="pet.health_status">
                    <template v-slot:prepend>
                      <v-icon color="info">mdi-heart-pulse</v-icon>
                    </template>
                    <v-list-item-title>健康狀況</v-list-item-title>
                    <v-list-item-subtitle>{{ pet.health_status }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-window-item>

              <!-- Shelter Tab -->
              <v-window-item value="shelter">
                <div class="pa-4">
                  <h3 class="text-h6 mb-2">送養機構</h3>
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon>mdi-domain</v-icon>
                      </template>
                      <v-list-item-subtitle class="text-grey">機構名稱</v-list-item-subtitle>
                      <v-list-item-title class="text-black">{{ pet.shelter_name || '未設定' }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </div>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-else-if="loading" fluid class="pet-detail-content">
    <v-row>
      <!-- Left Column Skeleton -->
      <v-col cols="12" md="6">
        <v-card>
          <v-skeleton-loader type="image" height="500" />
          <v-card-text class="pa-2">
            <v-row dense>
              <v-col v-for="i in 4" :key="i" cols="3">
                <v-skeleton-loader type="image" height="100" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Right Column Skeleton -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-skeleton-loader type="heading" width="200" />
          </v-card-title>
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col v-for="i in 4" :key="i" cols="6" sm="3">
                <v-skeleton-loader type="text" />
                <v-skeleton-loader type="text" width="60" />
              </v-col>
            </v-row>
            <v-skeleton-loader type="paragraph" />
            <v-skeleton-loader type="chip" class="mt-4" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <v-container v-else-if="error">
    <v-alert type="error" variant="tonal">
      {{ error }}
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFavoritesStore } from '@/stores/favorites'
import { calculateAge } from '@/utils/ageCalculator'
import apiClient from '@/api/client'
import { createOrGetChatRoom } from '@/api/chat'

const props = defineProps<{
  petId: number
  inDialog?: boolean
  initialData?: any  // 從列表頁傳入的初始數據
}>()

const emit = defineEmits<{
  close: []
}>()

const router = useRouter()
const authStore = useAuthStore()
const favoritesStore = useFavoritesStore()

const pet = ref<any>(props.initialData || null)  // 如果有初始數據，立即使用
const loading = ref(!props.initialData)  // 有初始數據就不顯示載入中
const error = ref<string | null>(null)
const selectedPhotoIndex = ref(0)
const activeTab = ref('details')

const primaryPhoto = computed(() => {
  if (!pet.value) return '/placeholder-pet.jpg'
  
  if (pet.value.photos && pet.value.photos.length > 0) {
    return pet.value.photos[selectedPhotoIndex.value]?.file_url || pet.value.photos[0].file_url
  }
  
  return pet.value.primary_photo_url || '/placeholder-pet.jpg'
})

const isFavorite = computed(() => {
  return favoritesStore.isFavorite(props.petId)
})

// 簡單的記憶體快取
const petCache = new Map<number, any>()
const CACHE_DURATION = 5 * 60 * 1000 // 5 分鐘

onMounted(() => {
  fetchPetDetails()
})

const fetchPetDetails = async () => {
  try {
    // 如果已有初始數據，先設置 loading 為 false 讓畫面立即顯示
    if (props.initialData && !pet.value) {
      pet.value = props.initialData
    }
    
    loading.value = true
    error.value = null
    
    // 先檢查快取
    const cached = petCache.get(props.petId)
    if (cached && (Date.now() - cached.timestamp < CACHE_DURATION)) {
      pet.value = cached.data
      loading.value = false
      return
    }
    
    const response = await apiClient.get(`/pets/${props.petId}`)
    pet.value = response.data.data
    
    // 快取數據
    petCache.set(props.petId, {
      data: pet.value,
      timestamp: Date.now()
    })
    
    // 只預載主照片，其他照片懶加載
    if (pet.value?.photos && pet.value.photos.length > 0) {
      const primaryPhoto = pet.value.photos.find((p: any) => p.is_primary) || pet.value.photos[0]
      if (primaryPhoto?.file_url) {
        const img = new Image()
        img.src = primaryPhoto.file_url
      }
    }
  } catch (err: any) {
    console.error('Error fetching pet details:', err)
    error.value = err.response?.data?.detail || '載入寵物資訊時發生錯誤'
  } finally {
    loading.value = false
  }
}

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/login', query: { redirect: `/pets/${props.petId}` } })
    return
  }

  try {
    if (favoritesStore.isFavorite(props.petId)) {
      await favoritesStore.removeFavorite(props.petId)
    } else {
      await favoritesStore.addFavorite(props.petId)
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
  }
}

const contactShelter = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/login', query: { redirect: `/pets/${props.petId}` } })
    return
  }
  
  try {
    const chatRoom = await createOrGetChatRoom(props.petId)
    
    const prefillText = `你好！我想詢問有關${pet.value?.name || '這隻寵物'}的資訊~`
    
    if (props.inDialog) {
      emit('close')
      // Wait for dialog to close then navigate
      setTimeout(() => {
        router.push({
          path: `/chat/${chatRoom.id}`,
          query: {
            title: pet.value?.name || '聊天室',
            prefill: prefillText
          }
        })
      }, 300)
    } else {
      router.push({
        path: `/chat/${chatRoom.id}`,
        query: {
          title: pet.value?.name || '聊天室',
          prefill: prefillText
        }
      })
    }
  } catch (error) {
    console.error('Failed to create chat room:', error)
    alert('無法開啟聊天室，請稍後再試')
  }
}

const startAdoption = () => {
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/login', query: { redirect: `/pets/${props.petId}` } })
    return
  }
  
  if (props.inDialog) {
    emit('close')
    // Wait for dialog to close then navigate
    setTimeout(() => {
      router.push(`/pets/${props.petId}/adopt`)
    }, 300)
  } else {
    router.push(`/pets/${props.petId}/adopt`)
  }
}

const getGenderText = (gender: string): string => {
  const genderMap: Record<string, string> = {
    male: '公',
    female: '母',
    unknown: '未知'
  }
  return genderMap[gender] || gender
}

const getSizeText = (size: string): string => {
  const sizeMap: Record<string, string> = {
    small: '小型',
    medium: '中型',
    large: '大型'
  }
  return sizeMap[size] || size
}

const getEnergyText = (energy: string | null): string => {
  if (!energy) return '未知'
  const energyMap: Record<string, string> = {
    low: '低活力',
    medium: '中等活力',
    high: '高活力'
  }
  return energyMap[energy] || energy
}

const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    available: 'success',
    pending: 'warning',
    adopted: 'info',
    unavailable: 'error'
  }
  return colorMap[status] || 'grey'
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    available: '可領養',
    pending: '審核中',
    adopted: '已領養',
    unavailable: '暫不開放'
  }
  return statusMap[status] || status
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Photo navigation functions
const nextPhoto = () => {
  if (pet.value?.photos && selectedPhotoIndex.value < pet.value.photos.length - 1) {
    selectedPhotoIndex.value++
  }
}

const previousPhoto = () => {
  if (selectedPhotoIndex.value > 0) {
    selectedPhotoIndex.value--
  }
}

const sharePet = () => {
  if (navigator.share && pet.value) {
    navigator.share({
      title: `領養 ${pet.value.name}`,
      text: `來看看這隻可愛的${pet.value.species} - ${pet.value.name}！`,
      url: `${window.location.origin}/pets/${props.petId}`
    })
  } else {
    // Fallback: Copy URL to clipboard
    navigator.clipboard.writeText(`${window.location.origin}/pets/${props.petId}`)
    alert('連結已複製到剪貼簿！')
  }
}

const viewShelterDetails = () => {
  if (pet.value) {
    if (props.inDialog) {
      emit('close')
      // Wait for dialog to close then navigate
      setTimeout(() => {
        router.push(`/shelters/${pet.value!.shelter_id}`)
      }, 300)
    } else {
      router.push(`/shelters/${pet.value.shelter_id}`)
    }
  }
}
</script>

<style scoped>
.pet-detail-content {
  max-width: 1400px;
  margin: 0 auto;
}

.photo-carousel-container {
  position: relative;
}

.pet-main-photo {
  border-radius: 8px;
}

.photo-navigation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.nav-arrow {
  pointer-events: auto;
  opacity: 0.9;
  transition: all 0.2s;
}

.nav-arrow:hover:not(:disabled) {
  opacity: 1;
  transform: scale(1.1);
}

.nav-arrow:disabled {
  opacity: 0.3;
}

.nav-arrow-left {
  position: absolute;
  left: 16px;
}

.nav-arrow-right {
  position: absolute;
  right: 16px;
}

.photo-counter {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  pointer-events: none;
}

.thumbnail {
  border: 3px solid transparent;
  border-radius: 4px;
  transition: all 0.2s;
}

.thumbnail:hover {
  border-color: rgb(var(--v-theme-primary));
  opacity: 0.8;
}

.thumbnail-active {
  border-color: rgb(var(--v-theme-primary));
}

.cursor-pointer {
  cursor: pointer;
}

.gap-2 {
  gap: 8px;
}
</style>
