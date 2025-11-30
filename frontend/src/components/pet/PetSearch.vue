<template>
  <div class="pet-search">
    <v-text-field
      v-model="searchQuery"
      label="搜尋寵物"
      placeholder="輸入寵物名稱、品種或關鍵字"
      prepend-inner-icon="mdi-magnify"
      variant="outlined"
      density="comfortable"
      clearable
      hide-details
      :loading="suggestionsLoading"
      @update:model-value="handleSearchInput"
      @keyup.enter="handleSearch"
      @click:clear="handleClear"
      @focus="handleFocus"
    >
      <template #append-inner>
        <v-btn
          icon="mdi-arrow-right"
          size="small"
          variant="text"
          :disabled="!searchQuery"
          @click="handleSearch"
        />
      </template>
    </v-text-field>

    <!-- Search Suggestions Dropdown -->
    <v-menu
      v-model="showSuggestions"
      :close-on-content-click="false"
      activator="parent"
      offset="4"
      max-height="400"
    >
      <v-list v-if="hasAnySuggestions" density="compact">
        <!-- API Suggestions -->
        <template v-if="apiSuggestions.length > 0">
          <v-list-subheader>搜尋建議</v-list-subheader>
          <v-list-item
            v-for="(suggestion, index) in apiSuggestions"
            :key="`api-${index}`"
            @click="selectApiSuggestion(suggestion)"
          >
            <template #prepend>
              <v-icon 
                :icon="suggestion.type === 'name' ? 'mdi-paw' : 'mdi-tag-outline'" 
                size="small" 
                :color="suggestion.type === 'name' ? 'primary' : 'secondary'"
              />
            </template>
            <v-list-item-title>
              {{ suggestion.value }}
              <span class="text-caption text-medium-emphasis ml-1">({{ suggestion.count }})</span>
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ suggestion.type === 'name' ? '寵物名稱' : '品種' }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider v-if="searchHistory.length > 0" class="my-1" />
        </template>

        <!-- Search History -->
        <template v-if="searchHistory.length > 0">
          <v-list-subheader>搜尋記錄</v-list-subheader>
          <v-list-item
            v-for="(history, index) in searchHistory"
            :key="`history-${index}`"
            @click="selectHistoryItem(history)"
          >
            <template #prepend>
              <v-icon icon="mdi-history" size="small" color="grey" />
            </template>
            <v-list-item-title>{{ history }}</v-list-item-title>
          </v-list-item>
          <v-divider class="my-1" />
          <v-list-item @click="clearHistory">
            <template #prepend>
              <v-icon icon="mdi-delete-outline" size="small" color="error" />
            </template>
            <v-list-item-title class="text-caption text-error">清除搜尋記錄</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>

      <!-- Loading State -->
      <v-list v-else-if="suggestionsLoading" density="compact">
        <v-list-item>
          <v-progress-circular indeterminate size="20" width="2" class="mr-2" />
          <v-list-item-title class="text-caption">載入建議中...</v-list-item-title>
        </v-list-item>
      </v-list>

      <!-- No Results -->
      <v-list v-else-if="searchQuery && searchQuery.length >= 2" density="compact">
        <v-list-item>
          <v-list-item-title class="text-caption text-medium-emphasis">
            沒有找到相關建議
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import type { SearchSuggestion } from '@/composables/useSearch'

interface Props {
  modelValue?: string
  suggestions?: SearchSuggestion[]
  suggestionsLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  suggestions: () => [],
  suggestionsLoading: false
})

const emit = defineEmits<{
  'update:model-value': [value: string]
  'search': [query: string]
  'input': [query: string]
}>()

const searchQuery = ref(props.modelValue || '')
const showSuggestions = ref(false)
const searchHistory = ref<string[]>([])

const SEARCH_HISTORY_KEY = 'pet_search_history'
const MAX_HISTORY_ITEMS = 5

// Computed
const apiSuggestions = computed(() => props.suggestions || [])
const hasAnySuggestions = computed(() => 
  apiSuggestions.value.length > 0 || searchHistory.value.length > 0
)

// Load search history from localStorage
onMounted(() => {
  loadSearchHistory()
})

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  searchQuery.value = newValue || ''
})

// Watch for input to show/hide suggestions
watch(searchQuery, (newValue) => {
  if (newValue && newValue.trim().length >= 2) {
    showSuggestions.value = true
  } else if (!newValue) {
    showSuggestions.value = false
  }
})

const loadSearchHistory = () => {
  const stored = localStorage.getItem(SEARCH_HISTORY_KEY)
  if (stored) {
    try {
      searchHistory.value = JSON.parse(stored)
    } catch (e) {
      console.error('Failed to parse search history:', e)
      searchHistory.value = []
    }
  }
}

const saveSearchHistory = () => {
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(searchHistory.value))
}

const addToHistory = (query: string) => {
  if (!query.trim()) return
  
  // Remove if already exists
  const index = searchHistory.value.indexOf(query)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
  }
  
  // Add to beginning
  searchHistory.value.unshift(query)
  
  // Keep only last MAX_HISTORY_ITEMS
  if (searchHistory.value.length > MAX_HISTORY_ITEMS) {
    searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY_ITEMS)
  }
  
  saveSearchHistory()
}

const handleSearchInput = (value: string) => {
  emit('update:model-value', value)
  emit('input', value) // For debounced API suggestions
}

const handleSearch = () => {
  if (searchQuery.value && searchQuery.value.trim()) {
    addToHistory(searchQuery.value.trim())
    emit('search', searchQuery.value.trim())
    showSuggestions.value = false
  }
}

const handleClear = () => {
  searchQuery.value = ''
  emit('update:model-value', '')
  emit('search', '')
  showSuggestions.value = false
}

const handleFocus = () => {
  if (searchQuery.value && searchQuery.value.trim().length >= 2) {
    showSuggestions.value = true
  } else if (searchHistory.value.length > 0 && !searchQuery.value) {
    showSuggestions.value = true
  }
}

const selectApiSuggestion = (suggestion: SearchSuggestion) => {
  searchQuery.value = suggestion.value
  addToHistory(suggestion.value)
  emit('update:model-value', suggestion.value)
  emit('search', suggestion.value)
  showSuggestions.value = false
}

const selectHistoryItem = (historyItem: string) => {
  searchQuery.value = historyItem
  emit('update:model-value', historyItem)
  emit('search', historyItem)
  showSuggestions.value = false
}

const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem(SEARCH_HISTORY_KEY)
  showSuggestions.value = false
}
</script>

<style scoped>
.pet-search {
  width: 100%;
  max-width: 600px;
}
</style>
