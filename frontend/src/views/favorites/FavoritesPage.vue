<template>
  <app-header />
  <div class="favorites-page">
    <!-- Header -->
    <div class="favorites-header">
      <h1 class="page-title">
        <i class="mdi mdi-heart"></i>
        我的收藏
      </h1>
      <p class="page-subtitle">
        共有 {{ favoriteCount }} 隻寵物在您的收藏清單中
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <!-- 骨架屏 -->
      <div class="favorites-grid">
        <div v-for="i in 6" :key="`skeleton-${i}`" class="skeleton-card">
          <div class="skeleton-image"></div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
          </div>
          <div class="skeleton-actions">
            <div class="skeleton-button"></div>
            <div class="skeleton-button"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <i class="mdi mdi-alert-circle error-icon"></i>
      <p class="error-message">{{ error }}</p>
      <button @click="loadFavorites" class="btn btn-primary">
        重試
      </button>
    </div>

    <!-- Empty State -->
    <EmptyFavorites v-else-if="favoriteCount === 0" />

    <!-- Favorites List -->
    <div v-else class="favorites-content">
      <!-- Filters and Sorting -->
      <div class="favorites-controls">
        <div class="filter-group">
          <label for="species-filter">物種篩選:</label>
          <select 
            id="species-filter" 
            v-model="filters.species" 
            @change="applyFilters"
            class="filter-select"
          >
            <option value="">全部</option>
            <option value="dog">狗</option>
            <option value="cat">貓</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="status-filter">狀態篩選:</label>
          <select 
            id="status-filter" 
            v-model="filters.status" 
            @change="applyFilters"
            class="filter-select"
          >
            <option value="">全部</option>
            <option value="available">可領養</option>
            <option value="pending">待審核</option>
            <option value="adopted">已領養</option>
          </select>
        </div>

        <div class="sort-group">
          <label for="sort-select">排序:</label>
          <select 
            id="sort-select" 
            v-model="sortBy" 
            @change="applySorting"
            class="sort-select"
          >
            <option value="date_desc">收藏時間 (新到舊)</option>
            <option value="date_asc">收藏時間 (舊到新)</option>
            <option value="name_asc">名稱 (A-Z)</option>
            <option value="name_desc">名稱 (Z-A)</option>
          </select>
        </div>
      </div>

      <!-- Favorites Grid -->
      <div class="favorites-grid">
        <FavoriteCard
          v-for="favorite in filteredAndSortedFavorites"
          :key="favorite.pet_id"
          :favorite="favorite"
          @remove="handleRemoveFavorite"
          @view-details="handleViewDetails"
          @prefetch="handlePrefetch"
        />
      </div>

      <!-- Pagination (if needed) -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="prevPage" 
          :disabled="currentPage === 1"
          class="btn btn-secondary"
        >
          上一頁
        </button>
        <span class="page-info">
          第 {{ currentPage }} 頁，共 {{ totalPages }} 頁
        </span>
        <button 
          @click="nextPage" 
          :disabled="currentPage === totalPages"
          class="btn btn-secondary"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- Pet Detail Dialog -->
    <PetDetailDialog
      v-model="showPetDialog"
      :pet-id="selectedPetId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFavoritesStore } from '@/stores/favorites'
import FavoriteCard from './components/FavoriteCard.vue'
import EmptyFavorites from './components/EmptyFavorites.vue'
import api from '@/services/api'
import AppHeader from '@/components/layout/AppHeader.vue'
import PetDetailDialog from '@/components/pet/PetDetailDialog.vue'

const router = useRouter()
const route = useRoute()
const favoritesStore = useFavoritesStore()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const favoritePets = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(12)
const totalFavorites = ref(0)
const showPetDialog = ref(false)
const selectedPetId = ref<number | null>(null)

// Filters and Sorting
const filters = ref({
  species: (route.query.species as string) || '',
  status: (route.query.status as string) || ''
})
const sortBy = ref((route.query.sort as string) || 'date_desc')

// Computed
const favoriteCount = computed(() => favoritePets.value.length)

const totalPages = computed(() => Math.ceil(totalFavorites.value / pageSize.value))

const filteredAndSortedFavorites = computed(() => {
  let result = [...favoritePets.value]

  // Apply filters
  if (filters.value.species) {
    result = result.filter(fav => fav.pet_species === filters.value.species)
  }
  if (filters.value.status) {
    result = result.filter(fav => fav.pet_status === filters.value.status)
  }

  // Apply sorting
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'date_desc':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'date_asc':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      case 'name_asc':
        return a.pet_name.localeCompare(b.pet_name)
      case 'name_desc':
        return b.pet_name.localeCompare(a.pet_name)
      default:
        return 0
    }
  })

  return result
})

// Methods
const loadFavorites = async () => {
  loading.value = true
  error.value = null

  try {
    // 使用 store 的快取機制載入數據
    await favoritesStore.loadFavorites()
    
    // 從 store 獲取資料，並應用分頁
    const allFavorites = favoritesStore.favorites
    console.log('📊 Loaded favorites:', allFavorites)
    
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    
    favoritePets.value = allFavorites.slice(start, end)
    totalFavorites.value = allFavorites.length
  } catch (err: any) {
    console.error('Failed to load favorites:', err)
    error.value = err.response?.data?.detail || '載入收藏清單失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const handleRemoveFavorite = async (petId: number) => {
  try {
    await favoritesStore.removeFavorite(petId)
    // Remove from local list
    favoritePets.value = favoritePets.value.filter(fav => fav.pet_id !== petId)
    totalFavorites.value--
  } catch (err: any) {
    console.error('Failed to remove favorite:', err)
    error.value = '取消收藏失敗，請稍後再試'
  }
}

const handleViewDetails = (petId: number) => {
  selectedPetId.value = petId
  showPetDialog.value = true
}

const handlePrefetch = async (petId: number) => {
  // 預加載寵物詳情到快取
  try {
    await api.get(`/pets/${petId}`)
  } catch (err) {
    // 靜默失敗，不影響用戶體驗
    console.log('Prefetch failed for pet:', petId)
  }
}

const applyFilters = () => {
  // Update URL query params
  router.push({
    query: {
      ...route.query,
      species: filters.value.species || undefined,
      status: filters.value.status || undefined
    }
  })
}

const applySorting = () => {
  // Update URL query params
  router.push({
    query: {
      ...route.query,
      sort: sortBy.value
    }
  })
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadFavorites()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadFavorites()
  }
}

// Watch route query changes
watch(() => route.query, () => {
  filters.value.species = (route.query.species as string) || ''
  filters.value.status = (route.query.status as string) || ''
  sortBy.value = (route.query.sort as string) || 'date_desc'
})

// Lifecycle
onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.favorites-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Header */
.favorites-header {
  margin-bottom: 2rem;
  margin-top: 4rem;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.page-title .mdi {
  color: #e91e63;
  font-size: 2.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #7f8c8d;
}

/* Loading State */
.loading-container {
  text-align: center;
  padding: 4rem 1rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #e91e63;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  text-align: center;
  padding: 4rem 1rem;
}

.error-icon {
  font-size: 4rem;
  color: #e74c3c;
  margin-bottom: 1rem;
}

.error-message {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 1.5rem;
}

/* Controls */
.favorites-controls {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group,
.sort-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label,
.sort-group label {
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.filter-select,
.sort-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 1rem;
  cursor: pointer;
  min-width: 150px;
}

.filter-select:hover,
.sort-select:hover {
  border-color: #e91e63;
}

/* Favorites Grid */
.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 骨架屏樣式 */
.skeleton-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.skeleton-image {
  width: 100%;
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-content {
  padding: 1rem;
}

.skeleton-title {
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.skeleton-text {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-actions {
  padding: 1rem;
  display: flex;
  gap: 0.5rem;
}

.skeleton-button {
  flex: 1;
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  font-weight: 600;
  color: #2c3e50;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #e91e63;
  color: white;
}

.btn-primary:hover {
  background: #c2185b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}

.btn-secondary {
  background: #7f8c8d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5f6c6d;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .favorites-page {
    padding: 1rem 0.5rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .favorites-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-group,
  .sort-group {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .filter-select,
  .sort-select {
    width: 100%;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .favorites-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
