<template>
  <v-container class="pet-detail-page" fluid>
    <!-- Loading State -->
    <v-row v-if="loading" justify="center">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <p class="text-h6 mt-4">載入中...</p>
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="my-4"
    >
      {{ error }}
    </v-alert>

    <!-- Pet Details -->
    <template v-else-if="pet">
      <!-- Back Button -->
      <v-row>
        <v-col cols="12">
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            @click="goBack"
          >
            返回列表
          </v-btn>
        </v-col>
      </v-row>

      <!-- Main Content -->
      <v-row>
        <!-- Left Column - Photos -->
        <v-col cols="12" md="6">
          <v-card>
            <v-img
              :src="primaryPhoto"
              :alt="pet.name"
              height="500"
              cover
              class="pet-main-photo"
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
                  :icon="(favoritesStore.isFavoriteForCurrentUser ? favoritesStore.isFavoriteForCurrentUser(pet.id) : favoritesStore.isFavorite(pet.id)) ? 'mdi-heart' : 'mdi-heart-outline'"
                  variant="text"
                  :color="(favoritesStore.isFavoriteForCurrentUser ? favoritesStore.isFavoriteForCurrentUser(pet.id) : favoritesStore.isFavorite(pet.id)) ? 'red' : 'pink'"
                  @click="toggleFavorite"
                ></v-btn>
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
                ></v-btn>
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
              <div class="mb-4" >
                <h3 class="text-h6 mb-2 d-flex align-center"style="font-weight: bold;">
                  <v-icon icon = "mdi-paw" class="me-2"/>
                  關於 {{ pet.name }}
                </h3>

                <p class="text-body-1">{{ pet.description }}</p>
                <p class="text-body-1">{{ pet.behavioral_info}}</p>
              </div>
              <v-divider class="my-4"></v-divider>

              <!-- Characteristics -->
              <div class="mb-4">
                <h3 class="text-h6 mb-2 d-flex align-center" style="font-weight: bold;">
                  <v-icon icon="mdi-creation" class="me-2" />
                  性格特徵</h3>
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
                <h3 class="text-h6 mb-2 d-flex align-center" style="font-weight: bold; ">
                  <v-icon icon="mdi-medical-bag" class="me-2" />
                  健康資訊</h3>
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
                <v-col cols="12" sm="6">
                  <v-btn
                    block
                    color="secondary"
                    variant="outlined"
                    size="large"
                    prepend-icon="mdi-phone"
                    @click="contactShelter"
                  >
                    聯繫機構
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

                  <v-divider class="my-4"></v-divider>

                  <!-- Vaccination Timeline -->
                  <VaccinationTimeline :pet-id="pet.id" />
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
                        <v-list-item-title>機構名稱</v-list-item-title>
                        <v-list-item-subtitle>{{ pet.shelter_name || '未設定' }}</v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </div>
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Contact Modal -->
    <ContactModal
      v-model="showContactModal"
      :pet-id="petId"
      :pet-name="pet?.name"
      :shelter-id="pet?.shelter_id"
      @submitted="handleContactSubmitted"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFavoritesStore } from '@/stores/favorites'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'
import { createOrGetChatRoom } from '@/api/chat'
import ContactModal from '@/components/pet/ContactModal.vue'
import VaccinationTimeline from '@/components/pet/VaccinationTimeline.vue'
import { calculateAge } from '@/utils/ageCalculator'

// Types
interface Pet {
  id: number
  name: string
  species: string
  breed: string | null
  age_years: number
  age_months: number
  gender: string
  size: string
  color: string | null
  description: string
  behavioral_info: string | null
  status: string
  adoption_fee: number | null
  shelter_id: number
  shelter_name?: string | null
  spayed_neutered: boolean
  vaccination_status?: boolean
  health_status?: string
  good_with_kids: boolean
  good_with_pets: boolean
  house_trained: boolean
  energy_level: string | null
  primary_photo_url: string | null
  created_at: string
  updated_at: string
  photos?: Array<{
    id: number
    file_url: string
    caption: string | null
  }>
}

// Composables
const route = useRoute()
const router = useRouter()
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()

// State
const pet = ref<Pet | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const selectedPhotoIndex = ref(0)
const activeTab = ref('details')
const showContactModal = ref(false)

// Computed
const petId = computed(() => parseInt(route.params.id as string))

const primaryPhoto = computed(() => {
  if (!pet.value) return '/placeholder-pet.jpg'
  
  if (pet.value.photos && pet.value.photos.length > 0) {
    return pet.value.photos[selectedPhotoIndex.value]?.file_url || pet.value.photos[0].file_url
  }
  
  return pet.value.primary_photo_url || '/placeholder-pet.jpg'
})

// Methods
// Check if we're in an iframe
const isInIframe = () => {
  try {
    return window.self !== window.top
  } catch (e) {
    return true
  }
}

// Handle login redirect (works in iframe and normal context)
const redirectToLogin = () => {
  const loginPath = '/auth/login'
  const redirectQuery = { redirect: route.fullPath }
  
  if (isInIframe()) {
    // If in iframe, close dialog and navigate in parent window
    if (window.top) {
      window.top.location.href = `${window.location.origin}${loginPath}?redirect=${encodeURIComponent(route.fullPath)}`
    }
  } else {
    // Normal navigation
    router.push({ path: loginPath, query: redirectQuery })
  }
}

const fetchPetDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await apiClient.get(`/pets/${petId.value}`)
    pet.value = response.data.data
  } catch (err: any) {
    console.error('Error fetching pet details:', err)
    error.value = err.response?.data?.detail || '載入寵物資訊時發生錯誤'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  const from = route.query.from
  if (from === 'favorites') {
    router.push('/favorites')
  } else if (from === 'management') {
    router.push('/pets/manage')
  } else {
    router.push('/pets')
  }
}

const toggleFavorite = async () => {
  if (!petId.value) return
  // If user not authenticated, redirect to login and preserve return path
  if (!authStore.isAuthenticated) {
    redirectToLogin()
    return
  }

  const favoritesStore = useFavoritesStore()

  try {
    if (favoritesStore.isFavorite(petId.value)) {
      await favoritesStore.removeFavorite(petId.value)
    } else {
      await favoritesStore.addFavorite(petId.value)
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
  }
}

const sharePet = () => {
  if (navigator.share && pet.value) {
    navigator.share({
      title: `領養 ${pet.value.name}`,
      text: `來看看這隻可愛的${pet.value.species} - ${pet.value.name}！`,
      url: window.location.href
    })
  } else {
    // Fallback: Copy URL to clipboard
    navigator.clipboard.writeText(window.location.href)
    alert('連結已複製到剪貼簿！')
  }
}

const startAdoption = () => {
  // Check authentication first
  if (!authStore.isAuthenticated) {
    redirectToLogin()
    return
  }
  
  // Navigate to adoption application form
  router.push(`/pets/${petId.value}/adopt`)
}

const contactShelter = async () => {
  // Check authentication first
  if (!authStore.isAuthenticated) {
    redirectToLogin()
    return
  }
  
  // 建立或獲取聊天室，然後導航
  try {
    const chatRoom = await createOrGetChatRoom(petId.value)
    
    const prefillText = `你好！我想詢問有關${pet.value?.name || '這隻寵物'}的資訊~`
    
    // 導航到聊天室
    router.push({
      path: `/chat/${chatRoom.id}`,
      query: {
        title: pet.value?.name || '聊天室',
        prefill: prefillText,
      }
    })
  } catch (error) {
    console.error('Failed to create chat room:', error)
    alert('無法開啟聊天室，請稍後再試')
  }
}

const handleContactSubmitted = () => {
  // Handle successful contact form submission
  console.log('Contact form submitted successfully')
  // Could show a success message or update UI
}

const viewShelterDetails = () => {
  if (pet.value) {
    router.push(`/shelters/${pet.value.shelter_id}`)
  }
}

// Utility Functions
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
    large: '大型',
    extra_large: '超大型'
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
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  fetchPetDetails()
})

// Watch route changes
watch(() => route.params.id, () => {
  if (route.params.id) {
    selectedPhotoIndex.value = 0
    fetchPetDetails()
  }
})
</script>

<style scoped>
.pet-detail-page {
  max-width: 1400px;
  margin: 0 auto;
}

.pet-main-photo {
  border-radius: 8px;
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
