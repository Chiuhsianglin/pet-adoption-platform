import { ref, computed } from 'vue'
import api from '@/services/api'

// Search Filter Types
export interface PetSearchFilters {
  query?: string
  species?: string[]
  gender?: string
  size?: string[]
  min_age?: number
  max_age?: number
  spayed_neutered?: boolean
  good_with_kids?: boolean
  good_with_pets?: boolean
  energy_level?: string
  max_adoption_fee?: number
  sort_by?: string
  order?: 'asc' | 'desc'
}

export interface PetSearchResult {
  id: number
  name: string
  species: string
  breed: string | null
  gender: string | null
  age_years: number | null
  age_months: number | null
  size: string | null
  description: string | null
  adoption_fee: number | null
  status: string
  primary_photo_url: string | null
  spayed_neutered: boolean
  vaccination_status: boolean
  sterilized: boolean
  good_with_kids: boolean
  good_with_pets: boolean
  energy_level: string | null
  location: string | null
  created_at: string
  updated_at: string
}

export interface PetSearchResponse {
  results: PetSearchResult[]
  total: number
  page: number
  page_size: number
  total_pages: number
  applied_filters: PetSearchFilters
}

export interface FilterOption {
  value: string
  label: string
  count: number
}

export interface FilterOptions {
  species: FilterOption[]
  genders: FilterOption[]
  sizes: FilterOption[]
  energy_levels: FilterOption[]
  age_ranges: Array<{ min: number; max: number; label: string; count: number }>
  adoption_fee_ranges: Array<{ min: number; max: number; label: string; count: number }>
}

export interface SearchSuggestion {
  value: string
  type: 'name' | 'breed'
  count: number
}

export function useSearch() {
  // State
  const searchQuery = ref('')
  const filters = ref<PetSearchFilters>({})
  const results = ref<PetSearchResult[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(12)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filterOptions = ref<FilterOptions | null>(null)
  const suggestions = ref<SearchSuggestion[]>([])
  const suggestionsLoading = ref(false)

  // Computed
  const hasFilters = computed(() => {
    return (
      filters.value.query ||
      (filters.value.species && filters.value.species.length > 0) ||
      filters.value.gender ||
      (filters.value.size && filters.value.size.length > 0) ||
      filters.value.min_age !== undefined ||
      filters.value.max_age !== undefined ||
      filters.value.spayed_neutered ||
      filters.value.good_with_kids ||
      filters.value.good_with_pets ||
      filters.value.energy_level ||
      filters.value.max_adoption_fee !== undefined
    )
  })

  const appliedFiltersCount = computed(() => {
    let count = 0
    if (filters.value.query) count++
    if (filters.value.species && filters.value.species.length > 0) count += filters.value.species.length
    if (filters.value.gender && filters.value.gender !== 'all') count++
    if (filters.value.size && filters.value.size.length > 0) count += filters.value.size.length
    if (filters.value.min_age !== undefined || filters.value.max_age !== undefined) count++
    if (filters.value.spayed_neutered) count++
    if (filters.value.good_with_kids) count++
    if (filters.value.good_with_pets) count++
    if (filters.value.energy_level) count++
    if (filters.value.max_adoption_fee !== undefined) count++
    return count
  })

  // Methods
  const search = async (skip?: number) => {
    loading.value = true
    error.value = null

    try {
      const currentSkip = skip !== undefined ? skip : (page.value - 1) * pageSize.value
      
      const response = await api.post<PetSearchResponse>('/pets/search', {
        ...filters.value,
        query: searchQuery.value || filters.value.query,
        skip: currentSkip,
        limit: pageSize.value,
        page: page.value,
        page_size: pageSize.value
      })

      // V2 API 返回 items，V1 返回 results
      const items = (response.data as any).items || response.data.results
      results.value = items
      total.value = response.data.total
      totalPages.value = response.data.total_pages
      page.value = response.data.page
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '搜尋失敗，請稍後再試'
      console.error('Search error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSuggestions = async (query: string, limit = 5) => {
    if (!query || query.trim().length < 2) {
      suggestions.value = []
      return
    }

    suggestionsLoading.value = true
    try {
      const response = await api.get<{ suggestions: SearchSuggestion[] }>(
        '/pets/search/suggestions',
        {
          params: { q: query, limit }
        }
      )
      suggestions.value = response.data.suggestions
    } catch (err) {
      console.error('Failed to fetch suggestions:', err)
      suggestions.value = []
    } finally {
      suggestionsLoading.value = false
    }
  }

  const getFilterOptions = async () => {
    try {
      const response = await api.get<FilterOptions>('/pets/filters/options')
      filterOptions.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch filter options:', err)
      throw err
    }
  }

  const updateFilter = (key: keyof PetSearchFilters, value: any) => {
    filters.value = {
      ...filters.value,
      [key]: value
    }
  }

  const removeFilter = (key: keyof PetSearchFilters) => {
    const newFilters = { ...filters.value }
    delete newFilters[key]
    filters.value = newFilters
  }

  const clearFilters = () => {
    filters.value = {}
    searchQuery.value = ''
  }

  const setPage = (newPage: number) => {
    page.value = newPage
    search((newPage - 1) * pageSize.value)
  }

  const setPageSize = (newSize: number) => {
    pageSize.value = newSize
    page.value = 1
    search(0)
  }

  const updateSearchQuery = (query: string) => {
    searchQuery.value = query
    filters.value.query = query
  }

  return {
    // State
    searchQuery,
    filters,
    results,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    filterOptions,
    suggestions,
    suggestionsLoading,
    
    // Computed
    hasFilters,
    appliedFiltersCount,
    
    // Methods
    search,
    getSuggestions,
    getFilterOptions,
    updateFilter,
    removeFilter,
    clearFilters,
    setPage,
    setPageSize,
    updateSearchQuery
  }
}
