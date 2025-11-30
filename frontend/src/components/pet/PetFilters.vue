<template>
  <v-card class="pet-filters" elevation="0">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>篩選條件</span>
      <v-btn
        variant="text"
        size="small"
        color="primary"
        @click="resetFilters"
      >
        重置
      </v-btn>
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-4">
      <!-- Species Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">動物種類</h4>
        <v-chip-group
          v-model="localFilters.species"
          column
          multiple
        >
          <v-chip
            v-for="species in speciesOptions"
            :key="species.value"
            :value="species.value"
            filter
            variant="outlined"
          >
            {{ species.label }}
          </v-chip>
        </v-chip-group>
      </div>

      <v-divider class="my-4" />

      <!-- Age Range Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">年齡</h4>
        <v-range-slider
          v-model="localFilters.ageRange"
          :max="15"
          :min="0"
          :step="1"
          strict
          thumb-label
          class="mt-6"
        >
          <template #thumb-label="{ modelValue }">
            {{ modelValue }}歲
          </template>
        </v-range-slider>
        <div class="d-flex justify-space-between text-caption text-medium-emphasis">
          <span>{{ localFilters.ageRange[0] }}歲</span>
          <span>{{ localFilters.ageRange[1] }}歲+</span>
        </div>
      </div>

      <v-divider class="my-4" />

      <!-- Size Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">體型</h4>
        <v-chip-group
          v-model="localFilters.size"
          column
          multiple
        >
          <v-chip
            v-for="size in sizeOptions"
            :key="size.value"
            :value="size.value"
            filter
            variant="outlined"
          >
            {{ size.label }}
          </v-chip>
        </v-chip-group>
      </div>

      <v-divider class="my-4" />

      <!-- Gender Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">性別</h4>
        <v-radio-group v-model="localFilters.gender" inline>
          <v-radio label="全部" value="all" />
          <v-radio label="公" value="male" />
          <v-radio label="母" value="female" />
        </v-radio-group>
      </div>

      <v-divider class="my-4" />

      <!-- Location Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">地區</h4>
        <v-autocomplete
          v-model="localFilters.location"
          :items="locationOptions"
          label="選擇地區"
          placeholder="所有地區"
          clearable
          variant="outlined"
          density="compact"
        />
      </div>

      <v-divider class="my-4" />

      <!-- Special Needs Filter -->
      <div class="filter-section">
        <h4 class="text-subtitle-2 mb-2">特殊條件</h4>
        <v-checkbox
          v-model="localFilters.sterilized"
          label="已絕育"
          density="compact"
          hide-details
        />
        <v-checkbox
          v-model="localFilters.vaccinated"
          label="已接種疫苗"
          density="compact"
          hide-details
        />
        <v-checkbox
          v-model="localFilters.special_needs"
          label="有特殊需求"
          density="compact"
          hide-details
        />
      </div>
    </v-card-text>

    <v-divider />

    <v-card-actions>
      <v-btn
        block
        color="primary"
        variant="elevated"
        @click="applyFilters"
      >
        套用篩選
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Filters {
  species: string[]
  ageRange: [number, number]
  size: string[]
  gender: string
  location: string | null
  sterilized: boolean
  vaccinated: boolean
  special_needs: boolean
}

interface Props {
  filters: Filters
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:filters': [filters: Filters]
  'apply': []
}>()

const localFilters = ref<Filters>({ ...props.filters })

// Options
const speciesOptions = [
  { label: '狗', value: 'dog' },
  { label: '貓', value: 'cat' },
  { label: '兔子', value: 'rabbit' },
  { label: '鳥類', value: 'bird' },
  { label: '其他', value: 'other' }
]

const sizeOptions = [
  { label: '小型', value: 'small' },
  { label: '中型', value: 'medium' },
  { label: '大型', value: 'large' }
]

const locationOptions = [
  '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
  '基隆市', '新竹市', '嘉義市',
  '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣',
  '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣', '金門縣', '連江縣'
]

// Watch for external filter changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

const applyFilters = () => {
  emit('update:filters', localFilters.value)
  emit('apply')
}

const resetFilters = () => {
  localFilters.value = {
    species: [],
    ageRange: [0, 15],
    size: [],
    gender: 'all',
    location: null,
    sterilized: false,
    vaccinated: false,
    special_needs: false
  }
  applyFilters()
}
</script>

<style scoped>
.pet-filters {
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.filter-section {
  margin-bottom: 8px;
}

.filter-section:last-child {
  margin-bottom: 0;
}
</style>
