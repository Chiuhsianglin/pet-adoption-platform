<template>
  <v-container fluid class="pet-browsing-page">
    <!-- Hero/Header (same style as HomePage, smaller height) -->
    <app-header />
    <v-card class="hero-section mb-6 mt-12" elevation="0">
      <v-img
        src="https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=1920&h=500&fit=crop"
        cover
        height="250"
        gradient="to bottom, rgba(0,0,0,.05), rgba(0,0,0,.35)"
      >
        <v-container class="fill-height">
          <v-row align="center" justify="center">
            <v-col cols="12" class="text-center text-white">
              <h1 class="text-h4 font-weight-bold mb-2">尋找你的毛孩</h1>
              <p class="text-subtitle-1 mb-0">瀏覽可愛的毛孩們，找到與你有緣的夥伴</p>
            </v-col>
          </v-row>
        </v-container>
      </v-img>
    </v-card>
    <!-- Header Section -->


    <!-- Search and Sort Bar -->
    <v-row class="mb-4">
      <v-col cols="12" md="8">
        <PetSearch
          v-model="searchComposable.searchQuery.value"
          :suggestions="searchComposable.suggestions.value"
          :suggestions-loading="searchComposable.suggestionsLoading.value"
          @search="handleSearch"
          @input="handleSearchInput"
        />
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center justify-end">
        <PetSorting
          :sort-by="sortBy"
          @update:sort-by="handleSortChange"
        />
        
        <!-- Mobile Filter Toggle -->
        <v-btn
          icon="mdi-filter-variant"
          class="ml-2 d-md-none"
          @click="mobileFilterDrawer = true"
        >
          <v-badge
            v-if="searchComposable.appliedFiltersCount.value > 0"
            :content="searchComposable.appliedFiltersCount.value"
            color="primary"
          />
        </v-btn>
      </v-col>
    </v-row>

    <!-- Main Content Area -->
    <v-row>
      <!-- Advanced Filters Sidebar (Desktop) -->
      <v-col cols="12" md="3" class="d-none d-md-block">
        <PetAdvancedFilters
          :filters="searchComposable.filters.value"
          :filter-options="searchComposable.filterOptions.value"
          :loading="filterOptionsLoading"
          @update:filters="handleFiltersUpdate"
          @apply="handleApplyFilters"
          @reset="handleResetFilters"
        />
      </v-col>

      <!-- Pet Grid -->
      <v-col cols="12" md="9">
        <!-- Active Filters Header -->
        <div v-if="searchComposable.hasFilters.value" class="mb-4">
          <div class="d-flex justify-space-between align-center mb-2">
            <span class="text-body-2 text-medium-emphasis">
              找到 {{ searchComposable.total.value }} 個結果
            </span>
            <v-btn
              variant="text"
              size="small"
              color="error"
              @click="handleResetFilters"
            >
              <v-icon start>mdi-close-circle</v-icon>
              清除全部篩選
            </v-btn>
          </div>
          
          <!-- Filter Chips -->
          <div class="d-flex flex-wrap gap-2">
            <v-chip
              v-if="searchComposable.searchQuery.value"
              closable
              @click:close="removeSearchQuery"
            >
              搜尋: {{ searchComposable.searchQuery.value }}
            </v-chip>
            
            <v-chip
              v-for="species in searchComposable.filters.value.species"
              :key="`species-${species}`"
              closable
              @click:close="removeArrayFilter('species', species)"
            >
              {{ getSpeciesLabel(species) }}
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.gender && searchComposable.filters.value.gender !== 'all'"
              closable
              @click:close="removeFilter('gender')"
            >
              {{ getGenderLabel(searchComposable.filters.value.gender) }}
            </v-chip>
            
            <v-chip
              v-for="size in searchComposable.filters.value.size"
              :key="`size-${size}`"
              closable
              @click:close="removeArrayFilter('size', size)"
            >
              {{ getSizeLabel(size) }}
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.min_age !== undefined || searchComposable.filters.value.max_age !== undefined"
              closable
              @click:close="removeAgeFilter"
            >
              年齡: {{ searchComposable.filters.value.min_age || 0 }}-{{ searchComposable.filters.value.max_age || 20 }}歲
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.spayed_neutered"
              closable
              @click:close="removeFilter('spayed_neutered')"
            >
              已絕育
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.good_with_kids"
              closable
              @click:close="removeFilter('good_with_kids')"
            >
              適合有小孩
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.good_with_pets"
              closable
              @click:close="removeFilter('good_with_pets')"
            >
              適合其他寵物
            </v-chip>
            
            <v-chip
              v-if="searchComposable.filters.value.energy_level"
              closable
              @click:close="removeFilter('energy_level')"
            >
              活力: {{ getEnergyLevelLabel(searchComposable.filters.value.energy_level) }}
            </v-chip>
          </div>
        </div>

        <!-- Pet Grid Component -->
        <PetGrid
          :pets="searchComposable.results.value"
          :loading="searchComposable.loading.value"
          :empty-message="emptyMessage"
          :show-reset-button="!!searchComposable.hasFilters.value"
          @reset-filters="handleResetFilters"
          @pet-click="handlePetClick"
        />

        <!-- Error Message -->
        <v-alert
          v-if="searchComposable.error.value"
          type="error"
          class="mt-4"
          closable
          @click:close="searchComposable.error.value = null"
        >
          {{ searchComposable.error.value }}
        </v-alert>

        <!-- Pagination -->
        <PaginationControls
          v-if="searchComposable.total.value > 0"
          :page="searchComposable.page.value"
          :page-size="searchComposable.pageSize.value"
          :total="searchComposable.total.value"
          class="mt-6"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </v-col>
    </v-row>

    <!-- Mobile Filter Drawer -->
    <v-navigation-drawer
      v-model="mobileFilterDrawer"
      location="right"
      temporary
      width="300"
      class="d-md-none"
    >
      <v-toolbar color="primary">
        <v-toolbar-title>篩選條件</v-toolbar-title>
        <v-btn icon="mdi-close" @click="mobileFilterDrawer = false" />
      </v-toolbar>
      
      <PetAdvancedFilters
        :filters="searchComposable.filters.value"
        :filter-options="searchComposable.filterOptions.value"
        :loading="filterOptionsLoading"
        @update:filters="handleFiltersUpdate"
        @apply="applyMobileFilters"
        @reset="handleResetFilters"
      />
    </v-navigation-drawer>

    <!-- Pet Detail Dialog -->
    <v-dialog
      v-model="petDetailDialog"
      max-width="90vw"
      scrollable
      :transition="false"
    >
      <v-card style="height: 85vh;">
        <v-toolbar color="primary" dark dense>
          <v-btn icon="mdi-arrow-left" @click="closePetDialog" />
          <v-toolbar-title>寵物詳情</v-toolbar-title>
          <v-spacer />
          <v-btn icon="mdi-close" @click="closePetDialog" />
        </v-toolbar>
        <v-card-text class="pa-0" style="height: calc(85vh - 48px); overflow-y: auto;">
          <keep-alive>
            <PetDetailContent 
              v-if="selectedPetId" 
              :pet-id="selectedPetId" 
              :in-dialog="true"
              @close="closePetDialog"
            />
          </keep-alive>
        </v-card-text>
      </v-card>
    </v-dialog>

    </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFavoritesStore } from '@/stores/favorites'
import { useSearch } from '@/composables/useSearch'
import type { PetSearchFilters } from '@/composables/useSearch'
import PetSearch from '@/components/pet/PetSearch.vue'
import PetSorting from '@/components/pet/PetSorting.vue'
import PetAdvancedFilters from '@/components/pet/PetAdvancedFilters.vue'
import PetGrid from '@/components/pet/PetGrid.vue'
import PaginationControls from '@/components/pet/PaginationControls.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import PetDetailContent from '@/components/pet/PetDetailContent.vue'

const route = useRoute()
const router = useRouter()
const favoritesStore = useFavoritesStore()

// Use search composable
const searchComposable = useSearch()

// Local state
const sortBy = ref('random')
const mobileFilterDrawer = ref(false)
const filterOptionsLoading = ref(false)
const petDetailDialog = ref(false)
const selectedPetId = ref<number | null>(null)

// Debounce timer for search suggestions
let suggestionDebounceTimer: ReturnType<typeof setTimeout> | null = null

// Computed
const emptyMessage = computed(() => {
  if (searchComposable.hasFilters.value) {
    return '沒有找到符合條件的寵物'
  }
  return '目前沒有可領養的寵物'
})

// Methods
const performSearch = async () => {
  try {
    // Update sort in filters
    if (sortBy.value === 'random') {
      // 隨機排序：不傳遞 sort_by 和 order
      searchComposable.updateFilter('sort_by', undefined)
      searchComposable.updateFilter('order', undefined)
    } else if (sortBy.value === 'newest') {
      searchComposable.updateFilter('sort_by', 'created_at')
      searchComposable.updateFilter('order', 'desc')
    } else if (sortBy.value === 'age_asc') {
      // 年齡小到大 = 出生年份大到小（年輕的在前）
      searchComposable.updateFilter('sort_by', 'age')
      searchComposable.updateFilter('order', 'desc')
    } else if (sortBy.value === 'age_desc') {
      // 年齡大到小 = 出生年份小到大（年長的在前）
      searchComposable.updateFilter('sort_by', 'age')
      searchComposable.updateFilter('order', 'asc')
    } else if (sortBy.value === 'name_asc') {
      searchComposable.updateFilter('sort_by', 'name')
      searchComposable.updateFilter('order', 'asc')
    } else if (sortBy.value === 'name_desc') {
      searchComposable.updateFilter('sort_by', 'name')
      searchComposable.updateFilter('order', 'desc')
    }

    await searchComposable.search()
    updateURL()
  } catch (error) {
    console.error('Search failed:', error)
  }
}

const handleSearch = (query: string) => {
  searchComposable.updateSearchQuery(query)
  searchComposable.setPage(1)
  performSearch()
}

const handleSearchInput = (query: string) => {
  // Debounce API suggestions
  if (suggestionDebounceTimer) {
    clearTimeout(suggestionDebounceTimer)
  }

  suggestionDebounceTimer = setTimeout(() => {
    if (query && query.trim().length >= 2) {
      searchComposable.getSuggestions(query)
    }
  }, 300)
}

const handleSortChange = (newSort: string) => {
  sortBy.value = newSort
  performSearch()
}

const handleFiltersUpdate = (newFilters: PetSearchFilters) => {
  searchComposable.filters.value = newFilters
}

const handleApplyFilters = () => {
  searchComposable.setPage(1)
  performSearch()
}

const handleResetFilters = () => {
  searchComposable.clearFilters()
  sortBy.value = 'random'
  mobileFilterDrawer.value = false
  performSearch()
}

const handlePageChange = (newPage: number) => {
  searchComposable.setPage(newPage)
}

const handlePageSizeChange = (newSize: number) => {
  searchComposable.setPageSize(newSize)
}

const applyMobileFilters = () => {
  mobileFilterDrawer.value = false
  searchComposable.setPage(1)
  performSearch()
}

const removeSearchQuery = () => {
  searchComposable.updateSearchQuery('')
  performSearch()
}

const removeFilter = (key: keyof PetSearchFilters) => {
  searchComposable.removeFilter(key)
  performSearch()
}

const removeArrayFilter = (key: 'species' | 'size', value: string) => {
  const currentValues = searchComposable.filters.value[key] || []
  const newValues = currentValues.filter((v: string) => v !== value)
  searchComposable.updateFilter(key, newValues.length > 0 ? newValues : undefined)
  performSearch()
}

const removeAgeFilter = () => {
  searchComposable.removeFilter('min_age')
  searchComposable.removeFilter('max_age')
  performSearch()
}

const updateURL = () => {
  const query: any = {}

  if (searchComposable.page.value > 1) {
    query.page = searchComposable.page.value.toString()
  }
  
  if (searchComposable.pageSize.value !== 24) {
    query.pageSize = searchComposable.pageSize.value.toString()
  }
  
  if (searchComposable.searchQuery.value) {
    query.search = searchComposable.searchQuery.value
  }
  
  if (sortBy.value !== 'newest') {
    query.sort = sortBy.value
  }
  
  const filters = searchComposable.filters.value
  
  if (filters.species && filters.species.length > 0) {
    query.species = filters.species.join(',')
  }
  
  if (filters.size && filters.size.length > 0) {
    query.size = filters.size.join(',')
  }
  
  if (filters.gender && filters.gender !== 'all') {
    query.gender = filters.gender
  }
  
  if (filters.min_age !== undefined) {
    query.min_age = filters.min_age.toString()
  }
  
  if (filters.max_age !== undefined) {
    query.max_age = filters.max_age.toString()
  }

  router.replace({ query })
}

const loadFromURL = () => {
  const query = route.query

  if (query.page) {
    searchComposable.page.value = parseInt(query.page as string)
  }
  
  if (query.pageSize) {
    searchComposable.pageSize.value = parseInt(query.pageSize as string)
  }
  
  if (query.search) {
    searchComposable.updateSearchQuery(query.search as string)
  }
  
  if (query.sort) {
    sortBy.value = query.sort as string
  }
  
  const filters: PetSearchFilters = {}
  
  if (query.species) {
    filters.species = (query.species as string).split(',')
  }
  
  if (query.size) {
    filters.size = (query.size as string).split(',')
  }
  
  if (query.gender) {
    filters.gender = query.gender as string
  }
  
  if (query.min_age) {
    filters.min_age = parseInt(query.min_age as string)
  }
  
  if (query.max_age) {
    filters.max_age = parseInt(query.max_age as string)
  }
  
  searchComposable.filters.value = filters
}

// Label helpers
const getSpeciesLabel = (species: string) => {
  const labels: Record<string, string> = {
    dog: '狗',
    cat: '貓',
    rabbit: '兔子',
    bird: '鳥類',
    other: '其他'
  }
  return labels[species] || species
}

const getGenderLabel = (gender: string) => {
  const labels: Record<string, string> = {
    male: '公',
    female: '母',
    unknown: '未知'
  }
  return labels[gender] || gender
}

const getSizeLabel = (size: string) => {
  const labels: Record<string, string> = {
    small: '小型',
    medium: '中型',
    large: '大型',
    extra_large: '超大型'
  }
  return labels[size] || size
}

const getEnergyLevelLabel = (level: string) => {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return labels[level] || level
}

const handlePetClick = (petId: number) => {
  // Immediately open dialog for faster perceived performance
  petDetailDialog.value = true
  // Set pet ID after dialog starts opening
  requestAnimationFrame(() => {
    selectedPetId.value = petId
  })
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

// Lifecycle
onMounted(async () => {
  // Load from URL first
  loadFromURL()
  
  // Parallel load: filter options and initial search at the same time
  filterOptionsLoading.value = true
  
  const [filterOptionsResult, searchResult] = await Promise.allSettled([
    searchComposable.getFilterOptions(),
    performSearch()
  ])
  
  filterOptionsLoading.value = false
  
  if (filterOptionsResult.status === 'rejected') {
    console.error('Failed to load filter options:', filterOptionsResult.reason)
  }
  
  if (searchResult.status === 'rejected') {
    console.error('Failed to perform initial search:', searchResult.reason)
  }
  
  // Load favorites in background (non-blocking)
  favoritesStore.loadFavorites().catch(err => {
    console.error('Failed to load favorites:', err)
  })
})

// Watch for route changes
watch(() => route.query, () => {
  loadFromURL()
  performSearch()
})
</script>

<style scoped>
.pet-browsing-page {
  padding-top: 24px;
  padding-bottom: 48px;
}
</style>
